"""Water objects API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from app.modules.core_data.dependencies import get_water_object_service
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.schemas.water_objects import (
    ListWaterObjectsRequest,
    WaterObjectCreateRequest,
    WaterObjectResponse,
    WaterObjectUpdateRequest,
)
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import require_org_access
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(prefix="/orgs/{org_id}/objects", tags=["objects"])


@router.get("", response_model=PaginatedResponse[WaterObjectResponse])
def list_water_objects(
    org_id: UUID = Path(...),
    query: ListWaterObjectsRequest = Depends(),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """List water objects."""
    objs, total = service.list_all(query, org_access)
    return PaginatedResponse(
        items=objs,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


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
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: WaterObjectService = Depends(get_water_object_service),
):
    """Get water object by ID."""
    return service.get_by_id(obj_id, org_access)


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
