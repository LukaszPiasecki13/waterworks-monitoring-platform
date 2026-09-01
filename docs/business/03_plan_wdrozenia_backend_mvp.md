# Plan wdrożenia backendu — MVP krok po kroku

**Dokument towarzyszący:** `01_plan_biznesowy.md`, `../technical/backend/01_backend-architecture.md`
**Data:** 2026-08-09 (Etapy 1–4: zrealizowane, stan opisu zaktualizowany 2026-08-30 — patrz [rozdział 1](#1-stan-wyjściowy-co-już-jest-zbudowane))
**Zakres:** wyłącznie backend (`backend/`). Frontend jest osobnym torem prac i nie jest tu opisany (ma już własną, nieudokumentowaną tu implementację — dashboard, devices, objects, groups, settings).

---

## 0. Zasady tego planu

- Każdy nowy moduł/encja stosuje **dokładnie** wzorzec z `../technical/backend/01_backend-architecture.md` i istniejącego modułu `core_data/users`: `api/ → services/ → repositories/ → infrastructure`, sync `Session` SQLAlchemy, `SQLRepository` jako baza repozytorium, serwisy przyjmują zależności przez `__init__` (bez `Depends()` w środku), transakcje (`commit`/`rollback`) prowadzi serwis (wyjątek: `telemetry` — tam repozytorium samo commituje, bo to zapis o wysokiej częstotliwości bez logiki biznesowej).
- Każda nowa tabela: model w `models/`, rejestracja w `app/infrastructure/sql/models_registry.py`, `alembic revision --autogenerate`, ręczny review diffu, `alembic upgrade head`.
- Każde nowe uprawnienie: stała w `app/modules/security/models/constants.py` + wpis w seedzie danych referencyjnych.
- Każda nowa auditowalna encja: wpis w `EntityType` (`app/core/audit.py`).
- Żadnych nowych zależności bez Twojej zgody (zgodnie z `CLAUDE.md`) — w planie zaznaczam, gdzie mogłaby się pojawić pokusa dodania paczki, i proponuję wariant z biblioteki standardowej / już obecnej w `requirements.txt`.
- Etapy są ułożone tak, by każdy blokował jak najmniej rzeczy naraz i dawał się przetestować end-to-end zanim zaczniesz kolejny.

### Założenia z pierwszej wersji planu — status po realizacji Etapów 1–4

Poniższe założenia były jawnie nazwane w pierwszej wersji tego planu (2026-08-09). Dwa z nich (A4, A8) zostały **zrealizowane inaczej, niż tu pierwotnie założono**; A5 pozostaje otwarte (dotyczy jeszcze nierozpoczętego Etapu 5) — zobacz [rozdział 1](#1-stan-wyjściowy-co-już-jest-zbudowane) po szczegóły faktycznej implementacji.

| # | Założenie (pierwotne, 2026-08-09) | Status |
|---|---|---|
| A1 | Nowe encje domenowe (Organizacja, Obiekt, Urządzenie, Punkt pomiarowy) trafiają do istniejącego modułu `core_data`. | ✅ Zrealizowane zgodnie z założeniem — `Organization`, `WaterObject`, `Device`, `MeasurementPoint` żyją w `core_data`. Autentykacja urządzenia (klucze, challenge/response) trafiła jednak do **osobnego** modułu `device_identity`, nie do `core_data` — patrz A3. |
| A2 | `device_id`/`object_id`/`org_id` z payloadu telemetrycznego są informacyjne; źródłem prawdy jest rejestr w bazie. | ✅ Zrealizowane. |
| A3 | Nieznany `device_id` przy ingest → odrzucenie pakietu, nie auto-provisioning. | ✅ Zrealizowane, ale **mechanizm autoryzacji jest inny od zakładanego** w Etapie 2 (§2.3 poniżej, wersja historyczna): zamiast współdzielonego sekretu (`X-Device-Key`) urządzenie dowodzi tożsamości asymetrycznym podpisem (EC P-256, challenge/response) w module `device_identity` i dostaje bearer token — patrz [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md). |
| A4 | Nieznany `point_id` u znanego urządzenia → pomiar pomijany (log ostrzeżenia). | ⚠️ **Zrealizowane inaczej**: nieznany `(device_id, point_id)`, jeśli `type` znajduje się w katalogu (`sensor_registry.yaml`), **auto-provisionuje** nowy `MeasurementPoint` bez interwencji użytkownika, zamiast go pomijać. Pomijany jest tylko przypadek niezgodności `(type, unit)` z już istniejącym punktem (`POINT_TYPE_MISMATCH` w `errors[]`). Typ spoza katalogu odrzuca cały pakiet (`400`). Patrz [`04_telemetry_module.md`, sekcja 5](../technical/backend/04_telemetry_module.md#5-pakiet-v2--batchowanie-i-wieloczujniki). |
| A5 | Ewaluacja reguł alarmowych jest synchroniczna, w tej samej transakcji co zapis pomiaru. | 🔲 Nadal otwarte — moduł alarmów (Etap 5) nie istnieje jeszcze w kodzie, założenie czeka na weryfikację przy starcie tego etapu. |
| A6 | Transmisja zostaje przy HTTP, MQTT odłożone na Etap 2 roadmapy produktowej. | ✅ Zrealizowane, nadal aktualne. |
| A7 | Powiadomienia w MVP: tylko e-mail przez `smtplib`. | 🔲 Nadal otwarte — moduł powiadomień (Etap 6) nie istnieje jeszcze w kodzie. |
| A8 | Użytkownik należy do **jednej** organizacji (`organization_id` nullable na `User`). | ⚠️ **Zrealizowane inaczej**: `User` nie ma kolumny `organization_id` — przynależność jest **wiele-do-wielu** przez tabelę `users_organizations` (`backend/app/modules/core_data/models/users_organizations.py`). Użytkownik może należeć do wielu gmin jednocześnie; rola super-admina platformy jest niezależną, drugą płaszczyzną dostępu (`PLATFORM_*` uprawnienia), nie „organizacją NULL" — patrz [`01_backend-architecture.md`, sekcja 7](../technical/backend/01_backend-architecture.md#7-płaszczyzny-dostępu-i-routing-api). |

---

## 1. Stan wyjściowy (co już jest zbudowane)

**Etapy 1–4 poniżej są zrealizowane w kodzie.** Ta sekcja opisuje faktyczny stan (2026-08-30), nie punkt startowy planu z 2026-08-09 — architektura poszła w kilku miejscach inną drogą niż pierwotnie założono (szczegóły w tabeli założeń wyżej i w opisach Etapów 1–4 poniżej). Docelowa dokumentacja modułów: [`02_core_data_module.md`](../technical/backend/02_core_data_module.md), [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md), [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md).

- `core/`, `infrastructure/sql`, `security` (JWT + elastyczny RBAC grupowy, dwie płaszczyzny dostępu org/platform), `audit` (partycjonowany log), `core_data` (users, organizations, water_objects, devices, measurement_points, users_organizations) — gotowe.
- `device_identity`: autentykacja urządzeń IoT asymetrycznym kluczem EC P-256 (challenge/response), provisioning przez jednorazowy kod aktywacyjny lub ścieżkę administracyjną, bearer token do ingestu — gotowe.
- `telemetry`: `POST /telemetry/ingest` (auth: bearer token urządzenia) zapisuje pakiet **równolegle** jako JSONB (`windows`/`points`) do `telemetry_packets` (audyt/replay, idempotentnie po `(device_id, seq)`) i jako wiersze w znormalizowanej, partycjonowanej tabeli `measurements` (idempotentnie po `(measurement_point_id, window_start)`); auto-provisionuje nieznane punkty pomiarowe znanego typu; `GET /api/v1/orgs/{org_id}/telemetry/objects[/{object_id}[/measurements]]` oraz `GET .../telemetry/points/{point_id}/measurements` obsługują status obiektu (`no_data`/`no_comm`/`warning`/`ok`), szczegóły i historię pomiarów, czytając z `measurements` — gotowe (pokrywa UC-01 i UC-02).
- `sensor_registry.yaml` (project root) — single source of truth dla `point_types`/`error_codes`, współdzielony między backend (`core_data/registry.py`) a firmware (pre-build codegen) — gotowe.
- Firmware (ESP32-S3 + A7670E, PT100 temperatura + PT506/ADS1015 ciśnienie) wysyła pakiety v2 wieloczujnikowe zgodne z `sensor_registry.yaml` — gotowe.
- **Brak jeszcze:** silnika reguł alarmowych, powiadomień, eksportu danych (Etapy 5–7 poniżej). Znormalizowana tabela `measurements` — brakujące ogniwo tych trzech etapów — **powstała** (patrz Etap 2 poniżej i [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md)).

---

## 2. Mapa etapów i zależności

```
Etap 1: Rejestr obiektów (core_data)                          ✅ zrealizowane
   │
   ▼
Etap 2: Telemetry v2 (per-device auth, normalizacja, diagnostyka)  ✅ zrealizowane (auth i diagnostyka inaczej niż plan — patrz wyżej)
   │
   ├──▼ Etap 3: Status / dashboard API (UC-01)                 ✅ zrealizowane (w module telemetry, nie w osobnym dashboard/)
   │
   └──▼ Etap 4: Historia i wykresy (UC-02)                     ✅ zrealizowane
          │
          ▼
Etap 5: Reguły anomalii i alarmy (UC-03)                       🔲 nie rozpoczęte
   │
   ▼
Etap 6: Powiadomienia                                          🔲 nie rozpoczęte
   │
   ▼
Etap 7: Eksport danych (UC-05)                                 🔲 nie rozpoczęte
```

Etapy 3 i 4 powstały równolegle po ukończeniu Etapu 2, oba w module `telemetry` (patrz Etap 3 poniżej — założenie o osobnym module `dashboard` się nie potwierdziło). Etap 6 wymaga Etapu 5. Etap 7 wymaga Etapu 4 (i opcjonalnie 5, jeśli eksport ma obejmować alarmy).

---

## Etap 1 — Rejestr obiektów (`core_data`) ✅ zrealizowane

Cel: encje **Organization → WaterObject → Device → MeasurementPoint**, powiązanie użytkownika z organizacją(-ami), CRUD API chronione RBAC.

**Zaimplementowane w `app/modules/core_data/`** (modele w `models/`: `organization.py`, `water_object.py`, `device.py`, `measurement_point.py`, `user.py`, `users_organizations.py`). Różnice względem planu z 2026-08-09:

- Przynależność user ↔ organizacja jest **wiele-do-wielu** (`users_organizations`), nie `organization_id` nullable na `User` — patrz założenie A8 w tabeli wyżej i [`01_backend-architecture.md`, sekcja 7](../technical/backend/01_backend-architecture.md#7-płaszczyzny-dostępu-i-routing-api) (dwie płaszczyzny: `/api/v1/orgs/{org_id}/...` dla członków gminy, `/api/v1/platform/...` dla super admina).
- `Device` **nie ma** pola `hashed_secret` ani sekretu generowanego przy tworzeniu — poświadczenie klucza publicznego żyje w osobnym module `device_identity` (`DeviceCredential`), rozdzielone od rekordu `Device` w `core_data`. Provisioning urządzenia to osobny flow (kod aktywacyjny + challenge/response), nie `POST /devices` z odpowiedzią zawierającą `plain_secret`.
- Endpointy API są org-scoped w ścieżce, nie płaskie: `/api/v1/orgs/{org_id}/objects`, `/api/v1/orgs/{org_id}/devices`, `/api/v1/orgs/{org_id}/members`, plus płaskie warianty platformowe (`/api/v1/platform/objects`, `/api/v1/platform/devices`) dla widoków cross-org super admina — zamiast pojedynczego płaskiego `/devices` z filtrem, jak sugerował pierwotny plan.

Pełny opis modelu danych, uprawnień i reguł biznesowych: [`02_core_data_module.md`](../technical/backend/02_core_data_module.md).

---

## Etap 2 — Telemetry v2 (per-device auth, normalizacja, diagnostyka) ✅ zrealizowane

Cel: ingest przestaje ufać wolnemu tekstowi i blobowi JSON; dane są uwierzytelnione per urządzenie; dochodzi kanał diagnostyczny.

**Zaimplementowane, w architekturze innej niż pierwotny plan:**

- **Autoryzacja per-device jest asymetryczna, nie shared-secret.** Zamiast `X-Device-Key`/`hashed_secret` porównywanego przez `verify_password`, urządzenie generuje na sobie parę kluczy EC P-256, rejestruje klucz publiczny (kod aktywacyjny lub ścieżka administracyjna), i dowodzi posiadania klucza prywatnego przez podpis w challenge/response (`POST /devices/auth/challenge` → `POST /devices/auth/verify`), dostając bearer token. Ingest wymaga `Authorization: Bearer <device_token>`, zweryfikowanego przez `get_current_device` z `device_identity`. Pełny opis: [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md).
- **Normalizacja dodana po fakcie (2026-09).** Pierwsza wersja Etapu 2 zapisywała pomiary wyłącznie jako JSONB w `telemetry_packets`, a zapytania szeregów czasowych parsowały blob. Blob **zostaje** (audyt i replay, dedup po `(device_id, seq)`), ale obok niego ingest zapisuje teraz wiersz na *(punkt, okno)* w partycjonowanej tabeli `measurements`, z drugą, niezależną idempotencją po `(measurement_point_id, window_start)`. Wszystkie odczyty aplikacyjne (dashboard, szczegóły obiektu, historia) czytają z `measurements`; z `telemetry_packets` pochodzą już tylko fakty pakietowe (ostatni kontakt, `seq`). Skrypt `scripts/backfill_measurements.py` przenosi dane historyczne. To **odblokowuje Etap 5** — patrz uwaga architektoniczna przed Etapem 5 poniżej.
- **Nieznany `point_id` u znanego urządzenia auto-provisionuje `MeasurementPoint`**, jeśli `type` jest w `sensor_registry.yaml`, zamiast pomijać pomiar z logiem ostrzeżenia (założenie A4, zrealizowane inaczej — patrz tabela wyżej).
- **Brak osobnego modelu/endpointu `DeviceDiagnostic`.** Diagnostyka firmware trafia jako pole `errors[]` w tym samym pakiecie telemetrycznym (zapisywane w `telemetry_errors`, indeks `(device_id, code, occurred_at)`), aktualizujące `Device.last_diagnostics_at` — nie osobny `POST /telemetry/diagnostics` z odrębnym modelem co 15 minut, jak zakładał pierwotny format wiadomości diagnostycznej z `01_plan_biznesowy.md` §3.4.3.

Pełny opis: [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md), w tym format pakietu v2 (sekcja 5), endpointy odczytu, partycjonowanie i backfill (sekcje 6–8) oraz mechanizm sensor registry (sekcja 9).

---

## Etap 3 — Status / dashboard API (UC-01) ✅ zrealizowane

Cel: odpowiedź na pytanie „który obiekt wymaga uwagi i dlaczego?".

**Zaimplementowane w module `telemetry`, nie w osobnym `app/modules/dashboard/`** — założenie planu, że status/dashboard to czysto kompozycyjny moduł ponad `core_data` i `telemetry`, się nie potwierdziło: logika statusu (`TelemetryQueryService._compute_status`) i endpointy żyją bezpośrednio w `telemetry`, bo to tam są dane potrzebne do jej wyliczenia.

- **Logika statusu** (bez pojęcia `alarm` — Etap 5 nie istnieje jeszcze): `no_data` (urządzenie nigdy nic nie wysłało), `no_comm` (ostatni kontakt starszy niż `settings.telemetry_stale_after_seconds`), `warning` (którykolwiek punkt ma `quality != "good"`), `ok` (pozostałe przypadki). Gdy Etap 5 (alarmy) powstanie, `alarm` jako priorytet stanu będzie trzeba dodać do tej samej funkcji.
- **Endpointy:** `GET /api/v1/orgs/{org_id}/telemetry/objects` (lista + status + ostatnie odczyty), `GET .../objects/{object_id}` (szczegóły obiektu), oba chronione `CAN_VIEW_ASSETS` przez `require_org_access` — filtrowanie po organizacji jest częścią samego routingu (`org_id` w ścieżce), nie osobnym helperem `get_current_user_organization_id` na koncie usera z jedną organizacją.

Pełny opis: [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md).

---

## Etap 4 — Historia i wykresy (UC-02) ✅ zrealizowane

**Endpointy:** `GET /api/v1/orgs/{org_id}/telemetry/objects/{object_id}/measurements` (historia obiektu) oraz `GET /api/v1/orgs/{org_id}/telemetry/points/{point_id}/measurements` (historia pojedynczego punktu) — moduł `telemetry`, zgodnie z rekomendacją pierwotnego planu, nie `dashboard`, który się nie zmaterializował. Po normalizacji (2026-09) oba czytają z tabeli `measurements` po indeksie `(measurement_point_id, window_start)`; wcześniejsza wersja parsowała JSONB, a przed nieograniczonym wynikiem broniła się limitem skanowanych pakietów (`MAX_PACKETS_PER_SERIES = 5000`). Limit `limit` (domyślnie 1000, maks. 5000) dotyczy teraz pomiarów, a `truncated` w odpowiedzi mówi klientowi, że szereg został ucięty.

Pełny opis: [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md).

---

## Etap 5 — Reguły anomalii i alarmy (UC-03, sekcje 8-9)

> **⚠️ Uwaga architektoniczna przed startem tego etapu (zdezaktualizowana 2026-09):** ten opis (poniżej, niezmieniony od 2026-08-09) zakłada normalizowaną tabelę `Measurement`. Tabela **istnieje** od normalizacji telemetrii (`measurements`, patrz Etap 2), więc `RuleEvaluationService` może dostać strumień pomiarów zamiast blobu — poniższy akapit opisuje stan sprzed tej zmiany i został zachowany jako kontekst decyzji. Historycznie: „Ta tabela **nie powstała** — telemetria żyje w `telemetry_packets` jako JSONB (patrz Etap 2 wyżej). `RuleEvaluationService.evaluate(measurement: Measurement)` w §5.3 poniżej trzeba więc przeprojektować pod rzeczywisty kształt danych: albo ewaluacja czyta punkty bezpośrednio z JSONB przy każdym ingestcie (`TelemetryIngestService.ingest()` już ma tam dostęp do sparsowanego payloadu), albo Etap 5 wprowadza własną, węższą strukturę do śledzenia stanu reguły (np. tylko „od kiedy warunek trwa" per `measurement_point_id`), bez pełnej normalizacji historii pomiarów. To decyzja do podjęcia na starcie tego etapu, nie założenie do przyjęcia biernie z treści poniżej. Założenie A5 (ewaluacja synchroniczna w tej samej transakcji co ingest) pozostaje prawdopodobnie aktualne niezależnie od tej decyzji."

Nowy moduł `app/modules/alarms/` — pełny wzorzec (`api/services/repositories/schemas/models/dependencies.py/exceptions.py/tests`).

### 5.1. Modele

- `AlarmRule`: `id`, `measurement_point_id` (FK), `rule_type` (`min_threshold`/`max_threshold`/`sudden_drop`/`no_data`), `threshold` (float, nullable dla `no_data`), `duration_seconds`, `hysteresis` (nullable float), `priority` (`critical`/`warning`/`info`), `min_interval_seconds` (deduplikacja), `required_quality` (JSON — lista dozwolonych statusów jakości), `is_active`.
- `Alarm`: `id`, `alarm_rule_id` (FK), `water_object_id` (FK, zdenormalizowane dla szybkich zapytań listy), `status` (`new`/`active`/`acknowledged`/`closed`/`rejected` — state machine z [dok. 01, rozdział 2.5](./01_plan_biznesowy.md#25-alarmy-i-powiadomienia)), `priority`, `triggered_at`, `trigger_value`, `resolved_at` (nullable), `acknowledged_by_id` (FK → `users.id`, nullable), `acknowledged_at` (nullable), `comment` (nullable).

Migracja + rejestracja w `models_registry.py`.

### 5.2. Uprawnienia i audit

`CAN_VIEW_ALARMS`, `CAN_MANAGE_ALARMS`, `CAN_MANAGE_ALARM_RULES` w `constants.py` (+ seed). `EntityType.ALARM_RULE`, `EntityType.ALARM` w `core/audit.py`.

### 5.3. Silnik reguł

`RuleEvaluationService.evaluate(...) -> None` (sygnatura do ustalenia na podstawie decyzji z uwagi architektonicznej powyżej — dane wejściowe to punkty z payloadu ingestu, nie wiersz `Measurement`), wołany z `TelemetryIngestService` **zaraz po** zapisie pakietu (założenie A5 — synchronicznie, ta sama transakcja). Logika per regułę dokładnie wg diagramu w [dok. 01, rozdział 2.6.4](./01_plan_biznesowy.md#264-parametry-reguł-i-logika-ewaluacji): sprawdź `required_quality` → sprawdź próg → sprawdź czas utrzymania warunku (potrzebny stan „od kiedy warunek trwa" — najprościej: kolejne przekroczenia progu bez luki tworzą/aktualizują **jeden** otwarty `Alarm` ze statusem `new`, dopiero po `duration_seconds` ciągłego przekroczenia zmienia się na `active`) → sprawdź `min_interval_seconds` od ostatniego zdarzenia tej reguły → utwórz/zaktualizuj `Alarm`.

**Zakres MVP dla reguł:** progi pojedynczego punktu (`min_threshold`/`max_threshold`/`no_data`) w pierwszej kolejności — pokrywają większość katalogu z [dok. 01, rozdział 2.6](./01_plan_biznesowy.md#26-katalog-zdarzeń-i-alarmów-wodociągowych). Reguły łączone (np. „spadek ciśnienia + wzrost przepływu jednocześnie", bilans strefy) to naturalne rozszerzenie tego samego serwisu, ale zaplanuj je jako osobny podetap **po** działających regułach prostych — inaczej ryzykujesz utknięcie na najtrudniejszym przypadku zamiast oddać działającą podstawę.

### 5.4. Cykl życia alarmu

`AlarmService`: `acknowledge()`, `add_comment()`, `close()`, `reject_as_false()` — strażnik przejść stanu (np. nie można zamknąć alarmu, który nie jest `active`/`acknowledged`) zgodnie z diagramem stanów w [dok. 01, rozdział 2.5](./01_plan_biznesowy.md#25-alarmy-i-powiadomienia).

### 5.5. API

Ścieżki poniżej są z pierwszej wersji planu (płaskie `/api/v1/...`) — Etapy 1–4 ustanowiły w kodzie konwencję dwóch płaszczyzn dostępu, org-scoped (`/api/v1/orgs/{org_id}/...`) i platformowej (`/api/v1/platform/...`, patrz [`01_backend-architecture.md`, sekcja 7](../technical/backend/01_backend-architecture.md#7-płaszczyzny-dostępu-i-routing-api)) — nowe endpointy alarmów powinny prawdopodobnie iść tą samą drogą (`/api/v1/orgs/{org_id}/alarms`, ...), do potwierdzenia na starcie tego etapu:

`GET /api/v1/alarms` (filtry: `status`, `priority`, `object_id`, zakres czasu), `POST /api/v1/alarms/{id}/acknowledge`, `POST /api/v1/alarms/{id}/comment`, `POST /api/v1/alarms/{id}/close`, `POST /api/v1/alarms/{id}/reject`. CRUD `AlarmRule` pod `/api/v1/points/{point_id}/rules`.

### 5.6. Testy

Testy jednostkowe silnika reguł to najważniejsza część — scenariusze czasowe (próg przekroczony za krótko → brak alarmu, przekroczony wystarczająco długo → alarm, histereza, deduplikacja przez `min_interval_seconds`, wymagana jakość danych blokuje regułę).

---

## Etap 6 — Powiadomienia

### 6.1. Odbiorcy

`NotificationRecipient` (nowy model w `alarms` albo w `core_data` — polecam `core_data`, bo to konfiguracja per organizacja, podobnie jak reszta rejestru): `organization_id` (FK), `email`, `is_active`, minimalnie `notify_on_priority` (lista priorytetów, żeby nie zalewać ludzi alarmami informacyjnymi).

### 6.2. Wysyłka e-mail

**Uwaga na zależności:** nie dodawaj nowej biblioteki (SendGrid/SES SDK itp.) bez zgody — `smtplib` z biblioteki standardowej Pythona wystarcza na MVP. Nowe ustawienia w `Settings`: `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `smtp_from_address`. `NotificationService.send_alarm_notification(alarm, recipients)`.

### 6.3. Wyzwolenie

Hook w `AlarmService` — przy przejściu alarmu do `new`/`active` (nie przy każdej aktualizacji), wywołanie `NotificationService` z serwisów `core_data` (odbiorcy danej organizacji obiektu).

### 6.4. Testy

Mock SMTP (np. `smtplib.SMTP` monkeypatched) — sprawdzić, że treść zawiera obiekt, priorytet, wartość wyzwalającą, że wysyłka nie blokuje zapisu alarmu przy błędzie SMTP (log błędu, nie wyjątek do klienta HTTP).

---

## Etap 7 — Eksport danych (UC-05)

### 7.1. Eksport pomiarów

`GET /api/v1/objects/{id}/export?format=csv&from=&to=` — `csv` z biblioteki standardowej + `StreamingResponse` (bez nowych zależności), kolumny: `point_id`, `type`, `unit`, `window_start`, `avg`, `min`, `max`, `value`, `quality`.

### 7.2. Eksport alarmów

`GET /api/v1/alarms/export?format=csv&from=&to=&object_id=`.

### 7.3. Testy

Poprawność nagłówków CSV, zakres dat, uprawnienia (te same co odczyt danych źródłowych).

---

## 8. Kryteria ukończenia MVP backendu

Wyprowadzone z wymagań MVP w dok. 01 (m.in. rozdziały 2.2, 3.2.1, 3.6) — checklist do odhaczenia po Etapie 7:

- [x] Backend działa wyłącznie read-only względem infrastruktury (brak endpointów sterujących) — **spełnione, pilnować przy każdym nowym module**.
- [x] Stabilnie pobiera i uwierzytelnia dane per urządzenie (Etap 2 — asymetryczny challenge/response, nie shared-secret jak pierwotnie planowano).
- [x] Zachowuje czas i jakość każdego pomiaru (Etap 2 — `quality` + `window_start` w kolumnach tabeli `measurements`, a dodatkowo w blobie `telemetry_packets.payload` jako ścieżce audytu).
- [x] Odzyskuje spójność po przerwie łączności — idempotencja `(device_id, seq)` gotowa; `no_comm` w statusie (Etap 3) domyka wykrywanie.
- [x] Poprawnie prezentuje aktualne i historyczne dane (Etapy 3-4).
- [ ] Generuje alarmy zgodnie ze skonfigurowanymi regułami (Etap 5 — nie rozpoczęte).
- [x] Pozwala rozróżnić awarię infrastruktury od awarii telemetryki — diagnostyka przez pole `errors[]` pakietu (nie osobny endpoint, patrz Etap 2) + status `no_comm` vs. `out_of_range`/`sensor_error` w danych (jakość pomiaru).

---

## 9. Otwarte pytania biznesowe (nie blokują startu, ale wpłyną na szczegóły)

- Próg komunikacji (`settings.telemetry_stale_after_seconds`) — jaka wartość domyślna ma sens dla pierwszego pilotażu?
- Czy `Administrator klienta` ([dok. 01, rozdział 2.7.3](./01_plan_biznesowy.md#273-wstępne-role-systemowe)) może sam tworzyć obiekty/urządzenia, czy tylko `Administrator platformy`? (Wpływa na dokładny podział `CAN_MANAGE_ASSETS` między grupy.)
- Kanały powiadomień poza e-mail (SMS — [dok. 01, rozdział 7.3.2](./01_plan_biznesowy.md#732-nadal-otwarte)) — kiedy potrzebne? (Etap 6, nie rozpoczęty.)
- ~~Czy jeden użytkownik będzie musiał obsługiwać więcej niż jedną organizację?~~ **Rozstrzygnięte:** tak, `users_organizations` (M:N) obsługuje to od Etapu 1 — założenie A8 z pierwszej wersji planu zostało porzucone w trakcie implementacji.

---

## 10. Sugerowana kolejność pracy w praktyce

1. ~~Etap 1 w całości~~ ✅ zrealizowane.
2. ~~Etap 2 w całości~~ ✅ zrealizowane.
3. ~~Etap 3 i 4~~ ✅ zrealizowane.
4. **Następny krok: Etap 5** — zacząć od rozstrzygnięcia architektonicznego opisanego w uwadze na początku tego etapu (brak tabeli `Measurement`), potem od reguł prostych progowych, dopiero później reguły łączone.
5. Etap 6 (krótki, zależny tylko od 5).
6. Etap 7 (najkrótszy, można zrobić w dowolnym momencie — Etap 4 już gotowy).
