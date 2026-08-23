"""Integration tests for the device-activation-codes API.

These deliberately use a real, permission-checked PlatformContext (via
`admin_user`) rather than mocking the service or the auth dependency, the
way `test_api_endpoints.py` does. A prior regression (the router read
`context.user_id`, which doesn't exist on PlatformContext — only
`context.actor.id` does) went undetected because no test exercised the
router body with a real PlatformContext; mocking the service bypasses the
router code entirely, and mocking auth never builds a real context.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.models import User
from app.modules.device_identity.api.activation_codes import activation_codes_router
from app.modules.security.dependencies import get_current_user


@pytest.fixture
def client(db_session: Session, admin_user: User) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(activation_codes_router, prefix="/api/v1/platform")

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin_user
    return TestClient(app)


def test_create_activation_code_returns_plaintext_code(client: TestClient) -> None:
    response = client.post("/api/v1/platform/device-activation-codes")

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "unused"
    assert "-" in data["activation_code"]


def test_get_activation_code_status(client: TestClient) -> None:
    created = client.post("/api/v1/platform/device-activation-codes").json()

    response = client.get(f"/api/v1/platform/device-activation-codes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "unused"
    assert response.json()["serial_number"] is None


def test_cancel_activation_code(client: TestClient) -> None:
    created = client.post("/api/v1/platform/device-activation-codes").json()

    response = client.post(
        f"/api/v1/platform/device-activation-codes/{created['id']}/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
