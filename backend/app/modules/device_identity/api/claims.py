"""Device claim intent API (org-level)."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.device_identity.dependencies import get_claim_service
from app.modules.device_identity.schemas.claims import (
    DeviceClaimRequest,
    DeviceClaimResponse,
    DeviceClaimStatusResponse,
)
from app.modules.device_identity.services.claims import DeviceClaimService
from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import require_org_access
from app.modules.security.permission_catalog import CAN_MANAGE_ASSETS, CAN_VIEW_ASSETS

claims_router = APIRouter(prefix="", tags=["claims"])


@claims_router.post(
    "/orgs/{org_id}/devices",
    response_model=DeviceClaimResponse,
)
async def claim_device(
    org_id: UUID,
    request: DeviceClaimRequest,
    service: DeviceClaimService = Depends(get_claim_service),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
) -> DeviceClaimResponse:
    """Request to claim a provisioned device for a water object."""
    status = service.request_claim(
        serial_number=request.serial_number,
        water_object_id=request.water_object_id,  # type: ignore
        org_access=org_access,
    )
    return DeviceClaimResponse(
        serial_number=request.serial_number,
        status=status,
    )


@claims_router.get(
    "/orgs/{org_id}/devices/claims/{serial_number}",
    response_model=DeviceClaimStatusResponse,
)
async def get_claim_status(
    org_id: UUID,
    serial_number: str,
    service: DeviceClaimService = Depends(get_claim_service),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
) -> DeviceClaimStatusResponse:
    """Get the current claim status of a device."""
    status = service.get_claim_status(
        serial_number=serial_number,
        org_access=org_access,
    )
    return DeviceClaimStatusResponse(
        serial_number=serial_number,
        status=status,
    )
