# `sensor_registry.yaml` jest jedynym źródłem prawdy dla typów punktów i kodów błędów — i tylko dla nich

Firmware i backend czerpią listę `point_types` oraz `error_codes` z jednego pliku YAML w katalogu głównym repozytorium. Reszta kontraktu pakietu telemetrycznego (koperta, jednostki, wartości `quality`, `severity` konkretnego błędu) źródłem prawdy objęta **nie** jest.

## Status
Proposed

## Kontekst
Backend ładuje rejestr przy starcie i waliduje nim ingest ([`registry.py`](../../../backend/app/modules/core_data/registry.py), [`ingest.py:47-52`](../../../backend/app/modules/telemetry/services/ingest.py#L47-L52), [`measurement_packet.py:50-59`](../../../backend/app/modules/telemetry/schemas/measurement_packet.py#L50-L59)). Firmware dostaje wygenerowany `SensorRegistry.h` — hook pre-build jest aktywny w [`platformio.ini`](../../../firmware/platformio.ini) i przerywa kompilację przy rozjeździe; wygenerowany nagłówek jest świadomie wykluczony z repozytorium (`.gitignore`).

## Decyzja
Rejestr obejmuje trzy rzeczy: `schema_version`, identyfikatory typów punktów i kody błędów. Skrypt weryfikacyjny porównuje dokładnie te trzy zbiory ([`prebuild.py`](../../../firmware/scripts/prebuild.py)) — dodanie pola do YAML nie rozszerza kontraktu automatycznie.

## Gdzie kończy się reguła
- **`canonical_unit` z YAML nie jest nigdzie egzekwowane.** Backend przyjmuje dowolny `unit` (`String(min_length=1, max_length=32)`) i zapisuje go w `measurement_points` przy autoprovisioningu ([ADR-0012](0012-autoprovisioning-punktow-pomiarowych.md)). Rozjazd jednostek między urządzeniami tego samego typu jest dziś możliwy.
- **`severity` przypisane w YAML do kodu błędu nie jest weryfikowane przy ingeście** — schemat sprawdza tylko, że wartość należy do `{info, warning, critical}`; urządzenie może zgłosić `SENSOR_READ_FAILED` z dowolną powagą.
- **Wartości `quality` nie są w rejestrze w ogóle.** `quality` to wolny string, a logika statusu obiektu porównuje go z literałem `"good"` ([`query.py:101`](../../../backend/app/modules/telemetry/services/query.py#L101)) — literówka w firmware oznacza obiekt trwale w stanie `warning`.
- **Koperta pakietu (`v`, `seq`, `windows`, `errors`) jest opisana wyłącznie w schemacie Pydantica**, po stronie backendu; firmware ma ją zaszytą w kodzie.

Rozszerzenie rejestru o którykolwiek z tych elementów jest osobną decyzją, nie doprecyzowaniem tej.
