import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.dependencies import dispose_sql_engines
from app.core.errors import register_error_handlers
from app.core.health import router as health_router
from app.core.logging import configure_logging
from app.modules.core_data.api.users import router as users_router
from app.modules.security.api import router as security_router
from app.modules.telemetry.api import router as telemetry_router

API_V1_PREFIX = "/api/v1"

settings = get_settings()
configure_logging(level=settings.log_level, json_output=settings.log_json)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Tables are managed by Alembic migrations.
    try:
        yield
    finally:
        dispose_sql_engines()
        logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=bool(settings.cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/", include_in_schema=False)
def root_redirect():
    if not settings.docs_enabled:
        return {"status": "ok"}
    return RedirectResponse(url="/docs")


# Infrastructure endpoints
app.include_router(health_router)

# Auth endpoints (unprefixed: /auth/*)
app.include_router(security_router)

# Ingest endpoint (unprefixed: /telemetry/ingest)
app.include_router(telemetry_router)

# API v1 endpoints
app.include_router(users_router, prefix=API_V1_PREFIX)
