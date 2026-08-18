"""Pydantic schemas for users."""

from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field

from app.core.schemas import BaseSchema


class PaginatedResponse[T](BaseSchema):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int


class UserResponse(BaseSchema):
    """User response DTO (platform-level, no organization scoping)."""

    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseSchema):
    """Admin user creation request (platform-level)."""

    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    is_active: bool = True


class UserUpdateRequest(BaseSchema):
    """Admin user update request (platform-level)."""

    username: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)


class ListUsersRequest(BaseSchema):
    """List users query parameters (platform-level)."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    search: str | None = None
    is_active: bool | None = None
