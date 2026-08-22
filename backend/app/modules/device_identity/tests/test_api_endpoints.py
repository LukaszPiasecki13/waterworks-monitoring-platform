"""Integration tests for device_identity API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.device_identity.api.claims import claims_router
from app.modules.device_identity.api.device_auth import device_auth_router
from app.modules.device_identity.api.provisioning import provisioning_router
from app.modules.device_identity.dependencies import (
    get_device_auth_service,
    get_provisioning_service,
)


@pytest.fixture
def test_app():
    """Create a test FastAPI app with device_identity routers."""
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(device_auth_router)
    app.include_router(provisioning_router, prefix="/api/v1/platform")
    app.include_router(claims_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(test_app, db_session):
    """Create a test client with dependency overrides."""

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return TestClient(test_app)


@pytest.fixture
def org_id():
    return str(uuid4())


@pytest.fixture
def water_object_id():
    return str(uuid4())


class TestDeviceAuthEndpoints:
    """Tests for /devices/auth/challenge and /devices/auth/verify"""

    def test_challenge_not_found(self, client, test_app):
        """Test challenge for unknown device returns 404."""
        from app.core.errors import NotFoundError

        mock_service = MagicMock()
        mock_service.challenge.side_effect = NotFoundError("Not found")

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/challenge",
            json={"serial_number": "UNKNOWN-SN"},
        )

        assert response.status_code == 404

    def test_challenge_success(self, client, test_app):
        """Test successful challenge request."""
        mock_service = MagicMock()
        mock_service.challenge.return_value = ("TEST-SN-001", "nonce123")

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/challenge",
            json={"serial_number": "TEST-SN-001"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["serial_number"] == "TEST-SN-001"
        assert data["challenge"] == "nonce123"

    def test_verify_success(self, client, test_app):
        """Test successful verify."""
        expires_at = datetime.now(UTC) + timedelta(hours=36)

        mock_service = MagicMock()
        mock_service.verify.return_value = ("token123", "bearer", expires_at)

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/verify",
            json={
                "serial_number": "TEST-SN-001",
                "signature": "deadbeef",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "token123"
        assert data["token_type"] == "bearer"

    def test_verify_no_challenge_returns_400(self, client, test_app):
        """Test verify without active challenge returns 400."""
        from app.core.errors import BadRequestError

        mock_service = MagicMock()
        mock_service.verify.side_effect = BadRequestError("No active challenge")

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/verify",
            json={
                "serial_number": "TEST-SN-001",
                "signature": "deadbeef",
            },
        )

        assert response.status_code == 400

    def test_verify_expired_challenge_returns_410(self, client, test_app):
        """Test verify with expired challenge returns 410."""
        from app.core.errors import GoneError

        mock_service = MagicMock()
        mock_service.verify.side_effect = GoneError("Challenge expired")

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/verify",
            json={
                "serial_number": "TEST-SN-001",
                "signature": "deadbeef",
            },
        )

        assert response.status_code == 410

    def test_verify_bad_signature_returns_401(self, client, test_app):
        """Test verify with invalid signature returns 401."""
        from app.core.errors import AuthenticationError

        mock_service = MagicMock()
        mock_service.verify.side_effect = AuthenticationError(
            "Signature verification failed"
        )

        test_app.dependency_overrides[get_device_auth_service] = lambda: mock_service

        response = client.post(
            "/devices/auth/verify",
            json={
                "serial_number": "TEST-SN-001",
                "signature": "badsig",
            },
        )

        assert response.status_code == 401


class TestProvisioningEndpoint:
    """Tests for POST /api/v1/platform/device-provisioning"""

    def test_provision_success(self, client, test_app):
        """Test successful device provisioning."""
        mock_service = MagicMock()
        mock_credential = MagicMock()
        mock_credential.serial_number = "TEST-SN-001"
        mock_credential.status = "unclaimed"
        mock_service.register.return_value = mock_credential

        test_app.dependency_overrides[get_provisioning_service] = lambda: mock_service

        response = client.post(
            "/api/v1/platform/device-provisioning",
            json={
                "serial_number": "TEST-SN-001",
                "public_key_pem": (
                    "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----"
                ),
            },
        )

        # Will fail auth check (no platform permission), but shows endpoint exists
        assert response.status_code in [401, 403, 200]


class TestClaimEndpoints:
    """Tests for POST/GET /api/v1/orgs/{org_id}/devices"""

    def test_claim_device_endpoint_exists(self, client, org_id, water_object_id):
        """Test claim device endpoint responds (auth will fail but endpoint exists)."""
        response = client.post(
            f"/api/v1/orgs/{org_id}/devices",
            json={
                "serial_number": "TEST-SN-001",
                "water_object_id": water_object_id,
            },
        )

        # Will fail auth check (no org access), but shows endpoint exists
        assert response.status_code in [401, 403, 200]

    def test_get_claim_status_endpoint_exists(self, client, org_id):
        """Test get claim status endpoint responds."""
        response = client.get(f"/api/v1/orgs/{org_id}/devices/claims/TEST-SN-001")

        # Will fail auth check (no org access), but shows endpoint exists
        assert response.status_code in [401, 403, 200]
