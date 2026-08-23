"""Pydantic schemas for device activation codes."""

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema


class ActivationCodeCreateResponse(BaseSchema):
    """Response when creating an activation code."""

    id: UUID
    activation_code: str = Field(
        description="Plaintext activation code (shown only once)"
    )
    status: str
    expires_at: datetime


class ActivationCodeStatusResponse(BaseSchema):
    """Response for activation code status check."""

    id: UUID
    status: str = Field(
        description="Current status: unused, used, expired, or cancelled"
    )
    expires_at: datetime
    used_at: datetime | None = None
    serial_number: str | None = Field(
        None, description="SN of device that redeemed this code (if used)"
    )

    model_config = ConfigDict(from_attributes=True)


class ActivationCodeCancelResponse(BaseSchema):
    """Response when cancelling an activation code."""

    id: UUID
    status: str


class DeviceActivationRedeemRequest(BaseSchema):
    """Request to redeem an activation code for device registration."""

    serial_number: str = Field(min_length=1, max_length=64)
    activation_code: str = Field(min_length=1, max_length=20)
    public_key_point: str = Field(
        min_length=130,
        max_length=130,
        pattern=r"^[0-9a-fA-F]{130}$",
        description="Uncompressed P-256 point (hex): 04 + X (64 hex) + Y (64 hex)",
    )


class DeviceActivationRedeemResponse(BaseSchema):
    """Response when redeeming an activation code."""

    serial_number: str
    status: str = Field(
        description="unclaimed (new device) or already_registered (retry)"
    )
    next_action: str = Field(
        description="What firmware should do next: perform_auth or wait"
    )
    already_registered: bool = Field(
        description="True if this is a retry of the same device/code (idempotent)"
    )
