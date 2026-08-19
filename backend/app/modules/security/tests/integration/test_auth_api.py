from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.core.rate_limit import register_rate_limiting
from app.modules.core_data.models import User
from app.modules.core_data.repositories import UserRepository
from app.modules.security.api import router
from app.modules.security.permission_catalog import STAFF_GROUP_KEY
from app.modules.security.repositories import PermissionRepository
from app.modules.security.services.password import hash_password
from app.modules.security.services.permissions import PermissionService


def permission_service(session: Session) -> PermissionService:
    return PermissionService(
        PermissionRepository(session), UserRepository(session), MagicMock()
    )


@pytest.fixture
def auth_client(db_session: Session) -> Generator[TestClient]:
    repo = PermissionRepository(db_session)
    if not repo.get_group_by_system_key(STAFF_GROUP_KEY):
        # "Staff" is reference data normally synced by SecuritySeedService at
        # startup; DATABASE_URL may point at a database where it already
        # exists, so only create it if missing.
        repo.create_system_group(
            name="Staff",
            description="Default application access",
            system_key=STAFF_GROUP_KEY,
        )
    db_session.commit()
    app = FastAPI()
    register_error_handlers(app)
    register_rate_limiting(app)
    app.include_router(router)

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_login_refresh_and_current_user(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    # Create a test user directly in DB (registration via /register removed)
    test_user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=hash_password("StrongPass123"),
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(test_user)
    db_session.commit()

    login_response = auth_client.post(
        "/auth/token",
        json={
            "username": "testuser",
            "password": "StrongPass123",
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["access"]
    assert tokens["refresh"]

    refresh_response = auth_client.post(
        "/auth/token/refresh",
        json={"refresh": tokens["refresh"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access"]

    current_user_response = auth_client.get(
        "/auth/user",
        headers={"Authorization": f"Bearer {tokens['access']}"},
    )
    assert current_user_response.status_code == 200
    user_data = current_user_response.json()
    assert user_data["email"] == "test@example.com"


def test_login_rejects_wrong_password(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    # Create a test user directly in DB
    test_user = User(
        username="login-user",
        email="login@example.com",
        first_name="",
        last_name="",
        hashed_password=hash_password("StrongPass123"),
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(test_user)
    db_session.commit()

    response = auth_client.post(
        "/auth/token",
        json={"username": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_rate_limited_after_repeated_attempts(auth_client: TestClient) -> None:
    """The 6th login attempt within a minute is rejected before it reaches
    AuthService, regardless of whether the credentials are valid."""
    for _ in range(5):
        response = auth_client.post(
            "/auth/token",
            json={"username": "nobody@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401

    limited_response = auth_client.post(
        "/auth/token",
        json={"username": "nobody@example.com", "password": "wrong-password"},
    )

    assert limited_response.status_code == 429
    assert limited_response.json() == {"detail": "Too many requests"}
