"""Telemetry ingest business logic."""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import ValidationError

from app.core.errors import BadRequestError, ConflictError, ForbiddenError
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.core_data.registry import SensorRegistry
from app.modules.core_data.services.measurement_points import MeasurementPointService
from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.models.telemetry_error import TelemetryError
from app.modules.telemetry.repositories.device_state import (
    DeviceStateReportRepository,
)
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.device_state import (
    SECTION_DEVICE,
    DeviceStateData,
    StateSectionEntry,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPoint as PacketPoint,
)

# Typed models for the sections this backend understands. A section absent
# here is still stored verbatim — the registry decides what is accepted, this
# map only decides what is additionally type-checked on the way in.
_SECTION_MODELS: dict[str, type[DeviceStateData]] = {SECTION_DEVICE: DeviceStateData}

# How far ahead of the platform a device clock may run before its captured_at
# is treated as wrong rather than as skew. NTP sync happens at boot and the
# device stamps captures from the same clock as `sent_at`, so anything beyond
# this is a broken clock, not jitter.
CLOCK_AHEAD_TOLERANCE = timedelta(minutes=5)


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


def _validate_section(entry: StateSectionEntry) -> str | None:
    """Type-check a section's payload; return a failure message or None.

    Only sections with a typed model are checked. A section the registry
    accepts but this backend has no model for passes through unchanged —
    that is what lets a new read ship on the device before the backend
    learns its shape.
    """
    model = _SECTION_MODELS.get(entry.section)
    if model is None:
        return None
    try:
        model.model_validate(entry.data)
    except ValidationError as exc:
        return "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in exc.errors()[:3]
        )
    return None


class TelemetryIngestService:
    def __init__(
        self,
        packet_repository: TelemetryPacketRepository,
        point_service: MeasurementPointService,
        state_repository: DeviceStateReportRepository,
    ):
        self._packet_repository = packet_repository
        self._point_service = point_service
        self._state_repository = state_repository

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
                    # A retransmission after a lost ACK carries no new data but
                    # is still proof of life: dropping it here would let a
                    # device that keeps retrying read as silent.
                    device.last_seen_at = datetime.now(UTC)
                    self._packet_repository.session.flush()
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
                state_errors = self._process_state_sections(ctx, device)
                reported_errors = _packet_reported_errors(ctx)
                errors = mismatch_errors + state_errors + reported_errors
                if errors:
                    self._packet_repository.session.add_all(errors)
                    self._packet_repository.flush()

                # Any packet proves the device is alive; only a state report
                # proves it answered a read. Before B-08 both meanings shared
                # last_diagnostics_at, which made the field's name a lie.
                device.last_seen_at = received_at
                self._packet_repository.session.flush()

        except TelemetryPacketAlreadyExistsError:
            # Lost the race to a concurrent request for the same (device_id,
            # seq). No last_seen_at here: the repository already rolled this
            # transaction back, and the request that won recorded the very
            # same proof of life microseconds earlier.
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

    def _process_state_sections(
        self, ctx: _IngestContext, device: Device
    ) -> list[TelemetryError]:
        """Persist the state sections a device attached to this packet.

        Invariant worth keeping: diagnostics must never cost you telemetry.
        An unknown, stale-versioned or malformed section becomes an error
        entry and (where it can be) is still stored, but never turns a packet
        full of good measurements into a rejection.
        """
        errors: list[TelemetryError] = []
        seen: set[str] = set()

        for entry in ctx.packet.state:
            if entry.section in seen:
                # The unique constraint would reject the second row anyway;
                # failing here keeps the whole packet from rolling back.
                errors.append(
                    _build_error(
                        ctx,
                        code="STATE_SECTION_INVALID",
                        point_id=None,
                        severity="warning",
                        message=f"Duplicate state section '{entry.section}' in packet",
                    )
                )
                continue
            seen.add(entry.section)

            expected_version = SensorRegistry.state_section_schema_version(
                entry.section
            )
            if expected_version is None:
                errors.append(
                    _build_error(
                        ctx,
                        code="STATE_SECTION_UNKNOWN",
                        point_id=None,
                        severity="warning",
                        message=f"Unknown state section '{entry.section}'",
                    )
                )
                continue

            trustworthy = True

            if expected_version != entry.schema_version:
                trustworthy = False
                errors.append(
                    _build_error(
                        ctx,
                        code="STATE_SCHEMA_VERSION_MISMATCH",
                        point_id=None,
                        severity="info",
                        message=(
                            f"Section '{entry.section}' sent schema_version="
                            f"{entry.schema_version}, registry expects "
                            f"{expected_version}"
                        ),
                    )
                )
            else:
                failure = _validate_section(entry)
                if failure is not None:
                    trustworthy = False
                    errors.append(
                        _build_error(
                            ctx,
                            code="STATE_SECTION_INVALID",
                            point_id=None,
                            severity="warning",
                            message=f"Section '{entry.section}': {failure}"[:512],
                        )
                    )

            # A capture cannot have happened after it arrived. Left unclamped, a
            # device whose clock jumped into the future would win the
            # "latest per section" ranking forever and, with the age clamped at
            # zero, keep reading as fresh — frozen data presented as live.
            captured_at = entry.captured_at
            if captured_at > ctx.received_at + CLOCK_AHEAD_TOLERANCE:
                errors.append(
                    _build_error(
                        ctx,
                        code="STATE_CLOCK_AHEAD",
                        point_id=None,
                        severity="warning",
                        message=(
                            f"Section '{entry.section}' captured_at "
                            f"{captured_at.isoformat()} is ahead of arrival "
                            f"{ctx.received_at.isoformat()}; clamped"
                        )[:512],
                    )
                )
                captured_at = ctx.received_at

            self._state_repository.create(
                packet_id=ctx.saved_packet_id,
                device_id=ctx.packet.device_id,
                section=entry.section,
                schema_version=entry.schema_version,
                captured_at=captured_at,
                received_at=ctx.received_at,
                data=entry.data,
            )

            if entry.section == SECTION_DEVICE:
                # Answering at all is what last_diagnostics_at records, so a
                # malformed answer still counts. Promoting a field out of the
                # blob onto the Device row is a different claim, and a section
                # we just flagged has not earned it.
                device.last_diagnostics_at = ctx.received_at
                reported_firmware = entry.data.get("firmware_version")
                if (
                    trustworthy
                    and isinstance(reported_firmware, str)
                    and reported_firmware
                ):
                    device.firmware_version = reported_firmware[:50]

        return errors

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
