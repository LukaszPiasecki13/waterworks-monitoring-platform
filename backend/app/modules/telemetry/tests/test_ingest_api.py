from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.telemetry.api import router as telemetry_router


def _payload(seq: int = 1) -> dict:
    return {
        "v": 1,
        "device_id": "gw-2026-0001",
        "org_id": "gmina-przyklad",
        "object_id": "przepompownia-01",
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

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_ingest_accepts_then_returns_duplicate(db_session: Session) -> None:
    get_settings.cache_clear()

    with _client(db_session) as client:
        first = client.post("/telemetry/ingest", json=_payload(seq=10542))
        assert first.status_code == 202
        assert first.json() == {
            "status": "accepted",
            "device_id": "gw-2026-0001",
            "seq": 10542,
        }

        second = client.post("/telemetry/ingest", json=_payload(seq=10542))
        assert second.status_code == 200
        assert second.json() == {
            "status": "duplicate",
            "device_id": "gw-2026-0001",
            "seq": 10542,
        }


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

    monkeypatch.delenv("TELEMETRY_INGEST_KEY", raising=False)
    get_settings.cache_clear()


def test_ingest_accepts_valid_device_key(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TELEMETRY_INGEST_KEY", "test-device-secret")
    get_settings.cache_clear()

    with _client(db_session) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"X-Device-Key": "test-device-secret"},
        )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    monkeypatch.delenv("TELEMETRY_INGEST_KEY", raising=False)
    get_settings.cache_clear()
