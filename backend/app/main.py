from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.errors import register_error_handlers

from app.modules.core_data.api.users import router as users_router
from app.modules.security.api import router as security_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Tables are managed by Alembic migrations.
    yield


app = FastAPI(
    title="waterworks-monitoring-platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")


# Auth endpoints (no /api/v1 prefix for backward compatibility)
app.include_router(security_router)

# API v1 endpoints
app.include_router(users_router, prefix="/api/v1")
