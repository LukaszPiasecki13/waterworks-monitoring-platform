"""End-to-end tests for the device state channel (B-08).

Device posts a telemetry packet carrying a `state[]` section, an operator
reads it back through the platform and org-scoped endpoints. Exercises the
real repository SQL — including the "latest per section" ranking and the
cross-organization scoping, neither of which a unit test with a mocked
repository can vouch for.
"""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.core_data.models.users_organizations import UsersOrganizations
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.security.dependencies import get_current_user, get_token_service
from app.modules.security.services.token import TokenService
from app.modules.telemetry.api import (
    device_state_platform_router,
    device_state_router,
)
from app.modules.telemetry.api import router as telemetry_router
from app.modules.telemetry.models.device_state_report import DeviceStateReport
from app.modules.telemetry.repositories.device_state import (
    DeviceStateReportRepository,
)

DEVICE_SN = "WW-STATE-0001"

DEVICE_SECTION_DATA = {
    "serial_number": DEVICE_SN,
    "firmware_version": "0.4.0",
    "registry_schema_version": 2,
    "uptime_seconds": 3600,
    "restart_count": 1,
    "restart_reason": "power_on",
    "rssi_dbm": -71,
    "free_heap_bytes": 184320,
    "min_free_heap_bytes": 151000,
    "buffer_windows_used": 4,
    "buffer_windows_capacity": 48,
    "buffer_windows_dropped": 0,
}


@pytest.fixture
def token_service() -> TokenService:
    return TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )


@pytest.fixture
def seeded_device(db_session: Session) -> Device:
    organization = Organization(name=f"org-{DEVICE_SN}")
    db_session.add(organization)
    db_session.flush()

    water_object = WaterObject(
        organization_id=organization.id,
        name=f"object-{DEVICE_SN}",
        object_type="pump_station",
    )
    db_session.add(water_object)
    db_session.flush()

    credential = DeviceCredential(
        serial_number=DEVICE_SN,
        public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
        status="claimed",
    )
    db_session.add(credential)
    db_session.flush()

    device = Device(
        water_object_id=water_object.id,
        external_id=DEVICE_SN,
        device_credential_id=credential.id,
    )
    db_session.add(device)
    db_session.commit()
    return device


@pytest.fixture
def device_token(seeded_device: Device, token_service: TokenService) -> str:
    token, _ = token_service.create_device_token(
        {
            "sub": str(seeded_device.id),
            "sn": seeded_device.external_id,
            "water_object_id": str(seeded_device.water_object_id),
        }
    )
    return token


@pytest.fixture
def client(
    db_session: Session, token_service: TokenService, admin_user
) -> Generator[TestClient]:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(telemetry_router)
    app.include_router(device_state_platform_router, prefix="/api/v1/platform")
    app.include_router(device_state_router, prefix="/api/v1/orgs/{org_id}/telemetry")

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_token_service] = lambda: token_service
    # Only the identity is stubbed; the platform permission check itself runs
    # for real against the seeded admin group.
    app.dependency_overrides[get_current_user] = lambda: admin_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _packet(seq: int, captured_at: datetime, data: dict | None = None) -> dict:
    window_start = captured_at.isoformat().replace("+00:00", "Z")
    return {
        "v": 2,
        "device_id": DEVICE_SN,
        "seq": seq,
        "sent_at": window_start,
        "windows": [
            {
                "window_start": window_start,
                "window_seconds": 15,
                "points": [
                    {
                        "point_id": "pt100_temperature",
                        "type": "temperature",
                        "unit": "°C",
                        "quality": "good",
                        "value": 21.5,
                    }
                ],
            }
        ],
        "state": [
            {
                "section": "device",
                "schema_version": 1,
                "captured_at": window_start,
                "data": DEVICE_SECTION_DATA if data is None else data,
            }
        ],
    }


def test_state_section_survives_the_round_trip(
    client: TestClient, device_token: str, seeded_device: Device
) -> None:
    captured_at = datetime.now(UTC) - timedelta(seconds=30)

    ingest = client.post(
        "/telemetry/ingest",
        json=_packet(seq=1, captured_at=captured_at),
        headers={"Authorization": f"Bearer {device_token}"},
    )
    assert ingest.status_code == 202, ingest.text

    response = client.get(
        f"/api/v1/platform/telemetry/devices/{seeded_device.id}/state"
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["external_id"] == DEVICE_SN
    assert len(body["sections"]) == 1

    section = body["sections"][0]
    assert section["section"] == "device"
    assert section["schema_version"] == 1
    assert section["data"]["rssi_dbm"] == -71
    assert section["data"]["buffer_windows_capacity"] == 48
    assert section["is_stale"] is False
    assert 0 <= section["age_seconds"] <= 120


def test_read_reports_the_newest_capture_per_section(
    client: TestClient,
    device_token: str,
    seeded_device: Device,
    db_session: Session,
) -> None:
    """A packet retried after an outage must not displace fresher state."""
    headers = {"Authorization": f"Bearer {device_token}"}
    now = datetime.now(UTC)

    fresh = _packet(
        seq=2,
        captured_at=now - timedelta(seconds=20),
        data={**DEVICE_SECTION_DATA, "uptime_seconds": 7200},
    )
    response = client.post("/telemetry/ingest", json=fresh, headers=headers)
    assert response.status_code == 202

    # Arrives later, but was captured earlier — a delayed retransmission.
    stale = _packet(
        seq=3,
        captured_at=now - timedelta(hours=2),
        data={**DEVICE_SECTION_DATA, "uptime_seconds": 60},
    )
    response = client.post("/telemetry/ingest", json=stale, headers=headers)
    assert response.status_code == 202

    assert (
        db_session.query(DeviceStateReport)
        .filter(DeviceStateReport.device_id == DEVICE_SN)
        .count()
        == 2
    )

    body = client.get(
        f"/api/v1/platform/telemetry/devices/{seeded_device.id}/state"
    ).json()

    assert len(body["sections"]) == 1
    assert body["sections"][0]["data"]["uptime_seconds"] == 7200


def test_stale_state_is_reported_as_stale(
    client: TestClient, device_token: str, seeded_device: Device
) -> None:
    captured_at = datetime.now(UTC) - timedelta(hours=1)

    client.post(
        "/telemetry/ingest",
        json=_packet(seq=4, captured_at=captured_at),
        headers={"Authorization": f"Bearer {device_token}"},
    )

    section = client.get(
        f"/api/v1/platform/telemetry/devices/{seeded_device.id}/state"
    ).json()["sections"][0]

    assert section["is_stale"] is True
    assert section["age_seconds"] > 3000


def test_device_without_state_returns_empty_sections(
    client: TestClient, seeded_device: Device
) -> None:
    body = client.get(
        f"/api/v1/platform/telemetry/devices/{seeded_device.id}/state"
    ).json()

    assert body["sections"] == []
    assert body["last_diagnostics_at"] is None


def test_org_scoped_read_hides_a_device_from_another_organization(
    client: TestClient,
    device_token: str,
    seeded_device: Device,
    db_session: Session,
    admin_user,
) -> None:
    """The org path must not become a way to read any device by id."""
    client.post(
        "/telemetry/ingest",
        json=_packet(seq=6, captured_at=datetime.now(UTC)),
        headers={"Authorization": f"Bearer {device_token}"},
    )

    owning_org = (
        db_session.query(WaterObject)
        .filter(WaterObject.id == seeded_device.water_object_id)
        .one()
        .organization_id
    )
    other_org = Organization(name=f"other-{DEVICE_SN}")
    db_session.add(other_org)
    db_session.flush()

    # The caller belongs to both organizations, so the only thing standing
    # between them is the device scoping this endpoint applies.
    db_session.add_all(
        [
            UsersOrganizations(user_id=admin_user.id, organization_id=owning_org),
            UsersOrganizations(user_id=admin_user.id, organization_id=other_org.id),
        ]
    )
    db_session.commit()

    own = client.get(
        f"/api/v1/orgs/{owning_org}/telemetry/devices/{seeded_device.id}/state"
    )
    assert own.status_code == 200
    assert len(own.json()["sections"]) == 1

    foreign = client.get(
        f"/api/v1/orgs/{other_org.id}/telemetry/devices/{seeded_device.id}/state"
    )
    assert foreign.status_code == 404


def test_state_rows_are_removed_with_their_packet(
    client: TestClient,
    device_token: str,
    db_session: Session,
) -> None:
    """Deleting a device's telemetry must not strand its state reports."""
    client.post(
        "/telemetry/ingest",
        json=_packet(seq=5, captured_at=datetime.now(UTC)),
        headers={"Authorization": f"Bearer {device_token}"},
    )
    repo = DeviceStateReportRepository(db_session)
    assert repo.list_latest_sections(DEVICE_SN)

    from app.modules.telemetry.repositories.packets import TelemetryPacketRepository

    TelemetryPacketRepository(db_session).delete_all_for_device(DEVICE_SN)
    db_session.flush()

    assert repo.list_latest_sections(DEVICE_SN) == []
