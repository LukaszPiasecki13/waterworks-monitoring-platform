"""Time-range partition maintenance for the `measurements` table.

`measurements` is created as `PARTITION BY RANGE (window_start)` by the
Alembic migration, but PostgreSQL will not invent the partitions themselves:
without one covering a row's `window_start`, the insert fails. Alembic only
ever creates the schema of the *current* revision, so the rolling set of
monthly partitions is maintained here instead — from application startup, the
backfill script, and the `ensure-measurement-partitions` CLI command.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MEASUREMENTS_TABLE = "measurements"
DEFAULT_PARTITION = "measurements_default"

# One year of partitions ahead of "now" is created on every startup, so a
# deployment that is never restarted still has somewhere to put its rows long
# before the default partition is reached.
MONTHS_AHEAD = 12
MONTHS_BACK = 1


def _month_floor(moment: datetime) -> datetime:
    return datetime(moment.year, moment.month, 1, tzinfo=UTC)


def _next_month(moment: datetime) -> datetime:
    if moment.month == 12:
        return datetime(moment.year + 1, 1, 1, tzinfo=UTC)
    return datetime(moment.year, moment.month + 1, 1, tzinfo=UTC)


def _shift_months(moment: datetime, months: int) -> datetime:
    total = moment.year * 12 + (moment.month - 1) + months
    return datetime(total // 12, total % 12 + 1, 1, tzinfo=UTC)


def _is_partitioned(session: Session) -> bool:
    relkind = session.execute(
        text("SELECT relkind FROM pg_class WHERE oid = to_regclass(:name)"),
        {"name": MEASUREMENTS_TABLE},
    ).scalar()
    return relkind == "p"


def _create(session: Session, statement: str, partition: str) -> bool:
    """Run one CREATE TABLE ... PARTITION OF inside its own savepoint.

    A partition that cannot be created (most plausibly because rows for its
    range already sit in the default partition) must not poison the caller's
    transaction, so each statement gets its own savepoint and its failure is
    reported rather than raised.
    """
    try:
        with session.begin_nested():
            session.execute(text(statement))
    except DatabaseError as exc:
        logger.warning("Could not create partition %s: %s", partition, exc)
        return False
    return True


def ensure_measurement_partitions(
    session: Session,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    months_back: int = MONTHS_BACK,
    months_ahead: int = MONTHS_AHEAD,
) -> list[str]:
    """Create the monthly partitions covering [start, end] plus the default one.

    Idempotent: every statement is `IF NOT EXISTS`, so calling this on every
    startup (or before every backfill batch) costs one catalog lookup per
    partition. Returns the names of the partitions that were created or
    already present. A no-op on non-PostgreSQL databases and on a
    `measurements` table that is not partitioned.
    """
    if session.get_bind().dialect.name != "postgresql":
        return []

    if not _is_partitioned(session):
        logger.warning(
            "Table %s is not partitioned — skipping partition maintenance",
            MEASUREMENTS_TABLE,
        )
        return []

    now = datetime.now(UTC)
    first = _month_floor(start or _shift_months(now, -months_back))
    last = _month_floor(end or _shift_months(now, months_ahead))

    ensured: list[str] = []

    # The default partition keeps ingest working even if this maintenance
    # never runs again; without it an out-of-range window_start is a 500.
    if _create(
        session,
        f"CREATE TABLE IF NOT EXISTS {DEFAULT_PARTITION} "
        f"PARTITION OF {MEASUREMENTS_TABLE} DEFAULT",
        DEFAULT_PARTITION,
    ):
        ensured.append(DEFAULT_PARTITION)

    month = first
    while month <= last:
        upper = _next_month(month)
        partition = f"{MEASUREMENTS_TABLE}_{month:%Y_%m}"
        # Bounds are formatted from datetimes computed here, never from
        # request data — PostgreSQL does not accept bind parameters in DDL.
        created = _create(
            session,
            f"CREATE TABLE IF NOT EXISTS {partition} "
            f"PARTITION OF {MEASUREMENTS_TABLE} FOR VALUES "
            f"FROM ('{month:%Y-%m-%d %H:%M:%S%z}') "
            f"TO ('{upper:%Y-%m-%d %H:%M:%S%z}')",
            partition,
        )
        if created:
            ensured.append(partition)
        month = upper

    return ensured
