"""Measurement point model for core data domain."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class MeasurementPoint(Base):
    """Measurement point model — represents a single measurement type on a device."""

    __tablename__ = "measurement_points"
    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "external_id",
            name="uq_measurement_points_device_external_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        primary_key=True,
    )
    device_id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        ForeignKey("devices.id"),
        nullable=False,
        index=True,
    )
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    point_type: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    min_technical: Mapped[float | None] = mapped_column()
    max_technical: Mapped[float | None] = mapped_column()
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
        return f"<MeasurementPoint {self.point_type}>"
