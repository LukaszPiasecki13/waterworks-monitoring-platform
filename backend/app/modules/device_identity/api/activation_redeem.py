"""Device activation redemption API (device-facing)."""

from fastapi import APIRouter, Depends, Request, Response

from app.core.rate_limit import limiter
from app.modules.device_identity.dependencies import get_activation_code_service
from app.modules.device_identity.schemas.activation_codes import (
    DeviceActivationRedeemRequest,
    DeviceActivationRedeemResponse,
)
from app.modules.device_identity.services.activation_codes import (
    DeviceActivationCodeService,
)

activation_redeem_router = APIRouter(tags=["activation"])


@activation_redeem_router.post(
    "/devices/activation/redeem",
    response_model=DeviceActivationRedeemResponse,
)
@limiter.limit("5/minute")
async def redeem_activation_code(
    request: Request,
    response: Response,
    payload: DeviceActivationRedeemRequest,
    service: DeviceActivationCodeService = Depends(get_activation_code_service),
) -> DeviceActivationRedeemResponse:
    """Redeem an activation code for device self-registration.

    Returns 201 if new device registration, 200 if idempotent retry (same SN+key).
    No authentication required — code itself is the authentication factor.
    Rate limited to 5/minute per IP to prevent brute-force code guessing.
    """
    result = service.redeem(
        serial_number=payload.serial_number,
        activation_code=payload.activation_code,
        public_key_point_hex=payload.public_key_point,
    )
    response.status_code = 201 if not result["already_registered"] else 200
    return DeviceActivationRedeemResponse(**result)
