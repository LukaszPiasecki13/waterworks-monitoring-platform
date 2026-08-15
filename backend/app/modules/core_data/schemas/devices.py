"""Pydantic schemas for devices."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreateRequest(BaseModel):
    """Create device request."""

    water_object_id: UUID
    external_id: str = Field(..., min_length=1, max_length=128)
    firmware_version: str | None = Field(None, max_length=50)


class DeviceUpdateRequest(BaseModel):
    """Update device request."""

    firmware_version: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class DeviceResponse(BaseModel):
    """Device response DTO (no secret)."""

    id: UUID
    water_object_id: UUID
    external_id: str
    firmware_version: str | None
    last_seen_at: datetime | None = None
    last_diagnostics_at: datetime | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ListDevicesRequest(BaseModel):
    """List devices query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    water_object_id: UUID | None = None
    organization_id: UUID | None = None
