# Analiza niezapisanych paradygmatów backendu

> Wynik autonomicznego przeglądu kodu backendu i warstwy styku (B-04). Potwierdzone wzorce zostały zapisane jako szkice ADR w [`docs/technical/adr/`](../adr/) ze statusem `Proposed`. Firmware (poza kontraktem `sensor_registry.yaml`) i frontend (poza kontraktem API) są poza zakresem.
>
> Stan kodu w chwili analizy: gałąź `claude/backend-paradigms-analysis-6x5o78`, backend `app/` = 15 715 linii w 202 plikach.

---

## 0. Zacznij tutaj — dwa ustalenia, które wyprzedzają całą resztę

**Backend w obecnym stanie nie startuje.** Trzy pliki zawierają błąd składni Pythona (`except ValueError, TypeError:` — składnia Pythona 2, niedozwolona w 3.x). Jednym z nich jest [`security/dependencies.py`](../../../backend/app/modules/security/dependencies.py#L118), importowany praktycznie przez każdy router — import aplikacji kończy się `SyntaxError`. Ten sam stan jest na `main`. Szczegóły i poprawka: **[D-01](#d-01)**.

**Brama jakości tego nie wykrywa i nie wykryje.** `ruff check` oraz `ruff format` (0.15.8, konfiguracja z `pyproject.toml`) przechodzą na tych plikach bez jednego ostrzeżenia — zweryfikowane na minimalnym przykładzie odtwarzającym konstrukcję. W `.pre-commit-config.yaml` nie ma ani `mypy`, ani `pytest`, ani żadnego kroku parsującego kod; w repozytorium nie ma też konfiguracji CI. Nic w projekcie nie sprawdza dziś, czy backend w ogóle da się zaimportować. Szczegóły: **[D-02](#d-02)**.

Reszta dokumentu opisuje wzorce w kodzie tak, jak są napisane — obie powyższe usterki są mechaniczne i nie zmieniają wniosków o architekturze.

---

## 1. Metoda

Dla każdego wzorca: zebranie **wszystkich** wystąpień (nie jednego), policzenie przypadków zgodnych i niezgodnych, dopiero potem klasyfikacja.

| Klasa | Kryterium | Skutek |
|---|---|---|
| **reguła** | wzorzec konsekwentny w wielu modułach, bez kontrprzykładów, albo już opisany w dokumentacji architektury | kandydat na ADR |
| **wyjątek** | reguła łamana w policzalnych miejscach, ale z dostrzegalnym uzasadnieniem | ADR opisujący regułę *i* jej granicę |
| **dług** | sprzeczność z deklarowaną dokumentacją bez uzasadnienia albo nazwa myląca wobec zachowania | lista długu (§5), nigdy ADR |

ADR nie powstaje z jednej obserwacji ani dla oczywistego wyboru bez realnej alternatywy — kryteria z `ai-tools/.claude/skills/domain-modeling/ADR-FORMAT.md`.

**Ograniczenia weryfikacji.** W środowisku analizy nie były zainstalowane zależności backendu, więc **nie uruchomiono testów ani `mypy`** (`mypy` dodatkowo przerywa pracę na składni generyków PEP 695 przy interpreterze starszym niż wymagany przez projekt 3.14). Wszystkie liczby poniżej pochodzą z analizy statycznej: parsowania AST, przeszukiwania kodu i lektury. Uruchomiono natomiast `ruff check` (przechodzi) oraz parser Pythona 3.13 na całym `app/` (3 błędy składni).

---

## 2. Wzorce potwierdzone jako reguły i wyjątki

| # | Wzorzec | Dowód | Klasa | ADR |
|---|---|---|---|---|
| W-01 | Backend w całości synchroniczny (`def`, `Session`) | 56 endpointów `def`, 0 wystąpień `AsyncSession`; 10 endpointów `async def` w jednym module jako odstępstwo | reguła + dług | [0001](../adr/0001-backend-synchroniczny.md) |
| W-02 | Commit bez wpisu audytowego jest błędem sesji | `AuditAwareSession`; 17 jawnych `skip_audit` w 3 rozłącznych kategoriach | reguła + wyjątek | [0002](../adr/0002-commit-bez-audytu-jest-bledem.md) |
| W-03 | Audyt jako delta z migawki `_state()` | 6 serwisów, identyczny kształt, bez kontrprzykładu | reguła | [0003](../adr/0003-audyt-jako-delta-ze-snapshotu.md) |
| W-04 | `transaction()` jedyną granicą transakcji; repozytoria nie commitują | 36 wystąpień; 1 świadomy wyjątek (seed), 4 miejsca łamiące (dług) | reguła + wyjątek | [0004](../adr/0004-transaction-jedyna-granica-transakcji.md) |
| W-05 | `get_` zwraca `None`, `find_` rzuca | 43/43 metody repozytoriów zgodne, 0 kontrprzykładów | reguła | [0005](../adr/0005-get-zwraca-none-find-rzuca.md) |
| W-06 | Kontrakt błędu `detail` + opcjonalny `code`; `HTTPException` tylko w `dependencies.py` | 0 `raise HTTPException` w `api/` i `services/`, 12 w 2 plikach zależności; frontend mapuje `code` | reguła | [0006](../adr/0006-kontrakt-bledu-detail-plus-code.md) |
| W-07 | Autoryzacja w zależnościach, kontekst dostępu do serwisu; 404 na członkostwo, 403 na uprawnienie | 3 fabryki zależności, wszystkie endpointy org/platform | reguła | [0007](../adr/0007-autoryzacja-w-zaleznosciach.md) |
| W-08 | Dwa podmioty (user/device) na jednym bearer, claim `type` | 3 typy tokenów, 3 miejsca weryfikacji typu | reguła | [0008](../adr/0008-dwa-podmioty-jeden-bearer.md) |
| W-09 | Telemetria jako surowy pakiet JSONB, bez tabeli pomiarów | brak modelu wartości; cały odczyt rozpakowuje `payload` | reguła | [0009](../adr/0009-telemetria-jako-surowy-pakiet-jsonb.md) |
| W-10 | Telemetria wiązana przez `external_id`, bez FK | 2 modele bez `ForeignKey`, operacje po numerze seryjnym | reguła | [0010](../adr/0010-telemetria-wiazana-przez-external-id.md) |
| W-11 | `sensor_registry.yaml` = SSoT dla typów punktów i kodów błędów, i tylko dla nich | walidacja ingestu + hook pre-build; 4 elementy kontraktu poza rejestrem | reguła + granica | [0011](../adr/0011-zakres-sensor-registry.md) |
| W-12 | Autoprovisioning punktów pomiarowych z pakietu | `get_or_create_internal` + `POINT_TYPE_MISMATCH` | reguła | [0012](../adr/0012-autoprovisioning-punktow-pomiarowych.md) |
| W-13 | Moduł wspierający bez `api/`, udostępniany portem z `core/` | `audit` — jedyny taki moduł; 2 konsumentów portu | reguła | [0013](../adr/0013-modul-bez-warstwy-api.md) |
| W-14 | Bezstanowa logika jako funkcje modułowe; kontekst jako frozen dataclass | 2 moduły bezklasowe + 15 funkcji modułowych w `services/`; 6 zamrożonych dataclass | reguła | [0014](../adr/0014-bezstanowa-logika-poza-klasami.md) |
| W-15 | Modele `core_data` jako wspólny słownik domenowy | 15 cross-modułowych importów modeli; 1 wyjątek zapisowy | wyjątek (granica reguły §2.3) | [0015](../adr/0015-modele-core-data-jako-wspolny-slownik.md) |

### W-01 — Backend synchroniczny

**Wystąpienia.** Wszystkie endpointy w `core_data/api/`, `security/api/`, `telemetry/api/` są zadeklarowane jako `def`. Endpointów synchronicznych jest 56. `async def` w kodzie produkcyjnym pojawia się 14 razy: 4 razy tam, gdzie wymaga tego framework (`lifespan` w [`main.py:55`](../../../backend/app/main.py#L55) i 3 handlery w [`core/errors.py`](../../../backend/app/core/errors.py#L86)), i **10 razy we wszystkich endpointach `device_identity/api/`**. `AsyncSession` nie występuje w repozytorium ani razu; wszystkie repozytoria przyjmują `sqlalchemy.orm.Session`.

**Klasyfikacja.** Reguła (synchroniczność) plus dług ([D-05](#d-05)) — `async def` wołające synchroniczną sesję blokuje pętlę zdarzeń, czyli daje efekt odwrotny do zamierzonego. Nie ma śladu uzasadnienia: te same operacje w innych modułach są synchroniczne.

### W-02 — Niezmiennik audytu i trzy kategorie `skip_audit`

**Wystąpienia.** 17 jawnych pominięć audytu. Po pogrupowaniu okazuje się, że nie tworzą listy wyjątków ad hoc, tylko trzy rozłączne klasy:

| Kategoria | Miejsca | Uzasadnienie widoczne w kodzie |
|---|---|---|
| pusta delta stanu | 12 (`users`, `water_objects`, `organizations`, `devices`, `measurement_points`, `auth`, `groups` ×5, `activation_codes:244`) | `if not calculate_delta(...): tx.skip_audit()` |
| zapis niebędący zmianą biznesową | 4 (ingest telemetrii, challenge urządzenia, 2× ścieżki `verify`) | strumień pomiarowy i przejściowy nonce |
| bootstrap bez aktora | 1 ([`seed.py:40`](../../../backend/app/modules/security/services/seed.py#L40)) | seed uprawnień przy starcie, brak użytkownika |

**Rozstrzygnięcie hipotezy z briefu.** Teza „zapis inicjowany przez urządzenie nie jest audytowany" jest **obalona**: redeem kodu aktywacyjnego i pierwszy claim urządzenia **są** audytowane, z urządzeniem w roli aktora (`actor_display_name = "device:<serial>"`). Właściwym kryterium jest „czy zaszła zmiana stanu biznesowego", a nie „kto ją zainicjował".

### W-05 — `get_` / `find_`

Analiza AST wszystkich 13 repozytoriów: **43 metody odczytu, zgodność 100 %**. Każde `get_*` ma w sygnaturze `| None` albo typ kolekcji i nie zawiera `raise`; każde `find_*` zwraca typ nieopcjonalny i rzuca `NotFoundError`. Zero kontrprzykładów w pięciu modułach.

**Rozstrzygnięcie hipotezy z briefu (`get_or_create_internal`).** To **nie jest** złamanie konwencji: konwencja wiąże warstwę repozytoriów, a to jest metoda serwisu, której nazwa jawnie opisuje zachowanie („pobierz albo utwórz"). Na poziomie serwisów prefiks `get_` i tak nie niesie tej semantyki — `DeviceService.get_by_id` rzuca, `DeviceService.get_by_external_id` zwraca `None`, i obie nazwy są poprawne. Ta metoda łamie natomiast inną regułę — sięga po `repo.session` — patrz [D-04](#d-04) i [D-06](#d-06).

### W-11 — Granica „jednego źródła prawdy"

**Korekta założenia z briefu.** Brief zakłada, że hook pre-build jest wyłączony. W [`firmware/platformio.ini`](../../../firmware/platformio.ini#L7) linia `extra_scripts = scripts/prebuild.py` jest **aktywna**, a [`prebuild.py`](../../../firmware/scripts/prebuild.py) generuje `SensorRegistry.h` z YAML-a i przerywa build przy rozjeździe wersji schematu, typów punktów lub kodów błędów. Wygenerowany nagłówek jest celowo w `.gitignore`, dlatego nie ma go w repozytorium.

Reguła obejmuje trzy rzeczy: `schema_version`, `point_types[].id`, `error_codes[].code`. Poza nią zostają: `canonical_unit` (nigdzie nieegzekwowane — ingest przyjmuje dowolną jednostkę), `severity` przypisane w YAML konkretnemu kodowi (schemat sprawdza tylko przynależność do `{info, warning, critical}`), wartości `quality` (wolny string porównywany z literałem `"good"` w logice statusu) i koperta pakietu (`v`, `seq`, `windows`, `errors` — opisana wyłącznie w schemacie Pydantica).

---

## 3. Wzorce sprawdzone i **odrzucone** jako reguły

| Wzorzec | Ustalenie |
|---|---|
| `extra="forbid"` na schematach wejściowych | **Jedno wystąpienie w całym backendzie** ([`measurement_packet.py:63`](../../../backend/app/modules/telemetry/schemas/measurement_packet.py#L63)) i to tylko na najwyższym poziomie pakietu — zagnieżdżone `MeasurementWindow`, `MeasurementPoint`, `ErrorEntry` nadmiarowe pola przepuszczają. To nie jest reguła, tylko niedokończone utwardzenie granicy zaufania → [D-09](#d-09). |
| Brak logowania w serwisach | W 7 plikach w ogóle występuje `logger`, żaden z nich nie jest serwisem biznesowym; błędy loguje wyłącznie globalny handler, z rozróżnieniem poziomu 4xx/5xx. Wzorzec jest konsekwentny, ale nie da się odróżnić świadomej decyzji („loguj raz, centralnie") od braku implementacji — nie spełnia kryterium „wynik realnego kompromisu", więc **ADR nie powstaje**. Brak identyfikatora korelacji odnotowany jako [D-26](#d-26). |
| Hardening produkcyjny w `Settings` | Walidator odrzucający start z krótkim `secret_key` lub wildcardem CORS poza devem ([`config.py:77-90`](../../../backend/app/core/config.py#L77-L90)) to dobry wzorzec, ale jedno wystąpienie i brak realnej alternatywy — nie ADR. |
| Query params zawsze przez schemat `Depends()` | Zgodność 100 % (0 wystąpień gołego `Query(`), ale to wprost reguła z `python-coding-standards`, nie decyzja architektoniczna projektu — nie ADR. |

---

## 4. Odpowiedzi na hipotezy wejściowe z briefu

| # | Hipoteza | Ustalenie |
|---|---|---|
| 1 | `get_` vs `find_`, czy `get_or_create_internal` łamie konwencję | Konwencja trzymana w 43/43 metodach repozytoriów. `get_or_create_internal` **nie łamie** jej (jest metodą serwisu z nazwą opisującą zachowanie), łamie natomiast granicę transakcji → [ADR-0005](../adr/0005-get-zwraca-none-find-rzuca.md), [D-04](#d-04) |
| 2 | Moduł bez `api/` | `audit` jest jedynym takim modułem. Kryterium wydestylowane: brak własnego zasobu URL + kontrakt wyrażalny jako protokół w `core/` → [ADR-0013](../adr/0013-modul-bez-warstwy-api.md) |
| 3 | `AuditAwareSession` i wspólna cecha `skip_audit=True` | Wspólna cecha istnieje, ale **inna niż zakładał brief** — nie „zapis z urządzenia", tylko „brak zmiany stanu biznesowego" (3 rozłączne kategorie) → [ADR-0002](../adr/0002-commit-bez-audytu-jest-bledem.md) |
| 4 | Funkcje modułowe zamiast metod serwisu | Wzorzec powtarzalny z jasnym kryterium („nie potrzebuje `self` → nie jest metodą"); 2 moduły są bezklasowe w całości → [ADR-0014](../adr/0014-bezstanowa-logika-poza-klasami.md) |
| 5 | Frozen dataclass jako przewlekany kontekst | Potwierdzone poza `_IngestContext`: `AuditEntry`, `OrganizationAccess`, `PlatformContext`, `PermissionDef`, `StoredAttachment` → [ADR-0014](../adr/0014-bezstanowa-logika-poza-klasami.md) |
| 6 | `sensor_registry.yaml` jako jedyne źródło prawdy | Reguła potwierdzona, **założenie briefu o wyłączonym hooku nieaktualne** — hook jest aktywny. Granica reguły opisana w [ADR-0011](../adr/0011-zakres-sensor-registry.md) |
| 7 | Nazewnictwo niezgodne z zachowaniem | Potwierdzone i gorsze, niż zakładał brief: `last_seen_at` **istnieje w modelu, nie jest nigdy zapisywane, a frontend wyświetla właśnie je** → [D-03](#d-03). Pozostałe znalezione niezgodności nazwy wobec zachowania: [D-23](#d-23) (`quality` porównywane z literałem), [D-27](#d-27) (`DELETE /devices/{id}` nie usuwa, tylko odpina; `assign_water_object` używane do odpięcia) |
| 8 | `transaction()` w każdym serwisie | 36 wystąpień; ręczne sterowanie transakcją w 4 miejscach poza `cli.py` — 1 uzasadnione (seed), 3 to dług → [ADR-0004](../adr/0004-transaction-jedyna-granica-transakcji.md), [D-04](#d-04), [D-06](#d-06) |
| 9 | `extra="forbid"` w innych modułach | **Hipoteza obalona** — jedno wystąpienie w całym backendzie, i to niepełne → [D-09](#d-09) |

---

## 5. Dług techniczny

Pozycje gotowe do przepisania na osobne zadania. Kolejność według skutku, nie według trudności.

### Krytyczne — blokują uruchomienie

<a id="d-01"></a>
**D-01. Trzy pliki z błędem składni Pythona.** Konstrukcja `except ValueError, TypeError:` (składnia Py2) w:
- [`security/dependencies.py:118`](../../../backend/app/modules/security/dependencies.py#L118)
- [`device_identity/dependencies.py:133`](../../../backend/app/modules/device_identity/dependencies.py#L133)
- [`device_identity/services/signature.py:32`](../../../backend/app/modules/device_identity/services/signature.py#L32)

Poprawka to nawiasy w każdym z trzech miejsc: `except (ValueError, TypeError):`. Stan występuje również na `main`. Weryfikacja po poprawce: `python -m compileall -q backend/app`.

<a id="d-02"></a>
**D-02. Brama jakości nie wykrywa niedziałającego kodu.** `ruff check` i `ruff format --check` przechodzą na plikach z D-01 (zweryfikowane na izolowanym przykładzie: `ruff --isolated` zwraca „All checks passed", `python3.13 -c ast.parse` zwraca `SyntaxError`). W `.pre-commit-config.yaml` są tylko `ruff-check`, `ruff-format`, `eslint`, `tsc`, `clang-format` — nic nie parsuje ani nie uruchamia Pythona; w repozytorium nie ma konfiguracji CI. Minimalna naprawa: dodać hook `check-ast` z `pre-commit-hooks` oraz krok uruchamiający `pytest` na backendzie.

### Wysokie — widoczne dla użytkownika albo grożące utratą danych

<a id="d-03"></a>
**D-03. `last_seen_at` nigdy nie jest zapisywane, a interfejs pokazuje właśnie je.** Ingest ustawia [`device.last_diagnostics_at`](../../../backend/app/modules/telemetry/services/ingest.py#L154), czyli pole o nazwie „ostatnia diagnostyka" pełni rolę „ostatnio widziane". Kolumna `last_seen_at` w modelu istnieje, ale w całym backendzie nie ma ani jednego przypisania do niej poza skryptem seedującym — podczas gdy frontend renderuje ją jako czas ostatniego kontaktu ([`PlatformDevicesPage.tsx:82-101`](../../../frontend/src/pages/PlatformDevicesPage.tsx#L82-L101), [`DeviceDetailDrawer.tsx:56`](../../../frontend/src/components/devices/DeviceDetailDrawer.tsx#L56)), łącznie z oceną świeżości danych. Efekt: dla realnych urządzeń kolumna jest pusta, a wskaźnik świeżości bezużyteczny. Naprawa wymaga decyzji, które z dwóch pól jest kanoniczne (patrz [P-01](#p-01)).

<a id="d-04"></a>
**D-04. `session.rollback()` wewnątrz cudzej transakcji.** [`measurement_points.py:182-187`](../../../backend/app/modules/core_data/services/measurement_points.py#L182-L187) obsługuje `IntegrityError` przez `self.repo.session.rollback()`. Metoda jest wołana z wnętrza transakcji ingestu, więc rollback cofa **całą** transakcję, w tym właśnie zapisany `TelemetryPacket`. Dalszy przebieg `ingest()` operuje wtedy na identyfikatorze pakietu, którego nie ma w bazie: wstawienie `TelemetryError` z `packet_id` naruszy klucz obcy, a `device.last_diagnostics_at` ustawiane jest na obiekcie po rollbacku. Scenariusz: dwa pakiety z tego samego urządzenia zgłaszające ten sam nowy `point_id` obsługiwane równolegle. Właściwe rozwiązanie to `SAVEPOINT` (`session.begin_nested()`) zamiast pełnego rollbacku.

### Średnie

<a id="d-05"></a>
**D-05. `device_identity/api/` asynchroniczne na synchronicznym stosie.** 10 endpointów `async def` wołających blokujące serwisy — każde żądanie blokuje pętlę zdarzeń na czas zapytania do bazy, zamiast trafić do puli wątków. Naprawa: zamiana na `def`, bez zmian w treści.

<a id="d-06"></a>
**D-06. Serwisy sięgają bezpośrednio po `session`.** Cztery miejsca łamią zasadę „serwis nie zna sesji": [`measurement_points.py:180`](../../../backend/app/modules/core_data/services/measurement_points.py#L180) i `:183`, [`ingest.py:151`](../../../backend/app/modules/telemetry/services/ingest.py#L151) i `:155`. Zapis błędów telemetrycznych i tworzenie punktu powinny być metodami repozytorium.

<a id="d-07"></a>
**D-07. Niespójny kształt `changes` w audycie.** W [`activation_codes.py:189`](../../../backend/app/modules/device_identity/services/activation_codes.py#L189) i [`:297`](../../../backend/app/modules/device_identity/services/activation_codes.py#L297) delta jest krotką `{"status": ("unused", "used")}`, podczas gdy cała reszta systemu zapisuje `{"pole": {"old": ..., "new": ...}}` (`calculate_delta`). Po serializacji do JSONB daje to tablicę zamiast obiektu — konsument audytu musi obsłużyć dwa kształty.

<a id="d-08"></a>
**D-08. Globalne zaokrąglanie wartości zmiennoprzecinkowych do 2 miejsc.** [`core/schemas.py:15-20`](../../../backend/app/core/schemas.py#L15-L20) zaokrągla przy serializacji do JSON **każde** pole `float` w każdym schemacie dziedziczącym po `BaseSchema` — w tym `value`, `avg`, `min`, `max` szeregów pomiarowych. Dla ciśnienia w barach to rozdzielczość 10 mbar narzucona na warstwie prezentacji danych, o której warstwa domenowa nic nie wie. Zaokrąglanie należy do formatowania w interfejsie, nie do kontraktu API.

<a id="d-09"></a>
**D-09. `extra="forbid"` tylko na najwyższym poziomie pakietu.** Nadmiarowe pole wewnątrz `windows[].points[]` jest po cichu ignorowane — literówka w firmware nie da żadnego sygnału. Utwardzenie granicy zaufania powinno objąć wszystkie schematy pakietu (najprościej: `extra="forbid"` w `BaseSchema` dla schematów wejściowych albo wspólna klasa bazowa dla payloadu urządzenia).

<a id="d-10"></a>
**D-10. Mieszany język komunikatów błędów.** `core_data` i `telemetry` rzucają komunikaty po angielsku („Device not found"), `security` po polsku („Grupa użytkowników nie istnieje", „Podaj obecne hasło, aby je zmienić."). Ponieważ frontend pokazuje `detail` wprost, gdy brakuje `code`, użytkownik widzi mieszankę dwóch języków.

<a id="d-11"></a>
**D-11. `code` tylko w 12 miejscach.** Bez `code` frontend nie ma czego przetłumaczyć i wyświetla surowy `detail` (patrz D-10). Każdy błąd, który interfejs ma jakoś zinterpretować, powinien nieść stabilny kod.

<a id="d-12"></a>
**D-12. `sync_org_membership_group` poza transakcją.** [`members.py:67-73`](../../../backend/app/modules/core_data/services/members.py#L67-L73) i trzy analogiczne miejsca wywołują synchronizację grup **po** zamknięciu transakcji dodania członka. Awaria między jednym a drugim zostawia użytkownika w organizacji bez przypisanej grupy, czyli bez uprawnień i bez widoczności w przełączniku środowisk.

<a id="d-13"></a>
**D-13. Rate limiting nie obejmuje wszystkich wrażliwych endpointów.** Limit 5/min mają `/auth/token` i redeem kodu aktywacyjnego. Nie mają go: `/auth/token/refresh` oraz ścieżki `device_auth` (challenge/verify) — te ostatnie generują nonce i wykonują kryptografię na każde żądanie.

<a id="d-14"></a>
**D-14. Odstępstwa od `security-checklist` w warstwie tokenów.** `python-jose` zamiast `PyJWT`, HS256 bez `audience`/`issuer`, token dostępu 120 minut, refresh 1 dzień bez rotacji, a po stronie frontendu refresh token trafia do `localStorage` (`zustand/persist` w [`authStore.ts`](../../../frontend/src/stores/authStore.ts)). Część z tego jest obroniona w kontekście monolitu (§6.3), część nie — rozdzielenie w tabeli poniżej.

### Niskie

<a id="d-15"></a>
**D-15. Dwie definicje `PaginatedResponse[T]`** — [`core_data/schemas/users.py:11`](../../../backend/app/modules/core_data/schemas/users.py#L11) i [`telemetry/schemas/query.py:109`](../../../backend/app/modules/telemetry/schemas/query.py#L109) — przy nieużywanym `T = TypeVar("T")` w [`core/schemas.py:7`](../../../backend/app/core/schemas.py#L7). Miejsce docelowe jest oczywiste i puste.

<a id="d-16"></a>
**D-16. Mieszanie API SQLAlchemy 1.x i 2.0.** `session.query(...)` w 11 plikach, `select(...) + session.execute(...)` w 7 — w tym w tych samych plikach (`users.py`, `groups.py`, `permissions.py`, `packets.py`). Bez rozpoznawalnego kryterium podziału.

<a id="d-17"></a>
**D-17. Niespójna inicjalizacja repozytoriów.** 9 z 13 repozytoriów robi `self.session = session`, 4 wołają `super().__init__(session)`. Efekt jest ten sam, ale pierwsza forma milcząco zakłada, że klasa bazowa nie zyska nigdy stanu.

<a id="d-18"></a>
**D-18. `MissingAuditRecordError` w module domenowym.** [`infrastructure/sql/factory.py:7`](../../../backend/app/infrastructure/sql/factory.py#L7) importuje wyjątek z `modules/audit/` — infrastruktura zależy od modułu, co jest odwróceniem dozwolonego kierunku zależności (§2.1 architektury). Wyjątek powinien mieszkać w `core/errors.py`.

<a id="d-19"></a>
**D-19. Brak `find_*` w `security/repositories/groups.py`.** Skutkiem są 4 powtórzenia `if not group: raise NotFoundError(...)` w `GroupService` — dokładnie ta duplikacja, którą konwencja z W-05 eliminuje w innych modułach.

<a id="d-20"></a>
**D-20. Rejestracja modeli dla Alembica działa przez efekt uboczny.** [`models_registry.py`](../../../backend/app/infrastructure/sql/models_registry.py) nie importuje `UsersOrganizations`; model rejestruje się tylko dlatego, że import `core_data.models.device` wykonuje `__init__.py` pakietu. Zadziała, dopóki nikt nie uprości `__init__.py`. Dokumentacja mówi „każdy nowy model musi być tu zarejestrowany" — warto, żeby tak faktycznie było.

<a id="d-21"></a>
**D-21. Niespójny układ testów.** `backend/tests/` (4 pliki) obok `app/modules/*/tests/`, gdzie podział `unit/`/`integration/` mają trzy moduły, a `device_identity` trzyma testy płasko obok katalogu `integration/`.

<a id="d-22"></a>
**D-22. `seed.py` wycisza wyjątki po dopasowaniu tekstu komunikatu.** [`seed.py:42-50`](../../../backend/app/modules/security/services/seed.py#L42-L50) przepuszcza błąd tylko wtedy, gdy komunikat *nie* zawiera „relation" i „does not exist" — dopasowanie do tekstu sterownika, wrażliwe na jego wersję i lokalizację. Właściwe jest sprawdzenie typu wyjątku (`ProgrammingError`/`UndefinedTable`).

<a id="d-23"></a>
**D-23. `quality` jako wolny string porównywany z literałem.** [`query.py:101`](../../../backend/app/modules/telemetry/services/query.py#L101) uznaje wszystko poza `"good"` za ostrzeżenie. Wartości nie ma w rejestrze ani w schemacie jako `Literal` — literówka w firmware daje obiekt trwale w stanie `warning`.

<a id="d-24"></a>
**D-24. Dokumentacja rozjechana z kodem.** [`05_audit_module.md` §2](05_audit_module.md) wymienia 7 wartości `EntityType`, w kodzie jest 9 (brakuje `device_identity_credential` i `device_identity_activation_code`). [`01_backend-architecture.md` §3](01_backend-architecture.md) opisuje strukturę z `core/base.py` i `infrastructure/nosql/`, których nie ma, a §5.2 i §9 pokazują `async def` i `AsyncSession` wbrew W-01.

<a id="d-25"></a>
**D-25. `passlib` w zależnościach, nieużywany w kodzie.** Hasła obsługuje bezpośrednio `bcrypt` ([`password.py`](../../../backend/app/modules/security/services/password.py)); `passlib==1.7.4` zostaje w `requirements.txt` i w `pyproject.toml` jako martwa zależność (i jedna pozycja więcej do śledzenia pod kątem podatności).

<a id="d-26"></a>
**D-26. Brak identyfikatora korelacji w logach.** Globalny handler loguje metodę i ścieżkę, ale nic nie wiąże wpisu z konkretnym żądaniem, użytkownikiem ani urządzeniem. Przy diagnostyce problemu zgłoszonego przez gminę („o 14:30 nie działało") to jest różnica między jednym `grep` a przeglądaniem wszystkiego.

<a id="d-27"></a>
**D-27. Nazwy niezgodne z zachowaniem w warstwie urządzeń.** `DELETE /orgs/{org_id}/devices/{device_id}` nazywa się `delete_device`, a wywołuje `detach_from_organization` i zwraca „Device detached from organization" ([`api/devices.py:73-82`](../../../backend/app/modules/core_data/api/devices.py#L73-L82)) — metoda HTTP i nazwa funkcji obiecują usunięcie, którego nie ma. Analogicznie [`DeviceRepository.assign_water_object(device, water_object_id: UUID)`](../../../backend/app/modules/core_data/repositories/devices.py#L66-L68) służy również do **odpinania** urządzenia, wołane z `None` wbrew własnej adnotacji typu ([`devices.py:243`](../../../backend/app/modules/core_data/services/devices.py#L243)).

---

## 6. Audyt zgodności z regułami `ai-tools/.claude/rules/`

Sprawdzone trzy reguły dotyczące tego zakresu. Zasada rozstrzygania: jeśli kod **konsekwentnie i z powodem** robi inaczej — nieaktualna jest reguła; jeśli robi różnie i bez powodu — to dług.

### 6.1. `python-coding-standards`

**Przestrzegane:** długość linii 88, podwójne cudzysłowy, sortowanie importów, unie przez `|`, nazewnictwo (moduły, klasy, funkcje, stałe, schematy Pydantica), parametry zapytań zawsze przez schemat z `Depends()` (0 wystąpień gołego `Query(`), brak mutowalnych argumentów domyślnych, brak gołego `except:`. Konfiguracja `ruff` w `pyproject.toml` jest zgodna z regułą co do joty.

| Odstępstwo | Charakter | Wniosek |
|---|---|---|
| Wzorce FastAPI w regule są asynchroniczne (`async def`, `AsyncSession`) | konsekwentne, uzasadnione (W-01) | **korekta reguły** |
| `uv` + `uv.lock` — projekt używa `pip` z `requirements.txt` (pinowany) i `pyproject.toml` | konsekwentne; brak `uv.lock` w repo | **decyzja do podjęcia** ([P-03](#p-03)) |
| `mypy strict` — w `pyproject.toml` `strict = false`, mypy nie jest w pre-commit ani w CI | reguła nieegzekwowana; część funkcji bez adnotacji (`_state(self, device)`, `list_all(self, query, org_access)`) | **dług/decyzja**, nie korekta reguły |
| Długość pliku ~300 linii — `groups.py` ma 523 | jednorazowe | drobiazg, do rozbicia przy okazji |

**Proponowana korekta reguły** (sekcja „FastAPI Patterns", po bloku `Router structure`):

```diff
+### Sync vs async
+
+Choose one and hold it. A `def` endpoint runs in FastAPI's threadpool and is the
+right default when the data layer is synchronous (`sqlalchemy.orm.Session`).
+`async def` is only correct when everything it awaits is genuinely async —
+an `async def` endpoint calling a blocking session blocks the event loop and is
+strictly worse than `def`.
```

**Proponowana korekta** (sekcja „Package Management"):

```diff
-Use `uv` exclusively - not pip or poetry. Always commit `uv.lock`. Do not commit `.venv/`.
+Use `uv` for new projects - not pip or poetry; always commit `uv.lock`.
+An existing project on pinned `requirements.txt` may stay there, but must pin
+every transitive dependency and keep `pyproject.toml` as the single declaration
+of direct dependencies. Never commit `.venv/`.
```

### 6.2. `error-handling-patterns`

**Przestrzegane:** walidacja na granicy systemu, brak łapania nieznanych wyjątków, brak wycieku szczegółów w odpowiedzi 500, logowanie raz (w globalnym handlerze), `logger.exception()` dla błędów nieoczekiwanych. Zasada „serwisy rzucają wyjątki domenowe, nigdy `HTTPException`" jest przestrzegana w 100 %.

| Odstępstwo | Charakter | Wniosek |
|---|---|---|
| Hierarchia: reguła mówi `AppError` w `app/exceptions.py`; kod ma `APIError` w `app/core/errors.py`, a kolizję z Pydantic rozwiązuje jako `ValidationException` | konsekwentne, rozwiązuje ten sam problem co reguła | **korekta reguły** |
| Kształt odpowiedzi: reguła wymaga `{"error": {"code", "message"}}`, kod zwraca `{"detail", "code"?}` | konsekwentne po obu stronach kontraktu (backend + frontend) | **korekta reguły** ([ADR-0006](../adr/0006-kontrakt-bledu-detail-plus-code.md)) |
| Warstwa frontendowa reguły opisuje Angulara (`LoadState`, interceptor HTTP), projekt jest w React + axios | reguła opisuje inny stos | **korekta reguły** (poza zakresem B-04, do odnotowania) |

**Proponowana korekta reguły** (sekcja „API Error Response Contract"):

```diff
-```json
-{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [{"field": "email", "issue": "..."}] } }
-```
+FastAPI projects keep the framework-native shape, so validation errors and
+domain errors parse the same way on the client:
+
+```json
+{ "detail": "Human-readable message", "code": "ACTIVATION_CODE_EXPIRED" }
+```
+
+`detail` is descriptive and may change without breaking the contract. `code` is
+a stable identifier, present only where the client must recognise the specific
+case (e.g. to render its own localized message). Pydantic validation keeps
+FastAPI's native 422 body, where `detail` is a list of per-field errors.
```

**Proponowana korekta** (sekcja „Service Layer Rule"):

```diff
-Services raise domain exceptions (`NotFoundError`, `AuthorizationError`, `DomainValidationError`) - never `HTTPException` directly. Router layer catches and maps.
+Services and routers raise domain exceptions - never `HTTPException` directly;
+a global handler maps them to responses. The one exception is the authentication
+dependency layer, where a 401 must carry a `WWW-Authenticate` header and the
+response is inseparable from the HTTP scheme.
```

### 6.3. `security-checklist`

**Przestrzegane:** brak sekretów w repozytorium (`.env` w `.gitignore`, hasło maskowane w logach połączenia), walidacja wejścia wyłącznie na granicy przez Pydantica z ograniczeniami pól, brak interpolacji danych użytkownika do SQL (jedyne `exec_driver_sql` cytuje identyfikator schematu z konfiguracji przez `identifier_preparer.quote()`), CSRF niepotrzebne przy tokenie w nagłówku, rate limiting na logowaniu (5/min), stały koszt weryfikacji hasła dla nieistniejącego konta ([`burn_password_verification`](../../../backend/app/modules/security/services/password.py#L48)), 404 zamiast 403 przeciw enumeracji zasobów.

| Odstępstwo | Charakter | Wniosek |
|---|---|---|
| `python-jose` zamiast `PyJWT` (reguła: „unmaintained since 2022") | konsekwentne, ale bez uzasadnienia poza inercją | **dług** ([D-14](#d-14)) — migracja jest mechaniczna |
| HS256 bez `audience`/`issuer` zamiast RS256 | konsekwentne i obronione: jeden monolit jest jednocześnie emitentem i konsumentem tokenu, nie ma trzeciej strony weryfikującej podpis | **korekta reguły** |
| Token dostępu 120 min (reguła: 15–30), refresh 1 dzień (reguła: 7–30) bez rotacji | konsekwentne, ale odwrotne do intencji reguły: długi token dostępu i krótki refresh to najgorsza kombinacja — okno kompromitacji jest długie, a wygoda użytkownika i tak niska | **dług** ([D-14](#d-14)) |
| Refresh token w `localStorage` zamiast `httpOnly`/`Secure`/`SameSite=Strict` | konsekwentne, ale to realna ekspozycja przy dowolnym XSS | **dług** ([D-14](#d-14)); naprawa dotyka frontendu i endpointu odświeżania |
| Rate limiting nieobecny na `/auth/token/refresh` i endpointach uwierzytelniania urządzeń | niekonsekwentne | **dług** ([D-13](#d-13)) |

**Proponowana korekta reguły** (sekcja „Authentication (JWT)"):

```diff
-- Algorithms: `RS256` with `audience` and `issuer` validation.
+- Algorithms: `RS256` with `audience` and `issuer` validation whenever the token
+  is verified by a party other than its issuer (multiple services, external
+  consumers, federated identity).
+- A single deployable that both issues and verifies its own tokens may use
+  `HS256`, provided the secret comes from the environment, is at least 32 bytes,
+  and the application refuses to start in production without it. Every token
+  must still carry a `type` claim, checked on every use, so a token minted for
+  one kind of principal cannot be replayed as another.
```

---

## 7. Pytania do rozstrzygnięcia

Rzeczy, których nie da się rozstrzygnąć samym kodem — wymagają decyzji, nie kolejnej analizy.

<a id="p-01"></a>
**P-01. `last_seen_at` czy `last_diagnostics_at`?** Kod zapisuje jedno pole, interfejs czyta drugie ([D-03](#d-03)). Są trzy wyjścia: (a) ingest zapisuje `last_seen_at`, a `last_diagnostics_at` zostaje na przyszłą, faktyczną diagnostykę; (b) `last_diagnostics_at` zostaje przemianowane migracją na `last_seen_at`, a drugie pole znika; (c) oba mają zostać i znaczyć co innego — wtedy trzeba dopisać, kto ustawia `last_diagnostics_at`. Wybór zależy od tego, czy planowana jest osobna ramka diagnostyczna z urządzenia, o czym kod nic nie mówi.

<a id="p-02"></a>
**P-02. Czy `mypy` ma być bramą, czy ma zniknąć z reguł?** Dziś reguła wymaga trybu strict, konfiguracja ustawia `strict = false`, a narzędzie nie jest uruchamiane nigdzie. Trzeci stan — „wymagamy, ale nie sprawdzamy" — jest najgorszy z możliwych. Doprowadzenie kodu do `strict` to realna praca (adnotacje w serwisach, `Mapped[...]` w modelach); rezygnacja to zmiana reguły w `ai-tools`.

<a id="p-03"></a>
**P-03. `uv` czy pinowany `requirements.txt`?** Reguła mówi `uv`, projekt ma `requirements.txt` w stylu `pip freeze` plus deklaracje w `pyproject.toml`. Obie drogi są spójne; niespójne jest tylko to, że reguła mówi co innego niż praktyka.

<a id="p-04"></a>
**P-04. Jaka jest polityka języka komunikatów błędów?** Angielski w `detail` z tłumaczeniem po stronie interfejsu przez `code` (wymaga uzupełnienia `code` wszędzie tam, gdzie użytkownik ma to zobaczyć — [D-11](#d-11)), czy polski w `detail` (prościej dziś, ale API przestaje być językowo neutralne). Kod robi dziś jedno i drugie.

<a id="p-05"></a>
**P-05. Kiedy przestaje wystarczać JSONB?** [ADR-0009](../adr/0009-telemetria-jako-surowy-pakiet-jsonb.md) jest słuszny przy kilku prototypach, ale nie ma dziś ustalonego progu (liczba obiektów × retencja × częstość odpytywania), po którego przekroczeniu trzeba znormalizować pomiary albo sięgnąć po bazę szeregów czasowych. Bez tego progu decyzja zostanie odłożona do momentu, w którym wykresy zaczną się urywać na `truncated`.

---

## Załącznik: jak odtworzyć ustalenia

```bash
# Błędy składni (D-01) — parser Pythona zamiast lintera
python3 - <<'PY'
import ast, pathlib
for p in sorted(pathlib.Path('backend/app').rglob('*.py')):
    try: ast.parse(p.read_text())
    except SyntaxError as e: print(f"{p}:{e.lineno}: {e.msg}")
PY

# Konwencja get_/find_ (W-05) — sygnatury i miejsca rzucania
python3 - <<'PY'
import ast, pathlib
for p in sorted(pathlib.Path('backend/app/modules').rglob('repositories/*.py')):
    try: t = ast.parse(p.read_text())
    except SyntaxError: continue
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef) and n.name.startswith(('get_', 'find_')):
            ret = ast.unparse(n.returns) if n.returns else '?'
            raises = any(isinstance(x, ast.Raise) for x in ast.walk(n))
            print(f"{p.name:32} {n.name:40} -> {ret:28} raises={raises}")
PY

# Granice transakcji i audytu (W-02, W-04)
grep -rn "\.transaction(\|skip_audit" backend/app --include=*.py | grep -v /tests/
grep -rn "\.commit()\|\.rollback()" backend/app --include=*.py | grep -v infrastructure/sql

# Synchroniczność (W-01)
grep -rn "async def" backend/app --include=*.py | grep -v /tests/
grep -rn "AsyncSession" backend/app --include=*.py   # brak wyników

# Kontrakt błędu (W-06)
grep -rn "HTTPException" backend/app/modules --include=*.py | grep -v /tests/
```
