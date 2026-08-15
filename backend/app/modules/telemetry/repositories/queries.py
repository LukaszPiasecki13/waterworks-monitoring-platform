"""Repository for telemetry data queries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.telemetry.models.measurement_packet import TelemetryPacket


class TelemetryQueryRepository(SQLRepository):
    """Query-side repository for telemetry data."""

    def __init__(self, session: Session):
        super().__init__(session)

    def _latest_packet_per_object(self):
        """Subquery holding the newest packet of every water object.

        Ranks by received_at, breaking ties on created_at (DB-assigned insert
        order) so the pick stays deterministic if two packets ever land in
        the same instant.
        """
        ranked = (
            select(
                WaterObject.id.label("object_id"),
                TelemetryPacket.id.label("packet_id"),
                TelemetryPacket.device_id.label("device_id"),
                TelemetryPacket.received_at.label("received_at"),
                func.row_number()
                .over(
                    partition_by=WaterObject.id,
                    order_by=(
                        TelemetryPacket.received_at.desc(),
                        TelemetryPacket.created_at.desc(),
                    ),
                )
                .label("recency_rank"),
            )
            .select_from(TelemetryPacket)
            .join(Device, TelemetryPacket.device_id == Device.external_id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .subquery()
        )
        return select(ranked).where(ranked.c.recency_rank == 1).subquery()

    def list_objects(
        self,
        org_id: UUID | None = None,
        skip: int = 0,
        limit: int | None = 50,
    ) -> list[dict]:
        """List water objects with their latest contact, newest contact first."""
        latest = self._latest_packet_per_object()

        stmt = (
            select(
                WaterObject.id.label("object_id"),
                Organization.id.label("org_id"),
                WaterObject.name,
                Organization.name.label("org_name"),
                latest.c.received_at.label("last_contact_at"),
                latest.c.device_id.label("last_device_id"),
                latest.c.packet_id.label("last_packet_id"),
            )
            .select_from(WaterObject)
            .join(Organization, WaterObject.organization_id == Organization.id)
            .outerjoin(latest, latest.c.object_id == WaterObject.id)
        )

        if org_id is not None:
            stmt = stmt.where(Organization.id == org_id)

        stmt = stmt.order_by(
            latest.c.received_at.desc().nullslast(), WaterObject.name
        ).offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        return [
            {
                "object_id": row.object_id,
                "org_id": row.org_id,
                "name": row.name,
                "org_name": row.org_name,
                "last_contact_at": row.last_contact_at,
                "last_device_id": row.last_device_id,
                "last_packet_id": row.last_packet_id,
            }
            for row in self.session.execute(stmt).fetchall()
        ]

    def count_objects(self, org_id: UUID | None = None) -> int:
        """Count water objects visible to the dashboard."""
        stmt = select(func.count(WaterObject.id)).select_from(WaterObject)

        if org_id is not None:
            stmt = stmt.where(WaterObject.organization_id == org_id)

        return self.session.execute(stmt).scalar() or 0

    def get_packets_by_ids(self, packet_ids: list[UUID]) -> dict[UUID, TelemetryPacket]:
        """Fetch packets by primary key, keyed by packet id.

        For batches where the caller already knows *which* packets it wants
        (e.g. the `last_packet_id` column from `list_objects`) — a plain
        indexed lookup, no ranking involved.
        """
        if not packet_ids:
            return {}

        stmt = select(TelemetryPacket).where(TelemetryPacket.id.in_(packet_ids))
        return {packet.id: packet for packet in self.session.execute(stmt).scalars()}

    def get_latest_packet(self, object_id: UUID) -> TelemetryPacket | None:
        """Get the most recent packet for a water object.

        A direct query, not routed through `_latest_packet_per_object()`:
        that subquery ranks every packet of every object, which is wasteful
        when only one object's latest packet is needed.
        """
        stmt = (
            select(TelemetryPacket)
            .select_from(TelemetryPacket)
            .join(Device, TelemetryPacket.device_id == Device.external_id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .where(WaterObject.id == object_id)
            .order_by(
                TelemetryPacket.received_at.desc(), TelemetryPacket.created_at.desc()
            )
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_packets_in_range(
        self,
        object_id: UUID,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> list[TelemetryPacket]:
        """Get packets for a water object in a time range, oldest first."""
        stmt = (
            select(TelemetryPacket)
            .select_from(TelemetryPacket)
            .join(Device, TelemetryPacket.device_id == Device.external_id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .where(
                WaterObject.id == object_id,
                TelemetryPacket.received_at >= start,
                TelemetryPacket.received_at <= end,
            )
            .order_by(TelemetryPacket.received_at.asc())
            .limit(limit)
        )

        return list(self.session.execute(stmt).scalars().all())

    def get_water_object(self, object_id: UUID) -> WaterObject | None:
        """Get a water object by id."""
        stmt = select(WaterObject).where(WaterObject.id == object_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_organization_name(self, org_id: UUID) -> str | None:
        """Get an organization's name, or None when it cannot be resolved."""
        stmt = select(Organization.name).where(Organization.id == org_id)
        return self.session.execute(stmt).scalar_one_or_none()
