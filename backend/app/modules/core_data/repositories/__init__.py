"""Core data repositories - data access layer."""

from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.users import UserRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository

__all__ = [
    "DeviceRepository",
    "MeasurementPointRepository",
    "OrganizationRepository",
    "UserRepository",
    "WaterObjectRepository",
]
