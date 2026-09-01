"""Normalized measurement persistence model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base

MEASUREMENTS_PARTITION_BY = "RANGE (window_start)"


class Measurement(Base):
    """One measurement window of one measurement point, unpacked from a packet.

    The JSONB blob in `telemetry_packets` stays the audit/replay path; this
    table is what alarms, charts and CSV export read, so it carries only the
    per-measurement facts and a loose pointer back to the packet it came from.
    """

    __tablename__ = "measurements"

    # (measurement_point_id, window_start) is the natural key: one point cannot
    # report two values for the same window. Using it as the primary key gives
    # ingest idempotency (independent of the packet-level (device_id, seq)
    # dedupe), the index the range queries need, and a primary key containing
    # the partition column — which PostgreSQL requires on a partitioned table.
    measurement_point_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("measurement_points.id", ondelete="CASCADE"),
        primary_key=True,
    )
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    avg: Mapped[float | None] = mapped_column()
    min: Mapped[float | None] = mapped_column()
    max: Mapped[float | None] = mapped_column()

    # The packet schema allows `float | int | bool | None` for a spot value.
    # Booleans (digital_input, power_status) get their own column instead of
    # being folded into 0.0/1.0: a threshold rule reading `value` must never
    # silently compare against a coerced flag, and the read API has to give a
    # client back `true`/`false`, not `1.0`.
    value: Mapped[float | None] = mapped_column()
    value_bool: Mapped[bool | None] = mapped_column(Boolean)

    quality: Mapped[str] = mapped_column(String(32), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Traceability back to the raw blob, deliberately without a foreign key:
    # blob retention (a separate task) must be free to prune packets without
    # cascading into measurements, and an unindexed FK would make every packet
    # delete scan this table. A dangling id resolves to "blob already pruned".
    source_packet_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "value IS NULL OR value_bool IS NULL",
            name="ck_measurements_single_value",
        ),
        {"postgresql_partition_by": MEASUREMENTS_PARTITION_BY},
    )
