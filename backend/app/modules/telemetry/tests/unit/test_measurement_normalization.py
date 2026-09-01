"""Ingest → `measurements` → query, end to end on an in-memory database."""

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.core_data.models import Device, MeasurementPoint
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.services.measurement_points import MeasurementPointService
from app.modules.telemetry.models import Measurement
from app.modules.telemetry.repositories.measurements import MeasurementRepository
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    MeasurementWindow,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPoint as PacketPoint,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService
from app.modules.telemetry.tests.unit.conftest import DEVICE_EXTERNAL_ID

WINDOW_START = datetime(2026, 8, 26, 10, 30, tzinfo=UTC)


def _service(session: Session) -> TelemetryIngestService:
    point_service = MeasurementPointService(
        MeasurementPointRepository(session),
        DeviceRepository(session),
        MagicMock(),
    )
    return TelemetryIngestService(
        packet_repository=TelemetryPacketRepository(session),
        point_service=point_service,
        measurement_repository=MeasurementRepository(session),
    )


def _packet(
    *,
    seq: int = 1,
    points: list[PacketPoint] | None = None,
    window_start: datetime = WINDOW_START,
    windows: list[MeasurementWindow] | None = None,
) -> MeasurementPacketRequest:
    if windows is None:
        windows = [
            MeasurementWindow(
                window_start=window_start,
                window_seconds=15,
                points=points
                or [
                    PacketPoint(
                        point_id="pressure-inlet",
                        type="pressure",
                        unit="bar",
                        quality="good",
                        value=3.42,
                    )
                ],
            )
        ]
    return MeasurementPacketRequest(
        v=2,
        device_id=DEVICE_EXTERNAL_ID,
        seq=seq,
        sent_at=WINDOW_START,
        windows=windows,
    )


def _measurements(session: Session) -> list[Measurement]:
    return list(
        session.execute(
            select(Measurement).order_by(Measurement.window_start)
        ).scalars()
    )


def test_packet_creates_one_row_per_point_and_window(
    session: Session, device: Device
) -> None:
    service = _service(session)
    service.ingest(
        _packet(
            windows=[
                MeasurementWindow(
                    window_start=WINDOW_START,
                    window_seconds=15,
                    points=[
                        PacketPoint(
                            point_id="pressure-inlet",
                            type="pressure",
                            unit="bar",
                            quality="good",
                            value=3.42,
                        ),
                        PacketPoint(
                            point_id="pt100",
                            type="temperature",
                            unit="°C",
                            quality="good",
                            value=23.5,
                        ),
                    ],
                ),
                MeasurementWindow(
                    window_start=WINDOW_START + timedelta(seconds=15),
                    window_seconds=15,
                    points=[
                        PacketPoint(
                            point_id="pressure-inlet",
                            type="pressure",
                            unit="bar",
                            quality="good",
                            value=3.44,
                        )
                    ],
                ),
            ]
        ),
        device,
    )

    assert len(_measurements(session)) == 3


def test_same_windows_resent_under_new_seq_create_no_duplicates(
    session: Session, device: Device
) -> None:
    """Idempotency is per (point, window) — independent of (device_id, seq).

    A gateway that retransmits a buffered window under a fresh sequence
    number passes the packet-level dedupe, so the measurement table has to
    reject the duplicate itself.
    """
    service = _service(session)
    service.ingest(_packet(seq=1), device)
    service.ingest(_packet(seq=2), device)

    rows = _measurements(session)
    assert len(rows) == 1
    assert rows[0].value == pytest.approx(3.42)


def test_bool_value_is_stored_apart_from_numeric_values(
    session: Session, device: Device
) -> None:
    service = _service(session)
    service.ingest(
        _packet(
            points=[
                PacketPoint(
                    point_id="pump-running",
                    type="digital_input",
                    unit="bool",
                    quality="good",
                    value=True,
                )
            ]
        ),
        device,
    )

    row = _measurements(session)[0]
    assert row.value is None
    assert row.value_bool is True


def test_numeric_value_leaves_the_bool_column_empty(
    session: Session, device: Device
) -> None:
    service = _service(session)
    service.ingest(_packet(), device)

    row = _measurements(session)[0]
    assert row.value == pytest.approx(3.42)
    assert row.value_bool is None


def test_aggregate_only_point_keeps_value_null(
    session: Session, device: Device
) -> None:
    service = _service(session)
    service.ingest(
        _packet(
            points=[
                PacketPoint(
                    point_id="pressure-inlet",
                    type="pressure",
                    unit="bar",
                    quality="suspect",
                    avg=3.42,
                    min=3.38,
                    max=3.45,
                )
            ]
        ),
        device,
    )

    row = _measurements(session)[0]
    assert row.value is None
    assert row.value_bool is None
    assert (row.avg, row.min, row.max) == (
        pytest.approx(3.42),
        pytest.approx(3.38),
        pytest.approx(3.45),
    )
    assert row.quality == "suspect"


def test_unknown_point_is_auto_provisioned_and_normalized(
    session: Session, device: Device
) -> None:
    """A point the registry has never seen still produces a measurement."""
    service = _service(session)
    service.ingest(
        _packet(
            points=[
                PacketPoint(
                    point_id="brand-new-sensor",
                    type="level",
                    unit="m",
                    quality="good",
                    value=1.75,
                )
            ]
        ),
        device,
    )

    point = session.execute(
        select(MeasurementPoint).where(
            MeasurementPoint.external_id == "brand-new-sensor"
        )
    ).scalar_one()
    row = _measurements(session)[0]
    assert row.measurement_point_id == point.id
    assert row.value == pytest.approx(1.75)


def test_point_type_mismatch_is_not_normalized(
    session: Session, device: Device
) -> None:
    """A value whose unit contradicts the registered point stays in the blob."""
    service = _service(session)
    service.ingest(_packet(seq=1), device)

    service.ingest(
        _packet(
            seq=2,
            window_start=WINDOW_START + timedelta(seconds=15),
            points=[
                PacketPoint(
                    point_id="pressure-inlet",
                    type="pressure",
                    unit="kPa",
                    quality="good",
                    value=342.0,
                )
            ],
        ),
        device,
    )

    rows = _measurements(session)
    assert len(rows) == 1
    assert rows[0].window_start.replace(tzinfo=UTC) == WINDOW_START


def test_window_start_is_normalized_to_utc(session: Session, device: Device) -> None:
    """The same instant sent with another offset is the same measurement."""
    service = _service(session)
    service.ingest(_packet(seq=1), device)
    service.ingest(
        _packet(
            seq=2,
            window_start=WINDOW_START.astimezone(timezone(timedelta(hours=2))),
        ),
        device,
    )

    assert len(_measurements(session)) == 1


def test_source_packet_id_points_at_the_stored_blob(
    session: Session, device: Device
) -> None:
    service = _service(session)
    service.ingest(_packet(), device)

    row = _measurements(session)[0]
    assert row.source_packet_id is not None
    assert row.received_at is not None
