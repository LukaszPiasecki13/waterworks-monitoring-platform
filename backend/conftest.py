"""Shared pytest fixtures for backend tests."""

import os
from collections.abc import Generator
from datetime import datetime
from uuid import uuid4

import pytest

# Configure test environment via .env file
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# Use Settings defaults for test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-chars-long!")
# DATABASE_URL must be provided in .env for tests

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.core.rate_limit import limiter
from app.infrastructure.sql import models_registry  # noqa: F401
from app.modules.core_data.api import users_router
from app.modules.core_data.models import User
from app.modules.security.api import auth_router
from app.modules.security.dependencies import get_current_user
from app.modules.security.models import security_user_groups
from app.modules.security.permission_catalog import ADMIN_GROUP_KEY
from app.modules.security.repositories import GroupRepository, PermissionRepository
from app.modules.security.services.seed import SecuritySeedService


@pytest.fixture
def db_engine() -> Generator[Engine]:
    """Engine for the configured database.

    Schema is owned by Alembic migrations, not by tests. DATABASE_URL may
    point at a shared/dev database, so this fixture must never create or
    drop tables — see db_session for how tests stay isolated instead.
    """
    settings = get_settings()
    engine = create_engine(settings.database_url, echo=False)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session]:
    """Session bound to a connection whose outer transaction is rolled back
    after the test. A SAVEPOINT is restarted after every commit/rollback so
    test code can call session.commit() freely without ending the outer
    transaction — every test leaves the database exactly as it found it.
    """
    connection = db_engine.connect()
    outer_transaction = connection.begin()

    settings = get_settings()
    if db_engine.dialect.name == "postgresql" and settings.database_schema:
        # Supabase's transaction-mode pooler can hand out a different physical
        # connection per transaction, so the schema must be (re)applied here
        # rather than relying on the role's default search_path. SET LOCAL
        # scopes it to this transaction, matching SQLConnectionFactory.
        schema_sql = db_engine.dialect.identifier_preparer.quote(
            settings.database_schema
        )
        connection.exec_driver_sql(f"SET LOCAL search_path TO {schema_sql}")

    session = sessionmaker(bind=connection, expire_on_commit=False)()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess: Session, transaction: object) -> None:
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None]:
    """Keep env-var driven settings from leaking between tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> Generator[None]:
    """Reset slowapi's in-memory counters between tests.

    TestClient requests all share one synthetic remote address, so without
    this every test hitting a rate-limited endpoint would draw down the same
    bucket as every other test in the run.
    """
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def settings_override(monkeypatch):
    """Fixture to override Settings via environment variables.

    Usage in test:
        def test_something(settings_override):
            settings_override.setenv("LOG_LEVEL", "DEBUG")
            settings = get_settings()  # Will read new value
    """
    return monkeypatch


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """A user with full permissions.

    The permission catalog and the "admin" system group are reference data
    owned by SecuritySeedService (synced at app startup), so this fixture
    reuses/get-or-creates them via the same service instead of inserting
    duplicate rows — DATABASE_URL may point at a database where that
    reference data already exists.
    """
    perm_repo = PermissionRepository(db_session)
    group_repo = GroupRepository(db_session)
    SecuritySeedService(perm_repo, group_repo).seed()
    admin_group = group_repo.get_group_by_system_key(ADMIN_GROUP_KEY)

    unique = uuid4().hex[:8]
    user = User(
        id=uuid4(),
        username=f"admin-{unique}",
        email=f"admin-{unique}@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password="not-used",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(user)
    db_session.flush()
    db_session.execute(
        security_user_groups.insert(),
        {"user_id": user.id, "group_id": admin_group.id},
    )
    db_session.commit()
    return user


@pytest.fixture
def api_client(
    db_session: Session,
    admin_user: User,
) -> Generator[TestClient]:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
