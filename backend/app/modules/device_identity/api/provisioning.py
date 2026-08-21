"""Device provisioning API (platform-level)."""

from fastapi import APIRouter, Depends

from app.modules.device_identity.dependencies import get_provisioning_service
from app.modules.device_identity.schemas.provisioning import (
    DeviceProvisionRequest,
    DeviceProvisionResponse,
)
from app.modules.device_identity.services.provisioning import (
    DeviceProvisioningService,
)
from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import require_platform_permission
from app.modules.security.permission_catalog import PLATFORM_MANAGE_DEVICE_PROVISIONING

provisioning_router = APIRouter(prefix="/device-provisioning", tags=["provisioning"])


@provisioning_router.post("", response_model=DeviceProvisionResponse)
async def register_device_credential(
    request: DeviceProvisionRequest,
    service: DeviceProvisioningService = Depends(get_provisioning_service),
    platform_ctx: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
) -> DeviceProvisionResponse:
    """Register a provisioned device credential (public key).

    Called by the provisioning script after firmware has generated a key pair.
    """
    credential = service.register(
        serial_number=request.serial_number,
        public_key_pem=request.public_key_pem,
        platform_ctx=platform_ctx,
    )
    return DeviceProvisionResponse(
        serial_number=credential.serial_number,
        status=credential.status,
    )
