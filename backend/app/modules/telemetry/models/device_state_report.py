"""Device state report persistence model (B-08).

One row per (packet, section). The table is deliberately section-agnostic —
a new read (device configuration, sensor inventory, ...) is a new `section`
value, not a new table and not a new migration.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class DeviceStateReport(Base):
    __tablename__ = "device_state_reports"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    packet_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("telemetry_packets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # external_id of the device, matching TelemetryPacket.device_id — the
    # telemetry module addresses devices by serial number, not by FK.
    device_id: Mapped[str] = mapped_column(String(128), nullable=False)

    section: Mapped[str] = mapped_column(String(64), nullable=False)

    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)

    # Device clock at capture. Kept apart from received_at so a reader can tell
    # "measured 20 minutes ago" from "arrived just now after a retry".
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        # Idempotence rides on the packet's own (device_id, seq) dedupe: a
        # retransmitted packet cannot duplicate its sections.
        UniqueConstraint(
            "packet_id", "section", name="uq_device_state_reports_packet_section"
        ),
        Index(
            "ix_device_state_reports_device_section_captured",
            "device_id",
            "section",
            "captured_at",
        ),
    )
