"""Auto-generated from sensor_registry.yaml. Do not edit manually."""

from typing import Literal

PointType = Literal[
    "temperature",
    "pressure",
    "flow_rate",
    "level",
    "battery_voltage",
    "digital_input",
    "modem_rssi",
    "power_status",
    "total_volume",
]

ErrorCode = Literal[
    "SENSOR_READ_FAILED",
    "SENSOR_FAULT_HW",
    "SENSOR_OUT_OF_RANGE",
    "POWER_LOW",
    "MODEM_SIGNAL_WEAK",
    "TIME_SYNC_FAILED",
    "WATCHDOG_RESTART",
    "WINDOW_DROPPED_BUFFER_FULL",
    "POINT_TYPE_MISMATCH",
]
