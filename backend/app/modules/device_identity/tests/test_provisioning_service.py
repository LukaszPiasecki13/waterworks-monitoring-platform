"""Tests for device provisioning service."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.errors import ConflictError
from app.modules.core_data.models.user import User
from app.modules.device_identity.services.provisioning import (
    DeviceProvisioningService,
)
from app.modules.security.access import PlatformContext


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_audit():
    return MagicMock()


@pytest.fixture
def service(mock_repo, mock_audit):
    return DeviceProvisioningService(mock_repo, mock_audit)


@pytest.fixture
def platform_ctx():
    user = User(
        id=uuid4(),
        username="admin",
        email="admin@example.com",
        hashed_password="hash",
        is_active=True,
    )
    return PlatformContext(
        actor=user, permissions={"PLATFORM_MANAGE_DEVICE_PROVISIONING"}
    )


def test_register_new_device(service, mock_repo, mock_audit, platform_ctx):
    """Test successful device registration."""
    mock_repo.get_by_serial_number.return_value = None
    credential_id = uuid4()
    mock_credential = MagicMock()
    mock_credential.id = credential_id
    mock_credential.serial_number = "TEST-SN-001"
    mock_credential.status = "unclaimed"
    mock_repo.create.return_value = mock_credential

    result = service.register(
        serial_number="TEST-SN-001",
        public_key_pem="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
        platform_ctx=platform_ctx,
    )

    assert result.id == credential_id
    assert result.status == "unclaimed"
    mock_repo.create.assert_called_once()
    mock_audit.record.assert_called_once()


def test_register_duplicate_device(service, mock_repo, platform_ctx):
    """Test registration fails for duplicate serial number."""
    existing_credential = MagicMock()
    mock_repo.get_by_serial_number.return_value = existing_credential

    with pytest.raises(ConflictError):
        service.register(
            serial_number="TEST-SN-001",
            public_key_pem="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
            platform_ctx=platform_ctx,
        )


def test_register_audit_recorded(service, mock_repo, mock_audit, platform_ctx):
    """Test that registration is audited."""
    mock_repo.get_by_serial_number.return_value = None
    credential_id = uuid4()
    mock_credential = MagicMock()
    mock_credential.id = credential_id
    mock_credential.serial_number = "TEST-SN-001"
    mock_repo.create.return_value = mock_credential

    service.register(
        serial_number="TEST-SN-001",
        public_key_pem="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
        platform_ctx=platform_ctx,
    )

    # Verify audit was called
    mock_audit.record.assert_called_once()
    audit_call = mock_audit.record.call_args[0][0]
    assert audit_call.entity_type == "device_identity_credential"
    assert audit_call.action == "REGISTER"
    assert audit_call.actor_id == str(platform_ctx.actor.id)
