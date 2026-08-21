"""Device authentication challenge/verify API."""

from fastapi import APIRouter, Depends

from app.modules.device_identity.dependencies import get_device_auth_service
from app.modules.device_identity.schemas.device_auth import (
    DeviceChallengeRequest,
    DeviceChallengeResponse,
    DeviceTokenResponse,
    DeviceVerifyRequest,
)
from app.modules.device_identity.services.device_auth import DeviceAuthService

device_auth_router = APIRouter(prefix="/devices/auth", tags=["device-auth"])


@device_auth_router.post("/challenge", response_model=DeviceChallengeResponse)
async def request_challenge(
    request: DeviceChallengeRequest,
    service: DeviceAuthService = Depends(get_device_auth_service),
) -> DeviceChallengeResponse:
    """Request a one-time challenge nonce for device signature."""
    serial_number, challenge = service.challenge(request.serial_number)
    return DeviceChallengeResponse(
        serial_number=serial_number,
        challenge=challenge,
    )


@device_auth_router.post("/verify", response_model=DeviceTokenResponse)
async def verify_challenge(
    request: DeviceVerifyRequest,
    service: DeviceAuthService = Depends(get_device_auth_service),
) -> DeviceTokenResponse:
    """Verify a signed challenge and return a device session token."""
    token, token_type, expires_at = service.verify(
        serial_number=request.serial_number,
        signature_der_b64=request.signature,
    )
    return DeviceTokenResponse(
        token=token,
        token_type=token_type,
        expires_at=expires_at,
    )
