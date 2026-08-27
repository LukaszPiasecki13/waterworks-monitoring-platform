# Moduł `telemetry`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`telemetry` przyjmuje pakiety pomiarowe z gatewayów terenowych i wystawia zapytania szeregów czasowych dla dashboardu. Dwie wyraźnie oddzielone ścieżki: **ingest** (write, autoryzacja kluczem urządzenia, `/telemetry/ingest`) i **query** (read, autoryzacja JWT, `/api/v1/orgs/{org_id}/telemetry/...`).

## 2. Model domenowy

`TelemetryPacket` — jeden wiersz na paczkę danych wysłaną przez gateway: `device_id` (external_id urządzenia, nie FK), `seq` (numer sekwencyjny nadawany przez firmware), `sent_at`, `received_at`, `payload` (JSONB z `windows`: oknami pomiarowymi zawierającymi punkty). Powiązanie z `core_data.Device` / `WaterObject` / `Organization` odbywa się przez `device_id`/`external_id`, odczytywane w zapytaniach repozytorium query-side, nie przez ORM relationship.

## 3. Kluczowe reguły i niezmienniki

**Dedupe po `(device_id, seq)`** — unikalny constraint w bazie (`uq_telemetry_packets_device_seq`). `TelemetryPacketRepository.create` robi `flush()` (nie `commit()`) właśnie po to, żeby złapać naruszenie unikalności tu, przetłumaczyć je na `TelemetryPacketAlreadyExistsError`, i pozwolić serwisowi odpowiedzieć klientowi `200 duplicate` zamiast błędu — gateway, który retransmituje pakiet po utracie łączności przed potwierdzeniem, nie dostaje błędu za coś, co już się udało.

**Status obiektu** liczony w `TelemetryQueryService._compute_status`:
- `no_data` — obiekt nigdy nie zgłosił pakietu
- `no_comm` — ostatni kontakt starszy niż `settings.telemetry_stale_after_seconds`
- `warning` — którykolwiek punkt ma `quality != "good"`
- `ok` — wszystko inne

**`MAX_PACKETS_PER_SERIES = 5000`** (limit na `limit` w zapytaniu measurements) — górna granica pakietów skanowanych w jednym zapytaniu szeregu czasowego, żeby szeroki zakres czasowy nie ściągnął nieograniczonego wyniku do pamięci procesu.

## 4. Nieoczywiste decyzje projektowe

**Per-device authentication przez bearer token** — zastąpiło wcześniejszy statyczny `X-Device-Key`/`Device.hashed_secret` (usunięty całkowicie). Ingest wymaga `Authorization: Bearer <device_token>`, zweryfikowanego przez zależność `get_current_device` z modułu [`device_identity`](./06_device_identity_module.md) — token wydawany po asymetrycznym challenge/response, nie po statycznym sekrecie. `get_current_device` zwraca `401` dla brakującego/nieprawidłowego tokenu i nieaktywnego urządzenia (`is_active=False`). Dodatkowo `TelemetryIngestService.ingest()` sprawdza `packet.device_id == device.external_id` ([`services/ingest.py:31-34`](../../backend/app/modules/telemetry/services/ingest.py#L31-L34)) → `403` przy niezgodności, żeby ważny token jednego urządzenia nie mógł podszyć się pod inny SN w treści pakietu. Pełny opis flow (provisioning → claim → challenge → verify) w [`06_device_identity_module.md`](./06_device_identity_module.md).

**`transaction(skip_audit=True)` na ingest** — pakiety telemetryczne to dane z urządzenia IoT, nie zmiana wywołana przez użytkownika, więc nie generują wpisu w audit logu (który śledzi "kto co zmienił", nie strumień pomiarowy).

**Window function zamiast agregatu do wyznaczenia "najnowszego pakietu na obiekt"** ([`queries.py:20-48`](../../backend/app/modules/telemetry/repositories/queries.py#L20-L48)):

```python
func.row_number().over(
    partition_by=WaterObject.id,
    order_by=TelemetryPacket.received_at.desc(),
)
```

Komentarz w kodzie tłumaczy dlaczego nie `MAX(device_id)`: zwróciłby leksykograficznie największy `external_id`, niekoniecznie urządzenie, które faktycznie zgłosiło się ostatnie — i mógłby sparować go z `received_at` z zupełnie innego pakietu.

**`get_latest_packets` pobiera całą stronę jednym zapytaniem** — `_summarize` w serwisie woła to raz dla wszystkich obiektów strony, zamiast N+1 zapytań (jedno na obiekt). `get_latest_packet` (liczba pojedyncza) to cienki wrapper wołający tę samą metodę z listą jednoelementową — nie duplikuje logiki SQL.

**`limit=None` w `list_objects`** — repozytorium wspiera zwrócenie kompletnego zbioru bez limitu, bo serwis czasem filtruje po statusie (`no_data`/`no_comm`/`warning`/`ok`), którego nie da się wyrazić w SQL bez dodatkowego joina na "ostatni pakiet" — więc musi mieć cały zbiór przed paginacją.

## 5. Pakiet v2 — batchowanie i wieloczujniki

Firmware v2 i dalej wysyła pakiety w formacie `/telemetry/ingest` (`POST`):

```json
{
  "v": 2,
  "device_id": "WW-xxx",
  "seq": 123,
  "sent_at": "2026-08-26T10:30:00.000Z",
  "windows": [
    {
      "window_start": "2026-08-26T10:30:00.000Z",
      "window_seconds": 15,
      "points": [
        {
          "point_id": "pt100_temperature",
          "type": "temperature",
          "unit": "°C",
          "quality": "good",
          "value": 23.5
        },
        {
          "point_id": "pressure_transducer",
          "type": "pressure",
          "unit": "bar",
          "quality": "good",
          "value": 2.1
        }
      ]
    },
    {
      "window_start": "2026-08-26T10:30:15.000Z",
      "window_seconds": 15,
      "points": [...]
    }
  ],
  "errors": [
    {
      "code": "SENSOR_FAULT_HW",
      "point_id": "pt100_temperature",
      "severity": "critical",
      "message": "MAX31865 fault bits detected"
    }
  ]
}
```

**Batchowanie okien**: Firmware próbkuje co `SAMPLE_INTERVAL_MS` (15s), ale wysyła co `SAMPLE_INTERVAL_MS * WINDOWS_PER_BATCH` (np. 4 okna × 15s = 60s), zmniejszając narzut TLS/HTTP. Bufor retencji `RETAIN_WINDOWS_MAX = 12 × WINDOWS_PER_BATCH` (12 minut) chroni przed stratą danych przy długotrwałej utracie łączności — zwiększony z 3 minut aby wspierać sieciowe outage'e dłuższe niż 3 minuty.

**Wieloczujniki**: `points[]` zawiera teraz jeden wpis na każdy aktywny czujnik urządzenia. Firmware implementuje `ISensor` interface; dodanie nowego czujnika = nowa klasa + wpis w `sensor_registry.yaml`, bez zmian w rdzeniu `TelemetryPayload`.

**Błędy**: Pole `errors[]` (opcjonalne, domyślnie puste) przenosi kody błędów z firmware (sensor, device, modem), a backend może dodać własne (`POINT_TYPE_MISMATCH` itp.). Zapisywane w tabeli `telemetry_errors` z indeksem `(device_id, code, occurred_at)` dla filtrowania "pokaż urządzenia z błędem X".

**Auto-provisioning**: `TelemetryIngestService.ingest()` przy widoku nieznanego `(device_id, point_id)` — jeśli `type` jest w katalogu (`point_types.yaml`) — tworzy `MeasurementPoint` bez interakcji użytkownika. Mismatch `(type, unit)` dla istniejącego punktu zwraca `POINT_TYPE_MISMATCH` w `errors[]`, punkt jest odrzucany z tego pakietu, reszta przetwarzana normalnie. Typ spoza katalogu → `400` na cały pakiet (to błąd firmware/rejestru).

**`Device.last_diagnostics_at`**: Zaktualizowany po każdym ingest'cie zawierającym `errors[]`, niezależnie od statusu — sygnał, że urządzenie jest żywe i raportuje problemy.

## 6. Sensor Registry: Single Source of Truth

Firmware i backend muszą znać identyczne listy `point_types` i `error_codes`. Rozwiązanie: plik [`sensor_registry.yaml`](../../sensor_registry.yaml) w project root — single source of truth dla obu systemów.

**Struktura** (`sensor_registry.yaml`):
```yaml
schema_version: 1

point_types:
  - id: temperature
    canonical_unit: "°C"
  - id: pressure
    canonical_unit: "bar"

error_codes:
  - code: SENSOR_FAULT_HW
    severity: critical
  - code: SENSOR_READ_FAILED
    severity: warning
```

**Backend** — runtime loading [`backend/app/modules/core_data/registry.py`](../../backend/app/modules/core_data/registry.py):
- App startup wołuje `SensorRegistry.initialize()` — ładuje, parsuje, waliduje YAML
- Builds immutable `frozenset` cache dla O(1) lookups (`is_valid_point_type()`, `is_valid_error_code()`)
- Thread-safe: lock synchronizuje inicjalizację

**Firmware** — compile-time validation:
- Pre-build script [`firmware/scripts/prebuild.py`](../../firmware/scripts/prebuild.py) generuje `firmware/include/SensorRegistry.h`
- Zawiera embedded JSON + `static constexpr` validatory
- Schema version mismatch = build error (nie można zabootować buggy firmware)

**Synchronizacja**: Pre-build script weryfikuje `point_types` i `error_codes` w firmware vs backend, fails if mismatch. Rezultat: oba są zawsze synced — brak duplikacji, brak ręcznej synchronizacji.

