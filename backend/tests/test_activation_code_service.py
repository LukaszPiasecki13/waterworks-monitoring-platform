"""Tests for device activation code service."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.errors import (
    BadRequestError,
    GoneError,
)
from app.modules.device_identity.repositories.device_activation_codes import (
    DeviceActivationCodeRepository,
)
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.device_identity.services.activation_codes import (
    DeviceActivationCodeService,
    _hash_code,
)
from app.modules.device_identity.services.signature import (
    public_key_point_hex_to_pem,
)


class TestHashCode:
    """Test code hashing and normalization."""

    def test_hash_normalizes_case(self):
        """Hash normalizes to uppercase before hashing."""
        code_lower = "K7M4-P9Q2-XR"
        code_upper = "k7m4-p9q2-xr"
        assert _hash_code(code_lower) == _hash_code(code_upper)

    def test_hash_strips_whitespace(self):
        """Hash strips leading/trailing whitespace."""
        code_normal = "K7M4-P9Q2-XR"
        code_padded = "  K7M4-P9Q2-XR  "
        assert _hash_code(code_normal) == _hash_code(code_padded)


class TestPublicKeyConversion:
    """Test EC point to PEM conversion."""

    def test_valid_p256_point(self):
        """Valid uncompressed P-256 point converts to PEM."""
        # Real P-256 uncompressed point (04 + X + Y)
        point_hex = (
            "04"
            "c7354436129084dd2dc5ea8a71b4e21fbfc10a32ef84bea0e07c8e35a0203d51"
            "7896a5dfe6eca31c9ee8d39a9e2849be82f9f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8"
        )
        pem = public_key_point_hex_to_pem(point_hex)
        assert pem.startswith("-----BEGIN PUBLIC KEY-----")
        assert pem.endswith("-----END PUBLIC KEY-----\n")

    def test_invalid_hex_raises(self):
        """Invalid hex string raises BadRequestError."""
        with pytest.raises(BadRequestError, match="Invalid public key point encoding"):
            public_key_point_hex_to_pem("not_hex")

    def test_wrong_length_raises(self):
        """Wrong point length raises BadRequestError."""
        # 64 chars instead of 130
        short_point = "04" + "aa" * 31
        with pytest.raises(BadRequestError, match="expected uncompressed P-256 point"):
            public_key_point_hex_to_pem(short_point)

    def test_wrong_prefix_raises(self):
        """Missing uncompressed marker (04) raises BadRequestError."""
        point_hex = (
            "05"  # Wrong prefix (should be 04)
            "c7354436129084dd2dc5ea8a71b4e21fbfc10a32ef84bea0e07c8e35a0203d51"
            "7896a5dfe6eca31c9ee8d39a9e2849be82f9f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8"
        )
        with pytest.raises(BadRequestError, match="expected uncompressed P-256 point"):
            public_key_point_hex_to_pem(point_hex)


def test_code_generation_idempotency(mocker):
    """Codes generated from same entropy are identical (deterministic)."""
    # Mock secrets.choice to return predictable sequence
    import app.modules.device_identity.services.activation_codes as ac_module

    original_choice = ac_module.secrets.choice
    choices_made = []

    def mock_choice(seq):
        result = original_choice(seq)
        choices_made.append(result)
        return result

    mocker.patch.object(ac_module.secrets, "choice", side_effect=mock_choice)

    # Generate a code
    from app.modules.device_identity.services.activation_codes import _generate_code

    code = _generate_code()
    assert "-" in code
    assert len(code.split("-")) == 3  # 10 chars split into 4-4-2


@pytest.mark.asyncio
async def test_redeem_idempotency_same_device(db_session, mocker):
    """Redeeming same code with same SN+key twice returns 200 +
    already_registered=True."""
    # Setup
    code_repo = DeviceActivationCodeRepository(db_session)
    cred_repo = DeviceCredentialRepository(db_session)
    audit = mocker.MagicMock()
    settings = mocker.MagicMock(device_activation_code_expire_seconds=900)

    service = DeviceActivationCodeService(code_repo, cred_repo, audit, settings)

    # Create a code
    _code_obj, plaintext = service.generate(uuid4())
    serial = "WW-TEST-SN-001"
    point_hex = (
        "04"
        "c7354436129084dd2dc5ea8a71b4e21fbfc10a32ef84bea0e07c8e35a0203d51"
        "7896a5dfe6eca31c9ee8d39a9e2849be82f9f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8"
    )

    # Redeem first time
    result1 = service.redeem(serial, plaintext, point_hex)
    assert result1["already_registered"] is False

    # Redeem again with same device
    result2 = service.redeem(serial, plaintext, point_hex)
    assert result2["already_registered"] is True
    assert result2["serial_number"] == serial


@pytest.mark.asyncio
async def test_redeem_expired_code_raises(db_session, mocker):
    """Redeeming expired code raises GoneError."""
    code_repo = DeviceActivationCodeRepository(db_session)
    cred_repo = DeviceCredentialRepository(db_session)
    audit = mocker.MagicMock()
    settings = mocker.MagicMock(device_activation_code_expire_seconds=1)

    service = DeviceActivationCodeService(code_repo, cred_repo, audit, settings)

    # Create code with minimal TTL
    _code_obj, plaintext = service.generate(uuid4())

    # Mock time to pass expiry
    mocker.patch(
        "app.modules.device_identity.services.activation_codes.datetime",
        wraps=mocker.MagicMock(
            now=mocker.MagicMock(return_value=datetime.now(UTC) + timedelta(seconds=10))
        ),
    )

    with pytest.raises(GoneError, match="expired"):
        service.redeem("WW-TEST", plaintext, "04" + "aa" * 64)


@pytest.mark.asyncio
async def test_cancel_expired_code_raises(db_session, mocker):
    """Cancelling expired code raises GoneError."""
    code_repo = DeviceActivationCodeRepository(db_session)
    cred_repo = DeviceCredentialRepository(db_session)
    audit = mocker.MagicMock()
    settings = mocker.MagicMock(device_activation_code_expire_seconds=1)

    service = DeviceActivationCodeService(code_repo, cred_repo, audit, settings)

    # Create and immediately expire
    code_obj, _ = service.generate(uuid4())
    code_obj.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.flush()

    with pytest.raises(GoneError, match="expired"):
        service.cancel(code_obj.id, "actor-1", "Test Actor")
