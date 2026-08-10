"""Device model for core data domain."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class Device(Base):
    """Device model — represents a telemetry device attached to a water object."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        primary_key=True,
    )
    water_object_id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        ForeignKey("water_objects.id"),
        nullable=False,
        index=True,
    )
    external_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    firmware_version: Mapped[str | None] = mapped_column(String(50))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_diagnostics_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Device {self.external_id}>"
