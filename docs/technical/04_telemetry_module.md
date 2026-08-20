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

**Per-device authentication** — każde `Device` ma unikalny `hashed_secret` generowany przy tworzeniu. Ingest weryfikuje `X-Device-Key` nagłówek wobec tego sekretu ([`services/ingest.py:31-48`](../../backend/app/modules/telemetry/services/ingest.py#L31-L48)) zamiast globalnego klucza. Zwraca `401` dla nieznanego urządzenia (`device_id` nie istnieje), `403` dla błędnego klucza lub nieaktywnego urządzenia (`is_active=False`).

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

