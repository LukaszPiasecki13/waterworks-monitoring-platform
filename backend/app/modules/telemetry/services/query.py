"""Service layer for telemetry queries."""

from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.core.errors import NotFoundError
from app.modules.core_data.models import User
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import (
    LatestPointValue,
    MeasurementSeriesItem,
    MeasurementsResponse,
    ObjectDetail,
    ObjectStatus,
    ObjectSummary,
    PaginatedResponse,
)


class TelemetryQueryService:
    """Service for reading and aggregating telemetry data."""

    def __init__(self, repository: TelemetryQueryRepository, settings: Settings):
        self.repo = repository
        self.settings = settings

    def _unpack_latest_points(self, packet) -> list[LatestPointValue]:
        """Extract measurement points from the latest window in a packet.

        Returns a list of LatestPointValue for each point in the latest window.
        If no windows exist, returns empty list.
        """
        if not packet.payload or "windows" not in packet.payload:
            return []

        windows = packet.payload.get("windows", [])
        if not windows:
            return []

        latest_window = max(windows, key=lambda w: w.get("window_start", ""))
        points = latest_window.get("points", [])

        measured_at = latest_window.get("window_start")
        if isinstance(measured_at, str):
            try:
                measured_at = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                measured_at = packet.received_at
        else:
            measured_at = packet.received_at

        device_name = self.repo.get_device_name(packet.device_id)

        result = []
        for point in points:
            value = point.get("value")
            if value is None:
                value = point.get("avg")

            point_id = point.get("point_id", "unknown")
            point_type = point.get("type", "unknown")

            result.append(
                LatestPointValue(
                    point_id=point_id,
                    point_name=point_type,
                    type=point_type,
                    unit=point.get("unit", "unknown"),
                    value=value,
                    quality=point.get("quality", "unknown"),
                    measured_at=measured_at,
                    device_id=packet.device_id,
                    device_name=device_name,
                )
            )

        return result

    def _compute_status(
        self,
        last_contact_at: datetime | None,
        points: list[LatestPointValue],
    ) -> ObjectStatus:
        """Determine object status based on last contact time and point quality.

        Status logic:
        - no_data: no packets received ever
        - no_comm: last contact older than stale_after threshold
        - warning: any point has quality != "good"
        - ok: everything else
        """
        if last_contact_at is None:
            return "no_data"

        now = datetime.now(UTC)
        stale_threshold = now - timedelta(
            seconds=self.settings.telemetry_stale_after_seconds
        )

        if last_contact_at < stale_threshold:
            return "no_comm"

        if any(p.quality != "good" for p in points):
            return "warning"

        return "ok"

    def list_objects(
        self,
        user: User,
        org_id: str | None = None,
        status: ObjectStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse[ObjectSummary]:
        """List all objects with their latest readings and status.

        Regular users: forced to their organization, org_id param ignored.
        Platform admins: can filter by any org_id or see all if org_id=None.
        Applies optional status filter (in-memory).
        """
        if user.organization_id is not None:
            org_id = str(user.organization_id)

        candidates_limit = 500 if status else limit

        total = self.repo.count_objects(org_id=org_id)
        object_rows = self.repo.list_object_ids(
            org_id=org_id, skip=skip, limit=candidates_limit
        )

        summaries = []
        for row in object_rows:
            packet = self.repo.get_latest_packet(row["object_id"])
            points = self._unpack_latest_points(packet) if packet else []
            obj_status = self._compute_status(row["last_contact_at"], points)

            if status is not None and obj_status != status:
                continue

            summary = ObjectSummary(
                org_id=row["org_id"],
                org_name=row["org_name"],
                object_id=row["object_id"],
                name=row["name"],
                device_id=row["last_device_id"],
                device_name=row["device_name"],
                status=obj_status,
                last_contact_at=row["last_contact_at"],
                last_measurement_at=points[0].measured_at
                if points
                else row["last_contact_at"],
                points=points,
            )
            summaries.append(summary)

        if status is not None:
            summaries = summaries[:limit]

        return PaginatedResponse(
            items=summaries,
            total=total,
            skip=skip,
            limit=limit,
        )

    def get_object_detail(self, user: User, object_id: str) -> ObjectDetail:
        """Get detailed view of a single object.

        Regular users: can only see objects in their organization.
        Platform admins: can see any object.
        """
        water_object = self.repo.get_water_object(object_id)
        if not water_object:
            raise NotFoundError(f"Object {object_id} not found")

        if (
            user.organization_id is not None
            and water_object.organization_id != user.organization_id
        ):
            raise NotFoundError(f"Object {object_id} not found")

        packet = self.repo.get_latest_packet(object_id)
        if not packet:
            raise NotFoundError(f"Object {object_id} not found")

        points = self._unpack_latest_points(packet)
        obj_status = self._compute_status(packet.received_at, points)

        available_points_set = set()
        start_24h = packet.received_at - timedelta(hours=24)
        recent_packets = self.repo.get_packets_in_range(
            object_id, start_24h, packet.received_at, limit=100
        )
        for p in recent_packets:
            windows = p.payload.get("windows", [])
            for window in windows:
                for point in window.get("points", []):
                    available_points_set.add(point.get("point_id", "unknown"))

        org_name = self.repo.get_organization_name(str(water_object.organization_id))
        device_name = self.repo.get_device_name(packet.device_id)

        return ObjectDetail(
            org_id=str(water_object.organization_id),
            org_name=org_name,
            object_id=object_id,
            name=water_object.name,
            device_id=packet.device_id,
            device_name=device_name,
            status=obj_status,
            last_contact_at=packet.received_at,
            last_measurement_at=points[0].measured_at if points else packet.received_at,
            points=points,
            last_seq=packet.seq,
            available_points=sorted(list(available_points_set)),
        )

    def get_measurements(
        self,
        user: User,
        object_id: str,
        point_id: str | None = None,
        type_: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000,
    ) -> MeasurementsResponse:
        """Get time series measurements for an object.

        Regular users: can only see measurements from objects in their organization.
        Platform admins: can see any object's measurements.
        Defaults start/end to last 24h if not provided.
        Flattens all windows/points from packets in range.
        Optionally filters by point_id and/or type.
        """
        limit = min(limit, 5000)

        water_object = self.repo.get_water_object(object_id)
        if not water_object:
            raise NotFoundError(f"Object {object_id} not found")

        if (
            user.organization_id is not None
            and water_object.organization_id != user.organization_id
        ):
            raise NotFoundError(f"Object {object_id} not found")

        latest_packet = self.repo.get_latest_packet(object_id)
        if not latest_packet:
            raise NotFoundError(f"Object {object_id} not found")

        if end is None:
            end = latest_packet.received_at
        if start is None:
            start = end - timedelta(hours=24)

        packets = self.repo.get_packets_in_range(object_id, start, end, limit=5000)

        items = []
        for packet in packets:
            windows = packet.payload.get("windows", [])
            for window in windows:
                window_start = window.get("window_start")
                if isinstance(window_start, str):
                    try:
                        window_start = datetime.fromisoformat(
                            window_start.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        window_start = packet.received_at
                else:
                    window_start = packet.received_at

                points = window.get("points", [])
                for point in points:
                    point_point_id = point.get("point_id", "unknown")
                    point_type = point.get("type", "unknown")

                    if point_id is not None and point_point_id != point_id:
                        continue
                    if type_ is not None and point_type != type_:
                        continue

                    device_name = self.repo.get_device_name(packet.device_id)

                    item = MeasurementSeriesItem(
                        point_id=point_point_id,
                        point_name=point_type,
                        type=point_type,
                        unit=point.get("unit", "unknown"),
                        measured_at=window_start,
                        value=point.get("value"),
                        avg=point.get("avg"),
                        min=point.get("min"),
                        max=point.get("max"),
                        quality=point.get("quality", "unknown"),
                        device_id=packet.device_id,
                        device_name=device_name,
                    )
                    items.append(item)

        items = items[:limit]

        return MeasurementsResponse(
            object_id=object_id,
            from_=start,
            to=end,
            count=len(items),
            items=items,
        )
