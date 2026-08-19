"""Telemetry query/read endpoints for dashboard."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.security.dependencies import require_org_permission
from app.modules.security.permission_catalog import CAN_VIEW_ASSETS
from app.modules.telemetry.dependencies import get_telemetry_query_service
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    ListObjectsRequest,
    MeasurementsResponse,
    ObjectDetailResponse,
    ObjectSummaryResponse,
    PaginatedResponse,
)
from app.modules.telemetry.services.query import TelemetryQueryService

router = APIRouter(
    prefix="/objects",
    tags=["telemetry"],
)


@router.get(
    "",
    response_model=PaginatedResponse[ObjectSummaryResponse],
    dependencies=[Depends(require_org_permission(CAN_VIEW_ASSETS))],
)
def list_objects(
    org_id: UUID,
    query: ListObjectsRequest = Depends(),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> PaginatedResponse[ObjectSummaryResponse]:
    """List all monitored objects with their latest readings and status."""
    return service.list_objects(organization_id=org_id, query=query)


@router.get(
    "/{object_id}",
    response_model=ObjectDetailResponse,
    dependencies=[Depends(require_org_permission(CAN_VIEW_ASSETS))],
)
def get_object_detail(
    org_id: UUID,
    object_id: UUID,
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> ObjectDetailResponse:
    """Get detailed view of a single object with its latest readings and
    available measurement points.
    """
    return service.get_object_detail(organization_id=org_id, object_id=object_id)


@router.get(
    "/{object_id}/measurements",
    response_model=MeasurementsResponse,
    dependencies=[Depends(require_org_permission(CAN_VIEW_ASSETS))],
)
def get_measurements(
    org_id: UUID,
    object_id: UUID,
    query: GetMeasurementsRequest = Depends(),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> MeasurementsResponse:
    """Get time series measurements for an object."""
    return service.get_measurements(
        organization_id=org_id, object_id=object_id, query=query
    )
