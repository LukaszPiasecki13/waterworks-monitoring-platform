"""Pydantic schemas for water objects."""

from typing import Literal
from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema

ObjectType = Literal["pump_station", "hydrophore", "intake", "network_point"]


class WaterObjectCreateRequest(BaseSchema):
    """Create water object request."""

    organization_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    object_type: ObjectType
    location_description: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None


class WaterObjectUpdateRequest(BaseSchema):
    """Update water object request."""

    name: str | None = Field(None, min_length=1, max_length=255)
    object_type: ObjectType | None = None
    location_description: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool | None = None


class WaterObjectResponse(BaseSchema):
    """Water object response DTO."""

    id: UUID
    organization_id: UUID
    name: str
    object_type: str
    location_description: str | None
    latitude: float | None
    longitude: float | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ListWaterObjectsRequest(BaseSchema):
    """List water objects query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    organization_id: UUID | None = None
