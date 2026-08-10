"""Dependency wiring for telemetry module."""

import secrets

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.modules.telemetry.exceptions import InvalidTelemetryIngestKeyError
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.services.ingest import TelemetryIngestService
from app.modules.telemetry.services.query import TelemetryQueryService


def verify_telemetry_ingest_key(
    x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
) -> None:
    expected_key = get_settings().telemetry_ingest_key

    if not expected_key:
        return

    if x_device_key is None or not secrets.compare_digest(x_device_key, expected_key):
        raise InvalidTelemetryIngestKeyError


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
