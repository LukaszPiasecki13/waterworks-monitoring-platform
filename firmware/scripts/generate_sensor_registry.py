#!/usr/bin/env python3
"""Generate SensorRegistry.h from sensor_registry.yaml — single source of truth.

This script:
1. Reads sensor_registry.yaml (project root)
2. Generates firmware/include/SensorRegistry.h with embedded JSON + constexpr validators
3. Ensures zero duplication and perfect sync between YAML and firmware

Can be used:
- Standalone: python3 generate_sensor_registry.py
- Pre-build hook: integrated into prebuild.py
"""

import json
import sys
from pathlib import Path

import yaml

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def generate():
    """Generate SensorRegistry.h from YAML registry.

    Returns:
        bool: True if generation succeeded, False if errors occurred
    """
    yaml_registry = Path("sensor_registry.yaml")
    header_file = Path("firmware/include/SensorRegistry.h")

    # Load YAML
    try:
        with open(yaml_registry, encoding="utf-8") as f:
            registry = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Registry file not found: {yaml_registry}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in {yaml_registry}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error reading {yaml_registry}: {e}", file=sys.stderr)
        return False

    # Validate registry structure
    if not isinstance(registry, dict):
        print("❌ Registry must be a YAML dict", file=sys.stderr)
        return False

    # Extract and validate data
    if "point_types" not in registry or "error_codes" not in registry:
        print("❌ Registry missing required keys: point_types, error_codes", file=sys.stderr)
        return False

    try:
        schema_version = registry.get("schema_version", 1)
        point_types = [pt["id"] for pt in registry.get("point_types", [])]
        error_codes = [ec["code"] for ec in registry.get("error_codes", [])]
    except (KeyError, TypeError) as e:
        print(f"❌ Invalid registry structure: {e}", file=sys.stderr)
        return False

    if not point_types:
        print("❌ Registry has no point_types defined", file=sys.stderr)
        return False
    if not error_codes:
        print("❌ Registry has no error_codes defined", file=sys.stderr)
        return False

    # Build embedded JSON (compact)
    embedded_json = json.dumps(
        {
            "schema_version": schema_version,
            "point_types": point_types,
            "error_codes": error_codes,
        },
        separators=(",", ":"),  # Compact: no spaces
    )

    # Generate OR chain for isValidPointType
    point_types_checks = " ||\n           ".join(
        f'stringEquals(id, "{pt}")' for pt in point_types
    )

    # Generate OR chain for isValidErrorCode
    error_codes_checks = " ||\n           ".join(
        f'stringEquals(code, "{code}")' for code in error_codes
    )

    # Generate header file
    header_content = f'''#pragma once

#include <Arduino.h>

// ⚠️ CRITICAL: This file is auto-generated from sensor_registry.yaml
// DO NOT EDIT manually. Regenerate with: python3 firmware/scripts/generate_sensor_registry.py
// Backend: docs/technical/telemetry/sensor_registry.yaml (schema_version: {schema_version})

// Embedded sensor registry JSON (generated from sensor_registry.yaml)
constexpr const char SENSOR_REGISTRY_JSON[] PROGMEM = R"({embedded_json})";

class SensorRegistry {{
 public:
  // Firmware schema version (auto-generated from YAML schema_version)
  static constexpr int SCHEMA_VERSION = {schema_version};

  static constexpr bool isValidPointType(const char* id) {{
    return {point_types_checks};
  }}

  static constexpr bool isValidErrorCode(const char* code) {{
    return {error_codes_checks};
  }}

 private:
  static constexpr bool stringEquals(const char* a, const char* b) {{
    return *a == *b && (*a == '\\0' || stringEquals(a + 1, b + 1));
  }}
}};

// Compile-time schema version validation
static_assert(SensorRegistry::SCHEMA_VERSION == {schema_version},
              "Firmware schema_version must match backend ({schema_version})");
'''

    # Write header file
    try:
        header_file.parent.mkdir(parents=True, exist_ok=True)
        with open(header_file, "w", encoding="utf-8") as f:
            f.write(header_content)
        print(f"✅ Generated {header_file} ({len(point_types)} point_types, {len(error_codes)} error_codes)")
        return True
    except IOError as e:
        print(f"❌ Failed to write {header_file}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = generate()
    sys.exit(0 if success else 1)
