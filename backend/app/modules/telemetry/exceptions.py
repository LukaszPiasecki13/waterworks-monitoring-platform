"""Telemetry-specific exceptions."""

from app.core.errors import ConflictError


class TelemetryPacketAlreadyExistsError(ConflictError):
    """Raised when a packet for the same device and sequence already exists."""

    def __init__(self, device_id: str, seq: int):
        super().__init__(
            f"Telemetry packet already exists for device_id={device_id}, seq={seq}"
        )
