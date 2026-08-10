"""Telemetry API endpoints."""

from fastapi import APIRouter

from app.modules.telemetry.api.ingest import router as ingest_router
from app.modules.telemetry.api.query import router as query_router

router = APIRouter()
router.include_router(ingest_router)

__all__ = ["router", "query_router"]
