"""Backfill the normalized `measurements` table from telemetry packet blobs.

Reads `telemetry_packets` oldest first, unpacks `payload.windows[].points[]`,
and writes one row per (measurement point, window) into `measurements`.

Designed to be run against a live system:

* **Additive only** — it never modifies or deletes a packet, and the schema
  migration that creates `measurements` blocks nothing, so ingest keeps
  running while this executes.
* **Batched** — one transaction per batch of packets, so it can be stopped
  with Ctrl-C at any point without leaving a half-written transaction.
* **Resumable** — the cursor (last processed `received_at`, packet id) is
  written to a state file after every committed batch.
* **Idempotent** — inserts conflict-skip on `(measurement_point_id,
  window_start)`, so re-running (or overlapping with live ingest) cannot
  create duplicates.

Usage:
    python scripts/backfill_measurements.py [--batch-size 500] [--dry-run]
    python scripts/backfill_measurements.py --restart   # ignore saved cursor
"""

import argparse
import json
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import func, literal, select, tuple_
from sqlalchemy.orm import Session

from app.core.dependencies import create_session
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.repositories.measurements import MeasurementRepository
from app.modules.telemetry.repositories.partitions import (
    ensure_measurement_partitions,
)

DEFAULT_STATE_FILE = ".backfill_measurements_state.json"
DEFAULT_BATCH_SIZE = 500


@dataclass
class Cursor:
    """Position of the backfill in the packet stream."""

    received_at: datetime
    packet_id: UUID

    @classmethod
    def load(cls, path: Path) -> Cursor | None:
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            received_at=datetime.fromisoformat(raw["received_at"]),
            packet_id=UUID(raw["packet_id"]),
        )

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "received_at": self.received_at.isoformat(),
                    "packet_id": str(self.packet_id),
                }
            ),
            encoding="utf-8",
        )


@dataclass
class Report:
    """What the run did, printed at the end and on interruption."""

    packets: int = 0
    candidates: int = 0
    inserted: int = 0
    rejected: Counter = field(default_factory=Counter)
    started_at: float = field(default_factory=time.monotonic)

    @property
    def duplicates(self) -> int:
        """Rows already present — a re-run, or a window live ingest got first."""
        return self.candidates - self.inserted

    def print_summary(self) -> None:
        elapsed = time.monotonic() - self.started_at
        print(f"\nPackets processed : {self.packets}")
        print(f"Rows inserted     : {self.inserted}")
        print(f"Rows already there: {self.duplicates}")
        print(f"Points rejected   : {sum(self.rejected.values())}")
        for reason, count in sorted(self.rejected.items()):
            print(f"  {reason}: {count}")
        print(f"Elapsed           : {elapsed:.1f}s")


def _parse_timestamp(raw: object) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _numeric(raw: object) -> float | None:
    """Coerce an aggregate to float, treating anything else as absent."""
    if isinstance(raw, bool) or not isinstance(raw, int | float):
        return None
    return float(raw)


class PointResolver:
    """Maps `(device external_id, point external_id)` to a measurement point.

    Points are looked up, never created: the backfill migrates history, and
    inventing registry rows for points nobody kept would silently reintroduce
    data an operator deleted on purpose. Devices and points are cached for the
    whole run — both registries are small compared to the packet stream.
    """

    def __init__(self, session: Session):
        self._session = session
        self._devices: dict[str, UUID] = {}
        self._points: dict[tuple[UUID, str], MeasurementPoint] = {}

    def device_id(self, external_id: str) -> UUID | None:
        if external_id not in self._devices:
            found = self._session.execute(
                select(Device.id).where(Device.external_id == external_id)
            ).scalar_one_or_none()
            self._devices[external_id] = found
        return self._devices[external_id]

    def point(self, device_id: UUID, external_id: str) -> MeasurementPoint | None:
        key = (device_id, external_id)
        if key not in self._points:
            self._points[key] = self._session.execute(
                select(MeasurementPoint).where(
                    MeasurementPoint.device_id == device_id,
                    MeasurementPoint.external_id == external_id,
                )
            ).scalar_one_or_none()
        return self._points[key]


def _point_row(
    point: MeasurementPoint,
    window_start: datetime,
    window_seconds: int,
    raw_point: dict,
    packet: TelemetryPacket,
) -> dict:
    value = raw_point.get("value")
    is_flag = isinstance(value, bool)
    return {
        "measurement_point_id": point.id,
        "window_start": window_start,
        "window_seconds": window_seconds,
        "avg": _numeric(raw_point.get("avg")),
        "min": _numeric(raw_point.get("min")),
        "max": _numeric(raw_point.get("max")),
        "value": None if is_flag else _numeric(value),
        "value_bool": value if is_flag else None,
        "quality": str(raw_point.get("quality", "unknown"))[:32],
        "received_at": packet.received_at,
        "source_packet_id": packet.id,
    }


def _rows_for_window(
    window: dict,
    packet: TelemetryPacket,
    device_id: UUID,
    resolver: PointResolver,
    report: Report,
) -> list[dict]:
    window_start = _parse_timestamp(window.get("window_start"))
    window_seconds = window.get("window_seconds")
    # The live path gets these bounds from MeasurementWindow (gt=0, le=3600);
    # here the same values arrive as raw JSON, from packets stored by older
    # firmware and older schema versions, so they are re-checked rather than
    # trusted.
    if (
        window_start is None
        or not isinstance(window_seconds, int)
        or isinstance(window_seconds, bool)
        or not 0 < window_seconds <= 3600
    ):
        report.rejected["malformed_window"] += len(window.get("points") or [])
        return []

    rows = []
    for raw_point in window.get("points") or []:
        external_id = raw_point.get("point_id")
        if not isinstance(external_id, str):
            report.rejected["malformed_point"] += 1
            continue

        point = resolver.point(device_id, external_id)
        if point is None:
            report.rejected["unknown_point"] += 1
            continue

        if point.point_type != raw_point.get("type") or point.unit != raw_point.get(
            "unit"
        ):
            # Same rule as live ingest: a value whose unit contradicts the
            # point on record is not normalized, only kept in the blob.
            report.rejected["point_type_mismatch"] += 1
            continue

        rows.append(_point_row(point, window_start, window_seconds, raw_point, packet))

    return rows


def _rows_for_packet(
    packet: TelemetryPacket, resolver: PointResolver, report: Report
) -> list[dict]:
    payload = packet.payload or {}
    windows = payload.get("windows") or []

    device_id = resolver.device_id(packet.device_id)
    if device_id is None:
        report.rejected["unknown_device"] += sum(
            len(window.get("points") or []) for window in windows
        )
        return []

    rows: list[dict] = []
    for window in windows:
        rows.extend(_rows_for_window(window, packet, device_id, resolver, report))
    return rows


def _fetch_batch(
    session: Session, cursor: Cursor | None, batch_size: int
) -> list[TelemetryPacket]:
    stmt = (
        select(TelemetryPacket)
        .order_by(TelemetryPacket.received_at.asc(), TelemetryPacket.id.asc())
        .limit(batch_size)
    )
    if cursor is not None:
        # Row-value comparison keeps the cursor stable when several packets
        # share a received_at timestamp.
        stmt = stmt.where(
            tuple_(TelemetryPacket.received_at, TelemetryPacket.id)
            > tuple_(
                literal(cursor.received_at, TelemetryPacket.received_at.type),
                literal(cursor.packet_id, TelemetryPacket.id.type),
            )
        )
    return list(session.execute(stmt).scalars().all())


def _print_source_stats(session: Session) -> None:
    """Volume of the source table — context for the run, not a decision input."""
    total, oldest, newest = session.execute(
        select(
            func.count(TelemetryPacket.id),
            func.min(TelemetryPacket.received_at),
            func.max(TelemetryPacket.received_at),
        )
    ).one()
    print(f"Source packets    : {total}")
    print(f"Range             : {oldest} .. {newest}")


def _ensure_partitions_for(
    session: Session, rows: list[dict], ensured_months: set[tuple[int, int]]
) -> None:
    """Create partitions covering this batch, once per month encountered."""
    months = {(row["window_start"].year, row["window_start"].month) for row in rows}
    missing = months - ensured_months
    if not missing:
        return

    starts = [datetime(year, month, 1, tzinfo=UTC) for year, month in missing]
    ensure_measurement_partitions(session, start=min(starts), end=max(starts))
    ensured_months.update(missing)


def run(args: argparse.Namespace) -> Report:
    session = create_session()
    repository = MeasurementRepository(session)
    resolver = PointResolver(session)
    report = Report()
    state_file = Path(args.state_file)
    ensured_months: set[tuple[int, int]] = set()

    cursor = None if args.restart else Cursor.load(state_file)
    if cursor is not None:
        print(f"Resuming after     : {cursor.received_at} / {cursor.packet_id}")

    try:
        _print_source_stats(session)

        while args.limit == 0 or report.packets < args.limit:
            batch_size = args.batch_size
            if args.limit:
                batch_size = min(batch_size, args.limit - report.packets)

            packets = _fetch_batch(session, cursor, batch_size)
            if not packets:
                break

            rows: list[dict] = []
            for packet in packets:
                rows.extend(_rows_for_packet(packet, resolver, report))
            report.packets += len(packets)
            report.candidates += len(rows)

            if rows and not args.dry_run:
                _ensure_partitions_for(session, rows, ensured_months)
                report.inserted += repository.insert_ignoring_duplicates(rows)

            cursor = Cursor(
                received_at=packets[-1].received_at, packet_id=packets[-1].id
            )
            if args.dry_run:
                session.rollback()
            else:
                session.commit(skip_audit=True)
                cursor.save(state_file)

            print(
                f"  ... {report.packets} packets, {report.inserted} rows inserted",
                flush=True,
            )
    except KeyboardInterrupt:
        session.rollback()
        print("\nInterrupted — rerun to resume from the saved cursor.")
    finally:
        session.close()

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Stop after this many packets (0 = all).",
    )
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Ignore the saved cursor and start from the oldest packet.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be written without writing anything.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args()).print_summary()
