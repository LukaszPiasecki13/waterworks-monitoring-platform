"""Service layer for telemetry queries."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from itertools import islice
from uuid import UUID

from app.core.config import Settings
from app.core.errors import NotFoundError
from app.modules.core_data.models import WaterObject
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    LatestPointValue,
    ListObjectsRequest,
    MeasurementSeriesItem,
    MeasurementsResponse,
    ObjectDetailResponse,
    ObjectStatus,
    ObjectSummaryResponse,
    PaginatedResponse,
)

# Upper bound on packets scanned for one series request, so a wide time range
# cannot pull an unbounded result set into memory.
MAX_PACKETS_PER_SERIES = 5000

# Packets scanned when collecting the point ids an object currently reports.
AVAILABLE_POINTS_LOOKBACK_PACKETS = 100


class TelemetryQueryService:
    """Service for reading and aggregating telemetry data."""

    def __init__(self, repository: TelemetryQueryRepository, settings: Settings):
        self.repo = repository
        self.settings = settings

    @staticmethod
    def _window_timestamp(window: dict, packet: TelemetryPacket) -> datetime:
        """Timestamp of a measurement window, falling back to packet arrival."""
        window_start = window.get("window_start")
        if isinstance(window_start, str):
            try:
                return datetime.fromisoformat(window_start.replace("Z", "+00:00"))
            except ValueError:
                return packet.received_at
        return packet.received_at

    def _unpack_latest_points(self, packet: TelemetryPacket) -> list[LatestPointValue]:
        """Extract the measurement points of a packet's most recent window."""
        if not packet.payload:
            return []

        windows = packet.payload.get("windows", [])
        if not windows:
            return []

        latest_window = max(windows, key=lambda w: w.get("window_start", ""))
        measured_at = self._window_timestamp(latest_window, packet)

        return [
            LatestPointValue(
                point_id=point.get("point_id", "unknown"),
                point_name=point.get("type", "unknown"),
                type=point.get("type", "unknown"),
                unit=point.get("unit", "unknown"),
                value=point.get("value", point.get("avg")),
                quality=point.get("quality", "unknown"),
                measured_at=measured_at,
                device_id=packet.device_id,
                # A device has no separate name; its external_id is what
                # operators identify it by.
                device_name=packet.device_id,
            )
            for point in latest_window.get("points", [])
        ]

    def _compute_status(
        self,
        last_contact_at: datetime | None,
        points: list[LatestPointValue],
    ) -> ObjectStatus:
        """Determine object status from last contact time and point quality.

        - no_data: the object has never reported
        - no_comm: last contact older than the stale threshold
        - warning: some point reports a quality other than "good"
        - ok: everything else
        """
        if last_contact_at is None:
            return "no_data"

        stale_threshold = datetime.now(UTC) - timedelta(
            seconds=self.settings.telemetry_stale_after_seconds
        )
        if last_contact_at < stale_threshold:
            return "no_comm"

        if any(point.quality != "good" for point in points):
            return "warning"

        return "ok"

    def _summarize(self, rows: list[dict]) -> list[ObjectSummaryResponse]:
        """Build summaries for the given object rows.

        Packets are fetched for the whole page by primary key in one query
        (list_objects already identified each object's last_packet_id),
        rather than one query per object.
        """
        packet_ids = [
            row["last_packet_id"] for row in rows if row["last_packet_id"] is not None
        ]
        packets = self.repo.get_packets_by_ids(packet_ids)

        summaries = []
        for row in rows:
            packet = packets.get(row["last_packet_id"])
            points = self._unpack_latest_points(packet) if packet else []
            last_contact_at = row["last_contact_at"]
            summaries.append(
                ObjectSummaryResponse(
                    org_id=str(row["org_id"]),
                    org_name=row["org_name"],
                    object_id=str(row["object_id"]),
                    name=row["name"],
                    device_id=row["last_device_id"],
                    device_name=row["last_device_id"],
                    status=self._compute_status(last_contact_at, points),
                    last_contact_at=last_contact_at,
                    last_measurement_at=(
                        points[0].measured_at if points else last_contact_at
                    ),
                    points=points,
                )
            )
        return summaries

    def list_objects(
        self,
        organization_id: UUID,
        query: ListObjectsRequest,
    ) -> PaginatedResponse[ObjectSummaryResponse]:
        """List objects in organization with their latest readings and status."""
        if query.status is None:
            rows = self.repo.list_objects(
                org_id=organization_id, skip=query.skip, limit=query.limit
            )
            return PaginatedResponse(
                items=self._summarize(rows),
                total=self.repo.count_objects(org_id=organization_id),
                skip=query.skip,
                limit=query.limit,
            )

        # Status derives from packet payload quality, which SQL cannot filter
        # on. Paginating before the filter would report a total for the
        # unfiltered set and let pages overlap, so the filter is applied to
        # every object first and skip/limit only afterwards.
        rows = self.repo.list_objects(org_id=organization_id, skip=0, limit=None)
        matching = [
            summary
            for summary in self._summarize(rows)
            if summary.status == query.status
        ]
        return PaginatedResponse(
            items=matching[query.skip : query.skip + query.limit],
            total=len(matching),
            skip=query.skip,
            limit=query.limit,
        )

    def _resolve_object(self, organization_id: UUID, object_id: UUID) -> WaterObject:
        """Load a water object, hiding objects outside the organization."""
        water_object = self.repo.get_water_object(object_id)
        if not water_object:
            raise NotFoundError(f"Object {object_id} not found")

        if water_object.organization_id != organization_id:
            raise NotFoundError(f"Object {object_id} not found")

        return water_object

    def get_object_detail(
        self, organization_id: UUID, object_id: UUID
    ) -> ObjectDetailResponse:
        """Get the detailed view of a single object.

        An object that has never reported is returned with status "no_data"
        rather than a 404 — it exists, it is simply awaiting its first packet.
        """
        water_object = self._resolve_object(organization_id, object_id)
        packet = self.repo.get_latest_packet(object_id)

        points = self._unpack_latest_points(packet) if packet else []
        last_contact_at = packet.received_at if packet else None

        available_points: set[str] = set()
        if packet:
            recent_packets = self.repo.get_packets_in_range(
                object_id,
                packet.received_at - timedelta(hours=24),
                packet.received_at,
                limit=AVAILABLE_POINTS_LOOKBACK_PACKETS,
            )
            for recent in recent_packets:
                for window in recent.payload.get("windows", []):
                    for point in window.get("points", []):
                        available_points.add(point.get("point_id", "unknown"))

        # organization_id is a non-null foreign key, so the fallback is
        # unreachable outside of corrupted data.
        org_name = self.repo.get_organization_name(water_object.organization_id) or ""

        return ObjectDetailResponse(
            org_id=str(water_object.organization_id),
            org_name=org_name,
            object_id=str(object_id),
            name=water_object.name,
            device_id=packet.device_id if packet else None,
            device_name=packet.device_id if packet else None,
            status=self._compute_status(last_contact_at, points),
            last_contact_at=last_contact_at,
            last_measurement_at=(points[0].measured_at if points else last_contact_at),
            points=points,
            last_seq=packet.seq if packet else None,
            available_points=sorted(available_points),
        )

    def _iter_series_items(
        self,
        packets: list[TelemetryPacket],
        point_id: str | None,
        type_: str | None,
    ) -> Iterator[MeasurementSeriesItem]:
        """Flatten packets into measurement items, lazily.

        Being a generator lets the caller stop at its limit instead of
        materialising every point of every window first.
        """
        for packet in packets:
            for window in packet.payload.get("windows", []):
                measured_at = self._window_timestamp(window, packet)
                for point in window.get("points", []):
                    point_point_id = point.get("point_id", "unknown")
                    point_type = point.get("type", "unknown")

                    if point_id is not None and point_point_id != point_id:
                        continue
                    if type_ is not None and point_type != type_:
                        continue

                    yield MeasurementSeriesItem(
                        point_id=point_point_id,
                        point_name=point_type,
                        type=point_type,
                        unit=point.get("unit", "unknown"),
                        measured_at=measured_at,
                        value=point.get("value"),
                        avg=point.get("avg"),
                        min=point.get("min"),
                        max=point.get("max"),
                        quality=point.get("quality", "unknown"),
                        device_id=packet.device_id,
                        device_name=packet.device_id,
                    )

    def get_measurements(
        self,
        organization_id: UUID,
        object_id: UUID,
        query: GetMeasurementsRequest,
    ) -> MeasurementsResponse:
        """Get the time series of an object, defaulting to the last 24h.

        `truncated` tells the client the series was cut at `limit` mid-range,
        so a chart does not silently render a partial window as complete.
        """
        self._resolve_object(organization_id, object_id)

        end = query.end
        if end is None:
            latest_packet = self.repo.get_latest_packet(object_id)
            end = latest_packet.received_at if latest_packet else datetime.now(UTC)
        start = query.start
        if start is None:
            start = end - timedelta(hours=24)

        packets = self.repo.get_packets_in_range(
            object_id, start, end, limit=MAX_PACKETS_PER_SERIES
        )

        series = self._iter_series_items(packets, query.point_id, query.type_)
        items = list(islice(series, query.limit))
        truncated = next(series, None) is not None

        return MeasurementsResponse(
            object_id=str(object_id),
            from_=start,
            to=end,
            count=len(items),
            truncated=truncated,
            items=items,
        )
