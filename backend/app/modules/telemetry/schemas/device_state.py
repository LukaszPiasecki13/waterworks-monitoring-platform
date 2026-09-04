"""Schemas for the device state read channel (B-08).

The device is behind carrier NAT, so the backend can never pull from it. Every
read is therefore answered by the device on its next contact, as one or more
*sections* carried in the telemetry packet's optional `state[]` array. This
module holds both halves of that contract:

- `StateSectionEntry` — the wire shape of one section, section-agnostic.
- `DeviceStateData` — the field-level shape of the `device` section.
- the read-side responses, which always pair a value with its age.

Adding a new read (device configuration, for example) means adding a section id
to `sensor_registry.yaml` plus a typed model here — not a new endpoint.
"""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.core.schemas import BaseSchema

# The section every device reports today: health and identity.
SECTION_DEVICE = "device"

# Upper bounds on one section's payload. Generous against the ~330 B / 12 keys
# the `device` section actually uses, tight enough that a compromised or
# malfunctioning gateway cannot grow the JSONB column without limit.
MAX_SECTION_KEYS = 64
MAX_SECTION_BYTES = 8192

# esp_reset_reason() values, mapped to names by the firmware before sending.
# "unknown" covers both an unmapped reason and firmware too old to report one.
RESTART_REASONS = frozenset(
    {
        "unknown",
        "power_on",
        "external",
        "software",
        "panic",
        "int_watchdog",
        "task_watchdog",
        "other_watchdog",
        "deep_sleep",
        "brownout",
        "sdio",
    }
)


class DeviceStateData(BaseSchema):
    """Field-level contract of the `device` section, schema_version 1.

    `extra="allow"` on purpose: a device running newer firmware may report
    fields this backend has not learned about yet, and dropping them at the
    door would lose data that is already paid for in transfer. Known fields
    are still typed, so a firmware regression on one of them is caught here
    rather than surfacing as a broken dashboard.
    """

    model_config = ConfigDict(extra="allow")

    serial_number: str | None = Field(None, max_length=128)
    firmware_version: str | None = Field(None, max_length=50)
    registry_schema_version: int | None = Field(None, ge=0)

    uptime_seconds: int | None = Field(None, ge=0)
    restart_count: int | None = Field(None, ge=0)
    restart_reason: str | None = Field(None, max_length=32)

    # RSSI in dBm; omitted (None) when the modem reports an unknown CSQ.
    rssi_dbm: int | None = Field(None, ge=-140, le=0)

    free_heap_bytes: int | None = Field(None, ge=0)
    min_free_heap_bytes: int | None = Field(None, ge=0)

    # Local buffer state — the platform promises 72 h of offline retention
    # while the device buffers roughly 12 minutes in RAM, so silent data loss
    # is only visible through these three fields.
    buffer_windows_used: int | None = Field(None, ge=0)
    buffer_windows_capacity: int | None = Field(None, ge=0)
    buffer_windows_dropped: int | None = Field(None, ge=0)

    @field_validator("restart_reason")
    @classmethod
    def validate_restart_reason(cls, v: str | None) -> str | None:
        if v is not None and v not in RESTART_REASONS:
            raise ValueError(
                f"Unknown restart_reason '{v}'. "
                f"Must be one of: {', '.join(sorted(RESTART_REASONS))}"
            )
        return v


class StateSectionEntry(BaseSchema):
    """One state section as it arrives on the wire.

    Deliberately section-agnostic: `data` is validated against the section's
    own model during ingest, not here, so an unknown or malformed section
    degrades to a flagged error entry instead of rejecting the whole packet
    and taking the measurements down with it.
    """

    model_config = ConfigDict(extra="forbid")

    section: str = Field(min_length=1, max_length=64)
    schema_version: int = Field(ge=1)
    captured_at: datetime
    data: dict[str, Any]

    @field_validator("data")
    @classmethod
    def bound_section_size(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Cap what an authenticated device can push into JSONB storage.

        `data` is stored verbatim so a newer firmware loses nothing, which
        also means the shape is not otherwise constrained. The real `device`
        section is ~330 B over ~12 keys, so these limits leave a wide margin
        for growth while keeping one misbehaving gateway from writing
        unbounded rows.
        """
        if len(v) > MAX_SECTION_KEYS:
            raise ValueError(
                f"State section carries {len(v)} keys, limit is {MAX_SECTION_KEYS}"
            )
        size = len(json.dumps(v, separators=(",", ":"), default=str))
        if size > MAX_SECTION_BYTES:
            raise ValueError(
                f"State section payload is {size} B, limit is {MAX_SECTION_BYTES} B"
            )
        return v


class DeviceStateSectionResponse(BaseSchema):
    """One stored section, read back with its age.

    `captured_at` is the device's clock at capture, `received_at` the
    platform's clock at arrival, and `age_seconds` is computed per request —
    a state read is never presented without saying how old it is.
    """

    section: str
    schema_version: int
    captured_at: datetime
    received_at: datetime
    age_seconds: int
    is_stale: bool
    data: dict[str, Any]


class DeviceStateResponse(BaseSchema):
    """Latest known state of one device, one entry per reported section."""

    device_id: UUID
    external_id: str
    last_seen_at: datetime | None = None
    last_diagnostics_at: datetime | None = None
    sections: list[DeviceStateSectionResponse] = Field(default_factory=list)
