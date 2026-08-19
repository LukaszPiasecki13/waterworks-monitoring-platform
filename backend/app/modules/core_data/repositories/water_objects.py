"""Water object repository for data access."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.water_object import WaterObject


class WaterObjectRepository(SQLRepository):
    """Repository for WaterObject model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, obj_id: UUID) -> WaterObject | None:
        """Get water object by ID."""
        return self.session.query(WaterObject).filter(WaterObject.id == obj_id).first()

    def find_by_id(self, obj_id: UUID) -> WaterObject:
        """Find water object by ID or raise NotFoundError."""
        obj = self.get_by_id(obj_id)
        if not obj:
            raise NotFoundError("Water object not found")
        return obj

    def get_in_organization(
        self, obj_id: UUID, organization_id: UUID
    ) -> WaterObject | None:
        """Get water object by ID within organization scope."""
        return (
            self.session.query(WaterObject)
            .filter(
                WaterObject.id == obj_id, WaterObject.organization_id == organization_id
            )
            .first()
        )

    def find_in_organization(self, obj_id: UUID, organization_id: UUID) -> WaterObject:
        """Find water object by ID within organization or raise NotFoundError."""
        obj = self.get_in_organization(obj_id, organization_id)
        if not obj:
            raise NotFoundError("Water object not found")
        return obj

    def list_all(
        self,
        organization_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[WaterObject]:
        """List water objects by organization."""
        query = self.session.query(WaterObject)
        if organization_id is not None:
            query = query.filter(WaterObject.organization_id == organization_id)
        return query.order_by(WaterObject.name).offset(skip).limit(limit).all()

    def count(self, organization_id: UUID | None = None) -> int:
        """Count water objects."""
        query = self.session.query(func.count(WaterObject.id))
        if organization_id is not None:
            query = query.filter(WaterObject.organization_id == organization_id)
        return query.scalar() or 0

    def create(
        self,
        organization_id: UUID,
        name: str,
        object_type: str,
        location_description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> WaterObject:
        """Create new water object."""
        obj = WaterObject(
            organization_id=organization_id,
            name=name,
            object_type=object_type,
            location_description=location_description,
            latitude=latitude,
            longitude=longitude,
        )
        self.session.add(obj)
        return obj

    def update(
        self,
        obj: WaterObject,
        *,
        name: str | None = None,
        object_type: str | None = None,
        location_description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        is_active: bool | None = None,
    ) -> WaterObject:
        """Update water object fields."""
        if name is not None:
            obj.name = name
        if object_type is not None:
            obj.object_type = object_type
        if location_description is not None:
            obj.location_description = location_description
        if latitude is not None:
            obj.latitude = latitude
        if longitude is not None:
            obj.longitude = longitude
        if is_active is not None:
            obj.is_active = is_active
        return obj

    def delete(self, obj: WaterObject) -> None:
        """Delete water object."""
        self.session.delete(obj)
