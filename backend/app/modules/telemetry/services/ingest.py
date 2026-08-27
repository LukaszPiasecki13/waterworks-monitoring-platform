"""Telemetry ingest business logic."""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from app.core.errors import BadRequestError, ConflictError, ForbiddenError
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.core_data.registry import SensorRegistry
from app.modules.core_data.services.measurement_points import MeasurementPointService
from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.models.telemetry_error import TelemetryError
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPoint as PacketPoint,
)


@dataclass(frozen=True)
class _IngestContext:
    """Bundles per-packet values threaded through the module-level helpers below."""

    packet: MeasurementPacketRequest
    device_id: UUID
    saved_packet_id: UUID
    received_at: datetime


def _authorize(packet: MeasurementPacketRequest, device: Device) -> None:
    if packet.device_id != device.external_id:
        raise ForbiddenError(
            "Device ID mismatch: packet doesn't match authenticated device"
        )
    if device.water_object_id is None:
        raise ConflictError(
            "Device not assigned to a water object", code="DEVICE_NOT_ASSIGNED"
        )


def _validate_point_type(point_type: str) -> None:
    """Validate point_type is in catalog. Raises BadRequestError if not."""
    if point_type not in SensorRegistry.point_type_ids():
        raise BadRequestError(
            f"Unknown point_type: {point_type}", code="UNKNOWN_POINT_TYPE"
        )


def _iter_points(packet: MeasurementPacketRequest) -> Iterator[PacketPoint]:
    """Flatten all points across all windows into a single stream."""
    for window in packet.windows:
        yield from window.points


def _build_response(
    status: Literal["accepted", "duplicate"], packet: MeasurementPacketRequest
) -> TelemetryIngestResponse:
    return TelemetryIngestResponse(
        status=status, device_id=packet.device_id, seq=packet.seq
    )


def _build_error(
    ctx: _IngestContext,
    *,
    code: str,
    point_id: str | None,
    severity: str,
    message: str | None,
) -> TelemetryError:
    return TelemetryError(
        packet_id=ctx.saved_packet_id,
        device_id=ctx.packet.device_id,
        point_id=point_id,
        code=code,
        severity=severity,
        message=message,
        occurred_at=ctx.received_at,
    )


def _packet_reported_errors(ctx: _IngestContext) -> list[TelemetryError]:
    """Convert device-reported error entries into TelemetryError rows."""
    return [
        _build_error(
            ctx,
            code=error.code,
            point_id=error.point_id,
            severity=error.severity,
            message=error.message,
        )
        for error in ctx.packet.errors
    ]


class TelemetryIngestService:
    def __init__(
        self,
        packet_repository: TelemetryPacketRepository,
        point_service: MeasurementPointService,
    ):
        self._packet_repository = packet_repository
        self._point_service = point_service

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
            BadRequestError: If packet contains unknown point_type
        """
        _authorize(packet, device)

        for point in _iter_points(packet):
            _validate_point_type(point.type)

        try:
            with self._packet_repository.transaction(skip_audit=True):
                duplicate = self._response_if_duplicate(packet)
                if duplicate:
                    return duplicate

                received_at = datetime.now(UTC)
                saved_packet = self._packet_repository.create(
                    packet=packet, received_at=received_at
                )
                ctx = _IngestContext(
                    packet=packet,
                    device_id=device.id,
                    saved_packet_id=saved_packet.id,
                    received_at=received_at,
                )

                mismatch_errors = self._process_measurement_windows(ctx)
                reported_errors = _packet_reported_errors(ctx)
                errors = mismatch_errors + reported_errors
                if errors:
                    self._packet_repository.session.add_all(errors)
                    self._packet_repository.flush()

                device.last_diagnostics_at = received_at
                self._packet_repository.session.flush()

        except TelemetryPacketAlreadyExistsError:
            return _build_response("duplicate", packet)

        return _build_response("accepted", packet)

    def delete_all_for_device(self, external_id: str) -> int:
        """Delete all telemetry packets for a device.

        Flushes rather than commits: the transaction belongs to the caller.
        Returns the number of packets deleted.
        """
        return self._packet_repository.delete_all_for_device(external_id)

    def _response_if_duplicate(
        self, packet: MeasurementPacketRequest
    ) -> TelemetryIngestResponse | None:
        is_duplicate = self._packet_repository.exists_by_device_seq(
            packet.device_id, packet.seq
        )
        if is_duplicate:
            return _build_response("duplicate", packet)
        return None

    def _process_measurement_windows(self, ctx: _IngestContext) -> list[TelemetryError]:
        """Resolve each reported point to its MeasurementPoint (auto-provisioning
        new ones) and flag any whose type/unit no longer matches what's on record.
        """
        errors: list[TelemetryError] = []
        resolved: dict[str, MeasurementPoint] = {}

        for point in _iter_points(ctx.packet):
            mp = resolved.get(point.point_id)
            if mp is None:
                mp = self._point_service.get_or_create_internal(
                    ctx.device_id, point.point_id, point.type, point.unit
                )
                resolved[point.point_id] = mp

            if mp.point_type != point.type or mp.unit != point.unit:
                errors.append(
                    _build_error(
                        ctx,
                        code="POINT_TYPE_MISMATCH",
                        point_id=point.point_id,
                        severity="critical",
                        message=(
                            f"Expected type={mp.point_type} unit={mp.unit}, "
                            f"got type={point.type} unit={point.unit}"
                        ),
                    )
                )

        return errors
