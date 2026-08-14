"""Telemetry packet persistence model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    UUID,
    BigInteger,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class TelemetryPacket(Base):
    __tablename__ = "telemetry_packets"

    id: Mapped[UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid4,
    )

    device_id: Mapped[str] = mapped_column(String(128), nullable=False)
    seq: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), "postgresql"), nullable=False
    )

    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("device_id", "seq", name="uq_telemetry_packets_device_seq"),
        Index("ix_telemetry_packets_device_id", "device_id"),
        Index("ix_telemetry_packets_received_at", "received_at"),
    )
