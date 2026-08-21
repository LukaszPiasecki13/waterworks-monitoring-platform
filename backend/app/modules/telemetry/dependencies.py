"""Dependency wiring for telemetry module."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.services.ingest import TelemetryIngestService
from app.modules.telemetry.services.query import TelemetryQueryService


def get_telemetry_packet_repository(
    session: Session = Depends(get_db),
) -> TelemetryPacketRepository:
    return TelemetryPacketRepository(session=session)


def get_telemetry_ingest_service(
    repository: TelemetryPacketRepository = Depends(get_telemetry_packet_repository),
) -> TelemetryIngestService:
    return TelemetryIngestService(repository=repository)


def get_telemetry_query_repository(
    session: Session = Depends(get_db),
) -> TelemetryQueryRepository:
    return TelemetryQueryRepository(session=session)


def get_telemetry_query_service(
    repository: TelemetryQueryRepository = Depends(get_telemetry_query_repository),
) -> TelemetryQueryService:
    return TelemetryQueryService(repository=repository, settings=get_settings())
