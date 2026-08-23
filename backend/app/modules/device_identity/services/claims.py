"""Device claim service — assign devices to water objects."""

from uuid import UUID

from app.core.errors import NotFoundError
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.security.access import OrganizationAccess


class DeviceClaimService:
    """Manage device assignment to water objects."""

    def __init__(
        self,
        water_object_service: WaterObjectService,
        device_service: DeviceService,
    ):
        self.water_object_service = water_object_service
        self.device_service = device_service

    def request_claim(
        self,
        serial_number: str,
        water_object_id: UUID,
        org_access: OrganizationAccess,
    ) -> str:
        """Assign a device to a water object.

        Args:
            serial_number: Device serial number (external_id)
            water_object_id: Water object to assign to
            org_access: Organization context

        Returns:
            "assigned" on success

        Raises:
            NotFoundError: If device or water object not found
            ConflictError: If device already assigned
        """
        self.water_object_service.get_by_id(water_object_id, org_access)

        self.device_service.assign_water_object(
            external_id=serial_number,
            water_object_id=water_object_id,
            actor_id=str(org_access.actor.id),
            actor_display_name=org_access.actor.email,
            context_id=org_access.organization_id,
        )

        return "assigned"

    def get_claim_status(
        self,
        serial_number: str,
        org_access: OrganizationAccess,
    ) -> str:
        """Get the claim/assignment status of a device in this organization.

        Returns "assigned" if the device is assigned to a water object in this org,
        or raises 404 if not found / not assigned / assigned to different org.

        Args:
            serial_number: Device serial number
            org_access: Organization context

        Returns:
            "assigned"

        Raises:
            NotFoundError: If device not found or not visible to org
        """
        device = self.device_service.get_by_external_id(serial_number)
        if not device or device.water_object_id is None:
            raise NotFoundError(f"Device {serial_number} not found or not assigned")

        self.water_object_service.get_by_id(device.water_object_id, org_access)

        return "assigned"
