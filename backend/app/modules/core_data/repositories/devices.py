"""Device repository for data access."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.water_object import WaterObject


class DeviceRepository(SQLRepository):
    """Repository for Device model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, device_id: UUID) -> Device | None:
        """Get device by ID."""
        return self.session.query(Device).filter(Device.id == device_id).first()

    def find_by_id(self, device_id: UUID) -> Device:
        """Find device by ID or raise NotFoundError."""
        device = self.get_by_id(device_id)
        if not device:
            raise NotFoundError("Device not found")
        return device

    def get_in_organization(
        self, device_id: UUID, organization_id: UUID
    ) -> Device | None:
        """Get device by ID within organization scope."""
        return (
            self.session.query(Device)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .filter(
                Device.id == device_id, WaterObject.organization_id == organization_id
            )
            .first()
        )

    def find_in_organization(self, device_id: UUID, organization_id: UUID) -> Device:
        """Find device by ID within organization or raise NotFoundError."""
        device = self.get_in_organization(device_id, organization_id)
        if not device:
            raise NotFoundError("Device not found")
        return device

    def get_by_external_id(self, external_id: str) -> Device | None:
        """Get device by external ID."""
        return (
            self.session.query(Device).filter(Device.external_id == external_id).first()
        )

    def list_all_with_org_filter(
        self,
        organization_id: UUID | None = None,
        water_object_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Device]:
        """List devices with org isolation via water_object join."""
        query = self.session.query(Device)

        if water_object_id is not None:
            query = query.filter(Device.water_object_id == water_object_id)

        if organization_id is not None:
            query = query.join(
                WaterObject, Device.water_object_id == WaterObject.id
            ).filter(WaterObject.organization_id == organization_id)

        return query.order_by(Device.external_id).offset(skip).limit(limit).all()

    def count_with_org_filter(
        self,
        organization_id: UUID | None = None,
        water_object_id: UUID | None = None,
    ) -> int:
        """Count devices with org isolation."""
        query = self.session.query(func.count(Device.id))

        if water_object_id is not None:
            query = query.filter(Device.water_object_id == water_object_id)

        if organization_id is not None:
            query = query.join(
                WaterObject, Device.water_object_id == WaterObject.id
            ).filter(WaterObject.organization_id == organization_id)

        return query.scalar() or 0

    def create(
        self,
        water_object_id: UUID,
        external_id: str,
        hashed_secret: str,
        firmware_version: str | None = None,
    ) -> Device:
        """Create new device."""
        device = Device(
            water_object_id=water_object_id,
            external_id=external_id,
            hashed_secret=hashed_secret,
            firmware_version=firmware_version,
        )
        self.session.add(device)
        return device

    def update(
        self,
        device: Device,
        *,
        firmware_version: str | None = None,
        is_active: bool | None = None,
    ) -> Device:
        """Update device fields."""
        if firmware_version is not None:
            device.firmware_version = firmware_version
        if is_active is not None:
            device.is_active = is_active
        return device

    def delete(self, device: Device) -> None:
        """Delete device."""
        self.session.delete(device)
