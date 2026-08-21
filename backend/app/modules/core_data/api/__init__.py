"""Core data API endpoints."""

from .context import router as context_router
from .devices import router as devices_router
from .measurement_points import router as measurement_points_router
from .members import router as members_router
from .organizations import router as organizations_router
from .users import router as users_router
from .water_objects import router as water_objects_router

__all__ = [
    "context_router",
    "devices_router",
    "measurement_points_router",
    "members_router",
    "organizations_router",
    "users_router",
    "water_objects_router",
]
