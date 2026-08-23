"""Device identity models."""

from app.modules.device_identity.models.device_activation_code import (
    DeviceActivationCode,
)
from app.modules.device_identity.models.device_credential import DeviceCredential

__all__ = ["DeviceActivationCode", "DeviceCredential"]
