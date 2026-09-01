"""Device lifecycle management — handles full device deletion with cascade."""

from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType
from app.modules.core_data.services.devices import DeviceService
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService


class DeviceLifecycleService:
    """Orchestrates device deletion across core_data, device_identity, telemetry."""

    def __init__(
        self,
        device_service: DeviceService,
        credential_repo: DeviceCredentialRepository,
        telemetry_service: TelemetryIngestService,
        audit: AuditPort,
    ):
        self.device_service = device_service
        self.credential_repo = credential_repo
        self.telemetry_service = telemetry_service
        self.audit = audit

    def delete_device_completely(
        self,
        device_id: UUID,
        actor_id: str,
        actor_display_name: str | None,
    ) -> None:
        """Delete a device and all related data atomically.

        Deletes:
        - All telemetry packets for this device
        - The device record (cascades measurement_points, and through them
          the normalized measurements, via FK)
        - The device credential

        All operations happen in a single transaction. If any step fails,
        the entire transaction rolls back.

        Raises:
            NotFoundError: Device not found
        """
        device = self.device_service.find_by_id_unscoped(device_id)

        with self.device_service.repo.transaction():
            # Delete telemetry packets (no FK, must be explicit)
            self.telemetry_service.delete_all_for_device(device.external_id)

            # Delete device record (cascades measurement_points via FK ondelete=CASCADE)
            self.device_service.delete_device_record(
                device_id, actor_id, actor_display_name
            )

            # Delete credential (cascades to activation_code.redeemed_by_credential_id)
            credential = self.credential_repo.get_by_id(device.device_credential_id)
            if credential:
                self.credential_repo.delete(credential)
                self.audit.record(
                    AuditEntry(
                        entity_type=EntityType.DEVICE_IDENTITY_CREDENTIAL.value,
                        entity_id=str(credential.id),
                        action="DELETE",
                        actor_id=actor_id,
                        actor_display_name=actor_display_name,
                        changes={},
                    )
                )
