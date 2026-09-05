# `sensor_registry.yaml` jest jedynym źródłem prawdy dla identyfikatorów typów i kodów błędów — i tylko dla nich

Jeden plik YAML w korzeniu repozytorium definiuje listę `point_types` i `error_codes`. Backend ładuje go w runtime (`SensorRegistry.initialize()` przy starcie), firmware dostaje go jako **generowany** nagłówek `firmware/include/SensorRegistry.h` z osadzonym JSON-em i walidatorami `constexpr`. Nagłówek jest w `.gitignore` — powstaje przy każdym buildzie, nie jest wersjonowany.

## Status

Proposed

## Kontekst

Backend i firmware muszą znać identyczne listy. Ręczna synchronizacja dwóch list w dwóch językach kończy się rozjazdem, którego nikt nie zauważy do momentu, aż urządzenie w terenie wyśle typ, którego backend nie zna.

## Decyzja

- YAML jest źródłem, kod jest pochodną. Nagłówek C++ **generuje się**, a nie pisze — dlatego jest ignorowany przez gita: gdyby był commitowany, mógłby się rozjechać z YAML-em.
- Backend waliduje `point_type` przy ingeście i przy ręcznym tworzeniu punktu; kod błędu waliduje walidator Pydantica na schemacie pakietu.
- Firmware waliduje **w czasie kompilacji**: `static_assert(SensorRegistry::isValidPointType("temperature"))` — czujnik używający niezarejestrowanego typu nie skompiluje się.
- Hook pre-build PlatformIO generuje nagłówek i porównuje `schema_version`, `point_types` i `error_codes` z YAML-em; niezgodność przerywa build.

## Gdzie ta reguła się kończy

To najważniejsza część tego ADR-a, bo nazwa „single source of truth" sugeruje więcej, niż registry faktycznie pilnuje:

| Element | Kontrolowany? |
|---|---|
| identyfikatory `point_type` | ✅ backend (runtime) + firmware (compile-time) |
| kody błędów | ✅ backend + firmware |
| **`canonical_unit`** | ❌ nie — `unit` z pakietu jest przyjmowany jako dowolny napis 1–32 znaków i zapisywany do bazy |
| **kształt payloadu** (`v`, `windows`, `points`, nazwy pól) | ❌ nie — schemat żyje osobno w `measurement_packet.py` i w kodzie firmware |
| `severity` kodu błędu | ❌ nie — urządzenie przysyła własną, registry ma własną, nikt ich nie porównuje |

Czyli: registry uzgadnia **słownik**, nie **protokół**.

## Konsekwencje

- Dodanie typu czujnika to jedna zmiana w YAML-u i rebuild firmware'u — bez dotykania kodu obu stron.
- `SensorRegistry.h` nie istnieje na świeżym klonie, dopóki nie odpali się generatora. Dotyczy to także testów natywnych, które ten nagłówek `#include`-ują.
- Urządzenie może zgłosić `type: temperature, unit: "F"` i backend to przyjmie, mimo że `canonical_unit` mówi `°C`. Rozbieżność wyjdzie dopiero jako `POINT_TYPE_MISMATCH` przy **drugim** pakiecie z innym `unit` — bo pierwszy ustawi punkt pomiarowy na tę wartość przez auto-provisioning.
