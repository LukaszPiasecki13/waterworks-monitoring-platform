"""Pydantic schemas for users."""

from typing import Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserStatus = Literal["regular", "admin"]

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int


class UserRegisterRequest(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    status: UserStatus = "regular"


class UserLoginRequest(BaseModel):
    """User login request - supports email or username."""

    username: str = Field(...)  # Can be username or email
    password: str = Field(...)


class TokenResponse(BaseModel):
    """Token response."""

    access: str = Field(alias="access_token")
    refresh: str = Field(alias="refresh_token")
    token_type: str = "bearer"

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    """User response DTO."""

    id: UUID
    organization_id: UUID | None
    username: str
    email: str
    first_name: str
    last_name: str
    status: UserStatus
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Admin user creation request."""

    organization_id: UUID | None = None
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    status: UserStatus = "regular"
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    """Admin user update request."""

    organization_id: UUID | None = None
    username: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    status: UserStatus | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)


class ListUsersRequest(BaseModel):
    """List users query parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    search: str | None = None
    status: UserStatus | None = None
    is_active: bool | None = None
