"""Measurement point repository for data access."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.core_data.models.water_object import WaterObject


class MeasurementPointRepository(SQLRepository):
    """Repository for MeasurementPoint model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, point_id: UUID) -> MeasurementPoint | None:
        """Get measurement point by ID."""
        return self.session.query(MeasurementPoint).filter(MeasurementPoint.id == point_id).first()

    def find_by_id(self, point_id: UUID) -> MeasurementPoint:
        """Find measurement point by ID or raise NotFoundError."""
        point = self.get_by_id(point_id)
        if not point:
            raise NotFoundError("Measurement point not found")
        return point

    def get_by_device_and_external_id(
        self, device_id: int, external_id: str
    ) -> MeasurementPoint | None:
        """Get measurement point by device and external ID."""
        return (
            self.session.query(MeasurementPoint)
            .filter(
                MeasurementPoint.device_id == device_id,
                MeasurementPoint.external_id == external_id,
            )
            .first()
        )

    def list_all_with_org_filter(
        self,
        organization_id: UUID | None = None,
        device_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MeasurementPoint]:
        """List measurement points with org isolation via device→water_object join."""
        query = self.session.query(MeasurementPoint)

        if device_id is not None:
            query = query.filter(MeasurementPoint.device_id == device_id)

        if organization_id is not None:
            query = (
                query.join(Device, MeasurementPoint.device_id == Device.id)
                .join(WaterObject, Device.water_object_id == WaterObject.id)
                .filter(WaterObject.organization_id == organization_id)
            )

        return query.order_by(MeasurementPoint.external_id).offset(skip).limit(limit).all()

    def count_with_org_filter(
        self,
        organization_id: UUID | None = None,
        device_id: UUID | None = None,
    ) -> int:
        """Count measurement points with org isolation."""
        query = self.session.query(func.count(MeasurementPoint.id))

        if device_id is not None:
            query = query.filter(MeasurementPoint.device_id == device_id)

        if organization_id is not None:
            query = (
                query.join(Device, MeasurementPoint.device_id == Device.id)
                .join(WaterObject, Device.water_object_id == WaterObject.id)
                .filter(WaterObject.organization_id == organization_id)
            )

        return query.scalar() or 0

    def create(
        self,
        device_id: int,
        external_id: str,
        point_type: str,
        unit: str,
        min_technical: float | None = None,
        max_technical: float | None = None,
    ) -> MeasurementPoint:
        """Create new measurement point."""
        point = MeasurementPoint(
            device_id=device_id,
            external_id=external_id,
            point_type=point_type,
            unit=unit,
            min_technical=min_technical,
            max_technical=max_technical,
        )
        self.session.add(point)
        return point

    def update(
        self,
        point: MeasurementPoint,
        *,
        point_type: str | None = None,
        unit: str | None = None,
        min_technical: float | None = None,
        max_technical: float | None = None,
        is_active: bool | None = None,
    ) -> MeasurementPoint:
        """Update measurement point fields."""
        if point_type is not None:
            point.point_type = point_type
        if unit is not None:
            point.unit = unit
        if min_technical is not None:
            point.min_technical = min_technical
        if max_technical is not None:
            point.max_technical = max_technical
        if is_active is not None:
            point.is_active = is_active
        return point

    def delete(self, point: MeasurementPoint) -> None:
        """Delete measurement point."""
        self.session.delete(point)
