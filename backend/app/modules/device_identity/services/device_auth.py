"""Device authentication challenge/verify service."""

import base64
import secrets
from datetime import UTC, datetime, timedelta

from app.core.audit import AuditPort
from app.core.errors import (
    AuthenticationError,
    BadRequestError,
    GoneError,
)
from app.modules.core_data.models.device import Device
from app.modules.core_data.services.devices import DeviceService
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.device_identity.services.signature import verify_signature
from app.modules.security.services.token import TokenService


class DeviceAuthService:
    """Handle device authentication challenges and verification."""

    def __init__(
        self,
        credential_repo: DeviceCredentialRepository,
        device_service: DeviceService,
        token_service: TokenService,
        audit: AuditPort,
        challenge_expire_seconds: int,
    ):
        self.credential_repo = credential_repo
        self.device_service = device_service
        self.token_service = token_service
        self.audit = audit
        self.challenge_expire_seconds = challenge_expire_seconds

    def challenge(self, serial_number: str) -> tuple[str, str]:
        """Generate a challenge nonce for a device to sign.

        Args:
            serial_number: Device serial number

        Returns:
            Tuple of (serial_number, challenge_nonce)

        Raises:
            NotFoundError: If credential not found
            AuthenticationError: If credential is revoked
            BadRequestError: If credential unclaimed with no pending claim
        """
        with self.credential_repo.transaction(skip_audit=True):
            credential = self.credential_repo.find_by_serial_number(serial_number)

            if credential.status == "revoked":
                raise AuthenticationError("Device is revoked")

            if (
                credential.status == "unclaimed"
                and not credential.pending_water_object_id
            ):
                raise BadRequestError("Device not claimed and no pending claim")

            nonce = secrets.token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(
                seconds=self.challenge_expire_seconds
            )

            credential.pending_challenge = nonce
            credential.challenge_expires_at = expires_at
            self.credential_repo.flush()

            return serial_number, nonce

    def verify(
        self,
        serial_number: str,
        signature_der_b64: str,
    ) -> tuple[str, str, datetime]:
        """Verify a signed challenge and return a device token.

        Args:
            serial_number: Device serial number
            signature_der_b64: Base64-encoded DER signature

        Returns:
            Tuple of (token, token_type, expires_at)

        Raises:
            NotFoundError: If credential not found
            BadRequestError: If no active challenge
            GoneError: If challenge expired
            AuthenticationError: If signature invalid
        """
        with self.credential_repo.transaction() as tx:
            credential = self.credential_repo.find_by_serial_number(serial_number)

            if not credential.pending_challenge:
                raise BadRequestError("No active challenge for this device")

            if (
                credential.challenge_expires_at
                and credential.challenge_expires_at < datetime.now(UTC)
            ):
                credential.pending_challenge = None
                credential.challenge_expires_at = None
                raise GoneError("Challenge has expired")

            try:
                signature_der = base64.b64decode(signature_der_b64)
            except Exception as err:
                raise BadRequestError("Invalid signature encoding") from err

            # Decode base64url challenge nonce to bytes before verification
            try:
                challenge_b64 = credential.pending_challenge
                # Add proper padding to make length multiple of 4
                while len(challenge_b64) % 4 != 0:
                    challenge_b64 += "="
                message = base64.urlsafe_b64decode(challenge_b64)
            except Exception as err:
                raise BadRequestError("Invalid challenge encoding") from err

            if not verify_signature(credential.public_key_pem, message, signature_der):
                raise AuthenticationError("Signature verification failed")

            credential.pending_challenge = None
            credential.challenge_expires_at = None

            if credential.claimed_device_id is None:
                device = self._handle_first_claim(credential)
                # Device creation audit already recorded inside create_claimed()
                tx.skip_audit()
            else:
                device = self._handle_reauth(credential, tx)

            token_data = {
                "sub": str(device.id),
                "sn": serial_number,
                "water_object_id": str(device.water_object_id),
            }
            token, expires_at = self.token_service.create_device_token(token_data)

            return token, "bearer", expires_at

    def _handle_first_claim(self, credential: DeviceCredential) -> Device:
        """Handle first-time device claim.

        Returns:
            The created/claimed Device object
        """
        water_object_id = credential.pending_water_object_id
        if not water_object_id:
            raise BadRequestError("No pending water object for claim")

        device = self.device_service.create_claimed(
            water_object_id=water_object_id,
            serial_number=credential.serial_number,
            device_credential_id=credential.id,
            actor_id=str(credential.id),
            actor_display_name=f"device:{credential.serial_number}",
        )

        credential.status = "claimed"
        credential.claimed_device_id = device.id
        credential.claimed_at = datetime.now(UTC)
        credential.pending_water_object_id = None

        self.credential_repo.flush()
        self.credential_repo.refresh(credential)

        return device

    def _handle_reauth(self, credential: DeviceCredential, tx) -> Device:
        """Handle re-authentication of already-claimed device.

        Returns:
            The existing Device object
        """
        tx.skip_audit()
        return self.device_service.find_by_id_unscoped(credential.claimed_device_id)
