"""Partition maintenance: the month arithmetic and the DDL it produces.

The execution half needs PostgreSQL, but the part that decides *which*
partitions exist and *what* their bounds are is plain arithmetic — and it is
the part that breaks silently at a year boundary, so it is asserted on here.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from app.modules.telemetry.repositories.partitions import (
    DEFAULT_PARTITION,
    ensure_measurement_partitions,
    partition_statements,
)


def _names(first: datetime, last: datetime) -> list[str]:
    return [name for name, _ in partition_statements(first, last)]


def test_the_default_partition_always_comes_first() -> None:
    """Ingest must have somewhere to put an out-of-range window."""
    names = _names(datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 9, 1, tzinfo=UTC))

    assert names[0] == DEFAULT_PARTITION


def test_one_partition_per_month_of_the_range() -> None:
    names = _names(datetime(2026, 9, 15, tzinfo=UTC), datetime(2026, 11, 2, tzinfo=UTC))

    assert names[1:] == [
        "measurements_2026_09",
        "measurements_2026_10",
        "measurements_2026_11",
    ]


def test_the_range_rolls_over_a_year_boundary() -> None:
    names = _names(datetime(2026, 11, 20, tzinfo=UTC), datetime(2027, 2, 3, tzinfo=UTC))

    assert names[1:] == [
        "measurements_2026_11",
        "measurements_2026_12",
        "measurements_2027_01",
        "measurements_2027_02",
    ]


def test_december_upper_bound_is_the_next_january() -> None:
    """An off-by-one here would leave a gap no partition accepts."""
    statements = dict(
        partition_statements(
            datetime(2026, 12, 1, tzinfo=UTC), datetime(2026, 12, 1, tzinfo=UTC)
        )
    )

    december = statements["measurements_2026_12"]
    assert "FROM ('2026-12-01 00:00:00+0000')" in december
    assert "TO ('2027-01-01 00:00:00+0000')" in december


def test_bounds_of_consecutive_months_meet_exactly() -> None:
    statements = dict(
        partition_statements(
            datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 10, 1, tzinfo=UTC)
        )
    )

    assert "TO ('2026-10-01 00:00:00+0000')" in statements["measurements_2026_09"]
    assert "FROM ('2026-10-01 00:00:00+0000')" in statements["measurements_2026_10"]


def test_every_statement_is_idempotent() -> None:
    """Startup runs this on every boot; it must never fail on the second one."""
    statements = partition_statements(
        datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 12, 1, tzinfo=UTC)
    )

    assert all("CREATE TABLE IF NOT EXISTS" in sql for _, sql in statements)


@pytest.mark.parametrize("months", [1, 12, 24])
def test_a_wider_range_never_skips_a_month(months: int) -> None:
    first = datetime(2026, 9, 1, tzinfo=UTC)
    total = first.year * 12 + (first.month - 1) + months
    last = datetime(total // 12, total % 12 + 1, 1, tzinfo=UTC)

    # +1 for the default partition, +1 because both endpoints are included.
    assert len(_names(first, last)) == months + 2


def test_maintenance_is_a_no_op_outside_postgresql(session: Session) -> None:
    """SQLite has no partitions; the tests above run against it regardless."""
    assert ensure_measurement_partitions(session) == []
