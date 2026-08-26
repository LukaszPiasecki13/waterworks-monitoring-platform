"""Telemetry error log model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class TelemetryError(Base):
    __tablename__ = "telemetry_errors"

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

    device_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    point_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    severity: Mapped[str] = mapped_column(String(16), nullable=False)

    message: Mapped[str | None] = mapped_column(String(512), nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_telemetry_errors_device_code_occurred",
            "device_id",
            "code",
            "occurred_at",
        ),
    )
