"""Telemetry ingest business logic."""

from datetime import UTC, datetime

from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)


class TelemetryIngestService:
    def __init__(self, repository: TelemetryPacketRepository):
        self._repository = repository

    def ingest(self, packet: MeasurementPacketRequest) -> TelemetryIngestResponse:
        exists = self._repository.exists_by_device_seq(
            device_id=packet.device_id,
            seq=packet.seq,
        )

        if exists:
            return TelemetryIngestResponse(
                status="duplicate",
                device_id=packet.device_id,
                seq=packet.seq,
            )

        received_at = datetime.now(UTC)

        try:
            self._repository.create(packet=packet, received_at=received_at)
        except TelemetryPacketAlreadyExistsError:
            return TelemetryIngestResponse(
                status="duplicate",
                device_id=packet.device_id,
                seq=packet.seq,
            )

        return TelemetryIngestResponse(
            status="accepted",
            device_id=packet.device_id,
            seq=packet.seq,
        )
