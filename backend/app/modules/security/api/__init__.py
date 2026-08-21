"""Security API endpoints."""

from .auth import router as auth_router
from .groups import org_router, platform_router
from .permissions import router as permissions_router
from .platform_audit import router as platform_audit_router

__all__ = [
    "auth_router",
    "org_router",
    "permissions_router",
    "platform_audit_router",
    "platform_router",
]
