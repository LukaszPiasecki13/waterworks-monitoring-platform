"""Dependency wiring for telemetry module.

Note: this module builds its own MeasurementPointService (repeating the wiring
in app.modules.core_data.dependencies) rather than importing it from there.
core_data.dependencies imports get_telemetry_ingest_service (for
DeviceLifecycleService), so importing back from core_data.dependencies here
would create a circular import.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.config import get_settings
from app.core.dependencies import get_db
from app.modules.audit.dependencies import get_audit_service
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.telemetry.repositories.device_state import (
    DeviceStateReportRepository,
)
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.services.device_state import DeviceStateQueryService
from app.modules.telemetry.services.ingest import TelemetryIngestService
from app.modules.telemetry.services.query import TelemetryQueryService


def get_telemetry_packet_repository(
    session: Session = Depends(get_db),
) -> TelemetryPacketRepository:
    return TelemetryPacketRepository(session=session)


def _get_measurement_point_repo(
    session: Session = Depends(get_db),
) -> MeasurementPointRepository:
    return MeasurementPointRepository(session=session)


def _get_device_repo(session: Session = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(session=session)


def _get_measurement_point_service(
    repo: MeasurementPointRepository = Depends(_get_measurement_point_repo),
    device_repo: DeviceRepository = Depends(_get_device_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> MeasurementPointService:
    return MeasurementPointService(repo, device_repo, audit)


def get_device_state_repository(
    session: Session = Depends(get_db),
) -> DeviceStateReportRepository:
    return DeviceStateReportRepository(session=session)


def get_telemetry_ingest_service(
    packet_repository: TelemetryPacketRepository = Depends(
        get_telemetry_packet_repository
    ),
    point_service: MeasurementPointService = Depends(_get_measurement_point_service),
    state_repository: DeviceStateReportRepository = Depends(
        get_device_state_repository
    ),
) -> TelemetryIngestService:
    return TelemetryIngestService(
        packet_repository=packet_repository,
        point_service=point_service,
        state_repository=state_repository,
    )


def _get_water_object_repo(
    session: Session = Depends(get_db),
) -> WaterObjectRepository:
    return WaterObjectRepository(session=session)


def _get_device_service(
    repo: DeviceRepository = Depends(_get_device_repo),
    water_object_repo: WaterObjectRepository = Depends(_get_water_object_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> DeviceService:
    return DeviceService(repo, water_object_repo, audit)


def get_device_state_query_service(
    repository: DeviceStateReportRepository = Depends(get_device_state_repository),
    device_service: DeviceService = Depends(_get_device_service),
) -> DeviceStateQueryService:
    return DeviceStateQueryService(
        repository=repository,
        device_service=device_service,
        settings=get_settings(),
    )


def get_telemetry_query_repository(
    session: Session = Depends(get_db),
) -> TelemetryQueryRepository:
    return TelemetryQueryRepository(session=session)


def get_telemetry_query_service(
    repository: TelemetryQueryRepository = Depends(get_telemetry_query_repository),
) -> TelemetryQueryService:
    return TelemetryQueryService(repository=repository, settings=get_settings())
