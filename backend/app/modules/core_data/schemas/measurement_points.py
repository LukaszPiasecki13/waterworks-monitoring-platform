"""Pydantic schemas for measurement points."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PointType = Literal["pressure", "flow_rate", "total_volume", "power_status"]


class MeasurementPointCreateRequest(BaseModel):
    """Create measurement point request."""

    device_id: int
    external_id: str = Field(..., min_length=1, max_length=128)
    point_type: PointType
    unit: str = Field(..., min_length=1, max_length=20)
    min_technical: float | None = None
    max_technical: float | None = None


class MeasurementPointUpdateRequest(BaseModel):
    """Update measurement point request."""

    point_type: PointType | None = None
    unit: str | None = Field(None, min_length=1, max_length=20)
    min_technical: float | None = None
    max_technical: float | None = None
    is_active: bool | None = None


class MeasurementPointResponse(BaseModel):
    """Measurement point response DTO."""

    id: int
    device_id: int
    external_id: str
    point_type: str
    unit: str
    min_technical: float | None
    max_technical: float | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ListMeasurementPointsRequest(BaseModel):
    """List measurement points query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    device_id: int | None = None
