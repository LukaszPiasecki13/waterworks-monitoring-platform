"""Device activation code generation and redemption service."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType
from app.core.config import Settings
from app.core.errors import ConflictError, GoneError, NotFoundError
from app.modules.device_identity.models.device_activation_code import (
    DeviceActivationCode,
)
from app.modules.device_identity.repositories.device_activation_codes import (
    DeviceActivationCodeRepository,
)
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.device_identity.services.signature import (
    public_key_point_hex_to_pem,
)

_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
_CODE_LENGTH = 10
_GROUP_SIZE = 4


def _generate_code() -> str:
    """Generate a random activation code."""
    raw = "".join(secrets.choice(_ALPHABET) for _ in range(_CODE_LENGTH))
    return "-".join(raw[i : i + _GROUP_SIZE] for i in range(0, len(raw), _GROUP_SIZE))


def _hash_code(code: str) -> str:
    """Hash an activation code using SHA-256."""
    return hashlib.sha256(code.strip().upper().encode()).hexdigest()


class DeviceActivationCodeService:
    """Service for device activation code generation and redemption."""

    def __init__(
        self,
        code_repo: DeviceActivationCodeRepository,
        credential_repo: DeviceCredentialRepository,
        audit: AuditPort,
        settings: Settings,
    ):
        self.code_repo = code_repo
        self.credential_repo = credential_repo
        self.audit = audit
        self.settings = settings

    def generate(self, creator_user_id: UUID) -> tuple[DeviceActivationCode, str]:
        """Generate a new activation code.

        Returns:
            Tuple of (DeviceActivationCode model, plaintext code string)
        """
        code = _generate_code()
        code_hash = _hash_code(code)

        expires_at = datetime.now(UTC) + timedelta(
            seconds=self.settings.device_activation_code_expire_seconds
        )

        with self.code_repo.transaction():
            activation_code = self.code_repo.create(
                code_hash=code_hash,
                expires_at=expires_at,
                created_by_user_id=creator_user_id,
            )
            self.code_repo.flush()
            self.code_repo.refresh(activation_code)

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.DEVICE_IDENTITY_ACTIVATION_CODE.value,
                    entity_id=str(activation_code.id),
                    action="GENERATE",
                    actor_id=str(creator_user_id),
                    actor_display_name=None,
                    changes={},
                )
            )

        return activation_code, code

    def get_status(self, code_id: UUID) -> dict:
        """Get status of an activation code.

        Returns dict with: id, status (effective), expires_at, used_at,
        serial_number (or None)
        """
        code = self.code_repo.find_by_id(code_id)

        status = code.status
        if status == "unused" and code.expires_at < datetime.now(UTC):
            status = "expired"

        serial_number = None
        if code.redeemed_by_credential_id:
            credential = self.credential_repo.get_by_id(code.redeemed_by_credential_id)
            if credential:
                serial_number = credential.serial_number

        return {
            "id": code.id,
            "status": status,
            "expires_at": code.expires_at,
            "used_at": code.used_at,
            "serial_number": serial_number,
        }

    def cancel(
        self, code_id: UUID, actor_id: str, actor_display_name: str | None
    ) -> dict:
        """Cancel an unused activation code.

        Args:
            code_id: ID of code to cancel
            actor_id: Audit actor ID
            actor_display_name: Audit actor display name

        Raises:
            GoneError: If code is expired or already cancelled
            ConflictError: If code is already used
        """
        with self.code_repo.transaction():
            code = self.code_repo.find_by_id(code_id)

            if code.status == "used":
                raise ConflictError("Cannot cancel a used code")

            if code.status == "cancelled":
                raise ConflictError("Code is already cancelled")

            if code.expires_at < datetime.now(UTC):
                raise GoneError(
                    "Cannot cancel an expired code",
                    code="ACTIVATION_CODE_EXPIRED",
                )

            old_status = code.status
            code.status = "cancelled"
            self.code_repo.flush()

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.DEVICE_IDENTITY_ACTIVATION_CODE.value,
                    entity_id=str(code.id),
                    action="CANCEL",
                    actor_id=actor_id,
                    actor_display_name=actor_display_name,
                    changes={"status": (old_status, "cancelled")},
                )
            )

        return {
            "id": code.id,
            "status": code.status,
        }

    def redeem(
        self, serial_number: str, activation_code: str, public_key_point_hex: str
    ) -> dict:
        """Redeem an activation code for device registration.

        Returns dict with: serial_number, status, next_action, already_registered (bool)

        Raises:
            NotFoundError: Code not found
            GoneError: Code expired or cancelled
            ConflictError: Code already used by different device, or device
                already registered
            BadRequestError: Invalid key format
        """
        code_hash = _hash_code(activation_code)

        with self.code_repo.transaction():
            code = self.code_repo.get_by_code_hash(code_hash)
            if not code:
                raise NotFoundError(
                    "Activation code not found", code="ACTIVATION_CODE_NOT_FOUND"
                )

            if code.status == "cancelled":
                raise GoneError(
                    "Activation code was cancelled", code="ACTIVATION_CODE_CANCELLED"
                )

            is_expired = code.status == "unused" and code.expires_at < datetime.now(UTC)
            if is_expired:
                raise GoneError(
                    "Activation code has expired", code="ACTIVATION_CODE_EXPIRED"
                )

            if code.status == "used":
                credential = self.credential_repo.get_by_id(
                    code.redeemed_by_credential_id
                )
                if not credential:
                    raise ConflictError("Credential for this code not found")

                public_key_pem = public_key_point_hex_to_pem(public_key_point_hex)
                if (
                    credential.serial_number == serial_number
                    and credential.public_key_pem == public_key_pem
                ):
                    return {
                        "serial_number": serial_number,
                        "status": "already_registered",
                        "next_action": "perform_auth",
                        "already_registered": True,
                    }

                raise ConflictError(
                    "This code was already used by a different device",
                    code="ACTIVATION_CODE_ALREADY_USED",
                )

            existing_credential = self.credential_repo.get_by_serial_number(
                serial_number
            )
            if existing_credential:
                raise ConflictError(
                    "Device with this serial number is already registered",
                    code="DEVICE_ALREADY_REGISTERED",
                )

            public_key_pem = public_key_point_hex_to_pem(public_key_point_hex)

            credential = self.credential_repo.create(
                serial_number=serial_number,
                public_key_pem=public_key_pem,
                status="unclaimed",
                activation_code_id=code.id,
            )
            try:
                self.credential_repo.flush()
            except IntegrityError as e:
                if "device_credentials_serial_number_key" in str(e):
                    raise ConflictError(
                        "Device with this serial number is already registered",
                        code="DEVICE_ALREADY_REGISTERED",
                    ) from e
                raise
            self.credential_repo.refresh(credential)

            code.status = "used"
            code.used_at = datetime.now(UTC)
            code.redeemed_by_credential_id = credential.id
            self.code_repo.flush()

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.DEVICE_IDENTITY_ACTIVATION_CODE.value,
                    entity_id=str(code.id),
                    action="REDEEM",
                    actor_id=None,
                    actor_display_name=None,
                    changes={"status": ("unused", "used")},
                )
            )

        return {
            "serial_number": serial_number,
            "status": "unclaimed",
            "next_action": "perform_auth",
            "already_registered": False,
        }
