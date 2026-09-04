#!/usr/bin/env python3
"""Pre-build: generacja plików pochodnych i walidacja kontraktów.

Kroki:
1. Wygeneruj ``firmware/include/SensorRegistry.h`` z ``sensor_registry.yaml``
   (jedyne źródło prawdy o typach punktów i kodach błędów).
2. Sprawdź, że wygenerowany nagłówek zgadza się z YAML-em.
3. Tylko dla ``env:native``: wygeneruj ``firmware/test/contract/PayloadContract.h``
   ze schematu backendu, żeby test kontraktowy sprawdzał aktualne reguły.

Uruchomienie:
1. Samodzielnie:            python3 firmware/scripts/prebuild.py
2. Hook PlatformIO:         extra_scripts = pre:scripts/prebuild.py

Uwaga na katalog roboczy: PlatformIO uruchamia hook z katalogu ``firmware/``,
a człowiek zwykle z korzenia repozytorium. Wszystkie ścieżki są więc liczone
od położenia tego pliku, nie od ``os.getcwd()``.
"""

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# SCons wykonuje skrypty `extra_scripts` przez exec(), a wtedy `__file__` nie
# istnieje. `co_filename` bieżącej ramki działa w obu trybach uruchomienia.
SCRIPT_DIR = Path(inspect.currentframe().f_code.co_filename).resolve().parent

REPO_ROOT = SCRIPT_DIR.parents[1]
FIRMWARE_HEADER = REPO_ROOT / "firmware" / "include" / "SensorRegistry.h"
YAML_REGISTRY = REPO_ROOT / "sensor_registry.yaml"
CONTRACT_SCRIPT = SCRIPT_DIR / "generate_payload_contract.py"

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def generate():
    """Generate firmware/include/SensorRegistry.h from YAML registry.

    Returns:
        bool: True if generation succeeded, False otherwise
    """
    generator_script = SCRIPT_DIR / "generate_sensor_registry.py"

    if not generator_script.exists():
        print(f"❌ Generator script not found: {generator_script}", file=sys.stderr)
        return False

    result = subprocess.run(
        [sys.executable, str(generator_script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
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
    # Extract embedded JSON from .h file
    try:
        with open(FIRMWARE_HEADER, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Firmware header not found: {FIRMWARE_HEADER}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"❌ Error reading {FIRMWARE_HEADER}: {e}", file=sys.stderr)
        return False

    # Extract JSON from R"({...})"; format
    match = re.search(r'R"\((\{.+?\})\)";', content, re.DOTALL)
    if not match:
        print(f"❌ Invalid header format: could not find embedded JSON in {FIRMWARE_HEADER}", file=sys.stderr)
        return False

    try:
        fw_json = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"❌ Malformed JSON in firmware header: {e}", file=sys.stderr)
        return False

    # Load YAML registry
    try:
        with open(YAML_REGISTRY, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ YAML registry not found: {YAML_REGISTRY}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in {YAML_REGISTRY}: {e}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"❌ Error reading {YAML_REGISTRY}: {e}", file=sys.stderr)
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
        print("❌ Point types mismatch:", file=sys.stderr)
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
        print("❌ Error codes mismatch:", file=sys.stderr)
        if missing_in_fw:
            print(f"   Missing in firmware: {missing_in_fw}", file=sys.stderr)
        if removed_from_backend:
            print(f"   Removed from backend: {removed_from_backend}", file=sys.stderr)
        return False

    print("✅ Firmware registry JSON valid and synced with backend")
    return True


def generate_payload_contract():
    """Regenerate the payload contract header used by the native contract test.

    Only relevant for `env:native`: the header describes the backend's
    MeasurementPacketRequest and never ends up in the device binary.

    Returns:
        bool: True if generation succeeded, False otherwise
    """
    if not CONTRACT_SCRIPT.exists():
        print(f"❌ Contract generator not found: {CONTRACT_SCRIPT}", file=sys.stderr)
        return False

    result = subprocess.run(
        [sys.executable, str(CONTRACT_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0


def run(include_payload_contract):
    """Run every pre-build step; returns True when all of them pass."""
    steps = [
        ("Generating firmware/include/SensorRegistry.h from YAML", generate),
        ("Verifying firmware/backend registry sync", validate),
    ]
    if include_payload_contract:
        steps.append(("Generating payload contract from backend schema", generate_payload_contract))

    for index, (title, step) in enumerate(steps, start=1):
        print(f"\n[{index}/{len(steps)}] {title}...")
        if not step():
            return False
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("Pre-build: sensor registry + payload contract")
    print("=" * 70)

    if not run(include_payload_contract=True):
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Generated artifacts ready")
    print("=" * 70)
    sys.exit(0)

# Integracja z PlatformIO.
#
# Skrypt jest podpięty jako `pre:scripts/prebuild.py`, więc wykonuje się przy
# ładowaniu środowiska — zanim ruszy kompilacja czegokolwiek. Poprzednia wersja
# wieszała się na `AddPreAction("$BUILD_DIR/firmware.elf")`, przez co w ogóle
# nie działała dla `env:native` (tam celem jest `program`, nie `firmware.elf`).
try:
    Import("env")  # noqa: F821 - wstrzykiwane przez SCons

    _env_name = env["PIOENV"]  # noqa: F821
    _is_native = env.get("PIOPLATFORM") == "native"  # noqa: F821

    print("\n" + "=" * 70)
    print(f"PRE-BUILD [{_env_name}]: sensor registry" + (" + payload contract" if _is_native else ""))
    print("=" * 70)

    if not run(include_payload_contract=_is_native):
        print("\n" + "=" * 70)
        print("❌ BUILD FAILED: pre-build generation/validation failed")
        print("=" * 70)
        env.Exit(1)  # noqa: F821

    print("=" * 70)
    print("✅ Pre-build OK")
    print("=" * 70 + "\n")
except NameError:
    pass
