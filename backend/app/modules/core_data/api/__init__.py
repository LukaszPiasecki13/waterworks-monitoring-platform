"""Core data API endpoints."""

from fastapi import APIRouter

from .context import router as context_router
from .devices import router as devices_router
from .measurement_points import router as measurement_points_router
from .organizations import router as organizations_router
from .users import router as users_router
from .water_objects import router as water_objects_router

router = APIRouter()
router.include_router(context_router)
router.include_router(organizations_router)
router.include_router(users_router)
router.include_router(water_objects_router)
router.include_router(devices_router)
router.include_router(measurement_points_router)

__all__ = ["router"]
