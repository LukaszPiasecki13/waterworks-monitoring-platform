"""Organization model for core data domain."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sql.base import Base


class Organization(Base):
    """Organization model — top-level container for water objects."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), 'postgresql'),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
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
        return f"<Organization {self.name}>"
