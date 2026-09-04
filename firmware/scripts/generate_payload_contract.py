#!/usr/bin/env python3
"""Generate firmware/test/contract/PayloadContract.h from the backend schema.

Source of truth: backend/app/modules/telemetry/schemas/measurement_packet.py
(``MeasurementPacketRequest`` and its nested models).

Why AST instead of importing the model
--------------------------------------
Importing ``MeasurementPacketRequest`` pulls in the whole ``app`` package
(SQLAlchemy models, pydantic, Python >= 3.14 syntax). Making a firmware test
build depend on the backend runtime environment is a bad trade, so the shape of
the contract is read statically instead.

The cost of that choice is that this script can silently misread a refactored
schema. To make that impossible it FAILS LOUDLY whenever the file no longer
looks the way it expects (missing class, missing ``extra="forbid"``, severity
that is not a ``Literal``, ...). A build failure is the correct outcome there —
a quietly empty contract would be worse than no contract at all.

Codes of telemetry errors are deliberately NOT duplicated here: the firmware
already validates them against the generated ``SensorRegistry.h``, which comes
from the same ``sensor_registry.yaml`` the backend loads at runtime.

Usage:
    python3 firmware/scripts/generate_payload_contract.py           # write header
    python3 firmware/scripts/generate_payload_contract.py --check   # verify only
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT / "backend" / "app" / "modules" / "telemetry" / "schemas" / "measurement_packet.py"
)
HEADER_PATH = REPO_ROOT / "firmware" / "test" / "contract" / "PayloadContract.h"

PACKET_CLASS = "MeasurementPacketRequest"
WINDOW_CLASS = "MeasurementWindow"
POINT_CLASS = "MeasurementPoint"
ERROR_CLASS = "ErrorEntry"


class ContractError(Exception):
    """The schema no longer matches what this generator knows how to read."""


# --- odczyt schematu -------------------------------------------------------


def _classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def _field_call(value: ast.expr | None) -> ast.Call | None:
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "Field":
        return value
    return None


def _is_required(value: ast.expr | None) -> bool:
    """A pydantic field is required unless it carries a default."""
    if value is None:
        return True

    call = _field_call(value)
    if call is None:
        return False  # plain `= None` / `= 5` -> optional

    if call.args:
        return False  # Field(None, ...) -> first positional is the default
    return not any(kw.arg in ("default", "default_factory") for kw in call.keywords)


def _field_kwarg(value: ast.expr | None, name: str) -> object | None:
    call = _field_call(value)
    if call is None:
        return None
    for kw in call.keywords:
        if kw.arg == name and isinstance(kw.value, ast.Constant):
            return kw.value.value
    return None


def _annotation_literals(annotation: ast.expr) -> list[str] | None:
    """Return the values of `Literal["a", "b"]`, or None if not a Literal."""
    if not isinstance(annotation, ast.Subscript):
        return None
    if not (isinstance(annotation.value, ast.Name) and annotation.value.id == "Literal"):
        return None

    elements = annotation.slice.elts if isinstance(annotation.slice, ast.Tuple) else [annotation.slice]
    values = []
    for element in elements:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            raise ContractError("Literal[...] zawiera wartość, która nie jest łańcuchem znaków")
        values.append(element.value)
    return values


def _split_fields(cls: ast.ClassDef) -> tuple[list[str], list[str], dict[str, ast.AnnAssign]]:
    required: list[str] = []
    optional: list[str] = []
    by_name: dict[str, ast.AnnAssign] = {}

    for node in cls.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        name = node.target.id
        if name == "model_config":
            continue
        by_name[name] = node
        (required if _is_required(node.value) else optional).append(name)

    if not by_name:
        raise ContractError(f"klasa {cls.name} nie ma żadnych pól — schemat wygląda inaczej niż zakładano")
    return required, optional, by_name


def _forbids_extra(cls: ast.ClassDef) -> bool:
    for node in cls.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "model_config" not in targets:
            continue
        if isinstance(node.value, ast.Call):
            for kw in node.value.keywords:
                if kw.arg == "extra" and isinstance(kw.value, ast.Constant):
                    return kw.value.value == "forbid"
    return False


def _has_model_validator(cls: ast.ClassDef) -> bool:
    for node in cls.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            func = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(func, ast.Name) and func.id == "model_validator":
                return True
    return False


def extract_contract() -> dict[str, object]:
    try:
        source = SCHEMA_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"nie można odczytać schematu backendu: {exc}") from exc

    classes = _classes(ast.parse(source))
    for name in (PACKET_CLASS, WINDOW_CLASS, POINT_CLASS, ERROR_CLASS):
        if name not in classes:
            raise ContractError(f"schemat backendu nie zawiera klasy {name}")

    packet = classes[PACKET_CLASS]
    window = classes[WINDOW_CLASS]
    point = classes[POINT_CLASS]
    error = classes[ERROR_CLASS]

    if not _forbids_extra(packet):
        raise ContractError(
            f"{PACKET_CLASS} nie ma już model_config = ConfigDict(extra='forbid') — "
            "kontrakt payloadu opiera się na tym, że nadmiarowe klucze są odrzucane"
        )

    packet_required, packet_optional, packet_fields = _split_fields(packet)
    window_required, window_optional, window_fields = _split_fields(window)
    point_required, point_optional, point_fields = _split_fields(point)
    error_required, error_optional, error_fields = _split_fields(error)

    if "severity" not in error_fields:
        raise ContractError(f"{ERROR_CLASS} nie ma pola severity")
    severities = _annotation_literals(error_fields["severity"].annotation)
    if not severities:
        raise ContractError(
            f"{ERROR_CLASS}.severity nie jest już Literal[...] — nie da się wygenerować listy poziomów"
        )

    # Każde pole, z którego czytamy ograniczenie, musi istnieć. Bez tej pętli
    # refaktor schematu kończyłby się KeyError-em i śladem stosu zamiast
    # zdaniem mówiącym, co dokładnie przestało pasować.
    for cls_name, fields, expected in (
        (PACKET_CLASS, packet_fields, ("v", "device_id", "windows")),
        (WINDOW_CLASS, window_fields, ("window_seconds", "points")),
        (POINT_CLASS, point_fields, ("point_id", "type", "unit", "quality")),
        (ERROR_CLASS, error_fields, ("code", "severity", "message")),
    ):
        missing = [name for name in expected if name not in fields]
        if missing:
            raise ContractError(
                f"{cls_name} nie ma już pól {missing} — generator kontraktu czyta z nich "
                f"ograniczenia i nie potrafi ich odtworzyć po zmianie schematu"
            )

    if "v" not in packet_fields:
        raise ContractError(f"{PACKET_CLASS} nie ma pola v (wersja protokołu)")
    v_min = _field_kwarg(packet_fields["v"].value, "ge")
    v_max = _field_kwarg(packet_fields["v"].value, "le")
    if v_min is None or v_max is None:
        raise ContractError(f"{PACKET_CLASS}.v nie ma już ograniczeń ge/le")

    if "window_seconds" not in window_fields:
        raise ContractError(f"{WINDOW_CLASS} nie ma pola window_seconds")
    window_seconds_gt = _field_kwarg(window_fields["window_seconds"].value, "gt")
    window_seconds_le = _field_kwarg(window_fields["window_seconds"].value, "le")
    if window_seconds_gt is None or window_seconds_le is None:
        raise ContractError(f"{WINDOW_CLASS}.window_seconds nie ma już ograniczeń gt/le")

    if not _has_model_validator(point):
        raise ContractError(
            f"{POINT_CLASS} nie ma już model_validator — reguła 'value albo agregat' "
            "przestała obowiązywać albo zmieniła formę"
        )

    return {
        "packet_required": packet_required,
        "packet_optional": packet_optional,
        "window_required": window_required,
        "window_optional": window_optional,
        "point_required": point_required,
        "point_optional": point_optional,
        "error_required": error_required,
        "error_optional": error_optional,
        "severities": severities,
        "v_min": int(v_min),
        "v_max": int(v_max),
        "window_seconds_gt": int(window_seconds_gt),
        "window_seconds_le": int(window_seconds_le),
        "min_windows": int(_field_kwarg(packet_fields["windows"].value, "min_length") or 0),
        "device_id_max": int(_field_kwarg(packet_fields["device_id"].value, "max_length") or 0),
        "point_id_max": int(_field_kwarg(point_fields["point_id"].value, "max_length") or 0),
        "message_max": int(_field_kwarg(error_fields["message"].value, "max_length") or 0),
        "point_aggregates": [name for name in ("avg", "min", "max") if name in point_fields],
    }


# --- generowanie nagłówka --------------------------------------------------


def _string_array(name: str, values: list[str]) -> str:
    if not values:
        return f"inline constexpr const char* const {name}[] = {{nullptr}};\ninline constexpr size_t {name}_COUNT = 0;"
    items = ", ".join(f'"{value}"' for value in values)
    return (
        f"inline constexpr const char* const {name}[] = {{{items}}};\n"
        f"inline constexpr size_t {name}_COUNT = {len(values)};"
    )


def render_header(contract: dict[str, object]) -> str:
    schema_rel = SCHEMA_PATH.relative_to(REPO_ROOT).as_posix()
    arrays = "\n\n".join(
        [
            _string_array("PACKET_REQUIRED", contract["packet_required"]),
            _string_array("PACKET_OPTIONAL", contract["packet_optional"]),
            _string_array("WINDOW_REQUIRED", contract["window_required"]),
            _string_array("WINDOW_OPTIONAL", contract["window_optional"]),
            _string_array("POINT_REQUIRED", contract["point_required"]),
            _string_array("POINT_OPTIONAL", contract["point_optional"]),
            _string_array("POINT_AGGREGATES", contract["point_aggregates"]),
            _string_array("ERROR_REQUIRED", contract["error_required"]),
            _string_array("ERROR_OPTIONAL", contract["error_optional"]),
            _string_array("ERROR_SEVERITIES", contract["severities"]),
        ]
    )

    return f"""#pragma once
//
// PLIK GENEROWANY — nie edytuj ręcznie.
// Źródło: {schema_rel} (MeasurementPacketRequest)
// Regeneracja: python3 firmware/scripts/generate_payload_contract.py
//
// Opisuje kształt pakietu telemetrycznego, jaki przyjmuje backend. Test
// kontraktowy (test/test_payload_contract.cpp) sprawdza payload zbudowany przez
// firmware względem tych tablic, dzięki czemu rozjazd z backendem wychodzi przy
// `pio test -e native`, a nie dopiero na produkcji.
//
// Kody błędów NIE są tu powielane — pochodzą z SensorRegistry.h, generowanego
// z tego samego sensor_registry.yaml, które backend ładuje w czasie działania.
//
#include <cstddef>

namespace PayloadContract {{

// Wersja protokołu akceptowana przez backend (MeasurementPacketRequest.v).
inline constexpr int V_MIN = {contract["v_min"]};
inline constexpr int V_MAX = {contract["v_max"]};

// Backend odrzuca pakiety z nadmiarowymi kluczami (ConfigDict(extra="forbid")).
inline constexpr bool FORBIDS_EXTRA_KEYS = true;

inline constexpr size_t MIN_WINDOWS = {contract["min_windows"]};
inline constexpr int WINDOW_SECONDS_MIN_EXCLUSIVE = {contract["window_seconds_gt"]};
inline constexpr int WINDOW_SECONDS_MAX = {contract["window_seconds_le"]};

inline constexpr size_t DEVICE_ID_MAX_LENGTH = {contract["device_id_max"]};
inline constexpr size_t POINT_ID_MAX_LENGTH = {contract["point_id_max"]};
inline constexpr size_t ERROR_MESSAGE_MAX_LENGTH = {contract["message_max"]};

// Punkt pomiarowy musi nieść `value` albo co najmniej jeden agregat
// (MeasurementPoint.validate_measurement_shape).
inline constexpr bool POINT_REQUIRES_VALUE_OR_AGGREGATE = true;

{arrays}

}}  // namespace PayloadContract
"""


def generate(check_only: bool = False) -> bool:
    try:
        contract = extract_contract()
    except ContractError as exc:
        print(f"❌ Kontrakt payloadu: {exc}", file=sys.stderr)
        return False

    rendered = render_header(contract)

    if check_only:
        if not HEADER_PATH.exists():
            print(f"❌ Brak {HEADER_PATH.relative_to(REPO_ROOT)} — uruchom generator", file=sys.stderr)
            return False
        current = HEADER_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print(
                f"❌ {HEADER_PATH.relative_to(REPO_ROOT)} jest nieaktualny względem schematu backendu. "
                "Uruchom: python3 firmware/scripts/generate_payload_contract.py",
                file=sys.stderr,
            )
            return False
        print("✅ Kontrakt payloadu zgodny ze schematem backendu")
        return True

    try:
        HEADER_PATH.parent.mkdir(parents=True, exist_ok=True)
        HEADER_PATH.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"❌ Nie udało się zapisać {HEADER_PATH}: {exc}", file=sys.stderr)
        return False

    print(f"✅ Wygenerowano {HEADER_PATH.relative_to(REPO_ROOT)}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="tylko sprawdź, czy zapisany nagłówek odpowiada schematowi backendu",
    )
    args = parser.parse_args()
    sys.exit(0 if generate(check_only=args.check) else 1)
