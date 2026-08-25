"""Devices API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from app.modules.core_data.dependencies import (
    get_device_lifecycle_service,
    get_device_service,
)
from app.modules.core_data.schemas.devices import (
    DeviceResponse,
    DeviceUpdateRequest,
    ListAllDevicesRequest,
    ListDevicesRequest,
)
from app.modules.core_data.services.device_lifecycle import DeviceLifecycleService
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


@router.get("", response_model=list[DeviceResponse])
def list_devices(
    org_id: UUID = Path(...),
    query: ListDevicesRequest = Depends(),
    _org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """List devices."""
    return service.list_devices(
        organization_id=org_id, water_object_id=query.water_object_id
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
    """Detach device from organization (device remains in system)."""
    service.detach_from_organization(device_id, org_access)
    return {"message": "Device detached from organization"}


# Platform-level endpoints
@platform_router.get("", response_model=list[DeviceResponse])
def list_all_devices(
    query: ListAllDevicesRequest = Depends(),
    service: DeviceService = Depends(get_device_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """List all devices across all organizations.

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    return service.list_devices(
        organization_id=query.organization_id,
        search=query.search,
    )


@platform_router.get("/{device_id}", response_model=DeviceResponse)
def get_all_devices_detail(
    device_id: UUID,
    service: DeviceService = Depends(get_device_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """Get device detail (platform-level).

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    Measurement points should be fetched separately via their dedicated endpoint.
    """
    return service.get_by_id(device_id)


@platform_router.delete("/{device_id}")
def delete_device_platform(
    device_id: UUID = Path(...),
    service: DeviceLifecycleService = Depends(get_device_lifecycle_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """Delete device completely (cascades to measurement points and telemetry).

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.

    This is a destructive operation that:
    - Removes the device record
    - Cascades deletion of associated measurement points
    - Deletes all telemetry packets for this device
    - Revokes the device credential
    - Frees the serial number for re-registration
    """
    service.delete_device_completely(
        device_id,
        actor_id=str(context.actor.id),
        actor_display_name=context.actor.email,
    )
    return {"message": "Device deleted successfully"}
