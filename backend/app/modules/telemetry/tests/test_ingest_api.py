import secrets
from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.security.services.password import hash_password
from app.modules.telemetry.api import router as telemetry_router


def _seed_device(session: Session, external_id: str) -> str:
    """Seed a Device and return the plain-text secret for testing.

    Per-device auth: each Device has its own hashed secret, so tests that
    expect successful ingest must know the plain secret to send in X-Device-Key.
    """
    organization = Organization(name=f"org-{external_id}")
    session.add(organization)
    session.flush()
    water_object = WaterObject(
        organization_id=organization.id,
        name=f"object-{external_id}",
        object_type="pump_station",
    )
    session.add(water_object)
    session.flush()

    # Generate a plain secret and hash it
    plain_secret = secrets.token_urlsafe(32)
    hashed_secret = hash_password(plain_secret)

    session.add(
        Device(
            water_object_id=water_object.id,
            external_id=external_id,
            hashed_secret=hashed_secret,
        )
    )
    session.commit()
    return plain_secret


def _payload(seq: int = 1) -> dict:
    return {
        "v": 1,
        "device_id": "gw-2026-0001",
        "seq": seq,
        "sent_at": "2026-07-27T14:30:00Z",
        "windows": [
            {
                "window_start": "2026-07-27T14:25:00Z",
                "window_seconds": 60,
                "points": [
                    {
                        "point_id": "pressure-inlet",
                        "type": "pressure",
                        "unit": "bar",
                        "quality": "good",
                        "avg": 3.42,
                        "min": 3.38,
                        "max": 3.45,
                    }
                ],
            }
        ],
    }


def _client(db_session: Session) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(telemetry_router)

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_ingest_accepts_then_returns_duplicate(db_session: Session) -> None:
    """Accept valid packet, then return 200 duplicate for same (device_id, seq)."""
    plain_secret = _seed_device(db_session, "gw-2026-0001")
    headers = {"X-Device-Key": plain_secret}

    with _client(db_session) as client:
        first = client.post(
            "/telemetry/ingest", json=_payload(seq=10542), headers=headers
        )
        assert first.status_code == 202
        assert first.json() == {
            "status": "accepted",
            "device_id": "gw-2026-0001",
            "seq": 10542,
        }

        second = client.post(
            "/telemetry/ingest", json=_payload(seq=10542), headers=headers
        )
        assert second.status_code == 200
        assert second.json() == {
            "status": "duplicate",
            "device_id": "gw-2026-0001",
            "seq": 10542,
        }


def test_ingest_rejects_unknown_device(db_session: Session) -> None:
    """Reject packet from unknown device_id with 401."""
    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=12),
            headers={"X-Device-Key": "any-secret"},
        )

    assert response.status_code == 401
    assert "not found" in response.json()["detail"]


def test_ingest_rejects_missing_device_secret(db_session: Session) -> None:
    """Reject packet without X-Device-Key header with 403."""
    _seed_device(db_session, "gw-2026-0001")

    with _client(db_session) as client:
        response = client.post("/telemetry/ingest", json=_payload(seq=12))

    assert response.status_code == 403
    assert "credentials" in response.json()["detail"]


def test_ingest_rejects_invalid_device_secret(db_session: Session) -> None:
    """Reject packet with wrong secret with 403."""
    _seed_device(db_session, "gw-2026-0001")

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=9),
            headers={"X-Device-Key": "wrong-secret"},
        )

    assert response.status_code == 403
    assert "credentials" in response.json()["detail"]


def test_ingest_rejects_inactive_device(db_session: Session) -> None:
    """Reject packet from inactive device with 403."""
    plain_secret = _seed_device(db_session, "gw-2026-0001")

    # Deactivate the device
    device = db_session.query(Device).filter_by(external_id="gw-2026-0001").first()
    assert device
    device.is_active = False
    db_session.commit()

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"X-Device-Key": plain_secret},
        )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"]


def test_ingest_accepts_valid_device_secret(db_session: Session) -> None:
    """Accept packet from authenticated device with valid secret."""
    plain_secret = _seed_device(db_session, "gw-2026-0001")

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"X-Device-Key": plain_secret},
        )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
