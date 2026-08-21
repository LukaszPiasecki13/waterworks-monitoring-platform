"""Device provisioning service."""

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.security.access import PlatformContext


class DeviceProvisioningService:
    """Register provisioned device credentials (public keys)."""

    def __init__(
        self,
        repo: DeviceCredentialRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.audit = audit

    def register(
        self,
        serial_number: str,
        public_key_pem: str,
        platform_ctx: PlatformContext,
    ) -> DeviceCredential:
        """Register a new device credential.

        Args:
            serial_number: Device serial number (unique)
            public_key_pem: PEM-encoded EC P-256 public key
            platform_ctx: Platform operator context

        Returns:
            The created credential

        Raises:
            ConflictError: If credential with this serial already exists
        """
        with self.repo.transaction():
            if self.repo.get_by_serial_number(serial_number):
                raise ConflictError(f"Device {serial_number} already registered")

            credential = self.repo.create(
                serial_number=serial_number,
                public_key_pem=public_key_pem,
                status="unclaimed",
            )
            self.repo.flush()
            self.repo.refresh(credential)

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.DEVICE_IDENTITY_CREDENTIAL.value,
                    entity_id=str(credential.id),
                    action="REGISTER",
                    actor_id=str(platform_ctx.actor.id),
                    actor_display_name=platform_ctx.actor.email,
                    changes=calculate_delta(
                        {},
                        {
                            "serial_number": serial_number,
                            "status": "unclaimed",
                        },
                    ),
                )
            )

            return credential
