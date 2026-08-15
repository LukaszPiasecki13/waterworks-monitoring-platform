from collections.abc import Generator
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.telemetry.api import router as telemetry_router
from app.modules.telemetry.dependencies import verify_telemetry_ingest_key
from app.modules.telemetry.exceptions import TelemetryIngestKeyNotConfiguredError


def _seed_device(session: Session, external_id: str) -> None:
    """Ingest resolves the packet's device_id against a real Device (and its
    WaterObject), so tests that expect a successful ingest must seed one."""
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
    session.add(
        Device(
            water_object_id=water_object.id,
            external_id=external_id,
            hashed_secret="unused",
        )
    )
    session.commit()


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


def test_ingest_accepts_then_returns_duplicate(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TELEMETRY_INGEST_KEY", "test-device-secret")
    get_settings.cache_clear()
    _seed_device(db_session, "gw-2026-0001")

    headers = {"X-Device-Key": "test-device-secret"}
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


def test_ingest_denied_when_no_key_is_configured(monkeypatch) -> None:
    """A missing TELEMETRY_INGEST_KEY closes ingest instead of opening it.

    Asserted against the dependency rather than the endpoint, so the result
    does not depend on whether a local .env happens to define the key.
    """
    monkeypatch.setattr(
        "app.modules.telemetry.dependencies.get_settings",
        lambda: SimpleNamespace(telemetry_ingest_key=None),
    )

    with pytest.raises(TelemetryIngestKeyNotConfiguredError) as exc_info:
        verify_telemetry_ingest_key(x_device_key="any-key")

    assert exc_info.value.status_code == 503


def test_ingest_rejects_missing_device_key(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TELEMETRY_INGEST_KEY", "test-device-secret")
    get_settings.cache_clear()

    with _client(db_session) as client:
        response = client.post("/telemetry/ingest", json=_payload(seq=12))

    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid telemetry ingest key"}


def test_ingest_rejects_invalid_device_key(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TELEMETRY_INGEST_KEY", "test-device-secret")
    get_settings.cache_clear()

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=9),
            headers={"X-Device-Key": "bad-key"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid telemetry ingest key"}


def test_ingest_accepts_valid_device_key(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TELEMETRY_INGEST_KEY", "test-device-secret")
    get_settings.cache_clear()
    _seed_device(db_session, "gw-2026-0001")

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"X-Device-Key": "test-device-secret"},
        )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
