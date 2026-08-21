# Moduł `device_identity`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).
>
> **Status: zaimplementowane, backend przechodzi pełny flow end-to-end.** Backend jest kompletny strukturalnie i funkcjonalnie (modele, API, migracja, testy) — dwa wcześniejsze blokujące bugi (weryfikacja podpisu, auto-tworzenie `Device` przy pierwszym `verify`) naprawione 2026-08-21, patrz [§7](#7-znane-problemy-i-ograniczenia) (zachowane jako historia zmiany). Firmware pozostaje w fazie planowania — patrz [`docs/plan/firmware_device_identity_implementation_plan.md`](../plan/firmware_device_identity_implementation_plan.md).

## 1. Cel modułu

`device_identity` implementuje asymetryczną autentykację urządzeń IoT, zastępując stary mechanizm — statyczny współdzielony sekret (`X-Device-Key` weryfikowany wobec `Device.hashed_secret`, usunięty całkowicie, bez fallbacku). Nowy schemat:

1. **Klucz publiczny przechowywany w bazie** — backend zna tylko publiczny klucz EC (P-256), nigdy klucz prywatny.
2. **Dowód posiadania przez challenge/response** — claim urządzenia wymaga podpisania jednorazowego nonce kluczem prywatnym.
3. **Sesyjne tokeny do telemetrii** — urządzenie otrzymuje krótkotrwały JWT (`type: "device"`) zamiast wysyłania podpisu z każdym pakietem.

Moduł oddzielony zarówno od `core_data` (zakłada urządzenie przypisane do organizacji — patrz [`02_core_data_module.md`](./02_core_data_module.md)), jak i od `security` (skupia się na ludzkich userach — [`03_security_module.md`](./03_security_module.md)); konsumowany przez inne moduły wyłącznie przez wstrzykiwane zależności (`get_current_device` itp.), nigdy przez `device_identity/repositories/` bezpośrednio.

## 2. Model domenowy

### 2.1 `device_credentials` (`models/device_credential.py`)

| Kolumna | Typ | Opis |
|---|---|---|
| `id` | UUID (PK) | |
| `serial_number` | `String(64)`, unique, indexed, NOT NULL | Numer seryjny urządzenia (jawny, nie sekret) |
| `public_key_pem` | `Text`, NOT NULL | Klucz publiczny EC (P-256), PEM/SPKI |
| `status` | `String(20)`, NOT NULL, default `"unclaimed"` | `"unclaimed"` / `"pending"` / `"claimed"` / `"revoked"` |
| `pending_water_object_id` | UUID, nullable | Cel aktualnej próby claim. **Bez `ForeignKey`** — ani w ORM, ani w DB (patrz [§4](#4-kluczowe-reguły-i-niezmienniki)) |
| `pending_challenge` | `String(64)`, nullable | Jednorazowy nonce (base64url, `secrets.token_urlsafe(32)`) |
| `challenge_expires_at` | `DateTime(timezone=True)`, nullable | TTL wyzwania |
| `claimed_device_id` | UUID, nullable, unique | Ustawiane po udanym pierwszym verify. **Bez `ForeignKey`**, jak wyżej |
| `claimed_at` | `DateTime(timezone=True)`, nullable | Timestamp pierwszego udanego verify |
| `created_at`, `updated_at` | `DateTime(timezone=True)`, NOT NULL | `server_default=func.now()`, `onupdate` na `updated_at` |

Status `"revoked"` jest zdefiniowany w schemacie i sprawdzany w `challenge()`, ale **nie istnieje żaden endpoint ani serwis, który go ustawia** — na dziś jest to martwa gałąź kodu, zarezerwowana pod przyszły proces administracyjny.

Zmiany audytowe zapisywane przez `AuditPort` (entity_type: `DEVICE_IDENTITY_CREDENTIAL`), bez dodatkowej kolumny `created_by`.

### 2.2 Zmiany w `core_data.Device` ([`models/device.py`](../../backend/app/modules/core_data/models/device.py))

- **Usunięto** `hashed_secret` — całkowita wymiana, bez fallbacku.
- **Dodano** `device_credential_id: UUID` — `ForeignKey("device_credentials.id")`, unique, NOT NULL, indexed. Jedyna realna FK spinająca oba modele (w przeciwną stronę, `device_credentials → devices`, nie ma FK — patrz wyżej).
- `external_id` zachowany (zawsze równy `serial_number` powiązanego `DeviceCredential`), zero zmian w `telemetry`/`measurement_points`.
- Device **nie przechowuje** tokenów sesyjnych — bezstanowe JWT, jak tokeny userów.

## 3. Struktura API

Moduł wystawia trzy routery, każdy zamontowany w [`main.py`](../../backend/app/main.py) z innym prefixem:

| Plik | Endpointy | Prefix montowania | Autoryzacja |
|---|---|---|---|
| `api/provisioning.py` | `POST /device-provisioning` | `{API_V1_PREFIX}/platform` | `require_platform_permission("PLATFORM_MANAGE_DEVICE_PROVISIONING")` |
| `api/device_auth.py` | `POST /devices/auth/challenge`, `POST /devices/auth/verify` | *(brak — routy już zawierają pełną ścieżkę)* | Brak — device-facing, dowód tożsamości to sam podpis |
| `api/claims.py` | `POST /orgs/{org_id}/devices`, `GET /orgs/{org_id}/devices/claims/{serial_number}` | `{API_V1_PREFIX}` | `require_org_access("CAN_MANAGE_ASSETS")` (POST), `require_org_access("CAN_VIEW_ASSETS")` (GET) |

Stary `POST /orgs/{org_id}/devices` (create-with-secret) w `core_data/api/devices.py` został **całkowicie usunięty** — `claims.py` jest jedynym właścicielem tej ścieżki, brak kolizji routingu. `core_data/api/devices.py` zachowuje tylko `GET`/`PATCH`/`DELETE`.

### 3.1 `POST /api/v1/platform/device-provisioning`

Rejestruje nowe urządzenie z jego kluczem publicznym.

```json
// Request
{ "serial_number": "DE:AD:BE:EF:00:01", "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----" }

// Response — status 200 OK (nie 201 — brak status_code na dekoratorze routy)
{ "serial_number": "DE:AD:BE:EF:00:01", "status": "unclaimed" }
```

Błędy: `409 Conflict` — SN już zarejestrowany (`ConflictError` w `services/provisioning.py`, brak re-provisioningu w tej iteracji); `401`/`403` ze standardowego łańcucha `require_platform_permission`.

### 3.2 `POST /devices/auth/challenge`

```json
// Request
{ "serial_number": "DE:AD:BE:EF:00:01" }
// Response
{ "serial_number": "DE:AD:BE:EF:00:01", "challenge": "<nonce base64url>" }
```

Logika (`services/device_auth.py::challenge`, w `transaction(skip_audit=True)`):
1. `find_by_serial_number` → `404 Not Found` jeśli SN nieznany.
2. `status == "revoked"` → **`401 Unauthorized`** (`AuthenticationError` — nie `403` jak można by oczekiwać; `ForbiddenError` istnieje jako osobna klasa, ale nie jest tu użyta).
3. `status == "unclaimed"` i brak `pending_water_object_id` → `400 Bad Request`.
4. W przeciwnym razie generuje `secrets.token_urlsafe(32)` (32 losowe bajty, base64url), ustawia TTL = `settings.device_challenge_expire_seconds` (domyślnie 300s).

### 3.3 `POST /devices/auth/verify`

```json
// Request
{ "serial_number": "DE:AD:BE:EF:00:01", "signature": "<DER ECDSA, base64>" }
// Response
{ "token": "<JWT>", "token_type": "bearer", "expires_at": "2026-08-22T10:45:30Z" }
```

Logika (`services/device_auth.py::verify`, w `transaction()`):
1. Brak `pending_challenge` → `400 Bad Request`.
2. Challenge wygasł → czyści challenge, `410 Gone`.
3. Base64-decode podpisu nieudany → `400 Bad Request`.
4. `verify_signature()` zwraca `False` → `401 Unauthorized`.
5. Czyści challenge (jednorazowe użycie).
6. Jeśli `claimed_device_id is None` (pierwsza weryfikacja — status `"unclaimed"` lub `"pending"` po claimie operatora) → tworzy `Device` przez `DeviceService.create_claimed()`, ustawia credential na `claimed`. W przeciwnym razie (re-auth już sclaimowanego urządzenia) → pobiera istniejący `Device` po `claimed_device_id`.
7. Wydaje token przez `TokenService.create_device_token({"sub": device.id, "sn": ..., "water_object_id": ...})`.

### 3.4 `POST /api/v1/orgs/{org_id}/devices` — claim przez operatora

```json
// Request
{ "serial_number": "DE:AD:BE:EF:00:01", "water_object_id": "550e8400-..." }
// Response
{ "serial_number": "DE:AD:BE:EF:00:01", "status": "pending" }
```

Logika (`services/claims.py::request_claim`): sprawdza dostęp do `water_object_id` w organizacji, po czym **zawsze** ustawia `credential.status = "pending"` razem z `pending_water_object_id` (nawet gdy credential było wcześniej `"unclaimed"`). Ponowny claim na *ten sam* `water_object_id` jest idempotentny (brak błędu). Konflikty: `409` jeśli credential już `"claimed"`, albo ma `pending_water_object_id` ustawiony na *inny* obiekt.

### 3.5 `GET /api/v1/orgs/{org_id}/devices/claims/{serial_number}` — status claim

Zwraca `{ "serial_number": ..., "status": ... }` dla polling przez UI operatora. Cross-org dostęp zwraca `404` (nie `403`), spójnie z resztą wzorca w `core_data` (patrz [`02_core_data_module.md`§3](./02_core_data_module.md#3-kluczowe-reguły-i-niezmienniki)).

### 3.6 Telemetry ingest — zmiana autoryzacji

`POST /telemetry/ingest` w `telemetry/api/ingest.py`: stara autoryzacja `X-Device-Key` całkowicie usunięta, zastąpiona `Authorization: Bearer <device_token>` przez zależność [`get_current_device`](../../backend/app/modules/device_identity/dependencies.py) (patrz [§4](#4-kluczowe-reguły-i-niezmienniki)). `TelemetryIngestService.ingest()` dodatkowo sprawdza `packet.device_id == device.external_id` → `403 Forbidden` przy niezgodności (zapobiega podszyciu się pod inny SN nawet z ważnym tokenem). Zaktualizowano też opis w [`04_telemetry_module.md`](./04_telemetry_module.md#4-nieoczywiste-decyzje-projektowe).

### 3.7 Weryfikacja podpisu i tokeny — biblioteka wewnętrzna

`services/signature.py::verify_signature(public_key_pem: str, message: bytes, signature_der: bytes) -> bool` — ECDSA P-256 + SHA256 przez `cryptography` (`serialization.load_pem_public_key`). Łapie `InvalidSignature`, `ValueError`, `TypeError`, `AttributeError` i zwraca `False`.

`security/services/token.py::TokenService.create_device_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, datetime]` — claim `type: "device"`, `exp` = +`settings.device_token_expire_hours` (domyślnie 36h). Ta sama biblioteka (`python-jose`) i ten sam serwis co tokeny userów — różni się tylko jednostką czasu wygaśnięcia i wartością `type`. Bezstanowy, brak persystencji/rotacji.

## 4. Kluczowe reguły i niezmienniki

- **Klucz prywatny nigdy nie trafia do backendu** — backend zna wyłącznie klucz publiczny.
- **Challenge jest jednorazowy i ma TTL** — `pending_challenge` czyszczony po jednym użyciu lub przeterminowaniu; ponowne użycie tego samego nonce → `410 Gone`.
- **SN sam w sobie nie jest dowodem tożsamości** — `POST /orgs/{org_id}/devices` oznacza *intencję* (ustawia `pending_water_object_id`); rzeczywiste powiązanie następuje wyłącznie po `verify` z walidnym podpisem.
- **`get_current_device`** (`dependencies.py`) — dekoduje bearer token, wymaga `type == "device"` i poprawnego UUID w `sub`, ładuje `Device` przez `find_by_id_unscoped`, sprawdza `is_active`. **Wszystkie ścieżki błędu zwracają `401`** (raw `HTTPException`, nie hierarchia `BaseAppException`) — nawet nieznane/nieaktywne urządzenie, bez rozróżnienia na `403`/`404`.
- **Referencyjna integralność `pending_water_object_id`/`claimed_device_id` jest wyłącznie logiczna** — brak `ForeignKey` w ORM i w bazie (potwierdzone też w migracji: brak `ForeignKeyConstraint` dla tych dwóch kolumn, jest tylko `UniqueConstraint('claimed_device_id')`). Ewentualne usunięcie `WaterObject` lub `Device` bez odpowiedniej logiki serwisowej nie zostanie wychwycone przez bazę.
- **Entity type w audit:** `DEVICE_IDENTITY_CREDENTIAL` — zapisywane zdarzenia provisioning i claim (operator context); `challenge`/`verify` idą przez `transaction(skip_audit=True)` — device request, nie zmiana wywołana przez usera.

## 5. Nieoczywiste decyzje projektowe

**`create_claimed()` sam zapisuje audit, `verify()` musi to wiedzieć.** `DeviceService.create_claimed()` (`core_data/services/devices.py`) tworzy wiersz `Device` **i** zapisuje wpis audytowy `CORE_DATA_DEVICE`/`CREATE` we własnej transakcji. `device_auth.py::verify()` woła to wewnątrz swojej własnej `transaction()` na `device_credentials`, więc musi jawnie wywołać `tx.skip_audit()` na zewnętrznej transakcji — inaczej `AuditAwareSession` zablokowałby commit z powodu podwójnego audytu (mechanizm opisany w [`01_backend-architecture.md`](./01_backend-architecture.md#42-infrastructure)).

**Provisioning i claim to świadomie oddzielone kroki, nawet dla tego samego operatora.** Provisioning (platform-level, `PLATFORM_MANAGE_DEVICE_PROVISIONING`) rejestruje klucz publiczny bez wiedzy o żadnej organizacji. Claim (org-level, `CAN_MANAGE_ASSETS`) wiąże SN z `water_object_id` **przed** faktycznym potwierdzeniem przez urządzenie — model "intencja, potem dowód", żeby operator mógł przygotować przypisanie zanim urządzenie w ogóle wystartuje w terenie.

## 6. Procedury operacyjne

### 6.1 Migracja Alembic

**Plik:** [`backend/alembic/versions/20260821_192715_ac83f3034632_replace_device_shared_secret_with_.py`](../../backend/alembic/versions/20260821_192715_ac83f3034632_replace_device_shared_secret_with_.py)

**Upgrade:**
1. Tworzy tabelę `device_credentials` (wszystkie kolumny, unique constraint na `claimed_device_id`, unique index na `serial_number`) — **bez FK** na `pending_water_object_id`/`claimed_device_id`.
2. `DELETE FROM devices` — istniejące wiersze (dane testowe) nie mają odpowiadających credentiali, muszą zniknąć, by ustawić `device_credential_id NOT NULL`.
3. Dodaje `devices.device_credential_id` (NOT NULL, unique, FK → `device_credentials.id`).
4. Usuwa `devices.hashed_secret`.

**Downgrade:** dodaje z powrotem `devices.hashed_secret` jako **`NOT NULL`** (nie nullable — uwaga, to inaczej niż mogłoby się wydawać z samej nazwy operacji; niegroźne tylko dlatego, że tabela jest w tym momencie pusta), usuwa `device_credential_id`, usuwa tabelę `device_credentials`. Usunięte wiersze `devices` **nie są odzyskiwane**.

**Aplikacja:**
```bash
cd backend
alembic upgrade head
```

### 6.2 Ręczne sprowizjonowanie urządzenia do testów

Pełny przepływ: provisioning → claim → challenge → verify → telemetry.

**Krok 1 — Provisioning** (wymaga `PLATFORM_MANAGE_DEVICE_PROVISIONING`):

```bash
curl -X POST http://localhost:8000/api/v1/platform/device-provisioning \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "DE:AD:BE:EF:00:01",
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE+r3tR...\n-----END PUBLIC KEY-----"
  }'

# 200 OK
# { "serial_number": "DE:AD:BE:EF:00:01", "status": "unclaimed" }
```

**Krok 2 — Claim przez operatora** (wymaga `CAN_MANAGE_ASSETS` w organizacji):

```bash
curl -X POST http://localhost:8000/api/v1/orgs/{org_id}/devices \
  -H "Authorization: Bearer <operator_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "DE:AD:BE:EF:00:01",
    "water_object_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# 200 OK
# { "serial_number": "DE:AD:BE:EF:00:01", "status": "pending" }
```

**Krok 3 — Challenge** (z urządzenia, bez auth):

```bash
curl -X POST http://localhost:8000/devices/auth/challenge \
  -H "Content-Type: application/json" \
  -d '{"serial_number": "DE:AD:BE:EF:00:01"}'

# 200 OK
# { "serial_number": "DE:AD:BE:EF:00:01", "challenge": "<nonce>" }
```

Nonce ważny 300s (`device_challenge_expire_seconds`).

**Krok 4 — Verify** (z urządzenia, bez auth):

```bash
curl -X POST http://localhost:8000/devices/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "DE:AD:BE:EF:00:01",
    "signature": "MEUCIQD1qHqYIXPILx..."
  }'
```

Wymaga poprawnego podpisu ECDSA P-256/SHA256 nad `pending_challenge` z kroku 3, wygenerowanego kluczem prywatnym odpowiadającym `public_key_pem` z kroku 1 (do szybkiego testu: `cryptography` w Pythonie — `private_key.sign(challenge.encode(), ec.ECDSA(hashes.SHA256()))`, `signature` w requeście to base64 tego DER-a).

Po udanym verify: credential → `claimed`, `Device` tworzony automatycznie (niezależnie od tego, czy status przed weryfikacją był `"unclaimed"` czy `"pending"` — decyduje `claimed_device_id is None`, patrz §3.3 pkt 6), token wydany (ważny 36h domyślnie).

**Krok 5 — Telemetry ingest** (z tokenem z kroku 4):

```bash
curl -X POST http://localhost:8000/telemetry/ingest \
  -H "Authorization: Bearer <device_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DE:AD:BE:EF:00:01",
    "seq": 1,
    "sent_at": "2026-08-21T09:00:00Z",
    "payload": {}
  }'

# 202 Accepted
```

`packet.device_id` musi równać się `device.external_id` (= serial number), inaczej `403`.

### 6.3 `seed_database.py`

W przeciwieństwie do wcześniejszego założenia planistycznego, **`backend/scripts/seed_database.py` aktywnie tworzy 5 testowych urządzeń**, z pominięciem provisioning/claim/verify: helper `create_test_device(session, external_id, water_object_id, firmware_version)` tworzy `DeviceCredential(status="claimed", public_key_pem=<dummy PEM>)` i powiązany `Device` bezpośrednio przez ORM. Urządzenia: `esp32-a7670e-0001`, `FR-INTAKE-001`, `FR-TREATMENT-001`, `RAD-INTAKE-001`, `RAD-TREATMENT-001`. Najszybszy sposób uzyskania urządzeń z aktywną telemetrią lokalnie bez generowania prawdziwej pary kluczy EC i przechodzenia całego flow provisioning→claim→verify (który teraz też działa, patrz §6.2).

## 7. Znane problemy i ograniczenia

### 7.1 ✅ (naprawione 2026-08-21) `verify_signature()` zawsze zwracał `False`

`services/signature.py` wołał nieistniejącą `ec.load_pem_public_key(...)` z modułu `cryptography.hazmat.primitives.asymmetric.ec`. Ponieważ funkcja łapała `AttributeError` w bloku `except`, błąd był cicho tłumaczony na `False` zamiast crashować — każde wywołanie zwracało odmowę, niezależnie od poprawności podpisu.

**Fix:** import zmieniony na właściwą lokalizację, `cryptography.hazmat.primitives.serialization.load_pem_public_key` ([`services/signature.py`](../../backend/app/modules/device_identity/services/signature.py)). Zweryfikowane `test_signature.py::test_verify_signature_valid` (przechodzi z realną parą klucz/podpis wygenerowaną w teście).

### 7.2 ✅ (naprawione 2026-08-21) Ścieżka auto-tworzenia `Device` przy pierwszym verify była nieosiągalna

`verify()` tworzył `Device` (przez `DeviceService.create_claimed()`) tylko gdy `credential.status == "unclaimed"`. Jednak `services/claims.py::request_claim` **zawsze** przestawia status na `"pending"` w momencie claimu przez operatora — nigdy nie zostawiał `"unclaimed"` z ustawionym `pending_water_object_id`. W efekcie pierwszy realny `verify` po claimie trafiał w gałąź `_handle_reauth`, która szukała `Device` po `claimed_device_id` — wciąż `None` — i zwracała `404 Not Found` zamiast utworzyć urządzenie.

**Fix:** warunek w `verify()` zmieniony z `credential.status == "unclaimed"` na `credential.claimed_device_id is None` ([`services/device_auth.py`](../../backend/app/modules/device_identity/services/device_auth.py)) — pierwsza weryfikacja tworzy `Device` niezależnie od dokładnej wartości `status`, druga (z ustawionym `claimed_device_id`) idzie ścieżką re-auth. `request_claim` pozostaje bez zmian (nadal zawsze ustawia `"pending"`). Brak było testu integracyjnego przechodzącego pełny łańcuch provisioning→claim→challenge→verify, co jest powodem, dla którego luka nie została wykryta wcześniej — takiego testu nadal brakuje (por. §7.5).

### 7.3 Drobniejsze rozbieżności względem pierwotnego planu

- Provisioning zwraca `200 OK`, nie `201 Created` (brak `status_code` na dekoratorze routy).
- Challenge dla urządzenia `"revoked"` zwraca `401`, nie `403` (`AuthenticationError`, nie `ForbiddenError`).
- `pending_water_object_id`/`claimed_device_id` w `device_credentials` nie mają rzeczywistych FK — ani w ORM, ani w migracji.
- Downgrade migracji przywraca `hashed_secret` jako `NOT NULL`.

### 7.4 Odłożone świadomie (bez zmian względem pierwotnego planu)

- **Brak rotacji klucza / re-provisioningu** — ponowna rejestracja tego samego SN zwraca `409`. Scenariusz „urządzenie utraciło klucz" wymaga w przyszłości dedykowanego procesu administracyjnego (status `"revoked"` + nowa rejestracja) — sam status już istnieje w modelu (§2.1), ale nie ma endpointu, który by go ustawiał.
- **Frontend konsumujący stary `DeviceCreateResponse.secret`** wymaga aktualizacji do nowego kontraktu (bez sekretu, plus polling statusu claim przez `GET .../claims/{serial_number}`).
- **Flash Encryption / Secure Boot firmware** — odłożone, patrz [`docs/plan/07_firmware_device_provisioning.md`](../plan/07_firmware_device_provisioning.md#6-znane-ograniczenia--świadomie-odłożone) (dokument planistyczny, częściowo nieaktualny — patrz [`docs/plan/firmware_device_identity_implementation_plan.md`](../plan/firmware_device_identity_implementation_plan.md) jako aktualny plan). Backend nie zależy od tego wyboru.
- **Firmware implementation pending** — `lib/DeviceIdentity`, `lib/ClaimClient`, `firmware/tools/provision.py` jeszcze nie istnieją.

### 7.5 Stan testów (zaktualizowane 2026-08-21)

- `device_identity/tests/test_api_endpoints.py` nadal nie da się skolekcjonować — `ImportError: cannot import name 'router'` (moduł eksportuje `device_auth_router`, nie `router`). Nienaprawione.
- `test_signature.py`, `test_device_auth_service.py` i `test_provisioning_service.py` — wszystkie 16 testów przechodzi. Poprawione przy okazji naprawy §7.1/§7.2:
  - `test_provisioning_service.py::platform_ctx` konstruował `User(password_hash=..., ...)` bez `username` — model `User` ma `hashed_password`/`username`, nie `password_hash`. Fixture poprawiony.
  - `test_device_auth_service.py::test_verify_invalid_signature` i `::test_verify_invalid_signature_encoding` miały zamienione intencje: string `"badsig"` (zła zakładka base64) failował na dekodowaniu zamiast na weryfikacji podpisu, a `"not_hex_zz"` dekodował się po cichu (Python `b64decode` bez `validate=True` ignoruje niepoprawne znaki) zamiast rzucić błąd kodowania. Stringi testowe zamienione miejscami.
- Testy integracyjne w `core_data`/`telemetry` wymagają uruchomionej migracji (`alembic upgrade head`) na testowej bazie — bez tego failują z `relation "device_credentials" does not exist`.
