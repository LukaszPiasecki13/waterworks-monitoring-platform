"""Schemas for device provisioning endpoints."""

from pydantic import BaseModel, Field


class DeviceProvisionRequest(BaseModel):
    """Request to register a provisioned device credential."""

    serial_number: str = Field(..., min_length=1, max_length=64)
    public_key_pem: str = Field(..., description="PEM-encoded EC P-256 public key")


class DeviceProvisionResponse(BaseModel):
    """Response after successful device provisioning."""

    serial_number: str
    status: str
