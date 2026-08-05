"""Telemetry schemas."""

from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    TelemetryIngestResponse,
)

__all__ = [
    "MeasurementPacketRequest",
    "TelemetryIngestResponse",
]
