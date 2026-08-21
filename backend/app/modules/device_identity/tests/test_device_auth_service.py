"""Tests for device authentication service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.core.errors import (
    AuthenticationError,
    BadRequestError,
    GoneError,
    NotFoundError,
)
from app.modules.device_identity.services.device_auth import DeviceAuthService


@pytest.fixture
def mock_credential_repo():
    return MagicMock()


@pytest.fixture
def mock_device_service():
    return MagicMock()


@pytest.fixture
def mock_token_service():
    service = MagicMock()
    service.create_device_token.return_value = (
        "test_token",
        datetime.now(UTC) + timedelta(hours=36),
    )
    return service


@pytest.fixture
def mock_audit():
    return MagicMock()


@pytest.fixture
def service(
    mock_credential_repo,
    mock_device_service,
    mock_token_service,
    mock_audit,
):
    return DeviceAuthService(
        credential_repo=mock_credential_repo,
        device_service=mock_device_service,
        token_service=mock_token_service,
        audit=mock_audit,
        challenge_expire_seconds=300,
    )


def test_challenge_success(service, mock_credential_repo):
    """Test successful challenge generation."""
    credential = MagicMock()
    credential.serial_number = "TEST-SN-001"
    credential.status = "pending"
    credential.pending_water_object_id = uuid4()
    mock_credential_repo.find_by_serial_number.return_value = credential

    serial, nonce = service.challenge("TEST-SN-001")

    assert serial == "TEST-SN-001"
    assert nonce is not None
    assert len(nonce) > 0
    assert credential.pending_challenge == nonce
    mock_credential_repo.flush.assert_called_once()


def test_challenge_unknown_device(service, mock_credential_repo):
    """Test challenge fails for unknown device."""
    mock_credential_repo.find_by_serial_number.side_effect = NotFoundError(
        "Device not found"
    )

    with pytest.raises(NotFoundError):
        service.challenge("UNKNOWN-SN")


def test_challenge_revoked_device(service, mock_credential_repo):
    """Test challenge fails for revoked device."""
    credential = MagicMock()
    credential.status = "revoked"
    mock_credential_repo.find_by_serial_number.return_value = credential

    with pytest.raises(AuthenticationError):
        service.challenge("REVOKED-SN")


def test_challenge_unclaimed_no_pending(service, mock_credential_repo):
    """Test challenge fails for unclaimed device with no pending claim."""
    credential = MagicMock()
    credential.status = "unclaimed"
    credential.pending_water_object_id = None
    mock_credential_repo.find_by_serial_number.return_value = credential

    with pytest.raises(BadRequestError):
        service.challenge("UNCLAIMED-SN")


def test_verify_first_claim_success(
    service, mock_credential_repo, mock_device_service, mock_token_service
):
    """Test successful first-time device claim via verify."""
    device_id = uuid4()
    credential_id = uuid4()
    water_object_id = uuid4()

    credential = MagicMock()
    credential.id = credential_id
    credential.serial_number = "TEST-SN-001"
    credential.status = "unclaimed"
    credential.claimed_device_id = None
    credential.pending_challenge = "nonce123"
    credential.challenge_expires_at = datetime.now(UTC) + timedelta(seconds=300)
    credential.pending_water_object_id = water_object_id
    credential.public_key_pem = (
        "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    )

    device = MagicMock()
    device.id = device_id
    device.external_id = "TEST-SN-001"
    device.water_object_id = water_object_id
    device.is_active = True

    mock_credential_repo.find_by_serial_number.return_value = credential
    mock_device_service.create_claimed.return_value = device

    with patch(
        "app.modules.device_identity.services.device_auth.verify_signature"
    ) as mock_verify:
        mock_verify.return_value = True

        token, token_type, _expires_at = service.verify(
            serial_number="TEST-SN-001",
            signature_der_b64="deadbeef",
        )

        assert token == "test_token"
        assert token_type == "bearer"
        assert mock_device_service.create_claimed.called


def test_verify_no_challenge(service, mock_credential_repo):
    """Test verify fails when no active challenge."""
    credential = MagicMock()
    credential.pending_challenge = None
    mock_credential_repo.find_by_serial_number.return_value = credential

    with pytest.raises(BadRequestError):
        service.verify(serial_number="TEST-SN-001", signature_der_b64="deadbeef")


def test_verify_expired_challenge(service, mock_credential_repo):
    """Test verify fails when challenge expired."""
    credential = MagicMock()
    credential.pending_challenge = "old_nonce"
    credential.challenge_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    mock_credential_repo.find_by_serial_number.return_value = credential

    with pytest.raises(GoneError):
        service.verify(serial_number="TEST-SN-001", signature_der_b64="deadbeef")


def test_verify_invalid_signature(service, mock_credential_repo, mock_token_service):
    """Test verify fails when signature doesn't match."""
    credential_id = uuid4()
    water_object_id = uuid4()

    credential = MagicMock()
    credential.id = credential_id
    credential.serial_number = "TEST-SN-001"
    credential.status = "unclaimed"
    credential.claimed_device_id = None
    credential.pending_challenge = "nonce123"
    credential.challenge_expires_at = datetime.now(UTC) + timedelta(seconds=300)
    credential.pending_water_object_id = water_object_id
    credential.public_key_pem = (
        "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    )

    mock_credential_repo.find_by_serial_number.return_value = credential

    with patch(
        "app.modules.device_identity.services.device_auth.verify_signature"
    ) as mock_verify:
        mock_verify.return_value = False

        with pytest.raises(AuthenticationError):
            service.verify(
                serial_number="TEST-SN-001",
                signature_der_b64="deadbeef",
            )


def test_verify_invalid_signature_encoding(service, mock_credential_repo):
    """Test verify fails when signature is not valid hex."""
    credential = MagicMock()
    credential.pending_challenge = "nonce123"
    credential.challenge_expires_at = datetime.now(UTC) + timedelta(seconds=300)
    mock_credential_repo.find_by_serial_number.return_value = credential

    with pytest.raises(BadRequestError):
        service.verify(
            serial_number="TEST-SN-001",
            signature_der_b64="!!!not-valid-base64!!!",
        )


def test_verify_reauth_success(
    service, mock_credential_repo, mock_device_service, mock_token_service
):
    """Test successful re-authentication of already-claimed device."""
    device_id = uuid4()
    credential_id = uuid4()
    water_object_id = uuid4()

    credential = MagicMock()
    credential.id = credential_id
    credential.serial_number = "TEST-SN-001"
    credential.status = "claimed"
    credential.claimed_device_id = device_id
    credential.pending_challenge = "nonce123"
    credential.challenge_expires_at = datetime.now(UTC) + timedelta(seconds=300)
    credential.public_key_pem = (
        "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    )

    device = MagicMock()
    device.id = device_id
    device.external_id = "TEST-SN-001"
    device.water_object_id = water_object_id

    mock_credential_repo.find_by_serial_number.return_value = credential
    mock_device_service.find_by_id_unscoped.return_value = device

    with patch(
        "app.modules.device_identity.services.device_auth.verify_signature"
    ) as mock_verify:
        mock_verify.return_value = True

        token, token_type, _expires_at = service.verify(
            serial_number="TEST-SN-001",
            signature_der_b64="deadbeef",
        )

        assert token == "test_token"
        assert token_type == "bearer"
        mock_device_service.find_by_id_unscoped.assert_called_once_with(device_id)
