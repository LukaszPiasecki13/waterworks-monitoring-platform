from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.repositories import UserRepository
from app.modules.security.api import router
from app.modules.security.permission_catalog import STAFF_GROUP_KEY
from app.modules.security.repositories import PermissionRepository
from app.modules.security.services.permissions import PermissionService


def permission_service(session: Session) -> PermissionService:
    return PermissionService(
        PermissionRepository(session), UserRepository(session), MagicMock()
    )


@pytest.fixture
def auth_client(db_session: Session) -> Generator[TestClient, None, None]:
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
    app.include_router(router)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_register_login_refresh_and_current_user(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    register_response = auth_client.post(
        "/auth/register",
        json={
            "username": "NewUser",
            "email": "NewUser@example.com",
            "password": "StrongPass123",
            "first_name": "Jan",
            "last_name": "Kowalski",
        },
    )
    assert register_response.status_code == 200
    assert register_response.json()["username"] == "newuser"
    assert register_response.json()["email"] == "newuser@example.com"
    assert register_response.json()["status"] == "regular"
    registered_id = register_response.json()["id"]
    assert len(permission_service(db_session).group_ids_for_user(registered_id)) == 1

    login_response = auth_client.post(
        "/auth/token",
        json={
            "username": "newuser@example.com",
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
    assert user_data["email"] == "newuser@example.com"
    assert "organization_id" in user_data
    assert user_data["organization_id"] is None  # New user has no organization


def test_login_rejects_wrong_password(auth_client: TestClient) -> None:
    auth_client.post(
        "/auth/register",
        json={
            "username": "login-user",
            "email": "login@example.com",
            "password": "StrongPass123",
        },
    )

    response = auth_client.post(
        "/auth/token",
        json={"username": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
