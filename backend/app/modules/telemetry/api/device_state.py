"""Device state read endpoints (B-08).

Lives in `telemetry` rather than `core_data`: the data arrives through
telemetry ingest, and `core_data` is the base module every other one builds
on — reading state from there would invert that dependency.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import (
    require_org_access,
    require_platform_permission,
)
from app.modules.security.permission_catalog import (
    CAN_VIEW_ASSETS,
    PLATFORM_MANAGE_DEVICE_PROVISIONING,
)
from app.modules.telemetry.dependencies import get_device_state_query_service
from app.modules.telemetry.schemas.device_state import DeviceStateResponse
from app.modules.telemetry.services.device_state import DeviceStateQueryService

# Organization-scoped router, mounted under /api/v1/orgs/{org_id}/telemetry
router = APIRouter(prefix="/devices", tags=["telemetry"])

# Platform-level router, mounted under /api/v1/platform
platform_router = APIRouter(prefix="/telemetry/devices", tags=["telemetry"])


@router.get(
    "/{device_id}/state",
    response_model=DeviceStateResponse,
    dependencies=[Depends(require_org_access(CAN_VIEW_ASSETS))],
)
def get_device_state(
    org_id: UUID = Path(...),
    device_id: UUID = Path(...),
    service: DeviceStateQueryService = Depends(get_device_state_query_service),
) -> DeviceStateResponse:
    """Last known state the device reported, one entry per section."""
    return service.get_device_state(device_id, organization_id=org_id)


@platform_router.get("/{device_id}/state", response_model=DeviceStateResponse)
def get_device_state_platform(
    device_id: UUID = Path(...),
    service: DeviceStateQueryService = Depends(get_device_state_query_service),
    _context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
) -> DeviceStateResponse:
    """Cross-organization variant for platform administrators."""
    return service.get_device_state(device_id)
