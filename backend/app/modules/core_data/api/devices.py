"""Devices API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from app.modules.core_data.dependencies import get_device_service
from app.modules.core_data.schemas.devices import (
    DeviceResponse,
    DeviceUpdateRequest,
    ListDevicesRequest,
)
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.services.devices import DeviceService
from app.modules.security.access import OrganizationAccess, PlatformContext
from app.modules.security.dependencies import (
    require_org_access,
    require_platform_permission,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
    PLATFORM_MANAGE_DEVICE_PROVISIONING,
)

# Organization-scoped router
router = APIRouter(prefix="/orgs/{org_id}/devices", tags=["devices"])

# Platform-level router
platform_router = APIRouter(prefix="/devices", tags=["platform-devices"])


@router.get("", response_model=PaginatedResponse[DeviceResponse])
def list_devices(
    org_id: UUID = Path(...),
    query: ListDevicesRequest = Depends(),
    _org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """List devices."""
    devices, total = service.list_all(query, organization_id=org_id)
    return PaginatedResponse(
        items=devices,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    org_id: UUID = Path(...),
    device_id: UUID = Path(...),
    _org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """Get device by ID."""
    return service.get_by_id(device_id, organization_id=org_id)


@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device(
    org_id: UUID = Path(...),
    device_id: UUID = Path(...),
    request: DeviceUpdateRequest = Body(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """Update device."""
    return service.update(device_id, request, org_access)


@router.delete("/{device_id}")
def delete_device(
    org_id: UUID = Path(...),
    device_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """Delete device."""
    service.delete(
        device_id,
        actor_id=str(org_access.actor.id),
        actor_display_name=org_access.actor.email,
        organization_id=org_id,
    )
    return {"message": "Device deleted successfully"}


# Platform-level endpoints
@platform_router.get("", response_model=PaginatedResponse[DeviceResponse])
def list_all_devices(
    query: ListDevicesRequest = Depends(),
    service: DeviceService = Depends(get_device_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """List all devices across all organizations.

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    devices, total = service.list_all(query)
    return PaginatedResponse(
        items=devices,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@platform_router.get("/{device_id}", response_model=DeviceResponse)
def get_all_devices_detail(
    device_id: UUID,
    service: DeviceService = Depends(get_device_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """Get device by ID (platform-level, no org scope).

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    return service.get_by_id(device_id)


@platform_router.delete("/{device_id}")
def delete_all_devices(
    device_id: UUID,
    service: DeviceService = Depends(get_device_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """Delete device (platform-level, no org scope).

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    service.delete(
        device_id,
        actor_id=str(context.actor.id),
        actor_display_name=context.actor.email,
    )
    return {"message": "Device deleted successfully"}
