"""Telemetry ingest business logic."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.core_data.models.device import Device
from app.modules.security.services.password import verify_password
from app.modules.telemetry.exceptions import (
    InactiveDeviceError,
    InvalidDeviceSecretError,
    TelemetryPacketAlreadyExistsError,
    UnknownDeviceError,
)
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)


class TelemetryIngestService:
    def __init__(self, repository: TelemetryPacketRepository, session: Session):
        self._repository = repository
        self._session = session

    def _verify_device_credentials(
        self, device_id: str, device_secret: str | None
    ) -> Device:
        """Authenticate a device by external_id and secret.

        Returns the Device if valid.
        Raises UnknownDeviceError (401), InvalidDeviceSecretError (403),
        or InactiveDeviceError (403).
        """
        if device_secret is None:
            raise InvalidDeviceSecretError

        stmt = select(Device).where(Device.external_id == device_id)
        device = self._session.execute(stmt).scalar_one_or_none()

        if not device:
            raise UnknownDeviceError(device_id)

        if not device.is_active:
            raise InactiveDeviceError(device_id)

        if not verify_password(device_secret, device.hashed_secret):
            raise InvalidDeviceSecretError

        return device

    def ingest(
        self, packet: MeasurementPacketRequest, device_secret: str | None
    ) -> TelemetryIngestResponse:
        """Ingest a telemetry packet from an authenticated device."""
        self._verify_device_credentials(packet.device_id, device_secret)

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
