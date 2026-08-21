"""Device claim intent service."""

from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError, NotFoundError
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.security.access import OrganizationAccess


class DeviceClaimService:
    """Manage device claim intents (associating credentials with water objects)."""

    def __init__(
        self,
        repo: DeviceCredentialRepository,
        water_object_service: WaterObjectService,
        device_service: DeviceService,
        audit: AuditPort,
    ):
        self.repo = repo
        self.water_object_service = water_object_service
        self.device_service = device_service
        self.audit = audit

    def request_claim(
        self,
        serial_number: str,
        water_object_id: UUID,
        org_access: OrganizationAccess,
    ) -> str:
        """Request to claim a device for a water object.

        Args:
            serial_number: Device serial number
            water_object_id: Water object to claim for
            org_access: Organization context

        Returns:
            The claim status

        Raises:
            NotFoundError: If credential or water object not found
            ConflictError: If credential already claimed or pending different object
        """
        with self.repo.transaction():
            credential = self.repo.find_by_serial_number(serial_number)

            self.water_object_service.get_by_id(water_object_id, org_access)

            if credential.status == "claimed":
                raise ConflictError(f"Device {serial_number} already claimed")

            if (
                credential.pending_water_object_id
                and credential.pending_water_object_id != water_object_id
            ):
                raise ConflictError(
                    f"Device {serial_number} has a pending claim for a different object"
                )

            old_state = {
                "status": credential.status,
                "pending_water_object_id": credential.pending_water_object_id,
            }

            credential.status = "pending"
            credential.pending_water_object_id = water_object_id

            self.repo.flush()
            self.repo.refresh(credential)

            new_state = {
                "status": credential.status,
                "pending_water_object_id": credential.pending_water_object_id,
            }

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.DEVICE_IDENTITY_CREDENTIAL.value,
                    entity_id=str(credential.id),
                    action="CLAIM_INTENT",
                    actor_id=str(org_access.actor.id),
                    actor_display_name=org_access.actor.email,
                    changes=calculate_delta(old_state, new_state),
                    context_type="organization",
                    context_id=str(org_access.organization_id),
                )
            )

            return credential.status

    def get_claim_status(
        self,
        serial_number: str,
        org_access: OrganizationAccess,
    ) -> str:
        """Get the current claim status of a device.

        Args:
            serial_number: Device serial number
            org_access: Organization context

        Returns:
            The claim status

        Raises:
            NotFoundError: If credential not found or not visible to org
        """
        credential = self.repo.find_by_serial_number(serial_number)

        if credential.status == "claimed":
            device_id = credential.claimed_device_id
            if not device_id:
                raise NotFoundError("Claimed device not found")
            device = self.device_service.find_by_id_unscoped(device_id)
            try:
                self.water_object_service.get_by_id(device.water_object_id, org_access)
            except NotFoundError as err:
                raise NotFoundError(
                    f"Device {serial_number} not visible to this organization"
                ) from err
        elif credential.pending_water_object_id:
            try:
                self.water_object_service.get_by_id(
                    credential.pending_water_object_id,
                    org_access,
                )
            except NotFoundError as err:
                raise NotFoundError(
                    f"Device {serial_number} not visible to this organization"
                ) from err
        else:
            raise NotFoundError(
                f"Device {serial_number} has no claim in this organization"
            )

        return credential.status
