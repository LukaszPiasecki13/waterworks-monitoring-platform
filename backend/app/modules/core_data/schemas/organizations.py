"""Pydantic schemas for organizations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreateRequest(BaseModel):
    """Create organization request."""

    name: str = Field(..., min_length=1, max_length=255)


class OrganizationUpdateRequest(BaseModel):
    """Update organization request."""

    name: str | None = Field(None, min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    """Organization response DTO."""

    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ListOrganizationsRequest(BaseModel):
    """List organizations query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
