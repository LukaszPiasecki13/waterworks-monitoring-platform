"""Pydantic schemas for devices."""

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema


class DeviceUpdateRequest(BaseSchema):
    """Update device request."""

    firmware_version: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class DeviceResponse(BaseSchema):
    """Device response DTO."""

    id: UUID
    water_object_id: UUID | None
    external_id: str
    firmware_version: str | None
    last_seen_at: datetime | None = None
    last_diagnostics_at: datetime | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ListDevicesRequest(BaseSchema):
    """List devices query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    water_object_id: UUID | None = None
