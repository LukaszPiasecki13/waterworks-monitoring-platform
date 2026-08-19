"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, Request

from app.core.rate_limit import limiter
from app.modules.core_data.models import User
from app.modules.security.dependencies import get_auth_service, get_current_user
from app.modules.security.schemas import (
    LoginRequest,
    ProfileUpdateRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.security.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request, data: LoginRequest, svc: AuthService = Depends(get_auth_service)
):
    """Login with username or email.

    Rate limited per IP: login is the one endpoint an attacker can hit
    repeatedly to guess passwords, unlike token-authenticated endpoints.
    """
    return svc.login(data)


@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(
    body: TokenRefreshRequest, svc: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token."""
    return svc.refresh(body.refresh)


@router.get("/user", response_model=UserResponse)
def get_user(user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return user


@router.patch("/user", response_model=UserResponse)
def update_user(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    svc: AuthService = Depends(get_auth_service),
):
    """Update the current authenticated user's own profile."""
    return svc.update_profile(user, data)
