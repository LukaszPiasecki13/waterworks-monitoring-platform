#!/usr/bin/env python3
"""Sensor registry pre-build workflow: generate header + verify sync.

Workflow:
1. Generate firmware/include/SensorRegistry.h from YAML (single source of truth)
2. Verify that firmware and backend registry are synced

Can be used in two ways:
1. Standalone: python3 prebuild.py
2. PlatformIO pre-build hook: extra_scripts = scripts/prebuild.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def generate():
    """Generate firmware/include/SensorRegistry.h from YAML registry.

    Returns:
        bool: True if generation succeeded, False otherwise
    """
    script_dir = Path(__file__).parent
    generator_script = script_dir / "generate_sensor_registry.py"

    if not generator_script.exists():
        print(f"❌ Generator script not found: {generator_script}", file=sys.stderr)
        return False

    result = subprocess.run(
        [sys.executable, str(generator_script)],
        cwd=Path(__file__).parent.parent.parent,  # Project root
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0


def validate():
    """Validate firmware registry JSON is synced with backend YAML.

    Returns:
        bool: True if registries match, False if validation failed
    """
    firmware_h = Path("firmware/include/SensorRegistry.h")
    yaml_registry = Path("sensor_registry.yaml")

    # Extract embedded JSON from .h file
    try:
        with open(firmware_h, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Firmware header not found: {firmware_h}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"❌ Error reading {firmware_h}: {e}", file=sys.stderr)
        return False

    # Extract JSON from R"({...})"; format
    match = re.search(r'R"\((\{.+?\})\)";', content, re.DOTALL)
    if not match:
        print(f"❌ Invalid header format: could not find embedded JSON in {firmware_h}", file=sys.stderr)
        return False

    try:
        fw_json = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"❌ Malformed JSON in firmware header: {e}", file=sys.stderr)
        return False

    # Load YAML registry
    try:
        with open(yaml_registry, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ YAML registry not found: {yaml_registry}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in {yaml_registry}: {e}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"❌ Error reading {yaml_registry}: {e}", file=sys.stderr)
        return False

    # Validate schema_version matches
    fw_version = fw_json.get("schema_version", 1)
    yaml_version = yaml_data.get("schema_version", 1)
    if fw_version != yaml_version:
        print(
            f"❌ Schema version mismatch: firmware={fw_version}, backend={yaml_version}. "
            f"Rebuild firmware after YAML changes!",
            file=sys.stderr,
        )
        return False

    # Validate point_types match
    fw_types = set(fw_json.get("point_types", []))
    yaml_types = {pt["id"] for pt in yaml_data.get("point_types", [])}
    if fw_types != yaml_types:
        missing_in_fw = yaml_types - fw_types
        removed_from_backend = fw_types - yaml_types
        print(
            f"❌ Point types mismatch:",
            file=sys.stderr,
        )
        if missing_in_fw:
            print(f"   Missing in firmware: {missing_in_fw}", file=sys.stderr)
        if removed_from_backend:
            print(f"   Removed from backend: {removed_from_backend}", file=sys.stderr)
        return False

    # Validate error_codes match
    fw_codes = set(fw_json.get("error_codes", []))
    yaml_codes = {ec["code"] for ec in yaml_data.get("error_codes", [])}
    if fw_codes != yaml_codes:
        missing_in_fw = yaml_codes - fw_codes
        removed_from_backend = fw_codes - yaml_codes
        print(
            f"❌ Error codes mismatch:",
            file=sys.stderr,
        )
        if missing_in_fw:
            print(f"   Missing in firmware: {missing_in_fw}", file=sys.stderr)
        if removed_from_backend:
            print(f"   Removed from backend: {removed_from_backend}", file=sys.stderr)
        return False

    # Validate state_sections match, ids and per-section schema_version alike:
    # a section whose version drifted would let firmware stamp a shape the
    # backend no longer expects.
    fw_sections = fw_json.get("state_sections", {})
    yaml_sections = {
        ss["id"]: ss["schema_version"] for ss in yaml_data.get("state_sections", [])
    }
    if fw_sections != yaml_sections:
        missing_in_fw = set(yaml_sections) - set(fw_sections)
        removed_from_backend = set(fw_sections) - set(yaml_sections)
        version_drift = {
            sid: (fw_sections[sid], yaml_sections[sid])
            for sid in set(fw_sections) & set(yaml_sections)
            if fw_sections[sid] != yaml_sections[sid]
        }
        print("❌ State sections mismatch:", file=sys.stderr)
        if missing_in_fw:
            print(f"   Missing in firmware: {missing_in_fw}", file=sys.stderr)
        if removed_from_backend:
            print(f"   Removed from backend: {removed_from_backend}", file=sys.stderr)
        if version_drift:
            print(
                f"   schema_version drift (firmware, backend): {version_drift}",
                file=sys.stderr,
            )
        return False

    print("✅ Firmware registry JSON valid and synced with backend")
    return True


def platformio_prebuild(source, target, env):
    """PlatformIO pre-build hook: generate registry header + verify sync.

    Called by PlatformIO before firmware.elf is built.
    Workflow:
    1. Generate SensorRegistry.h from YAML (single source of truth)
    2. Verify firmware and backend are synced
    """
    print("\n" + "="*70)
    print("PRE-BUILD: Sensor registry workflow...")
    print("="*70)

    # Step 1: Generate header from YAML
    print("\n[1/2] Generating firmware/include/SensorRegistry.h from YAML...")
    if not generate():
        print("\n" + "="*70)
        print("❌ BUILD FAILED: SensorRegistry.h generation failed!")
        print("="*70)
        env.Exit(1)

    # Step 2: Verify sync
    print("\n[2/2] Verifying firmware/backend sync...")
    if not validate():
        print("\n" + "="*70)
        print("❌ BUILD FAILED: Firmware registry out of sync with backend!")
        print("="*70)
        env.Exit(1)

    print("="*70)
    print("✅ Sensor registry ready for build")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Standalone mode: python3 prebuild.py
    print("=" * 70)
    print("Sensor registry workflow")
    print("=" * 70)

    print("\n[1/2] Generating SensorRegistry.h from YAML...")
    if not generate():
        sys.exit(1)

    print("\n[2/2] Verifying firmware/backend sync...")
    if not validate():
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Registry ready")
    print("=" * 70)
    sys.exit(0)

# PlatformIO pre-build hook integration
try:
    Import("env")
    env.AddPreAction("$BUILD_DIR/firmware.elf", platformio_prebuild)
except NameError:
    pass
