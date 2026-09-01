"""Service layer for telemetry queries."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Row

from app.core.config import Settings
from app.core.errors import NotFoundError
from app.modules.core_data.models import WaterObject
from app.modules.telemetry.repositories.measurements import MeasurementRepository
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    GetPointMeasurementsRequest,
    LatestPointValue,
    ListObjectsRequest,
    MeasurementSeriesItem,
    MeasurementsResponse,
    ObjectDetailResponse,
    ObjectStatus,
    ObjectSummaryResponse,
    PaginatedResponse,
    PointMeasurementItem,
    PointMeasurementsResponse,
)

DEFAULT_SERIES_HOURS = 24


def _point_value(row: Row) -> float | int | bool | None:
    """The single value a client charts for one measurement.

    A window that only carries aggregates (avg/min/max) still has to render a
    point, so `avg` is the fallback — the same rule the JSONB reader applied
    before normalization.
    """
    if row.value is not None:
        return row.value
    if row.value_bool is not None:
        return row.value_bool
    return row.avg


class TelemetryQueryService:
    """Service for reading and aggregating telemetry data.

    Reads split by what they ask about: packet-level facts (last contact,
    last sequence number) come from `telemetry_packets`, everything about
    measurements themselves comes from the normalized `measurements` table —
    no JSONB blob is parsed on any read path.
    """

    def __init__(
        self,
        repository: TelemetryQueryRepository,
        measurements: MeasurementRepository,
        settings: Settings,
    ):
        self.repo = repository
        self.measurements = measurements
        self.settings = settings

    @staticmethod
    def _latest_point_value(row: Row) -> LatestPointValue:
        return LatestPointValue(
            point_id=row.point_id,
            point_name=row.point_type,
            type=row.point_type,
            unit=row.unit,
            value=_point_value(row),
            quality=row.quality,
            measured_at=row.window_start,
            device_id=row.device_id,
            # A device has no separate name; its external_id is what
            # operators identify it by.
            device_name=row.device_id,
        )

    def _latest_points_by_object(
        self, object_ids: list[UUID]
    ) -> dict[UUID, list[LatestPointValue]]:
        """Latest reading of every point of the given objects, grouped by object."""
        grouped: dict[UUID, list[LatestPointValue]] = defaultdict(list)
        for row in self.measurements.latest_for_objects(object_ids):
            grouped[row.object_id].append(self._latest_point_value(row))
        return grouped

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

    @staticmethod
    def _last_measurement_at(
        points: list[LatestPointValue], last_contact_at: datetime | None
    ) -> datetime | None:
        if not points:
            return last_contact_at
        return max(point.measured_at for point in points)

    def _summarize(self, rows: list[dict]) -> list[ObjectSummaryResponse]:
        """Build summaries for the given object rows.

        The latest reading of every point on the page is fetched in one query
        (one indexed lookup per point), rather than one query per object.
        """
        by_object = self._latest_points_by_object([row["object_id"] for row in rows])

        summaries = []
        for row in rows:
            points = by_object.get(row["object_id"], [])
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
                    last_measurement_at=self._last_measurement_at(
                        points, last_contact_at
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

        # Status derives from measurement quality and contact age, which SQL
        # cannot filter on here. Paginating before the filter would report a
        # total for the unfiltered set and let pages overlap, so the filter is
        # applied to every object first and skip/limit only afterwards.
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

        points = self._latest_points_by_object([object_id]).get(object_id, [])
        last_contact_at = packet.received_at if packet else None

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
            last_measurement_at=self._last_measurement_at(points, last_contact_at),
            points=points,
            last_seq=packet.seq if packet else None,
            available_points=self.measurements.available_point_ids(object_id),
        )

    @staticmethod
    def _series_item(row: Row) -> MeasurementSeriesItem:
        return MeasurementSeriesItem(
            point_id=row.point_id,
            point_name=row.point_type,
            type=row.point_type,
            unit=row.unit,
            measured_at=row.window_start,
            value=_point_value(row),
            avg=row.avg,
            min=row.min,
            max=row.max,
            quality=row.quality,
            device_id=row.device_id,
            device_name=row.device_id,
        )

    @staticmethod
    def _range(
        start: datetime | None, end: datetime | None, latest: datetime | None
    ) -> tuple[datetime, datetime]:
        """Resolve the requested time range, defaulting to the last 24 hours.

        With no end given the range is anchored on the newest measurement, so
        an object that stopped reporting still returns its final day of data
        instead of an empty series. Something that never reported has no
        anchor, and falls back to the last 24 hours of wall-clock time — an
        empty series either way.
        """
        resolved_end = end or latest or datetime.now(UTC)
        resolved_start = start or resolved_end - timedelta(hours=DEFAULT_SERIES_HOURS)
        return resolved_start, resolved_end

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

        start, end = self._range(
            query.start,
            query.end,
            self.measurements.latest_window_start_for_object(object_id),
        )

        rows = self.measurements.series_for_object(
            object_id,
            start,
            end,
            point_id=query.point_id,
            point_type=query.type_,
            limit=query.limit,
        )
        truncated = len(rows) > query.limit
        items = [self._series_item(row) for row in rows[: query.limit]]

        return MeasurementsResponse(
            object_id=str(object_id),
            from_=start,
            to=end,
            count=len(items),
            truncated=truncated,
            items=items,
        )

    def get_point_measurements(
        self,
        organization_id: UUID,
        point_id: UUID,
        query: GetPointMeasurementsRequest,
    ) -> PointMeasurementsResponse:
        """Get the history of a single measurement point.

        Every item carries `window_start` and `quality`: a client charting or
        exporting a series must be able to tell when a value was measured and
        whether the sensor trusted it.
        """
        point = self.measurements.get_point_in_organization(point_id, organization_id)
        if not point:
            raise NotFoundError(f"Measurement point {point_id} not found")

        start, end = self._range(
            query.from_,
            query.to,
            self.measurements.latest_window_start_for_point(point_id),
        )

        rows = self.measurements.series_for_point(
            point_id, start, end, limit=query.limit
        )
        truncated = len(rows) > query.limit
        items = [
            PointMeasurementItem(
                window_start=row.window_start,
                window_seconds=row.window_seconds,
                value=_point_value(row),
                avg=row.avg,
                min=row.min,
                max=row.max,
                quality=row.quality,
            )
            for row in rows[: query.limit]
        ]

        return PointMeasurementsResponse(
            point_id=str(point.id),
            external_id=point.external_id,
            type=point.point_type,
            unit=point.unit,
            from_=start,
            to=end,
            count=len(items),
            truncated=truncated,
            items=items,
        )
