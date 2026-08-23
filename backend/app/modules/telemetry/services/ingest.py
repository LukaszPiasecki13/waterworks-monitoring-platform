"""Telemetry ingest business logic."""

from datetime import UTC, datetime

from app.core.errors import ConflictError, ForbiddenError
from app.modules.core_data.models.device import Device
from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)


class TelemetryIngestService:
    def __init__(self, repository: TelemetryPacketRepository):
        self._repository = repository

    def ingest(
        self, packet: MeasurementPacketRequest, device: Device
    ) -> TelemetryIngestResponse:
        """Ingest a telemetry packet from an authenticated device.

        Args:
            packet: The measurement packet
            device: The authenticated device (from bearer token)

        Raises:
            ForbiddenError: If packet device_id doesn't match authenticated device
            ConflictError: If device is not assigned to a water object
        """
        if packet.device_id != device.external_id:
            raise ForbiddenError(
                "Device ID mismatch: packet doesn't match authenticated device"
            )

        if device.water_object_id is None:
            raise ConflictError(
                "Device not assigned to a water object",
                code="DEVICE_NOT_ASSIGNED",
            )

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
            with self._repository.transaction(skip_audit=True):
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

    def delete_all_for_device(self, external_id: str) -> int:
        """Delete all telemetry packets for a device.

        Flushes rather than commits: the transaction belongs to the caller.
        Returns the number of packets deleted.
        """
        return self._repository.delete_all_for_device(external_id)
