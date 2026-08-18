"""Telemetry ingest endpoint."""

from fastapi import APIRouter, Depends, Response, status

from app.modules.telemetry.dependencies import (
    get_device_secret_header,
    get_telemetry_ingest_service,
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
)
def ingest_measurement_packet(
    packet: MeasurementPacketRequest,
    response: Response,
    device_secret: str | None = Depends(get_device_secret_header),
    service: TelemetryIngestService = Depends(get_telemetry_ingest_service),
) -> TelemetryIngestResponse:
    result = service.ingest(packet, device_secret)

    if result.status == "duplicate":
        response.status_code = status.HTTP_200_OK

    return result
