# Moduł `telemetry`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`telemetry` przyjmuje pakiety pomiarowe z gatewayów terenowych i wystawia zapytania szeregów czasowych dla dashboardu. Dwie wyraźnie oddzielone ścieżki: **ingest** (write, autoryzacja kluczem urządzenia, `/telemetry/ingest`) i **query** (read, autoryzacja JWT, `/api/v1/orgs/{org_id}/telemetry/...`).

## 2. Model domenowy

Pakiet zapisuje się w **dwóch** miejscach, o rozłącznych rolach:

`TelemetryPacket` (`telemetry_packets`) — jeden wiersz na paczkę danych wysłaną przez gateway: `device_id` (external_id urządzenia, nie FK), `seq` (numer sekwencyjny nadawany przez firmware), `sent_at`, `received_at`, `payload` (JSONB z `windows`: oknami pomiarowymi zawierającymi punkty). Powiązanie z `core_data.Device` / `WaterObject` / `Organization` odbywa się przez `device_id`/`external_id`, odczytywane w zapytaniach repozytorium query-side, nie przez ORM relationship. **To jest ścieżka audytu i replay** — blob zostaje nienaruszony, żaden odczyt aplikacyjny go nie parsuje.

`Measurement` ([`models/measurement.py`](../../backend/app/modules/telemetry/models/measurement.py), tabela `measurements`) — jeden wiersz na *(punkt pomiarowy, okno)*: `measurement_point_id` (FK → `measurement_points.id`, `ON DELETE CASCADE`), `window_start`, `window_seconds`, `avg`/`min`/`max`, `value`, `value_bool`, `quality`, `received_at`, `source_packet_id`. **To jest ścieżka odczytu** — dashboard, historia, wykresy, a docelowo alarmy (Etap 5) i eksport CSV (Etap 7).

| Decyzja | Uzasadnienie |
|---|---|
| **Klucz główny `(measurement_point_id, window_start)`**, bez kolumny `id` | To jest naturalny klucz (punkt nie ma dwóch wartości dla tego samego okna). Daje idempotencję zapisu, indeks pod zapytania zakresowe i klucz zawierający kolumnę partycjonującą — czego PostgreSQL wymaga od tabeli partycjonowanej. Trzy rzeczy za darmo zamiast trzech osobnych obiektów. |
| **`value` (liczba) i `value_bool` (flaga) w osobnych kolumnach** | Schemat pakietu dopuszcza `float \| int \| bool \| None` ([`measurement_packet.py:21`](../../backend/app/modules/telemetry/schemas/measurement_packet.py#L21)). Gdyby `digital_input`/`power_status` lądowały jako `0.0`/`1.0` w `value`, reguła progowa z Etapu 5 porównywałaby próg z zakodowaną flagą, a API zwracałoby `1.0` zamiast `true`. `CHECK (value IS NULL OR value_bool IS NULL)` pilnuje, że wypełniona jest najwyżej jedna. |
| **`source_packet_id` bez klucza obcego** | Celowo. Retencja blobów (osobne zadanie) musi móc kasować pakiety bez kaskady na pomiary, a nieindeksowany FK kazałby PostgreSQL skanować `measurements` przy każdym kasowanym pakiecie. Wiszące id znaczy „blob już wyczyszczony". |
| **`window_start` normalizowany do UTC przy zapisie** | `window_start` to połowa klucza głównego — ten sam moment przysłany z innym offsetem (albo bez offsetu) musi trafić w jeden wiersz i w partycję właściwego miesiąca. |

## 3. Kluczowe reguły i niezmienniki

**Dedupe po `(device_id, seq)`** — unikalny constraint w bazie (`uq_telemetry_packets_device_seq`). `TelemetryPacketRepository.create` robi `flush()` (nie `commit()`) właśnie po to, żeby złapać naruszenie unikalności tu, przetłumaczyć je na `TelemetryPacketAlreadyExistsError`, i pozwolić serwisowi odpowiedzieć klientowi `200 duplicate` zamiast błędu — gateway, który retransmituje pakiet po utracie łączności przed potwierdzeniem, nie dostaje błędu za coś, co już się udało.

**Druga, niezależna idempotencja: `(measurement_point_id, window_start)`** — zapis do `measurements` idzie przez `INSERT ... ON CONFLICT DO NOTHING` ([`repositories/measurements.py`](../../backend/app/modules/telemetry/repositories/measurements.py)). Dedupe pakietowy nie wystarcza: gateway, który po odzyskaniu łączności wysyła zbuforowane okna pod **nowym** `seq`, przechodzi przez kontrolę `(device_id, seq)` i dopiero constraint na pomiarze zatrzymuje duplikat. Ta sama właściwość pozwala backfillowi biec na żywym systemie — nie ma znaczenia, kto zapisał okno pierwszy.

**Punkt z niezgodnym `(type, unit)` nie jest normalizowany** — `POINT_TYPE_MISMATCH` trafia do `errors[]`, punkt jest pomijany przy zapisie do `measurements`, reszta pakietu przetwarzana normalnie. Wartość w jednostce sprzecznej z zarejestrowanym punktem zatruwałaby każdy wykres i każdy próg, który ją potem przeczyta; blob i tak zachowuje ją do replay.

**Status obiektu** liczony w `TelemetryQueryService._compute_status`:
- `no_data` — obiekt nigdy nie zgłosił pakietu
- `no_comm` — ostatni kontakt starszy niż `settings.telemetry_stale_after_seconds`
- `warning` — którykolwiek punkt ma `quality != "good"`
- `ok` — wszystko inne

**`limit` w zapytaniach szeregów czasowych** (domyślnie 1000, maksymalnie 5000) — repozytorium pobiera `limit + 1` wierszy i na tej podstawie ustawia `truncated` w odpowiedzi, żeby klient odróżnił kompletny szereg od uciętego, bez drugiego zapytania zliczającego. Przed normalizacją limit dotyczył **pakietów** skanowanych z JSONB (`MAX_PACKETS_PER_SERIES`); teraz dotyczy **pomiarów**, bo zapytanie schodzi po indeksie `(measurement_point_id, window_start)` zamiast rozpakowywać blob w pamięci procesu.

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

**Podział odczytów między dwie tabele** — `TelemetryQueryService` czyta fakty *pakietowe* (kiedy urządzenie ostatnio się odezwało, pod jakim `seq`) z `telemetry_packets` przez [`queries.py`](../../backend/app/modules/telemetry/repositories/queries.py), a wszystko o samych pomiarach z `measurements` przez [`measurements.py`](../../backend/app/modules/telemetry/repositories/measurements.py). „Ostatni kontakt" to własność transmisji, nie pomiaru — urządzenie może zgłosić się z pakietem, w którym każdy punkt zostanie odrzucony, i nadal jest to kontakt. Żaden odczyt nie parsuje `payload`.

**Najświeższy pomiar per punkt bez rankowania historii** — `latest_for_objects` łączy się z `measurements` po `window_start = (SELECT max(window_start) ... WHERE measurement_point_id = ...)`. Obie połowy jadą po kluczu głównym `(measurement_point_id, window_start)`: podzapytanie czyta maksimum z indeksu, join trafia w dokładnie ten wiersz. Poprzednia wersja rankowała `row_number()` po wszystkich pakietach obiektu, więc jej koszt rósł z liczbą przechowywanych pakietów.

**`available_points` z rejestru punktów, nie ze skanu telemetrii** — punkt istnieje dokładnie dlatego, że urządzenie go zgłosiło (auto-provisioning) albo operator go założył; przekopywanie ostatnich 100 pakietów, żeby odtworzyć tę samą listę, było pracą do wyrzucenia. Zapytanie odsiewa jednak punkty **bez ani jednego pomiaru** (`EXISTS`, jedna sonda po indeksie na punkt): lista odpowiada na pytanie „co da się wykreślić", a punkt założony ręcznie i nigdy niepodłączony dałby klientowi pustą serię.

**Zapis dzielony na porcje mieszczące się w limicie parametrów** — jeden wielowierszowy `INSERT` niesie jeden parametr bindowania na kolumnę na wiersz, a backendy to limitują (PostgreSQL 65535 parametrów protokołu, SQLite `SQLITE_MAX_VARIABLE_NUMBER`). Jedna paczka backfillu (500 pakietów × 4 okna × 3 czujniki = 6000 wierszy) przekracza ten limit, więc repozytorium tnie zapis na porcje wyliczone z `dialect.insertmanyvalues_max_parameters` i liczby kolumn modelu — dodanie kolumny albo zmiana backendu nie wypchnie paczki poza limit po cichu.

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

## 6. Endpointy odczytu

| Endpoint | Zwraca |
|---|---|
| `GET /api/v1/orgs/{org_id}/telemetry/objects` | Lista obiektów: status, ostatni kontakt (z `telemetry_packets`), najświeższy odczyt każdego punktu (z `measurements`) |
| `GET /api/v1/orgs/{org_id}/telemetry/objects/{object_id}` | Szczegóły obiektu + `available_points` (aktywne punkty obiektu, które mają jakikolwiek pomiar) |
| `GET /api/v1/orgs/{org_id}/telemetry/objects/{object_id}/measurements?point_id=&type=&start=&end=&limit=` | Szereg czasowy całego obiektu |
| `GET /api/v1/orgs/{org_id}/telemetry/points/{point_id}/measurements?from=&to=&limit=` | Historia **jednego** punktu pomiarowego |

Wszystkie chronione `CAN_VIEW_ASSETS` przez `require_org_access`; izolacja organizacji jest częścią routingu (`org_id` w ścieżce), a dodatkowo serwis potwierdza przynależność obiektu/punktu do organizacji i zwraca `404` (nie `403`) dla cudzych zasobów — brak potwierdzenia istnienia.

Każda pozycja szeregu **zawsze** ma `window_start` i `quality`: szereg bez znacznika czasu i bez informacji, czy czujnik ufał wartości, nie nadaje się ani na wykres, ani do eksportu. Brak `end`/`to` w zapytaniu kotwiczy zakres na najświeższym pomiarze (nie na „teraz"), żeby obiekt, który przestał nadawać, nadal pokazał swoją ostatnią dobę danych; brak `start`/`from` cofa o 24 h.

## 7. Partycjonowanie `measurements`

Tabela jest tworzona jako `PARTITION BY RANGE (window_start)`, z partycjami miesięcznymi (`measurements_YYYY_MM`) i partycją `measurements_default` jako siatką bezpieczeństwa. Powód wprowadzenia od razu, na pustej tabeli: [`01_plan_biznesowy.md` §3.8.2–3.8.3](../../business/01_plan_biznesowy.md) szacuje ~1,6 mln rekordów pomiarowych rocznie na obiekt i ~23,4 mln dla gminy 15-obiektowej — przepartycjonowanie tabeli przy takim wolumenie kosztuje dużo więcej niż zrobienie tego teraz.

**Partycje nie są tworzone przez migrację.** Alembic zna tylko schemat bieżącej rewizji, a zbiór partycji jest ruchomy, więc utrzymuje go [`repositories/partitions.py`](../../backend/app/modules/telemetry/repositories/partitions.py):

- **przy starcie aplikacji** (`lifespan` w `main.py`) — 1 miesiąc wstecz i 12 miesięcy w przód, idempotentnie (`CREATE TABLE IF NOT EXISTS`),
- **w skrypcie backfillu** — dla miesięcy, w których faktycznie są dane historyczne,
- **ręcznie**: `python -m app.cli ensure-measurement-partitions [--months-ahead N]`.

Każde `CREATE TABLE ... PARTITION OF` idzie we własnym savepoincie: nieudane utworzenie jednej partycji (np. bo w partycji domyślnej leżą już wiersze z tego zakresu) trafia do logu ostrzeżeniem i nie psuje reszty transakcji. Na dialekcie innym niż PostgreSQL i na niepartycjonowanej tabeli funkcja jest no-opem — dlatego testy jednostkowe modułu chodzą na SQLite.

Partycje są niewidoczne dla `alembic revision --autogenerate`, bo `include_name` w [`alembic/env.py`](../../backend/alembic/env.py) przepuszcza wyłącznie tabele z metadanych ORM — autogenerate nie zaproponuje ich skasowania.

## 8. Backfill danych historycznych

[`scripts/backfill_measurements.py`](../../backend/scripts/backfill_measurements.py) przepisuje istniejące bloby z `telemetry_packets` do `measurements`. Zaprojektowany pod uruchomienie na żywym systemie, bez okna serwisowego:

- **addytywny** — nie modyfikuje ani nie kasuje żadnego pakietu,
- **batchowany** — jedna transakcja na paczkę pakietów (`--batch-size`, domyślnie 500); sam zapis dzieli się dodatkowo na porcje mieszczące się w limicie parametrów bindowania bazy, więc większy `--batch-size` nie wysadzi instrukcji,
- **wznawialny** — kursor `(received_at, packet_id)` zapisywany do pliku stanu po każdym zacommitowanym batchu; `--restart` zaczyna od początku,
- **idempotentny** — wstawia przez ten sam `ON CONFLICT DO NOTHING`, więc ponowne uruchomienie (albo wyścig z żywym ingestem) nie tworzy duplikatów,
- **raportujący** — na końcu: ile pakietów, ile wierszy wstawionych, ile już było, ile punktów odrzuconych i z jakiego powodu (`unknown_device`, `unknown_point`, `point_type_mismatch`, `malformed_window`, `malformed_point`).

Skrypt **nie zakłada** brakujących `MeasurementPoint` — punkt usunięty przez operatora ma pozostać usunięty; takie pomiary lądują w raporcie jako `unknown_point`, a nie w bazie. `--dry-run` pokazuje, co by zrobił, nie zapisując nic.

Kolejność wdrożenia (bez zatrzymywania przyjmowania telemetrii): migracja schematu → restart aplikacji (partycje + zapis do `measurements` przy ingescie) → backfill → odczyty już czytają z nowej tabeli.

## 9. Sensor Registry: Single Source of Truth

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

