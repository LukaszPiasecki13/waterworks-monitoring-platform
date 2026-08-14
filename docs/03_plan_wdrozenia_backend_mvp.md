# Plan wdrożenia backendu — MVP krok po kroku

**Dokument towarzyszący:** `01_plan_biznesowy.md`, `backend-architecture.md`
**Data:** 2026-08-09
**Zakres:** wyłącznie backend (`backend/`). Frontend jest osobnym torem prac i nie jest tu opisany.

---

## 0. Zasady tego planu

- Każdy nowy moduł/encja stosuje **dokładnie** wzorzec z `backend-architecture.md` i istniejącego modułu `core_data/users`: `api/ → services/ → repositories/ → infrastructure`, sync `Session` SQLAlchemy, `SQLRepository` jako baza repozytorium, serwisy przyjmują zależności przez `__init__` (bez `Depends()` w środku), transakcje (`commit`/`rollback`) prowadzi serwis (wyjątek: `telemetry` — tam repozytorium samo commituje, bo to zapis o wysokiej częstotliwości bez logiki biznesowej).
- Każda nowa tabela: model w `models/`, rejestracja w `app/infrastructure/sql/models_registry.py`, `alembic revision --autogenerate`, ręczny review diffu, `alembic upgrade head`.
- Każde nowe uprawnienie: stała w `app/modules/security/models/constants.py` + wpis w seedzie danych referencyjnych (patrz krok 1.2 — skrypt seedujący trzeba odtworzyć, bo `alembic/README.md` się do niego odwołuje, ale `scripts/seed_required_data.py` nie istnieje w repo).
- Każda nowa auditowalna encja: wpis w `EntityType` (`app/core/audit.py`).
- Żadnych nowych zależności bez Twojej zgody (zgodnie z `CLAUDE.md`) — w planie zaznaczam, gdzie mogłaby się pojawić pokusa dodania paczki, i proponuję wariant z biblioteki standardowej / już obecnej w `requirements.txt`.
- Etapy są ułożone tak, by każdy blokował jak najmniej rzeczy naraz i dawał się przetestować end-to-end zanim zaczniesz kolejny.

### Przyjęte założenia projektowe (możesz je zmienić — są tu jawnie nazwane, nie ukryte w kodzie)

| # | Założenie | Uzasadnienie |
|---|---|---|
| A1 | Nowe encje domenowe (Organizacja, Obiekt, Urządzenie, Punkt pomiarowy) trafiają do istniejącego modułu `core_data`, nie do nowego modułu. | `backend-architecture.md` opisuje `core_data` wprost jako „dane słownikowe i konfiguracyjne współdzielone przez inne moduły" — to dokładnie ten przypadek. |
| A2 | `device_id`, `object_id`, `org_id` z payloadu telemetrycznego stają się **informacyjne**; źródłem prawdy jest rejestr w bazie, wiązany po `device_id`. | Firmware nie musi się zmieniać (nadal wysyła te same pola), ale backend przestaje im ślepo ufać. |
| A3 | Nieznany `device_id` przy ingest → odrzucenie pakietu (401/403), nie auto-provisioning. | Zgodne z sekcją 14 dok. 01 („unikalne poświadczenia każdego urządzenia") — urządzenie musi być jawnie zarejestrowane. |
| A4 | Nieznany `point_id` w ramach znanego urządzenia → pomiar tego punktu jest pomijany (log ostrzeżenia), reszta pakietu przetwarzana normalnie. | Częściowe dane są lepsze niż odrzucenie całego pakietu z powodu jednego nieskonfigurowanego punktu. |
| A5 | Ewaluacja reguł alarmowych jest **synchroniczna**, wywoływana w tej samej transakcji co zapis pomiaru (bez brokera/workera). | Wolumeny są bardzo małe (dok. 02, sekcja 5) — jeden pakiet na obiekt co 1-5 min. Broker/worker to niepotrzebna złożoność na MVP. |
| A6 | Transmisja zostaje przy HTTP (obecny PoC), MQTT z sekcji 10 dok. 01 jest świadomie odłożone na Etap 2 roadmapy. | HTTP już działa z firmware, jest prostsze operacyjnie. |
| A7 | Powiadomienia w MVP: tylko e-mail, przez `smtplib` z biblioteki standardowej (zero nowych zależności). | SMS/webhook to sekcja 25.2 dok. 01 — decyzja otwarta, nie blokuje MVP. |
| A8 | Użytkownik należy do **jednej** organizacji (`organization_id` nullable na `User`; `NULL` = administrator platformy widzący wszystko). | Najprostszy model spełniający sekcję 17.3. Multi-org per user to rozszerzenie, nie blokuje MVP. |

---

## 1. Stan wyjściowy (co już jest zbudowane)

- `core/`, `infrastructure/sql`, `security` (JWT + elastyczny RBAC grupowy), `audit` (partycjonowany log), `core_data.users` — gotowe.
- `telemetry`: `POST /telemetry/ingest` zapisuje **cały pakiet jako JSON blob** do `telemetry_packets`, idempotentnie po `(device_id, seq)`. Autoryzacja to **jeden globalny klucz** (`X-Device-Key` porównywany z jednym `telemetry_ingest_key` w konfiguracji) — do naprawienia w Etapie 2.
- Brak jakiejkolwiek tabeli Organizacja/Obiekt/Urządzenie/Punkt pomiarowy.
- Firmware (ESP32-S3 + A7670E) działa i wysyła dane w formacie zgodnym z `MeasurementPacketRequest`.

---

## 2. Mapa etapów i zależności

```
Etap 1: Rejestr obiektów (core_data)
   │  (bez tego nic poniżej nie ma sensu — brak multi-tenant, brak per-device auth)
   ▼
Etap 2: Telemetry v2 (per-device auth, normalizacja pomiarów, diagnostyka)
   │
   ├──▼ Etap 3: Status / dashboard API (UC-01)
   │
   └──▼ Etap 4: Historia i wykresy (UC-02)
          │
          ▼
Etap 5: Reguły anomalii i alarmy (UC-03)
   │
   ▼
Etap 6: Powiadomienia
   │
   ▼
Etap 7: Eksport danych (UC-05)
```

Etapy 3 i 4 mogą powstawać równolegle po ukończeniu Etapu 2. Etap 6 wymaga Etapu 5. Etap 7 wymaga Etapu 4 (i opcjonalnie 5, jeśli eksport ma obejmować alarmy).

---

## Etap 1 — Rejestr obiektów (`core_data`)

Cel: encje **Organization → WaterObject → Device → MeasurementPoint**, powiązanie użytkownika z organizacją, CRUD API chronione RBAC.

### 1.1. Modele i migracja

Nowe pliki w `app/modules/core_data/models/`:

| Plik | Model | Kluczowe pola |
|---|---|---|
| `organizations.py` | `Organization` | `id`, `name` (unique), `created_at`, `updated_at` |
| `water_objects.py` | `WaterObject` | `id`, `organization_id` (FK), `name`, `object_type` (str: `pump_station`/`hydrophore`/`intake`/`network_point`), `location_description` (nullable), `latitude`/`longitude` (nullable float), `is_active`, `created_at`, `updated_at` |
| `devices.py` | `Device` | `id`, `water_object_id` (FK), `external_id` (str, unique — to jest `device_id` z payloadu), `hashed_secret`, `firmware_version` (nullable), `last_seen_at` (nullable), `last_diagnostics_at` (nullable), `is_active`, `created_at`, `updated_at` |
| `measurement_points.py` | `MeasurementPoint` | `id`, `device_id` (FK), `external_id` (str — to jest `point_id` z payloadu), `point_type` (str: `pressure`/`flow_rate`/`total_volume`/`power_status`/...), `unit`, `min_technical`/`max_technical` (nullable float), `is_active`, `created_at`, `updated_at`; `UniqueConstraint(device_id, external_id)` |

Zmiana w `app/modules/core_data/models/user.py`: dodać `organization_id: Mapped[int | None]` (FK → `organizations.id`, nullable — patrz założenie A8).

Kroki:
1. Utworzyć 4 pliki modeli wg tabeli wyżej (dziedziczą z `Base`, wzorowane na `models/user.py`).
2. Zarejestrować wszystkie w `app/infrastructure/sql/models_registry.py`.
3. `alembic revision --autogenerate -m "Add organizations, water objects, devices, measurement points"`.
4. Ręcznie sprawdzić diff (indeksy na FK, `UniqueConstraint`).
5. `alembic upgrade head`.

### 1.2. Uprawnienia i seed danych referencyjnych

Dodać do `app/modules/security/models/constants.py`:
```
CAN_VIEW_ORGANIZATIONS = "CAN_VIEW_ORGANIZATIONS"
CAN_MANAGE_ORGANIZATIONS = "CAN_MANAGE_ORGANIZATIONS"
CAN_VIEW_ASSETS = "CAN_VIEW_ASSETS"       # obiekty, urządzenia, punkty pomiarowe
CAN_MANAGE_ASSETS = "CAN_MANAGE_ASSETS"
```

`alembic/README.md` odwołuje się do `python -m scripts.seed_required_data`, ale ten skrypt **nie istnieje** w repozytorium (tylko ślad w cache testów) — trzeba go odtworzyć: `backend/scripts/seed_required_data.py`, ładujący `Permission` (wszystkie stałe z `constants.py`, w tym istniejące `CAN_VIEW_USERS` itd.) i domyślne grupy `admin`/`staff` z sensownym przypisaniem (admin = wszystko, staff = tylko `CAN_VIEW_*`). To domyka lukę, nie tylko dla tego etapu.

### 1.3. Audit

Dodać do `EntityType` w `app/core/audit.py`: `ORGANIZATION`, `WATER_OBJECT`, `DEVICE`, `MEASUREMENT_POINT`.

### 1.4. Schematy

`app/modules/core_data/schemas/`: `organizations.py`, `water_objects.py`, `devices.py`, `measurement_points.py` — każdy z `<Resource>CreateRequest`, `<Resource>UpdateRequest`, `<Resource>Response` (wzorowane na `schemas/users.py`, reużyć istniejący generyczny `PaginatedResponse[T]`).

Szczególny przypadek — `DeviceCreateRequest`/`DeviceResponse`: sekret urządzenia jest **generowany po stronie serwera** i zwracany **tylko raz**, przy tworzeniu (jak API key). Potrzebny osobny schemat `DeviceCreateResponse` zawierający `plain_secret: str` obok reszty pól — kolejne odczyty (`GET /devices/{id}`) nigdy nie zwracają sekretu, tylko np. `secret_last_rotated_at`.

### 1.5. Repozytoria

`app/modules/core_data/repositories/`: `organizations.py`, `water_objects.py`, `devices.py`, `measurement_points.py`, dziedziczące z `SQLRepository` (wzorowane na `repositories/users.py`): `get_by_id`, `list_all` (z filtrami: dla obiektów — po `organization_id`; dla urządzeń — po `water_object_id`; dla punktów — po `device_id`), `count`, `create`, `update`, `delete`, `exists`/`get_by_external_id`.

### 1.6. Generowanie i weryfikacja sekretu urządzenia

Nowy plik `app/modules/core_data/services/device_secrets.py`: `generate_device_secret() -> str` (np. `secrets.token_urlsafe(32)`) + reużycie `hash_password`/`verify_password` z `app/modules/security/services/password.py` do hashowania/weryfikacji (to są generyczne funkcje bcrypt, nie ma potrzeby duplikować logiki).

### 1.7. Serwisy

`app/modules/core_data/services/`: `organizations.py`, `water_objects.py`, `devices.py`, `measurement_points.py` — wzorowane na `services/users.py` (walidacja unikalności, sprawdzenie istnienia rodzica przed utworzeniem dziecka — obiekt wymaga istniejącej organizacji, urządzenie wymaga istniejącego obiektu, punkt wymaga istniejącego urządzenia — audit log przez `AuditPort` przy każdym create/update/delete, transakcje przez `flush`/`commit`/`rollback` na repozytorium).

`DeviceService.create()` zwraca `plain_secret` tylko w tym jednym wywołaniu (przechowuje `hashed_secret`, zwraca `plain_secret` do serializacji w API).

### 1.8. API

`app/modules/core_data/api/`: `organizations.py` (prefix `/organizations`, chronione `CAN_VIEW_ORGANIZATIONS`/`CAN_MANAGE_ORGANIZATIONS` — **tylko admin platformy**), `water_objects.py` (prefix `/objects`), `devices.py` (prefix `/objects/{object_id}/devices` lub płaski `/devices` z filtrem — polecam płaski, prościej filtrować), `measurement_points.py` (analogicznie `/devices/{device_id}/points`), wszystkie chronione `CAN_VIEW_ASSETS`/`CAN_MANAGE_ASSETS`. Zarejestrować routery w `app/modules/core_data/api/__init__.py`.

### 1.9. Powiązanie user ↔ organizacja

Rozszerzyć `UserCreateRequest`/`UserUpdateRequest`/`UserResponse` o `organization_id: int | None`. Dodać w `app/modules/security/dependencies.py` helper `get_current_user_organization_id(user: User = Depends(get_current_user)) -> int | None` — będzie reużywany w Etapach 3-5 do filtrowania danych po organizacji (użytkownik z `organization_id=None` = platform admin widzi wszystko).

### 1.10. Testy

Mirror struktury `core_data/tests/unit` + `tests/integration` z modułu `users`: testy jednostkowe serwisów (mock repozytoriów), testy integracyjne API (RBAC + kształt odpowiedzi), w tym: obiekt bez istniejącej organizacji → 404/422, urządzenie zwraca `plain_secret` tylko przy tworzeniu, duplikat `external_id` → 409.

**Definicja ukończenia Etapu 1:** jako admin platformy można przez API utworzyć organizację → obiekt → urządzenie (odebrać sekret jednorazowo) → punkt pomiarowy; użytkownik przypisany do organizacji A nie widzi zasobów organizacji B; pełny zestaw testów zielony.

---

## Etap 2 — Telemetry v2 (per-device auth, normalizacja, diagnostyka)

Cel: ingest przestaje ufać wolnemu tekstowi i blobowi JSON; dane trafiają do znormalizowanej tabeli pomiarów; dochodzi kanał diagnostyczny.

### 2.1. Model pomiarów znormalizowanych

`app/modules/telemetry/models/measurement.py` — `Measurement`: `id` (bigint), `measurement_point_id` (FK → `measurement_points.id`), `window_start` (datetime tz-aware), `window_seconds`, `avg`/`min`/`max`/`value` (nullable float), `quality` (str), `received_at`, `source_packet_id` (FK → `telemetry_packets.id`, dla traceability). `UniqueConstraint(measurement_point_id, window_start)` — idempotencja per punkt per okno.

### 2.2. Model diagnostyki

`app/modules/telemetry/models/device_diagnostic.py` — `DeviceDiagnostic`: `id`, `device_id` (FK), `received_at`, `firmware_version`, `config_version`, `uptime_seconds`, `last_restart_at`, `restart_reason`, `rssi_dbm`, `cellular_technology`, `cellular_operator`, `buffer_records_pending`, `buffer_usage_percent`, `power_source`, `voltage_v`, `temperature_c`, `raw_payload` (JSON — pełny blob na przyszłość). Pola dokładnie wg formatu z `01_plan_biznesowy.md`, rozdział 3.4.3 (Wiadomość diagnostyczna).

Rejestracja obu modeli w `models_registry.py`, `alembic revision --autogenerate -m "Add measurements and device diagnostics"`, review, `upgrade head`.

### 2.3. Autoryzacja per-device

Zastąpić `verify_telemetry_ingest_key` w `app/modules/telemetry/dependencies.py`. Nowa zależność `verify_device_credentials`:
1. Czyta `X-Device-Key` z nagłówka i `device_id` z body (FastAPI: trzeba przenieść tę walidację **po** sparsowaniu body, albo zrobić lookup wewnątrz serwisu ingestu zamiast w `Depends()` na poziomie nagłówka — prościej: przenieść weryfikację do `TelemetryIngestService.ingest()`, na samym początku, przed zapisem czegokolwiek).
2. Woła nowy serwis w `core_data` — `DeviceLookupService.get_active_by_external_id(device_id)` (komunikacja międzymodułowa **wyłącznie przez warstwę serwisów**, zgodnie z regułą 2.3 `backend-architecture.md`).
3. Weryfikuje `X-Device-Key` przez `verify_password(x_device_key, device.hashed_secret)`.
4. Nieznane urządzenie / zła para klucz-urządzenie / `is_active=False` → 401/403 (nowe wyjątki w `telemetry/exceptions.py`: `UnknownDeviceError`, `InvalidDeviceSecretError`, `InactiveDeviceError`).

Nagłówek `X-Device-Key` zostaje bez zmian w firmware — zmienia się tylko wartość: docelowo unikalny sekret per urządzenie zamiast `"Test1"` dla wszystkich.

### 2.4. Normalizacja przy zapisie

W `TelemetryIngestService.ingest()`, po zapisaniu surowego `TelemetryPacket` (zostaje jak jest — log/audyt/replay):
1. Dla każdego `window` i `point` w payloadzie: znaleźć `MeasurementPoint` po `(device.id, point.point_id)` przez `MeasurementPointLookupService` z `core_data`.
2. Nie znaleziono → pominąć punkt, zapisać ostrzeżenie w logu (założenie A4), kontynuować pozostałe.
3. Znaleziono → wstawić wiersz `Measurement`.
4. Zaktualizować `Device.last_seen_at = received_at`.

### 2.5. Endpoint diagnostyczny

`app/modules/telemetry/api/diagnostics.py`: `POST /telemetry/diagnostics`, ta sama autoryzacja per-device co ingest, schema `DeviceDiagnosticRequest` (wg sekcji 1.3 dok. 02), zapis `DeviceDiagnostic` + aktualizacja `Device.last_seen_at`/`firmware_version`/`last_diagnostics_at`. Zarejestrować router w `app/main.py` obok istniejącego `telemetry_router`.

### 2.6. Testy

Zaktualizować `telemetry/tests/test_ingest_api.py` pod per-device auth (nieznane urządzenie → 401, cudzy klucz → 403, nieaktywne urządzenie → 403). Nowe testy: normalizacja tworzy poprawne wiersze `Measurement`, nieznany `point_id` nie wywala całego requestu, `Device.last_seen_at` się aktualizuje, nowy endpoint diagnostyczny.

**Definicja ukończenia Etapu 2:** ingest odrzuca nieznane/cudze klucze urządzeń; poprawny pakiet tworzy wiersze w `measurements`; `device.last_seen_at` żyje; diagnostyka jest przyjmowana i zapisywana strukturalnie.

---

## Etap 3 — Status / dashboard API (UC-01)

Cel: odpowiedź na pytanie „który obiekt wymaga uwagi i dlaczego?" (sekcja 18.1 dok. 01).

Nowy moduł `app/modules/dashboard/` — **bez własnych modeli/repozytoriów**, tylko `api/` + `services/`, agregujący dane z `core_data` (rejestr, `Device.last_seen_at`) i `telemetry` (ostatnie pomiary) przez ich warstwy serwisów. To zgodne z regułą modularnego monolitu — moduł czysto kompozycyjny.

### 3.1. Próg komunikacji

`communication_timeout_minutes: int = 15` w `Settings` (`app/core/config.py`) — konfigurowalny próg „brak komunikacji" (UC-04).

### 3.2. Logika statusu

`ObjectStatusService`: dla obiektu status = 
- `no_data` — urządzenie nigdy nic nie wysłało,
- `no_comm` — `last_seen_at` starsze niż próg,
- `alarm` — istnieje aktywny alarm priorytetu krytycznego (Etap 5 — do czasu jego wdrożenia zwracać zawsze „brak" tutaj, to nie blokuje wcześniejszego oddania Etapu 3),
- `warning` — aktywny alarm priorytetu ostrzegawczego lub ostatnia jakość danych ≠ `good`,
- `ok` — w pozostałych przypadkach.

### 3.3. Filtrowanie po organizacji

Każdy endpoint korzysta z `get_current_user_organization_id` (Etap 1.9): `organization_id is None` → wszystkie organizacje, w przeciwnym razie tylko obiekty tej organizacji.

### 3.4. Endpointy

- `GET /api/v1/objects` — lista: `id`, `name`, `object_type`, `status`, `last_contact_at`, ostatnie ciśnienie/przepływ (jeśli są punkty tego typu), liczba aktywnych alarmów. Filtry: `status`, `object_type`, `organization_id` (tylko dla platform admina).
- `GET /api/v1/objects/{id}` — pełny widok wg sekcji 18.2: metadane, aktualne wartości per punkt (z `quality` i czasem pomiaru — **nigdy** samej wartości bez tych dwóch, zgodnie z sekcją 7.3), stan urządzenia/gatewaya (ostatnia diagnostyka).

### 3.5. Testy

Scenariusze statusów (ok/warning/no_comm/no_data), izolacja międzyorganizacyjna, kształt odpowiedzi szczegółowej.

---

## Etap 4 — Historia i wykresy (UC-02)

### 4.1. Zapytania historyczne

W `telemetry` dodać `MeasurementRepository`/serwis z metodą zwracającą pomiary punktu w przedziale czasu, posortowane po `window_start`.

### 4.2. Endpoint

`GET /api/v1/objects/{object_id}/points/{point_id}/measurements?from=&to=&limit=` (moduł `dashboard` lub `telemetry` — polecam `telemetry`, bo to jego dane; `dashboard` zostaje czysto kompozycyjny dla widoków zbiorczych). Odpowiedź zawiera `quality` i `window_start` dla każdego punktu danych — front musi umieć pokazać przerwy w komunikacji (brak wierszy w oknie czasowym = przerwa, nie trzeba tego specjalnie kodować po stronie backendu).

### 4.3. Wolumen

Wg dok. 02 sekcja 5: ~1,6 mln rekordów/rok na obiekt, ~23 mln dla gminy 15-obiektowej — bezpośrednie zapytanie z indeksem na `(measurement_point_id, window_start)` wystarcza na MVP, downsampling/agregacja po stronie bazy to temat na Etap 2 roadmapy, nie teraz.

### 4.4. Testy

Zakres dat, filtrowanie po punkcie, paginacja/limit.

---

## Etap 5 — Reguły anomalii i alarmy (UC-03, sekcje 8-9)

Nowy moduł `app/modules/alarms/` — pełny wzorzec (`api/services/repositories/schemas/models/dependencies.py/exceptions.py/tests`).

### 5.1. Modele

- `AlarmRule`: `id`, `measurement_point_id` (FK), `rule_type` (`min_threshold`/`max_threshold`/`sudden_drop`/`no_data`), `threshold` (float, nullable dla `no_data`), `duration_seconds`, `hysteresis` (nullable float), `priority` (`critical`/`warning`/`info`), `min_interval_seconds` (deduplikacja), `required_quality` (JSON — lista dozwolonych statusów jakości), `is_active`.
- `Alarm`: `id`, `alarm_rule_id` (FK), `water_object_id` (FK, zdenormalizowane dla szybkich zapytań listy), `status` (`new`/`active`/`acknowledged`/`closed`/`rejected` — state machine z sekcji 9), `priority`, `triggered_at`, `trigger_value`, `resolved_at` (nullable), `acknowledged_by_id` (FK → `users.id`, nullable), `acknowledged_at` (nullable), `comment` (nullable).

Migracja + rejestracja w `models_registry.py`.

### 5.2. Uprawnienia i audit

`CAN_VIEW_ALARMS`, `CAN_MANAGE_ALARMS`, `CAN_MANAGE_ALARM_RULES` w `constants.py` (+ seed). `EntityType.ALARM_RULE`, `EntityType.ALARM` w `core/audit.py`.

### 5.3. Silnik reguł

`RuleEvaluationService.evaluate(measurement: Measurement) -> None`, wołany z `TelemetryIngestService` **zaraz po** zapisie każdego `Measurement` (założenie A5 — synchronicznie, ta sama transakcja). Logika per regułę dokładnie wg diagramu w sekcji 8 dok. 01: sprawdź `required_quality` → sprawdź próg → sprawdź czas utrzymania warunku (potrzebny stan „od kiedy warunek trwa" — najprościej: kolejne przekroczenia progu bez luki tworzą/aktualizują **jeden** otwarty `Alarm` ze statusem `new`, dopiero po `duration_seconds` ciągłego przekroczenia zmienia się na `active`) → sprawdź `min_interval_seconds` od ostatniego zdarzenia tej reguły → utwórz/zaktualizuj `Alarm`.

**Zakres MVP dla reguł:** progi pojedynczego punktu (`min_threshold`/`max_threshold`/`no_data`) w pierwszej kolejności — pokrywają większość katalogu z sekcji 19. Reguły łączone (np. „spadek ciśnienia + wzrost przepływu jednocześnie", bilans strefy) to naturalne rozszerzenie tego samego serwisu, ale zaplanuj je jako osobny podetap **po** działających regułach prostych — inaczej ryzykujesz utknięcie na najtrudniejszym przypadku zamiast oddać działającą podstawę.

### 5.4. Cykl życia alarmu

`AlarmService`: `acknowledge()`, `add_comment()`, `close()`, `reject_as_false()` — strażnik przejść stanu (np. nie można zamknąć alarmu, który nie jest `active`/`acknowledged`) zgodnie z diagramem stanów sekcji 9.

### 5.5. API

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

Bezpośrednio z sekcji 21 dok. 01 — checklist do odhaczenia po Etapie 7:

- [ ] Backend działa wyłącznie read-only względem infrastruktury (brak endpointów sterujących) — **już spełnione, pilnować przy każdym nowym module**.
- [ ] Stabilnie pobiera i uwierzytelnia dane per urządzenie (Etap 2).
- [ ] Zachowuje czas i jakość każdego pomiaru (Etap 2 — `quality` + `window_start` w `Measurement`).
- [ ] Odzyskuje spójność po przerwie łączności — idempotencja `(device_id, seq)` już jest; `no_comm` w statusie (Etap 3) domyka wykrywanie.
- [ ] Poprawnie prezentuje aktualne i historyczne dane (Etapy 3-4).
- [ ] Generuje alarmy zgodnie ze skonfigurowanymi regułami (Etap 5).
- [ ] Pozwala rozróżnić awarię infrastruktury od awarii telemetryki — diagnostyka urządzenia (Etap 2.5) + status `no_comm` vs. `out_of_range`/`sensor_error` w danych (jakość pomiaru).

---

## 9. Otwarte pytania biznesowe (nie blokują startu, ale wpłyną na szczegóły)

- Próg `communication_timeout_minutes` — jaka wartość domyślna ma sens dla pierwszego pilotażu?
- Czy `Administrator klienta` (sekcja 17.3) może sam tworzyć obiekty/urządzenia, czy tylko `Administrator platformy`? (Wpływa na dokładny podział `CAN_MANAGE_ASSETS` między grupy w Etapie 1.2.)
- Kanały powiadomień poza e-mail (SMS — sekcja 25.2 dok. 01) — kiedy potrzebne?
- Czy jeden użytkownik będzie musiał obsługiwać więcej niż jedną organizację (założenie A8 to wyklucza na MVP)?

---

## 10. Sugerowana kolejność pracy w praktyce

1. Etap 1 w całości (fundament — bez tego reszta nie ma sensu).
2. Etap 2 w całości (bezpieczeństwo + dane do wykorzystania).
3. Etap 3 i 4 równolegle (obie tylko odczytują, żadna nie blokuje drugiej).
4. Etap 5 (najbardziej złożony logicznie — zacząć od reguł prostych progowych, dopiero potem reguły łączone).
5. Etap 6 (krótki, zależny tylko od 5).
6. Etap 7 (najkrótszy, można zrobić w dowolnym momencie po Etapie 4).
