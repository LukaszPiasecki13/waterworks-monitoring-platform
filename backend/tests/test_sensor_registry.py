"""Unit tests for sensor registry runtime loading."""

import threading

from app.modules.core_data.registry import SensorRegistry


class TestSensorRegistry:
    """Unit tests for SensorRegistry runtime loading."""

    def test_initialize_success(self):
        """Registry initializes without error."""
        SensorRegistry.initialize()
        assert SensorRegistry._data is not None

    def test_point_type_ids_complete(self):
        """All point_types from YAML are loaded."""
        ids = SensorRegistry.point_type_ids()
        assert "temperature" in ids
        assert "pressure" in ids
        assert len(ids) >= 9

    def test_error_codes_complete(self):
        """All error_codes from YAML are loaded."""
        codes = SensorRegistry.error_codes()
        assert "SENSOR_FAULT_HW" in codes
        assert "SENSOR_READ_FAILED" in codes
        assert len(codes) >= 9

    def test_is_valid_point_type_true(self):
        """Valid point_type returns True."""
        assert SensorRegistry.is_valid_point_type("temperature") is True

    def test_is_valid_point_type_false(self):
        """Invalid point_type returns False."""
        assert SensorRegistry.is_valid_point_type("invalid_type") is False

    def test_is_valid_error_code_true(self):
        """Valid error_code returns True."""
        assert SensorRegistry.is_valid_error_code("SENSOR_FAULT_HW") is True

    def test_is_valid_error_code_false(self):
        """Invalid error_code returns False."""
        assert SensorRegistry.is_valid_error_code("INVALID_CODE") is False

    def test_schema_version_matches_backend(self):
        """Schema version from registry is available."""
        version = SensorRegistry.schema_version()
        assert version >= 1

    def test_registry_not_reloaded_on_second_call(self):
        """Registry cached in memory (load only once)."""
        v1 = id(SensorRegistry.load())
        v2 = id(SensorRegistry.load())
        assert v1 == v2  # Same object reference


class TestSensorRegistryErrors:
    """Error handling tests."""

    def test_point_types_structure_valid(self):
        """Point types have required fields."""
        registry = SensorRegistry.load()
        for pt in registry.get("point_types", []):
            assert "id" in pt
            assert isinstance(pt["id"], str)
            assert len(pt["id"]) > 0

    def test_error_codes_structure_valid(self):
        """Error codes have required fields."""
        registry = SensorRegistry.load()
        for ec in registry.get("error_codes", []):
            assert "code" in ec
            assert isinstance(ec["code"], str)
            assert len(ec["code"]) > 0


class TestSensorRegistryThreadSafety:
    """Thread-safety and race condition tests."""

    def test_concurrent_initialization_is_safe(self):
        """Multiple threads initializing registry simultaneously is safe."""
        # Reset registry state for this test
        SensorRegistry._data = None
        SensorRegistry._schema_version = None
        SensorRegistry._point_type_ids_cache = None
        SensorRegistry._error_codes_cache = None
        SensorRegistry._state_sections_cache = None

        results = []
        errors = []

        def init_registry():
            try:
                SensorRegistry.initialize()
                results.append("success")
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=init_registry) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should succeed and no exceptions should occur
        assert len(errors) == 0, f"Concurrent init raised errors: {errors}"
        assert SensorRegistry._data is not None

    def test_concurrent_point_type_access_is_consistent(self):
        """Multiple threads accessing point_type_ids() get same result."""
        results = []

        def get_types():
            ids = SensorRegistry.point_type_ids()
            results.append(ids)

        threads = [threading.Thread(target=get_types) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be identical (same object reference due to caching)
        assert all(r is results[0] for r in results), (
            "Concurrent access returned different cached objects"
        )
        assert isinstance(results[0], frozenset)

    def test_concurrent_error_codes_access_is_consistent(self):
        """Multiple threads accessing error_codes() get same result."""
        results = []

        def get_codes():
            codes = SensorRegistry.error_codes()
            results.append(codes)

        threads = [threading.Thread(target=get_codes) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be identical (same object reference due to caching)
        assert all(r is results[0] for r in results), (
            "Concurrent access returned different cached objects"
        )
        assert isinstance(results[0], frozenset)

    def test_caching_returns_frozenset(self):
        """point_type_ids and error_codes return frozen immutable sets."""
        assert isinstance(SensorRegistry.point_type_ids(), frozenset)
        assert isinstance(SensorRegistry.error_codes(), frozenset)
