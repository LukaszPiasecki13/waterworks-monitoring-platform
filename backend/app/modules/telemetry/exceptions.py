"""Telemetry-specific exceptions."""

from app.core.errors import ConflictError, PermissionError


class TelemetryPacketAlreadyExistsError(ConflictError):
    """Raised when a packet for the same device and sequence already exists."""

    def __init__(self, device_id: str, seq: int):
        super().__init__(
            f"Telemetry packet already exists for device_id={device_id}, seq={seq}"
        )


class InvalidTelemetryIngestKeyError(PermissionError):
    """Raised when the telemetry ingest key is missing or invalid."""

    def __init__(self):
        super().__init__("Invalid telemetry ingest key")
