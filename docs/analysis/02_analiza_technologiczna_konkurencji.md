# Analiza technologiczna i sprzętowa konkurencji — cały system

> **Zlecenie:** B-02 z [`01_briefy_dla_agentow.md`](../plan/01_briefy_dla_agentow.md).
> **Zakres:** warstwa techniczna — firmware, sprzęt, protokoły, backend, chmura. Warstwa UX/UI to osobne zlecenie (B-03) i nie jest tu poruszana.
> **Data researchu:** 4 września 2026. Wszystkie źródła sprawdzone tego dnia.
> **Uzupełnia, nie zastępuje:** [`01_plan_biznesowy.md` §5.2](../business/01_plan_biznesowy.md) — analiza biznesowa konkurencji (pozycjonowanie, ceny, mocne i słabe strony) już istnieje i nie jest tu powtarzana.

---

## Spis treści

1. [Jak czytać ten dokument](#1-jak-czytać-ten-dokument)
2. [Punkt odniesienia — nasz system w 11 wymiarach](#2-punkt-odniesienia--nasz-system-w-11-wymiarach)
3. [Kogo zbadano, kogo odrzucono i dlaczego](#3-kogo-zbadano-kogo-odrzucono-i-dlaczego)
4. [Tabela porównawcza — podmiot × 11 wymiarów](#4-tabela-porównawcza--podmiot--11-wymiarów)
5. [Analiza wymiar po wymiarze](#5-analiza-wymiar-po-wymiarze)
6. [Karty podmiotów — fakty źródłowe](#6-karty-podmiotów--fakty-źródłowe)
7. [Platformy device management ogólnego przeznaczenia — kupić czy budować](#7-platformy-device-management-ogólnego-przeznaczenia--kupić-czy-budować)
8. [Co warto skopiować](#8-co-warto-skopiować)
9. [Czego świadomie nie kopiujemy i dlaczego](#9-czego-świadomie-nie-kopiujemy-i-dlaczego)
10. [Lista konkretnych zmian do rozważenia w naszej architekturze](#10-lista-konkretnych-zmian-do-rozważenia-w-naszej-architekturze)
11. [Korekty do istniejących analiz](#11-korekty-do-istniejących-analiz)
12. [Luki informacyjne — czego nie udało się ustalić](#12-luki-informacyjne--czego-nie-udało-się-ustalić)
13. [Źródła](#13-źródła)

---

## 1. Jak czytać ten dokument

### 1.1. Etykiety wiarygodności

Każde ustalenie o konkurencie ma etykietę typu źródła. Kolejność wiarygodności zgodna z metodą briefu:

| Etykieta | Znaczenie |
|---|---|
| **[dok]** | Dokumentacja techniczna, karta katalogowa, instrukcja, dokumentacja developerska producenta |
| **[spec]** | Publiczna specyfikacja standardu (np. WITS PSA, Cumulocity) |
| **[mkt]** | Materiał marketingowy producenta — strona produktu, folder, wpis blogowy. Najsłabsze źródło; deklaracje niesprawdzalne |
| **[3rd]** | Źródło trzecie — dystrybutor, katalog branżowy, prasa, Wikipedia |
| **[repo]** | Nasz własny kod lub dokumentacja w tym repozytorium — weryfikowalne bezpośrednio |
| **nieujawnione** | Informacji nie ma publicznie. Nie zgadujemy |
| **szacunek własny** | Ocena autora analizy, nie fakt ze źródła |

**Poziom pewności wynika wprost z etykiety** — nie dublujemy go osobną skalą:

| Etykieta | Poziom pewności | Jak czytać |
|---|---|---|
| **[repo]** | pewne | Weryfikowalne w tym repozytorium jednym `grep` |
| **[dok]**, **[spec]** | wysoki | Parametr z karty katalogowej lub specyfikacji standardu; producent odpowiada za niego formalnie |
| **[3rd]** | średni | Źródło niezależne, ale wtórne — mogło stracić aktualność albo uprościć |
| **[mkt]** | niski | Deklaracja producenta bez weryfikacji. Traktujemy jako *deklarację*, nie jako zmierzony parametr |
| **nieujawnione** | brak danych | Nie zgadujemy i nie wnioskujemy z analogii |
| **szacunek własny** | ocena autora | Do zakwestionowania przy przeglądzie |

**Zasada:** brak etykiety **[dok]/[spec]/[repo]** przy twierdzeniu o zdolności technicznej oznacza, że twierdzenie pochodzi od producenta i nie zostało niezależnie potwierdzone. Deklaracje w rodzaju „wdrożenie w 30 minut" albo „bateria 20 lat" są **[mkt]** i nie należy budować na nich porównań ilościowych.

### 1.2. Skala pozycji

Dla każdego z 11 wymiarów podajemy, gdzie stoimy względem rynku:

- 🔴 **z tyłu** — brakuje nam czegoś, co rynek traktuje jako standard i co ma konsekwencje operacyjne;
- 🟡 **na poziomie** — mamy odpowiednik, choć często węższy albo w innej formie;
- 🟢 **z przodu** — nasze rozwiązanie jest lepsze albo bardziej nowoczesne od typowego na rynku.

Ocena dotyczy **stanu dzisiejszego kodu**, nie planów.

### 1.3. Uwaga o asymetrii dostępnych źródeł

Podmioty europejskie i australijskie (Kallipr, Ayyeka, Metasphere, HWM) publikują karty katalogowe z pełnymi parametrami elektrycznymi i część dokumentacji integracyjnej. Podmioty polskie publikują mniej: dokumentacja Inventia DataPortal jest za loginem, AquaRD trzyma DTR-y na FTP dla klientów, Hawle nie podaje interfejsów elektrycznych swojego urządzenia w ogóle. Oznacza to, że **puste pola w tabelach dla polskich dostawców częściej znaczą „nie publikują" niż „nie mają"**. Nie należy tego czytać jako przewagi konkurencyjnej po naszej stronie.

---

## 2. Punkt odniesienia — nasz system w 11 wymiarach

Wszystko poniżej zweryfikowane w kodzie i dokumentacji tego repozytorium (4 września 2026). To jest baza, względem której porównujemy rynek.

| # | Wymiar | Stan naszego systemu | Dowód |
|---|---|---|---|
| 1 | Architektura sprzętowa gatewaya | Zestaw deweloperski ESP32-S3-DevKitC-1 + HAT KAmod z A7670E (LTE Cat 1). Bez obudowy, bez stopnia IP, bez ochrony przepięciowej. Zasilanie zewnętrzne 5 V / min. 2 A, wspólna masa z ESP32. Montaż własny, przewody | [`01_hardware.md`](../technical/firmware/01_hardware.md) |
| 2 | Interfejsy pomiarowe | SPI → MAX31865 → PT100 (zweryfikowane). Pętla 4-20 mA dla PT-506 — **draft, dane syntetyczne (sinus)**. Brak Modbus, brak RS485, brak wejść cyfrowych/impulsowych, brak 0-10 V | [`01_hardware.md` §5](../technical/firmware/01_hardware.md), [`TelemetryPayload.cpp`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp) |
| 3 | Protokół urządzenie ↔ chmura | HTTPS POST na `/telemetry/ingest`, port 443, JSON „v2" własnego formatu. TLS realizowany w modemie (`TINY_GSM_MODEM_A76XXSSL`). Brak MQTT. Specyfikacja nieopublikowana — istnieje tylko w naszej dokumentacji wewnętrznej | [`Config.h`](../../firmware/include/Config.h), [`platformio.ini`](../../firmware/platformio.ini), [`04_telemetry_module.md` §5](../technical/backend/04_telemetry_module.md) |
| 4 | Tożsamość i provisioning | Para kluczy EC P-256 generowana **na urządzeniu**, challenge/response z podpisem, token JWT 36 h. Kod aktywacyjny jednorazowy (TTL 900 s, ~50 bitów entropii) wpisywany po porcie szeregowym: `ACTIVATE <kod>`. Pierwsze uruchomienie w terenie **wymaga laptopa** | [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md) |
| 5 | Format telemetrii | Okna agregowane: próbka co 15 s, batch 4 okien = transmisja co 60 s. `quality` per punkt pomiarowy, `errors[]` z katalogu, `sent_at` + `received_at`. Deduplikacja po `(device_id, seq)` unikalnym constraintem → `200 duplicate` zamiast błędu | [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md), [`TelemetryPayload.h`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) |
| 6 | Konfiguracja bez rekompilacji | **Brak.** Interwały, APN, adres serwera, piny — wszystko `#define`/`const` w [`Config.h`](../../firmware/include/Config.h), ustalane na etapie kompilacji. `sensor_registry.yaml` jest wspólnym źródłem prawdy dla *typów* i *kodów błędów*, ale nie dla konfiguracji urządzenia. Obietnica „profili urządzeń" z [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md) nie ma dziś implementacji | [`Config.h`](../../firmware/include/Config.h), [`sensor_registry.yaml`](../../sensor_registry.yaml) |
| 7 | OTA i zarządzanie flotą | **Brak OTA.** Aktualizacja firmware wymaga fizycznego dostępu i kabla USB. Brak widoku floty; [`06_device_identity_module.md` §6](../technical/backend/06_device_identity_module.md) sam wskazuje brak widoku „pula nieprzypisanych urządzeń". Brak zarządzania SIM | grep w `firmware/` — zero kodu OTA |
| 8 | Model danych i retencja | PostgreSQL, jeden wiersz na pakiet, pomiary w kolumnie `payload` JSONB. Brak TSDB, brak polityki retencji, brak downsamplingu. Ochrona przed nieograniczonym odczytem: `MAX_PACKETS_PER_SERIES = 5000` | [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md), [`packets.py`](../../backend/app/modules/telemetry/repositories/packets.py) |
| 9 | Model alarmów | **Brak modułu alarmowego** — ani na gatewayu, ani w backendzie. Istnieje wyłącznie status wyliczany na żądanie w `TelemetryQueryService._compute_status` (`no_data` / `no_comm` / `warning` / `ok`) oraz `errors[]` zapisywane do `telemetry_errors`. Reguły alarmowe z [`01_plan_biznesowy.md` §2.6](../business/01_plan_biznesowy.md) nie są zaimplementowane | [`query.py`](../../backend/app/modules/telemetry/services/query.py) |
| 10 | API i integracje | REST (FastAPI), dwie płaszczyzny dostępu: `/api/v1/orgs/{org_id}/...` i `/api/v1/platform/...`, autoryzacja JWT + kody `CAN_*`/`PLATFORM_*`. Brak publicznego API dla klienta, brak webhooków, brak integracji ze SCADA/GIS, brak eksportu poza UI | [`01_backend-architecture.md` §7](../technical/backend/01_backend-architecture.md) |
| 11 | Bezpieczeństwo | TLS w transmisji, uwierzytelnianie urządzeń kluczem asymetrycznym, RBAC, **append-only audit log wymuszony na poziomie sesji SQLAlchemy** (`AuditAwareSession` blokuje commit bez wpisu audytowego), rate limiting per-IP na redeem. Brak Secure Boot i Flash Encryption (świadomie odłożone). Brak certyfikatów ISO, brak polityki ujawniania podatności, brak pen-testów | [`01_backend-architecture.md` §4.2](../technical/backend/01_backend-architecture.md), [`06_device_identity_module.md` §6](../technical/backend/06_device_identity_module.md) |

### 2.1. Trzy fakty, które trzeba mieć w głowie przy czytaniu reszty

1. **Bufor lokalny istnieje tylko w RAM.** `std::vector<MeasurementWindow> windows_buffer_` w [`TelemetryPayload.h:43`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L43), pojemność `RETAIN_WINDOWS_MAX = 4 × 12` okien ≈ 12 minut. Reset, zanik zasilania albo watchdog kasuje bufor. [`CONTEXT.md`](../business/CONTEXT.md) definiuje „bufor lokalny" jako *pamięć flash/SD z minimalną retencją 72 godzin* — **kod nie realizuje własnej definicji ze słownika domenowego, różnica wynosi trzy rzędy wielkości**.
2. **Transmisja jest bezwarunkowa i stała.** Co 60 s, niezależnie od tego, czy dane się zmieniły i czy dzieje się coś ważnego. Nie ma trybu „wyślij natychmiast, bo przekroczono próg".
3. **Read-only jest świadomym wyborem** ([`CONTEXT.md`](../business/CONTEXT.md), założenia MVP). Wszędzie tam, gdzie konkurencja ma sterowanie, zapis do rejestrów albo DNP3 control points, my mamy z definicji lukę — i to jest w porządku. Ten dokument nie traktuje braku sterowania jako opóźnienia.

---

## 3. Kogo zbadano, kogo odrzucono i dlaczego

### 3.1. Polska — zestaw zamknięty z §5.2 planu biznesowego

Brief nakazuje nie szukać nowych polskich konkurentów. Zbadano technicznie pięć podmiotów wskazanych w [§5.2](../business/01_plan_biznesowy.md):

| Podmiot | Badany artefakt | Głębokość dostępnych źródeł |
|---|---|---|
| **Inventia** | moduły MT-101 / MT-151 / MT-331 / MT-713, platforma DataPortal | wysoka dla sprzętu (karty katalogowe, instrukcje), **niska dla platformy** (dokumentacja za loginem) |
| **AquaRD** | rejestratory CellBOX (H4, HS, NFL), platforma HydraNet Expert / WMR | średnia — karty katalogowe publiczne, DTR-y na FTP „strefy klienta" |
| **UniCloud / Unitronics / Elmark** | platforma UniCloud, routery IIoT, sterowniki UniStream | **wysoka** — jedyny podmiot z publiczną stroną „Security Fundamentals" opisującą model bezpieczeństwa |
| **Hawle.live** | Hawle.live BOX, CAP, KEY, aplikacja | **niska** — materiały wyłącznie marketingowe, brak jakiejkolwiek karty katalogowej z parametrami elektrycznymi |
| **AIUT WaterPrime** | platforma analityczna | średnia — opis modułów analitycznych, brak warstwy urządzeniowej (jej nie ma w produkcie) |

Pozostałe podmioty z §5.2 (NASUS, Hydro-Vacuum, Metalchem, Hydro-Partner) to **integratorzy i producenci pomp sprzedający monitoring jako dodatek**. Nie mają własnej architektury technicznej do porównania w 11 wymiarach — ich „stack" to cudze PLC i cudza SCADA dobrane per projekt. Pominięte świadomie; ocena biznesowa z §5.2 pozostaje w mocy.

### 3.2. Świat — kandydaci zweryfikowani

Brief wskazał listę kandydatów do sprawdzenia i wymagał odrzucenia niepasujących z uzasadnieniem.

**Przyjęci jako porównywalni (6):**

| Podmiot | Kraj | Dlaczego porównywalny |
|---|---|---|
| **Kallipr** (Captis + Kallipr Kloud) | AU | Wzorzec wskazany w briefie. Model tożsamy z docelowym: własne urządzenie bateryjne LPWAN + platforma chmurowa + zarządzanie flotą |
| **Ayyeka** (Wavelet + FAI) | IL / US | Najbliższy technicznie odpowiednik tego, czym chcemy być: urządzenie neutralne wobec czujników, platforma z REST API, silny nacisk na cyberbezpieczeństwo |
| **HWM** (MultiLog LX2 + DataGate / HWMOnline) | UK | Bezpośredni odpowiednik w wod-kan: logger + hurtownia danych + portal. Publikuje instrukcje użytkownika |
| **Metasphere** (Point Orange IoT / Point Blue) | UK | Jedyny badany podmiot z **konfigurowalnym programowo I/O** i obsługą otwartego standardu branżowego WITS-DNP3 |
| **Ovarro** (Kingfisher, TBox, D26) | UK | Wzorzec dla warstwy protokołów przemysłowych (DNP3, IEC 60870-5-101/104) i redundancji. Uwaga: Ovarro ≠ Metasphere, to dwie różne firmy |
| **NIVUS** (NivuLink + D2W / WebPortal) | DE | Europejski odpowiednik modelu „logger + portal + osobne narzędzie konfiguracji urządzeń", z interfejsem HART |

**Odrzuceni z uzasadnieniem (3):**

| Podmiot | Dlaczego odrzucony |
|---|---|
| **Xylem / Sensus (FlexNet)** | To **AMI**, nie telemetria obiektowa. FlexNet jest prywatną, licencjonowaną siecią radiową dalekiego zasięgu budowaną pod masowy odczyt wodomierzy, z wieżami nadawczymi po stronie operatora **[mkt]**. Model ekonomiczny (inwestycja w sieć radiową) i skala (dziesiątki tysięcy punktów) nie mają styku z „5–15 obiektów w małej gminie". Porównywanie 11 wymiarów dałoby pozorne wnioski |
| **Itron (Intelis, OpenWay Riva)** | To samo co wyżej — licznik + własna sieć AMI. Dodatkowo produkt jest meter-centric: jednostką jest wodomierz, nie obiekt wodociągowy z wieloma kanałami |
| **Telit** | Producent modułów komórkowych z platformą (OneEdge/deviceWISE) **związaną z własnymi modułami** — patrz §7. Nie jest konkurentem w naszej kategorii; jako komponent do kupienia rozpatrzony w osobnej sekcji |

**Golioth, Blues Wireless, Balena** — zgodnie z decyzją briefu **nie są traktowane jako konkurencja** i nie występują w tabeli porównawczej. To potencjalne komponenty do kupienia zamiast budowania; analiza w [§7](#7-platformy-device-management-ogólnego-przeznaczenia--kupić-czy-budować).

### 3.3. Standard, który okazał się ważniejszy od pojedynczego konkurenta

W trakcie badania wymiaru 3 (protokół) wyszła rzecz, której nie było w żadnej z list kandydatów, a która ma dla nas większe znaczenie niż połowa zbadanych firm: **WITS** — otwarty standard telemetrii dla branży wodociągowej, w wariancie **WITS-IoT** oparty dokładnie na tym, co my budujemy własnymi siłami. Opisany w [§5.3](#53-wymiar-3--protokół-transmisji-urządzenie--chmura) i [§8](#8-co-warto-skopiować).

---

## 4. Tabela porównawcza — podmiot × 11 wymiarów

Skróty: **M** = Modbus, **AI** = wejście analogowe, **DI** = wejście cyfrowe/impulsowe, **n/u** = nieujawnione, **n/d** = nie dotyczy (podmiot nie ma tej warstwy).

| Podmiot | 1. Sprzęt gatewaya | 2. Interfejsy | 3. Protokół | 4. Tożsamość / provisioning | 5. Format telemetrii | 6. Konfiguracja bez rekompilacji |
|---|---|---|---|---|---|---|
| **NASZ SYSTEM** | dev-kit, brak obudowy/IP, zasilanie sieciowe | SPI/PT100; 4-20 mA draft | HTTPS + własny JSON, niepublikowany | EC P-256 na urządzeniu, challenge/response, kod po Serial | okna 15 s, batch 60 s, `quality` per punkt, dedupe `(device_id, seq)` | **brak** — wszystko compile-time |
| **Inventia** | przemysłowy, DIN, 12/24 VDC / 24 VAC | 8 DI/licznik + 8 konfig. I/O + 2 AI 4-20 mA + RS-232/485/422, M RTU master i slave, 1-Wire | własny nad GPRS/SMS/CSD; **MQTT + TLS** w MT-331 | numer seryjny + IMEI w DataPortal | event-triggered data logger, filtracja i histereza na module | **tak** — konfiguracja i programowanie lokalnie lub zdalnie przez GPRS; CODESYS na MT-121/151 |
| **AquaRD** | przemysłowy, **IP68 / IP54**, bateria do 5 lat lub AkuBOX / 230 VAC | 6× AI 4-20 mA + 6× DI impulsowe, 2× RS485, M RTU/ASCII **master do 10 urządzeń**, M TCP do SCADA | GPRS / LTE-M / NB-IoT / WIZE 169 MHz; M RTU i TCP do systemu nadrzędnego | n/u | harmonogram (np. 1 h) **+ transmisja spontaniczna przy alarmie**; pamięć nieulotna | **tak** — CellBOX Konfigurator lokalnie, Hydra.Net zdalnie |
| **UniCloud** | router IIoT (~2 000 zł) lub sterownik UniStream | zależne od PLC/routera; integracja z istniejącą automatyką | **MQTT z certyfikatem X.509 (AWS IoT)**; REST po TLS | **certyfikat X.509**, ownership zarządzany przez platformę | n/u; buforowanie na routerze przy braku łącza | **tak** — konfiguracja z chmury, VPN do PLC bez stałego IP |
| **Hawle.live** | urządzenie produktowe, bateria + PowerPack + panel solarny | n/u — producent nie publikuje interfejsów elektrycznych | 4G/3G/2G, globalna SIM; protokół n/u | rejestracja przez portal „My Hawle" | **co 12 h + natychmiast przy alarmie**; kanały konfigurowalne | **tak** — kanały i progi konfigurowalne, harmonogram alertów |
| **WaterPrime** | n/d — platforma analityczna bez własnego gatewaya | n/d (konsumuje SCADA, AMR/AMI, GIS) | n/d | n/d | n/d — pracuje na danych z cudzych systemów | zarządzanie konfiguracją sieci czujników pod kątem energii i diagnostyki |
| **Kallipr** | Captis, **IP68**, bateria (S2: deklarowane 20 lat) | AI / DI / szeregowe (rodzina Captis) | **MQTT**; specyfikacja MQTT publikowana w materiałach wsparcia; certyfikacja Cumulocity (SmartREST 2.0); opcja Azure IoT | zarządzane przez Kallipr Kloud / Cumulocity | interwały pomiaru i transmisji **w pełni konfigurowalne** — jawny kompromis dokładność/latencja/bateria | **tak** — konfiguracja zdalna z platformy |
| **Ayyeka** | Wavelet V2, **IP68/NEMA 6P, −40…+80 °C**, bateria 32 Ah / 5+ lat, dual SIM, GPS | **do 12 czujników**: 4× AI (0-33 mA, 0-27,5 V), 4× szeregowe (RS485/SDI-12/RS232, M RTU/ASCII), 2× DI z licznikiem | do FAI; **FAI Lite** wypuszcza dane wprost do brokera MQTT / DNP3 / OPC-UA / CSV | n/u (platforma zarządza flotą) | 700 KB pamięci wewnętrznej (2–3 tyg.), opcjonalna karta SD 8–32 GB (~500 mln próbek) | **tak** — zdalna konfiguracja z FAI |
| **HWM** | MultiLog LX2, **IP68**, bateria 5 lat | wejście szeregowe z obsługą Modbus, impulsy do 128/s | LTE-M / NB-IoT z fallbackiem 2G; **dane do DataGate albo wprost na serwer klienta** | n/u | **interwał logowania od 24 h do 1 s** | **tak** — zdalna zmiana progów alarmowych i częstotliwości próbkowania z DataGate |
| **Metasphere** | Point Orange IoT, **IP68 (4 m przez 4 dni)**, bateria 5+ lat; Point Blue = wersja iskrobezpieczna (Ex) | **programowo konfigurowalne I/O** (AI/CI/DI), 5 czujników + 10 przez multidrop M/SDI-12 | **DNP3, WITS-DNP3**, Medina, Modbus master, SDI-12; NB-IoT/Cat-M1, 5G ready | n/u | **250 mln rekordów w pamięci** | **tak** — zdalna konfiguracja i zdalna aktualizacja firmware |
| **Ovarro** | Kingfisher / Kingfisher Plus — modułowy RTU z redundancją CPU, zasilania i komunikacji | modułowe karty I/O | **DNP3, IEC 60870-5-101/104, Modbus**; komórkowa / radiowa / Ethernet | n/u | klonowanie konfiguracji na kartę SD | **tak** — narzędzia konfiguracyjne producenta |
| **NIVUS** | NivuLink Micro II, **IP68**, samowystarczalny | 4 wejścia uniwersalne (analogowe lub cyfrowe) + **HART** | GPRS do portalu D2W; SIM NIVUS albo własna | n/u | portal z przekazywaniem danych dalej (data forwarding) | **tak** — osobne narzędzie D2W DeviceConfig |

| Podmiot | 7. OTA i flota | 8. Model danych i retencja | 9. Model alarmów | 10. API i integracje | 11. Bezpieczeństwo (deklarowane publicznie) |
|---|---|---|---|---|---|
| **NASZ SYSTEM** | **brak OTA**, brak widoku floty, brak zarządzania SIM | PostgreSQL + JSONB, **brak retencji i downsamplingu** | **brak modułu**; tylko status `no_data`/`no_comm`/`warning`/`ok` i `errors[]` | REST wewnętrzny, **brak publicznego API i webhooków** | TLS, klucz asymetryczny, RBAC, **audit log wymuszony na poziomie sesji DB**, rate limiting. Brak Secure Boot, brak ISO, brak polityki ujawniania podatności |
| **Inventia** | **zdalna aktualizacja firmware** (flash), zdalne programowanie przez GPRS | data logger na module, wyzwalany zdarzeniem; retencja w DataPortal n/u | **progi na module** z histerezą, deadband i filtracją; alarmy SMS | otwarta łączność do SCADA klienta, baz relacyjnych; **MQTT do chmur IT** (MT-331) | **ISO 9001 + ISO/IEC 27001**; deklarowane zarządzanie podatnościami, ciągłość wsparcia, odpowiedzialność w łańcuchu dostaw. Brak publicznej polityki CVD |
| **AquaRD** | zdalne zarządzanie przez Hydra.Net; zarządzanie kartami SIM w ofercie | pamięć nieulotna na urządzeniu; HydraNet z bilansowaniem DMA | **alarm na urządzeniu wyzwala transmisję spontaniczną** | M TCP/RTU do SCADA; integracja Billing / GIS / model matematyczny; aplikacje mobilne Android | n/u |
| **UniCloud** | fleet management z mapą; **automatyczny backup programu PLC co 30 dni z restore** | n/u (SaaS na AWS) | ewaluacja w chmurze; push / SMS / e-mail; wykrywanie anomalii; raporty miesięczne e-mailem | **REST API + webhooki**; eksport CSV | **ISO/IEC 27001:2013 + ISO/IEC 27017:2015**, MQTT X.509, szyfrowanie at rest i in transit, 2FA, WAF, SOC/NOC 24/7, AWS CloudTrail, multitenant |
| **Hawle.live** | n/u | „trwałe przechowywanie danych do pełnej dokumentacji" **[mkt]** | progi alarmów i ostrzeżeń per kanał, harmonogram czasowy alertów; push / SMS / e-mail | n/u | n/u |
| **WaterPrime** | zarządzanie konfiguracją floty czujników | integruje bazy, modele hydrauliczne, odczyty; poprawa jakości danych | detekcja anomalii i wycieków, predykcja, **ILI per strefa DMA wg dyrektywy 2020/2184** | integracja SCADA / AMR / AMI / GIS / **IBM Maximo** | n/u |
| **Kallipr** | **Firmware Management** przez Cumulocity; device management w Kloud | dane w Kloud, wizualizacja near real-time | n/u | **rozdział data plane / management plane** — dane do własnego brokera MQTT, zarządzanie zostaje w Kloud; Shell Commands, Events, Child Device Management | „dane szyfrowane end-to-end" **[mkt]** |
| **Ayyeka** | **zdalna aktualizacja firmware + zdalna konfiguracja + fleet oversight z FAI** | 700 KB / SD do 32 GB na urządzeniu; FAI hostowane **albo on-premise** | alerty **SMS / e-mail / głosowe** z poziomami ważności | **REST API**, DNP3, OPC; FAI Lite → MQTT / DNP3 / OPC-UA / CSV | **TLS 1.2 + AES-256**, dynamiczny adres IP per sesja urządzenia dla zmniejszenia powierzchni ataku |
| **HWM** | zdalna zmiana parametrów pracy loggera z DataGate | DataGate jako hurtownia danych, deklarowane 99,99% uptime | **progi alarmowe konfigurowane zdalnie**, automatyczne alerty do wielu użytkowników | **API na wniosek** (klucz API mailem do supportu); eksport do Excela, SCADA, systemów billingowych | n/u |
| **Metasphere** | **zdalna aktualizacja firmware + zdalna konfiguracja** | 250 mln rekordów lokalnie | zgodnie z modelem WITS-DNP3 (alarmowanie w standardzie) | łączy się z masterami Medina / DNP3 / WITS-DNP3 (np. ClearSCADA) | model bezpieczeństwa wynika z WITS-DNP3 (uwierzytelnianie master↔device) **[spec]** |
| **Ovarro** | narzędzia producenta, klonowanie SD | logowanie lokalne | model SCADA (DNP3 / IEC 60870) | protokoły przemysłowe do dowolnego SCADA | „bezpieczne połączenia chroniące aktywa i dane" **[mkt]**; redundancja jako element odporności |
| **NIVUS** | D2W DeviceConfig | WebPortal — przechowywanie, analiza, weryfikacja, protokoły | alarmowanie z portalu | **data forwarding** z portalu do systemów klienta | n/u |

---

## 5. Analiza wymiar po wymiarze

Dla każdego wymiaru: co robi rynek → gdzie stoimy → co konkretnie by to zmieniło.

### 5.0. Podsumowanie pozycji — odpowiedź na pytanie „gdzie stoimy"

| Wymiar | Pozycja | Jednozdaniowe uzasadnienie | Co ją zmienia |
|---|---|---|---|
| 1. Sprzęt gatewaya | 🔴 z tyłu | Zestaw deweloperski bez obudowy i bez IP, gdy rynkowym minimum jest IP68 albo montaż DIN w wykonaniu przemysłowym | H-1, H-3 |
| 2. Interfejsy pomiarowe | 🔴 z tyłu | Jeden działający kanał (PT100/SPI) wobec 4–6 kanałów uniwersalnych + Modbus multidrop u każdego konkurenta | F-5, F-6, F-7, H-2 |
| 3. Protokół | 🟡 na poziomie / 🔴 strategicznie | Bezpieczny i sensowny, ale wyłącznie własny i nieopublikowany — przy istniejącym otwartym standardzie branżowym (WITS-IoT) | B-6, poz. 12 z §8 |
| 4. Tożsamość i provisioning | 🟢 z przodu kryptograficznie / 🔴 operacyjnie | Klucz generowany na urządzeniu jest mocniejszy niż SN+IMEI, ale wymagamy laptopa w hydroforni, czego nie wymaga nikt | B-10 |
| 5. Format telemetrii | 🟢 semantyka / 🔴 strategia i bufor | `quality`, `errors[]` i dedupe po `(device_id, seq)` są dobre; 12 minut bufora w RAM i sztywne 60 s — nie | F-1, F-2, F-3 |
| 6. Konfiguracja bez rekompilacji | 🔴 z tyłu | Wszystko compile-time, gdy zdalną konfigurację ma **każdy** badany podmiot; „profil urządzenia" z ADR-0002 nie ma implementacji | F-4, B-2 |
| 7. OTA i flota | 🔴 z tyłu | Brak OTA = wyjazd do każdego obiektu przy każdej poprawce i brak ścieżki łatania podatności | F-8, B-8, B-9 |
| 8. Model danych i retencja | 🟡 na dziś / 🔴 na trajektorii | PostgreSQL+JSONB wystarcza przy kilku prototypach, ale nie ma żadnej polityki retencji ani downsamplingu | B-3, B-4 |
| 9. Model alarmów | 🔴 z tyłu | Zero implementacji wobec §2.6 planu; propozycja wartości „dowiesz się, zanim zadzwoni mieszkaniec" nie ma pokrycia | B-1, F-3 |
| 10. API i integracje | 🔴 z tyłu | REST tylko na własne potrzeby: brak eksportu, webhooków i jakiegokolwiek wyjścia do systemów klienta | B-5, B-6, B-7 |
| 11. Bezpieczeństwo | 🟡 technicznie / 🔴 formalnie / 🟢 audyt | Wymuszony maszynowo audit log jest mocniejszy niż typowy; brakuje Secure Boot, certyfikacji i polityki CVD | F-9, poz. 10 z §8 |

Odczyt całości: **mocni jesteśmy tam, gdzie decydował projekt oprogramowania** (kryptografia urządzenia, semantyka pomiaru, niezmiennik audytowy), **słabi tam, gdzie decyduje dojrzałość produktu w terenie** (sprzęt, interfejsy, zdalna konfiguracja, OTA, alarmy, otwartość danych). To jest typowy profil systemu, który przeszedł dobrą fazę projektową i nie przeszedł jeszcze fazy eksploatacyjnej — i dokładnie tak należy go przedstawiać.

### 5.1. Wymiar 1 — architektura sprzętowa gatewaya

**Rynek.** Wszystkie sześć zbadanych podmiotów zagranicznych i dwa z trzech polskich z własnym sprzętem dostarczają **urządzenie w obudowie o określonym stopniu ochrony**. IP68 jest normą, nie wyróżnikiem: Ayyeka Wavelet V2 **[dok]**, Kallipr Captis **[mkt]**, HWM MultiLog LX2 **[mkt]**, Metasphere Point Orange (IP68 do 4 m przez 4 dni) **[mkt]**, NIVUS NivuLink **[mkt]**, AquaRD CellBOX H4 (IP68 i IP54) **[mkt]**. Inventia idzie inną, równie zamkniętą drogą: montaż na szynę DIN, zasilanie 12/24 VDC / 24 VAC, wejścia optoizolowane **[dok]**.

Zakres temperatur podaje publicznie tylko Ayyeka: **−40 °C do +80 °C** **[dok]**. To jest liczba, którą warto zapamiętać jako poprzeczkę — hydrofornia bez ogrzewania w styczniu i szafa w pełnym słońcu w lipcu mieszczą się w tym zakresie z zapasem, a zestaw deweloperski ESP32-S3 nie ma podanego zakresu przemysłowego.

Drugi podział przebiega wzdłuż **zasilania**. Rynek dzieli się na dwie klasy:
- *bateryjne, samowystarczalne* — AquaRD (do 5 lat), Ayyeka (32 Ah, 5+ lat, wymienialna w terenie), HWM (5 lat), Metasphere (5+ lat), Kallipr (S2: deklarowane 20 lat), Hawle (bateria + PowerPack + panel solarny). Ta klasa nadaje się na komory pomiarowe i studnie bez zasilania;
- *sieciowe, obiektowe* — Inventia, Ovarro, UniCloud. Ta klasa nadaje się do hydroforni i przepompowni z szafą.

**Gdzie stoimy: 🔴 z tyłu.** Nasz W1 nie należy do żadnej z tych klas — jest zestawem deweloperskim bez obudowy, bez IP, bez ochrony przepięciowej, z zasilaniem zewnętrznym 5 V / 2 A i wspólną masą prowadzoną przewodami ([`01_hardware.md` §7](../technical/firmware/01_hardware.md)). W szafie hydroforni z falownikiem to jest problem odporności, nie estetyki.

**Co by to zmieniło.** Zamknięcie luki nie wymaga własnej płytki: klasa „sieciowa, obiektowa" jest osiągalna przez obudowę DIN + zasilacz przemysłowy + ochronnik przepięciowy na wejściu, przy zachowaniu obecnej elektroniki. Klasa „bateryjna, IP68" jest natomiast poza zasięgiem obecnej architektury — ESP32-S3 z modemem LTE Cat 1 transmitujący co 60 s nie zbliży się do 5 lat na baterii. **To jest realna, strukturalna granica naszego obecnego wyboru sprzętowo-transmisyjnego** i trzeba ją świadomie przyjąć albo zmienić oba elementy naraz (moduł LTE-M/NB-IoT + rzadsza transmisja + deep sleep). Zasila to bezpośrednio wybór wariantów W1/W2/W3 w B-01.

### 5.2. Wymiar 2 — obsługiwane interfejsy pomiarowe

**Rynek.** Realny katalog, nie deklaracje:

| Podmiot | AI 4-20 mA | 0-10 V | DI / impulsowe | RS485 / Modbus | SDI-12 | Inne |
|---|---|---|---|---|---|---|
| Inventia MT-101 | 2 (optoizolowane) | — | 8 + 8 konfigurowalnych | RS-232/485/422, M RTU master **i slave** | — | 1-Wire (MT-331), liczniki 0-2 kHz |
| AquaRD CellBOX H4 | 6 uniwersalnych | — | 6 impulsowych | 2× RS485, M RTU/ASCII master do 10 urządzeń, M TCP | — | HART n/u |
| Ayyeka Wavelet V2 | 4 (0-33 mA, 0-27,5 V) | tak (0-27,5 V) | 2 (styk bezprądowy / open drain, licznik) | RS485/RS232, M RTU/ASCII | **tak** | do 12 czujników na 3 portach |
| Metasphere Point Orange | konfigurowalne programowo | konfigurowalne | konfigurowalne | M master RS232/485 | **tak, multidrop** | 5 czujników + 10 przez multidrop |
| HWM MultiLog LX2 | n/u | n/u | impulsy do 128/s | port szeregowy z Modbus | n/u | — |
| NIVUS NivuLink Micro II | 4 uniwersalne (AI lub DI) | — | 4 uniwersalne | n/u | — | **HART** |
| **NASZ SYSTEM** | **1, w wersji draft** | — | — | — | — | SPI/MAX31865 (PT100) |

Trzy obserwacje z tej tabeli:

1. **Modbus RTU master jest wspólnym mianownikiem** — mają go wszyscy poza nami. To nie jest „dodatek dla zaawansowanych", to podstawowy sposób podpięcia się do istniejącej automatyki bez wymiany czujników. Nasza [`CONTEXT.md`](../business/CONTEXT.md) w założeniu „neutralność sprzętowa" wymienia Modbus RTU jako obsługiwany. **Nie jest.**
2. **Wejścia impulsowe są równie powszechne** — bo wodomierz z wyjściem impulsowym to najczęstszy istniejący pomiar w małej gminie. Ich brak wyklucza cały przypadek użycia „przepływ z istniejącego wodomierza".
3. **SDI-12 pojawia się tam, gdzie w grę wchodzi jakość wody** (Ayyeka, Metasphere). Dla naszej Fazy 2 (chlor, mętność) to sygnał, którym interfejsem pójść.

**Gdzie stoimy: 🔴 z tyłu, i to jest największa różnica techniczna w całej analizie.** Mamy jeden zweryfikowany kanał (PT100 przez SPI) i jeden w wersji draft wysyłający sinusa. Rynek zaczyna od 4–6 kanałów uniwersalnych plus multidrop.

**Co by to zmieniło.** Dodanie Modbus RTU master przez RS485 to jedna klasa `ISensor` plus transceiver — architektura firmware jest na to gotowa ([`06_adding_sensors.md`](../technical/firmware/06_adding_sensors.md), interfejs `ISensor` i wpis w `sensor_registry.yaml` bez zmian w rdzeniu `TelemetryPayload`). Ten jeden dodatek zamienia „czytamy nasze dwa czujniki" na „czytamy to, co gmina już ma", czyli realizuje obietnicę z [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md). **Szacunek własny: 3–5 dni roboczych** przy istniejącym `ISensor`, plus koszt sprzętu rzędu kilkunastu złotych za moduł RS485.

### 5.3. Wymiar 3 — protokół transmisji urządzenie ↔ chmura

**Rynek dzieli się na trzy obozy:**

1. **MQTT** — Kallipr **[mkt/spec]**, UniCloud (MQTT X.509 nad AWS IoT) **[mkt]**, Inventia w MT-331 (MQTT + TLS) **[mkt]**, Ayyeka jako wyjście alternatywne (FAI Lite → broker MQTT) **[mkt]**.
2. **Protokoły przemysłowe SCADA** — DNP3 i IEC 60870-5-101/104 (Ovarro **[mkt]**), Modbus TCP jako wyjście do systemu nadrzędnego (AquaRD **[mkt]**), Medina i WITS-DNP3 (Metasphere **[mkt]**).
3. **Protokoły własne** nad GPRS/HTTP — Inventia w starszej rodzinie, HWM do DataGate, my.

**Kluczowe ustalenie całego wymiaru: istnieje otwarty standard branżowy dokładnie dla naszego przypadku.**

**WITS** (Worldwide Industrial Telemetry Standards, pierwotnie *Water* Industry Telemetry Standards) powstał w połowie lat 2000 z inicjatywy brytyjskich wodociągów wspólnie z producentami sprzętu; od 2011 zarządza nim **WITS Protocol Standards Association** **[3rd]**. Ma dwa warianty:

- **WITS-DNP3** — na bazie DNP3 level 2+, dla dużych, stale zasilanych obiektów. Uwierzytelnianie master↔urządzenie, ograniczone plug-and-play **[3rd]**;
- **WITS-IoT** — opublikowany w wersji 1.0 w październiku 2018. **MQTT + TLS jako transport, wiadomości JSON jako warstwa aplikacyjna.** Zaprojektowany dla bardzo dużej liczby małych urządzeń, które są online tylko przez krótkie okresy, zasilanych bateryjnie, po bezprzewodowym WAN. Funkcje protokołu: odczyt wartości, sterowanie punktami, **alarmowanie, logowanie, sterowanie aplikacją i konfiguracja urządzenia — wszystko objęte jednym modelem bezpieczeństwa**. Pełne plug-and-play **[spec/3rd]**.

Oba warianty definiują **profile urządzeń jako opisy możliwości w XML**, zdalne zarządzanie konfiguracją i lokalne logowanie ze znacznikami czasu **[3rd]**.

Przeczytajmy tę listę funkcji jeszcze raz obok naszego backlogu: alarmowanie (nie mamy), logowanie z buforem (mamy 12 minut w RAM), zdalna konfiguracja urządzenia (nie mamy), profile urządzeń opisujące możliwości (obiecane w ADR-0002, nie mamy), jeden model bezpieczeństwa dla wszystkiego (mamy własny, tylko dla danych). **To jest specyfikacja rzeczy, które i tak zamierzamy zbudować — napisana przez branżę, dla której budujemy, i przetestowana interoperacyjnie.**

**Gdzie stoimy: 🟡 na poziomie technicznie, 🔴 z tyłu strategicznie.** Nasz HTTPS + JSON działa, jest bezpieczny i ma sensowną semantykę. Ale jest **wyłącznie nasz**: nieopublikowany, nieinteroperacyjny, niedający się podłączyć do żadnego istniejącego mastera. W przetargu, w którym padnie słowo „WITS" albo „DNP3", nie mamy czym odpowiedzieć.

**Uczciwe zastrzeżenie.** Sam Inventia w materiale o MQTT stawia trafną tezę: MQTT nie daje interoperacyjności między producentami, bo konfiguracja i interpretacja danych zostaje po stronie użytkownika **[mkt]**. Właśnie dlatego warstwa aplikacyjna WITS-IoT nad MQTT jest ciekawsza niż samo przejście na MQTT — przejście na MQTT bez warstwy semantycznej zamieni jeden własny format na drugi.

**Co by to zmieniło.** Trzy poziomy ambicji, rosnący koszt:
- *tanio:* opublikować naszą specyfikację payloadu (OpenAPI + JSON Schema) jako dokument dla klienta i integratora — to zamienia „format zamknięty" w „format udokumentowany". **Szacunek własny: 1–2 dni**;
- *średnio:* dopasować nazewnictwo i semantykę naszego JSON do pojęć WITS-IoT (punkty, jakość, znaczniki, konfiguracja), zostając przy HTTP. Ułatwia późniejszą pełną zgodność. **Szacunek własny: 3–5 dni** plus koszt pozyskania specyfikacji;
- *drogo:* pełna zgodność WITS-IoT na MQTT z akredytacją. **Nie do zrobienia przed pierwszym wdrożeniem** i bez sensu przy kilku prototypach — ale warto wiedzieć, że ścieżka istnieje, zanim wybierzemy się w przeciwną stronę na własnym formacie.

### 5.4. Wymiar 4 — model tożsamości i provisioningu urządzenia

**Rynek.** Trzy modele:

| Model | Kto | Ocena |
|---|---|---|
| **Certyfikat X.509** | UniCloud (MQTT X.509 nad AWS IoT, ownership zarządzany przez platformę) **[mkt]** | Standard branżowy, integruje się z chmurami publicznymi |
| **Identyfikator sprzętowy** | Inventia — numer seryjny + IMEI w DataPortal **[mkt]** | Proste, ale IMEI nie jest sekretem; bezpieczeństwo opiera się na APN/VPN, nie na kryptografii urządzenia |
| **Zarządzane przez platformę, nieujawnione** | Kallipr, Ayyeka, HWM, Metasphere, NIVUS | Wszyscy mają fleet provisioning, żaden nie opisuje mechanizmu publicznie |

Osobno warto odnotować, jak wygląda **pierwsze uruchomienie w terenie**, bo to wymiar czysto operacyjny:
- Kallipr, Metasphere, HWM, AquaRD, Hawle — urządzenie jest **fabrycznie zarejestrowane w platformie**, montaż to przykręcenie i sprawdzenie zasięgu; konfiguracja zdalna z portalu albo lokalnie aplikacją;
- UniCloud deklaruje wdrożenie „poniżej 30 minut" **[mkt]** i wdrożenie na czynnym obiekcie w ok. 2 tygodnie bez przestoju **[mkt]** — te dwie liczby dotyczą różnych rzeczy i pierwsza jest marketingowa;
- **my** — technik musi podłączyć laptopa do portu USB i wpisać `ACTIVATE <kod>` po porcie szeregowym, w oknie 900 sekund ważności kodu ([`06_device_identity_module.md` §3.2](../technical/backend/06_device_identity_module.md)).

**Gdzie stoimy: 🟢 z przodu kryptograficznie, 🔴 z tyłu operacyjnie.**

Kryptograficznie mamy rzecz mocniejszą niż większość rynku i porównywalną z UniCloud: **klucz prywatny generowany na urządzeniu i nigdy go nieopuszczający**, dowód posiadania przez podpis, brak współdzielonego sekretu z backendem. To jest lepszy model niż SN + IMEI i równorzędny z X.509 (a przy X.509 klucz często wgrywa się fabrycznie, więc opuszcza urządzenie).

Operacyjnie natomiast wymagamy w terenie **laptopa i terminala szeregowego**, w oknie 15 minut, przy montażu w hydroforni. Nikt inny tego nie wymaga. To jest ta różnica, która w praktyce decyduje, czy montaż robi elektryk z gminy, czy musi jechać nasz inżynier — a więc bezpośrednio uderza w model kosztowy z [§4.2.3 planu](../business/01_plan_biznesowy.md).

**Co by to zmieniło.** Nie trzeba zmieniać kryptografii — trzeba zmienić **kanał wprowadzenia kodu**. Wystarczy, żeby kod aktywacyjny dało się dostarczyć bez laptopa: powiązanie kodu z numerem seryjnym po stronie platformy (operator wpisuje SN i kod w panelu, urządzenie pobiera swój claim samo po pierwszym połączeniu) albo tryb AP z prostą stroną konfiguracyjną z telefonu. Warto przy tym zauważyć, że dziś **kod aktywacyjny świadomie nie jest powiązany z SN** ([`06_device_identity_module.md` §4](../technical/backend/06_device_identity_module.md)) — powiązanie go rozwiązuje jednocześnie problem operacyjny i zamyka lukę „kod może zużyć dowolne urządzenie". **Szacunek własny: 5–8 dni** (backend + firmware + panel operatora).

### 5.5. Wymiar 5 — format telemetrii

**Rynek.** Nikt z badanych nie publikuje pełnego schematu payloadu poza Kallipr (specyfikacje MQTT w materiałach wsparcia **[mkt]**) i standardem WITS-IoT **[spec]**. Można natomiast porównać **strategie próbkowania i wysyłki**, i to jest ciekawsze:

| Podmiot | Strategia |
|---|---|
| AquaRD CellBOX | harmonogram (np. co godzinę) **+ transmisja spontaniczna przy alarmie** **[mkt]** |
| Hawle.live BOX | **co 12 h domyślnie + natychmiast w przypadku alarmu** **[mkt]** |
| Inventia MT-101 | **event triggered data logger** — logowanie wyzwalane zdarzeniem **[dok]** |
| HWM MultiLog LX2 | interwał logowania konfigurowalny **od 24 h do 1 s** **[mkt]** |
| Kallipr Captis | interwały pomiaru i transmisji **osobno konfigurowalne**, jawnie opisane jako kompromis dokładność/latencja/bateria **[mkt]** |
| Sensus FlexNet (odrzucony, ale wzorzec) | do 6 odczytów dziennie, ale **alarmy transmitowane w ciągu minut** **[mkt]** |
| **NASZ SYSTEM** | stałe 15 s próbka / 60 s transmisja, bez wyjątków |

**Wzorzec jest jednoznaczny i powtarza się u pięciu niezależnych producentów: rozdziel częstotliwość pomiaru od częstotliwości transmisji, a transmisję rutynową od transmisji alarmowej.** Rutyna idzie rzadko i tanio; zdarzenie idzie natychmiast.

Drugi wymiar to **głębokość bufora lokalnego**:

| Podmiot | Bufor |
|---|---|
| Metasphere Point Orange | **250 mln rekordów** **[mkt]** |
| Ayyeka Wavelet V2 | 700 KB wewnętrznie (2–3 tygodnie), opcjonalna SD 8–32 GB (~500 mln próbek) **[dok]** |
| AquaRD CellBOX | pamięć nieulotna wewnętrzna **[mkt]** |
| UniCloud | buforowanie na routerze przy braku internetu **[mkt]** |
| **NASZ SYSTEM** | **~12 minut w RAM**, tracone przy resecie |

**Gdzie stoimy: 🟢 z przodu w semantyce, 🔴 z tyłu w strategii i buforze.**

Nasza semantyka jest dobra i miejscami lepsza niż rynkowa: `quality` przy każdym punkcie, `errors[]` ze wspólnego katalogu, rozdzielenie `sent_at` od `received_at`, **deduplikacja po `(device_id, seq)` obsłużona jako `200 duplicate`, a nie jako błąd** ([`04_telemetry_module.md` §3](../technical/backend/04_telemetry_module.md)). To ostatnie jest przemyślane — retransmisja po utracie potwierdzenia nad LTE jest normą, nie wyjątkiem, i mało kto obsługuje ją tak czysto.

Ale strategia jest sztywna, a bufor 12-minutowy w RAM to **poważna luka względem własnej dokumentacji**: [`CONTEXT.md`](../business/CONTEXT.md) definiuje bufor lokalny jako flash lub kartę SD z minimalną retencją **72 godzin**. Różnica między 12 minutami w ulotnej pamięci a 72 godzinami w nieulotnej to nie jest niedopracowanie — to jest inna właściwość produktu. Przy dwugodzinnej awarii LTE (rzecz codzienna w terenie) tracimy dane bezpowrotnie, a UC-04 z planu („utrata komunikacji") kończy się dziurą w historii zamiast opóźnioną dostawą.

**Co by to zmieniło.** Dwie zmiany, obie w firmware:
- przeniesienie bufora do NVS/flash z retencją liczoną w godzinach, nie minutach ([`TelemetryPayload.h`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) — `windows_buffer_` staje się warstwą nad pamięcią nieulotną). **Szacunek własny: 4–6 dni** wraz z testami wznawiania po resecie;
- rozdzielenie interwału próbkowania od transmisyjnego i dodanie wyzwalacza „wyślij teraz" — to samo w sobie jest tanie, ale ma sens dopiero, gdy istnieje coś, co potrafi stwierdzić „przekroczono próg", czyli po wymiarze 9.

### 5.6. Wymiar 6 — konfiguracja bez rekompilacji

**Rynek: wszyscy badani mają zdalną konfigurację. Bez wyjątku.**

- Inventia — konfiguracja i programowanie lokalnie **lub zdalnie przez GPRS**; progi, histereza, deadband i filtracja ustawiane na module **[dok]**;
- AquaRD — CellBOX Konfigurator lokalnie, Hydra.Net zdalnie **[mkt]**;
- HWM — z DataGate zdalnie zmienia się **progi alarmowe i częstotliwość próbkowania** **[3rd]**;
- Metasphere — zdalna konfiguracja i zdalna aktualizacja firmware, przy **programowo konfigurowalnym I/O** (to samo wejście fizyczne bywa analogowe, licznikowe albo cyfrowe zależnie od konfiguracji) **[mkt]**;
- Kallipr — interwały konfigurowalne z platformy **[mkt]**;
- Ayyeka — zdalna konfiguracja z FAI **[mkt]**;
- NIVUS — osobne narzędzie D2W DeviceConfig **[mkt]**;
- UniCloud — konfiguracja z chmury plus VPN do PLC bez stałego IP **[mkt]**;
- Hawle — kanały indywidualnie konfigurowalne, progi alarmów i ostrzeżeń, harmonogram alertów **[mkt]**.

A ponad tym stoi standard: WITS definiuje **profile urządzeń jako opisy możliwości w XML** i zdalne zarządzanie konfiguracją jako część protokołu, nie jako dodatek **[3rd]**.

**Gdzie stoimy: 🔴 z tyłu, jednoznacznie i bez okoliczności łagodzących.** Wszystko jest compile-time. Zmiana APN, adresu serwera, interwału próbkowania albo dodanie kanału wymaga rekompilacji i fizycznego dostępu do urządzenia — bo nie mamy też OTA (wymiar 7). W praktyce oznacza to **wyjazd do obiektu z laptopem po każdej zmianie parametru**.

Warto to zestawić z [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md) i [`CONTEXT.md`](../business/CONTEXT.md), gdzie „profil urządzenia" jest zdefiniowany jako *konfiguracja zawierająca protokół komunikacji, mapowanie rejestrów, jednostki i skalowanie, używana bez zmian firmware'u*. Definicja jest trafna i zgodna z tym, co robi rynek. **Implementacji nie ma żadnej.** To jest największy rozjazd między naszą dokumentacją a naszym kodem, jaki ta analiza znalazła.

**Co by to zmieniło.** Jest tania ścieżka pośrednia, którą warto rozważyć przed pełnymi profilami: **pobieranie konfiguracji przy starcie**. Urządzenie po uwierzytelnieniu odpytuje backend o swoją konfigurację (interwały, progi, lista kanałów, mapowanie), zapisuje ją w NVS i stosuje. Nie wymaga OTA, nie wymaga zmiany protokołu, a zdejmuje z barków 80% powodów do wyjazdu w teren. **Szacunek własny: 6–10 dni** (endpoint + model konfiguracji w backendzie + klient w firmware + panel edycji).

### 5.7. Wymiar 7 — OTA i zarządzanie flotą

**Rynek.** Zdalna aktualizacja firmware jest standardem, w tym u polskiego dostawcy z rodowodem sprzed ery IoT: Inventia deklaruje **firmware flash z możliwością zdalnej aktualizacji** już przy MT-101 **[dok]**. Metasphere — zdalna aktualizacja firmware **[mkt]**. Ayyeka — aktualizacja firmware z poziomu FAI, obok zdalnej konfiguracji i przeglądu floty **[mkt]**. Kallipr — **Firmware Management** jako certyfikowana funkcja w ekosystemie Cumulocity, obok Events, Measurements, Shell Commands i Child Device Management **[spec]**.

Ciekawostka warta odnotowania: UniCloud robi rzecz, której nie robi nikt inny z badanych — **automatyczny backup programu sterownika PLC co 30 dni z możliwością przywrócenia** **[mkt]**. To jest zarządzanie flotą rozumiane jako ochrona przed utratą konfiguracji obiektu, nie tylko jako wysyłanie nowych wersji.

Zarządzanie SIM jako element oferty: AquaRD **[mkt]**, NIVUS (SIM NIVUS albo własna) **[mkt]**, Hawle (globalna karta SIM) **[mkt]**.

**Gdzie stoimy: 🔴 z tyłu — to jest najostrzejsza operacyjnie luka w całej analizie.**

Nie mamy OTA. Przy kilku prototypach u jednego klienta da się z tym żyć — ale każda poprawka bezpieczeństwa, każda zmiana formatu payloadu i każdy bug fix oznacza **fizyczny wyjazd do każdego obiektu z kablem USB**. Przy 15 obiektach jednej gminy rozproszonych po jej terenie to jest dzień pracy na każdą wersję firmware.

Jest jeszcze konsekwencja, której nie widać od razu: **brak OTA blokuje bezpieczeństwo**. [`06_device_identity_module.md` §6](../technical/backend/06_device_identity_module.md) odkłada Secure Boot i Flash Encryption na później — to rozsądne. Ale bez OTA nie mamy też ścieżki naprawy podatności, którą znajdziemy po wdrożeniu. Wobec nadchodzącego Cyber Resilience Act i wymagań NIS2 wobec dostawców podmiotów kluczowych (zakres B-01) „nie mamy jak zaktualizować urządzenia w terenie" jest odpowiedzią, której nie da się obronić przed gminą.

**Co by to zmieniło.** ESP32 ma OTA w standardzie (`esp_ota_ops`, dwie partycje aplikacji, rollback po nieudanym boot). Główna praca to nie sam mechanizm, tylko **bezpieczne pobranie obrazu przez modem** (HTTPS chunkowany przez TinyGSM, weryfikacja podpisu obrazu) i **strona serwerowa** (rejestr wersji, przypisanie do urządzeń, raportowanie stanu). Wzorzec „cohorts" Golioth (grupy urządzeń, jedna aktywna dystrybucja na grupę) jest dobrym modelem do skopiowania nawet przy własnej implementacji — patrz [§7](#7-platformy-device-management-ogólnego-przeznaczenia--kupić-czy-budować). **Szacunek własny: 10–15 dni** dla wersji własnej z podpisem obrazu i rollbackiem.

### 5.8. Wymiar 8 — model danych i retencja

**Rynek.** To najsłabiej udokumentowany wymiar — **żaden z badanych podmiotów nie publikuje, jakiej bazy używa ani jaką ma politykę retencji**. Dostępne są tylko pojemności po stronie urządzenia (Metasphere: 250 mln rekordów **[mkt]**; Ayyeka: ~500 mln próbek na SD **[dok]**) i ogólniki po stronie chmury (HWM DataGate jako „hurtownia danych" z deklarowanym 99,99% uptime **[3rd]**; Hawle: „trwałe przechowywanie danych do pełnej dokumentacji" **[mkt]**).

Jedyna twarda informacja o architekturze danych pochodzi z ekosystemu open source, nie od konkurencji: **ThingsBoard** trzyma encje w PostgreSQL, a szeregi czasowe w PostgreSQL, **TimescaleDB** albo Cassandrze — do wyboru zależnie od skali **[dok]**. To jest realna wskazówka, jak wygląda dojrzały wybór w tej klasie systemów.

TimescaleDB jest rozszerzeniem PostgreSQL (nie osobną bazą), które daje automatyczne partycjonowanie po czasie (hypertables), **kompresję danych historycznych** oraz **continuous aggregates** — inkrementalnie odświeżane widoki zagregowane, i **polityki retencji** usuwające lub kompresujące dane starsze niż zadany okres **[3rd]**.

**Gdzie stoimy: 🟡 na poziomie na dziś, 🔴 z tyłu na trajektorii.**

PostgreSQL z pomiarami w JSONB jest dla kilku prototypów wyborem całkowicie poprawnym — prostszym w utrzymaniu niż osobna TSDB i wystarczającym przy obecnym wolumenie. Ale mamy **zero polityki retencji i zero downsamplingu**, przy telemetrii wpadającej co 60 s z każdego obiektu i bez żadnego mechanizmu, który by ją kiedykolwiek zredukował. Limit `MAX_PACKETS_PER_SERIES = 5000` chroni pojedyncze zapytanie przed wyczerpaniem pamięci procesu, ale **nie chroni bazy przed nieograniczonym wzrostem** — to zabezpieczenie odczytu, nie zarządzanie cyklem życia danych.

Jest też kwestia kształtu danych. Jeden wiersz na pakiet z pomiarami zagnieżdżonymi w `payload` JSONB oznacza, że zapytanie o szereg czasowy jednego punktu pomiarowego musi przeskanować pakiety i rozpakować JSON w locie. Przy roku danych z 15 obiektów to zaczyna być odczuwalne, a każdy indeks na „punkt pomiarowy + czas" jest utrudniony.

**Co by to zmieniło.** Kolejność ma znaczenie i warto ją zapisać:
1. **najpierw polityka retencji** — decyzja produktowa („ile lat trzymamy pomiary z rozdzielczością 1 min, ile z 1 h"), nie techniczna. Bez niej pozostałe kroki są przedwczesne;
2. **potem downsampling** — agregaty godzinowe i dobowe liczone raz, zamiast liczenia średnich z surowych danych przy każdym wejściu na dashboard;
3. **dopiero na końcu TimescaleDB**, jeśli wolumen tego wymaga. Jest to rozszerzenie PostgreSQL, więc migracja jest addytywna i mieści się w dyscyplinie zero-downtime z ustaleń wspólnych briefów.

Ważne: krok 1 i 2 dają się zrobić na czystym PostgreSQL. **Szacunek własny: 3–4 dni** na politykę retencji z zadaniem czyszczącym, 5–8 dni na tabelę agregatów. Zmiana kształtu tabeli pomiarowej (rozbicie JSONB na wiersze per punkt) to osobna, większa decyzja — i jest to dokładnie ten rodzaj migracji, który briefy każą projektować jako addytywną z backfillem w tle.

### 5.9. Wymiar 9 — model alarmów

**Rynek. Alarm jest ewaluowany blisko danych, czyli na urządzeniu — i to jest wzorzec, nie przypadek:**

- **Inventia MT-101** — konfigurowalne progi alarmowe na obu wejściach analogowych, z konfigurowalną **histerezą, deadbandem i filtracją** **[dok]**. To poziom szczegółu, który mówi wszystko: producent wie, że surowy próg bez histerezy generuje lawinę alarmów przy wartości oscylującej wokół granicy;
- **AquaRD CellBOX** — alarm na urządzeniu **wyzwala transmisję spontaniczną** poza harmonogramem **[mkt]**;
- **Hawle.live** — progi alarmów i ostrzeżeń per kanał, **harmonogram czasowy alertów** (inne progi/reguły w innych porach), transmisja natychmiastowa przy alarmie **[mkt]**;
- **HWM** — progi alarmowe zmieniane zdalnie z DataGate, automatyczne alerty do wielu użytkowników **[3rd]**;
- **WITS-IoT** — alarmowanie jest **funkcją protokołu**, obok odczytu, logowania i konfiguracji, objętą wspólnym modelem bezpieczeństwa **[spec]**.

Ewaluacja po stronie chmury występuje tam, gdzie reguła wymaga korelacji między obiektami: UniCloud (wykrywanie anomalii, powiadomienia push/SMS/e-mail) **[mkt]**, WaterPrime (detekcja wycieków, ILI per strefa DMA) **[mkt]**, Ayyeka (alerty SMS/e-mail/**głosowe** z poziomami ważności) **[mkt]**.

Zwraca uwagę **kanał głosowy u Ayyeki** — dla awarii o trzeciej w nocy SMS i e-mail bywają niewystarczające. Warto zapamiętać jako opcję, nie jako wymóg.

**Gdzie stoimy: 🔴 z tyłu — mamy zero.** Ani na gatewayu, ani w backendzie. Cały [§2.6 planu biznesowego](../business/01_plan_biznesowy.md) (katalog alarmów krytycznych, ostrzeżeń, zdarzeń informacyjnych i parametrów reguł) nie ma odpowiednika w kodzie. Istnieje wyłącznie status wyliczany na żądanie w `TelemetryQueryService._compute_status` — czyli informacja, że *teraz* coś jest nie tak, bez historii, bez potwierdzania, bez powiadomienia i bez trwałości.

Warto to nazwać wprost: **UC-03 z planu („wykrycie możliwego wycieku lub pęknięcia") i cała propozycja wartości „gmina dowiaduje się o awarii, zanim zadzwoni mieszkaniec" nie mają dziś implementacji.** Dashboard pokaże spadek ciśnienia komuś, kto akurat patrzy.

**Co by to zmieniło.** Rynek podpowiada podział, który warto przyjąć od razu, żeby nie przepisywać tego dwa razy:
- **na gatewayu** — proste progi na wartości z jednego kanału, z **histerezą i deadbandem** (wzorzec Inventia), których jedynym zadaniem jest wyzwolenie natychmiastowej transmisji. Firmware nie wysyła powiadomień, tylko przestaje czekać na harmonogram;
- **w backendzie** — pełny cykl życia alarmu (wystąpienie, potwierdzenie, komentarz, zamknięcie, fałszywy alarm), reguły czasowe („ciśnienie < 2 bar **przez 120 s**" z [`CONTEXT.md`](../business/CONTEXT.md)), korelacje między kanałami, powiadomienia i eskalacja.

Nowy moduł backendu `alarms/` wpisuje się wprost w istniejący szablon modułu domenowego z [`01_backend-architecture.md` §5](../technical/backend/01_backend-architecture.md), a fakt, że alarm jest zmianą stanu biznesowego (potwierdzenie przez człowieka), zgrywa się z niezmiennikiem audytowym — w przeciwieństwie do ingestu telemetrii, który świadomie commituje z `skip_audit=True`. **Szacunek własny: 12–20 dni** dla modułu backendu z powiadomieniami, 3–5 dni dla progów w firmware. Projekt ekranu alarmów jest przedmiotem B-03 i te dwa zlecenia trzeba zestawić przed implementacją.

### 5.10. Wymiar 10 — API i integracje

**Rynek.** Trzy poziomy otwartości:

| Poziom | Kto | Konkret |
|---|---|---|
| **Publiczne API jako funkcja produktu** | UniCloud | **REST API + webhooki**, eksport CSV **[mkt]** |
| | Ayyeka | **REST API**, DNP3, OPC, on-premise jako opcja; **FAI Lite** — dane wprost do brokera MQTT / DNP3 / OPC-UA / CSV z pominięciem platformy **[mkt]** |
| | Kallipr | dane do **własnego brokera MQTT klienta**, przy zachowaniu device managementu w Kloud; integracja z Cumulocity i Azure IoT **[spec/mkt]** |
| **API na wniosek** | HWM | klucz API wydawany po kontakcie z supportem; integracja z Excelem, SCADA, systemami billingowymi **[3rd]** |
| **Integracja przez protokół przemysłowy** | AquaRD | Modbus TCP/RTU do SCADA, integracja Billing/GIS/model matematyczny **[mkt]** |
| | Ovarro | DNP3, IEC 60870-5-101/104 **[mkt]** |
| | Metasphere | mastery Medina / DNP3 / WITS-DNP3 **[mkt]** |
| | NIVUS | data forwarding z portalu do systemów klienta **[mkt]** |
| | Inventia | otwarta łączność do SCADA klienta i baz relacyjnych **[mkt]** |

**Najciekawszy wzorzec całej analizy pojawił się tu, i to niezależnie u dwóch producentów z dwóch kontynentów: rozdzielenie płaszczyzny danych od płaszczyzny zarządzania.**

Kallipr pozwala przekierować dane pomiarowe do brokera MQTT klienta, **zostawiając zarządzanie urządzeniami w Kallipr Kloud** **[mkt]**. Ayyeka robi to samo pod nazwą FAI Lite — surowe dane do MQTT/DNP3/OPC-UA/CSV, z pominięciem pełnej platformy **[mkt]**.

Dlaczego to jest ważne akurat dla nas: usuwa najsilniejszy zarzut, jaki gmina może postawić małemu dostawcy — **„co się stanie z naszymi danymi, jeśli wy przestaniecie istnieć"**. Odpowiedź „dane lecą również na wasz endpoint, platforma jest wygodą, nie więzieniem" jest mocniejsza niż jakakolwiek deklaracja o ciągłości działania. Dla dostawcy bez historii i bez ISO to jest realny argument sprzedażowy, a nie tylko funkcja.

**Gdzie stoimy: 🔴 z tyłu.** Mamy REST, ale **wyłącznie na własne potrzeby**: dwie płaszczyzny dostępu, JWT, kody uprawnień. Klient nie ma czym pobrać swoich danych poza interfejsem. Brak webhooków, brak eksportu, brak jakiegokolwiek wyjścia w stronę SCADA czy GIS.

**Co by to zmieniło.** Kolejność od najtańszego:
1. **Eksport CSV z UI** — najtańsza rzecz w tej analizie, a odpowiada na UC-05 („raport i eksport") wprost. **Szacunek własny: 1–2 dni**;
2. **Publiczne, wersjonowane API odczytu** z tokenem per organizacja — nasza architektura już ma płaszczyznę organizacji i kody uprawnień, więc to jest głównie kwestia autoryzacji tokenem zamiast JWT użytkownika i opublikowania OpenAPI. **Szacunek własny: 4–6 dni**;
3. **Webhooki na alarm** — mają sens dopiero po wymiarze 9, ale zaprojektować warto razem z nim;
4. **Wyjście „dane też do was"** (kopia telemetrii na endpoint klienta albo jego broker MQTT) — wzorzec Kallipr/Ayyeka. **Szacunek własny: 5–8 dni**, i to jest ta funkcja o najlepszym stosunku wartości sprzedażowej do kosztu w całym wymiarze.

### 5.11. Wymiar 11 — bezpieczeństwo

**Rynek. Publiczna komunikacja bezpieczeństwa jest bardzo nierówna:**

| Podmiot | Co deklaruje publicznie |
|---|---|
| **UniCloud** | **ISO/IEC 27001:2013 + ISO/IEC 27017:2015** (ta druga to norma specyficznie chmurowa), MQTT X.509, szyfrowanie at rest i in transit, REST po TLS, 2FA, polityka haseł, WAF przeciw SQL injection i XSS, SOC i NOC 24/7, antywirus, audyt zasobów przez AWS CloudTrail, multitenant, VPN do serwisu PLC **[mkt]** |
| **Inventia** | **ISO 9001 + ISO/IEC 27001**, deklarowane: aktualizacje, obsługa podatności, dokumentacja, ciągłość wsparcia, procedury, odpowiedzialność w łańcuchu dostaw **[mkt]** |
| **Ayyeka** | **TLS 1.2 + AES-256**, dynamiczny adres IP dla każdej sesji urządzenia w celu zmniejszenia powierzchni ataku, opcja wdrożenia on-premise **[dok/mkt]** |
| **Metasphere** | model bezpieczeństwa dziedziczony z WITS-DNP3 (bezpieczne uwierzytelnianie master↔urządzenie w standardzie) **[spec]** |
| **Kallipr** | „dane szyfrowane end-to-end" **[mkt]** |
| **Ovarro** | „bezpieczne połączenia chroniące aktywa i dane" **[mkt]**, redundancja CPU/zasilania/komunikacji |
| **AquaRD, Hawle, NIVUS, HWM, WaterPrime** | nieujawnione |

**Nikt z badanych nie publikuje polityki skoordynowanego ujawniania podatności (CVD) ani listy security advisories.** Sprawdzone celowo — to jest luka całej branży, nie tylko nasza. Warto ją odnotować, bo Cyber Resilience Act robi z CVD obowiązek producenta, a CERT Polska prowadzi ścieżkę CVD dla polskich producentów niebędących CNA **[3rd]**. Wobec gminy objętej NIS2 posiadanie takiej polityki jest tanim wyróżnikiem — dokument, nie inżynieria.

**Gdzie stoimy: 🟡 na poziomie technicznie, 🔴 z tyłu formalnie, 🟢 z przodu w jednym konkretnym miejscu.**

*Z przodu:* nasz **append-only audit log wymuszony na poziomie sesji SQLAlchemy** to rozwiązanie mocniejsze niż typowe. `AuditAwareSession` blokuje `commit()`, jeśli w sesji nie zarejestrowano zdarzenia audytowego i nie przekazano jawnie `skip_audit=True` ([`01_backend-architecture.md` §4.2](../technical/backend/01_backend-architecture.md)). Niezmiennik „żadna zmiana biznesowa nie commituje się bez śladu" jest wymuszony maszynowo, nie konwencją w code review. Żaden z badanych podmiotów nie komunikuje niczego na tym poziomie szczegółu — choć uczciwie: bo nikt nie opisuje publicznie wnętrza swojego backendu. To przewaga względem tego, co widać, nie dowiedziona przewaga względem tego, co jest.

*Na poziomie:* TLS w transmisji, uwierzytelnianie urządzeń kluczem asymetrycznym generowanym na urządzeniu (mocniejsze niż SN+IMEI Inventii, porównywalne z X.509 UniCloud), RBAC, rate limiting.

*Z tyłu:* brak Secure Boot i Flash Encryption (świadomie odłożone, [`06_device_identity_module.md` §6](../technical/backend/06_device_identity_module.md)) — a bez nich klucz prywatny EC leży w NVS w postaci odczytywalnej po zdjęciu obudowy. Brak jakiejkolwiek certyfikacji. Brak polityki ujawniania podatności. Brak pen-testów. Brak ścieżki łatania (patrz wymiar 7).

**Co by to zmieniło.** Najtańsze rzeczy o największym efekcie wobec gminy to **dokumenty, nie kod**: polityka ujawniania podatności na stronie, opis modelu bezpieczeństwa dla klienta, deklaracja czasów reakcji. **Szacunek własny: 2–3 dni.** Certyfikacja ISO 27001 przy obecnej skali jest niewspółmierna kosztowo (zakres B-01). Secure Boot i Flash Encryption warto włączyć **przed pierwszym wdrożeniem produkcyjnym**, bo po wdrożeniu wymagają fizycznego dostępu do każdego urządzenia — a bez OTA tym bardziej.

---

## 6. Karty podmiotów — fakty źródłowe

Skrócone karty z twardymi ustaleniami. Pełne notatki źródłowe w [§13](#13-źródła).

### 6.1. Inventia (PL)

Rodzina modułów telemetrycznych: MT-101, MT-121, MT-151 (HMI/LED, CODESYS), MT-331, MT-713/723. Technologie: 2G/LTE, LTE Cat M1, NB-IoT, GPS/GNSS, LTE450 **[mkt]**.

MT-101 **[dok]**: montaż DIN; zasilanie 12/24 VDC lub 24 VAC; 8 optoizolowanych wejść binarnych/licznikowych 24 V; 8 konfigurowalnych wyjść/wejść/liczników 24 V; 2 optoizolowane wejścia analogowe 4-20 mA (dokładność 8 bit, rozdzielczość 10 bit) z konfigurowalną histerezą i filtracją; izolowany port szeregowy RS-232/485/422; MODBUS RTU master i slave ze „smart MODBUS RTU routing"; wszystkie wejścia binarne jako liczniki lub konwertery częstotliwość→analog (0-2 kHz); firmware flash ze zdalną aktualizacją; **event triggered data logger**; konfiguracja i programowanie lokalnie lub zdalnie przez GPRS; RTC z synchronizacją zewnętrzną.

MT-331 **[3rd/mkt]**: modem u-blox SARA-U201 (2G/3G) lub LARA-R211 (2G/4G); niezależny procesor; akumulator Li-Ion podtrzymujący pracę; wejście 1-Wire; **MQTT z TLS** do integracji z chmurami IT.

DataPortal: identyfikacja modułu przez **numer seryjny i IMEI**; narzędzia integracyjne do SCADA klienta i baz relacyjnych **[mkt]**. Pełna dokumentacja platformy jest za loginem — **nieujawniona publicznie**, co uniemożliwia ocenę wymiarów 8 i 10 po stronie chmury.

Bezpieczeństwo: ISO 9001 i ISO/IEC 27001; deklarowane zarządzanie podatnościami i odpowiedzialność w łańcuchu dostaw; **brak publicznej polityki CVD i security advisories** **[mkt]**.

### 6.2. AquaRD (PL)

CellBOX H4 **[mkt]**: 6 uniwersalnych wejść analogowych 4-20 mA; 6 wejść impulsowych/zdarzeniowych; ModBUS RTU/ASCII **master do 10 podłączonych urządzeń pomiarowych**; 2× RS485; opcjonalnie Bluetooth/RFID/NFC; ModBUS TCP/RTU do SCADA; obudowa **IP68 lub IP54**; pamięć nieulotna; łączność GPRS / LTE Cat-M1 / NB-IoT / opcjonalnie WIZE 169 MHz; baterie litowe wewnętrzne dające **pracę bezobsługową do 5 lat** zależnie od częstotliwości transmisji, typu przetworników i temperatury; alternatywnie AkuBOX (wymienny pakiet akumulatorowy) lub 230 VAC / 24 VDC.

Transmisja: **harmonogram (np. co godzinę) + transmisja spontaniczna w przypadku alarmu** **[mkt]**.
Konfiguracja: lokalnie programem **CellBOX Konfigurator**, zdalnie przez **Hydra.Net** **[mkt]**.

HydraNet Expert **[mkt]**: bilansowanie wody w strefach DMA, wskaźniki ilościowe i jakościowe sieci, odczyt z wodomierzy, przetworników ciśnienia i przepływu, deszczomierzy, monitorów jakości wody, sterowników zaworów i loggerów akustycznych; integracja ze SCADA, Billing, GIS i modelem matematycznym; aplikacje mobilne Android (HydraNET Service, WMR Mobile).

### 6.3. UniCloud / Unitronics / Elmark (IL / PL)

Architektura **[mkt]**: sterowniki UniStream/Vision/Samba/Jazz oraz routery łączą się z SaaS na AWS. **MQTT z uwierzytelnianiem certyfikatem X.509** (AWS IoT), ownership urządzenia zarządzany przez platformę. REST API po TLS + webhooki. Multitenant.

Funkcje **[mkt]**: dashboardy no-code (wskaźniki, wykresy, tabele, mapy); fleet management z lokalizacją na mapie; **automatyczny backup programu PLC co 30 dni z przywracaniem**; role i organizacje; wielojęzyczność; branding klienta; VPN do serwisu PLC bez stałego IP.

Bezpieczeństwo **[mkt]**: ISO/IEC 27001:2013 i ISO/IEC 27017:2015; szyfrowanie at rest i in transit; 2FA; polityka haseł; WAF przeciw SQL injection i XSS; SOC i NOC 24/7; antywirus; AWS CloudTrail.

Wariant wod-kan (Elmark) **[mkt]**: router IIoT ok. 2 000 zł; **buforowanie danych na routerze przy braku internetu i wysyłka po przywróceniu połączenia**; połączenie wychodzące bez otwierania portów; alarmy push/SMS/e-mail z wykrywaniem odchyleń; eksport CSV jednym kliknięciem; raporty miesięczne wysyłane e-mailem; abonament 1–3 tys. zł rocznie za obiekt; integracja 3–7 tys. zł; wdrożenie ok. 2 tygodni bez przestoju produkcyjnego.

### 6.4. Hawle.live (AT / PL)

Hawle.live BOX **[mkt]**: stacja IoT zasilana bateryjnie, z opcjonalnym PowerPack i panelem solarnym dającym zasilanie ciągłe; łączność 4G (LTE) / 3G / 2G, globalna karta SIM, wydajna antena; kanały indywidualnie konfigurowalne; konfigurowalne progi alarmów i ostrzeżeń; harmonogram czasowy alertów; powiadomienia push / SMS / e-mail.

Transmisja: **dane zapisane przesyłane co 12 godzin (standard) oraz natychmiast w przypadku alarmu** **[mkt]**.

Zakres pomiarów: poziom napełnienia, wodomierz, przepływ, ciśnienie, zawory regulacyjne, jakość wody, kontaktron drzwiowy, temperatura, wykrycie zalania **[mkt]**.

Ekosystem: Hawle.live CAP (inteligentne nakładki modernizujące istniejące hydranty naziemne i podziemne), Hawle.live KEY (klucz NFC do zasuw), aplikacja z mapą i raportami **[mkt]**.

**Interfejsy elektryczne nieujawnione** — producent nie publikuje, czy i jak podłącza się czujniki 4-20 mA, Modbus czy impulsowe. To najsłabiej udokumentowany technicznie podmiot w całej analizie.

### 6.5. AIUT WaterPrime (PL)

Platforma analityczno-informatyczna bez własnej warstwy urządzeniowej **[mkt]**. Integruje: SCADA, AMR/AMI, bazy GIS, skalibrowane modele hydrauliczne, przepływomierze i nakładki na wodomierze.

Moduły: lokalizacja wycieku wskazująca nie tylko strefę, ale i konkretne miejsce; bilansowanie DMA z obliczaniem **ILI (Infrastructure Leakage Index) dla każdej strefy zgodnie z dyrektywą UE 2020/2184**; predykcja i detekcja anomalii; poprawa jakości danych; zarządzanie majątkiem zintegrowane z **IBM Maximo** (EAM/CMMS). Warstwa IoT: aktywne zarządzanie konfiguracją sieci czujników pod kątem zużycia energii i dokładności diagnostyki. Projekt współfinansowany ze środków UE (2,88 mln EUR).

**Znaczenie dla nas:** to nie jest konkurent na poziomie gatewaya. To pokazuje, dokąd prowadzi ścieżka analityczna, jeśli kiedyś w nią wejdziemy — i że wskaźnik ILI z dyrektywy 2020/2184 jest walutą, w której rozmawia się o stratach wody.

### 6.6. Kallipr (AU)

Captis **[mkt]**: IP68; LTE Cat-M1 / NB-IoT (pasmo 700 MHz); interwały pomiaru i transmisji w pełni konfigurowalne, jawnie opisane jako kompromis między dokładnością, częstotliwością, latencją a żywotnością baterii; dane szyfrowane. Captis S2: deklarowana bateria 20 lat.

Platforma Kallipr Kloud **[mkt]**: wizualizacja near real-time, przechowywanie do analizy. **Dane pomiarowe można przekierować do brokera MQTT klienta, przy czym device management zostaje w Kloud.**

Materiały wsparcia zawierają **specyfikacje MQTT** obok kart katalogowych i przewodników konfiguracji **[mkt]** — czyli protokół jest udokumentowany dla integratorów.

Certyfikacja w ekosystemie **Cumulocity IoT** **[spec]**: typ integracji „MQTT (SmartREST 2.0) Custom Agent"; wspierane funkcje platformy: Child Device Management, Events, **Firmware Management**, Measurements, Shell Commands. Alternatywnie integracja z Azure IoT.

### 6.7. Ayyeka (IL / US)

Wavelet V2 **[dok]**: 3 porty obsługujące do 12 czujników — 4 analogowe (0-33 mA, 0-27,5 V; obsługa 4-20 mA i 0-10 V), 4 szeregowe (RS485, SDI-12, RS232 z Modbus RTU/ASCII), 2 cyfrowe (5 styków bezprądowych / open drain z zliczaniem impulsów); bateria litowo-tionylochlorkowa 32 Ah wymienialna w terenie, **5+ lat**; zasilanie zewnętrzne 6-24 VDC z automatycznym przełączaniem; pamięć 700 KB wewnętrznie (2–3 tygodnie), opcjonalna karta SD 8–32 GB (~500 mln próbek); 4G z fallbackiem 3G/2G, **dual SIM**, opcjonalnie LoRaWAN, wbudowany GPS; **IP68/NEMA 6P, −40 °C do +80 °C**; wymiary 13,2 × 16,5 × 7,3 cm.

Wavelet 4R **[dok]**: LTE Cat-M1 / NB-IoT, 1 port, do 4 czujników, pojedynczy nano SIM, bez GPS, ta sama bateria i klasa środowiskowa.

Bezpieczeństwo **[dok]**: **TLS 1.2 z szyfrowaniem AES-256**; **dynamiczny adres IP dla każdej sesji urządzenia** w celu istotnego zmniejszenia powierzchni ataku.

Platforma FAI **[mkt]**: mapa aktywów; alerty SMS / e-mail / **głosowe** z konfigurowalnymi poziomami ważności; **zdalna konfiguracja, aktualizacja firmware i przegląd floty**; DNP3 i OPC; **REST API**; wdrożenie hostowane u dostawcy **albo on-premise**. **FAI Lite** — pominięcie pełnej platformy i podanie danych wprost do brokera MQTT lub agentów DNP3 / OPC-UA / CSV.

### 6.8. HWM (UK)

MultiLog LX2 **[mkt]**: LTE-M i NB-IoT z fallbackiem 2G; **interwał logowania od 24 godzin do 1 sekundy**; obsługa do 128 impulsów na sekundę; bateria wewnętrzna z deklarowaną żywotnością 5 lat; obudowa IP68 do zanurzenia; wejście szeregowe z obsługą Modbus do integracji z czujnikami i licznikami.

Transmisja: do portalu DataGate, **albo bezpośrednio na serwer wskazany przez klienta** **[mkt]**.

DataGate **[3rd]**: hurtownia danych z deklarowanym 99,99% uptime; udostępnianie danych aplikacjom wizualizacyjnym i systemom trzecim (Excel, SCADA, billing); **zarządzanie konfiguracją loggerów z możliwością zdalnej zmiany progów alarmowych i częstotliwości próbkowania**; automatyczne alerty do wielu użytkowników po odebraniu alarmu; **API udostępniane na wniosek** (klucz API po kontakcie z supportem).

### 6.9. Metasphere (UK)

Point Orange IoT **[mkt]**: **programowo konfigurowalne I/O** obsługujące wejścia analogowe, licznikowe i cyfrowe w setkach kombinacji; monitoring do 5 czujników w czasie rzeczywistym plus **do 10 dodatkowych przez multidrop Modbus lub SDI-12**; protokoły **DNP3, WITS-DNP3**, Medina, Modbus master (RS232 i RS485), SDI-12; łączność NB-IoT/Cat-M1, „5G ready", warianty 4G i GSM/GPRS, automatyczne przełączanie anteny wewnętrznej i zewnętrznej; bateria litowa 5+ lat; **IP68 do 4 metrów przez 4 dni**; **pamięć na 250 mln rekordów**; **zdalna aktualizacja firmware i zdalna konfiguracja**; łączy się z masterami Medina, DNP3 i WITS-DNP3 (przykład: ClearSCADA).

Point Blue **[mkt]**: wersja iskrobezpieczna Point Orange do stref zagrożonych wybuchem.

**Uwaga terminologiczna:** Metasphere i Ovarro to dwie różne firmy, mimo że produkt Point Orange bywa oferowany przez różnych dystrybutorów. Ovarro powstało w marcu 2021 z połączenia Servelec Technologies i Primayer pod jedną marką **[3rd]**.

### 6.10. Ovarro (UK)

Kingfisher i Kingfisher Plus **[mkt]**: modułowa platforma RTU dla wymagających zastosowań SCADA; wydajny procesor z inteligentnymi modułami komunikacyjnymi i I/O; **protokoły DNP3, IEC 60870-5-101/104, Modbus**; komunikacja komórkowa, radiowa i Ethernet; **redundancja CPU, zasilania i komunikacji**; wyświetlacz OLED/LED; klonowanie konfiguracji przez kartę SD. Pozostałe rodziny: TBox, DataWatt D26.

**Znaczenie dla nas:** wzorzec warstwy protokołów przemysłowych i odporności, a nie produktu do skopiowania. Kingfisher to klasa urządzeń dla obiektów, których małe gminy nie mają.

### 6.11. NIVUS (DE)

NivuLink Micro II **[mkt]**: do 4 wejść uniwersalnych, każde jako interfejs analogowy lub cyfrowy; wbudowany **interfejs HART** pozwalający podłączyć szeroki zakres czujników; obudowa **IP68**; samowystarczalny data logger.

Transmisja: GPRS do portalu D2W; praca z międzynarodową kartą SIM NIVUS albo z własną kartą klienta **[mkt]**.

Oprogramowanie **[mkt]**: **D2W DeviceConfig** jako osobne narzędzie konfiguracji urządzeń; NIVUS WebPortal jako system zarządzania danymi z analizą odczytów, weryfikacją systemu, **przekazywaniem danych dalej (data forwarding)**, alarmowaniem i generowaniem pełnych protokołów.

---

## 7. Platformy device management ogólnego przeznaczenia — kupić czy budować

Brief nakazuje potraktować te platformy **osobno, nie jako konkurencję**, i odpowiedzieć na pytanie: czy któryś z gotowych mechanizmów (provisioning, OTA, zarządzanie flotą) opłaca się wziąć z półki zamiast pisać samodzielnie.

### 7.1. Kandydaci i werdykty

| Platforma | Model | Zgodność z naszym stosem | Werdykt |
|---|---|---|---|
| **Golioth** | Chmura device management: OTA, konfiguracja, telemetria. SDK dla ESP-IDF i Zephyr. Transport **CoAP nad DTLS**, uwierzytelnianie **PSK albo X.509 z ECDSA**. Model: Packages → Artifacts → Deployments → **Cohorts** (urządzenie należy do jednej kohorty, kohorta ma jedną aktywną dystrybucję). OTA obejmuje nie tylko główny firmware, ale i **firmware modemu komórkowego** oraz dowolne binaria. Darmowy plan indywidualny: nieograniczona liczba urządzeń, 1 projekt, 1 GB OTA miesięcznie, do 3 kohort; plan Teams 299 USD/mies. **[dok/3rd]** | **Częściowa.** SDK celuje w ESP-IDF; nasz firmware to framework Arduino na PlatformIO z TinyGSM i AT-command HTTP. Golioth zakłada gniazda z offloadowanym DTLS i pełny stos IP — u nas transport realizuje modem po AT | **Nie adoptować całości teraz. Skopiować model.** Migracja to przepisanie warstwy transportowej firmware. Ale **model kohort jest wart skopiowania nawet przy własnym OTA** — grupa testowa dostaje wersję pierwsza, produkcja później. To dokładnie ta dyscyplina, której zabraknie przy „wgrywamy wszystkim naraz" |
| **Blues Wireless (Notecard + Notehub)** | Notecard to moduł M.2 z łącznością komórkową, komunikujący się z hostem **poleceniami JSON**. Notehub: routing danych do dowolnej chmury, zdalne zarządzanie, analityka, **OTA firmware hosta**. Funkcja **Notecard Outboard Firmware Update** pozwala wdrożyć OTA hosta **bez pisania kodu** — Notehub ustawia zmienną `_fw` na docelową wersję, a Notecard podmienia firmware przy kolejnej synchronizacji **[dok]** | **Zastępuje nasz modem.** To nie jest biblioteka, tylko inny sprzęt — A7670E + TinyGSM zniknęłyby | **Rozważyć przy wariancie W2/W3 sprzętu, nie teraz.** Jeśli B-01 doprowadzi do przeprojektowania sprzętu, Notecard jest realnym kandydatem: rozwiązuje naraz łączność, TLS, OTA i część provisioningu. Przy obecnym W1 to zmiana sprzętowa, nie programowa |
| **balena / balenaOS** | Kontenery na urządzeniach brzegowych | **Brak.** balenaOS to minimalna dystrybucja Linuksa (Yocto) dla komputerów jednopłytkowych i SOM-ów. **Mikrokontrolery, w tym ESP32, nie są wspierane** — istnieje otwarte zgłoszenie funkcjonalności od użytkowników, usługa Custom Device Support również wymaga sprzętu linuksowego **[dok/3rd]** | **Odrzucone definitywnie.** Niezgodność architektury, nie kwestia nakładu pracy |
| **Telit (OneEdge / deviceWISE)** | Zintegrowana oferta: moduły Telit + łączność + chmura. Transmisja przez **LwM2M**; FOTA i kampanie zarządzania urządzeniami; automatyczne akcje, alerty i alarmy na regułach w chmurze; plany pakietowe łączące moduł, oprogramowanie i transmisję **[dok/mkt]** | **Wymaga modułów Telit.** Plan „Lungo" obejmuje moduł ME910C1 LTE Cat M1/NB1 — czyli wymianę A7670E | **Odrzucone na teraz.** Wiąże nas z jednym dostawcą modułów i jednym operatorem oferty. Wartość: LwM2M jako standard device managementu wart odnotowania obok WITS |
| **ThingsBoard** (spoza listy briefu, dodane jako najbliższy realny substytut) | Otwartoźródłowa platforma IoT: zbieranie i wizualizacja danych, device management, **rule engine** przekształcający payload w model danych, **alarmy z propagacją po hierarchii encji**, alerty wielokanałowe (e-mail, SMS, Slack, Teams). Provisioning: poświadczenia podstawowe, tokeny dostępu albo **łańcuchy certyfikatów X.509**, w tym bulk provisioning z CSV. Dane: encje w PostgreSQL, szeregi czasowe w PostgreSQL, **TimescaleDB** albo Cassandrze. Licencja **Apache 2.0** — wolno użyć komercyjnie **[dok]** | **Wysoka technicznie, ale to platforma, nie biblioteka.** Zastąpiłaby nasz backend, nie uzupełniła go | **Nie adoptować — czytać jako wzorzec.** Nasz backend ma już moduły, audyt i model uprawnień dopasowany do gmin. Ale **model alarmów i rule engine ThingsBoard to najlepsza dostępna publicznie referencja** przy projektowaniu naszego modułu `alarms/` (wymiar 9), a ich wybór „PostgreSQL na encje, TimescaleDB na szeregi" potwierdza kierunek z wymiaru 8 |

### 7.2. Odpowiedź na pytanie briefu

**Nie warto dziś kupować platformy device managementu z półki. Warto skopiować z niej trzy konkretne mechanizmy i jeden wybór technologiczny.**

Uzasadnienie: każda z platform, która realnie rozwiązałaby nasz problem OTA (Golioth, Blues, Telit), wymaga zmiany warstwy transportowej firmware albo wymiany modemu. Przy kilku prototypach koszt migracji przewyższa koszt napisania własnego OTA na `esp_ota_ops`, które ESP32 ma w standardzie. Dodatkowo każda z nich wprowadza zależność od zewnętrznego dostawcy w ścieżce krytycznej urządzenia — co wobec gminy objętej NIS2 wymaga osobnego uzasadnienia w łańcuchu dostaw.

Do skopiowania bez adopcji platformy:
1. **Kohorty z Golioth** — grupowanie urządzeń, jedna aktywna dystrybucja na grupę, wdrożenie najpierw na urządzenia testowe;
2. **Rozdział „OTA firmware hosta" od „OTA firmware modemu"** — Golioth traktuje je jako osobne artefakty. Warto od razu tak zaprojektować, bo modem A7670E też ma własne firmware;
3. **Model alarmów z ThingsBoard** — reguły, propagacja po hierarchii encji (u nas: punkt pomiarowy → urządzenie → obiekt wodociągowy → organizacja), alerty wielokanałowe;
4. **Wybór bazy** — PostgreSQL na encje, TimescaleDB na szeregi czasowe, gdy wolumen tego wymaga.

Jedyny scenariusz, w którym warto wrócić do zakupu: **jeśli B-01 doprowadzi do przeprojektowania sprzętu na wariant W2 lub W3**, Blues Notecard należy wtedy rozważyć poważnie, bo rozwiązuje łączność, TLS, OTA i część provisioningu jednym komponentem z własnym CE.

---

## 8. Co warto skopiować

Uszeregowane według stosunku wartości do kosztu. Szacunki nakładu są **szacunkami własnymi**, nie danymi ze źródeł.

| # | Wzorzec | Od kogo | Dlaczego u nas | Nakład (szac. własny) |
|---|---|---|---|---|
| **1** | **Transmisja spontaniczna przy zdarzeniu, obok harmonogramu** | AquaRD, Hawle, Inventia, Sensus | Rozwiązuje sprzeczność, której dziś nie widać: żeby wykryć wyciek szybko, musimy nadawać często; żeby nadawać rzadko (bateria, transmisja), musimy wykrywać wolno. Rynek rozwiązał ją dwadzieścia lat temu — rutyna rzadko, zdarzenie natychmiast. Odblokowuje UC-03 i całą ścieżkę bateryjną | 3–5 dni (firmware), zależne od poz. 3 |
| **2** | **Modbus RTU master przez RS485** | wszyscy poza nami | Realizuje obietnicę „neutralności sprzętowej" z `CONTEXT.md` i ADR-0002, która dziś nie ma pokrycia. Zamienia „czytamy nasze dwa czujniki" na „czytamy to, co gmina ma" | 3–5 dni + kilkanaście zł sprzętu |
| **3** | **Progi z histerezą i deadbandem na urządzeniu** | Inventia (najlepiej opisane), AquaRD, Hawle | Wyzwalacz dla poz. 1. Histereza i deadband są w tym samym zdaniu karty katalogowej MT-101 co same progi — bo producent wie, że próg bez histerezy przy wartości drgającej wokół granicy generuje lawinę | 3–5 dni (firmware) |
| **4** | **Bufor w pamięci nieulotnej z retencją w godzinach** | Metasphere (250 mln rek.), Ayyeka (SD), AquaRD, UniCloud (bufor na routerze) | Nasze 12 minut w RAM vs. 72 godziny obiecane we własnym `CONTEXT.md`. Dwugodzinna awaria LTE = bezpowrotna dziura w danych | 4–6 dni (firmware + testy wznawiania) |
| **5** | **Pobieranie konfiguracji przy starcie** | wszyscy (zdalna konfiguracja jest u wszystkich) | Zdejmuje większość powodów do wyjazdu w teren, bez budowania pełnego OTA. Najtańsza droga do części obietnicy „profili urządzeń" | 6–10 dni (backend + firmware + panel) |
| **6** | **Kopia danych do systemu klienta („dane też do was")** | Kallipr (własny broker MQTT klienta), Ayyeka (FAI Lite), HWM (serwer klienta) | Najlepszy stosunek wartości sprzedażowej do kosztu w całej analizie. Rozbraja zarzut „co z naszymi danymi, jeśli wy znikniecie" — zarzut, który mały dostawca bez ISO i bez historii usłyszy na pewno | 5–8 dni |
| **7** | **OTA z kohortami i podpisanym obrazem** | Inventia, Metasphere, Ayyeka, Kallipr; model kohort z Golioth | Bez tego każda poprawka to wyjazd do każdego obiektu, a każda podatność jest nienaprawialna. Warunek konieczny dla jakiejkolwiek rozmowy o NIS2/CRA | 10–15 dni |
| **8** | **Moduł alarmów z pełnym cyklem życia** | wszyscy; wzorzec modelu z ThingsBoard | Bez niego propozycja wartości „dowiesz się, zanim zadzwoni mieszkaniec" nie ma implementacji. Do zestawienia z projektem ekranu z B-03 przed startem | 12–20 dni (backend) |
| **9** | **Publiczne API odczytu + eksport CSV** | UniCloud (REST+webhooki), Ayyeka (REST), HWM (API na wniosek) | Eksport CSV realizuje UC-05 za 1–2 dni. API odczytu jest tanie, bo płaszczyzna organizacji i kody uprawnień już istnieją | 1–2 dni (CSV) + 4–6 dni (API) |
| **10** | **Polityka ujawniania podatności i publiczny opis modelu bezpieczeństwa** | UniCloud (jako jedyny robi to porządnie); luka całej reszty branży | Dokument, nie inżynieria. Wobec gminy objętej NIS2 tani wyróżnik — i nikt z badanych polskich dostawców tego nie ma | 2–3 dni |
| **11** | **Rozdzielenie interwału pomiaru od interwału transmisji jako parametrów** | Kallipr (opisuje to wprost jako kompromis), HWM (1 s – 24 h) | Dziś oba są zaszyte w `Config.h` i sprzężone. Rozdzielenie jest warunkiem sensownej pracy na baterii i przy droższej transmisji | 2–3 dni, razem z poz. 5 |
| **12** | **Semantyka WITS-IoT jako wzorzec dla naszego payloadu** | standard WITS PSA | Nie pełna zgodność — same pojęcia i struktura. Alternatywą jest wymyślanie tego samego drugi raz, gorzej | 3–5 dni + koszt dostępu do specyfikacji |

---

## 9. Czego świadomie nie kopiujemy i dlaczego

| Czego nie kopiujemy | Od kogo pochodzi | Dlaczego nie |
|---|---|---|
| **Pełna zgodność z WITS-DNP3 / DNP3 / IEC 60870-5-104** | Ovarro, Metasphere | To protokoły dla systemów sterujących z masterem SCADA. Nasz system jest read-only i nie ma mastera po drugiej stronie. Implementacja DNP3 to miesiące pracy dla funkcji, których nasz klient nie ma czym odebrać — mała gmina nie ma ClearSCADA. Wracamy do tematu, gdy pierwszy klient poprosi o integrację z istniejącym SCADA, i wtedy prawdopodobnie taniej będzie wystawić Modbus TCP niż DNP3 |
| **Sterowanie i zapis do rejestrów** | Inventia (moduł jako PLC), Hydro-Vacuum, Metalchem, UniCloud | [`CONTEXT.md`](../business/CONTEXT.md) i MVP wykluczają sterowanie świadomie: read-only obniża klasę ryzyka, upraszcza analizę bezpieczeństwa i skraca drogę do wdrożenia u podmiotu z infrastrukturą krytyczną. To jest wybór, nie zaległość |
| **CODESYS / programowalny PLC na gatewayu** | Inventia MT-121/MT-151 | Wynika z powyższego. Programowalna logika na obiekcie to inny produkt, z innym profilem ryzyka i innym klientem |
| **Analityka hydrauliczna, bilansowanie DMA, ILI, detekcja wycieków modelem** | WaterPrime, AquaRD HydraNet, Ovarro LeakNavigator | Wymaga skalibrowanego modelu hydraulicznego sieci, gęstego opomiarowania stref i danych, których mała gmina nie ma. Sprzedaż tego bez modelu to sprzedaż liczby, która nic nie znaczy. Kierunek na później, po latach zebranych danych — nie na MVP |
| **Zarządzanie majątkiem / EAM (IBM Maximo)** | WaterPrime | Klasa systemu i cena kompletnie poza segmentem małych gmin |
| **Architektura bateryjna IP68 na 5 lat** | AquaRD, Ayyeka, HWM, Metasphere, Kallipr | Nie tyle „nie kopiujemy", co **nie da się jej skopiować przy obecnym wyborze ESP32-S3 + LTE Cat 1 + transmisja co 60 s**. To wymaga zmiany wszystkich trzech elementów naraz. Decyzja należy do B-01 i B-11, nie do tej analizy. Odnotowujemy jako granicę, nie jako zaległość do nadrobienia w bieżącym sprincie |
| **Prywatna licencjonowana sieć radiowa** | Sensus FlexNet, Itron | Model ekonomiczny wymaga tysięcy punktów na operatora. Nasz klient ma 5–15 |
| **Certyfikacja ISO 27001 teraz** | UniCloud, Inventia | Koszt niewspółmierny do skali kilku prototypów. Wartościowe wtedy, gdy zaczniemy przegrywać przetargi z tego powodu — a to jest pytanie do B-01, nie do tej analizy |
| **Własna sieć dystrybutorów i partnerów wdrożeniowych** | Inventia, AquaRD | Model organizacyjny, nie techniczny. Poza zakresem tego dokumentu |
| **Adopcja Golioth / Blues / Telit jako platformy** | — | Uzasadnienie w [§7.2](#72-odpowiedź-na-pytanie-briefu): koszt migracji warstwy transportowej lub wymiany modemu przewyższa dziś koszt własnej implementacji OTA, a dochodzi zależność w ścieżce krytycznej urządzenia |

---

## 10. Lista konkretnych zmian do rozważenia w naszej architekturze

Format: **co → gdzie w kodzie → dlaczego → z którego wymiaru wynika**. To jest lista do przekształcenia w zadania, nie plan wdrożenia — kolejność wynika z zależności technicznych, nie z priorytetu biznesowego.

### 10.1. Firmware

| # | Zmiana | Pliki | Wynika z |
|---|---|---|---|
| F-1 | **Bufor telemetrii w pamięci nieulotnej.** `windows_buffer_` jako warstwa nad NVS/flash zamiast `std::vector` w RAM, z wznawianiem po resecie i retencją liczoną w godzinach | [`TelemetryPayload.h:43`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L43), [`TelemetryPayload.cpp`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp) | wym. 5 |
| F-2 | **Rozdzielenie interwału próbkowania od transmisyjnego** i wyprowadzenie obu z konfiguracji runtime zamiast `const` | [`Config.h`](../../firmware/include/Config.h) (`SAMPLE_INTERVAL_MS`), [`TelemetryPayload.h`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) (`WINDOWS_PER_BATCH`) | wym. 5, 6 |
| F-3 | **Klasa progu z histerezą i deadbandem** implementująca ocenę wartości z jednego kanału, wyzwalająca natychmiastową wysyłkę | nowa biblioteka w `firmware/lib/`, integracja w [`main.cpp`](../../firmware/src/main.cpp) i `TelemetrySender` | wym. 9, 5 |
| F-4 | **Klient konfiguracji**: po uwierzytelnieniu pobiera konfigurację z backendu, zapisuje w NVS, stosuje przy starcie | nowa biblioteka; wzorzec z [`DeviceAuthClient`](../../firmware/lib/DeviceAuthClient/src/DeviceAuthClient.cpp); przechowywanie jak w [`DeviceIdentity`](../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp) | wym. 6 |
| F-5 | **Sterownik Modbus RTU master przez RS485** jako implementacja `ISensor`, z mapowaniem rejestrów z konfiguracji | `firmware/lib/Sensor/`, zgodnie z [`06_adding_sensors.md`](../technical/firmware/06_adding_sensors.md) | wym. 2 |
| F-6 | **Sterownik wejścia impulsowego** (wodomierz z wyjściem impulsowym) — typ `total_volume` i `flow_rate` już są w [`sensor_registry.yaml`](../../sensor_registry.yaml), brakuje strony firmware | `firmware/lib/Sensor/` | wym. 2 |
| F-7 | **Dokończenie PT-506 (4-20 mA)** — usunięcie danych syntetycznych. Dziś kanał ciśnienia wysyła sinusa, co jest stanem nie do pokazania klientowi | [`TelemetryPayload.cpp`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp), [`01_hardware.md` §5](../technical/firmware/01_hardware.md) | wym. 2 |
| F-8 | **OTA z podpisanym obrazem i rollbackiem** na `esp_ota_ops`, z pobraniem przez HTTPS nad TinyGSM; osobne artefakty dla firmware aplikacji i firmware modemu | nowa biblioteka; [`platformio.ini`](../../firmware/platformio.ini) (tablica partycji) | wym. 7, 11 |
| F-9 | **Secure Boot i Flash Encryption** — włączyć **przed** pierwszym wdrożeniem produkcyjnym, bo po wdrożeniu wymaga fizycznego dostępu do każdego urządzenia | [`platformio.ini`](../../firmware/platformio.ini), [`DeviceIdentity`](../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp) (klucz EC w NVS) | wym. 11 |

### 10.2. Backend

| # | Zmiana | Pliki | Wynika z |
|---|---|---|---|
| B-1 | **Nowy moduł `alarms/`** wg szablonu modułu domenowego: definicje reguł per obiekt, ewaluacja, cykl życia alarmu (wystąpienie → potwierdzenie → komentarz → zamknięcie → fałszywy), propagacja po hierarchii punkt → urządzenie → obiekt → organizacja. Alarm to zmiana biznesowa, więc **podlega audytowi** (inaczej niż ingest telemetrii z `skip_audit=True`) | nowy `backend/app/modules/alarms/`, wzorzec z [`01_backend-architecture.md` §5](../technical/backend/01_backend-architecture.md) | wym. 9 |
| B-2 | **Endpoint konfiguracji urządzenia** — `GET` konfiguracji dla uwierzytelnionego urządzenia + model konfiguracji + panel edycji po stronie operatora | `backend/app/modules/device_identity/` lub nowy submoduł `core_data/`; autoryzacja jak w [`get_current_device`](../../backend/app/modules/telemetry/services/ingest.py) | wym. 6 |
| B-3 | **Polityka retencji telemetrii** — decyzja produktowa + zadanie czyszczące. Dziś `MAX_PACKETS_PER_SERIES = 5000` chroni pojedyncze zapytanie, ale nic nie ogranicza wzrostu tabeli | [`packets.py`](../../backend/app/modules/telemetry/repositories/packets.py), [`04_telemetry_module.md` §3](../technical/backend/04_telemetry_module.md) | wym. 8 |
| B-4 | **Agregaty godzinowe i dobowe** liczone raz, zamiast agregowania surowych pakietów przy każdym otwarciu wykresu | [`queries.py`](../../backend/app/modules/telemetry/repositories/queries.py) | wym. 8 |
| B-5 | **Eksport CSV** szeregu czasowego (UC-05) | `backend/app/modules/telemetry/api/` | wym. 10 |
| B-6 | **Publiczne, wersjonowane API odczytu** z tokenem per organizacja + opublikowany OpenAPI. Płaszczyzna organizacji i kody uprawnień już istnieją, brakuje autoryzacji tokenem zamiast JWT użytkownika | [`01_backend-architecture.md` §7](../technical/backend/01_backend-architecture.md) | wym. 10, 3 |
| B-7 | **Forwarding telemetrii na endpoint klienta** — konfigurowalna kopia pakietów na wskazany URL lub broker MQTT klienta | nowy submoduł w `telemetry/`; wzorzec Kallipr/Ayyeka | wym. 10 |
| B-8 | **Rejestr wersji firmware i przypisanie do kohort urządzeń** — strona serwerowa OTA (F-8) | nowy submoduł w `device_identity/` | wym. 7 |
| B-9 | **Widok floty urządzeń** — dziś brak nawet „puli nieprzypisanych", operator wpisuje numer seryjny ręcznie na podstawie statusu kodu | [`06_device_identity_module.md` §6](../technical/backend/06_device_identity_module.md) | wym. 7 |
| B-10 | **Powiązanie kodu aktywacyjnego z numerem seryjnym** — zamyka lukę „kod może zużyć dowolne urządzenie" i **jednocześnie umożliwia provisioning bez laptopa** | [`services/activation_codes.py`](../../backend/app/modules/device_identity/services/activation_codes.py), [`06_device_identity_module.md` §4](../technical/backend/06_device_identity_module.md) | wym. 4, 11 |

### 10.3. Sprzęt

| # | Zmiana | Odniesienie | Wynika z |
|---|---|---|---|
| H-1 | **Obudowa DIN + zasilacz przemysłowy + ochronnik przepięciowy** na wejściu — minimum, żeby W1 dało się zamontować w szafie hydroforni. Nie wymaga zmiany elektroniki | [`01_hardware.md`](../technical/firmware/01_hardware.md); ścieżka wariantów w B-01 | wym. 1 |
| H-2 | **Transceiver RS485** dla Modbus RTU (F-5) — kilkanaście złotych, odblokowuje cały wymiar 2 | [`01_hardware.md`](../technical/firmware/01_hardware.md), [`Config.h`](../../firmware/include/Config.h) | wym. 2 |
| H-3 | **Rozstrzygnięcie klasy urządzenia** — czy idziemy w „sieciowe, obiektowe" (obecna trajektoria) czy „bateryjne IP68" (wymaga LTE-M/NB-IoT + rzadszej transmisji + deep sleep). **To jest decyzja architektoniczna, nie ulepszenie** | wejście do B-01 i B-11 | wym. 1, 5 |
| H-4 | **Weryfikacja zworek J2 i J_APWK** na module KAmod — dziś status „do zweryfikowania fizycznie", a od tego zależy poprawność sekwencji power-on modemu | [`01_hardware.md` §7](../technical/firmware/01_hardware.md) | wym. 1 |

### 10.4. Zależności między zmianami

```
H-2 ──► F-5 (Modbus)
F-4 ──► F-2 (interwały z konfiguracji)   B-2 ──► F-4
F-3 ──► F-1 (transmisja spontaniczna ma sens, gdy bufor przetrwa reset)
B-1 ──► F-3 (progi na urządzeniu to wyzwalacz; pełna logika w backendzie)
F-8 ──► B-8 (OTA wymaga rejestru wersji po stronie serwera)
F-9 przed pierwszym wdrożeniem produkcyjnym; po wdrożeniu koszt rośnie skokowo
B-3 ──► B-4 (retencja to decyzja, agregaty to jej konsekwencja)
```

---

## 11. Korekty do istniejących analiz

Zgodnie z briefem: rzeczy znalezione przy okazji, które korygują istniejącą dokumentację. **Nie przepisujemy tych dokumentów — wskazujemy rozbieżności.**

| # | Gdzie | Co jest napisane | Co ustalono | Waga |
|---|---|---|---|---|
| K-1 | [`CONTEXT.md`](../business/CONTEXT.md), hasło „Bufor lokalny" | „Pamięć gateway'a (flash, SD card)… Minimalna retencja: 72 godziny" | Bufor jest w RAM (`std::vector`), pojemność ~12 minut, tracony przy resecie | **Wysoka** — słownik domenowy opisuje właściwość produktu, której produkt nie ma |
| K-2 | [`CONTEXT.md`](../business/CONTEXT.md) („Neutralność sprzętowa") oraz [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md) pkt 2 | „Obsługujemy najpopularniejsze interfejsy (Modbus RTU, 4-20 mA)"; ADR-0002 opisuje proces „jeśli interfejs się pokrywa z tym, co obsługujemy (Modbus RTU, 4-20 mA, impulsy licznikowe)… procesujemy normalnie" | Modbus RTU nie jest obsługiwany wcale; impulsy nie są obsługiwane wcale; 4-20 mA jest w wersji draft z danymi syntetycznymi. Realnie obsługiwany jest jeden interfejs: SPI/MAX31865 dla PT100 | **Wysoka** — proces wdrożenia z ADR-0002 opiera się na zdolności, której nie ma; każda inwentaryzacja obiektu skończy się dziś decyzją „wymaga custom pracy" |
| K-3 | [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md) i `CONTEXT.md`, „Profil urządzenia" | Konfiguracja z mapowaniem rejestrów i skalowaniem, stosowana bez zmian firmware'u | Nie istnieje żadna implementacja; cała konfiguracja jest compile-time | **Wysoka** — obietnica produktowa bez pokrycia |
| K-4 | [`04_telemetry_module.md` §5](../technical/backend/04_telemetry_module.md) | Auto-provisioning sprawdza typ „w katalogu (`point_types.yaml`)" | Pliku `point_types.yaml` nie ma w repozytorium; katalogiem jest [`sensor_registry.yaml`](../../sensor_registry.yaml) | Niska — literówka w nazwie pliku, myląca przy nawigacji |
| K-5 | [`01_briefy_dla_agentow.md`](../plan/01_briefy_dla_agentow.md), B-04 pkt 6 | „prebuild hook, który miał tego pilnować, jest wyłączony ([`platformio.ini`](../../firmware/platformio.ini))" | Hook **jest aktywny**: `extra_scripts = scripts/prebuild.py` w linii 7, bez zakomentowania | Średnia — B-04 wyszedłby z fałszywej przesłanki |
| K-6 | [`01_plan_biznesowy.md` §5.2](../business/01_plan_biznesowy.md), macierz porównawcza | Kallipr opisany jako „zagraniczny wzorzec" w kategorii „przemysłowe IoT i device management" | Trafne, ale niepełne: najciekawszy technicznie element Kallipr to **rozdział płaszczyzny danych od płaszczyzny zarządzania** (dane do brokera klienta, zarządzanie w Kloud), a nie sam device management | Niska — uzupełnienie, nie korekta |
| K-7 | [`01_plan_biznesowy.md` §5.2](../business/01_plan_biznesowy.md), lista konkurentów | Lista polskich konkurentów nie zawiera **TEL-STER (TelWin SCADA)** | TEL-STER oferuje TelWin SCADA dla wod-kan z ponad 100 modułami komunikacyjnymi (DNP3, OPC UA), z integracją m.in. z AquaRD **[mkt]**. Nie ma publicznej oferty SaaS dla małych gmin, więc nie jest bezpośrednim konkurentem — ale jest realnym graczem w segmencie i warto go mieć na mapie | Niska — do rozważenia przy następnej aktualizacji §5.2 |
| K-8 | — | — | **Metasphere i Ovarro to dwie różne firmy.** Ovarro powstało w marcu 2021 z połączenia Servelec Technologies i Primayer. Point Orange jest produktem Metasphere. Łatwo je pomylić, bo obie sprzedają RTU dla wod-kan w UK przez częściowo tych samych dystrybutorów | Informacyjna — zapisane, żeby błąd nie wszedł do żadnego dokumentu |

---

## 12. Luki informacyjne — czego nie udało się ustalić

Zgodnie z metodą briefu: tam, gdzie informacji nie ma publicznie, piszemy „nieujawnione", nie zgadujemy. Poniżej rzeczy, których brak ma znaczenie dla wniosków.

| Czego nie ustalono | Kogo dotyczy | Dlaczego to blokuje | Jak to zdobyć |
|---|---|---|---|
| **Format payloadu i protokół aplikacyjny do chmury** | Inventia (poza faktem MQTT w MT-331), AquaRD, Hawle, NIVUS, HWM | Wymiar 3 i 5 oparte są dla tych podmiotów na strategii transmisji, nie na strukturze wiadomości | Dokumentacja integracyjna dostępna po zakupie lub dla partnerów |
| **Model retencji i baza danych po stronie chmury** | **wszyscy badani bez wyjątku** | Wymiar 8 nie ma dla konkurencji żadnego twardego punktu odniesienia — jedyne dane pochodzą z ThingsBoard (open source) | Praktycznie niedostępne publicznie |
| **Mechanizm provisioningu i tożsamości urządzenia** | Kallipr, Ayyeka, HWM, Metasphere, NIVUS, AquaRD | Wymiar 4 porównuje nas głównie z UniCloud i Inventią, bo tylko oni to opisują | Dokumentacja dla integratorów |
| **Interfejsy elektryczne urządzenia** | **Hawle.live** — kompletny brak | Hawle nie da się rzetelnie ocenić w wymiarze 2 | Kontakt z producentem (poza zakresem: brief zakazuje rejestracji na dema) |
| **Polityka ujawniania podatności, security advisories, wyniki pen-testów** | **wszyscy badani bez wyjątku** | To luka całej branży, nie tylko nasza — i jednocześnie tania okazja do wyróżnienia się | — |
| **Rzeczywiste ceny sprzętu** | większość; publiczne tylko UniCloud (router ~2 000 zł, abonament 1–3 tys. zł/rok/obiekt) i USR-DR154-E z briefu B-01 | Porównanie kosztowe wariantów należy do B-01 i B-10, nie do tej analizy | Zapytania ofertowe |
| **Pełna specyfikacja WITS-IoT** | standard WITS PSA | Rekomendacja „użyj semantyki WITS-IoT" opiera się na opisie funkcji i architektury standardu, nie na przeczytanym dokumencie specyfikacji | WITS PSA — warunki dostępu do specyfikacji do sprawdzenia przed podjęciem decyzji |
| **Dokumentacja Inventia DataPortal** | Inventia | Podręcznik i dokumentacja są za loginem; ocena platformy Inventii opiera się na materiałach produktowych | Konto testowe (Inventia oferuje test funkcjonalności — poza zakresem tego briefu) |

---

## 13. Źródła

Wszystkie odwiedzone 4 września 2026.

### Polska

- Inventia — MT-101, opis modułu i specyfikacja: https://inventia.online/mt-101-telemetry-module-for-on-line-monitoring-and-local-control/
- Inventia — MT-101, instrukcja użytkownika (PDF): https://inventia.online/wp-content/uploads/2020/04/MT-101-telemetry-module-for-on-line-monitoring-and-local-control.pdf
- Inventia — MT-331: https://inventia.online/mt-331-telemetry-module-2/
- Inventia — MQTT w modułach MT-331: https://inventia.online/news/mqtt-protocol-in-mt-331-telemetry-modules/
- Inventia — strona główna, rodzina produktów i technologie: https://inventia.online/
- Inventia — cyberodporna telemetria dla wod-kan (ISO 9001, ISO/IEC 27001): https://www.inventia.pl/baza-wiedzy-telemetron-1-2026-wydanie-o-cyberodpornej-telemetrii-dla-branzy-wod-kan/
- Inventia — rozwiązania WOD-KAN: https://www.inventia.pl/wod-kan/
- DataPortal — podręcznik (dostęp po zalogowaniu): https://dataportal.online/pl/tutorial/podrecznik-dataportalu
- AquaRD — CellBOX H4: https://aquard.pl/cellbox-h4/
- AquaRD — HydraNet Expert: https://aquard.pl/hydranet-expert/
- AquaRD — HydraNet WMR: https://aquard.pl/hydranet-wmr/
- AquaRD — urządzenia CellBOX: https://aquard.pl/urzadzenia/
- Unitronics — UniCloud, security fundamentals: https://unitronics.cloud/security-fundamentals/
- Unitronics — UniCloud, funkcje: https://unitronics.cloud/functions/
- Elmark — UniCloud dla wod-kan: https://smart.elmark.com.pl/uni/umc/branze/wod-kan
- Hawle — Hawle.live (PL): https://www.hawle.com/pl/dla-klienta/serwis-hawle/hawle-live
- Hawle Service — Hawle.live BOX (DE), interwał transmisji i alarmy: https://www.hawle-service.at/services/hawle-live/hawle-live-box/
- AIUT — WaterPrime: https://waterprime.eu/
- TEL-STER — produkty TelWin SCADA: https://www.telwin.pl/index.php/8-produkty

### Świat

- Kallipr — wsparcie i specyfikacje (w tym MQTT): https://kallipr.com/support/
- Kallipr — Captis Series 1: https://kallipr.com/product/captis-series-1/
- Kallipr — Captis S2: https://kallipr.com/product/captis-s2-range/
- Cumulocity Ecosystem — certyfikacja Captis Pulse 1.2 (MQTT SmartREST 2.0, Firmware Management): https://ecosystem.cumulocity.com/product/captis-pulse-1-2/
- Ayyeka — specyfikacje urządzeń (Wavelet V2, Wavelet 4R): https://www.ayyeka.com/en/knowledge/device-specifications
- Ayyeka — platforma Field Assets Intelligence i FAI Lite: https://www.ayyeka.com/fai
- HWM — MultiLog LX2: https://www.hwmglobal.com/products/multilog-lx2/
- HWM — DataGate, opis serwera danych (PDF): https://tmgroup.com.eg/wp-content/uploads/2022/05/HWM-DataGate.pdf
- HWM — DataGate2, instrukcja dla użytkowników i administratorów (PDF): https://www.hwmglobal.com/uploads/manuals/DataGate2/MAN-130-0015-A%20DataGate2%20Introduction%20for%20Users%20and%20Administrators.pdf
- Metasphere — Point Orange IoT RTU: https://metasphere.co.uk/products/point-orange/
- Ovarro — Kingfisher RTU: https://ovarro.com/en/global/solutions/monitoring--control-devices/remote-telemetry-units-rtus-from-ovarro/2/kingfisher/
- Ovarro — powstanie marki (Servelec Technologies + Primayer, 2021): https://smartwatermagazine.com/news/servelec-technologies/ovarro-servelec-technologies-and-primayer-unite-under-one-brand-and-one
- NIVUS — NivuLink Micro II: https://www.nivus.com/en/products-solutions/data/transmission-and-telecontrol-systems/self-sufficient-data-logger/nivulink-micro-ii
- NIVUS — portal danych pomiarowych (D2W, WebPortal): https://www.nivus.com/en/products-solutions/data/software-solutions/measurement-data-portal
- Xylem/Sensus — FlexNet dla wody (podstawa odrzucenia): https://www.xylem.com/en-us/solutions/communication-networks/flexnet-for-water/

### Standardy i platformy

- WITS Protocol Standards Association: https://www.witsprotocol.org/
- WITS-IoT — publikacja wersji 1.0 (październik 2018): https://www.witsprotocol.org/16-oct-2018-wits-iot-protocol-published-at-version-1-0/
- WITS — opis obu wariantów i governance: https://en.wikipedia.org/wiki/Worldwide_Industrial_Telemetry_Standards
- Golioth — dokumentacja OTA (packages, artifacts, deployments, cohorts): https://docs.golioth.io/device-management/ota/
- Golioth — uwierzytelnianie certyfikatem: https://docs.golioth.io/device-management/authentication/certificate-auth/
- Blues — Notecard Outboard Firmware Update: https://dev.blues.io/notehub/host-firmware-updates/notecard-outboard-firmware-update/
- Blues — Notehub: https://blues.com/notehub/
- balena — wspierane komputery jednopłytkowe (podstawa odrzucenia dla ESP32): https://docs.balena.io/reference/hardware/versioning
- balena — zgłoszenie użytkowników o wsparcie dla ESP32: https://forums.balena.io/t/add-support-for-arduino-m5stack-expressif-esp32/373383
- Telit — getting started z OneEdge: https://docs.devicewise.com/Content/GettingStarted/Getting-Started-with-Oneedge.htm
- Telit — LwM2M w OneEdge: https://www.telit.com/blog/data-management-lwm2m-oneedge/
- ThingsBoard — czym jest ThingsBoard (architektura, provisioning, rule engine, bazy): https://thingsboard.io/docs/getting-started-guides/what-is-thingsboard/
- CERT Polska — zgłaszanie i obsługa podatności (CVD): https://cert.pl/cvd/

### Repozytorium (punkt odniesienia)

- [`docs/business/CONTEXT.md`](../business/CONTEXT.md), [`docs/business/01_plan_biznesowy.md`](../business/01_plan_biznesowy.md), [`docs/business/adr/0002-pragmatic-integration-strategy.md`](../business/adr/0002-pragmatic-integration-strategy.md)
- [`docs/technical/backend/01_backend-architecture.md`](../technical/backend/01_backend-architecture.md), [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md), [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md)
- [`docs/technical/firmware/01_hardware.md`](../technical/firmware/01_hardware.md), [`06_adding_sensors.md`](../technical/firmware/06_adding_sensors.md)
- [`firmware/include/Config.h`](../../firmware/include/Config.h), [`firmware/platformio.ini`](../../firmware/platformio.ini), [`firmware/lib/TelemetryPayload/`](../../firmware/lib/TelemetryPayload/), [`sensor_registry.yaml`](../../sensor_registry.yaml)
