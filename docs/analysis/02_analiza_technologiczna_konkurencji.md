# Analiza technologiczna i sprzętowa konkurencji — cały system

> Zlecenie **B-02**. Warstwa techniczna: firmware, sprzęt, transmisja, backend. Analiza **biznesowa** konkurencji istnieje osobno ([`01_plan_biznesowy.md §5.2`](../business/01_plan_biznesowy.md)) i nie jest tu powtarzana. Warstwa **UX/UI** to osobne zlecenie (B-03) — poza zakresem tego dokumentu.
>
> Data badania: **2026-09-01**. Interfejsy i cenniki zmieniają się między wersjami — każde ustalenie ma datę dostępu równą dacie badania.

---

## 0. Metoda i jej ograniczenia

### 0.1. Ograniczenie techniczne badania — przeczytaj przed użyciem wniosków

**W sesji, w której powstał ten dokument, bezpośrednie pobieranie stron (WebFetch/curl) było zablokowane przez politykę egress organizacji** — sprawdzone na `inventia.pl`, `aquard.pl`, `kallipr.com`, `docs.golioth.io` i `en.wikipedia.org` (wszystkie: `403` na tunelu CONNECT / `EGRESS_BLOCKED`). Działało wyłącznie wyszukiwanie (WebSearch), które zwraca odpowiedź syntetyzowaną z treści stron wraz z adresami źródeł.

Konsekwencja, którą trzeba znać czytając tabele niżej:

- **Adresy źródeł są prawdziwe i weryfikowalne** — każdy link prowadzi do konkretnej karty katalogowej, instrukcji lub strony produktowej producenta.
- **Treść tych źródeł nie została odczytana bezpośrednio przez autora dokumentu**, tylko za pośrednictwem wyszukiwarki. Liczby i parametry są cytatami z tych stron, ale nie zostały zweryfikowane wzrokowo w PDF-ie.
- **Dlatego żadne ustalenie w tym dokumencie nie ma pewności „wysoka" na podstawie samego wyszukiwania.** Poziom „wysoka" zarezerwowany jest dla ustaleń o **naszym własnym systemie**, które pochodzą z kodu w tym repozytorium.
- Przed użyciem konkretnej liczby w ofercie, umowie lub decyzji zakupowej — **otwórz link i potwierdź**. Lista linków do potwierdzenia: [§10](#10-źródła).

To ograniczenie nie unieważnia analizy: kierunki, wzorce architektoniczne i luki względem rynku są ustalone na tyle spójnie między niezależnymi źródłami, że wnioski się bronią. Unieważnia natomiast używanie pojedynczych liczb (ceny, lata pracy baterii, liczby kanałów) jako twardych danych bez potwierdzenia.

### 0.2. Konwencja etykiet

Każde istotne ustalenie o podmiocie zewnętrznym ma etykietę `[typ źródła / pewność]`:

| Typ źródła | Znaczenie |
|---|---|
| **D** | dokumentacja techniczna, instrukcja obsługi, karta katalogowa (PDF producenta) |
| **P** | strona produktowa producenta z treścią techniczną |
| **T** | trzecia strona: dystrybutor, katalog branżowy, prasa techniczna |
| **M** | materiał marketingowy (najsłabszy — traktowany jako deklaracja, nie fakt) |

| Pewność | Znaczenie |
|---|---|
| **Ś** | średnia — parametr konkretny, spójny między źródłami, ale odczytany przez wyszukiwarkę (zob. §0.1) |
| **N** | niska — pojedyncze źródło, sformułowanie ogólne, albo źródło typu M |
| **W** | wysoka — **wyłącznie dla naszego systemu**, ustalenia z kodu w tym repozytorium |

**„nieujawnione"** = informacji nie ma publicznie. Nie zgadujemy i nie wypełniamy komórki domysłem.

### 0.3. Kolejność wiarygodności

Zgodnie z briefem: dokumentacja techniczna i developerska producenta → karty katalogowe i instrukcje PDF → whitepapery → materiały marketingowe. Gdzie dostępna była instrukcja obsługi (HWM, Ovarro, Ayyeka, AquaRD), ma pierwszeństwo nad stroną produktową. Wyłącznie źródła publicznie dostępne — bez płatnych raportów i bez rejestracji na dema.

---

## 1. Kogo zbadano, a kogo odrzucono i dlaczego

### 1.1. Konkurenci polscy (lista zamknięta z §5.2 — nie szukano nowych)

| Podmiot | Badany produkt techniczny |
|---|---|
| **Inventia** | moduły MOBICON MT-151 / MT-251 / MT-331 + platforma DataPortal |
| **AquaRD** | rodzina rejestratorów CellBOX (H4, H3, HS, SMET, U4, R) |
| **UniCloud / Unitronics / Elmark** | sterowniki UniStream, routery UCR, platforma UniCloud |
| **Hawle.live** | stacja Hawle.live BOX, Hawle.live CAP (hydrant) |
| **AIUT WaterPrime** | platforma analityczna (warstwa danych, nie urządzenie) |

### 1.2. Wzorce światowe — przyjęte

| Podmiot | Dlaczego porównywalny |
|---|---|
| **Kallipr** (Captis + Kloud) | wzorzec z §5.2.5; urządzenie IoT + platforma zarządzania flotą, model bardzo zbliżony do docelowego |
| **Ayyeka** (Wavelet + platforma) | battery-powered IIoT edge device dla utilities, silny nacisk na cyberbezpieczeństwo — bezpośredni odpowiednik naszego kierunku |
| **Metasphere** (Point Orange) | bateryjny RTU dla wod-kan, otwarty protokół WITS-DNP3, zdalna konfiguracja i firmware |
| **HWM Global** (Multilog 2 + DataGate) | wielokanałowy logger LTE-M + platforma; najlepiej udokumentowany publicznie proces provisioningu i konfiguracji |
| **Ovarro** (TBox RTU) | górna półka RTU: 40+ protokołów, natywne MQTT/OPC UA — benchmark tego, co znaczy „szeroka integracja" |
| **Xylem / Sensus** (FlexNet) | wzorzec architektury sieciowej i modelu dostarczania (NaaS) w skali AMI |

### 1.3. Odrzucone — z uzasadnieniem

| Podmiot | Dlaczego odrzucony |
|---|---|
| **Itron** | AMI/opomiarowanie masowe rozliczeniowe. Problem inny niż nasz (monitoring obiektów procesowych), a warstwa techniczna zamknięta za relacją handlową — brak publicznej dokumentacji do porównania na 11 wymiarach. |
| **Nivus** | producent przepływomierzy (pomiar, nie platforma telemetryczna). Konkurencja dla *czujnika*, nie dla systemu. Poza osią tego zlecenia. |
| **Balena** | zarządzanie flotą kontenerów na **Linuksie** (balenaOS, balenaEngine). Nasz gateway to mikrokontroler ESP32-S3 bez systemu operacyjnego z kontenerami. Architektonicznie nieprzenośne — żaden mechanizm nie daje się u nas zastosować. Odrzucone jako wzorzec, opisane w §7 tylko po to, żeby zamknąć pytanie. |
| **Telit** (deviceWISE) | platforma enterprise „pay-as-you-go" bez publicznego cennika i bez publicznej dokumentacji integracyjnej na poziomie pozwalającym ocenić koszt. Zostawione w §7 jako kategoria, bez ustaleń szczegółowych — **nieujawnione**. |

**Uwaga rozgraniczająca:** Golioth, Blues Wireless, Memfault i AWS IoT Core **nie są konkurencją** i celowo nie występują w tabeli porównawczej (§3). To potencjalne komponenty do kupienia zamiast zbudowania — osobna sekcja [§7](#7-platformy-ogólnego-przeznaczenia--kupić-czy-zbudować).

---

## 2. Punkt odniesienia — nasz system, stan na 2026-09-01

Żeby porównanie miało sens, najpierw twardo: co mamy, ustalone z kodu. Wszystkie pozycje w tej tabeli mają pewność **W** (wysoka).

| Wymiar | Stan faktyczny | Dowód |
|---|---|---|
| Sprzęt gatewaya | ESP32-S3-DevKitC-1 + KAmod A7670E HAT, montaż własny, **bez obudowy, bez klasy IP, bez ochrony przepięciowej**, zasilanie zewnętrzne 5 V / min. 2 A | [`01_hardware.md`](../technical/firmware/01_hardware.md) |
| Interfejsy pomiarowe | SPI → MAX31865 → PT100 — **jedyny działający kanał**. Ciśnienie (PT-506, 4-20 mA): **w firmware nie istnieje w żadnej postaci** — brak klasy czujnika, brak rejestracji, brak odczytu ADC. Modbus: brak. | [`main.cpp:94-97`](../../firmware/src/main.cpp#L94-L97) rejestruje wyłącznie `PT100Sensor`; `firmware/lib/Sensor/src/` zawiera tylko `PT100Sensor.{h,cpp}`; `grep -rin "pressure" firmware/` → 0 trafień |
| Protokół transmisji | HTTPS POST JSON, `POST /telemetry/ingest`, port 443 | [`Config.h`](../../firmware/include/Config.h), [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md) |
| Tożsamość urządzenia | para EC P-256 generowana **na urządzeniu**, challenge/response, token Bearer 36 h. Klucz prywatny (32 B) w NVS przez `Preferences`. | [`DeviceIdentity.cpp:205`](../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L205), [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md) |
| Provisioning w terenie | kod aktywacyjny wpisywany **przez port szeregowy**: `ACTIVATE YU4N-6HGS-Y3` → `ACTIVATION_CODE_ACCEPTED` | [`04_device_provisioning_flow.md §3.2`](../technical/firmware/04_device_provisioning_flow.md) |
| Format telemetrii | okna agregowane (15 s), batch 4 okien ≈ 60 s, `quality` per punkt, `errors[]` z kodami, dedupe po `(device_id, seq)` → `200 duplicate` | [`04_telemetry_module.md §3, §5`](../technical/backend/04_telemetry_module.md) |
| Bufor lokalny | **wyłącznie RAM**, `RETAIN_WINDOWS_MAX = 12 × WINDOWS_PER_BATCH` ≈ **12 minut** | [`04_telemetry_module.md §5`](../technical/backend/04_telemetry_module.md) |
| Konfiguracja bez rekompilacji | [`sensor_registry.yaml`](../../sensor_registry.yaml) — tylko `point_types` i `error_codes`. **Brak profili urządzeń, brak mapowania rejestrów, brak konfiguracji z przeglądarki.** Nowy czujnik = nowa klasa C++ + rekompilacja. | [`sensor_registry.yaml`](../../sensor_registry.yaml), [`04_telemetry_module.md §5`](../technical/backend/04_telemetry_module.md) |
| OTA | **nie istnieje.** Brak `esp_ota`, `Update.h`, `httpUpdate`, `ArduinoOTA` w całym `firmware/`. | `grep -rn "esp_ota\|Update.h\|httpUpdate\|ArduinoOTA" firmware/` → 0 trafień |
| Zarządzanie flotą / SIM | brak. Brak kanałów wydawniczych, rollbacku, inwentarza kart SIM. | jw. |
| Model danych | PostgreSQL (`psycopg2`), pakiety jako **JSONB w jednej tabeli** `telemetry_packets`. Brak TSDB, brak partycjonowania, **brak polityki retencji, brak downsamplingu**. `MAX_PACKETS_PER_SERIES = 5000` jako zabezpieczenie zapytań. | [`requirements.txt`](../../backend/requirements.txt), [`04_telemetry_module.md §2, §3`](../technical/backend/04_telemetry_module.md) |
| Alarmy | **moduł nie istnieje.** Jest tylko status obiektu wyliczany w zapytaniu: `no_data` / `no_comm` / `warning` / `ok`. | brak `alarm_rule` / `class Alarm` w `backend/app`; [`04_telemetry_module.md §3`](../technical/backend/04_telemetry_module.md) |
| API | REST `/api/v1/orgs/{org_id}/...` + `/api/v1/platform/...`, JWT, dwie płaszczyzny dostępu. Brak webhooków, brak OPC UA, brak integracji SCADA. | [`01_backend-architecture.md §7`](../technical/backend/01_backend-architecture.md) |
| Bezpieczeństwo | brak współdzielonego sekretu, audit log append-only wymuszony przez `AuditAwareSession`, read-only wobec procesu. Brak: secure boot, flash/NVS encryption, OTA (= brak ścieżki łatania), ISO 27001, polityki ujawniania podatności. | [`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md), [`05_audit_module.md`](../technical/backend/05_audit_module.md) |

---

## 3. Tabela porównawcza — podmiot × 11 wymiarów

Tabela rozbita na trzy części dla czytelności. **W3** = wariant docelowy naszego sprzętu z briefu B-01 (przemysłowy ESP32 w obudowie DIN) — pokazany tam, gdzie zmienia ocenę.

### 3.1. Wymiary 1–4: sprzęt, interfejsy, protokół, tożsamość

| Podmiot | 1. Architektura sprzętowa gatewaya | 2. Interfejsy pomiarowe | 3. Protokół urządzenie ↔ chmura | 4. Tożsamość i provisioning |
|---|---|---|---|---|
| **NASZ SYSTEM** | zestaw deweloperski, montaż własny, brak obudowy/IP/ochrony przepięciowej, zasilanie sieciowe 5 V | PT100 przez SPI. 4-20 mA **niezaimplementowane**. Modbus **brak** | HTTPS POST JSON, specyfikacja udokumentowana wewnętrznie, **niepublikowana** | EC P-256 generowana na urządzeniu + challenge/response + kod jednorazowy. Klucz w **jawnym NVS**. Aktywacja **przez port szeregowy → wymaga laptopa** |
| **Inventia** (MT-151/251/331) | przemysłowa obudowa na szynę DIN; tryb energooszczędny → praca z baterii lub panelu solarnego `[P/Ś]` | MT-151: 16 wejść binarnych, 12 wyjść binarnych, 4× 4-20 mA, 2× 0-10 V; konfigurowalna liczba wejść licznikowych `[T/Ś]` | MQTT 3.1 (MT-331); dodatkowo Modbus RTU/TCP, M-BUS, IEC 60870-5-104, SNMP, GENIbus jako protokoły polowe `[P/Ś]`. Specyfikacja własnego formatu: **nieujawniona** | rejestracja w DataPortal przez **numer seryjny + IMEI**, bez dodatkowego oprogramowania `[P/Ś]`. Zabezpieczenia zdalnego dostępu: lista autoryzowanych IP i numerów telefonów, opcjonalne hasło, blokada odczytu `[P/Ś]` |
| **AquaRD** (CellBOX H4) | rejestrator terenowy, warianty **IP68 i IP54**; do **5 lat** pracy na wbudowanych bateriach dzięki uśpieniu modułu GSM `[P/Ś]` | **6 wejść analogowych + 6 cyfrowych**; dwie niezależne magistrale **Modbus RTU/ASCII po RS485**, do 10 urządzeń; wejścia impulsowe z wodomierzy `[P/Ś]` | GPRS / LTE Cat M1 / NB-IoT, opcjonalnie **WIZE 169 MHz** `[P/Ś]`. Format do systemu nadrzędnego: **nieujawniony** publicznie | konfigurator producenta (`Konfigurator CellBOX-UxR RTU` — instrukcja publiczna) `[D/Ś]`. Model tożsamości kryptograficznej: **nieujawniony** |
| **UniCloud / Unitronics** | sterownik PLC UniStream **albo router UCR** w obiekcie — sprzęt przemysłowy, ale ekosystemowy `[P/Ś]` | przez PLC/router: Modbus i dowolne urządzenia mówiące Modbus podpinane do UniCloud przez routery UCR `[P/Ś]`; EtherNet/IP, SNMP | **MQTT** natywnie, REST API po TLS, OPC UA, SQL client `[P/Ś]` | **MQTT z uwierzytelnianiem X.509** `[P/Ś]` — najbliższy naszemu modelowi asymetrycznemu w polskiej stawce. Uruchomienie deklarowane jako „30 minut" `[M/N]` |
| **Hawle.live BOX** | gotowa stacja terenowa sprzedawana z armaturą; wariant CAP montowany w hydrancie podziemnym `[P/N]` | sonda optyczna (barwa, mętność) + „szereg innych czujników" — **realny katalog nieujawniony** `[M/N]` | LTE-M i NB-IoT `[P/Ś]`. Protokół aplikacyjny: **nieujawniony** | **nieujawnione** |
| **AIUT WaterPrime** | nie dostarcza własnego gatewaya — platforma nad cudzymi danymi `[P/Ś]` | integruje dane z opomiarowania, modeli hydraulicznych i zdalnych odczytów; warstwa danych, nie wejść fizycznych `[P/Ś]` | nie dotyczy — integracja na poziomie baz i systemów `[P/Ś]` | nie dotyczy |
| **Kallipr** (Captis S1/S2) | **IP68**, pełna hermetyzacja do zanurzenia, antena wewnętrzna lub zewnętrzna; bateria wymienna, opcjonalnie solar/DC `[P/Ś]`. Captis S2 komunikowany jako **„20-Year Battery"** `[M/N]` | impulsowe, analogowe, **Modbus** `[P/Ś]` | LTE-M (Cat-M1) i NB-IoT `[P/Ś]`. **Publikuje specyfikację MQTT i przewodniki API** w portalu wsparcia `[P/Ś]` — jedyny w stawce, który to robi jawnie | aplikacja mobilna **Kallipr Kloud Field**: skan urządzenia, konfiguracja i weryfikacja w terenie, **Bluetooth** do bezpośredniej komunikacji (szybciej przy słabym zasięgu), praca offline z późniejszą synchronizacją `[P/Ś]` |
| **Ayyeka** (Wavelet V2 / V2 EX) | **IP68 / NEMA6p**, wariant **iskrobezpieczny (EX)**, zasilanie bateryjne, praca w warunkach ekstremalnych `[D/Ś]` | wieloczujnikowy edge device dla infrastruktury utilities; katalog wejść w karcie katalogowej `[D/Ś]` | dane szyfrowane, transmisja ciągła; wsparcie **OPC, DNP3** oraz protokołów własnych `[D/Ś]` | „szyfrowanie, uwierzytelnianie i zdalne aktualizacje" jako filar produktu `[D/Ś]`. Konkretny mechanizm (X.509 / secure element): **nieujawniony** |
| **Metasphere** (Point Orange) | bateryjny RTU, **IP68 do 4 m przez 4 dni**, opatentowany wewnętrzny czujnik zalania, **5+ lat** na baterii `[P/Ś]` | **Modbus Master (RS232 i RS485) do 10 czujników**, **SDI-12 multidrop do 10 czujników**, do 5 konfigurowalnych I/O `[P/Ś]` | **DNP3, WITS-DNP3**, Medina; warianty 4G/GSM-GPRS oraz NB-IoT/Cat-M1 `[P/Ś]`. WITS-DNP3 to **otwarty, publikowany standard branżowy** (WITS PSA) `[P/Ś]` | **nieujawnione** w warstwie kryptograficznej; zdalna konfiguracja jest natywna `[P/Ś]` |
| **HWM** (Multilog 2 / 2 WW) | logger terenowy; wariant WW dla ścieków (non-ATEX), wariant Multilog IS iskrobezpieczny `[D/Ś]` | **do 8 kanałów**: analogowe, cyfrowe, **Modbus** (logger jako master, adresowanie i zapis/odczyt rejestrów), **SDI-12**, wyjścia sterujące `[D/Ś]` | LTE-M z fallbackiem 2G, alternatywnie 3G/2G `[D/Ś]`; warianty wspierające **WITS** — osobny suplement instrukcji `[D/Ś]` | **provisioning fabryczny**: urządzenie opuszczające fabrykę jest już zarejestrowane w DataGate i powiązane z pustym „blank site" `[D/Ś]`. Konfiguracja narzędziem **IDT** — zalecana **przed wyjazdem w teren** `[D/Ś]` |
| **Ovarro** (TBox RTU) | rodzina RTU od 5 punktów I/O do setek na szafę; karty I/O i komunikacyjne wymienne `[P/Ś]` | modularne I/O; jako master/slave w Modbus RTU/TCP/ASCII `[P/Ś]` | **40+ protokołów**: Modbus, DNP 3.0, IEC 60870-5-101/104, OPC UA, **MQTT(S)**, EtherNet/IP, IEC 61850 (MMS) — **bez dodatkowego gatewaya** `[P/Ś]` | pakiet cyberbezpieczeństwa: uwierzytelnianie, szyfrowanie, firewall, SSL/TLS, HTTPS, SMTPS, SFTP/FTPS, VPN `[P/Ś]`. Model tożsamości urządzenia: **nieujawniony** |
| **Xylem / Sensus** (FlexNet) | dedykowana sieć komunikacyjna operatorska (nie pojedynczy gateway) `[P/Ś]` | liczniki i czujniki w ekosystemie Sensus `[P/Ś]` | własna sieć dwukierunkowa FlexNet `[P/Ś]`; specyfikacja radiowa: **nieujawniona** | **nieujawnione** |

### 3.2. Wymiary 5–8: telemetria, konfiguracja, OTA, dane

| Podmiot | 5. Format telemetrii | 6. Konfiguracja bez rekompilacji | 7. OTA i zarządzanie flotą | 8. Model danych i retencja |
|---|---|---|---|---|
| **NASZ SYSTEM** | okna agregowane 15 s, batch ≈60 s, `quality` per punkt, `errors[]`, **dedupe po `(device_id, seq)`**. Bufor **RAM ≈ 12 min** | tylko katalog typów i kodów błędów. **Nowy czujnik = kod C++ + rekompilacja** | **brak w całości** | PostgreSQL + JSONB, jedna tabela, **brak retencji i downsamplingu** |
| **Inventia** | wbudowany rejestrator danych i zdarzeń **z zapisem na kartę microSD** `[P/Ś]` | **zdalna konfiguracja i programowanie przez sieć bezprzewodową**; program użytkownika w **CODESYS** (MT-151) `[P/Ś]` | **zdalna zmiana aplikacji i firmware'u przez GPRS/3G**, narzędziem MTManager `[P/Ś]` — pełny OTA, standard rynkowy od lat | DataPortal w chmurze **AWS**; archiwizacja i prezentacja w przeglądarce `[P/Ś]`. Silnik bazodanowy i retencja: **nieujawnione** |
| **AquaRD** | rejestrator wielokanałowy, programowalny; zapis lokalny przed transmisją `[P/Ś]` | konfigurator producenta z instrukcją publiczną, w tym mapowanie Modbus RTU `[D/Ś]` | **nieujawnione** publicznie | **nieujawnione** |
| **UniCloud** | dashboardy budowane bez kodu nad danymi z PLC `[M/N]` | **„no-code"** budowa dashboardów; integracja urządzeń Modbus przez routery UCR bez programowania PLC `[P/Ś]` | zarządzanie przez chmurę; **5-letnia przedpłacona subskrypcja startowa** dołączana do UniStream Cloud PLC `[M/N]` | **nieujawnione** |
| **Hawle.live** | **nieujawnione** | **nieujawnione** | **nieujawnione** | **nieujawnione** |
| **WaterPrime** | nie dotyczy — wejściem są dane, nie surowe pomiary `[P/Ś]` | konfiguracja modeli i stref DMA po stronie platformy `[P/Ś]` | nie dotyczy | analityka: wskaźnik ILI per DMA, wzorce zużycia dla grup odbiorców, wykrywanie anomalii `[P/Ś]`; **IBM Maximo** jako warstwa EAM/CMMS `[P/Ś]` |
| **Kallipr** | **konfigurowalna częstotliwość logowania od 10 sekund**, sterowana z Kloud `[P/Ś]` | konfiguracja z chmury i z aplikacji terenowej, bez rekompilacji `[P/Ś]` | **OTA firmware z powiadomieniem użytkownika o dostępnej aktualizacji w Kallipr Kloud** `[P/Ś]`; osobny produkt **Kloud Fleet** do zarządzania flotą `[P/Ś]` | **nieujawnione**; integracja danych przez REST API `[P/Ś]` |
| **Ayyeka** | ciągłe zbieranie, przechowywanie i transmisja danych szyfrowanych `[D/Ś]` | **nieujawnione** | **„zdalne aktualizacje"** wymienione jako funkcja produktu `[D/Ś]`; szczegóły nieujawnione | platforma z integracją do systemów zewnętrznych przez REST/SOAP `[D/Ś]` |
| **Metasphere** | duża pamięć lokalna rejestratora; dane znaczone czasem `[P/Ś]` | **zdalna konfiguracja** `[P/Ś]` | **zdalna aktualizacja firmware'u** `[P/Ś]` | **nieujawnione** |
| **HWM** | do 8 kanałów, znaczniki czasu; przesył do DataGate/HWMOnline `[D/Ś]` | konfiguracja rejestrów Modbus narzędziem IDT — **w biurze przed wyjazdem** `[D/Ś]` | **nieujawnione** wprost w przejrzanych instrukcjach | DataGate jako platforma danych z administracją użytkowników i witryn `[D/Ś]`; retencja **nieujawniona** |
| **Ovarro** | pełny RTU z lokalną logiką i buforem `[P/Ś]` | konfiguracja i program RTU; natywne MQTT/OPC UA do chmury bez dodatkowego sprzętu `[P/Ś]` | **nieujawnione** wprost; pakiet cyberbezpieczeństwa sugeruje zarządzany cykl życia `[P/Ś]` | **nieujawnione** |
| **Xylem / Sensus** | dane dystrybucji zbierane siecią FlexNet `[P/Ś]` | **nieujawnione** | sieć w modelu **NaaS** — operator utrzymuje infrastrukturę `[P/Ś]` | Sensus Analytics + **Xylem Data Lake** `[P/Ś]` |

### 3.3. Wymiary 9–11: alarmy, API, bezpieczeństwo

| Podmiot | 9. Model alarmów | 10. API i integracje | 11. Bezpieczeństwo (deklaracje publiczne) |
|---|---|---|---|
| **NASZ SYSTEM** | **brak modułu.** Tylko status obiektu liczony w chmurze przy zapytaniu | REST + JWT, dwie płaszczyzny dostępu. **Brak webhooków, OPC UA, integracji SCADA** | auth asymetryczna urządzenia, audit log append-only, read-only. **Brak OTA → brak ścieżki łatania.** Brak certyfikatów i polityki ujawniania podatności |
| **Inventia** | alarmowanie w DataPortal + logika lokalna w module (program użytkownika) `[P/Ś]` | **MTDataProvider: OPC UA/DA, ODBC, CSV** — integracja ze SCADA, bazami relacyjnymi i systemami zarządzania danymi `[P/Ś]` | deklaruje **ISO 9001 i ISO/IEC 27001**, zarządzanie podatnościami, ciągłość wsparcia, cyberodporność `[M/N — deklaracja własna, §5.2 planu]`; kontrola dostępu przez listy IP/numerów, hasło, blokada odczytu `[P/Ś]` |
| **AquaRD** | alarmowanie w warstwie SCADA/platformy `[P/N]` | integracja z istniejącą infrastrukturą, SCADA, GIS, bilansowanie `[P/N]` | **nieujawnione** |
| **UniCloud** | alarmy w platformie chmurowej `[M/N]` | **REST API po TLS**, MQTT, OPC UA, SQL client, SNMP `[P/Ś]` | **szyfrowane REST API po TLS, MQTT X.509, antywirus i reguły WAF** `[P/Ś]` — najkonkretniejsza publiczna deklaracja w polskiej stawce |
| **Hawle.live** | alarmowanie, raporty i prezentacja geograficzna `[M/N]` | portal WWW + aplikacja `[M/N]` | **nieujawnione** |
| **WaterPrime** | alarmy, rekomendacje i prognozy generowane przez AI nad danymi `[P/Ś]` | integracja wielu baz i modeli; **IBM Maximo** `[P/Ś]` | **nieujawnione** |
| **Kallipr** | alarmy i trendy w Kloud `[P/Ś]` | **REST API**, opublikowana **specyfikacja MQTT**, przewodniki API, noty wydawnicze firmware `[P/Ś]` | **nieujawnione** wprost |
| **Ayyeka** | monitoring i predykcyjne utrzymanie aktywów `[D/Ś]` | **OPC, DNP3**, protokoły własne; integracja **REST lub SOAP** z systemami trzecimi `[D/Ś]` | pozycjonowanie „cyber-secure": szyfrowanie, uwierzytelnianie, zdalne aktualizacje `[D/Ś]`; brak publicznych certyfikatów w przejrzanych materiałach |
| **Metasphere** | RTU z logiką lokalną — alarm generowany na urządzeniu (np. przelew w kanalizacji) `[P/Ś]` | **WITS-DNP3** jako standard interoperacyjności między dostawcami `[P/Ś]` | **nieujawnione** wprost |
| **HWM** | alarmy w DataGate/HWMOnline `[D/Ś]` | DataGate jako punkt integracji `[D/Ś]` | **nieujawnione** wprost |
| **Ovarro** | pełna logika alarmowa na RTU + w systemie nadrzędnym `[P/Ś]` | **40+ protokołów** natywnie, w tym OPC UA i MQTT(S) `[P/Ś]` | uwierzytelnianie, szyfrowanie, **firewall**, SSL/TLS, HTTPS, SMTPS, SFTP/FTPS, **VPN** `[P/Ś]` — najszerszy publiczny opis w stawce |
| **Xylem / Sensus** | aplikacje: wykrywanie wycieków, regulacja ciśnienia, demand response `[P/Ś]` | integracja z Xylem Data Lake `[P/Ś]` | „utility-grade", bezpieczna transmisja `[M/N]` |

---

## 4. Gdzie stoimy — werdykt na każdym z 11 wymiarów

Skala: **z tyłu** / **na poziomie** / **z przodu** względem stawki z §3. Kolumna „co konkretnie by to zmieniło" mówi o skutku dla klienta lub dla nas, nie o samej funkcji.

| # | Wymiar | Werdykt | Uzasadnienie | Co konkretnie by to zmieniło |
|---|---|---|---|---|
| 1 | Architektura sprzętowa | **z tyłu, wyraźnie** | Cała stawka to sprzęt przemysłowy: IP68 (Kallipr, Ayyeka, Metasphere, AquaRD), szyna DIN (Inventia), warianty iskrobezpieczne (Ayyeka EX, HWM IS). My: dev-kit bez obudowy i bez ochrony przepięciowej | Pierwsze przepięcie w hydroforni albo zalanie szafy kończy pilotaż. To jest ryzyko wdrożeniowe, nie estetyczne |
| 2 | Interfejsy pomiarowe | **z tyłu, najgłębiej z całej listy** | AquaRD: 6 AI + 6 DI + 2× RS485/Modbus. HWM: 8 kanałów + Modbus master + SDI-12. Metasphere: Modbus master do 10 czujników + SDI-12. My: **jeden kanał, temperatura**. Ciśnienia nie ma w kodzie wcale, Modbus zero | Bez Modbus RTU obietnica „neutralności sprzętowej" z [`CONTEXT.md`](../business/CONTEXT.md) i [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md) jest **niewykonalna technicznie**. Nie da się podpiąć istniejącego przepływomierza gminy. Co więcej: MVP zdefiniowane w §2.2.1 planu jako „temperatura **+ ciśnienie**" jest dziś zrealizowane w połowie |
| 3 | Protokół transmisji | **na poziomie** | HTTPS+JSON jest w porządku dla naszego profilu (zasilanie sieciowe, batch 60 s). Rynek idzie w MQTT (Inventia MT-331, UniStream, Kallipr) i WITS-DNP3 (UK). Przewaga rynku nie leży w protokole, tylko w tym, że **Kallipr specyfikację publikuje**, a my nie | Publikacja specyfikacji otwiera drogę integratorom i podnosi wiarygodność przy ocenie technicznej przez gminę. Sama zmiana na MQTT — niewiele |
| 4 | Tożsamość i provisioning | **rozdwojony: model z przodu, wykonanie z tyłu** | Model logiczny (klucz generowany na urządzeniu, brak współdzielonego sekretu, challenge/response) jest **mocniejszy niż większość stawki** — porównywalny z MQTT X.509 UniStream i lepszy niż provisioning fabryczny HWM. Ale: klucz prywatny leży w **jawnym NVS**, a aktywacja wymaga **podłączenia laptopa kablem** w hydroforni, podczas gdy Kallipr robi to aplikacją przez Bluetooth | Argument bezpieczeństwa jest realny i warto go używać w rozmowie z gminą — **pod warunkiem** domknięcia ochrony klucza. Aktywacja przez serial to konkretny koszt każdego wdrożenia |
| 5 | Format telemetrii | **z przodu** | Okna agregowane, `quality` per punkt, `errors[]` z katalogiem kodów, idempotencja po `(device_id, seq)` z odpowiedzią `200 duplicate` — to jest dojrzalsze niż typowy logger, który wysyła surowe próbki bez metadanych jakości. **Wyjątek: bufor.** 12 minut w RAM przy stawce, która trzyma dane na microSD (Inventia) i w dużej pamięci nieulotnej (Metasphere) | Format się obroni w rozmowie technicznej. Bufor **nie** — i jest wprost sprzeczny z własną deklaracją 72 h (§9.1) |
| 6 | Konfiguracja bez rekompilacji | **z tyłu, i to jest luka obietnica–stan** | Inventia: zdalna konfiguracja i programowanie przez sieć. HWM: mapowanie rejestrów Modbus narzędziem IDT. Kallipr: częstotliwość logowania od 10 s ustawiana z chmury. My: `sensor_registry.yaml` to katalog typów, **nie profil urządzenia** — nowy czujnik wymaga klasy C++ i rekompilacji | „Profil urządzenia" z [`CONTEXT.md`](../business/CONTEXT.md) dziś nie istnieje jako mechanizm. Każdy nietypowy klient = nowa wersja firmware, czyli dokładnie to, przed czym ADR-0002 ostrzega |
| 7 | OTA i zarządzanie flotą | **z tyłu, całkowicie — mamy zero** | Inventia zdalnie wymienia **firmware i aplikację przez GPRS** i robi to od lat. Metasphere: zdalna aktualizacja firmware. Kallipr: OTA z powiadomieniem w Kloud + osobny produkt Kloud Fleet. My: brak jakiegokolwiek mechanizmu | Bez OTA każda poprawka to wyjazd do obiektu. Gorzej: **przy NIS2/KSC brak procesu aktualizacji jest wprost zagrożeniem nr 7 z §5.2.8 planu** — gmina jako podmiot kluczowy ma prawo tego wymagać kontraktowo i nie mamy czym odpowiedzieć |
| 8 | Model danych i retencja | **z tyłu** | Stawka w większości nie ujawnia silnika, ale wzorzec inżynierski jest ustalony: hypertable + continuous aggregates + polityka retencji (Timescale), albo data lake (Xylem). My: JSONB w jednej tabeli, **bez retencji i bez downsamplingu**, z `MAX_PACKETS_PER_SERIES = 5000` jako protezą | Przy 15 obiektach × 60 s tabela rośnie bez ograniczenia, a wykresy roczne będą albo wolne, albo obcięte limitem 5000 pakietów. To dług, który rośnie liniowo z czasem działania pilotażu |
| 9 | Model alarmów | **z tyłu — modułu nie ma** | Metasphere i Ovarro ewaluują alarmy **na urządzeniu** (RTU z lokalną logiką), platformy chmurowe ewaluują centralnie. My mamy tylko status wyliczany przy zapytaniu | To główna funkcja produktu obiecana w §2.5–2.6 planu i jej po prostu nie ma. Bez alarmów produkt nie odpowiada na UC-03 ani UC-04 |
| 10 | API i integracje | **na poziomie w REST, z tyłu w integracji przemysłowej** | REST + JWT jest w porządku. Ale Inventia daje **OPC UA/DA i ODBC**, Ovarro 40+ protokołów natywnie, Ayyeka OPC/DNP3 + REST/SOAP. My: brak webhooków i brak jakiejkolwiek ścieżki do SCADA | Gmina, która ma już SCADA, nie ma jak wpiąć naszych danych. To zamyka część rynku i osłabia argument „nie wymieniamy waszej automatyki" |
| 11 | Bezpieczeństwo | **mieszany: fundament z przodu, proces z tyłu** | Z przodu: brak współdzielonego sekretu, audit log wymuszony na poziomie sesji, read-only. Z tyłu: brak secure boot i szyfrowania flash/NVS, **brak OTA = brak ścieżki łatania**, brak certyfikacji (Inventia deklaruje ISO 27001), brak polityki ujawniania podatności (Inventia i Ovarro komunikują zarządzanie podatnościami) | Fundament jest dobry i wart komunikowania. Ale przy ocenie dostawcy przez podmiot objęty NIS2 pytanie „jak łatacie podatność w urządzeniu w terenie" pada zawsze — i dziś odpowiedź brzmi „wyjazdem" |

**Podsumowanie werdyktu:** z przodu jesteśmy w **dwóch** miejscach (format telemetrii, model kryptograficzny tożsamości), na poziomie w **dwóch** (protokół, REST API), z tyłu w **siedmiu**. Trzy najgroźniejsze luki, bo blokują obietnicę produktu, a nie tylko go osłabiają: **brak Modbus (2)**, **brak OTA (7)**, **brak alarmów (9)**.

---

## 5. Co warto skopiować

Uszeregowane wg stosunku wartości do kosztu. Szacunki kosztu to **rzędy wielkości pracy inżynierskiej jednej osoby**, nie wyceny — oznaczone jako **suggestion**, bo nie wynikają z pomiaru w tym repozytorium.

### 5.1. Bufor telemetrii na pamięci nieulotnej zamiast RAM

**Skąd:** Inventia — rejestrator z zapisem na kartę microSD `[P/Ś]`; Metasphere — duża pamięć lokalna rejestratora `[P/Ś]`.

**Dlaczego u nas:** deklarujemy 72 h retencji bufora w [`CONTEXT.md`](../business/CONTEXT.md), a mamy ≈12 minut w RAM, kasowane każdym restartem — a restart jest u nas **normalną ścieżką recovery** ([`03_esp32_reset_and_recovery.md`](../technical/firmware/03_esp32_reset_and_recovery.md)). Każda dłuższa utrata zasięgu LTE albo watchdog = dziura w danych.

**Koszt: mały.** ESP32-S3 ma partycję SPIFFS/LittleFS na pokładzie — nie trzeba dokładać sprzętu. Ring buffer okien na flashu + zmiana `TelemetrySender` na źródło „z flasha, nie z RAM". **suggestion:** ~1 tydzień, w tym testy na `env:native`.

**Uwaga:** flash ESP32 ma ograniczoną liczbę cykli kasowania — zapis co 15 s wymaga ring buffera z rotacją, nie naiwnego „plik na okno".

### 5.2. OTA firmware z kanałami wydawniczymi i rollbackiem

**Skąd:** Inventia — zdalna wymiana firmware i aplikacji przez GPRS narzędziem MTManager `[P/Ś]`; Metasphere — zdalna aktualizacja `[P/Ś]`; Kallipr — OTA z powiadomieniem w Kloud `[P/Ś]`.

**Dlaczego u nas:** to jedyna luka, która jest jednocześnie problemem operacyjnym (każda poprawka = wyjazd), sprzedażowym (zagrożenie nr 7 z §5.2.8) i bezpieczeństwa (brak ścieżki łatania).

**Jak, konkretnie:** ESP-IDF ma `esp_https_ota` z dwiema partycjami aplikacji i `esp_ota_mark_app_valid_cancel_rollback()` — czyli **rollback po nieudanym starcie jest wbudowany w platformę**, nie trzeba go pisać. Manifest wersji wystawia backend, urządzenie odpytuje po już posiadanym tokenie Bearer — cała warstwa uwierzytelnienia już istnieje i nie trzeba jej dublować.

**Ryzyko do zaprojektowania, nie do pominięcia:** pobranie obrazu (~1–2 MB) przez A7670E przy naszym profilu transmisji zajmie minuty i musi współistnieć z watchdogiem (`WATCHDOG_STUCK_MS = 5 min`) oraz z buforowaniem pomiarów w trakcie aktualizacji. To jest właściwy powód, żeby najpierw zrobić §5.1.

**Koszt: średni.** **suggestion:** ~2–3 tygodnie (firmware + endpoint manifestu + kanały `stable`/`beta` + test rollbacku na płytce).

### 5.3. Modbus RTU master + profil urządzenia jako dane, nie kod

**Skąd:** AquaRD — 2 niezależne magistrale RS485, do 10 urządzeń, Modbus RTU/ASCII `[P/Ś]`; HWM — logger jako master z adresowaniem i zapisem/odczytem rejestrów, konfigurowany narzędziem IDT `[D/Ś]`; Metasphere — Modbus master do 10 czujników `[P/Ś]`.

**Dlaczego u nas:** to jest **warunek prawdziwości głównej obietnicy produktu**. „Podłączamy się do tego, co gmina ma" bez Modbusa oznacza „podłączamy się do czujników, które sami przywieziemy".

**Jak, konkretnie — najważniejsza część wzorca:** u wszystkich trzech mapowanie rejestrów jest **konfiguracją**, nie kodem. Nasz odpowiednik: rozszerzyć [`sensor_registry.yaml`](../../sensor_registry.yaml) o sekcję `device_profiles` (adres slave, prędkość/parzystość, adres i typ rejestru, kolejność bajtów, skalowanie, jednostka, mapowanie na `point_type`), a firmware ma profil **interpretować w runtime**, nie kompilować. Profil dostarczany urządzeniu tym samym kanałem co OTA.

**Koszt: duży**, i jest to koszt sprzętowy plus programistyczny: transceiver RS485 (izolowany), obsługa magistrali w firmware, parser profilu, format profilu po stronie backendu, ekran konfiguracji. **suggestion:** ~4–6 tygodni. **Rekomendacja kolejności:** nie zaczynać przed §5.2 — bez OTA każdy błąd w parserze profilu to wyjazd w teren.

### 5.4. Aktywacja w terenie bez laptopa

**Skąd:** Kallipr **Kloud Field** — aplikacja mobilna: skan, konfiguracja, weryfikacja urządzenia w terenie, Bluetooth do bezpośredniej komunikacji przy słabym zasięgu, praca offline z synchronizacją `[P/Ś]`. Kontrapunkt: HWM rejestruje urządzenie **fabrycznie** w DataGate i wiąże z pustym „blank site" `[D/Ś]` — inna droga do tego samego celu.

**Dlaczego u nas:** dziś kod aktywacyjny wchodzi przez **port szeregowy** ([`04_device_provisioning_flow.md §3.2`](../technical/firmware/04_device_provisioning_flow.md)) — czyli monter stoi w hydroforni z laptopem i kablem USB. Przy „kilku prototypach" to niedogodność; przy kilkunastu obiektach to koszt każdego wdrożenia i miara, którą plan biznesowy sam każe mierzyć (§5.2.9 pkt 7: czas uruchomienia jednego punktu).

**Jak, konkretnie — tanio i bez nowego sprzętu:** odwrócić kierunek. Zamiast wpisywać kod **do** urządzenia, operator przypisuje kod **do numeru seryjnego w panelu**, a urządzenie po starcie samo odpytuje backend o swoje przypisanie. Numer seryjny jest deterministyczny (MAC → `WW-<12 hex>`), więc może być nadrukowany na obudowie jako QR. Mechanizm odpytywania częściowo już istnieje — `CLAIM_POLL_INTERVAL_MS` w [`Config.h`](../../firmware/include/Config.h). Wariant z Bluetooth (jak Kallipr) zostawić na później: ESP32-S3 ma BLE, ale to nowa powierzchnia ataku i osobna decyzja.

**Koszt: mały–średni.** **suggestion:** ~1–2 tygodnie po stronie firmware + prosty ekran przypisania w panelu.

### 5.5. Ścieżka integracyjna do istniejącego SCADA

**Skąd:** Inventia **MTDataProvider — OPC UA/DA, ODBC, CSV** `[P/Ś]`; Ovarro — natywne OPC UA i MQTT(S) bez dodatkowego gatewaya `[P/Ś]`; Ayyeka — REST **lub SOAP** plus OPC i DNP3 `[D/Ś]`.

**Dlaczego u nas:** gmina, która ma SCADA, dziś nie ma jak odebrać naszych danych. To bezpośrednio osłabia pozycjonowanie „nie wymieniamy waszej automatyki".

**Jak, konkretnie — nie budujmy OPC UA na MVP.** Najtańsze 80% wartości: **webhooki wychodzące** (zdarzenie „nowy pakiet"/„alarm" → HTTP POST na adres klienta) plus **eksport CSV/API po zakresie czasu**, który już jest częściowo pokryty przez query-side telemetrii. OPC UA to osobna, kosztowna decyzja na później i tylko pod konkretnego klienta.

**Koszt: mały** dla webhooków (**suggestion:** ~3–5 dni), **duży** dla OPC UA (nie rekomendowane teraz).

### 5.6. Publikacja specyfikacji protokołu i API

**Skąd:** Kallipr publikuje **specyfikację MQTT, przewodniki API i noty wydawnicze firmware** w portalu wsparcia `[P/Ś]` — jako jedyny w całej stawce.

**Dlaczego u nas:** mamy dobrze opisany format ([`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md)) — tylko wewnętrznie. Publiczna specyfikacja to najtańszy sygnał dojrzałości technicznej wobec gminy i jej integratora, i wprost adresuje zarzut „zamknięty ekosystem", który stawiamy konkurentom (§5.2.2 planu wobec UniCloud).

**Koszt: bardzo mały.** **suggestion:** ~2–3 dni — publiczny OpenAPI (FastAPI generuje go automatycznie) + opis pakietu telemetrycznego wycięty z istniejącego dokumentu.

### 5.7. Warstwa czasu w bazie: hypertable, agregaty ciągłe, polityka retencji

**Skąd:** wzorzec inżynierski TimescaleDB (rozszerzenie PostgreSQL): hypertable partycjonowane po czasie, **continuous aggregates** jako samoodświeżające się widoki zmaterializowane, **polityki retencji** kasujące całe chunki zamiast wierszy, kompresja kolumnowa dla starych chunków `[T/Ś]`.

**Dlaczego u nas:** wykres roczny na naszej strukturze (JSONB + `MAX_PACKETS_PER_SERIES = 5000`) będzie albo wolny, albo niekompletny. Dane rosną bez żadnej polityki.

**Ważne zastrzeżenie:** Timescale to **rozszerzenie PostgreSQL**, więc migracja nie oznacza zmiany bazy — ale **wymaga hostingu, który to rozszerzenie udostępnia**. Nasz backend stoi dziś na Render ([`Config.h`](../../firmware/include/Config.h): `waterworks-monitoring-platform.onrender.com`). **To trzeba sprawdzić przed decyzją — nie sprawdzone w tej analizie.**

**Wariant awaryjny, gdyby rozszerzenie było niedostępne:** natywne partycjonowanie PostgreSQL po czasie + tabela agregatów godzinowych odświeżana zadaniem + `DROP PARTITION` jako retencja. Daje 80% korzyści bez zależności od hostingu.

**Koszt: średni.** **suggestion:** ~1,5–2 tygodnie. Migracja zgodnie z regułą zero-downtime z briefów (schemat addytywnie → backfill batchami → przełączenie odczytów).

### 5.8. Ochrona klucza prywatnego na urządzeniu

**Skąd:** Blues Notecard — **secure element z certyfikatem ECC P-384 wgranym fabrycznie na etapie produkcji chipu** `[P/Ś]`; ESP32-WROOM-32SE z **ATECC608A**, który generuje i przechowuje klucz ECC **sprzętowo**, do mutual TLS na X.509 `[D/Ś]`.

**Dlaczego u nas:** nasz klucz prywatny to 32 bajty zapisane przez `Preferences` w NVS ([`DeviceIdentity.cpp:205`](../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L205)). Istotny szczegół platformy: **partycja NVS nie jest objęta domyślnym szyfrowaniem flash** — biblioteka NVS nie jest z nim wprost kompatybilna i wymaga osobno włączonego szyfrowania NVS `[D/Ś]`. Praktyczny wniosek: kto ma urządzenie w ręku i czytnik flash, ma klucz.

**Jak, konkretnie — dwa progi:**
1. **Tani:** włączyć szyfrowanie NVS + Secure Boot v2 + flash encryption na ESP32-S3. Bez nowego sprzętu, ale **operacja jednokierunkowa na eFuse** — po przepaleniu nie ma powrotu, więc najpierw na płytce testowej.
2. **Docelowy:** secure element (ATECC608A) przy przejściu na wariant W3 z B-01 — klucz nigdy nie opuszcza układu.

**Koszt:** próg 1 **średni** (**suggestion:** ~1 tydzień + ostrożność przy eFuse), próg 2 związany z decyzją sprzętową z B-01, nie osobny.

**Uczciwie o wadze:** przy modelu read-only skutek kradzieży klucza jest ograniczony — atakujący może **podszyć się pod urządzenie i wstrzykiwać fałszywe pomiary**, ale nie steruje procesem. To realne (fałszywy alarm albo ukrycie prawdziwego), lecz nie katastrofalne. Dlatego pozycja jest niżej niż OTA i Modbus, mimo że brzmi groźniej.

### 5.9. Alarm braku komunikacji ewaluowany w chmurze — zasada, nie funkcja

**Skąd:** Metasphere i Ovarro ewaluują alarmy procesowe **na urządzeniu** `[P/Ś]`; platformy chmurowe ewaluują centralnie.

**Dlaczego u nas — i dlaczego to nie jest banał:** urządzenie offline **nie zgłosi własnego milczenia**. Alarm „utrata komunikacji" (UC-04) musi być z definicji ewaluowany w chmurze, niezależnie od tego, gdzie trafią pozostałe reguły. Mamy już w chmurze status `no_comm` — to jest właściwy fundament i nie należy go przenosić na urządzenie.

**Rekomendacja podziału dla projektowanego modułu alarmów:** MVP ewaluuje **wszystkie** reguły w chmurze (prostsze, zmiana progu nie wymaga dotykania urządzenia, spójne z read-only). Ewaluację na urządzeniu rozważyć dopiero wtedy, gdy pojawi się wymóg reakcji szybszej niż cykl transmisji 60 s — czyli prawdopodobnie nigdy w tym produkcie.

**Koszt:** to decyzja projektowa, nie praca — ale trafia wprost do projektu modułu alarmów, którego jeszcze nie ma.

---

## 6. Czego świadomie nie kopiujemy i dlaczego

| Wzorzec | Skąd | Dlaczego **nie** u nas |
|---|---|---|
| **WITS-DNP3** | Metasphere, HWM (warianty WITS) `[P/Ś]` | Otwarty standard branżowy — ale wypracowany przez brytyjskie przedsiębiorstwa wodociągowe i tam wymagany przetargowo. W Polsce nie jest warunkiem zakupu, a implementacja DNP3 level 2+ z rozszerzeniami to duży, ciężki stos w mikrokontrolerze. Wracamy do tematu, jeśli pojawi się klient, który go wymaga w SIWZ |
| **Sparkplug B** | wzorzec MQTT w przemyśle `[T/Ś]` | Sens ma tam, gdzie **SCADA musi rozumieć dane z wielu różnych źródeł bez integracji per dostawca**. Mamy jeden typ urządzenia i własny backend — dokładamy narzut topic namespace i birth/death certificates bez odbiorcy tej korzyści |
| **LwM2M / CoAP** | rekomendowane dla NB-IoT i urządzeń bateryjnych `[T/Ś]` | Przewaga CoAP/LwM2M nad MQTT wynika z braku trwałego połączenia i mniejszych pakietów — co się liczy przy **baterii i NB-IoT**. Nasz gateway ma zasilanie sieciowe i LTE Cat-1, i wysyła batch co 60 s. Kupujemy złożoność, nie oszczędność |
| **Bateria 5–20 lat + IP68** | Kallipr (Captis S2 „20-Year Battery" `[M/N]`), Metasphere (5+ lat, IP68 4 m/4 dni `[P/Ś]`), AquaRD (do 5 lat `[P/Ś]`), Ayyeka `[D/Ś]` | To odpowiedź na **inny problem**: czujnik w studzience bez zasilania. Nasze obiekty to hydrofornie i przepompownie z szafą i zasilaniem 230 V. Kopiowanie tego oznaczałoby projektowanie pod scenariusz, którego nie obsługujemy. **Co warto wziąć osobno:** klasę szczelności i zakres temperatur — ale przez wybór gotowej obudowy przemysłowej (wariant W3 z B-01), nie przez przeprojektowanie na baterię |
| **Programowalny PLC na urządzeniu (CODESYS)** | Inventia MT-151 `[P/Ś]` | Sprzeczne z dwiema własnymi decyzjami naraz: **read-only na MVP** i „instalator uruchamia obiekt **bez programowania**" (§5.2.7 planu). Program użytkownika na urządzeniu to dokładnie ten koszt inżynierski per wdrożenie, który mamy eliminować |
| **Model hydrauliczny, DMA, ILI, AI** | AIUT WaterPrime `[P/Ś]` | Wymaga gęstego opomiarowania, modelu sieci i audytu — czyli zasobów, których mała gmina z 5–15 obiektami nie ma. To kierunek na później, potwierdzony już w §5.2.4 planu. Powtarzamy tu wyłącznie po to, żeby zamknąć wymiar 8 i 9 |
| **IBM Maximo / EAM** | WaterPrime `[P/Ś]` | Zarządzanie majątkiem to osobny produkt i osobna sprzedaż. Poza zakresem |
| **Własna sieć radiowa / NaaS** | Xylem Sensus FlexNet `[P/Ś]` | Model sensowny przy setkach tysięcy punktów rozliczeniowych. Przy kilku prototypach to nie jest opcja do rozważania — komercyjny LTE-M wystarcza |
| **balenaCloud i kontenery** | balena `[P/Ś]` | balenaOS to dystrybucja Linuksa z silnikiem kontenerów. Gateway na ESP32-S3 nie ma systemu operacyjnego, na którym to działa. Nieprzenośne **architektonicznie**, nie kosztowo |
| **Ekosystem zamknięty na jednym producencie sprzętu** | UniCloud/Unitronics (routery UCR + PLC UniStream), Hawle.live (armatura Hawle) | To jest dokładnie ta słabość konkurencji, na której budujemy pozycjonowanie (§5.2.2, §5.2.4 planu). Skopiowanie mechanizmu — nawet w wersji „nasz sprzęt albo nic" — kasuje naszą jedyną wyraźną przewagę rynkową |

---

## 7. Platformy ogólnego przeznaczenia — kupić czy zbudować

Ta sekcja jest **celowo oddzielona** od tabeli w §3. Golioth, Blues, Balena, Telit i Memfault nie konkurują z nami o gminę — są potencjalnym **komponentem inżynierskim do kupienia zamiast napisania**. Pytanie z briefu brzmi wprost: czy któryś z gotowych mechanizmów (provisioning, OTA, zarządzanie flotą) opłaca się wziąć z półki.

### 7.1. Kandydaci i ich realny stosunek do naszego stosu

| Platforma | Co daje | Cena publiczna | Dopasowanie do ESP32-S3 + A7670E przez AT/TinyGSM |
|---|---|---|---|
| **Blues Wireless** (Notecard + Notehub) | moduł komórkowy **z prepaid transmisją**, secure element z certyfikatem **ECC P-384 wgranym na etapie produkcji chipu**, Notehub: OTA, zarządzanie flotą, zmienne środowiskowe per flota, routing danych do własnej chmury po TLS. Urządzenie **nie ma publicznego adresu IP** i nie stoi w publicznym internecie | **od $49** za Notecard z **10 latami usługi i 500 MB** danych; brak abonamentu i opłat SIM `[P/Ś]` | **Zastępuje nasz modem, nie uzupełnia go.** To decyzja sprzętowa: A7670E + `ModemLink` + `ModemPower` + `TelemetryHttpClient` + `DeviceAuthClient` znikają, zastąpione komunikacją I²C/UART z Notecard. Duża zmiana, ale usuwa najbardziej awaryjną warstwę firmware'u |
| **Golioth** | zarządzanie urządzeniami, OTA, logi, ustawienia; wspiera ESP-IDF/ESP32 | free tier: **1 GB OTA/mies. i 200 MB logów/mies.**, bez opłat za połączenia. Model płatny od 2026-04-01: **$0,25 za unikalne urządzenie na miesiąc**, $0,35/MB OTA ponad limit, $0,20/MB logów `[P/Ś]` | **Problem: transport.** Golioth komunikuje się przez CoAP/DTLS po stosie sieciowym urządzenia. Nasz gateway nie ma stosu IP — ma modem sterowany komendami AT przez TinyGSM. Integracja wymagałaby albo przejścia na tryb PPP/`esp_modem`, albo przepisania warstwy transportu. **To nie jest „dodaj bibliotekę"** |
| **Memfault** | obserwowalność urządzeń (coredumpy, metryki, heartbeaty) + OTA | **brak publicznego cennika per urządzenie**; w AWS Marketplace widoczna oferta kontraktowa rzędu **$100 000/rok** `[T/N]` — pozycjonowanie enterprise | Wartość realna (diagnostyka zdalna to nasza słaba strona), ale przy kilku prototypach nieproporcjonalna. **Odłożyć** |
| **AWS IoT Core** | broker MQTT z X.509, shadow, jobs (OTA), reguły | model per komponent; przykładowo **$0,042 za urządzenie rocznie** za samą łączność `[T/N]` | Tanio i dojrzale, ale wciąga cały ekosystem AWS do backendu, który dziś jest samodzielnym monolitem FastAPI na Render. **Duża zmiana architektoniczna dla jednej funkcji** |
| **balena** | flota urządzeń **linuksowych** w kontenerach | pierwsze **10 urządzeń za darmo**; plany od ~**$159/mies.** (30 urządzeń) `[P/Ś]` | **Nieprzenośne** — wymaga Linuksa. Odrzucone (§1.3) |
| **Telit deviceWISE** | platforma IoT enterprise, FOTA, kampanie aktualizacji | **nieujawniony** (pay-as-you-go bez publicznego cennika) `[P/N]` | Bez publicznej ceny i publicznej dokumentacji integracyjnej nie da się ocenić. **Odrzucone na tym etapie** |

### 7.2. Odpowiedź na pytanie z briefu

**Provisioning: budujemy dalej sami — to już jest gotowe i lepsze niż większość rynku.** Mamy działający, zweryfikowany na sprzęcie mechanizm (klucz na urządzeniu, challenge/response, kody aktywacyjne). Kupowanie tego byłoby regresem. Jedyne, co warto wziąć z półki, to **sprzętowa ochrona klucza** (§5.8) — a to komponent, nie platforma.

**OTA: budujemy sami, ale nie dlatego, że gotowe jest złe — dlatego, że nie pasuje do naszego transportu.** `esp_https_ota` daje partycjonowanie i rollback za darmo w platformie, a warstwę uwierzytelnienia i kanał HTTPS przez modem **już mamy**. Golioth wymagałby zmiany transportu na CoAP/DTLS; AWS IoT — wciągnięcia AWS do backendu. Oba są droższe w integracji niż napisanie OTA, którego zakres jest u nas mały: jeden model urządzenia, jeden obraz, jeden kanał.

**Zarządzanie flotą: budujemy sami, bo przy kilkunastu urządzeniach to jest ekran, a nie platforma.** Inwentarz urządzeń, wersja firmware, ostatni kontakt, przypisanie SIM — to tabela w istniejącym module `core_data` plus widok. Kupowanie platformy do zarządzania flotą kilkunastu urządzeń kosztuje więcej w integracji niż w licencji.

**Jedyny kandydat wart poważnej rozmowy to Blues Notecard — i to nie jako platforma, tylko jako decyzja sprzętowa.** Za $49 z 10-letnią transmisją znika: sterowanie modemem AT, `ModemPower`, obsługa PWRKEY i zworek KAmod, zarządzanie kartami SIM, a klucz prywatny ląduje w secure elemencie zamiast w jawnym NVS. To adresuje **naraz** wymiary 1, 3, 4 i 7 oraz część 11.

Czego to nie rozwiązuje i o czym trzeba pamiętać, zanim ktoś potraktuje to jako skrót: **wchodzimy w zależność od jednego dostawcy w warstwie łączności**, tracimy kontrolę nad tym, którą siecią i jakim APN idą dane (istotne przy rozmowie o NIS2 i przy prywatnym APN, którym operuje np. NASUS), a interfejsy pomiarowe (§5.3) trzeba zbudować niezależnie — Notecard ich nie dotyka.

**Rekomendacja:** nie podejmować tej decyzji w tym dokumencie. Wpisać ją jako **jawny wariant sprzętowy do porównania w B-01 obok W1/W2/W3** — bo to jest decyzja o wariancie gatewaya, a nie o bibliotece, i powinna być rozstrzygana razem z pytaniem o obudowę, CE i zasilanie.

---

## 8. Konkretne zmiany do rozważenia w naszej architekturze

Lista uszeregowana. Kolumna „blokuje" pokazuje zależności — kolejność nie jest dowolna.

### 8.1. Firmware

| # | Zmiana | Pliki | Wymiar | Blokuje / zależy |
|---|---|---|---|---|
| F1 | Bufor okien na LittleFS zamiast RAM; retencja liczona w godzinach, nie minutach | [`TelemetrySender/`](../../firmware/lib/TelemetrySender/), [`TelemetryPayload/`](../../firmware/lib/TelemetryPayload/), `RETAIN_WINDOWS_MAX` | 5 | warunek wstępny dla F2 (dane muszą przeżyć restart po OTA) |
| F2 | OTA przez `esp_https_ota` na tokenie Bearer, dwie partycje aplikacji, `esp_ota_mark_app_valid_cancel_rollback()` | nowa biblioteka `lib/FirmwareUpdater/`, [`platformio.ini`](../../firmware/platformio.ini) (tablica partycji), [`Config.h`](../../firmware/include/Config.h) | 7, 11 | zależy od F1; blokuje F4 i bezpieczne wdrożenie F3 |
| F3 | Modbus RTU master na RS485 + interpretacja profilu urządzenia w runtime | nowa `lib/ModbusMaster/`, [`lib/Sensor/`](../../firmware/lib/Sensor/) (`ISensor` jako punkt wpięcia), [`Config.h`](../../firmware/include/Config.h) (piny UART2) | 2, 6 | zależy od F2 i od B3; wymaga sprzętu (transceiver) |
| F4 | Aktywacja bez laptopa: urządzenie odpytuje backend o przypisanie do numeru seryjnego zamiast czekać na `ACTIVATE` po serialu | [`lib/EnrollmentClient/`](../../firmware/lib/EnrollmentClient/), `CLAIM_POLL_INTERVAL_MS` w [`Config.h`](../../firmware/include/Config.h) | 4 | zależy od B4; ścieżkę serial zostawić jako awaryjną |
| F5 | Kanał ciśnienia od zera: `PressureSensor : ISensor` + odczyt 4-20 mA przez ADS1015 + rejestracja w `initializeSensors()` | nowy `lib/Sensor/src/PressureSensor.{h,cpp}`, [`main.cpp:94-97`](../../firmware/src/main.cpp#L94-L97), [`Config.h`](../../firmware/include/Config.h) (pin ADC + wartość rezystora) | 2 | niezależne od F1–F4; **domyka zakres MVP**. Wymaga rozstrzygnięcia rezystora — §9.5 |
| F6 | Szyfrowanie NVS + Secure Boot v2 + flash encryption; docelowo secure element | [`lib/DeviceIdentity/`](../../firmware/lib/DeviceIdentity/), konfiguracja partycji | 4, 11 | operacja **jednokierunkowa na eFuse** — najpierw płytka testowa |

**Uwaga do F5 — dlaczego jest wyżej, niż sugerowałby jej rozmiar.** MVP zdefiniowane w [§2.2.1 planu](../business/01_plan_biznesowy.md) to **temperatura i ciśnienie**. Kanał ciśnienia nie istnieje w firmware w żadnej postaci: nie ma klasy czujnika, nie ma odczytu ADC, `initializeSensors()` rejestruje wyłącznie `PT100Sensor`. Nie chodzi więc o dokończenie sterownika, tylko o to, że **połowa zakresu MVP nie jest napisana** — a interfejs `ISensor` i wielokanałowy format pakietu są gotowe i czekają, więc pozycja jest tania w stosunku do tego, co domyka.

**Dobra wiadomość przy okazji:** wbrew temu, co twierdzi dokumentacja (§9.7), system **nie wysyła dziś syntetycznych danych ciśnienia** — nie wysyła ich wcale. Nie ma więc ryzyka, że zmyślony pomiar trafi na ekran gminy z etykietą `quality: "good"`. Gdyby jednak kanał był wdrażany etapami, ta zasada musi zostać utrzymana: wartość niepochodząca z czujnika nigdy nie może opuścić urządzenia z jakością `good` — do tego służą kody błędów z [`sensor_registry.yaml`](../../sensor_registry.yaml).

### 8.2. Sprzęt

| # | Zmiana | Wymiar | Uwagi |
|---|---|---|---|
| H1 | Obudowa przemysłowa (DIN lub IP) + ochrona przepięciowa na zasilaniu i na pętli 4-20 mA | 1 | wchodzi wprost do porównania wariantów W1/W2/W3 w **B-01** |
| H2 | Izolowany transceiver RS485 | 2 | warunek sprzętowy F3 |
| H3 | Rozważenie Blues Notecard jako **czwartego wariantu (W4)** gatewaya | 1, 3, 4, 7, 11 | zob. §7.2 — decyzja należy do B-01, nie do tego dokumentu |
| H4 | Weryfikacja fizyczna zworek J2 i J_APWK na module KAmod | 1 | znany otwarty punkt z [`01_hardware.md §7`](../technical/firmware/01_hardware.md); nie wynika z tej analizy, ale blokuje powtarzalność montażu |

### 8.3. Backend

| # | Zmiana | Pliki | Wymiar | Uwagi |
|---|---|---|---|---|
| B1 | Warstwa czasu: hypertable/partycjonowanie + agregaty godzinowe + polityka retencji | [`modules/telemetry/repositories/queries.py`](../../backend/app/modules/telemetry/repositories/queries.py), nowa migracja Alembic | 8 | **najpierw sprawdzić dostępność rozszerzenia TimescaleDB na Render**; wariant awaryjny w §5.7. Migracja zero-downtime |
| B2 | Endpoint manifestu firmware + kanały wydawnicze + rejestr wersji na urządzenie | nowy moduł lub rozszerzenie [`modules/device_identity/`](../../backend/app/modules/device_identity/) | 7 | para dla F2; wersja firmware to nowe pole na `Device` |
| B3 | `device_profiles` w [`sensor_registry.yaml`](../../sensor_registry.yaml) + walidacja + dystrybucja profilu do urządzenia | [`sensor_registry.yaml`](../../sensor_registry.yaml), [`modules/telemetry/schemas/`](../../backend/app/modules/telemetry/schemas/), [`firmware/scripts/prebuild.py`](../../firmware/scripts/prebuild.py) | 6 | **zmienia charakter pliku**: dziś jest to katalog stałych współdzielonych w czasie kompilacji, po zmianie część treści staje się konfiguracją dystrybuowaną w runtime. To zasługuje na ADR |
| B4 | Przypisanie kodu aktywacyjnego do numeru seryjnego + endpoint odpytywania przez urządzenie | [`modules/device_identity/services/activation_codes.py`](../../backend/app/modules/device_identity/services/activation_codes.py) | 4 | para dla F4 |
| B5 | Moduł alarmów: reguły per punkt pomiarowy, ewaluacja **w chmurze**, cykl życia zdarzenia | nowy `modules/alarms/` wg szablonu z [`01_backend-architecture.md §5`](../technical/backend/01_backend-architecture.md) | 9 | projekt ekranu i cyklu życia alarmu powstaje w **B-03**; ten dokument dostarcza wyłącznie decyzję „gdzie ewaluować" (§5.9) |
| B6 | Webhooki wychodzące + eksport po zakresie czasu | [`modules/telemetry/api/`](../../backend/app/modules/telemetry/api/) | 10 | tanie 80% wartości integracji ze SCADA; OPC UA **nie teraz** |
| B7 | Publiczna specyfikacja: OpenAPI + opis pakietu telemetrycznego | [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md) jako źródło | 3, 10 | najtańsza pozycja na całej liście |

### 8.4. Sugerowana kolejność

```
F5  →  F1  →  F2 + B2  →  F4 + B4  →  B1  →  B7 + B6  →  B3 + F3 + H2  →  B5  →  F6  →  H1/H3 (z B-01)
```

Uzasadnienie kolejności: **F5** domyka zadeklarowany zakres MVP (dziś działa połowa: temperatura bez ciśnienia) i jest tanie, bo infrastruktura wielokanałowa już istnieje. **F1→F2** daje zdalną naprawialność, bez której każda kolejna zmiana w firmware kosztuje wyjazd. **B1** zatrzymuje dług rosnący z każdym dniem działania pilotażu. **B3+F3** to największa pozycja i wymaga, żeby wszystko powyżej już działało. **B5** (alarmy) świadomie po infrastrukturze, ale przed nią, jeśli pilotaż wymaga alarmów wcześniej — to decyzja produktowa, nie techniczna.

---

## 9. Korekty do istniejących analiz

Rzeczy znalezione przy okazji tego badania, które **korygują** istniejące dokumenty. Zgodnie z briefem: nie przepisujemy tych analiz, tylko wskazujemy rozbieżność.

### 9.1. `CONTEXT.md` — deklarowana retencja bufora jest 360× większa od faktycznej

[`CONTEXT.md`](../business/CONTEXT.md) definiuje **Bufor lokalny** jako „pamięć gateway'a (**flash, SD card**) […] **Minimalna retencja: 72 godziny**".

Stan faktyczny: bufor jest **wyłącznie w RAM**, `RETAIN_WINDOWS_MAX = 12 × WINDOWS_PER_BATCH` ≈ **12 minut**, kasowany przy każdym restarcie ([`04_telemetry_module.md §5`](../technical/backend/04_telemetry_module.md)).

To nie jest kosmetyczna rozbieżność: 72 h to deklaracja, którą można powtórzyć klientowi, a 12 min to zupełnie inna obietnica dostępności danych. **Do rozstrzygnięcia: albo implementujemy F1, albo poprawiamy `CONTEXT.md`.** Rekomendacja: implementować — 72 h na flashu jest osiągalne i tanie (§5.1).

### 9.2. `CONTEXT.md` i ADR-0002 — „profil urządzenia" i „neutralność sprzętowa" nie mają dziś implementacji

[`CONTEXT.md`](../business/CONTEXT.md) definiuje **Profil urządzenia** jako konfigurację z mapowaniem rejestrów, używaną „bez zmian firmware'u", oraz **Neutralność sprzętową**: „Obsługujemy najpopularniejsze interfejsy (Modbus RTU, 4-20 mA); nowe protokoły dodajemy przez profile, nie recompile".

Stan faktyczny: Modbus RTU **nie jest obsługiwany w ogóle**, 4-20 mA **nie jest zaimplementowane**, a dodanie czujnika to nowa klasa C++ i rekompilacja. Mechanizm profili nie istnieje — [`sensor_registry.yaml`](../../sensor_registry.yaml) to katalog typów i kodów błędów, nie profil urządzenia.

To jest najpoważniejsza luka obietnica–stan w całej analizie i uzasadnia pozycje B3/F3. **Do czasu ich wykonania obietnica neutralności sprzętowej nie powinna pojawiać się w materiałach dla klienta** jako stan obecny.

### 9.3. `01_plan_biznesowy.md §5.2.8` — zagrożenie nr 7 jest już zmaterializowane

Plan wymienia jako zagrożenie: „Tani gateway bez procesu aktualizacji, dokumentacji i zarządzania podatnościami może nie przejść oceny klienta".

To nie jest ryzyko przyszłe — **brak OTA jest stanem obecnym** (§2, potwierdzone brakiem `esp_ota`/`Update.h`/`httpUpdate`/`ArduinoOTA` w całym `firmware/`). Sugerowana zmiana kwalifikacji w planie: z „zagrożenie" na „znana luka z planem naprawy (F2/B2)".

### 9.4. `01_plan_biznesowy.md §5.2.2` — zarzut wobec UniCloud wymaga doprecyzowania

Plan wymienia wśród obszarów do weryfikacji u UniCloud „eksport danych i integracja z systemami zewnętrznymi". Badanie techniczne pokazuje, że **UniStream wystawia REST API po TLS, MQTT, OPC UA, SQL client i SNMP** `[P/Ś]`, a MQTT używa **uwierzytelniania X.509** `[P/Ś]`.

Zarzut o zamknięciu ekosystemu pozostaje trafny — ale dotyczy **zależności od sprzętu Unitronics**, nie ubóstwa interfejsów integracyjnych. W obecnym brzmieniu sugeruje to drugie i **byłby to zarzut łatwy do obalenia w rozmowie z klientem**, który UniCloud zna. Rekomendacja: przeformułować precyzyjnie.

### 9.5. Rezystor pętli 4-20 mA — brief B-05 opisuje rozbieżność, której w kodzie nie ma

Sprawdzone przy okazji pozycji F5 (skalowanie odczytu ADC zależy wprost od wartości rezystora pomiarowego):

| Miejsce | Wartość |
|---|---|
| [`01_hardware.md §3`](../technical/firmware/01_hardware.md) | **250 Ω** |
| [`01_hardware.md §6`](../technical/firmware/01_hardware.md) | **250 Ω** |
| [`Config.h`](../../firmware/include/Config.h) | **brak jakiejkolwiek wartości rezystora** — tor 4-20 mA nie jest zaimplementowany |
| jedyna stała rezystancji w firmware | `REF_RESISTOR_OHMS = 430.0f` w [`PT100Sensor.h:22`](../../firmware/lib/Sensor/src/PT100Sensor.h#L22) — rezystor **referencyjny MAX31865 dla PT100**, niezwiązany z pętlą prądową |

Brief B-05 zakłada, że `Config.h` i §3 mówią o **136 Ω** (2× 68 Ω), a §6 o 250 Ω. **Kod tego nie potwierdza:** oba paragrafy `01_hardware.md` podają zgodnie 250 Ω, a `Config.h` nie zawiera tej stałej w ogóle. Wygląda to na rozbieżność między briefem a stanem repozytorium, nie między dwoma paragrafami dokumentu.

Rozstrzygnięcie należy do **B-05** (ma to w zakresie) i wymaga sprawdzenia, co jest fizycznie wlutowane — czego ta analiza nie robi. Znaczenie dla nas: dopóki wartość nie jest ustalona i zapisana w `Config.h`, pozycja F5 nie może być poprawnie zaimplementowana, bo nie ma czym przeliczyć prądu na ciśnienie.

### 9.6. Brief B-04 — prebuild hook nie jest wyłączony

Brief B-04 ([`01_briefy_dla_agentow.md`](../plan/01_briefy_dla_agentow.md), hipoteza 6) zakłada, że „prebuild hook, który miał tego pilnować, jest wyłączony ([`platformio.ini`](../../firmware/platformio.ini))".

Stan faktyczny na 2026-09-01: hook jest **aktywny** — [`platformio.ini`](../../firmware/platformio.ini) zawiera odkomentowane `extra_scripts = scripts/prebuild.py`, a [`firmware/scripts/prebuild.py`](../../firmware/scripts/prebuild.py) generuje `SensorRegistry.h` z YAML-a i weryfikuje synchronizację z backendem. Do uwzględnienia przy realizacji B-04, żeby nie opisał nieistniejącego problemu.

### 9.7. `01_hardware.md` — opisuje kod ciśnienia, którego nie ma

Najpoważniejsza rozbieżność dokumentacja–kod znaleziona w tym badaniu. [`01_hardware.md`](../technical/firmware/01_hardware.md) mówi w dwóch miejscach:

> §1: „`TelemetryPayload` od wersji 2026-08-24 odczytuje PT100 przez MAX31865 (SPI). **PT-506 wciąż generuje wartości syntetyczne (funkcja sinus).**"
>
> §5: „**PT-506 — draft.** Brak biblioteki odczytu ADC; **telemetria PT-506 wciąż wysyła dane syntetyczne (sinus)**."

Stan faktyczny: **w firmware nie ma żadnego kodu ciśnienia — ani prawdziwego, ani syntetycznego.**

| Sprawdzenie | Wynik |
|---|---|
| `grep -rin "pressure" firmware/` (bez bibliotek zewnętrznych) | **0 trafień** |
| `grep -rn "sin(" firmware/lib` | **0 trafień** |
| zawartość `firmware/lib/Sensor/src/` | wyłącznie `PT100Sensor.h`, `PT100Sensor.cpp` |
| [`main.cpp:94-97`](../../firmware/src/main.cpp#L94-L97) `initializeSensors()` | rejestruje wyłącznie `new PT100Sensor(PT100_SPI_CS)` |

Dodatkowo brief B-05 zakłada, że §1 „wskazuje istniejący [`PressureSensor.cpp`](../../firmware/lib/Sensor/src/)" — **ten plik nie istnieje.**

Dlaczego to jest istotne, a nie tylko nieaktualne: rozbieżność idzie w **obie strony i obie są mylące**. Dokumentacja jednocześnie **zaniża** wiarygodność systemu (sugeruje, że wysyłamy zmyślone dane, czego nie robimy — to zły sygnał przy ocenie technicznej przez klienta) i **zawyża** stan zaawansowania (sugeruje istniejący, choć „draftowy", tor ciśnienia, podczas gdy jest to praca do napisania od zera — pozycja F5).

Naprawa należy do **B-05**, który ma uzgodnienie dokumentacji ze stanem kodu w zakresie. Ta analiza dostarcza dowód.

---

## 10. Źródła

Wszystkie linki dostępne publicznie, stan na **2026-09-01**. Zgodnie z §0.1 treść odczytana przez wyszukiwarkę, nie bezpośrednio — **przed użyciem konkretnej liczby otwórz link i potwierdź**.

### Polska

**Inventia**
- [MT-151 LED — sterownik telemetryczny GSM/GPRS serii MOBICON](https://www.inventia.pl/mt-151-led-sterownik-telemetryczny-gsmgprs-serii-mobicon/) `[P]`
- [MT-151 LED programowany w środowisku CODESYS](https://www.inventia.pl/mt-151-led-sterownik-telemetryczny-programowany-w-srodowisku-codesys/) `[P]`
- [Tabela porównawcza modułów (PDF)](https://www.inventia.pl/wp-content/uploads/2019/03/Tabela-porownawcza-modulow-2019.pdf) `[D]`
- [MT-331 — moduł telemetryczny](https://inventia.online/mt-331-telemetry-module-2/) `[P]`
- [Protokół MQTT w modułach MT-331](https://inventia.online/news/mqtt-protocol-in-mt-331-telemetry-modules/) `[P]`
- [DataPortal — autorski system SCADA (ulotka PDF)](https://www.inventia.pl/wp-content/uploads/2021/10/Ulotka-DataPortal.pdf) `[M]`
- [Inventia — rozwiązania WOD-KAN](https://www.inventia.pl/wod-kan/) `[P]`

**AquaRD**
- [CellBOX H4](https://aquard.pl/cellbox-h4/) `[P]`
- [Karta katalogowa CellBOX H4 (PDF)](https://aquard.pl/wp-content/uploads/2025/05/Karta-katalogowa-CellBOX-H4.pdf) `[D]`
- [Karta katalogowa CellBOX-H3 (PDF)](https://ftp.aquard.pl/strefaklienta/Dokumentacja%20techniczna,%20katalogi,%20certyfikaty/_CellBOX-H3/Karta%20katalogowa%20CellBOX-H3.pdf) `[D]`
- [Instrukcja konfiguratora CellBOX-UxR RTU / Modbus (PDF)](https://ftp.aquard.pl/strefaklienta/Dokumentacja%20techniczna,%20katalogi,%20certyfikaty/archiwum%20CellBOX-UxR/Instrukcja%20u%C5%BCytkowania%20konfiguratora%20CellBOX-UxR%20RTU.pdf) `[D]`
- [CellBOX — urządzenia (przegląd rodziny)](https://aquard.pl/urzadzenia/) `[P]`

**UniCloud / Unitronics**
- [UniCloud — platforma IIoT](https://unitronics.cloud/product/) `[P]`
- [UniStream — sterowniki programowalne](https://www.unitronicsplc.com/programmable-controllers-unistream-series/) `[P]`
- [UniStream MQTT](http://scadainthecloud.com/Unitronics-UniStream-MQTT.php) `[T]`
- [UniStream REST API](http://scadainthecloud.com/Unitronics-UniStream-REST.php) `[T]`
- [UniStream OPC UA](http://scadainthecloud.com/Unitronics-UniStream-OPC-UA.php) `[T]`

**Hawle**
- [Hawle.live — monitoring sieci wodociągowej](https://www.hawle.com/en/service/services/hawle-live) `[P]`
- [Hawle.live CAP — inteligentny hydrant](https://www.hawle.com/pl/hawle-knowledge/systemy-i-rozwiazania/hawle-live-cap-inteligentny-hydrant) `[P]`

**AIUT WaterPrime**
- [WaterPrime — strona główna](https://waterprime.eu/en/home/) `[P]`
- [AIUT — WaterPrime ogranicza straty wody](https://aiut.com/en/aiut-waterprime-reduces-water-losses-in-water-supply-networks-effectively/) `[P]`

### Świat

**Kallipr**
- [Captis Series 1 — IP68 IoT data logger](https://kallipr.com/product/captis-series-1/) `[P]`
- [Captis S2 — 20-Year Battery](https://kallipr.com/product/captis-s2-range/) `[P/M]`
- [Kallipr Kloud Fleet — zarządzanie flotą](https://kallipr.com/product/kallipr-kloud-fleet/) `[P]`
- [Kallipr Support — specyfikacje MQTT, przewodniki API, noty wydawnicze firmware](https://kallipr.com/support/) `[P]`
- [Kallipr Kloud Field (Google Play)](https://play.google.com/store/apps/details?id=com.kalliprkloud.field) `[P]`

**Ayyeka**
- [Wavelet V2 EX — karta katalogowa (PDF)](https://www.ayyeka.com/hubfs/Marketing%20Materials%20-%20Marketing%20Manager/Wavelet%20Page/Ayyeka%20Wavelet%20V2%20EX%20-%20Datasheet%20-%202025.pdf) `[D]`
- [Wavelet V2 — karta katalogowa (PDF)](https://www.ayyeka.com/hubfs/Dropbox%20-%20Not%20Needed/Wavelet%20Datasheets/Datasheet%20-%20%20Wavelet%20V2%20-%20May%202021.pdf) `[D]`
- [Wavelet Series — przegląd urządzeń IIoT (PDF)](https://www.geotechenv.com/pdf/telemetry/ayyeka_IoT_devices.pdf) `[D]`

**Metasphere**
- [Point Orange IoT RTU](https://metasphere.co.uk/products/point-orange/) `[P]`
- [Point Orange 3G RTU](https://metasphere.co.uk/products/point-orange-3g/) `[P]`
- [Point Orange — bateryjny RTU (opis techniczny u dystrybutora)](https://www.environmental-expert.com/products/metasphere-3g-rtu-point-orange-iot-system-718343) `[T]`

**HWM Global**
- [Multilog 2 — instrukcja użytkownika (PDF)](https://www.hwmglobal.com/uploads/manuals/Multilog%202/MAN-147-0018-A%20User%20Manual%20-%20Multilog2.pdf) `[D]`
- [Multilog 2 — suplement dla modeli z WITS (PDF)](https://www.hwmglobal.com/uploads/manuals/Multilog%202/MAN-147-0017-A%20User%20Guide%20Multilog2%20(Supplement%20for%20models%20supporting%20WITS%20protocol).pdf) `[D]`
- [DataGate v2 — wprowadzenie dla użytkowników i administratorów (PDF)](https://www.hwmglobal.com/uploads/manuals/DataGate2/MAN-130-0015-A%20DataGate2%20Introduction%20for%20Users%20and%20Administrators.pdf) `[D]`
- [Multilog 2 — karta katalogowa (PDF)](https://www.fluidconservation.com/wp-content/uploads/2023/01/Multilog-2-Datasheet.pdf) `[D]`

**Ovarro**
- [TBox RTU — przegląd](https://ovarro.com/en/global/solutions/monitoring--control-devices/remote-telemetry-units-rtus-from-ovarro/2/tbox/2/) `[P]`
- [TBox MS — karta katalogowa (PDF)](https://ovarro.com/content-media/assigned/32372/Ovarro_TBox_MS.pdf) `[D]`
- [TBox LT2 — broszura (PDF)](https://www.cimpro.com/hubfs/Ovarro/Data%20sheets/Ovarro-TBox-LT2-Web-Brochure%20V1.2%20-%20Co-brandable.pdf) `[D]`

**Xylem / Sensus**
- [Sensus Smart Water](https://www.xylem.com/en-us/brand/sensus/smart-utility-networks/smart-water/) `[P]`
- [Jak FlexNet zmienia sieci AMI](https://www.xylem.com/en-us/brands/sensus/blog/how-sensus-flexnet-is-redefining-ami-networks/) `[P/M]`

### Standardy i wzorce inżynierskie

- [WITS Protocol PSA — czym jest WITS](https://www.witsprotocol.org/what-is-wits/) `[P]`
- [Rozwój standardu WITS-DNP3](https://www.witsprotocol.org/development-wits-dnp3-protocol-standard/) `[P]`
- [MQTT vs Sparkplug B — kiedy które](https://flowfuse.com/blog/2026/06/mqtt-vs-sparkplug-b/) `[T]`
- [NB-IoT: dlaczego CoAP i LwM2M wypadają lepiej niż MQTT — na przykładzie smart water metering](https://avsystem.com/blog/iot/protocol-choices-coap-lwm2m-outshine-mqtt) `[T]`
- [ESP-IDF — Flash Encryption (ograniczenie partycji NVS)](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/flash-encryption.html) `[D]`
- [ESP-IDF — Secure Boot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/secure-boot-v1.html) `[D]`
- [ESP-IDF — secure element (ATECC608A)](https://github.com/espressif/esp-idf/blob/v4.4.5/docs/en/api-reference/peripherals/secure_element.rst) `[D]`
- [TimescaleDB — continuous aggregates](https://www.tigerdata.com/learn/continuous-aggregates-timescaledb) `[D]`
- [TimescaleDB — polityki retencji](https://docs.tigerdata.com/use-timescale/latest/data-retention/about-data-retention/) `[D]`

### Platformy ogólnego przeznaczenia

- [Blues Notecard Cellular](https://blues.com/products/notecard/notecard-cellular/) `[P]`
- [Blues — najprostszy sposób dodania łączności komórkowej do ESP32](https://dev.blues.io/blog/easiest-way-to-add-cellular-to-an-esp32-iot-project/) `[P]`
- [Blues Store — cennik Notecard](https://shop.blues.com/collections/notecard) `[P]`
- [Golioth — cennik](https://golioth.io/pricing) `[P]`
- [Golioth — uproszczony cennik (blog, stawki od 2026-04-01)](https://blog.golioth.io/new-simplified-pricing/) `[P]`
- [Golioth — OTA na ESP32 z ESP-IDF](https://blog.golioth.io/how-to-do-esp32-ota-updates-using-golioth-and-esp-idf/) `[P]`
- [Memfault — platforma obserwowalności](https://memfault.com/product/) `[P]`
- [AWS IoT Core — cennik](https://aws.amazon.com/iot-core/pricing/) `[P]`
- [balena — cennik](https://www.balena.io/pricing) `[P]`
- [Telit deviceWISE CLOUD](https://www.telit.com/iot-platforms-overview/telit-devicewise-cloud/) `[P]`

---

## 11. Otwarte pytania

Rzeczy, których ta analiza **nie rozstrzygnęła** i które wymagają albo dostępu do źródeł (§0.1), albo decyzji spoza jej zakresu:

1. **Czy hosting na Render udostępnia rozszerzenie TimescaleDB?** Blokuje wybór wariantu w B1 (§5.7). Sprawdzenie: kilkanaście minut, nie zrobione w tej sesji.
2. **Jaki jest realny format i protokół transmisji AquaRD CellBOX i Hawle.live BOX do systemu nadrzędnego?** Obie pozycje mają „nieujawnione" w wymiarze 3. Karty katalogowe mogą to zawierać — patrz linki w §10.
3. **Czy Inventia i Ovarro publikują politykę ujawniania podatności?** Istotne dla porównania w wymiarze 11 i dla własnej odpowiedzi na pytania NIS2 od gminy.
4. **Czy Blues Notecard jest wariantem sprzętowym do porównania w B-01?** Decyzja produktowa, świadomie nieprzesądzona tutaj (§7.2).
5. **Ile faktycznie waży obraz firmware po zbudowaniu** i ile potrwa jego pobranie przez A7670E — wejście do projektu F2. Do zmierzenia, nie do oszacowania.
