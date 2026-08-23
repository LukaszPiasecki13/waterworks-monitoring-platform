"""Device activation code generation and management API (platform-level)."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.device_identity.dependencies import get_activation_code_service
from app.modules.device_identity.schemas.activation_codes import (
    ActivationCodeCancelResponse,
    ActivationCodeCreateResponse,
    ActivationCodeStatusResponse,
)
from app.modules.device_identity.services.activation_codes import (
    DeviceActivationCodeService,
)
from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import require_platform_permission
from app.modules.security.permission_catalog import PLATFORM_MANAGE_DEVICE_PROVISIONING

activation_codes_router = APIRouter(
    prefix="/device-activation-codes", tags=["activation-codes"]
)


@activation_codes_router.post(
    "", response_model=ActivationCodeCreateResponse, status_code=201
)
async def create_activation_code(
    service: DeviceActivationCodeService = Depends(get_activation_code_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
) -> ActivationCodeCreateResponse:
    """Generate a new device activation code.

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    Returns the plaintext code only once — store it securely.
    """
    code, plaintext = service.generate(creator_user_id=context.actor.id)
    return ActivationCodeCreateResponse(
        id=code.id,
        activation_code=plaintext,
        status=code.status,
        expires_at=code.expires_at,
    )


@activation_codes_router.get("/{code_id}", response_model=ActivationCodeStatusResponse)
async def get_activation_code_status(
    code_id: UUID,
    service: DeviceActivationCodeService = Depends(get_activation_code_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
) -> ActivationCodeStatusResponse:
    """Get status of an activation code.

    Shows which device (SN) redeemed it, if any.
    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    status_data = service.get_status(code_id)
    return ActivationCodeStatusResponse(**status_data)


@activation_codes_router.post(
    "/{code_id}/cancel", response_model=ActivationCodeCancelResponse
)
async def cancel_activation_code(
    code_id: UUID,
    service: DeviceActivationCodeService = Depends(get_activation_code_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
) -> ActivationCodeCancelResponse:
    """Cancel an unused activation code.

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    result = service.cancel(
        code_id=code_id,
        actor_id=str(context.actor.id),
        actor_display_name=context.actor.email,
    )
    return ActivationCodeCancelResponse(**result)
