import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.dependencies import create_session, dispose_sql_engines
from app.core.errors import register_error_handlers
from app.core.health import router as health_router
from app.core.logging import configure_logging
from app.core.rate_limit import register_rate_limiting
from app.modules.core_data.api import (
    context_router,
    devices_organizations_router,
    devices_platform_router,
    devices_router,
    measurement_points_router,
    members_router,
    users_router,
    water_objects_platform_router,
    water_objects_router,
)
from app.modules.device_identity.api.activation_codes import (
    activation_codes_router,
)
from app.modules.device_identity.api.activation_redeem import (
    activation_redeem_router,
)
from app.modules.device_identity.api.claims import claims_router
from app.modules.device_identity.api.device_auth import device_auth_router
from app.modules.device_identity.api.provisioning import provisioning_router
from app.modules.security.api import (
    auth_router,
    org_router,
    permissions_router,
    platform_audit_router,
    platform_router,
)
from app.modules.security.dependencies import get_group_repo, get_permission_repo
from app.modules.security.services.seed import SecuritySeedService
from app.modules.telemetry.api.ingest import router as telemetry_ingest_router
from app.modules.telemetry.api.query import router as telemetry_query_router

API_V1_PREFIX = "/api/v1"

settings = get_settings()
configure_logging(level=settings.log_level, json_output=settings.log_json)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Seed security (permissions + system groups)
    try:
        session = create_session()
        try:
            perm_repo = get_permission_repo(session)
            group_repo = get_group_repo(session)
            seed = SecuritySeedService(perm_repo, group_repo)
            seed.seed()
        finally:
            session.close()
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
register_rate_limiting(app)


@app.get("/", include_in_schema=False)
def root_redirect():
    if not settings.docs_enabled:
        return {"status": "ok"}
    return RedirectResponse(url="/docs")


# Infrastructure endpoints
app.include_router(health_router)

# Auth endpoints (unprefixed: /auth/*)
app.include_router(auth_router)
app.include_router(context_router)

# Ingest endpoint (unprefixed: /telemetry/ingest)
app.include_router(telemetry_ingest_router)

# Device authentication endpoints (unprefixed: /devices/auth/*)
app.include_router(device_auth_router)

# Device activation endpoints (unprefixed: /devices/activation/*)
app.include_router(activation_redeem_router)

# API v1 endpoints - platform level
app.include_router(users_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(devices_organizations_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(platform_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(platform_audit_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(provisioning_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(activation_codes_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(devices_platform_router, prefix=f"{API_V1_PREFIX}/platform")
app.include_router(water_objects_platform_router, prefix=f"{API_V1_PREFIX}/platform")

# API v1 endpoints - organization level
app.include_router(water_objects_router, prefix=API_V1_PREFIX)
app.include_router(devices_router, prefix=API_V1_PREFIX)
app.include_router(claims_router, prefix=API_V1_PREFIX)
app.include_router(measurement_points_router, prefix=API_V1_PREFIX)
app.include_router(members_router, prefix=API_V1_PREFIX)
app.include_router(permissions_router, prefix=API_V1_PREFIX)
app.include_router(org_router, prefix=API_V1_PREFIX)
app.include_router(
    telemetry_query_router, prefix=f"{API_V1_PREFIX}/orgs/{{org_id}}/telemetry"
)
