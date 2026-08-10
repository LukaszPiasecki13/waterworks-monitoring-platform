"""Repository for telemetry data queries."""

from datetime import datetime

from sqlalchemy import UUID as SA_UUID, func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models import WaterObject
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
        """List unique objects, grouped by object_id/org_id with their latest contact time.

        Returns list of dicts with keys: object_id, org_id, name, last_contact_at, last_device_id.
        Sorted by last_contact_at DESC (most recent first).
        """
        stmt = (
            select(
                TelemetryPacket.object_id,
                TelemetryPacket.org_id,
                WaterObject.name,
                func.max(TelemetryPacket.received_at).label("last_contact_at"),
                func.max(TelemetryPacket.device_id).label("last_device_id"),
            )
            .join(
                WaterObject,
                TelemetryPacket.object_id.cast(SA_UUID) == WaterObject.id,
            )
            .group_by(TelemetryPacket.object_id, TelemetryPacket.org_id, WaterObject.name)
        )

        if org_id is not None:
            stmt = stmt.where(TelemetryPacket.org_id == org_id)

        stmt = stmt.order_by(func.max(TelemetryPacket.received_at).desc()).offset(skip).limit(limit)

        rows = self.session.execute(stmt).fetchall()
        return [
            {
                "object_id": row.object_id,
                "org_id": row.org_id,
                "name": row.name,
                "last_contact_at": row.last_contact_at,
                "last_device_id": row.last_device_id,
            }
            for row in rows
        ]

    def count_objects(self, org_id: str | None = None) -> int:
        """Count unique objects (optionally filtered by org_id)."""
        stmt = select(func.count(func.distinct(TelemetryPacket.object_id)))

        if org_id is not None:
            stmt = stmt.where(TelemetryPacket.org_id == org_id)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def get_latest_packet(self, object_id: str) -> TelemetryPacket | None:
        """Get the most recent packet for an object."""
        stmt = (
            select(TelemetryPacket)
            .where(TelemetryPacket.object_id == object_id)
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
        """Get packets for an object within a time range, ordered by received_at ASC.

        Useful for fetching historical time series.
        """
        stmt = (
            select(TelemetryPacket)
            .where(
                TelemetryPacket.object_id == object_id,
                TelemetryPacket.received_at >= start,
                TelemetryPacket.received_at <= end,
            )
            .order_by(TelemetryPacket.received_at.asc())
            .limit(limit)
        )

        return self.session.execute(stmt).scalars().all()

    def get_water_object(self, object_id: str) -> WaterObject | None:
        """Get a water object by ID (stored as UUID, but object_id is a string)."""
        from uuid import UUID
        try:
            obj_uuid = UUID(object_id)
            stmt = select(WaterObject).where(WaterObject.id == obj_uuid)
            return self.session.execute(stmt).scalar_one_or_none()
        except ValueError:
            return None
