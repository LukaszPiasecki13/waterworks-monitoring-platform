"""Telemetry ingest endpoint."""

from fastapi import APIRouter, Depends, Response, status

from app.modules.core_data.models.device import Device
from app.modules.device_identity.dependencies import get_current_device
from app.modules.telemetry.dependencies import get_telemetry_ingest_service
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
    device: Device = Depends(get_current_device),
    service: TelemetryIngestService = Depends(get_telemetry_ingest_service),
) -> TelemetryIngestResponse:
    result = service.ingest(packet, device)

    if result.status == "duplicate":
        response.status_code = status.HTTP_200_OK

    return result
