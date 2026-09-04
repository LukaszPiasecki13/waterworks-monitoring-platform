"""Runtime sensor registry loader — single source of truth from YAML.

- Backend: Loaded at app startup with thread-safe initialization and caching
- Firmware: Embedded as auto-generated JSON in PROGMEM (compile-time validation)

Registry path: project root/sensor_registry.yaml
"""

import logging
import threading
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Registry is at project root for shared access (backend + firmware)
REGISTRY_PATH = Path(__file__).resolve().parents[4] / "sensor_registry.yaml"


class RegistryLoadError(Exception):
    """Raised when registry cannot be loaded or is invalid."""

    pass


class SensorRegistry:
    """Thread-safe sensor registry loader with immutable caching.

    Initialization (app startup):
    - initialize() loads and validates YAML once, protected by lock
    - Raises RegistryLoadError if file missing or invalid

    Caching:
    - point_type_ids() and error_codes() return cached frozensets (immutable)
    - Cache built on first access, reused for all subsequent calls
    - Safe for concurrent access from FastAPI async handlers
    """

    _data: dict[str, Any] | None = None
    _schema_version: int | None = None
    _lock = threading.Lock()
    _point_type_ids_cache: frozenset[str] | None = None
    _error_codes_cache: frozenset[str] | None = None
    _state_sections_cache: dict[str, int] | None = None

    @classmethod
    def initialize(cls) -> None:
        """Load and validate registry at app startup (thread-safe, idempotent).

        Raises:
            RegistryLoadError: If registry file missing, corrupted, or invalid
        """
        with cls._lock:
            if cls._data is not None:
                return

            try:
                with open(REGISTRY_PATH, encoding="utf-8") as f:
                    cls._data = yaml.safe_load(f)
            except FileNotFoundError as e:
                msg = f"Registry file not found: {REGISTRY_PATH}"
                raise RegistryLoadError(msg) from e
            except yaml.YAMLError as e:
                msg = f"Invalid YAML in {REGISTRY_PATH}: {e}"
                raise RegistryLoadError(msg) from e

            cls._validate_structure()
            cls._schema_version = cls._data.get("schema_version", 1)

            logger.info(
                "Registry loaded: schema_version=%d, point_types=%d, "
                "error_codes=%d, state_sections=%d",
                cls._schema_version,
                len(cls._data["point_types"]),
                len(cls._data["error_codes"]),
                len(cls._data["state_sections"]),
            )

    @classmethod
    def _validate_structure(cls) -> None:
        """Validate registry YAML structure and required fields.

        Raises:
            RegistryLoadError: If structure is invalid
        """
        if not isinstance(cls._data, dict):
            raise RegistryLoadError("Registry must be a YAML dict")

        required_keys = {"point_types", "error_codes", "state_sections"}
        if not required_keys.issubset(cls._data.keys()):
            missing = required_keys - cls._data.keys()
            raise RegistryLoadError(f"Registry missing required keys: {missing}")

        # Validate point_types entries
        for pt in cls._data["point_types"]:
            if not isinstance(pt, dict) or "id" not in pt:
                msg = f"Invalid point_type entry (missing 'id'): {pt}"
                raise RegistryLoadError(msg)

        # Validate error_codes entries
        for ec in cls._data["error_codes"]:
            if not isinstance(ec, dict) or "code" not in ec:
                msg = f"Invalid error_code entry (missing 'code'): {ec}"
                raise RegistryLoadError(msg)

        # Validate state_sections entries — each needs its own schema_version,
        # because a section evolves independently of the registry as a whole.
        for ss in cls._data["state_sections"]:
            if not isinstance(ss, dict) or "id" not in ss:
                msg = f"Invalid state_section entry (missing 'id'): {ss}"
                raise RegistryLoadError(msg)
            version = ss.get("schema_version")
            if not isinstance(version, int) or isinstance(version, bool) or version < 1:
                msg = (
                    "Invalid state_section entry "
                    f"('schema_version' must be an int >= 1): {ss}"
                )
                raise RegistryLoadError(msg)

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Get loaded registry (raises if not initialized).

        Returns:
            Dict with keys: schema_version, point_types[], error_codes[]

        Raises:
            RegistryLoadError: If registry not initialized via initialize()
        """
        if cls._data is None:
            msg = "Registry not initialized — call initialize() at app startup"
            raise RegistryLoadError(msg)
        return cls._data

    @classmethod
    def schema_version(cls) -> int:
        """Get registry schema version for firmware/backend sync.

        Returns:
            Schema version (int)
        """
        return cls._schema_version or 1

    @classmethod
    def point_type_ids(cls) -> frozenset[str]:
        """Get all valid point_type IDs (cached).

        Returns:
            Frozenset of point_type IDs (e.g., {'temperature', 'pressure', ...})
        """
        if cls._point_type_ids_cache is None:
            registry = cls.load()
            cls._point_type_ids_cache = frozenset(
                pt["id"] for pt in registry["point_types"]
            )
        return cls._point_type_ids_cache

    @classmethod
    def error_codes(cls) -> frozenset[str]:
        """Get all valid error codes (cached).

        Returns:
            Frozenset of error codes (e.g., {'SENSOR_FAULT_HW', ...})
        """
        if cls._error_codes_cache is None:
            registry = cls.load()
            cls._error_codes_cache = frozenset(
                ec["code"] for ec in registry["error_codes"]
            )
        return cls._error_codes_cache

    @classmethod
    def state_sections(cls) -> dict[str, int]:
        """Get the device state section catalogue as {section_id: schema_version}.

        Returns:
            Mapping of registered state section ids to the schema version the
            backend currently understands for each.
        """
        if cls._state_sections_cache is None:
            registry = cls.load()
            cls._state_sections_cache = {
                ss["id"]: ss["schema_version"] for ss in registry["state_sections"]
            }
        return cls._state_sections_cache

    @classmethod
    def is_valid_point_type(cls, point_type_id: str) -> bool:
        """Check if point_type_id is registered."""
        return point_type_id in cls.point_type_ids()

    @classmethod
    def is_valid_error_code(cls, code: str) -> bool:
        """Check if error code is registered."""
        return code in cls.error_codes()

    @classmethod
    def is_valid_state_section(cls, section: str) -> bool:
        """Check if a device state section id is registered."""
        return section in cls.state_sections()

    @classmethod
    def state_section_schema_version(cls, section: str) -> int | None:
        """Schema version the backend expects for a section, None if unknown."""
        return cls.state_sections().get(section)
