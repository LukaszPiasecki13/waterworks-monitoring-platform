# Moduł `telemetry`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`telemetry` przyjmuje pakiety pomiarowe z gatewayów terenowych i wystawia zapytania szeregów czasowych dla dashboardu. Dwie wyraźnie oddzielone ścieżki: **ingest** (write, autoryzacja kluczem urządzenia) i **query** (read, autoryzacja JWT).

## 2. Struktura

```text
modules/telemetry/
├─ api/
│  ├─ ingest.py      # POST /telemetry/ingest, montowany bez /api/v1
│  └─ query.py        # GET /telemetry/objects..., montowany pod /api/v1
├─ models/
│  └─ measurement_packet.py   # TelemetryPacket
├─ repositories/
│  ├─ packets.py       # write-side: exists_by_device_seq, create
│  └─ queries.py        # read-side: list_objects, get_latest_packets, get_packets_in_range
├─ schemas/
├─ services/
│  ├─ ingest.py
│  └─ query.py
└─ tests/
```

## 3. Model domenowy

`TelemetryPacket` — jeden wiersz na paczkę danych wysłaną przez gateway: `device_id` (external_id urządzenia, nie FK), `seq` (numer sekwencyjny nadawany przez firmware), `sent_at`, `received_at`, `payload` (JSONB z `windows`: oknami pomiarowymi zawierającymi punkty). Powiązanie z `core_data.Device` / `WaterObject` / `Organization` odbywa się przez `device_id`/`external_id`, odczytywane w zapytaniach repozytorium query-side, nie przez ORM relationship.

## 4. Endpointy API

| Metoda | Ścieżka | Montaż | Auth | Opis |
|---|---|---|---|---|
| POST | `/telemetry/ingest` | bez prefiksu | `X-Device-Key` (nagłówek, `verify_telemetry_ingest_key`) | Przyjmuje jeden pakiet pomiarowy; `202`, albo `200` jeśli duplikat |
| GET | `/api/v1/telemetry/objects` | `/api/v1` | JWT (`get_current_user`) | Lista monitorowanych obiektów z ostatnim odczytem i statusem; filtry `org_id`, `status`, paginacja |
| GET | `/api/v1/telemetry/objects/{object_id}` | `/api/v1` | JWT | Szczegóły obiektu + dostępne punkty pomiarowe |
| GET | `/api/v1/telemetry/objects/{object_id}/measurements` | `/api/v1` | JWT | Szereg czasowy; filtry `point_id`, `type`, `start`/`end` (domyślnie ostatnie 24h), `limit` (max 5000) |

## 5. Kluczowe reguły i niezmienniki

**Dedupe po `(device_id, seq)`** — unikalny constraint w bazie (`uq_telemetry_packets_device_seq`). `TelemetryPacketRepository.create` robi `flush()` (nie `commit()`) właśnie po to, żeby złapać naruszenie unikalności tu, przetłumaczyć je na `TelemetryPacketAlreadyExistsError`, i pozwolić serwisowi odpowiedzieć klientowi `200 duplicate` zamiast błędu — gateway, który retransmituje pakiet po utracie łączności przed potwierdzeniem, nie dostaje błędu za coś, co już się udało.

**Status obiektu** liczony w `TelemetryQueryService._compute_status`:
- `no_data` — obiekt nigdy nie zgłosił pakietu
- `no_comm` — ostatni kontakt starszy niż `settings.telemetry_stale_after_seconds`
- `warning` — którykolwiek punkt ma `quality != "good"`
- `ok` — wszystko inne

**`MAX_PACKETS_PER_SERIES = 5000`** (limit na `limit` w zapytaniu measurements) — górna granica pakietów skanowanych w jednym zapytaniu szeregu czasowego, żeby szeroki zakres czasowy nie ściągnął nieograniczonego wyniku do pamięci procesu.

## 6. Nieoczywiste decyzje projektowe

**`transaction(skip_audit=True)` na ingest** — pakiety telemetryczne to dane z urządzenia IoT, nie zmiana wywołana przez użytkownika, więc nie generują wpisu w audit logu (który śledzi "kto co zmienił", nie strumień pomiarowy).

**Window function zamiast agregatu do wyznaczenia "najnowszego pakietu na obiekt"** ([`queries.py:28-54`](../../backend/app/modules/telemetry/repositories/queries.py#L28-L54)):

```python
func.row_number().over(
    partition_by=WaterObject.id,
    order_by=TelemetryPacket.received_at.desc(),
)
```

Komentarz w kodzie tłumaczy dlaczego nie `MAX(device_id)`: zwróciłby leksykograficznie największy `external_id`, niekoniecznie urządzenie, które faktycznie zgłosiło się ostatnie — i mógłby sparować go z `received_at` z zupełnie innego pakietu.

**`get_latest_packets` pobiera całą stronę jednym zapytaniem** — `_summarize` w serwisie woła to raz dla wszystkich obiektów strony, zamiast N+1 zapytań (jedno na obiekt). `get_latest_packet` (liczba pojedyncza) to cienki wrapper wołający tę samą metodę z listą jednoelementową — nie duplikuje logiki SQL.

**`limit=None` w `list_objects`** — repozytorium wspiera zwrócenie kompletnego zbioru bez limitu, bo serwis czasem filtruje po statusie (`no_data`/`no_comm`/`warning`/`ok`), którego nie da się wyrazić w SQL bez dodatkowego joina na "ostatni pakiet" — więc musi mieć cały zbiór przed paginacją.

## 7. Zależności międzymodułowe

- Czyta modele `Device`, `WaterObject`, `Organization` z `core_data` (przez własne repozytorium `TelemetryQueryRepository`, nie przez serwisy `core_data` — jedyne miejsce w kodzie, gdzie odczyt przekracza granicę modułu poza warstwą serwisów, uzasadnione tym, że to zapytania czysto agregujące/raportowe, nie mutacje)
- `query.py` (API) wymaga `security.dependencies.get_current_user`
- `ingest.py` (API) wymaga `verify_telemetry_ingest_key` z własnego `dependencies.py` modułu (klucz statyczny z konfiguracji, nie per-urządzenie — `03_plan_wdrozenia_backend_mvp.md` w `docs/business/` opisuje plan przejścia na klucz per-device)

## 8. Testowanie

`tests/unit/` pokrywa logikę statusu i rozpakowywanie payloadu JSONB bez bazy danych (mockowane repozytorium). `tests/integration/` (`test_ingest_api.py`, `test_query_api.py`, `test_query_security.py`) — pełny flow przez `TestClient`, w tym dedupe (dwukrotny POST tego samego `seq` → `200 duplicate`, nie błąd) i guard `401` bez `X-Device-Key`/tokenu.
