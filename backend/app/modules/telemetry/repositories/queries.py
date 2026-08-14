"""Repository for telemetry data queries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SA_UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.telemetry.models.measurement_packet import TelemetryPacket


class TelemetryQueryRepository(SQLRepository):
    """Query-side repository for telemetry data."""

    def __init__(self, session: Session):
        super().__init__(session)

    def list_object_ids(
        self,
        org_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """List unique objects, grouped by water_object_id with their latest
        contact time.

        Joins: TelemetryPacket -> Device -> WaterObject -> Organization
        Returns list of dicts with keys: object_id, org_id, name,
        last_contact_at, last_device_id.
        Sorted by last_contact_at DESC (most recent first).
        """
        stmt = (
            select(
                WaterObject.id.cast(SA_UUID).label("object_id"),
                Organization.id.cast(SA_UUID).label("org_id"),
                WaterObject.name,
                func.max(TelemetryPacket.received_at).label("last_contact_at"),
                func.max(TelemetryPacket.device_id).label("last_device_id"),
                Organization.name.label("org_name"),
            )
            .join(
                Device,
                TelemetryPacket.device_id == Device.external_id,
            )
            .join(
                WaterObject,
                Device.water_object_id == WaterObject.id,
            )
            .join(
                Organization,
                WaterObject.organization_id == Organization.id,
            )
            .group_by(
                WaterObject.id, Organization.id, WaterObject.name, Organization.name
            )
        )

        if org_id is not None:
            try:
                org_uuid = UUID(org_id)
                stmt = stmt.where(Organization.id == org_uuid)
            except ValueError:
                return []

        stmt = (
            stmt.order_by(func.max(TelemetryPacket.received_at).desc())
            .offset(skip)
            .limit(limit)
        )

        rows = self.session.execute(stmt).fetchall()
        return [
            {
                "object_id": str(row.object_id),
                "org_id": str(row.org_id),
                "name": row.name,
                "org_name": row.org_name,
                "last_contact_at": row.last_contact_at,
                "last_device_id": row.last_device_id,
                # device_id doubles as name since it's a string identifier
                "device_name": row.last_device_id,
            }
            for row in rows
        ]

    def count_objects(self, org_id: str | None = None) -> int:
        """Count unique objects (optionally filtered by org_id)."""
        stmt = (
            select(func.count(func.distinct(WaterObject.id)))
            .select_from(TelemetryPacket)
            .join(
                Device,
                TelemetryPacket.device_id == Device.external_id,
            )
            .join(
                WaterObject,
                Device.water_object_id == WaterObject.id,
            )
        )

        if org_id is not None:
            try:
                org_uuid = UUID(org_id)
                stmt = stmt.join(
                    Organization,
                    WaterObject.organization_id == Organization.id,
                ).where(Organization.id == org_uuid)
            except ValueError:
                return 0

        result = self.session.execute(stmt).scalar()
        return result or 0

    def get_latest_packet(self, object_id: str) -> TelemetryPacket | None:
        """Get the most recent packet for a water object (by water_object_id UUID)."""
        try:
            water_object_uuid = UUID(object_id)
        except ValueError:
            return None

        stmt = (
            select(TelemetryPacket)
            .select_from(TelemetryPacket)
            .join(
                Device,
                TelemetryPacket.device_id == Device.external_id,
            )
            .join(
                WaterObject,
                Device.water_object_id == WaterObject.id,
            )
            .where(WaterObject.id == water_object_uuid)
            .order_by(TelemetryPacket.received_at.desc())
            .limit(1)
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_packets_in_range(
        self,
        object_id: str,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> list[TelemetryPacket]:
        """Get packets for a water object within a time range, ordered by
        received_at ASC.
        """
        try:
            water_object_uuid = UUID(object_id)
        except ValueError:
            return []

        stmt = (
            select(TelemetryPacket)
            .select_from(TelemetryPacket)
            .join(
                Device,
                TelemetryPacket.device_id == Device.external_id,
            )
            .join(
                WaterObject,
                Device.water_object_id == WaterObject.id,
            )
            .where(
                WaterObject.id == water_object_uuid,
                TelemetryPacket.received_at >= start,
                TelemetryPacket.received_at <= end,
            )
            .order_by(TelemetryPacket.received_at.asc())
            .limit(limit)
        )

        return self.session.execute(stmt).scalars().all()

    def get_water_object(self, object_id: str) -> WaterObject | None:
        """Get a water object by UUID string."""
        try:
            obj_uuid = UUID(object_id)
            stmt = select(WaterObject).where(WaterObject.id == obj_uuid)
            return self.session.execute(stmt).scalar_one_or_none()
        except ValueError:
            return None

    def get_device_name(self, device_id: str) -> str:
        """Get device name.

        Since device_id is a string identifier (not UUID), return it as-is.
        """
        return device_id

    def get_organization_name(self, org_id: str) -> str:
        """Get organization name by ID, or return 'Nieznana' if not found."""
        from uuid import UUID

        try:
            org_uuid = UUID(org_id)
            stmt = select(Organization.name).where(Organization.id == org_uuid)
            result = self.session.execute(stmt).scalar_one_or_none()
            return result or "Nieznana"
        except ValueError:
            return "Nieznana"
