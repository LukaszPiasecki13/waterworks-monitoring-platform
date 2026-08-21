"""Schemas for device claim intent and status."""

from uuid import UUID

from pydantic import BaseModel, Field


class DeviceClaimRequest(BaseModel):
    """Intent to claim a provisioned device for a water object."""

    serial_number: str = Field(..., min_length=1, max_length=64)
    water_object_id: UUID


class DeviceClaimResponse(BaseModel):
    """Confirmation of claim intent."""

    serial_number: str
    status: str


class DeviceClaimStatusResponse(BaseModel):
    """Current status of a device claim."""

    serial_number: str
    status: str
