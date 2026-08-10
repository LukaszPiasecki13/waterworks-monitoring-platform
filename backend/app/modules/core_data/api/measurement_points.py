"""Measurement points API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.core_data.dependencies import get_measurement_point_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.measurement_points import (
    MeasurementPointCreateRequest,
    MeasurementPointResponse,
    MeasurementPointUpdateRequest,
    ListMeasurementPointsRequest,
)
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.security.dependencies import require_permission
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(prefix="/measurement-points", tags=["measurement-points"])


@router.get("", response_model=PaginatedResponse[MeasurementPointResponse])
def list_measurement_points(
    query: ListMeasurementPointsRequest = Depends(),
    service: MeasurementPointService = Depends(get_measurement_point_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """List measurement points."""
    points, total = service.list_all(query, actor=user)
    return PaginatedResponse(
        items=points,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post("", response_model=MeasurementPointResponse)
def create_measurement_point(
    request: MeasurementPointCreateRequest,
    service: MeasurementPointService = Depends(get_measurement_point_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Create measurement point."""
    return service.create(request, actor=user)


@router.get("/{point_id}", response_model=MeasurementPointResponse)
def get_measurement_point(
    point_id: UUID,
    service: MeasurementPointService = Depends(get_measurement_point_service),
    user: User = Depends(require_permission(CAN_VIEW_ASSETS)),
):
    """Get measurement point by ID."""
    return service.get_by_id(point_id, actor=user)


@router.patch("/{point_id}", response_model=MeasurementPointResponse)
def update_measurement_point(
    point_id: UUID,
    request: MeasurementPointUpdateRequest,
    service: MeasurementPointService = Depends(get_measurement_point_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Update measurement point."""
    return service.update(point_id, request, actor=user)


@router.delete("/{point_id}")
def delete_measurement_point(
    point_id: UUID,
    service: MeasurementPointService = Depends(get_measurement_point_service),
    user: User = Depends(require_permission(CAN_MANAGE_ASSETS)),
):
    """Delete measurement point."""
    service.delete(point_id, actor=user)
    return {"message": "Measurement point deleted successfully"}
