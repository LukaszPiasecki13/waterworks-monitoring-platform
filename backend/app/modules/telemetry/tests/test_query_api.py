"""Tests for telemetry query/read endpoints."""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import NotFoundError, register_error_handlers
from app.modules.core_data.models import User
from app.modules.security.dependencies import get_current_user
from app.modules.telemetry.api.query import router as query_router
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import LatestPointValue
from app.modules.telemetry.services.query import TelemetryQueryService


@pytest.fixture
def telemetry_user(db_session: Session) -> User:
    """Create a test user for telemetry queries."""
    user = User(
        id=100,
        username="telemetry_user",
        email="telemetry@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="not-used",
        status="regular",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def telemetry_client(
    db_session: Session,
    telemetry_user: User,
) -> Generator[TestClient, None, None]:
    """FastAPI test client with telemetry router and mocked auth."""
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(query_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: telemetry_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_packet_data() -> dict:
    """Sample telemetry packet payload."""
    return {
        "v": 1,
        "device_id": "esp32-test-001",
        "org_id": "test-org",
        "object_id": "pump-station-01",
        "seq": 1,
        "sent_at": datetime.now(UTC).isoformat(),
        "windows": [
            {
                "window_start": datetime.now(UTC).isoformat(),
                "window_seconds": 30,
                "points": [
                    {
                        "point_id": "pressure",
                        "type": "pressure",
                        "unit": "bar",
                        "quality": "good",
                        "value": 3.5,
                        "avg": 3.5,
                        "min": 3.2,
                        "max": 3.8,
                    }
                ],
            }
        ],
    }


def test_query_service_unpacks_latest_points(sample_packet_data, db_session: Session):
    """Test that _unpack_latest_points correctly extracts point values."""
    settings = get_settings()
    repo = TelemetryQueryRepository(session=db_session)
    service = TelemetryQueryService(repo, settings)

    packet = TelemetryPacket(
        device_id="esp32-test-001",
        org_id="test-org",
        object_id="pump-station-01",
        seq=1,
        sent_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        payload=sample_packet_data,
    )

    points = service._unpack_latest_points(packet)

    assert len(points) == 1
    assert points[0].point_id == "pressure"
    assert points[0].type == "pressure"
    assert points[0].unit == "bar"
    assert points[0].value == 3.5
    assert points[0].quality == "good"
    assert points[0].device_id == "esp32-test-001"


def test_query_service_compute_status_no_data(db_session: Session):
    """Test status computation for no data."""
    settings = get_settings()
    repo = TelemetryQueryRepository(session=db_session)
    service = TelemetryQueryService(repo, settings)

    status = service._compute_status(None, [])
    assert status == "no_data"


def test_query_service_compute_status_no_comm(db_session: Session):
    """Test status computation for no communication (stale)."""
    settings = get_settings()
    repo = TelemetryQueryRepository(session=db_session)
    service = TelemetryQueryService(repo, settings)

    stale_time = datetime.now(UTC) - timedelta(hours=2)

    status = service._compute_status(stale_time, [])
    assert status == "no_comm"


def test_query_service_compute_status_warning(db_session: Session):
    """Test status computation when quality is not 'good'."""
    settings = get_settings()
    repo = TelemetryQueryRepository(session=db_session)
    service = TelemetryQueryService(repo, settings)

    points = [
        LatestPointValue(
            point_id="pressure",
            type="pressure",
            unit="bar",
            value=2.1,
            quality="sensor_error",
            measured_at=datetime.now(UTC),
            device_id="esp32-test-002",
        )
    ]

    status = service._compute_status(datetime.now(UTC), points)
    assert status == "warning"


def test_query_service_compute_status_ok(db_session: Session):
    """Test status computation for healthy object."""
    settings = get_settings()
    repo = TelemetryQueryRepository(session=db_session)
    service = TelemetryQueryService(repo, settings)

    points = [
        LatestPointValue(
            point_id="pressure",
            type="pressure",
            unit="bar",
            value=3.5,
            quality="good",
            measured_at=datetime.now(UTC),
            device_id="esp32-test-001",
        )
    ]

    status = service._compute_status(datetime.now(UTC), points)
    assert status == "ok"


def test_query_service_get_measurements_not_found(db_session: Session):
    """Test that get_measurements raises NotFoundError for unknown object."""
    settings = get_settings()
    repo = TelemetryQueryRepository(db_session)
    service = TelemetryQueryService(repo, settings)

    with pytest.raises(NotFoundError):
        service.get_measurements(object_id="unknown-object")


def test_api_list_objects_requires_auth(db_session: Session):
    """Test that list_objects endpoint requires authentication."""
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(query_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    response = client.get("/api/v1/telemetry/objects")
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_api_list_objects_empty(telemetry_client: TestClient):
    """Test list_objects returns empty list when no data."""
    response = telemetry_client.get("/api/v1/telemetry/objects")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["skip"] == 0
    assert data["limit"] == 50


def test_api_get_object_detail_not_found(telemetry_client: TestClient):
    """Test get_object_detail returns 404 for unknown object."""
    response = telemetry_client.get("/api/v1/telemetry/objects/unknown-object")
    assert response.status_code == 404
