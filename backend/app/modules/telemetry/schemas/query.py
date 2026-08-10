"""Pydantic schemas for telemetry query/read endpoints."""

from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

ObjectStatus = Literal["ok", "warning", "no_comm", "no_data"]


class LatestPointValue(BaseModel):
    """Latest value for a single measurement point."""

    point_id: str
    type: str
    unit: str
    value: float | int | bool | None = None
    quality: str
    measured_at: datetime
    device_id: str

    model_config = ConfigDict(from_attributes=True)


class ObjectSummary(BaseModel):
    """Summary of an object with its latest readings."""

    org_id: str
    object_id: str
    device_id: str
    status: ObjectStatus
    last_contact_at: datetime | None = None
    last_measurement_at: datetime | None = None
    points: list[LatestPointValue] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ObjectDetail(ObjectSummary):
    """Detailed view of an object."""

    last_seq: int | None = None
    available_points: list[str] = Field(default_factory=list)


class MeasurementSeriesItem(BaseModel):
    """A single measurement in a time series."""

    point_id: str
    type: str
    unit: str
    measured_at: datetime
    value: float | int | bool | None = None
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    quality: str
    device_id: str

    model_config = ConfigDict(from_attributes=True)


class MeasurementsResponse(BaseModel):
    """Time series measurements for an object."""

    object_id: str
    from_: datetime = Field(alias="from")
    to: datetime
    count: int
    items: list[MeasurementSeriesItem]

    model_config = ConfigDict(populate_by_name=True)


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int
