"""Integration tests: Telemetry ingest with runtime registry."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.modules.telemetry.schemas.measurement_packet import (
    ErrorEntry,
    MeasurementPacketRequest,
)


class TestErrorEntryValidation:
    """Validate error codes via new registry."""

    def test_valid_error_code_accepted(self):
        """Valid error_code in packet is accepted."""
        error = ErrorEntry(
            code="SENSOR_FAULT_HW",
            point_id="pt100_temp",
            severity="critical",
            message="MAX31865 fault",
        )
        assert error.code == "SENSOR_FAULT_HW"

    def test_invalid_error_code_rejected(self):
        """Invalid error_code raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorEntry(code="INVALID_CODE", point_id="pt100_temp", severity="critical")
        assert "Invalid error code" in str(exc_info.value)

    def test_error_codes_from_registry(self):
        """All registry error codes are valid."""
        from app.modules.core_data.registry import SensorRegistry

        for code in SensorRegistry.error_codes():
            error = ErrorEntry(code=code, severity="info")
            assert error.code == code


class TestMeasurementPacketValidation:
    """Validate measurement packet error codes."""

    def test_packet_with_valid_error_code(self):
        """Packet with valid error_code is accepted."""
        packet_data = {
            "v": 2,
            "device_id": "WW-001",
            "seq": 123,
            "sent_at": datetime.now(),
            "windows": [
                {"window_start": datetime.now(), "window_seconds": 15, "points": []}
            ],
            "errors": [
                {
                    "code": "SENSOR_FAULT_HW",
                    "point_id": "pt100_temp",
                    "severity": "critical",
                    "message": "MAX31865 fault",
                }
            ],
        }
        packet = MeasurementPacketRequest(**packet_data)
        assert packet.errors[0].code == "SENSOR_FAULT_HW"

    def test_packet_with_invalid_error_code_rejected(self):
        """Packet with invalid error_code raises ValidationError."""
        packet_data = {
            "v": 2,
            "device_id": "WW-001",
            "seq": 123,
            "sent_at": datetime.now(),
            "windows": [
                {"window_start": datetime.now(), "window_seconds": 15, "points": []}
            ],
            "errors": [
                {
                    "code": "INVALID_CODE",
                    "point_id": "pt100_temp",
                    "severity": "critical",
                }
            ],
        }
        with pytest.raises(ValidationError) as exc_info:
            MeasurementPacketRequest(**packet_data)
        assert "Invalid error code" in str(exc_info.value)

    def test_packet_without_errors_accepted(self):
        """Packet without errors is accepted (errors is optional)."""
        packet_data = {
            "v": 2,
            "device_id": "WW-001",
            "seq": 123,
            "sent_at": datetime.now(),
            "windows": [
                {
                    "window_start": datetime.now(),
                    "window_seconds": 15,
                    "points": [
                        {
                            "point_id": "sensor1",
                            "type": "temperature",
                            "unit": "°C",
                            "quality": "good",
                            "value": 23.5,
                        }
                    ],
                }
            ],
        }
        packet = MeasurementPacketRequest(**packet_data)
        assert len(packet.errors) == 0
