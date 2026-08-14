"""Telemetry packet repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.water_object import WaterObject
from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.schemas.measurement_packet import MeasurementPacketRequest


class TelemetryPacketRepository(SQLRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def exists_by_device_seq(self, device_id: str, seq: int) -> bool:
        stmt = select(TelemetryPacket.id).where(
            TelemetryPacket.device_id == device_id,
            TelemetryPacket.seq == seq,
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def create(
        self,
        packet: MeasurementPacketRequest,
        received_at: datetime,
    ) -> TelemetryPacket:
        device = (
            self.session.query(Device)
            .filter(Device.external_id == packet.device_id)
            .first()
        )

        if not device:
            raise NotFoundError(
                f"Device with external_id '{packet.device_id}' not found"
            )

        water_object = (
            self.session.query(WaterObject)
            .filter(WaterObject.id == device.water_object_id)
            .first()
        )

        if not water_object:
            raise NotFoundError(
                f"Water object with id '{device.water_object_id}' not found"
            )

        entity = TelemetryPacket(
            device_id=packet.device_id,
            seq=packet.seq,
            sent_at=packet.sent_at,
            received_at=received_at,
            payload=packet.model_dump(mode="json"),
        )

        self.session.add(entity)

        try:
            self.commit(skip_audit=True)
        except IntegrityError as exc:
            self.rollback()
            message = (
                str(exc.orig).lower() if exc.orig is not None else str(exc).lower()
            )
            is_unique_device_seq = (
                "uq_telemetry_packets_device_seq" in message
                or "telemetry_packets.device_id, telemetry_packets.seq" in message
                or "telemetry_packets.device_id,telemetry_packets.seq" in message
            )
            if is_unique_device_seq:
                raise TelemetryPacketAlreadyExistsError(
                    packet.device_id,
                    packet.seq,
                ) from exc
            raise

        self.refresh(entity)
        return entity
