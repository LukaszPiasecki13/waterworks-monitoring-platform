"""Dependency wiring for telemetry module."""

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.services.ingest import TelemetryIngestService
from app.modules.telemetry.services.query import TelemetryQueryService


def get_device_secret_header(
    x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
) -> str | None:
    """Extract device secret from X-Device-Key header, if present."""
    return x_device_key


def get_telemetry_packet_repository(
    session: Session = Depends(get_db),
) -> TelemetryPacketRepository:
    return TelemetryPacketRepository(session=session)


def get_telemetry_ingest_service(
    repository: TelemetryPacketRepository = Depends(get_telemetry_packet_repository),
    session: Session = Depends(get_db),
) -> TelemetryIngestService:
    return TelemetryIngestService(repository=repository, session=session)


def get_telemetry_query_repository(
    session: Session = Depends(get_db),
) -> TelemetryQueryRepository:
    return TelemetryQueryRepository(session=session)


def get_telemetry_query_service(
    repository: TelemetryQueryRepository = Depends(get_telemetry_query_repository),
) -> TelemetryQueryService:
    return TelemetryQueryService(repository=repository, settings=get_settings())
