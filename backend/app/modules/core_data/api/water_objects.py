"""Water objects API endpoints."""

from fastapi import APIRouter, Depends

from app.modules.core_data.dependencies import get_water_object_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.schemas.water_objects import (
    WaterObjectCreateRequest,
    WaterObjectResponse,
    WaterObjectUpdateRequest,
    ListWaterObjectsRequest,
)
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.security.dependencies import (
    get_current_user,
    require_permission,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(prefix="/objects", tags=["objects"])


@router.get("", response_model=PaginatedResponse[WaterObjectResponse])
def list_water_objects(
    query: ListWaterObjectsRequest = Depends(),
    service: WaterObjectService = Depends(get_water_object_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """List water objects."""
    objs, total = service.list_all(query, actor=user)
    return PaginatedResponse(
        items=objs,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post("", response_model=WaterObjectResponse)
def create_water_object(
    request: WaterObjectCreateRequest,
    service: WaterObjectService = Depends(get_water_object_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Create water object."""
    return service.create(request, actor=user)


@router.get("/{obj_id}", response_model=WaterObjectResponse)
def get_water_object(
    obj_id: int,
    service: WaterObjectService = Depends(get_water_object_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """Get water object by ID."""
    return service.get_by_id(obj_id, actor=user)


@router.patch("/{obj_id}", response_model=WaterObjectResponse)
def update_water_object(
    obj_id: int,
    request: WaterObjectUpdateRequest,
    service: WaterObjectService = Depends(get_water_object_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Update water object."""
    return service.update(obj_id, request, actor=user)


@router.delete("/{obj_id}")
def delete_water_object(
    obj_id: int,
    service: WaterObjectService = Depends(get_water_object_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Delete water object."""
    service.delete(obj_id, actor=user)
    return {"message": "Water object deleted successfully"}
