"""Telemetry-specific exceptions."""

from fastapi import status

from app.core.errors import APIError, AuthenticationError, ConflictError, ForbiddenError


class TelemetryPacketAlreadyExistsError(ConflictError):
    """Raised when a packet for the same device and sequence already exists."""

    def __init__(self, device_id: str, seq: int):
        super().__init__(
            f"Telemetry packet already exists for device_id={device_id}, seq={seq}"
        )


class UnknownDeviceError(AuthenticationError):
    """Raised when device with given external_id does not exist."""

    def __init__(self, device_id: str):
        super().__init__(f"Device '{device_id}' not found")


class InvalidDeviceSecretError(ForbiddenError):
    """Raised when device secret (X-Device-Key) does not match."""

    def __init__(self):
        super().__init__("Invalid device credentials")


class InactiveDeviceError(ForbiddenError):
    """Raised when device is inactive (is_active=False)."""

    def __init__(self, device_id: str):
        super().__init__(f"Device '{device_id}' is inactive")


class InvalidTelemetryIngestKeyError(ForbiddenError):
    """Raised when the telemetry ingest key is missing or invalid.

    Deprecated: kept for backwards compatibility during transition to per-device auth.
    """

    def __init__(self):
        super().__init__("Invalid telemetry ingest key")


class TelemetryIngestKeyNotConfiguredError(APIError):
    """Raised when the deployment has no telemetry ingest key configured.

    A server-side misconfiguration, not a client error: ingest stays closed
    until TELEMETRY_INGEST_KEY is set.

    Deprecated: kept for backwards compatibility during transition to per-device auth.
    """

    def __init__(self):
        super().__init__(
            "Telemetry ingest is not configured",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
