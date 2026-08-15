"""Telemetry-specific exceptions."""

from fastapi import status

from app.core.errors import APIError, ConflictError, ForbiddenError


class TelemetryPacketAlreadyExistsError(ConflictError):
    """Raised when a packet for the same device and sequence already exists."""

    def __init__(self, device_id: str, seq: int):
        super().__init__(
            f"Telemetry packet already exists for device_id={device_id}, seq={seq}"
        )


class InvalidTelemetryIngestKeyError(ForbiddenError):
    """Raised when the telemetry ingest key is missing or invalid."""

    def __init__(self):
        super().__init__("Invalid telemetry ingest key")


class TelemetryIngestKeyNotConfiguredError(APIError):
    """Raised when the deployment has no telemetry ingest key configured.

    A server-side misconfiguration, not a client error: ingest stays closed
    until TELEMETRY_INGEST_KEY is set.
    """

    def __init__(self):
        super().__init__(
            "Telemetry ingest is not configured",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
