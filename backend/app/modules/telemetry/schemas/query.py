"""Pydantic schemas for telemetry query/read endpoints."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema

ObjectStatus = Literal["ok", "warning", "no_comm", "no_data"]


class ListObjectsRequest(BaseSchema):
    """List objects query parameters."""

    org_id: UUID | None = None
    status: ObjectStatus | None = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)


class GetMeasurementsRequest(BaseSchema):
    """Get measurements query parameters."""

    point_id: str | None = None
    type_: str | None = Field(None, alias="type")
    start: datetime | None = None
    end: datetime | None = None
    limit: int = Field(1000, ge=1, le=5000)

    model_config = ConfigDict(populate_by_name=True)


class GetPointMeasurementsRequest(BaseSchema):
    """Get point history query parameters."""

    from_: datetime | None = Field(None, alias="from")
    to: datetime | None = None
    limit: int = Field(1000, ge=1, le=5000)

    model_config = ConfigDict(populate_by_name=True)


class LatestPointValue(BaseSchema):
    """Latest value for a single measurement point."""

    point_id: str
    point_name: str
    type: str
    unit: str
    value: float | int | bool | None = None
    quality: str
    measured_at: datetime
    device_id: str
    device_name: str

    model_config = ConfigDict(from_attributes=True)


class ObjectSummaryResponse(BaseSchema):
    """Summary of an object with its latest readings."""

    org_id: str
    org_name: str
    object_id: str
    name: str
    device_id: str | None = None
    device_name: str | None = None
    status: ObjectStatus
    last_contact_at: datetime | None = None
    last_measurement_at: datetime | None = None
    points: list[LatestPointValue] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ObjectDetailResponse(ObjectSummaryResponse):
    """Detailed view of an object."""

    last_seq: int | None = None
    available_points: list[str] = Field(default_factory=list)


class MeasurementSeriesItem(BaseSchema):
    """A single measurement in a time series."""

    point_id: str
    point_name: str
    type: str
    unit: str
    measured_at: datetime
    value: float | int | bool | None = None
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    quality: str
    device_id: str
    device_name: str

    model_config = ConfigDict(from_attributes=True)


class MeasurementsResponse(BaseSchema):
    """Time series measurements for an object."""

    object_id: str
    from_: datetime = Field(alias="from")
    to: datetime
    count: int
    # True when more measurements existed in range than `limit` allowed, so a
    # client can tell a complete series from one cut short.
    truncated: bool = False
    items: list[MeasurementSeriesItem]

    model_config = ConfigDict(populate_by_name=True)


class PointMeasurementItem(BaseSchema):
    """A single measurement window of one measurement point.

    `window_start` and `quality` are always present: a series is only
    interpretable if each value says when it was measured and whether the
    sensor trusted it.
    """

    window_start: datetime
    window_seconds: int
    value: float | int | bool | None = None
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    quality: str

    model_config = ConfigDict(from_attributes=True)


class PointMeasurementsResponse(BaseSchema):
    """History of a single measurement point."""

    point_id: str
    external_id: str
    type: str
    unit: str
    from_: datetime = Field(alias="from")
    to: datetime
    count: int
    truncated: bool = False
    items: list[PointMeasurementItem]

    model_config = ConfigDict(populate_by_name=True)


class PaginatedResponse[T](BaseSchema):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int
