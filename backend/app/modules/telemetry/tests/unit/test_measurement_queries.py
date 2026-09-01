"""Read paths after normalization — no packet blob is parsed anywhere here."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import NotFoundError
from app.modules.core_data.models import Device, MeasurementPoint
from app.modules.telemetry.models import Measurement
from app.modules.telemetry.repositories.measurements import MeasurementRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    GetPointMeasurementsRequest,
)
from app.modules.telemetry.services.query import TelemetryQueryService

WINDOW_START = datetime(2026, 8, 26, 10, 30, tzinfo=UTC)


def _settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        secret_key="test-secret-key-at-least-32-chars-long!",
    )


def _query_service(session: Session) -> TelemetryQueryService:
    return TelemetryQueryService(
        repository=TelemetryQueryRepository(session),
        measurements=MeasurementRepository(session),
        settings=_settings(),
    )


def _point(session: Session, device: Device, external_id: str, **kwargs) -> UUID:
    point = MeasurementPoint(
        id=uuid4(),
        device_id=device.id,
        external_id=external_id,
        point_type=kwargs.get("point_type", "pressure"),
        unit=kwargs.get("unit", "bar"),
        is_active=kwargs.get("is_active", True),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(point)
    session.flush()
    return point.id


def _measurement(
    session: Session,
    point_id: UUID,
    *,
    offset_seconds: int,
    value: float | None = None,
    quality: str = "good",
) -> None:
    session.add(
        Measurement(
            measurement_point_id=point_id,
            window_start=WINDOW_START + timedelta(seconds=offset_seconds),
            window_seconds=15,
            value=value,
            quality=quality,
            received_at=WINDOW_START + timedelta(seconds=offset_seconds),
            source_packet_id=uuid4(),
        )
    )
    session.flush()


def test_latest_for_objects_returns_the_newest_window_per_point(
    session: Session, device: Device
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    temperature = _point(session, device, "pt100", point_type="temperature", unit="°C")
    _measurement(session, pressure, offset_seconds=0, value=3.40)
    _measurement(session, pressure, offset_seconds=15, value=3.44)
    _measurement(session, temperature, offset_seconds=0, value=23.5)

    rows = MeasurementRepository(session).latest_for_objects([device.water_object_id])

    values = {row.point_id: row.value for row in rows}
    assert values == {
        "pressure-inlet": pytest.approx(3.44),
        "pt100": pytest.approx(23.5),
    }


def test_latest_for_objects_ignores_deactivated_points(
    session: Session, device: Device
) -> None:
    retired = _point(session, device, "old-sensor", is_active=False)
    _measurement(session, retired, offset_seconds=0, value=1.0)

    rows = MeasurementRepository(session).latest_for_objects([device.water_object_id])

    assert rows == []


def test_series_for_object_filters_by_point_and_range(
    session: Session, device: Device
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    temperature = _point(session, device, "pt100", point_type="temperature", unit="°C")
    _measurement(session, pressure, offset_seconds=0, value=3.40)
    _measurement(session, pressure, offset_seconds=15, value=3.44)
    _measurement(session, pressure, offset_seconds=3600, value=3.50)
    _measurement(session, temperature, offset_seconds=0, value=23.5)

    rows = MeasurementRepository(session).series_for_object(
        device.water_object_id,
        WINDOW_START,
        WINDOW_START + timedelta(seconds=60),
        point_id="pressure-inlet",
        limit=100,
    )

    assert [row.value for row in rows] == [pytest.approx(3.40), pytest.approx(3.44)]


def test_get_measurements_reads_the_normalized_table(
    session: Session, device: Device, organization_id: UUID
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    _measurement(session, pressure, offset_seconds=0, value=3.40)
    _measurement(session, pressure, offset_seconds=15, value=3.44, quality="suspect")
    session.commit()

    response = _query_service(session).get_measurements(
        organization_id,
        device.water_object_id,
        GetMeasurementsRequest(),
    )

    assert response.count == 2
    assert response.truncated is False
    assert [item.quality for item in response.items] == ["good", "suspect"]
    assert response.items[0].measured_at.replace(tzinfo=UTC) == WINDOW_START


def test_get_measurements_flags_a_truncated_series(
    session: Session, device: Device, organization_id: UUID
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    for offset in range(0, 45, 15):
        _measurement(session, pressure, offset_seconds=offset, value=3.4)
    session.commit()

    response = _query_service(session).get_measurements(
        organization_id,
        device.water_object_id,
        GetMeasurementsRequest(limit=2),
    )

    assert response.count == 2
    assert response.truncated is True


def test_get_point_measurements_always_reports_window_and_quality(
    session: Session, device: Device, organization_id: UUID
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    _measurement(session, pressure, offset_seconds=0, value=3.40, quality="suspect")
    session.commit()

    response = _query_service(session).get_point_measurements(
        organization_id,
        pressure,
        GetPointMeasurementsRequest(),
    )

    assert response.external_id == "pressure-inlet"
    assert response.unit == "bar"
    assert len(response.items) == 1
    assert response.items[0].quality == "suspect"
    assert response.items[0].window_start.replace(tzinfo=UTC) == WINDOW_START
    assert response.items[0].window_seconds == 15


def test_get_point_measurements_hides_points_of_other_organizations(
    session: Session, device: Device
) -> None:
    pressure = _point(session, device, "pressure-inlet")
    session.commit()

    with pytest.raises(NotFoundError):
        _query_service(session).get_point_measurements(
            uuid4(),
            pressure,
            GetPointMeasurementsRequest(),
        )


def test_available_points_come_from_the_point_registry(
    session: Session, device: Device
) -> None:
    _point(session, device, "pressure-inlet")
    _point(session, device, "pt100", point_type="temperature", unit="°C")
    _point(session, device, "old-sensor", is_active=False)
    session.commit()

    available = MeasurementRepository(session).available_point_ids(
        device.water_object_id
    )

    assert available == ["pressure-inlet", "pt100"]
