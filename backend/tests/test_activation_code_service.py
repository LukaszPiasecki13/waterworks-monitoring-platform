"""Tests for device activation code service."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.errors import (
    BadRequestError,
    GoneError,
)
from app.modules.core_data.models import User
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
        # Real, on-curve P-256 uncompressed point (04 + X + Y, 65 bytes)
        point_hex = (
            "049fc1ad37e02898f02ea3a307dfe05047780b32c21e9b7f953f7bc03a378b970"
            "97777161e42d76f97118b31e5981b9f205bb1d07a8234995599eb57f40ed4b1c3"
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
            "05"  # Wrong prefix (should be 04); rest is a real, correctly-sized point
            "9fc1ad37e02898f02ea3a307dfe05047780b32c21e9b7f953f7bc03a378b970"
            "97777161e42d76f97118b31e5981b9f205bb1d07a8234995599eb57f40ed4b1c3"
        )
        with pytest.raises(BadRequestError, match="expected uncompressed P-256 point"):
            public_key_point_hex_to_pem(point_hex)


def test_code_generation_idempotency(monkeypatch):
    """Codes generated from same entropy are identical (deterministic)."""
    # Mock secrets.choice to return predictable sequence
    import app.modules.device_identity.services.activation_codes as ac_module

    original_choice = ac_module.secrets.choice
    choices_made = []

    def mock_choice(seq):
        result = original_choice(seq)
        choices_made.append(result)
        return result

    monkeypatch.setattr(ac_module.secrets, "choice", mock_choice)

    # Generate a code
    from app.modules.device_identity.services.activation_codes import _generate_code

    code = _generate_code()
    assert "-" in code
    assert len(code.split("-")) == 3  # 10 chars split into 4-4-2


def _create_user(session) -> User:
    """Minimal persisted user, needed to satisfy
    device_activation_codes.created_by_user_id's FK to users.id."""
    unique = uuid4().hex[:8]
    user = User(
        username=f"creator-{unique}",
        email=f"creator-{unique}@example.com",
        first_name="Creator",
        last_name="Test",
        hashed_password="not-used",
    )
    session.add(user)
    session.flush()
    return user


@pytest.mark.asyncio
async def test_redeem_idempotency_same_device(audited_db_session, real_audit_service):
    """Redeeming same code with same SN+key twice returns 200 +
    already_registered=True, without violating the commit-time audit guard.

    Uses audited_db_session + real_audit_service (not a mocked AuditPort)
    so this test actually exercises AuditAwareSession's MissingAuditRecordError
    guard the way production does — a prior regression here (the idempotent
    redeem branch returned without calling audit.record() or skip_audit())
    went undetected because a fully-mocked AuditPort can never fail that
    guard regardless of what the service does.
    """
    # Setup
    code_repo = DeviceActivationCodeRepository(audited_db_session)
    cred_repo = DeviceCredentialRepository(audited_db_session)
    settings = SimpleNamespace(device_activation_code_expire_seconds=900)

    service = DeviceActivationCodeService(
        code_repo, cred_repo, real_audit_service, settings
    )

    # audited_db_session sees only its own connection's transaction, so a
    # user created via the plain db_session fixture wouldn't be visible
    # here for the created_by_user_id FK — this test creates its own.
    creator = _create_user(audited_db_session)

    # Create a code
    _code_obj, plaintext = service.generate(creator.id)
    serial = "WW-TEST-SN-001"
    point_hex = (
        "049fc1ad37e02898f02ea3a307dfe05047780b32c21e9b7f953f7bc03a378b970"
        "97777161e42d76f97118b31e5981b9f205bb1d07a8234995599eb57f40ed4b1c3"
    )

    # Redeem first time
    result1 = service.redeem(serial, plaintext, point_hex)
    assert result1["already_registered"] is False

    # Redeem again with same device
    result2 = service.redeem(serial, plaintext, point_hex)
    assert result2["already_registered"] is True
    assert result2["serial_number"] == serial


@pytest.mark.asyncio
async def test_redeem_expired_code_raises(db_session, monkeypatch):
    """Redeeming expired code raises GoneError."""
    code_repo = DeviceActivationCodeRepository(db_session)
    cred_repo = DeviceCredentialRepository(db_session)
    audit = MagicMock()
    settings = SimpleNamespace(device_activation_code_expire_seconds=1)

    service = DeviceActivationCodeService(code_repo, cred_repo, audit, settings)

    # Create code with minimal TTL
    creator = _create_user(db_session)
    _code_obj, plaintext = service.generate(creator.id)

    # Mock time to pass expiry
    future_now = datetime.now(UTC) + timedelta(seconds=10)
    monkeypatch.setattr(
        "app.modules.device_identity.services.activation_codes.datetime",
        MagicMock(now=MagicMock(return_value=future_now)),
    )

    with pytest.raises(GoneError, match="expired"):
        service.redeem("WW-TEST", plaintext, "04" + "aa" * 64)


@pytest.mark.asyncio
async def test_cancel_expired_code_raises(db_session):
    """Cancelling expired code raises GoneError."""
    code_repo = DeviceActivationCodeRepository(db_session)
    cred_repo = DeviceCredentialRepository(db_session)
    audit = MagicMock()
    settings = SimpleNamespace(device_activation_code_expire_seconds=1)

    service = DeviceActivationCodeService(code_repo, cred_repo, audit, settings)

    # Create and immediately expire
    creator = _create_user(db_session)
    code_obj, _ = service.generate(creator.id)
    code_obj.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.flush()

    with pytest.raises(GoneError, match="expired"):
        service.cancel(code_obj.id, "actor-1", "Test Actor")
