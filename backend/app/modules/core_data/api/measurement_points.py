"""Measurement points API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from app.modules.core_data.dependencies import get_measurement_point_service
from app.modules.core_data.schemas.measurement_points import (
    ListMeasurementPointsRequest,
    MeasurementPointCreateRequest,
    MeasurementPointResponse,
    MeasurementPointUpdateRequest,
)
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import require_org_access
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ASSETS,
    CAN_VIEW_ASSETS,
)

router = APIRouter(
    prefix="/orgs/{org_id}/measurement-points", tags=["measurement-points"]
)


@router.get("", response_model=PaginatedResponse[MeasurementPointResponse])
def list_measurement_points(
    org_id: UUID = Path(...),
    query: ListMeasurementPointsRequest = Depends(),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: MeasurementPointService = Depends(get_measurement_point_service),
):
    """List measurement points."""
    points, total = service.list_all(query, org_access)
    return PaginatedResponse(
        items=points,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post("", response_model=MeasurementPointResponse)
def create_measurement_point(
    org_id: UUID = Path(...),
    request: MeasurementPointCreateRequest = Body(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: MeasurementPointService = Depends(get_measurement_point_service),
):
    """Create measurement point."""
    return service.create(request, org_access)


@router.get("/{point_id}", response_model=MeasurementPointResponse)
def get_measurement_point(
    org_id: UUID = Path(...),
    point_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_ASSETS)),
    service: MeasurementPointService = Depends(get_measurement_point_service),
):
    """Get measurement point by ID."""
    return service.get_by_id(point_id, org_access)


@router.patch("/{point_id}", response_model=MeasurementPointResponse)
def update_measurement_point(
    org_id: UUID = Path(...),
    point_id: UUID = Path(...),
    request: MeasurementPointUpdateRequest = Body(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: MeasurementPointService = Depends(get_measurement_point_service),
):
    """Update measurement point."""
    return service.update(point_id, request, org_access)


@router.delete("/{point_id}")
def delete_measurement_point(
    org_id: UUID = Path(...),
    point_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_MANAGE_ASSETS)),
    service: MeasurementPointService = Depends(get_measurement_point_service),
):
    """Delete measurement point."""
    service.delete(point_id, org_access)
    return {"message": "Measurement point deleted successfully"}
