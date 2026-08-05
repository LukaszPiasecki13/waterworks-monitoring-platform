"""Telemetry ingest endpoint."""

from fastapi import APIRouter, Depends, Response, status

from app.modules.telemetry.dependencies import (
    get_telemetry_ingest_service,
    verify_telemetry_ingest_key,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.post(
    "/ingest",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_telemetry_ingest_key)],
)
def ingest_measurement_packet(
    packet: MeasurementPacketRequest,
    response: Response,
    service: TelemetryIngestService = Depends(get_telemetry_ingest_service),
) -> TelemetryIngestResponse:
    result = service.ingest(packet)

    if result.status == "duplicate":
        response.status_code = status.HTTP_200_OK

    return result
