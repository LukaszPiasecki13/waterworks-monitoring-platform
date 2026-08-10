"""Shared pytest fixtures for backend tests."""

import os
from collections.abc import Generator
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Configure test environment via .env file
from dotenv import load_dotenv
load_dotenv()

# Use Settings defaults for test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-chars-long!")
# DATABASE_URL must be provided in .env for tests

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.infrastructure.sql import models_registry  # noqa: F401
from app.infrastructure.sql.base import Base
from app.modules.core_data.api.users import router as users_router
from app.modules.core_data.models import User
from app.modules.security.api import router as security_router
from app.modules.security.dependencies import (
    get_current_user,
    require_admin,
)
from app.modules.security.models import (
    Permission,
    UserGroup,
    security_user_groups,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ATTACHMENTS,
    CAN_MANAGE_SECURITY,
    CAN_MANAGE_USERS,
    CAN_VIEW_ATTACHMENTS,
    CAN_VIEW_SECURITY,
    CAN_VIEW_USERS,
)


@pytest.fixture
def db_engine() -> Generator[Engine, None, None]:
    # Use production database for tests
    settings = get_settings()
    engine = create_engine(settings.database_url, echo=False)

    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    """Keep env-var driven settings from leaking between tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


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
    db_session.flush()
    admin_uuid = uuid4()
    user = User(
        id=admin_uuid,
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password="not-used",
        status="admin",
        is_active=True,
        organization_id=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    all_permissions = [
        Permission(code=code, name=code, category="test")
        for code in (
            CAN_VIEW_USERS,
            CAN_MANAGE_USERS,
            CAN_VIEW_SECURITY,
            CAN_MANAGE_SECURITY,
            CAN_VIEW_ATTACHMENTS,
            CAN_MANAGE_ATTACHMENTS,
        )
    ]
    admin_group = UserGroup(
        name="Admin",
        description="Full system access",
        is_system=True,
        system_key="admin",
        permissions=all_permissions,
    )
    db_session.add(admin_group)
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
) -> Generator[TestClient, None, None]:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(security_router)
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
