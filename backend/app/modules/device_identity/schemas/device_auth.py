"""Schemas for device authentication challenge/verify flow."""

from datetime import datetime

from pydantic import BaseModel, Field


class DeviceChallengeRequest(BaseModel):
    """Request a one-time challenge nonce for device auth."""

    serial_number: str = Field(..., min_length=1, max_length=64)


class DeviceChallengeResponse(BaseModel):
    """Challenge nonce for device to sign."""

    serial_number: str
    challenge: str = Field(..., description="Nonce to sign (base64url-safe)")


class DeviceVerifyRequest(BaseModel):
    """Verify a signed challenge."""

    serial_number: str = Field(..., min_length=1, max_length=64)
    signature: str = Field(..., description="DER-encoded signature (base64)")


class DeviceTokenResponse(BaseModel):
    """Device session token."""

    token: str
    token_type: str = "bearer"
    expires_at: datetime
