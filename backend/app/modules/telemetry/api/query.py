"""Telemetry query/read endpoints for dashboard."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.modules.core_data.models import User
from app.modules.security.dependencies import get_current_user
from app.modules.telemetry.dependencies import get_telemetry_query_service
from app.modules.telemetry.schemas.query import (
    MeasurementsResponse,
    ObjectDetail,
    ObjectStatus,
    ObjectSummary,
    PaginatedResponse,
)
from app.modules.telemetry.services.query import TelemetryQueryService

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.get(
    "/objects",
    response_model=PaginatedResponse[ObjectSummary],
)
def list_objects(
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
    org_id: str | None = Query(None, description="Filter by organization ID"),
    status: ObjectStatus | None = Query(None, description="Filter by object status"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=500, description="Number of items to return"),
) -> PaginatedResponse[ObjectSummary]:
    """List all monitored objects with their latest readings and status."""
    return service.list_objects(
        user=user, org_id=org_id, status=status, skip=skip, limit=limit
    )


@router.get(
    "/objects/{object_id}",
    response_model=ObjectDetail,
)
def get_object_detail(
    object_id: str,
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
) -> ObjectDetail:
    """Get detailed view of a single object with its latest readings and
    available measurement points.
    """
    return service.get_object_detail(user=user, object_id=object_id)


@router.get(
    "/objects/{object_id}/measurements",
    response_model=MeasurementsResponse,
)
def get_measurements(
    object_id: str,
    user: User = Depends(get_current_user),
    service: TelemetryQueryService = Depends(get_telemetry_query_service),
    point_id: str | None = Query(None, description="Filter by measurement point ID"),
    type_: str | None = Query(
        None, alias="type", description="Filter by measurement type"
    ),
    start: datetime | None = Query(
        None, description="Start time (ISO 8601, defaults to 24h ago)"
    ),
    end: datetime | None = Query(
        None, description="End time (ISO 8601, defaults to now)"
    ),
    limit: int = Query(
        1000, ge=1, le=5000, description="Max number of measurements to return"
    ),
) -> MeasurementsResponse:
    """Get time series measurements for an object."""
    return service.get_measurements(
        user=user,
        object_id=object_id,
        point_id=point_id,
        type_=type_,
        start=start,
        end=end,
        limit=limit,
    )
