"""Integration tests for telemetry ingest with device bearer token authentication."""

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.models import Device, Organization, WaterObject
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.security.dependencies import get_token_service
from app.modules.security.services.token import TokenService
from app.modules.telemetry.api import router as telemetry_router


def _seed_device_with_token(
    session: Session, external_id: str, token_service: TokenService
) -> tuple[str, Device]:
    """Seed a Device and return a bearer token + device for testing.

    Creates a DeviceCredential (claimed status), Device, and mints a bearer token.
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

    credential = DeviceCredential(
        serial_number=external_id,
        public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
        status="claimed",
    )
    session.add(credential)
    session.flush()

    device = Device(
        water_object_id=water_object.id,
        external_id=external_id,
        device_credential_id=credential.id,
    )
    session.add(device)
    session.commit()

    # Mint a bearer token
    token_data = {
        "sub": str(device.id),
        "sn": external_id,
        "water_object_id": str(device.water_object_id),
    }
    token, _ = token_service.create_device_token(token_data)

    return token, device


def _payload(seq: int = 1, device_id: str = "gw-2026-0001") -> dict:
    return {
        "v": 2,
        "device_id": device_id,
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


def _client(db_session: Session, token_service: TokenService) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(telemetry_router)

    def override_get_db() -> Generator[Session]:
        yield db_session

    def override_get_token_service() -> TokenService:
        return token_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_token_service] = override_get_token_service

    return TestClient(app)


def test_ingest_accepts_then_returns_duplicate(db_session: Session) -> None:
    """Accept valid packet, then return 200 duplicate for same (device_id, seq)."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    token, _device = _seed_device_with_token(db_session, "gw-2026-0001", token_service)
    headers = {"Authorization": f"Bearer {token}"}

    with _client(db_session, token_service) as client:
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


def test_ingest_rejects_missing_bearer_token(db_session: Session) -> None:
    """Reject packet without Authorization header with 401."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    _seed_device_with_token(db_session, "gw-2026-0001", token_service)

    with _client(db_session, token_service) as client:
        response = client.post("/telemetry/ingest", json=_payload(seq=12))

    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()


def test_ingest_rejects_invalid_bearer_token(db_session: Session) -> None:
    """Reject packet with invalid bearer token with 401."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    _seed_device_with_token(db_session, "gw-2026-0001", token_service)

    with _client(db_session, token_service) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=9),
            headers={"Authorization": "Bearer invalid-token-xyz"},
        )

    assert response.status_code == 401


def test_ingest_rejects_inactive_device(db_session: Session) -> None:
    """Reject packet from inactive device with 401."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    token, device = _seed_device_with_token(db_session, "gw-2026-0001", token_service)

    # Deactivate the device
    device.is_active = False
    db_session.commit()

    with _client(db_session, token_service) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()


def test_ingest_accepts_valid_bearer_token(db_session: Session) -> None:
    """Accept packet from authenticated device with valid bearer token."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    token, _device = _seed_device_with_token(db_session, "gw-2026-0001", token_service)

    with _client(db_session, token_service) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10),
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_ingest_rejects_device_id_mismatch(db_session: Session) -> None:
    """Reject packet where packet.device_id doesn't match auth device."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    # Seed device A
    token, _ = _seed_device_with_token(db_session, "gw-2026-0001", token_service)

    # Send packet as device B
    with _client(db_session, token_service) as client:
        response = client.post(
            "/telemetry/ingest",
            json=_payload(seq=10, device_id="gw-2026-0002"),  # Mismatch!
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    assert "mismatch" in response.json()["detail"].lower()


def test_ingest_accepts_temperature_measurement(db_session: Session) -> None:
    """Accept valid temperature measurement from PT100 sensor."""
    from app.modules.security.services.token import TokenService

    token_service = TokenService(
        secret_key="test-secret",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        device_token_expire_hours=36,
    )

    token, _device = _seed_device_with_token(db_session, "gw-2026-0001", token_service)
    headers = {"Authorization": f"Bearer {token}"}

    # Payload with temperature data
    temp_payload = {
        "v": 2,
        "device_id": "gw-2026-0001",
        "seq": 1001,
        "sent_at": "2026-08-24T12:00:00Z",
        "windows": [
            {
                "window_start": "2026-08-24T12:00:00Z",
                "window_seconds": 30,
                "points": [
                    {
                        "point_id": "pt100_temperature",
                        "type": "temperature",
                        "unit": "°C",
                        "quality": "good",
                        "avg": 22.45,
                        "min": -10,
                        "max": 100,
                    }
                ],
            }
        ],
    }

    with _client(db_session, token_service) as client:
        response = client.post("/telemetry/ingest", json=temp_payload, headers=headers)

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
    assert response.json()["device_id"] == "gw-2026-0001"
    assert response.json()["seq"] == 1001
