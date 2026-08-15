"""Telemetry query/read endpoints for dashboard."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.core_data.models import User
from app.modules.security.dependencies import get_current_user
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
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.get(
    "/objects",
    response_model=PaginatedResponse[ObjectSummaryResponse],
)
def list_objects(
    query: ListObjectsRequest = Depends(),
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> PaginatedResponse[ObjectSummaryResponse]:
    """List all monitored objects with their latest readings and status."""
    return service.list_objects(user=user, query=query)


@router.get(
    "/objects/{object_id}",
    response_model=ObjectDetailResponse,
)
def get_object_detail(
    object_id: UUID,
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> ObjectDetailResponse:
    """Get detailed view of a single object with its latest readings and
    available measurement points.
    """
    return service.get_object_detail(user=user, object_id=object_id)


@router.get(
    "/objects/{object_id}/measurements",
    response_model=MeasurementsResponse,
)
def get_measurements(
    object_id: UUID,
    query: GetMeasurementsRequest = Depends(),
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> MeasurementsResponse:
    """Get time series measurements for an object."""
    return service.get_measurements(user=user, object_id=object_id, query=query)
