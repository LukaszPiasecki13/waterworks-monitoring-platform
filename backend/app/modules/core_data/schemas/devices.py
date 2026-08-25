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
    created_at: datetime
    device_credential_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class DeviceStatsResponse(BaseSchema):
    """Aggregate device counts for platform-admin KPI strip."""

    total: int
    active: int
    unassigned: int
    unclaimed: int


class ListDevicesRequest(BaseSchema):
    """List devices query parameters (organization-scoped)."""

    water_object_id: UUID | None = None
    search: str | None = Field(None, max_length=128)


class ListAllDevicesRequest(BaseSchema):
    """List all devices (platform-level).

    Supports search and optional org filter only; no pagination.
    """

    search: str | None = Field(None, max_length=128)
    organization_id: UUID | None = None
