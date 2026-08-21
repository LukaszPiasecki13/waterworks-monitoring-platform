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
from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import require_org_access
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(prefix="/orgs/{org_id}/devices", tags=["devices"])


@router.get("", response_model=PaginatedResponse[DeviceResponse])
def list_devices(
    org_id: UUID = Path(...),
    query: ListDevicesRequest = Depends(),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """List devices."""
    devices, total = service.list_all(query, org_access)
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
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: DeviceService = Depends(get_device_service),
):
    """Get device by ID."""
    return service.get_by_id(device_id, org_access)


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
    service.delete(device_id, org_access)
    return {"message": "Device deleted successfully"}
