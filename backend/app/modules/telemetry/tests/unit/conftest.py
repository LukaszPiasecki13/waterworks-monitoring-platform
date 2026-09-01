"""In-memory database fixtures for the telemetry normalization tests.

These tests exercise the real ingest → `measurements` → query path against a
SQLite database created from the ORM metadata, so they run without the
PostgreSQL instance the integration suite needs. Only the tables this path
touches are created; the PostgreSQL-only `PARTITION BY` clause on
`measurements` is a dialect keyword and is simply ignored here.
"""

from collections.abc import Generator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.sql.base import Base
from app.infrastructure.sql.factory import AuditAwareSession
from app.modules.core_data.models import (
    Device,
    MeasurementPoint,
    Organization,
    WaterObject,
)
from app.modules.core_data.registry import SensorRegistry
from app.modules.telemetry.models import Measurement, TelemetryError, TelemetryPacket

DEVICE_EXTERNAL_ID = "gw-test-0001"

_TABLES = [
    Organization.__table__,
    WaterObject.__table__,
    Device.__table__,
    MeasurementPoint.__table__,
    TelemetryPacket.__table__,
    TelemetryError.__table__,
    Measurement.__table__,
]


@pytest.fixture(scope="session", autouse=True)
def sensor_registry() -> None:
    """Ingest validates point types against the shared registry."""
    SensorRegistry.initialize()


def _open_session(session_class: type[Session]) -> Generator[Session]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=_TABLES)
    factory = sessionmaker(bind=engine, expire_on_commit=False, class_=session_class)
    db = factory()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def session() -> Generator[Session]:
    yield from _open_session(Session)


@pytest.fixture
def audited_session() -> Generator[AuditAwareSession]:
    """Session with the production commit guard, as the backfill script sees it."""
    yield from _open_session(AuditAwareSession)


@pytest.fixture
def device(session: Session) -> Device:
    organization = Organization(id=uuid4(), name="org-test")
    session.add(organization)
    session.flush()

    water_object = WaterObject(
        id=uuid4(),
        organization_id=organization.id,
        name="object-test",
        object_type="pump_station",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(water_object)
    session.flush()

    entity = Device(
        id=uuid4(),
        water_object_id=water_object.id,
        external_id=DEVICE_EXTERNAL_ID,
        # device_credentials is not part of this path; SQLite does not enforce
        # the foreign key, so a synthetic id keeps the fixture small.
        device_credential_id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(entity)
    session.commit()
    return entity


@pytest.fixture
def organization_id(session: Session, device: Device) -> UUID:
    water_object = session.get(WaterObject, device.water_object_id)
    return water_object.organization_id
