"""Authentication schemas."""

from pydantic import EmailStr, Field

from app.core.schemas import BaseSchema


class LoginRequest(BaseSchema):
    """Login request - supports email or username."""

    username: str = Field(...)  # Can be email or username
    password: str = Field(..., min_length=1, max_length=72)


class TokenResponse(BaseSchema):
    """Token response."""

    access: str
    refresh: str


class TokenRefreshRequest(BaseSchema):
    """Token refresh request."""

    refresh: str


class ProfileUpdateRequest(BaseSchema):
    """Self-service profile update request (email, name, optional password change)."""

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    current_password: str | None = Field(default=None, min_length=6, max_length=72)
    new_password: str | None = Field(default=None, min_length=6, max_length=72)
