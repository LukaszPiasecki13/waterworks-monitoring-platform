"""Water object model for core data domain."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class WaterObject(Base):
    """Water object model — represents a pump station, hydrophore, intake, or network point."""

    __tablename__ = "water_objects"

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        primary_key=True,
    )
    organization_id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location_description: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()
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
        return f"<WaterObject {self.name}>"
