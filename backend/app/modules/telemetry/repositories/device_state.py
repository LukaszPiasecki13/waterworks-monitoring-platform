"""Device state report repository."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.telemetry.models.device_state_report import DeviceStateReport


class DeviceStateReportRepository(SQLRepository):
    """Reads and writes for the section-based device state channel."""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(
        self,
        *,
        packet_id: UUID,
        device_id: str,
        section: str,
        schema_version: int,
        captured_at: datetime,
        received_at: datetime,
        data: dict[str, Any],
    ) -> DeviceStateReport:
        """Stage one section row. The caller owns the transaction."""
        entity = DeviceStateReport(
            packet_id=packet_id,
            device_id=device_id,
            section=section,
            schema_version=schema_version,
            captured_at=captured_at,
            received_at=received_at,
            data=data,
        )
        self.session.add(entity)
        return entity

    def list_latest_sections(self, device_id: str) -> list[DeviceStateReport]:
        """Return the newest report per section for one device.

        Ranked by `captured_at` (the device's own clock) rather than
        `received_at`: a packet retried after an outage arrives late but
        still carries the state as of its capture, and must not displace a
        fresher report that got through first.
        """
        ranked = (
            select(
                DeviceStateReport.id,
                func.row_number()
                .over(
                    partition_by=DeviceStateReport.section,
                    order_by=(
                        DeviceStateReport.captured_at.desc(),
                        DeviceStateReport.received_at.desc(),
                    ),
                )
                .label("rank"),
            )
            .where(DeviceStateReport.device_id == device_id)
            .subquery()
        )

        stmt = (
            select(DeviceStateReport)
            .join(ranked, DeviceStateReport.id == ranked.c.id)
            .where(ranked.c.rank == 1)
            .order_by(DeviceStateReport.section)
        )
        return list(self.session.execute(stmt).scalars().all())
