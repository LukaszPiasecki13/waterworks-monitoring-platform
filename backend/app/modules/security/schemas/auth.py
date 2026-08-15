"""Authentication schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)


class LoginRequest(BaseModel):
    """Login request - supports email or username."""

    username: str = Field(...)  # Can be email or username
    password: str = Field(..., min_length=1, max_length=72)


class TokenResponse(BaseModel):
    """Token response."""

    access: str
    refresh: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""

    refresh: str


class UserResponse(BaseModel):
    """User response DTO."""

    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    status: str
    organization_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateRequest(BaseModel):
    """Self-service profile update request (email, name, optional password change)."""

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    current_password: str | None = Field(default=None, min_length=6, max_length=72)
    new_password: str | None = Field(default=None, min_length=6, max_length=72)
