"""Read side of the device state channel (B-08)."""

from datetime import UTC, datetime
from uuid import UUID

from app.core.config import Settings
from app.modules.core_data.models.device import Device
from app.modules.core_data.services.devices import DeviceService
from app.modules.telemetry.models.device_state_report import DeviceStateReport
from app.modules.telemetry.repositories.device_state import (
    DeviceStateReportRepository,
)
from app.modules.telemetry.schemas.device_state import (
    DeviceStateResponse,
    DeviceStateSectionResponse,
)


class DeviceStateQueryService:
    """Serves the last known state of a device, always dated.

    Freshness is computed here rather than stored, because "how old is this"
    is a property of the moment someone asks, not of the row. The staleness
    threshold is the same `telemetry_stale_after_seconds` the dashboard uses
    for `no_comm`, so a device cannot read "stale" in one view and "fine" in
    the other.
    """

    def __init__(
        self,
        repository: DeviceStateReportRepository,
        device_service: DeviceService,
        settings: Settings,
    ):
        self.repo = repository
        self.device_service = device_service
        self.settings = settings

    def _to_section(
        self, report: DeviceStateReport, now: datetime
    ) -> DeviceStateSectionResponse:
        captured_at = report.captured_at
        if captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=UTC)

        # A device clock running ahead would otherwise yield a negative age;
        # clamping keeps "0 s" meaning "as fresh as we can tell".
        age_seconds = max(0, int((now - captured_at).total_seconds()))

        return DeviceStateSectionResponse(
            section=report.section,
            schema_version=report.schema_version,
            captured_at=report.captured_at,
            received_at=report.received_at,
            age_seconds=age_seconds,
            is_stale=age_seconds > self.settings.telemetry_stale_after_seconds,
            data=report.data,
        )

    def get_device_state(
        self, device_id: UUID, organization_id: UUID | None = None
    ) -> DeviceStateResponse:
        """Latest state per section for one device.

        A device that has never reported state is not an error — it returns
        an empty `sections` list, the same way an object awaiting its first
        packet reports `no_data` instead of 404.
        """
        device: Device = self.device_service.get_by_id(
            device_id, organization_id=organization_id
        )

        now = datetime.now(UTC)
        reports = self.repo.list_latest_sections(device.external_id)

        return DeviceStateResponse(
            device_id=device.id,
            external_id=device.external_id,
            last_seen_at=device.last_seen_at,
            last_diagnostics_at=device.last_diagnostics_at,
            sections=[self._to_section(report, now) for report in reports],
        )
