"""Repository for the normalized `measurements` table."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, Select, func, insert, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models import Device, MeasurementPoint, WaterObject
from app.modules.telemetry.models.measurement import Measurement

# The natural key of a measurement; also the conflict target that makes a
# re-sent packet a no-op instead of a duplicate row.
CONFLICT_COLUMNS = ("measurement_point_id", "window_start")

COLUMN_COUNT = len(Measurement.__table__.columns)

# Used when a dialect does not advertise its own limit.
FALLBACK_MAX_BIND_PARAMS = 32700


def insert_chunk_rows(dialect: Dialect) -> int:
    """How many rows fit in one multi-row INSERT on this database.

    A statement sends one bind parameter per column per row, and every backend
    caps them (PostgreSQL at 65535 wire-protocol parameters, SQLite at its
    SQLITE_MAX_VARIABLE_NUMBER). One backfill batch — 500 packets x 4 windows x
    3 sensors is 6000 rows — goes over that, so rows are chunked in the
    repository rather than at every call site. Both the limit and the column
    count are read at runtime, so neither a different backend nor a new column
    can silently push a batch over the edge.
    """
    limit = getattr(
        dialect, "insertmanyvalues_max_parameters", FALLBACK_MAX_BIND_PARAMS
    )
    return max(1, limit // COLUMN_COUNT)


_MEASUREMENT_FIELDS = (
    "window_start",
    "window_seconds",
    "avg",
    "min",
    "max",
    "value",
    "value_bool",
    "quality",
)


def _point_columns() -> tuple[Any, ...]:
    return (
        MeasurementPoint.id.label("point_uuid"),
        MeasurementPoint.external_id.label("point_id"),
        MeasurementPoint.point_type.label("point_type"),
        MeasurementPoint.unit.label("unit"),
        Device.external_id.label("device_id"),
    )


class MeasurementRepository(SQLRepository):
    """Write and read access to normalized measurements.

    Reads join `measurement_points → devices → water_objects` for organization
    scoping; the packet blob is never touched on this path.
    """

    def __init__(self, session: Session):
        super().__init__(session)

    def insert_ignoring_duplicates(self, rows: list[dict]) -> int:
        """Insert measurement rows, skipping ones already stored.

        Idempotency is per `(measurement_point_id, window_start)` and therefore
        independent of the packet-level `(device_id, seq)` dedupe: a gateway
        that re-sends the same window under a new sequence number still
        produces exactly one row per window.

        Returns the number of rows actually inserted.
        """
        if not rows:
            return 0

        # Two windows of one packet can carry the same window_start only if the
        # device is misbehaving; collapsing them here (last one wins) keeps the
        # statement itself free of self-conflicts.
        deduplicated = {
            (row["measurement_point_id"], row["window_start"]): row for row in rows
        }
        values = list(deduplicated.values())

        chunk_rows = insert_chunk_rows(self.session.get_bind().dialect)

        inserted = 0
        for start in range(0, len(values), chunk_rows):
            chunk = values[start : start + chunk_rows]
            result = self.session.execute(self._insert_statement(chunk))
            inserted += result.rowcount
        return inserted

    def _insert_statement(self, values: list[dict]):
        """Build the conflict-skipping INSERT for the session's dialect.

        Both PostgreSQL and SQLite spell it `ON CONFLICT DO NOTHING`; any other
        backend gets a plain INSERT and will raise on a duplicate rather than
        silently losing the idempotency guarantee.
        """
        dialect = self.session.get_bind().dialect.name
        if dialect == "postgresql":
            stmt = postgresql_insert(Measurement).values(values)
            return stmt.on_conflict_do_nothing(index_elements=CONFLICT_COLUMNS)
        if dialect == "sqlite":
            stmt = sqlite_insert(Measurement).values(values)
            return stmt.on_conflict_do_nothing(index_elements=CONFLICT_COLUMNS)
        return insert(Measurement).values(values)

    def _object_scoped(self, stmt: Select, object_id: UUID) -> Select:
        return (
            stmt.join(
                MeasurementPoint,
                Measurement.measurement_point_id == MeasurementPoint.id,
            )
            .join(Device, MeasurementPoint.device_id == Device.id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .where(WaterObject.id == object_id)
        )

    def latest_for_objects(self, object_ids: list[UUID]) -> list[Row]:
        """Latest measurement of every active point of the given objects.

        Both halves ride the primary key `(measurement_point_id,
        window_start)`: the correlated subquery reads one point's newest
        window as an index max, and the join then hits that exact row. No
        ranking over the point's whole history, and no window function over
        rows that get thrown away — which is what made the JSONB version of
        this query scale with the number of packets stored.
        """
        if not object_ids:
            return []

        newest_window = (
            select(func.max(Measurement.window_start))
            .where(Measurement.measurement_point_id == MeasurementPoint.id)
            .correlate(MeasurementPoint)
            .scalar_subquery()
        )

        stmt = (
            select(
                WaterObject.id.label("object_id"),
                *_point_columns(),
                *(getattr(Measurement, field) for field in _MEASUREMENT_FIELDS),
            )
            .select_from(MeasurementPoint)
            .join(Device, MeasurementPoint.device_id == Device.id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .join(Measurement, Measurement.measurement_point_id == MeasurementPoint.id)
            .where(
                WaterObject.id.in_(object_ids),
                MeasurementPoint.is_active.is_(True),
                Measurement.window_start == newest_window,
            )
            .order_by(WaterObject.id, MeasurementPoint.external_id)
        )
        return list(self.session.execute(stmt).fetchall())

    def series_for_object(
        self,
        object_id: UUID,
        start: datetime,
        end: datetime,
        *,
        point_id: str | None = None,
        point_type: str | None = None,
        limit: int,
    ) -> list[Row]:
        """Measurements of one object in a time window, oldest first.

        `limit + 1` rows are fetched so the caller can tell a complete series
        from one cut short without a second count query.
        """
        stmt = select(
            *_point_columns(),
            *(getattr(Measurement, field) for field in _MEASUREMENT_FIELDS),
        ).select_from(Measurement)
        stmt = self._object_scoped(stmt, object_id).where(
            Measurement.window_start >= start,
            Measurement.window_start <= end,
        )

        if point_id is not None:
            stmt = stmt.where(MeasurementPoint.external_id == point_id)
        if point_type is not None:
            stmt = stmt.where(MeasurementPoint.point_type == point_type)

        stmt = stmt.order_by(
            Measurement.window_start.asc(), MeasurementPoint.external_id.asc()
        ).limit(limit + 1)

        return list(self.session.execute(stmt).fetchall())

    def series_for_point(
        self,
        point_id: UUID,
        start: datetime,
        end: datetime,
        *,
        limit: int,
    ) -> list[Row]:
        """Measurements of one measurement point, oldest first (`limit + 1`)."""
        stmt = (
            select(*(getattr(Measurement, field) for field in _MEASUREMENT_FIELDS))
            .where(
                Measurement.measurement_point_id == point_id,
                Measurement.window_start >= start,
                Measurement.window_start <= end,
            )
            .order_by(Measurement.window_start.asc())
            .limit(limit + 1)
        )
        return list(self.session.execute(stmt).fetchall())

    def latest_window_start_for_object(self, object_id: UUID) -> datetime | None:
        """Newest `window_start` reported by an object, or None."""
        stmt = select(func.max(Measurement.window_start)).select_from(Measurement)
        return self.session.execute(self._object_scoped(stmt, object_id)).scalar()

    def latest_window_start_for_point(self, point_id: UUID) -> datetime | None:
        """Newest `window_start` of one measurement point, or None."""
        stmt = select(func.max(Measurement.window_start)).where(
            Measurement.measurement_point_id == point_id
        )
        return self.session.execute(stmt).scalar()

    def available_point_ids(self, object_id: UUID) -> list[str]:
        """External ids of the active points of an object that hold data.

        Driven by the point registry rather than by a scan of recent packets —
        but a point with no measurement at all is left out, because the list
        answers "what can this object be charted on". A point an operator
        created by hand and no device ever reported would otherwise offer an
        empty series. The EXISTS is one index probe per point, against the
        primary key.
        """
        has_data = (
            select(Measurement.window_start)
            .where(Measurement.measurement_point_id == MeasurementPoint.id)
            .correlate(MeasurementPoint)
            .exists()
        )
        stmt = (
            select(MeasurementPoint.external_id)
            .select_from(MeasurementPoint)
            .join(Device, MeasurementPoint.device_id == Device.id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .where(
                WaterObject.id == object_id,
                MeasurementPoint.is_active.is_(True),
                has_data,
            )
            .distinct()
            .order_by(MeasurementPoint.external_id)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_point_in_organization(
        self, point_id: UUID, organization_id: UUID
    ) -> MeasurementPoint | None:
        """Load a measurement point, hiding points outside the organization."""
        stmt = (
            select(MeasurementPoint)
            .join(Device, MeasurementPoint.device_id == Device.id)
            .join(WaterObject, Device.water_object_id == WaterObject.id)
            .where(
                MeasurementPoint.id == point_id,
                WaterObject.organization_id == organization_id,
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()
