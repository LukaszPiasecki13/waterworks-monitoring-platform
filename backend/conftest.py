"""Shared pytest fixtures for backend tests."""

import os
from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALGORITHM"] = "HS256"

from app.core.dependencies import get_db  # noqa: E402
from app.core.errors import register_error_handlers  # noqa: E402
from app.infrastructure.sql.base import Base  # noqa: E402
from app.infrastructure.sql import models_registry  # noqa: F401, E402
from app.modules.core_data.api.users import router as users_router  # noqa: E402
from app.modules.core_data.models import User  # noqa: E402
from app.modules.security.api import router as security_router  # noqa: E402
from app.modules.security.dependencies import (  # noqa: E402
    get_current_user,
    require_admin,
)
from app.modules.security.models import (  # noqa: E402
    UserGroup,
    security_user_groups,
)



@pytest.fixture
def db_engine() -> Generator[Engine, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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


@pytest.fixture
def admin_user(db_session: Session) -> User:
    db_session.flush()
    user = User(
        id=999,
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password="not-used",
        status="admin",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    admin_group = db_session.query(UserGroup).filter_by(system_key="admin").one()
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
