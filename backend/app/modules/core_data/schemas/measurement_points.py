"""Pydantic schemas for measurement points."""

from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema
from app.modules.core_data.schemas.point_types import PointType


class MeasurementPointCreateRequest(BaseSchema):
    """Create measurement point request."""

    device_id: UUID
    external_id: str = Field(..., min_length=1, max_length=128)
    point_type: PointType
    unit: str = Field(..., min_length=1, max_length=20)
    min_technical: float | None = None
    max_technical: float | None = None


class MeasurementPointUpdateRequest(BaseSchema):
    """Update measurement point request."""

    point_type: PointType | None = None
    unit: str | None = Field(None, min_length=1, max_length=20)
    min_technical: float | None = None
    max_technical: float | None = None
    is_active: bool | None = None


class MeasurementPointResponse(BaseSchema):
    """Measurement point response DTO."""

    id: UUID
    device_id: UUID
    external_id: str
    point_type: str
    unit: str
    min_technical: float | None
    max_technical: float | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ListMeasurementPointsRequest(BaseSchema):
    """List measurement points query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    device_id: UUID | None = None
    organization_id: UUID | None = None
