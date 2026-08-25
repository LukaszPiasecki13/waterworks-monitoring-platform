"""Water objects API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from app.modules.core_data.dependencies import get_water_object_service
from app.modules.core_data.schemas.water_objects import (
    ListWaterObjectsRequest,
    WaterObjectCreateRequest,
    WaterObjectResponse,
    WaterObjectUpdateRequest,
)
from app.modules.core_data.services.water_objects import WaterObjectService
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

router = APIRouter(prefix="/orgs/{org_id}/objects", tags=["objects"])
platform_router = APIRouter(prefix="/objects", tags=["platform-objects"])


@router.get("", response_model=list[WaterObjectResponse])
def list_water_objects(
    org_id: UUID = Path(...),
    query: ListWaterObjectsRequest = Depends(),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """List water objects."""
    objs, _ = service.list_all(query, org_access)
    return objs


@router.post("", response_model=WaterObjectResponse)
def create_water_object(
    org_id: UUID = Path(...),
    request: WaterObjectCreateRequest = Body(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """Create water object."""
    return service.create(request, org_access)


@router.get("/{obj_id}", response_model=WaterObjectResponse)
def get_water_object(
    org_id: UUID = Path(...),
    obj_id: UUID = Path(...),
    _org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """Get water object by ID."""
    return service.get_by_id(obj_id, organization_id=org_id)


@router.patch("/{obj_id}", response_model=WaterObjectResponse)
def update_water_object(
    org_id: UUID = Path(...),
    obj_id: UUID = Path(...),
    request: WaterObjectUpdateRequest = Body(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """Update water object."""
    return service.update(obj_id, request, org_access)


@router.delete("/{obj_id}")
def delete_water_object(
    org_id: UUID = Path(...),
    obj_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """Delete water object."""
    service.delete(obj_id, org_access)
    return {"message": "Water object deleted successfully"}


# Platform-level endpoints
@platform_router.get("/{obj_id}", response_model=WaterObjectResponse)
def get_water_object_platform(
    obj_id: UUID = Path(...),
    service: WaterObjectService = Depends(get_water_object_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_DEVICE_PROVISIONING)
    ),
):
    """Get water object by ID (platform-level, for device detail views).

    Requires PLATFORM_MANAGE_DEVICE_PROVISIONING permission.
    """
    return service.get_by_id(obj_id)
