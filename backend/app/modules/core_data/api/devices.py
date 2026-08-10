"""Devices API endpoints."""

from fastapi import APIRouter, Depends

from app.modules.core_data.dependencies import get_device_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.devices import (
    DeviceCreateRequest,
    DeviceCreateResponse,
    DeviceResponse,
    DeviceUpdateRequest,
    ListDevicesRequest,
)
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.services.devices import DeviceService
from app.modules.security.dependencies import require_permission
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=PaginatedResponse[DeviceResponse])
def list_devices(
    query: ListDevicesRequest = Depends(),
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """List devices."""
    devices, total = service.list_all(query, actor=user)
    return PaginatedResponse(
        items=devices,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post("", response_model=DeviceCreateResponse)
def create_device(
    request: DeviceCreateRequest,
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Create device (returns plain secret, shown only once)."""
    return service.create(request, actor=user)


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """Get device by ID."""
    return service.get_by_id(device_id, actor=user)


@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    request: DeviceUpdateRequest,
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Update device."""
    return service.update(device_id, request, actor=user)


@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Delete device."""
    service.delete(device_id, actor=user)
    return {"message": "Device deleted successfully"}
