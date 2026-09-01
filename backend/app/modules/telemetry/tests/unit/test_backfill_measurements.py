"""The historical backfill: what it migrates, what it rejects, how it resumes."""

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.factory import AuditAwareSession
from app.modules.core_data.models import (
    Device,
    MeasurementPoint,
    Organization,
    WaterObject,
)
from app.modules.telemetry.models import Measurement, TelemetryPacket
from scripts import backfill_measurements

WINDOW_START = datetime(2026, 8, 26, 10, 30, tzinfo=UTC)
DEVICE_EXTERNAL_ID = "gw-backfill-0001"


def _seed_device(session: Session) -> Device:
    organization = Organization(id=uuid4(), name="org-backfill")
    session.add(organization)
    session.flush()

    water_object = WaterObject(
        id=uuid4(),
        organization_id=organization.id,
        name="object-backfill",
        object_type="pump_station",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(water_object)
    session.flush()

    device = Device(
        id=uuid4(),
        water_object_id=water_object.id,
        external_id=DEVICE_EXTERNAL_ID,
        device_credential_id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(device)
    session.flush()
    return device


def _seed_point(session: Session, device: Device, external_id: str) -> MeasurementPoint:
    point = MeasurementPoint(
        id=uuid4(),
        device_id=device.id,
        external_id=external_id,
        point_type="pressure",
        unit="bar",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(point)
    session.flush()
    return point


def _seed_packet(
    session: Session,
    *,
    seq: int,
    points: list[dict],
    window_start: datetime = WINDOW_START,
) -> TelemetryPacket:
    packet = TelemetryPacket(
        id=uuid4(),
        device_id=DEVICE_EXTERNAL_ID,
        seq=seq,
        sent_at=window_start,
        received_at=window_start + timedelta(seconds=30),
        payload={
            "v": 2,
            "device_id": DEVICE_EXTERNAL_ID,
            "seq": seq,
            "sent_at": window_start.isoformat(),
            "windows": [
                {
                    "window_start": window_start.isoformat(),
                    "window_seconds": 15,
                    "points": points,
                }
            ],
        },
    )
    session.add(packet)
    session.flush()
    return packet


def _point_payload(**overrides) -> dict:
    payload = {
        "point_id": "pressure-inlet",
        "type": "pressure",
        "unit": "bar",
        "quality": "good",
        "value": 3.42,
    }
    payload.update(overrides)
    return payload


def _args(tmp_path: Path, **overrides) -> argparse.Namespace:
    values = {
        "batch_size": 2,
        "limit": 0,
        "state_file": str(tmp_path / "state.json"),
        "restart": False,
        "dry_run": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.fixture
def backfill_session(
    audited_session: AuditAwareSession, monkeypatch: pytest.MonkeyPatch
) -> AuditAwareSession:
    """Point the script's session factory at the in-memory database."""
    monkeypatch.setattr(
        backfill_measurements, "create_session", lambda: audited_session
    )
    # The script closes the session it opened; the fixture still needs it for
    # assertions afterwards, so closing is neutralized here.
    monkeypatch.setattr(audited_session, "close", lambda: None)
    return audited_session


def _row_count(session: Session) -> int:
    return session.execute(select(func.count()).select_from(Measurement)).scalar()


def test_backfill_migrates_blob_points_into_measurements(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    _seed_packet(backfill_session, seq=1, points=[_point_payload()])
    _seed_packet(
        backfill_session,
        seq=2,
        points=[_point_payload(value=3.44)],
        window_start=WINDOW_START + timedelta(seconds=15),
    )
    backfill_session.commit(skip_audit=True)

    report = backfill_measurements.run(_args(tmp_path))

    assert report.packets == 2
    assert report.inserted == 2
    assert _row_count(backfill_session) == 2


def test_rerunning_the_backfill_inserts_nothing_new(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    """Idempotent both ways: the cursor skips done work, conflicts catch the rest."""
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    _seed_packet(backfill_session, seq=1, points=[_point_payload()])
    backfill_session.commit(skip_audit=True)

    backfill_measurements.run(_args(tmp_path))
    second = backfill_measurements.run(_args(tmp_path, restart=True))

    assert second.packets == 1
    assert second.inserted == 0
    assert second.duplicates == 1
    assert _row_count(backfill_session) == 1


def test_backfill_resumes_from_the_saved_cursor(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    for seq in range(4):
        _seed_packet(
            backfill_session,
            seq=seq,
            points=[_point_payload()],
            window_start=WINDOW_START + timedelta(seconds=15 * seq),
        )
    backfill_session.commit(skip_audit=True)

    first = backfill_measurements.run(_args(tmp_path, limit=2))
    second = backfill_measurements.run(_args(tmp_path))

    assert first.packets == 2
    assert second.packets == 2
    assert _row_count(backfill_session) == 4


def test_backfill_reports_points_it_cannot_place(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    _seed_packet(
        backfill_session,
        seq=1,
        points=[
            _point_payload(point_id="never-registered"),
            _point_payload(unit="kPa"),
        ],
    )
    backfill_session.commit(skip_audit=True)

    report = backfill_measurements.run(_args(tmp_path))

    assert report.inserted == 0
    assert report.rejected["unknown_point"] == 1
    assert report.rejected["point_type_mismatch"] == 1


@pytest.mark.parametrize("window_seconds", [0, -15, 7200, "15", None])
def test_backfill_rejects_windows_with_an_impossible_length(
    backfill_session: AuditAwareSession, tmp_path: Path, window_seconds: object
) -> None:
    """Blob content is re-validated: only the live path went through pydantic."""
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    packet = _seed_packet(backfill_session, seq=1, points=[_point_payload()])
    payload = dict(packet.payload)
    payload["windows"][0]["window_seconds"] = window_seconds
    packet.payload = payload
    backfill_session.commit(skip_audit=True)

    report = backfill_measurements.run(_args(tmp_path))

    assert report.inserted == 0
    assert report.rejected["malformed_window"] == 1


def test_backfill_stores_bool_values_in_their_own_column(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    device = _seed_device(backfill_session)
    point = _seed_point(backfill_session, device, "pump-running")
    point.point_type = "digital_input"
    point.unit = "bool"
    _seed_packet(
        backfill_session,
        seq=1,
        points=[
            _point_payload(
                point_id="pump-running",
                type="digital_input",
                unit="bool",
                value=False,
            )
        ],
    )
    backfill_session.commit(skip_audit=True)

    backfill_measurements.run(_args(tmp_path))

    row = backfill_session.execute(select(Measurement)).scalar_one()
    assert row.value is None
    assert row.value_bool is False


def test_dry_run_writes_nothing(
    backfill_session: AuditAwareSession, tmp_path: Path
) -> None:
    device = _seed_device(backfill_session)
    _seed_point(backfill_session, device, "pressure-inlet")
    _seed_packet(backfill_session, seq=1, points=[_point_payload()])
    backfill_session.commit(skip_audit=True)

    report = backfill_measurements.run(_args(tmp_path, dry_run=True))

    assert report.candidates == 1
    assert report.inserted == 0
    assert _row_count(backfill_session) == 0
    assert not (tmp_path / "state.json").exists()
