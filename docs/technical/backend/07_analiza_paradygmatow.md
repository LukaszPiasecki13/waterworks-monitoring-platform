# Analiza niezapisanych paradygmatów backendu

> Wynik zlecenia **B-04** ([`docs/plan/01_briefy_dla_agentow.md`](../../plan/01_briefy_dla_agentow.md#b-04--niezapisane-paradygmaty-backendu--analiza-autonomiczna--adr)).
> Zakres: `backend/app/` (wszystkie moduły) + warstwa styku ([`sensor_registry.yaml`](../../../sensor_registry.yaml), schematy payloadów, kontrakt API konsumowany przez frontend).
> Firmware i frontend jako **kod** są poza zakresem — pojawiają się wyłącznie tam, gdzie są drugą stroną kontraktu.
> Stan repozytorium w chwili analizy: `main` @ `43116cd`.

---

## Spis treści

- [0. Jak to było robione](#0-jak-to-było-robione)
- [1. 🛑 Blokujące ustalenie: backend w tej chwili się nie importuje](#1--blokujące-ustalenie-backend-w-tej-chwili-się-nie-importuje)
- [2. Potwierdzone wzorce — klasyfikacja i dowody](#2-potwierdzone-wzorce--klasyfikacja-i-dowody)
- [3. Hipotezy z briefu — werdykt punkt po punkcie](#3-hipotezy-z-briefu--werdykt-punkt-po-punkcie)
- [4. Audyt zgodności z regułami `ai-tools/.claude/rules/`](#4-audyt-zgodności-z-regułami-ai-toolsclauderules)
- [5. Proponowane korekty istniejących reguł i dokumentacji](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji)
- [6. Lista długu technicznego](#6-lista-długu-technicznego)
- [7. Pytania do rozstrzygnięcia](#7-pytania-do-rozstrzygnięcia)
- [8. Indeks powstałych ADR-ów](#8-indeks-powstałych-adr-ów)

---

## 0. Jak to było robione

Metoda zgodna z briefem: dla każdego wzorca zebrano **wszystkie** wystąpienia w `backend/app/`, policzono zgodne i niezgodne przypadki, i dopiero na tej podstawie nadano klasyfikację:

| Klasa | Kryterium | Skutek |
|---|---|---|
| **reguła** | wzorzec trzymany blisko 100% w ≥2 modułach, bez kontrprzykładów, albo już opisany w [`01_backend-architecture.md`](./01_backend-architecture.md) / regułach `.claude/rules/` | kandydat na ADR |
| **wyjątek** | reguła złamana w policzalnych miejscach, ale ze wspólnym, dającym się nazwać uzasadnieniem | ADR opisujący regułę **i jej granicę** |
| **dług** | sprzeczność z tym, co dokumentacja deklaruje, bez uzasadnienia; albo nazwa/zachowanie wprowadzające w błąd | wyłącznie [sekcja 6](#6-lista-długu-technicznego), nigdy ADR |
| **brak reguły** | wzorzec występuje, ale rozkład zgodnych/niezgodnych nie daje się wyjaśnić żadnym kryterium | opis w raporcie, bez ADR |

Weryfikacja była statyczna: czytanie kodu, `grep` po wszystkich modułach, oraz parsowanie AST wszystkich plików `backend/app/**/*.py`.
**Czego nie udało się zweryfikować wykonaniem:** w środowisku analizy nie ma `.venv` ani zainstalowanych zależności (`pydantic`, `sqlalchemy`, `fastapi`), a `CLAUDE.md` zakazuje instalacji pakietów bez zgody. Nie uruchomiono więc testów ani aplikacji. Każde ustalenie, które wymaga uruchomienia, jest niżej oznaczone i ma podaną **komendę weryfikującą** — do odpalenia w `.venv`.

---

## 1. 🛑 Blokujące ustalenie: backend w tej chwili się nie importuje

To wyszło mimochodem, przy parsowaniu plików pod kątem wzorców, i przesłania resztę raportu.

**Trzy pliki zawierają składnię Pythona 2**, nielegalną w każdej wersji Pythona 3:

| Plik | Linia | Treść |
|---|---|---|
| [`security/dependencies.py:118`](../../../backend/app/modules/security/dependencies.py#L118) | 118 | `except ValueError, TypeError:` |
| [`device_identity/dependencies.py:133`](../../../backend/app/modules/device_identity/dependencies.py#L133) | 133 | `except ValueError, TypeError:` |
| [`device_identity/services/signature.py:32`](../../../backend/app/modules/device_identity/services/signature.py#L32) | 32 | `except ValueError, TypeError, AttributeError:` |

Poprawna forma (użyta prawidłowo w [`security/services/auth.py:148`](../../../backend/app/modules/security/services/auth.py#L148)) to `except (ValueError, TypeError):` — z nawiasami. Bez nich interpreter zgłasza `SyntaxError: multiple exception types must be parenthesized` **przy imporcie modułu**, a nie dopiero przy wykonaniu tej gałęzi.

Konsekwencje, jeśli ustalenie się potwierdzi na maszynie deweloperskiej:

- `app.modules.security.dependencies` jest importowany przez [`main.py:42`](../../../backend/app/main.py#L42) i przez `conftest.py` → **aplikacja nie wystartuje, a testy nie zbiorą się w ogóle**.
- `device_identity.dependencies` dostarcza `get_current_device` dla `/telemetry/ingest`.
- To nie jest świeża regresja: linie pochodzą z commitów `e6be001` i `5e89b37`, czyli z pierwszego importu backendu.

**Weryfikacja (2 sekundy, bez zależności):**

```bash
cd backend && python -m compileall -q app/modules/security/dependencies.py \
    app/modules/device_identity/dependencies.py \
    app/modules/device_identity/services/signature.py
```

**Dlaczego nikt tego nie złapał** — i to jest właściwy wniosek systemowy, nie sam błąd:

- w repozytorium **nie ma CI** (brak katalogu `.github/`), więc nic nie uruchamia `ruff`/`pytest` na push;
- [`.pre-commit-config.yaml`](../../../.pre-commit-config.yaml) definiuje `ruff-check` na `^backend/`, ale został dodany **tym samym commitem** co feralny kod, więc nigdy się po nim nie przejechał; `ruff` na tych plikach padłby na etapie parsowania.

Naprawa to trzy znaki na plik, ale samo ich poprawienie nie zamyka sprawy — patrz [dług D-01 i D-02](#6-lista-długu-technicznego).

> **Uwaga metodologiczna:** przy tym samym przebiegu AST zgłosiły się jeszcze `core_data/schemas/users.py:11` i `telemetry/schemas/query.py:109`. To **fałszywe trafienia** — składnia generyków PEP 695 (`class PaginatedResponse[T](BaseSchema)`), poprawna od Pythona 3.12, a interpreter użyty do analizy miał 3.11. Projekt deklaruje `requires-python = ">=3.14"`, więc te dwa pliki są w porządku.

---

## 2. Potwierdzone wzorce — klasyfikacja i dowody

### 2.1. Jedna sesja na request; `transaction()` z dowolnego repozytorium obejmuje całą jednostkę pracy — **reguła** → [ADR-0001](../adr/0001-jedna-sesja-na-request.md)

Wszystkie repozytoria dostają sesję przez tę samą zależność `get_db` ([`core/dependencies.py`](../../../backend/app/core/dependencies.py)), więc w obrębie jednego żądania **każde repozytorium trzyma tę samą `Session`**. `SQLRepository.transaction()` nie otwiera własnej transakcji — otwiera blok, który na wyjściu commituje całą sesję.

Wystąpienia, które bez tego założenia byłyby niepoprawne:

| Miejsce | Co robi |
|---|---|
| [`activation_codes.py:214-299`](../../../backend/app/modules/device_identity/services/activation_codes.py#L214-L299) | zapisy przez `credential_repo` domknięte blokiem `code_repo.transaction()` |
| [`device_lifecycle.py:49-71`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L49-L71) | trzy moduły (`telemetry`, `core_data`, `device_identity`) w jednym `device_service.repo.transaction()` |
| [`measurement_points.py:97-119`](../../../backend/app/modules/core_data/services/measurement_points.py#L97-L119) | odczyt przez `device_repo`, zapis przez `repo`, jeden blok |
| [`device_auth.py:91-142`](../../../backend/app/modules/device_identity/services/device_auth.py#L91-L142) | `credential_repo.transaction()` obejmuje `device_service.create_claimed()` |

**Granica reguły (i jej najsłabszy punkt):** `transaction()` **nie jest re-entrantne**. Zagnieżdżenie — jak w `device_auth.verify()` → `create_claimed()`, które otwiera własny `with self.repo.transaction()` — powoduje, że **wewnętrzny blok commituje całą zewnętrzną jednostkę pracy** w połowie operacji. Autor o tym wie: [`device_auth.py:128-129`](../../../backend/app/modules/device_identity/services/device_auth.py#L128-L129) niesie komentarz „Device creation audit already recorded inside create_claimed()" i wymuszony `tx.skip_audit()`, bo wewnętrzny commit skonsumował flagę audytu. To działa, ale to obejście, nie mechanizm → [dług D-06](#6-lista-długu-technicznego).

### 2.2. Commit bez wpisu audytowego jest niemożliwy; wyjątki mają jedno kryterium — **reguła + wyjątek** → [ADR-0002](../adr/0002-niezmiennik-audytu-przy-commicie.md)

`AuditAwareSession.commit()` ([`factory.py:15-24`](../../../backend/app/infrastructure/sql/factory.py#L15-L24)) rzuca `MissingAuditRecordError`, jeśli w sesji nie ustawiono `info["audit_recorded"]`. Flagę ustawia wyłącznie `AuditRepository.mark_recorded()`, wołane z `SqlAuditService.record()`. Niezmiennik jest wymuszony na poziomie SQLAlchemy, nie konwencją w serwisie.

Wszystkie 17 miejsc pominięcia audytu (poza infrastrukturą i testami) dzieli się na **dwie rozłączne kategorie plus jeden nazwany wyjątek**:

**A. `transaction(skip_audit=True)` — całą operację inicjuje urządzenie, nie człowiek** (2 wystąpienia):
- [`ingest.py:131`](../../../backend/app/modules/telemetry/services/ingest.py#L131) — pakiet telemetryczny,
- [`device_auth.py:54`](../../../backend/app/modules/device_identity/services/device_auth.py#L54) — zapis nonce'a challenge'u.

**B. `tx.skip_audit()` — operacja użytkownika, która *okazała się* nic nie zmieniać** (12 wystąpień: [`devices.py:160`](../../../backend/app/modules/core_data/services/devices.py#L160), [`measurement_points.py:145`](../../../backend/app/modules/core_data/services/measurement_points.py#L145), [`users.py:151`](../../../backend/app/modules/core_data/services/users.py#L151), [`water_objects.py:104`](../../../backend/app/modules/core_data/services/water_objects.py#L104), [`organizations.py:109`](../../../backend/app/modules/core_data/services/organizations.py#L109), [`auth.py:128`](../../../backend/app/modules/security/services/auth.py#L128), `groups.py:204,223,279,302,341`, [`activation_codes.py:244`](../../../backend/app/modules/device_identity/services/activation_codes.py#L244)) — zawsze poprzedzone sprawdzeniem `if not calculate_delta(...)` albo idempotentnym powtórzeniem żądania. Plus 2 wystąpienia podprzypadku: [`device_auth.py:129,173`](../../../backend/app/modules/device_identity/services/device_auth.py#L129) — audyt już zapisało wywołanie zagnieżdżone.

Jedyne wystąpienie poza tym podziałem (17. z 17): [`seed.py:40`](../../../backend/app/modules/security/services/seed.py#L40) woła `perm_repo.commit(skip_audit=True)` bezpośrednio, z pominięciem `transaction()` — seed startowy, poza ścieżką żądania. Uzasadnione, ale to jedyny commit w kodzie produkcyjnym poza `transaction()` → [dług D-11](#6-lista-długu-technicznego).

Klasyfikacja odrzucona: „wyjątki `skip_audit` są ad hoc". Odrzucona, bo 16/17 wystąpień daje się przypisać do jednej z dwóch kategorii bez naciągania.

### 2.3. Aktorem audytu bywa urządzenie — **reguła** → [ADR-0003](../adr/0003-aktor-audytu-jako-napis.md)

`AuditEntry.actor_id` to `str`, a `audit_events.actor_id` to `String(255)` bez FK do `users` ([`models/audit.py:49`](../../../backend/app/modules/audit/models/audit.py#L49)). Powód widać w danych, nie w typie:

- człowiek: `actor_id=str(user.id)`, `actor_display_name=user.email` (większość serwisów);
- urządzenie: `actor_id=str(credential.id)`, `actor_display_name=f"device:{serial_number}"` — [`device_auth.py:154-155`](../../../backend/app/modules/device_identity/services/device_auth.py#L154-L155) i [`activation_codes.py:295-296`](../../../backend/app/modules/device_identity/services/activation_codes.py#L295-L296).

Bez tej decyzji rejestracja urządzenia (pierwszy claim, redeem kodu) nie miałaby jak trafić do append-only logu, bo nie stoi za nią żaden użytkownik.

### 2.4. Autoryzacja żyje wyłącznie na granicy API — **reguła** → [ADR-0004](../adr/0004-autoryzacja-na-granicy-api.md)

Serwis **nigdy** nie sprawdza uprawnień. Dostaje gotowy, udowodniony kontekst: `OrganizationAccess` albo `PlatformContext` — oba `@dataclass(frozen=True)` ([`access.py:10,23`](../../../backend/app/modules/security/access.py#L10)).

- `require_org_access(*codes)` łączy sprawdzenie członkostwa (**404**, żeby nie zdradzić istnienia cudzej gminy) z sprawdzeniem uprawnień (**403**) — [`dependencies.py:166-180`](../../../backend/app/modules/security/dependencies.py#L166-L180).
- Serwisy przyjmują `org_access` jako argument i **ufają mu**; kontrakt jest zapisany w docstringach klas, identycznie w [`DeviceService`](../../../backend/app/modules/core_data/services/devices.py#L15-L20) i [`MeasurementPointService`](../../../backend/app/modules/core_data/services/measurement_points.py#L23-L28): „Callers are expected to have already validated organization membership and permissions".
- Zero wywołań `has_permission` / `permissions_for_user` w warstwie serwisów biznesowych — jedynym konsumentem `PermissionService` jest warstwa `dependencies.py`.

Kontrprzykładów brak. Wariant stylistyczny: `telemetry/api/query.py` deklaruje zależność w `dependencies=[Depends(...)]` dekoratora, `core_data/api/*` — jako parametr `_org_access` z podkreśleniem. Oba są poprawne, ale niejednolite → [dług D-12](#6-lista-długu-technicznego).

### 2.5. Dwie płaszczyzny dostępu = dwa routery na zasób — **reguła** → [ADR-0005](../adr/0005-dwie-plaszczyzny-dostepu.md)

Ten sam zasób jest wystawiony dwa razy, w dwóch niezależnych routerach w jednym pliku: `router` (`/orgs/{org_id}/devices`, kody `CAN_*`) i `platform_router` (`/devices`, kody `PLATFORM_*`) — [`api/devices.py:31,34`](../../../backend/app/modules/core_data/api/devices.py#L31-L34), analogicznie `water_objects`, `users`, `activation_codes`. Prefiks `/api/v1/platform` doklejany jest dopiero przy montażu w [`main.py:124-131`](../../../backend/app/main.py#L124-L131). Płaszczyzny opisuje [`01_backend-architecture.md §7`](./01_backend-architecture.md#7-płaszczyzny-dostępu-i-routing-api), ale nigdzie nie zapisano *dlaczego* to dwa routery, a nie jeden z rozgałęzieniem po uprawnieniu.

### 2.6. Endpointy urządzeniowe stoją poza `/api/v1` — **reguła** → [ADR-0006](../adr/0006-endpointy-urzadzeniowe-poza-api-v1.md)

[`main.py:110-121`](../../../backend/app/main.py#L110-L121) montuje bez prefiksu: `/auth/*`, `/telemetry/ingest`, `/devices/auth/*`, `/devices/activation/*`. Wszystko inne dostaje `/api/v1`. Druga strona kontraktu jest zaszyta w firmware — [`firmware/include/Config.h:46,53-55`](../../../firmware/include/Config.h#L46) trzyma dokładnie te ścieżki jako `const char[]`. To najtrudniejsza do odwrócenia decyzja w całym repozytorium: zmiana ścieżki wymaga flashowania urządzeń w terenie.

### 2.7. Telemetria jest luźno związana z rejestrem urządzeń — **reguła** → [ADR-0007](../adr/0007-telemetria-bez-fk-do-rejestru.md)

`telemetry_packets.device_id` to `String(128)` = `Device.external_id`, **bez klucza obcego** ([`models/measurement_packet.py:31`](../../../backend/app/modules/telemetry/models/measurement_packet.py#L31)). Potwierdzenie w kodzie kasującym: [`device_lifecycle.py:50`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L50) — komentarz „Delete telemetry packets (no FK, must be explicit)". Kontrast: `telemetry_errors.packet_id` **ma** FK z `ondelete="CASCADE"` w obrębie własnego modułu. Czyli reguła jest precyzyjna: FK w obrębie modułu — tak, FK przez granicę modułu — nie.

### 2.8. Operacja wielomodułowa: rdzeń bez commitu, transakcja u orkiestratora — **reguła** → [ADR-0008](../adr/0008-rdzenie-bez-commitu-w-operacjach-wielomodulowych.md)

Dwie metody są jawnie oznaczone jako „nie commituję, transakcja należy do wołającego":

- [`devices.py:263`](../../../backend/app/modules/core_data/services/devices.py#L263) — `delete_device_record`: „No-commit core — transaction belongs to caller.";
- [`ingest.py:165`](../../../backend/app/modules/telemetry/services/ingest.py#L165) i [`packets.py:86`](../../../backend/app/modules/telemetry/repositories/packets.py#L86) — „Flushes rather than commits: the transaction belongs to the caller."

Konsument: `DeviceLifecycleService`, jedyny orkiestrator w kodzie. Wzorzec jest tym, co pozwala kasować urządzenie atomowo przez trzy moduły — i jest bezpośrednią konsekwencją [ADR-0001](../adr/0001-jedna-sesja-na-request.md).

### 2.9. `sensor_registry.yaml` jako jedno źródło prawdy — **reguła z wyraźną granicą** → [ADR-0009](../adr/0009-sensor-registry-jedno-zrodlo-prawdy.md)

Co registry faktycznie kontroluje:

| Element kontraktu | Egzekwowane? | Gdzie |
|---|---|---|
| identyfikatory `point_type` | ✅ backend | [`ingest.py:49`](../../../backend/app/modules/telemetry/services/ingest.py#L49), [`measurement_points.py:91,129`](../../../backend/app/modules/core_data/services/measurement_points.py#L91) |
| kody błędów | ✅ backend, walidator Pydantic | [`measurement_packet.py:50-59`](../../../backend/app/modules/telemetry/schemas/measurement_packet.py#L50-L59) |
| identyfikatory + kody po stronie firmware | ✅ compile-time `static_assert` | [`PT100Sensor.cpp:7-9`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L7-L9) |
| **`canonical_unit`** | ❌ **nigdzie** | `unit` z pakietu jest przyjmowany jako dowolny `str` (`min_length=1, max_length=32`) i zapisywany do `measurement_points.unit` |
| **kształt payloadu (`v`, `windows`, `points`)** | ❌ registry go nie opisuje | schemat żyje wyłącznie w `measurement_packet.py` i w kodzie firmware |
| `severity` kodu błędu | ❌ | urządzenie przysyła własną `severity`, registry ma swoją — nikt ich nie porównuje |

Nagłówek `firmware/include/SensorRegistry.h` jest **generowany i celowo niekomitowany** ([`.gitignore:15`](../../../.gitignore#L15)), a generator odpalany jako pre-build hook PlatformIO.

**Korekta briefu:** brief B-04 pkt 6 twierdzi, że hook „jest wyłączony". **To nieprawda** — [`platformio.ini:7`](../../../firmware/platformio.ini#L7) ma aktywne `extra_scripts = scripts/prebuild.py`, a [`prebuild.py:203`](../../../firmware/scripts/prebuild.py#L203) rejestruje `env.AddPreAction("$BUILD_DIR/firmware.elf", ...)`. Hook jest podłączony. Ma natomiast dwie realne dziury → [dług D-08 i D-09](#6-lista-długu-technicznego).

### 2.10. Moduł bez `api/`: `audit` wystawia się przez port — **reguła** → [ADR-0010](../adr/0010-modul-bezportowy-audit.md)

`audit` jest **jedynym** z pięciu modułów bez katalogu `api/` (sprawdzone: `core_data`, `security`, `telemetry`, `device_identity` mają). Wystawia się przez dwa protokoły w `core/audit.py`: `AuditPort` (zapis, wstrzykiwany do serwisów biznesowych) i `AuditReaderPort` (odczyt, wstrzykiwany do endpointów cudzych modułów) — [`platform_audit.py:21`](../../../backend/app/modules/security/api/platform_audit.py#L21) i `core_data/api/users.py:121`.

Destylowane kryterium „kiedy moduł jest bezportowy": **kiedy jego dane nie mają samodzielnego przypadku użycia**. Historii audytu nie ogląda się „samej w sobie" — ogląda się ją *dla użytkownika*, *dla grupy*, *dla gminy*. Uprawnienie do jej obejrzenia należy do tamtej encji, nie do audytu, więc endpoint też należy tam. Jedyny wyjątek — globalny podgląd platformowy — mieszka w `security/api/platform_audit.py`, bo jego uprawnieniem jest `PLATFORM_VIEW_AUDIT`, czyli obiekt modułu `security`.

### 2.11. Serwisy CRUD zwracają encje ORM; DTO robi FastAPI — **reguła sprzeczna z dokumentacją** → [ADR-0011](../adr/0011-serwisy-zwracaja-encje-orm.md)

`DeviceService.get_by_id() -> Device`, `MeasurementPointService.create()` zwraca `MeasurementPoint`, `AuthService.update_profile() -> User`. Konwersja na Pydantic dzieje się dopiero w FastAPI, przez `response_model=` + `ConfigDict(from_attributes=True)` — obecne we wszystkich schematach odpowiedzi CRUD (10 plików). Działa to, bo `sessionmaker` ma `expire_on_commit=False` ([`factory.py:98`](../../../backend/app/infrastructure/sql/factory.py#L98)) — encja pozostaje użyteczna po commicie.

To **jest** sprzeczne z przykładem w [`01_backend-architecture.md §5.2`](./01_backend-architecture.md#servicesresourcepy), który pokazuje `return ResourceResponse.model_validate(entity)`. Zgodnie z metodą z briefu (kod konsekwentny + dobry powód ⇒ nieaktualna jest dokumentacja) klasyfikuję to jako regułę, a rozbieżność jako [korektę dokumentacji K-04](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji).

Granica: moduł `telemetry` w warstwie **odczytowej** robi odwrotnie — `TelemetryQueryService` buduje i zwraca gotowe DTO (`ObjectSummaryResponse`, `MeasurementsResponse`), bo agreguje dane z JSONB i nie ma encji do zwrócenia. Kryterium jest więc: **CRUD nad encją → ORM; model odczytowy/agregat → DTO.**

### 2.12. Niezmienna `frozen dataclass` jako nośnik kontekstu — **reguła, ale bez ADR-a**

Pięć wystąpień: `_IngestContext` ([`ingest.py:26`](../../../backend/app/modules/telemetry/services/ingest.py#L26)), `PlatformContext` i `OrganizationAccess` ([`access.py:10,23`](../../../backend/app/modules/security/access.py#L10)), `PermissionDefinition` ([`permission_catalog.py:37`](../../../backend/app/modules/security/permission_catalog.py#L37)), `AuditEntry` ([`core/audit.py:24`](../../../backend/app/core/audit.py#L24), dodatkowo `slots=True`). Wspólne kryterium: **paczka wartości przewlekana przez łańcuch wywołań, której nikt po drodze nie ma prawa zmienić.** Wzorzec potwierdzony.

**Świadomie nie powstaje z tego ADR.** Kryteria z `ai-tools/.claude/skills/domain-modeling/ADR-FORMAT.md` wymagają, by decyzja była *trudna do odwrócenia*, *zaskakująca bez kontekstu* i *wynikiem realnego kompromisu*. Ta nie spełnia żadnego z trzech — to idiom kodowania, nie decyzja architektoniczna. Miejsce dla niej to sekcja konwencji w `01_backend-architecture.md` → [korekta K-05](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji).

### 2.13. Funkcje modułowe zamiast metod serwisu — **brak reguły**

Hipoteza z briefu (pkt 4) mówi: „funkcja bez potrzeby stanu `self` zostaje funkcją". Sprawdzone na wszystkich serwisach:

*Za:* `ingest.py` ma 6 funkcji modułowych (`_authorize`, `_validate_point_type`, `_iter_points`, `_build_response`, `_build_error`, `_packet_reported_errors`); `activation_codes.py` — `_generate_code`, `_hash_code`; `password.py` i `signature.py` to całe pliki bez klasy.

*Przeciw:* pięć metod `_state(self, obj)` w [`devices.py:32`](../../../backend/app/modules/core_data/services/devices.py#L32), [`measurement_points.py:40`](../../../backend/app/modules/core_data/services/measurement_points.py#L40), `organizations.py:39`, `water_objects.py:31`, `users.py:28` **też nie używa `self`** — a mimo to są metodami. Do tego `GroupService._ensure_custom_group` i `_ensure_permissions_editable` są `@staticmethod`, czyli trzecia forma tego samego.

Trzy formy zapisu bezstanowego helpera, bez kryterium, które by je rozdzielało. Werdykt: **wzorzec nie istnieje jako reguła**. Nie ma ADR-a; drobna niespójność trafia na listę długu jako [D-13](#6-lista-długu-technicznego) o niskim priorytecie.

### 2.14. `get_` vs `find_` — **reguła warstwy repozytorium, nie serwisu**

W repozytoriach konwencja jest trzymana **w 100%**: każda metoda `find_*` (9 sztuk: `find_by_id` ×4, `find_in_organization` ×3, `find_by_external_id_unscoped`, `find_by_serial_number`) rzuca `NotFoundError`, każda `get_*` zwracająca pojedynczą encję zwraca `| None`. Bez kontrprzykładów. `get_*` zwracające listę (`get_by_entity`, `get_packets_in_range`) nie należą do tej konwencji — dotyczy ona odczytu pojedynczego obiektu.

W **serwisach** konwencja nie obowiązuje i to jest spójne: `MeasurementPointService.get_by_id` ([`:68`](../../../backend/app/modules/core_data/services/measurement_points.py#L68)) i `DeviceService.get_by_id` ([`:61`](../../../backend/app/modules/core_data/services/devices.py#L61)) **rzucają** — bo w serwisie nazwa opisuje przypadek użycia („pobierz urządzenie"), a nie kontrakt odczytu. Dokumentacja tego rozróżnienia nie zapisuje → [korekta K-03](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji).

Nie tworzę z tego ADR-a: konwencja jest już opisana w `01_backend-architecture.md §5.2`, więc ADR tylko by ją zdublował.

---

## 3. Hipotezy z briefu — werdykt punkt po punkcie

| # | Hipoteza | Werdykt | Klasa | Gdzie |
|---|---|---|---|---|
| 1 | `get_` vs `find_` trzymane wszędzie | **Częściowo.** 100% w repozytoriach, świadomie nieobowiązujące w serwisach. `get_or_create_internal` łamie ją naprawdę: `get_` nigdy nie zwraca `None` i do tego zapisuje | reguła + 1 dług | [2.14](#214-get_-vs-find_--reguła-warstwy-repozytorium-nie-serwisu), [D-05](#6-lista-długu-technicznego) |
| 2 | `audit` jedynym modułem bez `api/` | **Potwierdzone.** 1/5 modułów; kryterium bezportowości wydestylowane | reguła | [2.10](#210-moduł-bez-api-audit-wystawia-się-przez-port--reguła--adr-0010) |
| 3 | `skip_audit=True` ma wspólną cechę | **Potwierdzone i doprecyzowane.** Dwie rozłączne kategorie, nie jedna: „zapis inicjowany przez urządzenie" (2×) i „operacja użytkownika bez realnej zmiany" (13×) | reguła + wyjątek | [2.2](#22-commit-bez-wpisu-audytowego-jest-niemożliwy-wyjątki-mają-jedno-kryterium--reguła--wyjątek--adr-0002) |
| 4 | Funkcje modułowe mają rozpoznawalne kryterium | **Obalone.** Trzy współistniejące formy (funkcja modułowa / metoda bez `self` / `@staticmethod`) bez kryterium rozdzielającego | brak reguły | [2.13](#213-funkcje-modułowe-zamiast-metod-serwisu--brak-reguły) |
| 5 | Frozen dataclass jako kontekst występuje gdzie indziej | **Potwierdzone.** 5 wystąpień, wspólne kryterium. Świadomie bez ADR-a (nie spełnia progu z ADR-FORMAT) | reguła | [2.12](#212-niezmienna-frozen-dataclass-jako-nośnik-kontekstu--reguła-ale-bez-adr-a) |
| 6 | `sensor_registry.yaml` jako źródło prawdy; hook wyłączony | **Reguła potwierdzona, przesłanka o hooku obalona.** Hook jest aktywny w `platformio.ini`, ale ma zepsute ścieżki i nie obejmuje środowiska `native` | reguła + 2 długi | [2.9](#29-sensor_registryyaml-jako-jedno-źródło-prawdy--reguła-z-wyraźną-granicą--adr-0009), [D-08](#6-lista-długu-technicznego), [D-09](#6-lista-długu-technicznego) |
| 7 | `last_diagnostics_at` znaczy „last_seen" | **Potwierdzone, i jest gorzej.** `last_seen_at` istnieje, jest wystawione w API, czytane przez frontend — i **nigdy nie jest zapisywane** przez aplikację | dług (wysoki) | [D-03](#6-lista-długu-technicznego) |
| 8 | Każdy serwis używa `transaction()` | **Potwierdzone.** 36 użyć w kodzie produkcyjnym. Cztery odstępstwa, każde nazwane: `seed.py:40` (seed startowy), `measurement_points.py:183` i `packets.py:64` (rollback po `IntegrityError`), `cli.py` (poza ścieżką żądania) | reguła | [2.1](#21-jedna-sesja-na-request-transaction-z-dowolnego-repozytorium-obejmuje-całą-jednostkę-pracy--reguła--adr-0001) |
| 9 | `extra="forbid"` stosowane konsekwentnie | **Obalone.** Dokładnie **1** wystąpienie w całym backendzie, i nawet ono nie obejmuje modeli zagnieżdżonych | dług | [D-07](#6-lista-długu-technicznego) |

---

## 4. Audyt zgodności z regułami `ai-tools/.claude/rules/`

### 4.1. `python-coding-standards.md`

| Wymaganie reguły | Stan kodu | Ocena |
|---|---|---|
| Line length 88, wcięcie 4, cudzysłowy `"`, isort | `[tool.ruff]` ustawia dokładnie to | ✅ zgodne |
| Query params **zawsze** przez schemat Pydantic + `Depends()` | **12/12** endpointów listujących; zero surowych `Query(...)` | ✅ wzorowo |
| `uv` wyłącznie, commitowany `uv.lock`, bez pip/poetry | `requirements.txt` + `setuptools`; brak `uv.lock` | ❌ systematyczne odstępstwo → [K-01](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji) |
| mypy **strict**, pełne adnotacje wszystkich funkcji | `pyproject.toml`: `strict = false`; `ignore_errors` dla `app.infrastructure.*` i testów. Pokrycie adnotacjami zwrotu: repozytoria 103/117, serwisy 124/159, API **15/66** | ❌ odstępstwo częściowo świadome (API), częściowo przypadkowe (serwisy `core_data`) → [K-02](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji), [D-10](#6-lista-długu-technicznego) |
| Zakaz `except:` bez typu | Brak gołych `except:`. Są za to trzy `except A, B:` — patrz [sekcja 1](#1--blokujące-ustalenie-backend-w-tej-chwili-się-nie-importuje) | ⚠️ inna klasa błędu, gorsza |
| Zakaz mutowalnych argumentów domyślnych | Brak wystąpień | ✅ |
| Złożoność ≤10, funkcja ~50 linii, plik ~300 linii | `max-complexity = 10` ustawione. Jedyne wyraźne przekroczenie długości pliku: `security/services/groups.py` (523 linie przy zaleceniu ~300) | ⚠️ miękkie, nie raportuję jako dług |
| Nazewnictwo (snake_case, PascalCase, `is_`/`has_`) | Zgodne wszędzie, gdzie sprawdzałem | ✅ |
| Docstringi tylko dla publicznego API i nieoczywistej logiki | Kod jest **bardziej** udokumentowany, niż reguła wymaga (docstringi przy prostym CRUD) | ⚠️ nadmiar, nie naruszenie |

### 4.2. `error-handling-patterns.md`

| Wymaganie reguły | Stan kodu | Ocena |
|---|---|---|
| Hierarchia `AppError` → `NotFoundError` / `AuthorizationError` / `DomainValidationError` z polem `code` | Kod ma `APIError` → `BadRequestError` / `NotFoundError` / `ConflictError` / `AuthenticationError` / `ForbiddenError` / `ValidationException` / `GoneError`, każdy z `status_code` i opcjonalnym `code` | ❌ inne nazwy, **bogatsza i spójnie stosowana** hierarchia → [K-06](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji) |
| Kształt odpowiedzi `{"error": {"code", "message"}}` | Kod zwraca `{"detail": ..., "code": ...}` ([`errors.py:73-79`](../../../backend/app/core/errors.py#L73-L79)) — i **frontend czyta dokładnie ten kształt** ([`frontend/src/lib/errors.ts:24-41`](../../../frontend/src/lib/errors.ts#L24-L41)) | ❌ reguła jest nieaktualna, nie kod → [K-06](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji) |
| Serwis rzuca wyjątki domenowe, nigdy `HTTPException` | Serwisy — ✅ bez wyjątku. Warstwa `dependencies.py` (`security`, `device_identity`) rzuca `HTTPException` bezpośrednio, 9 miejsc | ⚠️ świadome: to warstwa zależności FastAPI, nie serwis. Ale niespójne z resztą → [D-14](#6-lista-długu-technicznego) |
| Log raz, w warstwie łapiącej; `logger.exception()` dla nieoczekiwanych | [`errors.py:82-119`](../../../backend/app/core/errors.py#L82-L119): 5xx → `logger.error`, 4xx → `logger.info`, nieobsłużone → `logger.exception`. Zero podwójnego logowania | ✅ wzorowo |
| Nigdy nie wyciekać wewnętrznych szczegółów | Handler `Exception` zwraca stałe `"Internal server error"` | ✅ |

**Ustalenie ponad regułę:** faktycznym kontraktem błędu jest para `(status, code)`, a nie `detail`. Frontend mapuje `code` na polski komunikat przez `domainErrorMessages`, a `detail` traktuje jako fallback. Backend nadaje `code` w **12 miejscach** na 79 wywołań `raise ...Error(...)` w warstwach serwisów i repozytoriów; pozostałe 67 idzie bez kodu, więc do UI trafia surowy angielski tekst z backendu. To wyjaśnia też [D-04](#6-lista-długu-technicznego).

### 4.3. `security-checklist.md`

| Wymaganie reguły | Stan kodu | Ocena |
|---|---|---|
| **Nie używać `python-jose`** (nieutrzymywany od 2022), używać `PyJWT` | `pyproject.toml` → `python-jose[cryptography]`; [`token.py:3`](../../../backend/app/modules/security/services/token.py#L3) → `from jose import JWTError, jwt` | 🔴 **naruszenie** → [D-15](#6-lista-długu-technicznego) |
| `RS256` z walidacją `audience` i `issuer` | `HS256` ([`config.py:29`](../../../backend/app/core/config.py#L29)), brak claimów `aud`/`iss`, brak ich walidacji w `decode_token` | 🔴 **naruszenie** → [D-16](#6-lista-długu-technicznego) |
| Access token 15–30 min | `access_token_expire_minutes = 120` | 🟠 odstępstwo |
| Refresh 7–30 dni, **rotowany przy użyciu** | `refresh_token_expire_days = 1`; `AuthService.refresh` ([`:139-153`](../../../backend/app/modules/security/services/auth.py#L139-L153)) wydaje nową parę, ale starego refresha nie unieważnia (brak listy odwołań) — token żyje do `exp` | 🟠 krótsze życie częściowo kompensuje brak rotacji |
| Refresh w ciasteczku `httpOnly`/`Secure`/`SameSite=Strict`, nigdy w `localStorage` | Refresh jest polem JSON-a w `TokenResponse` i wraca w ciele odpowiedzi `/auth/token` | 🟠 odstępstwo → [D-17](#6-lista-długu-technicznego) |
| Walidacja na granicy, Pydantic z twardymi ograniczeniami | Schematy mają `min_length`/`max_length`/`ge`/`le`/`Literal` konsekwentnie; `ObjectType` i `severity` jako `Literal` | ✅ |
| Zapytania parametryzowane | Wyłącznie SQLAlchemy ORM / Core; zero konkatenacji SQL. Jedyny `exec_driver_sql` ([`factory.py:80`](../../../backend/app/infrastructure/sql/factory.py#L80)) wstawia nazwę schematu przepuszczoną przez `identifier_preparer.quote()` | ✅ poprawnie |
| Brak sekretów w repo, ładowanie z env | `Settings` bez wartości domyślnych dla `database_url` i `secret_key` → brak env = brak startu | ✅ |
| Rate limiting na endpointach auth, login ≤5/min | [`auth.py:21`](../../../backend/app/modules/security/api/auth.py#L21) → `@limiter.limit("5/minute")`. **`/auth/token/refresh` nie jest limitowany** | ⚠️ częściowo → [D-18](#6-lista-długu-technicznego) |
| CSRF: JWT w nagłówku `Authorization` ⇒ CSRF zbędny | Tak właśnie jest | ✅ |

**Zabezpieczenia obecne w kodzie, których reguła nie wymaga** (warto, żeby zostały):
- `enforce_production_hardening` ([`config.py:77-90`](../../../backend/app/core/config.py#L77-L90)) — aplikacja **odmawia startu** w `staging`/`production` przy sekrecie <32 znaków, pustej albo wildcardowej liście CORS;
- `burn_password_verification` ([`password.py:48-50`](../../../backend/app/modules/security/services/password.py#L48-L50)) — logowanie nieistniejącego konta kosztuje tyle samo czasu co istniejącego (obrona przed enumeracją kont po czasie odpowiedzi);
- brak członkostwa w gminie zwraca **404**, nie 403 ([`access.py:54-55`](../../../backend/app/modules/security/access.py#L54-L55)) — nie zdradza istnienia cudzej organizacji;
- `_mask_url` przy logowaniu URL-a bazy ([`factory.py:33-40`](../../../backend/app/infrastructure/sql/factory.py#L33-L40));
- `docs_enabled = not is_production` — `/docs` i `/openapi.json` wyłączone poza devem.

Żadne z nich nie jest opisane w `docs/`. `CLAUDE.md` wymaga dokumentowania nieoczywistych zabezpieczeń → [K-07](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji).

---

## 5. Proponowane korekty istniejących reguł i dokumentacji

### K-01 — `python-coding-standards.md`: menedżer pakietów

Kod nie używa `uv` i nigdy nie używał. To odstępstwo **systematyczne**, więc reguła jest nieaktualna dla tego repozytorium — albo repozytorium ma migrować. Rekomendacja: reguła jest wspólna dla wielu projektów, więc nie kasować jej, tylko dopuścić drugi wariant.

```diff
 ## Package Management

-Use `uv` exclusively - not pip or poetry. Always commit `uv.lock`. Do not commit `.venv/`.
+Use `uv` for new projects - not pip or poetry. Always commit `uv.lock`. Do not commit `.venv/`.
+
+Existing projects on `pip` + `requirements.txt` (e.g. `waterworks-monitoring-platform/backend`)
+stay as they are until a deliberate migration: pin every direct dependency with `>=`
+lower bounds in `pyproject.toml`, and keep `requirements.txt` as the installable lockfile.
```

### K-02 — `python-coding-standards.md`: mypy strict

Reguła mówi „mypy strict, wszystkie funkcje z pełnymi adnotacjami", a kod ma `strict = false` i 51 z 66 handlerów API bez adnotacji zwrotu. **Odstępstwo w warstwie API jest uzasadnione** — kontraktem odpowiedzi jest `response_model=`, a nie adnotacja Pythona. Odstępstwo w serwisach `core_data` uzasadnienia nie ma (patrz [D-10](#6-lista-długu-technicznego)). Reguła powinna to rozróżniać:

```diff
 ## Type Safety (mypy strict)

 All functions must have full type annotations.
+
+Exception - FastAPI route handlers: the response contract is `response_model=` on the
+decorator, which mypy cannot check anyway. A missing return annotation on a handler that
+declares `response_model` is not a finding. Everything below the router - services,
+repositories, helpers - is annotated with no exceptions.
```

### K-03 — `01_backend-architecture.md §5.2`: zasięg konwencji `get_`/`find_`

Konwencja jest opisana bez wskazania warstwy, przez co czytelnik oczekuje jej także w serwisach — a tam jej nie ma i **słusznie**. Do wstawienia po tabeli `get_by_id` / `find_by_id`:

```diff
 | `find_by_id(id)` | Rzuca `NotFoundError` jeśli nie znaleziono | Publiczne API, gdy brak = błąd |
+
+**Konwencja dotyczy wyłącznie warstwy repozytorium.** W serwisach nazwa metody opisuje
+przypadek użycia, nie kontrakt odczytu — `DeviceService.get_by_id()` rzuca `NotFoundError`,
+bo „pobierz urządzenie" bez urządzenia jest błędem. Prefiksy `get_`/`find_` w serwisie
+nie niosą informacji o tym, czy metoda rzuca; niesie ją sygnatura zwrotu.
```

### K-04 — `01_backend-architecture.md §5.2`: co zwraca serwis

Przykład w dokumentacji pokazuje `return ResourceResponse.model_validate(entity)`, a cały kod CRUD zwraca encje ORM (patrz [2.11](#211-serwisy-crud-zwracają-encje-orm-dto-robi-fastapi--reguła-sprzeczna-z-dokumentacją--adr-0011)). Do poprawienia przykład i dopisania zasady:

```diff
 class ResourceService:
     def __init__(self, repository: ResourceRepository):
         self._repo = repository

-    async def create(self, data: ResourceCreateRequest) -> ResourceResponse:
+    def create(self, data: ResourceCreateRequest) -> Resource:
         if await self._repo.exists(name=data.name):
             raise ResourceAlreadyExistsError(data.name)
-        entity = await self._repo.create(data)
-        return ResourceResponse.model_validate(entity)
+        return self._repo.create(data)
+
+**Serwis CRUD zwraca encję ORM, nie DTO.** Konwersję robi FastAPI przez `response_model=`
+i `ConfigDict(from_attributes=True)`. Jest to bezpieczne, bo `sessionmaker` ma
+`expire_on_commit=False` — encja pozostaje użyteczna po commicie.
+Wyjątek: serwisy **odczytowe**, które agregują dane bez odpowiadającej im encji
+(`TelemetryQueryService`), budują i zwracają DTO.
```

### K-05 — `01_backend-architecture.md`: konwencja niezmiennego kontekstu

Do dopisania jako nowy punkt w sekcji 5 (potwierdzony wzorzec, za mały na ADR):

```markdown
### Kontekst przewlekany przez wywołania

Paczka wartości przekazywana w dół łańcucha wywołań jest niemutowalną `@dataclass(frozen=True)`,
a nie słownikiem ani osobnymi argumentami: `OrganizationAccess`, `PlatformContext`,
`AuditEntry`, `_IngestContext`, `PermissionDefinition`. Zapobiega to modyfikacji kontekstu
w połowie operacji przez funkcję pomocniczą — a przy `AuditEntry` dodatkowo gwarantuje,
że zbudowany wpis audytowy dotrze do zapisu w takiej postaci, w jakiej powstał.
```

### K-06 — `error-handling-patterns.md`: kontrakt błędu

Reguła opisuje kontrakt `{"error": {"code","message"}}`, którego w tym repozytorium nie ma i nigdy nie było, a wdrożony kontrakt jest **konsekwentny i konsumowany przez frontend**. Aktualizacja reguły do stanu faktycznego:

```diff
 ### FastAPI Exception Handler (`app/error_handlers.py`)

 - Map codes to HTTP: `NOT_FOUND` → 404, `VALIDATION_ERROR` → 422, `FORBIDDEN` → 403, `CONFLICT` → 409, default → 500.
-- Response shape: `{"error": {"code": "...", "message": "..."}}`.
-- Register: `app.add_exception_handler(AppError, app_error_handler)`.
+- Response shape: `{"detail": "...", "code": "DOMAIN_CODE"}` - `code` present only when the
+  client must branch on the specific cause; `detail` is a human-readable fallback.
+  Pydantic validation errors put the raw `exc.errors()` list in `detail`, so `detail` is
+  `str | list`, and clients must handle both.
+- `code` is the contract, `detail` is not: the client maps `code` to its own localised
+  message and only falls back to `detail` when the code is unknown to it.
+  Every error a user can act on gets a `code`; purely technical errors need none.
+- Register: `app.add_exception_handler(APIError, api_exception_handler)`.

 ## API Error Response Contract

-{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }
+{ "detail": "Device is already assigned", "code": "DEVICE_ALREADY_ASSIGNED" }
```

### K-07 — `docs/technical/backend/03_security_module.md`: nieudokumentowane zabezpieczenia

Pięć obron wymienionych na końcu [sekcji 4.3](#43-security-checklistmd) nie jest nigdzie opisanych. `CLAUDE.md` („Module & Key-Change Documentation") wymaga dokumentowania nieoczywistych zabezpieczeń. Rekomendacja: dopisać do `03_security_module.md` sekcję „Zabezpieczenia niewidoczne w kontrakcie API" z tymi pięcioma pozycjami i uzasadnieniem każdej — **bez** tworzenia nowego pliku, bo moduł ma już swój dokument.

---

## 6. Lista długu technicznego

Gotowa do przepisania na osobne zlecenia. Kolejność = priorytet.

| # | Dług | Dowód | Skutek | Szac. |
|---|---|---|---|---|
| **D-01** | 🛑 Trzy pliki z `except A, B:` — składnia Pythona 2 | [sekcja 1](#1--blokujące-ustalenie-backend-w-tej-chwili-się-nie-importuje) | Backend się nie importuje; testy się nie zbierają | 15 min |
| **D-02** | 🛑 Brak CI; pre-commit nigdy nie przejechał po istniejącym kodzie | brak `.github/`; `.pre-commit-config.yaml` dodany tym samym commitem co D-01 | Nic nie broni gałęzi `main` przed kodem, który się nie parsuje | 2–4 h |
| **D-03** | 🔴 `last_seen_at` nigdy nie zapisywane, a frontend na nim liczy „świeżość" urządzenia | pole w [`device.py:43`](../../../backend/app/modules/core_data/models/device.py#L43) i w `DeviceResponse`; zapis tylko w `scripts/seed_database.py:490`; `ingest.py:154` zapisuje `last_diagnostics_at`; [`frontend/src/lib/deviceFreshness.ts:3`](../../../frontend/src/lib/deviceFreshness.ts#L3) i `PlatformDevicesPage.tsx:82-101` czytają `last_seen_at` | Wskaźnik świeżości w UI jest **zawsze** `unknown` na produkcji | 1–2 h + migracja |
| **D-04** | 🔴 `context_type="organization"` zamiast `"core_data_organization"` w jednym miejscu | [`devices.py:222`](../../../backend/app/modules/core_data/services/devices.py#L222) vs 5× `"core_data_organization"` w `members.py`/`groups.py`; zapytanie `get_by_context` filtruje po dokładnej wartości | Zdarzenia przypisania urządzenia do gminy **nie pokazują się** w historii audytu tej gminy | 30 min + backfill |
| **D-05** | 🔴 `get_or_create_internal` robi `session.rollback()` w środku cudzej transakcji | [`measurement_points.py:180-187`](../../../backend/app/modules/core_data/services/measurement_points.py#L180-L187), wołane z [`ingest.py:190`](../../../backend/app/modules/telemetry/services/ingest.py#L190) wewnątrz `transaction(skip_audit=True)` | Przy wyścigu na `IntegrityError` rollback kasuje zapisany już `TelemetryPacket`, a kod leci dalej i dopina `TelemetryError` z `packet_id` do nieistniejącego pakietu (FK `ondelete=CASCADE`) | 2–3 h |
| **D-06** | 🔴 `transaction()` nie jest re-entrantne; zagnieżdżenie commituje zewnętrzną jednostkę pracy | [`device_auth.py:127-129`](../../../backend/app/modules/device_identity/services/device_auth.py#L127-L129) → `create_claimed` → `devices.py:124` | „Atomowa" weryfikacja urządzenia to w rzeczywistości dwa commity; obejście przez `tx.skip_audit()` z komentarzem | 3–5 h |
| **D-07** | 🟠 `extra="forbid"` tylko na najwyższym modelu pakietu; modele zagnieżdżone przyjmują nieznane pola po cichu | [`measurement_packet.py:63`](../../../backend/app/modules/telemetry/schemas/measurement_packet.py#L63); `MeasurementWindow`, `MeasurementPoint`, `ErrorEntry` bez `extra` | Literówka w kluczu wewnątrz `points[]` przechodzi bez błędu i ginie | 30 min |
| **D-08** | 🟠 `prebuild.py::validate()` używa ścieżek względnych względem katalogu roboczego | [`prebuild.py`](../../../firmware/scripts/prebuild.py) — `Path("firmware/include/SensorRegistry.h")`, `Path("sensor_registry.yaml")`; PlatformIO uruchamia hook z `cwd = firmware/` | Krok 1 (generacja, `subprocess` z poprawnym `cwd`) działa; krok 2 (walidacja) nie znajduje plików i **wywala build** — albo hook nigdy nie był używany. Do potwierdzenia jednym `pio run` | 30 min |
| **D-09** | 🟠 `SensorRegistry.h` nie jest generowany dla środowiska `[env:native]` | hook podpięty pod `$BUILD_DIR/firmware.elf`; `firmware/test/test_isensor_pt100.cpp:3` robi `#include <SensorRegistry.h>`; plik jest w `.gitignore` | Testy natywne na czystym klonie nie kompilują się, dopóki ktoś ręcznie nie odpali generatora | 1 h |
| **D-10** | 🟠 Brakujące adnotacje typów w serwisach `core_data` | `_state(self, device)`, `_record_audit(..., device, ...)`, `list_all(self, query, ...)` ×4, `create`/`update`/`get_by_id` bez typu zwrotu — łącznie 13 funkcji z nieotypowanym argumentem | Blokuje włączenie `mypy --strict`; `-> dict` bez parametryzacji nie mówi nic | 2–3 h |
| **D-11** | 🟡 `seed.py` commituje z pominięciem `transaction()` | [`seed.py:40`](../../../backend/app/modules/security/services/seed.py#L40) | Jedyny commit produkcyjny poza wspólnym mechanizmem; przy błędzie w połowie seeda brak rollbacku | 30 min |
| **D-12** | 🟡 Dwa style deklarowania zależności autoryzacyjnej | `dependencies=[Depends(require_org_access(...))]` w `telemetry/api/query.py` vs `_org_access: ... = Depends(...)` w `core_data/api/*`; w endpointach platformowych nieużywany parametr `context` **bez** podkreślenia ([`devices.py:90,108,124`](../../../backend/app/modules/core_data/api/devices.py#L90)) | Czytelnik nie wie, czy brak podkreślenia znaczy „używane" | 1 h |
| **D-13** | 🟡 Trzy formy bezstanowego helpera obok siebie | funkcja modułowa (`ingest.py`), metoda bez `self` (`_state` ×5), `@staticmethod` (`groups.py`) | Brak kryterium; przy dopisywaniu helpera trzeba zgadywać | 1 h |
| **D-14** | 🟡 `dependencies.py` rzuca `HTTPException` zamiast wyjątków domenowych | 9 miejsc w `security/dependencies.py` i `device_identity/dependencies.py` | Dwie drogi do odpowiedzi błędu; `HTTPException` omija `_error_response`, więc **nigdy nie niesie pola `code`** | 2 h |
| **D-15** | 🔴 `python-jose` — biblioteka nieutrzymywana, jawnie zakazana przez `security-checklist` | `pyproject.toml`, [`token.py:3`](../../../backend/app/modules/security/services/token.py#L3) | Zależność bez łatek bezpieczeństwa w ścieżce uwierzytelniania. Migracja na `PyJWT` to ~30 linii | 2–3 h |
| **D-16** | 🟠 JWT bez `aud`/`iss`, algorytm `HS256` | [`token.py`](../../../backend/app/modules/security/services/token.py), `config.py:29` | Token użytkownika i token urządzenia są podpisane **tym samym** sekretem i różnią się tylko polem `type` — jedyną barierą jest sprawdzenie `payload.get("type")` | 3–4 h |
| **D-17** | 🟠 Refresh token w ciele odpowiedzi, bez rotacji i bez unieważniania | `TokenResponse`, `AuthService.refresh` | Wykradziony refresh działa do `exp` (24 h) i nie da się go odwołać | 4–6 h |
| **D-18** | 🟡 `/auth/token/refresh` bez rate-limitu | [`auth.py:33-38`](../../../backend/app/modules/security/api/auth.py#L33-L38) — brak `@limiter.limit` | Endpoint przyjmujący token bez limitu prób | 15 min |
| **D-19** | 🟠 `BaseSchema.serialize_floats` zaokrągla **wszystkie** floaty do 2 miejsc, także współrzędne geograficzne | [`core/schemas.py:15-20`](../../../backend/app/core/schemas.py#L15-L20) + `WaterObjectResponse.latitude/longitude` ([`water_objects.py:39-40`](../../../backend/app/modules/core_data/schemas/water_objects.py#L39-L40)) | Zaokrąglenie szerokości geogr. do 2 miejsc to błąd rzędu **~1,1 km**; obiekt na mapie ląduje w innej wsi. Intencją commita `55380ee` było formatowanie pomiarów, nie geometrii | 1 h |
| **D-20** | 🟡 Dwa kształty pola `changes` w tym samym logu audytu | `{"status": (old, "cancelled")}` w [`activation_codes.py:189,297`](../../../backend/app/modules/device_identity/services/activation_codes.py#L189) vs `{"k": {"old":…, "new":…}}` w pozostałych 17 miejscach | Krotka serializuje się do tablicy JSON; konsument historii musi obsłużyć dwa formaty | 30 min + backfill |
| **D-21** | 🟡 `PaginatedResponse[T]` zdefiniowany dwukrotnie, `T` w `core/schemas.py` nieużywany | `core_data/schemas/users.py:11` i `telemetry/schemas/query.py:109`; `core/schemas.py:7` | Dwa niezależne modele o tej samej nazwie w OpenAPI | 30 min |
| **D-22** | 🟡 Komunikaty błędów API mieszają polski i angielski | **19** polskich komunikatów, wszystkie w module `security` (`services/groups.py` 13, `services/auth.py` 2, `services/permissions.py` 2, `schemas/groups.py` 2); wszystkie pozostałe moduły — angielskie | Bez `code` frontend pokazuje surowy `detail` — użytkownik widzi raz polski, raz angielski | 2 h, **wymaga decyzji** → [P-1](#7-pytania-do-rozstrzygnięcia) |
| **D-23** | 🟢 `DeviceLifecycleService` importuje **repozytorium** cudzego modułu | [`device_lifecycle.py:7-9`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L7-L9) — `DeviceCredentialRepository`; `01_backend-architecture.md §2.3` zabrania wprost | Przeskok warstwy; jedyne takie miejsce w kodzie | 1–2 h |
| **D-24** | 🟢 `SensorRegistry` to globalny, mutowalny stan klasy w module domenowym | `core_data/registry.py`; importowany bezpośrednio przez `telemetry/schemas` i `telemetry/services` z pominięciem warstwy serwisów | Łamie `§2.3` (cross-module tylko przez serwisy) i „DI zamiast globalnego stanu". Naturalne miejsce to `core/` | 2 h |
| **D-25** | 🟢 Niespójna inicjalizacja repozytoriów | `super().__init__(session)` w `packets.py`, `audit.py`; `self.session = session` w `groups.py`, `permissions.py`, `devices.py`, `measurement_points.py`, `organizations.py`, `users.py`, `water_objects.py`, `users_organizations.py` | Powielony konstruktor bazowy; przy dodaniu pola do `SQLRepository` część repozytoriów go nie dostanie | 30 min |
| **D-26** | 🟢 `DEVICE_ALREADY_ASSIGNED` nieznany frontendowi | backend: `devices.py:205`; `domainErrorMessages` w `frontend/src/lib/errors.ts:34-41` zna 6 kodów, tego nie | Użytkownik dostaje angielskie „Device is already assigned" | 15 min |
| **D-27** | 🟢 `modules/device_identity/` bez `__init__.py`; brak `exceptions.py` w 3 z 5 modułów | struktura katalogów vs template z `01_backend-architecture.md §5.1` | Niespójność z własnym szablonem. **Uwaga:** brak `exceptions.py` jest uzasadniony (patrz niżej), brak `__init__.py` nie | 15 min |
| **D-28** | 🟢 `Mapped[UUID]` wskazuje na `sqlalchemy.UUID`, nie `uuid.UUID` | [`measurement_packet.py:9,26`](../../../backend/app/modules/telemetry/models/measurement_packet.py#L26) — import `from sqlalchemy import UUID` | Adnotacja semantycznie błędna; działa tylko dlatego, że typ kolumny podano jawnie | 15 min |

### Jak zweryfikować pozycje, których nie dało się sprawdzić uruchomieniem

Wszystko poniżej do odpalenia w `.venv` (analiza była statyczna — patrz [sekcja 0](#0-jak-to-było-robione)).

**D-01 — składnia (bez zależności, 2 s):**
```bash
cd backend && python -m compileall -q app/
```

**D-19 — zaokrąglanie współrzędnych:**
```bash
cd backend && python -c "
from app.modules.core_data.schemas.water_objects import WaterObjectResponse
from uuid import uuid4
o = WaterObjectResponse(id=uuid4(), organization_id=uuid4(), name='x', object_type='intake',
                        location_description=None, latitude=50.061947, longitude=19.936856, is_active=True)
print(o.model_dump_json())"
# oczekiwane, jeśli dług istnieje: latitude 50.06, longitude 19.94  (~1 km błędu)
```

**D-05 — rollback w środku transakcji ingestu:** test regresyjny, nie jednolinijkowiec. Scenariusz: dwa równoległe pakiety od tego samego urządzenia z **nowym** `point_id`, tak żeby `get_or_create_internal` trafił na `IntegrityError` na `uq_measurement_points_device_external_id`. Oczekiwane po naprawie: pakiet zapisany, `TelemetryError` spójny; przed naprawą: rollback usuwa pakiet, a kod leci dalej.

**D-08 — ścieżki w hooku pre-build:**
```bash
cd firmware && pio run -e esp32-s3 2>&1 | head -30
# oczekiwane, jeśli dług istnieje: "❌ Firmware header not found: firmware/include/SensorRegistry.h"
```

**Uwaga do D-27:** brak `exceptions.py` w `core_data`, `security` i `device_identity` **nie jest** długiem. Faktyczna reguła, wyczytana z kodu, brzmi: własna klasa wyjątku powstaje tylko wtedy, gdy wołający musi ją rozróżnić programowo — `TelemetryPacketAlreadyExistsError` jest łapany po typie w `ingest.py:157`, `MissingAuditRecordError` w testach sesji. W pozostałych przypadkach wystarczy `core.errors.*` z komunikatem i opcjonalnym `code`. To warto dopisać do `01_backend-architecture.md §5.2`.

---

## 7. Pytania do rozstrzygnięcia

Tylko rzeczy, których **nie da się** rozstrzygnąć przewagą dowodów z kodu — reszta została zaklasyfikowana wyżej.

**P-1. W jakim języku mają być komunikaty błędów API?**
Kod jest podzielony i to podzielony czysto: 19 polskich komunikatów siedzi **wyłącznie** w module `security`, wszystkie pozostałe moduły mówią po angielsku. Frontend ma własną mapę polskich komunikatów po `code`, ale zna tylko 6 kodów. Trzy spójne warianty, każdy do wyboru, żaden nie wynika z kodu:
(a) backend zawsze po angielsku + `code` przy każdym błędzie, tłumaczenie wyłącznie we frontendzie — najczystsze, ale wymaga nadania `code` w ~80 miejscach;
(b) backend zawsze po polsku, `code` tylko tam, gdzie klient musi się rozgałęzić — najtańsze, ale wiąże API z jednym rynkiem;
(c) status quo, uporządkowane per moduł — najgorsze, ale najtańsze.
Bez tej decyzji [D-22](#6-lista-długu-technicznego) i [D-26](#6-lista-długu-technicznego) nie da się domknąć.

**P-2. Czy `last_seen_at` ma zostać, czy `last_diagnostics_at` ma być przemianowane?**
Dowody mówią jednoznacznie, że stan jest zły, ale nie mówią, która nazwa jest zamierzona. Dwa warianty: (a) `ingest` zapisuje `last_seen_at`, a `last_diagnostics_at` zostaje pusty do czasu, aż pojawi się osobny pakiet diagnostyczny; (b) `last_diagnostics_at` znika, zostaje samo `last_seen_at`. Wariant (a) ma sens tylko wtedy, gdy w planach jest osobny strumień diagnostyki — a tego z kodu nie widać.

**P-3. Czy `POINT_TYPE_MISMATCH` ma odrzucać punkt, czy tylko go logować?**
Opis w [`sensor_registry.yaml`](../../../sensor_registry.yaml) mówi „rejected this point", ale kod ([`ingest.py:195-207`](../../../backend/app/modules/telemetry/services/ingest.py#L195-L207)) dopisuje `TelemetryError` i **przyjmuje pakiet w całości** — cały payload trafia do `telemetry_packets.payload`, łącznie z niezgodnym punktem. Zapis w registry i zachowanie kodu są sprzeczne; nie da się z samego kodu wywnioskować, która strona jest zamierzona.

**P-4. Czy `audit_events` ma być faktycznie partycjonowane?**
Klucz główny jest złożony `(id, created_at)` ([`models/audit.py`](../../../backend/app/modules/audit/models/audit.py)), a `05_audit_module.md` mówi, że „wspiera partycjonowanie po czasie". Żadnej partycji nie ma. Koszt tego kompromisu (`created_at` w PK, listener obchodzący ograniczenie SQLite w testach) jest płacony już teraz. Pytanie, czy partycjonowanie jest w planach — jeśli nie, klucz można uprościć.

---

## 8. Indeks powstałych ADR-ów

Wszystkie w statusie **`Proposed`** — nie przełączam ich sam na `Accepted`.

| ADR | Tytuł | Klasa | Sekcja raportu |
|---|---|---|---|
| [0001](../adr/0001-jedna-sesja-na-request.md) | Jedna sesja SQLAlchemy na żądanie; `transaction()` obejmuje całą jednostkę pracy | reguła | [2.1](#21-jedna-sesja-na-request-transaction-z-dowolnego-repozytorium-obejmuje-całą-jednostkę-pracy--reguła--adr-0001) |
| [0002](../adr/0002-niezmiennik-audytu-przy-commicie.md) | Commit bez wpisu audytowego jest blokowany na poziomie sesji | reguła + wyjątek | [2.2](#22-commit-bez-wpisu-audytowego-jest-niemożliwy-wyjątki-mają-jedno-kryterium--reguła--wyjątek--adr-0002) |
| [0003](../adr/0003-aktor-audytu-jako-napis.md) | Aktor audytu to napis bez klucza obcego — urządzenie też jest aktorem | reguła | [2.3](#23-aktorem-audytu-bywa-urządzenie--reguła--adr-0003) |
| [0004](../adr/0004-autoryzacja-na-granicy-api.md) | Autoryzacja wyłącznie na granicy API; serwis dostaje udowodniony kontekst | reguła | [2.4](#24-autoryzacja-żyje-wyłącznie-na-granicy-api--reguła--adr-0004) |
| [0005](../adr/0005-dwie-plaszczyzny-dostepu.md) | Dwie płaszczyzny dostępu = dwa routery na zasób | reguła | [2.5](#25-dwie-płaszczyzny-dostępu--dwa-routery-na-zasób--reguła--adr-0005) |
| [0006](../adr/0006-endpointy-urzadzeniowe-poza-api-v1.md) | Endpointy urządzeniowe poza `/api/v1` i bez wersjonowania | reguła | [2.6](#26-endpointy-urządzeniowe-stoją-poza-apiv1--reguła--adr-0006) |
| [0007](../adr/0007-telemetria-bez-fk-do-rejestru.md) | Telemetria wiąże się z rejestrem przez `external_id`, bez klucza obcego | reguła | [2.7](#27-telemetria-jest-luźno-związana-z-rejestrem-urządzeń--reguła--adr-0007) |
| [0008](../adr/0008-rdzenie-bez-commitu-w-operacjach-wielomodulowych.md) | Operacje wielomodułowe: rdzenie bez commitu, transakcja u orkiestratora | reguła | [2.8](#28-operacja-wielomodułowa-rdzeń-bez-commitu-transakcja-u-orkiestratora--reguła--adr-0008) |
| [0009](../adr/0009-sensor-registry-jedno-zrodlo-prawdy.md) | `sensor_registry.yaml` jako jedno źródło prawdy — i gdzie się kończy | reguła + granica | [2.9](#29-sensor_registryyaml-jako-jedno-źródło-prawdy--reguła-z-wyraźną-granicą--adr-0009) |
| [0010](../adr/0010-modul-bezportowy-audit.md) | Moduł bezportowy: `audit` wystawia się przez port w `core/` | reguła | [2.10](#210-moduł-bez-api-audit-wystawia-się-przez-port--reguła--adr-0010) |
| [0011](../adr/0011-serwisy-zwracaja-encje-orm.md) | Serwisy CRUD zwracają encje ORM; DTO buduje FastAPI | reguła | [2.11](#211-serwisy-crud-zwracają-encje-orm-dto-robi-fastapi--reguła-sprzeczna-z-dokumentacją--adr-0011) |

**Świadomie nie powstały ADR-y dla:**

- *niezmiennej `frozen dataclass` jako kontekstu* — wzorzec potwierdzony (5 wystąpień), ale nie przechodzi progu z `ADR-FORMAT.md`: łatwo odwracalny, nie zaskakuje, nie jest wynikiem realnego kompromisu. Miejsce: konwencja w architekturze ([K-05](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji));
- *konwencji `get_`/`find_`* — jest już opisana w `01_backend-architecture.md §5.2`; ADR by ją zdublował. Potrzebne jest doprecyzowanie zasięgu ([K-03](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji));
- *`extra="forbid"` na granicy* — 1 wystąpienie, poniżej progu 2–3 zgodnych. Trafia do długu ([D-07](#6-lista-długu-technicznego));
- *twardnienia konfiguracji produkcyjnej* — jedno miejsce, brak pokrycia w dokumentacji architektury; wartościowe, ale jako dokumentacja modułu, nie ADR ([K-07](#5-proponowane-korekty-istniejących-reguł-i-dokumentacji));
- *funkcji modułowych w serwisach* — hipoteza obalona, nie ma czego zapisywać ([2.13](#213-funkcje-modułowe-zamiast-metod-serwisu--brak-reguły)).
