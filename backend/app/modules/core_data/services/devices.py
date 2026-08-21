"""Device management service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.core_data.models.device import Device
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.devices import DeviceUpdateRequest
from app.modules.security.access import OrganizationAccess


class DeviceService:
    """Service for device management operations.

    Callers are expected to have already validated organization membership
    and permissions (see `require_org_access`) and pass in the resulting
    `OrganizationAccess`.
    """

    def __init__(
        self,
        repo: DeviceRepository,
        water_object_repo: WaterObjectRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.water_object_repo = water_object_repo
        self.audit = audit

    def _state(self, device) -> dict:
        return {
            "external_id": device.external_id,
            "water_object_id": device.water_object_id,
            "device_credential_id": device.device_credential_id,
            "firmware_version": device.firmware_version,
            "is_active": device.is_active,
        }

    def _record_audit(
        self,
        action: str,
        device,
        actor_id: str,
        actor_display_name: str | None,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_DEVICE.value,
                entity_id=str(device.id),
                action=action,
                actor_id=actor_id,
                actor_display_name=actor_display_name,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, device_id: UUID, org_access: OrganizationAccess):
        """Get device by ID."""
        return self.repo.find_in_organization(device_id, org_access.organization_id)

    def find_by_id_unscoped(self, device_id: UUID) -> Device:
        """Find device by ID without org scope (for device_identity internal use).

        Raises NotFoundError if not found.
        """
        return self.repo.find_by_id(device_id)

    def get_by_external_id(self, external_id: str) -> Device | None:
        """Get device by external ID, returns None if not found."""
        return self.repo.get_by_external_id(external_id)

    def list_all(self, query, org_access: OrganizationAccess):
        """List devices in organization."""
        devices = self.repo.list_all_with_org_filter(
            organization_id=org_access.organization_id,
            water_object_id=query.water_object_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count_with_org_filter(
            organization_id=org_access.organization_id,
            water_object_id=query.water_object_id,
        )
        return devices, count

    def create_claimed(
        self,
        *,
        water_object_id: UUID,
        serial_number: str,
        device_credential_id: UUID,
        actor_id: str,
        actor_display_name: str | None,
    ) -> Device:
        """Create a device claimed by a credential.

        Called by device_identity on first verify.

        Args:
            water_object_id: Water object the device belongs to
            serial_number: Device serial number (external_id)
            device_credential_id: The credential UUID
            actor_id: Audit actor ID
            actor_display_name: Audit actor display name

        Returns:
            The created device
        """
        with self.repo.transaction():
            device = self.repo.create(
                water_object_id=water_object_id,
                external_id=serial_number,
                device_credential_id=device_credential_id,
                firmware_version=None,
            )
            self.repo.flush()
            self.repo.refresh(device)
            self._record_audit(
                "CREATE",
                device,
                actor_id,
                actor_display_name,
                {},
                self._state(device),
            )
            return device

    def update(
        self,
        device_id: UUID,
        request: DeviceUpdateRequest,
        org_access: OrganizationAccess,
    ):
        """Update device."""
        with self.repo.transaction() as tx:
            device = self.repo.find_in_organization(
                device_id, org_access.organization_id
            )
            old_state = self._state(device)
            self.repo.update(device, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(device)
            new_state = self._state(device)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return device
            self._record_audit(
                "UPDATE",
                device,
                str(org_access.actor.id),
                org_access.actor.email,
                old_state,
                new_state,
            )
            return device

    def delete(self, device_id: UUID, org_access: OrganizationAccess) -> None:
        """Delete device."""
        try:
            with self.repo.transaction():
                device = self.repo.find_in_organization(
                    device_id, org_access.organization_id
                )
                old_state = self._state(device)
                self.repo.delete(device)
                self._record_audit(
                    "DELETE",
                    device,
                    str(org_access.actor.id),
                    org_access.actor.email,
                    old_state,
                    {},
                )
        except IntegrityError as err:
            raise ConflictError(
                "Cannot delete device with related measurement points"
            ) from err
