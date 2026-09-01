"""Telemetry query/read endpoints for dashboard."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.modules.security.dependencies import require_org_access
from app.modules.security.permission_catalog import CAN_VIEW_ASSETS
from app.modules.telemetry.dependencies import get_telemetry_query_service
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    GetPointMeasurementsRequest,
    ListObjectsRequest,
    MeasurementsResponse,
    ObjectDetailResponse,
    ObjectSummaryResponse,
    PaginatedResponse,
    PointMeasurementsResponse,
)
from app.modules.telemetry.services.query import TelemetryQueryService

router = APIRouter(
    prefix="/objects",
    tags=["telemetry"],
)

points_router = APIRouter(
    prefix="/points",
    tags=["telemetry"],
)


@router.get(
    "",
    response_model=PaginatedResponse[ObjectSummaryResponse],
    dependencies=[Depends(require_org_access(CAN_VIEW_ASSETS))],
)
def list_objects(
    org_id: UUID = Path(...),
    query: ListObjectsRequest = Depends(),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> PaginatedResponse[ObjectSummaryResponse]:
    """List all monitored objects with their latest readings and status."""
    return service.list_objects(organization_id=org_id, query=query)


@router.get(
    "/{object_id}",
    response_model=ObjectDetailResponse,
    dependencies=[Depends(require_org_access(CAN_VIEW_ASSETS))],
)
def get_object_detail(
    org_id: UUID = Path(...),
    object_id: UUID = Path(...),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> ObjectDetailResponse:
    """Get detailed view of a single object with its latest readings and
    available measurement points.
    """
    return service.get_object_detail(organization_id=org_id, object_id=object_id)


@router.get(
    "/{object_id}/measurements",
    response_model=MeasurementsResponse,
    dependencies=[Depends(require_org_access(CAN_VIEW_ASSETS))],
)
def get_measurements(
    org_id: UUID = Path(...),
    object_id: UUID = Path(...),
    query: GetMeasurementsRequest = Depends(),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> MeasurementsResponse:
    """Get time series measurements for an object."""
    return service.get_measurements(
        organization_id=org_id, object_id=object_id, query=query
    )


@points_router.get(
    "/{point_id}/measurements",
    response_model=PointMeasurementsResponse,
    dependencies=[Depends(require_org_access(CAN_VIEW_ASSETS))],
)
def get_point_measurements(
    org_id: UUID = Path(...),
    point_id: UUID = Path(...),
    query: GetPointMeasurementsRequest = Depends(),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> PointMeasurementsResponse:
    """Get the measurement history of a single measurement point."""
    return service.get_point_measurements(
        organization_id=org_id, point_id=point_id, query=query
    )
