# Testy firmware — pokrycie, warstwa testowalna, weryfikacja sprzętowa

> Stan: **do weryfikacji na sprzęcie** — testy `native` przechodzą, ale zmiany dotykają
> warstwy komunikacyjnej, której `native` z definicji nie sprawdza. Lista rzeczy do
> przejścia na płytce jest w [§8](#8-lista-zmian-do-weryfikacji-na-sprzęcie).

Dokument opisuje: co faktycznie było pokryte testami przed zmianą, jak zaprojektowana
jest warstwa testowalna, jak uruchomić testy i co pozostaje poza ich zasięgiem.

---

## 1. Stan wyjściowy: testy nie uruchamiały się wcale

Repozytorium miało `env:native` z googletest i 5 plików w `firmware/test/`. **Żaden z nich
nie kompilował się**, więc suite nigdy nie przeszedł — a skoro nie przechodził, nikt nie
zauważył, że asercje w środku też są błędne.

Dowód (`pio test -e native` na stanie przed zmianą):

| Plik | Powód, dla którego nie kompilował się |
|---|---|
| `test_isensor_pt100.cpp` | `Adafruit_MAX31865.h` niedostępne na `native`; stała `POINT_TYPE_TEMPERATURE` **nie istnieje w żadnym pliku repozytorium** |
| `test_logger.cpp` | `Logger.h` → `Arduino.h`, brak warstwy zgodności dla hosta |
| `test_telemetry_pt100.cpp` | `ArduinoJson.h` nie było w `lib_deps` środowiska `native`; `EXPECT_THAT`/`HasSubstr` bez `#include <gmock/gmock.h>` |
| `test_timestamp_regression.cpp` | jw. (gmock) |
| `test_timesync.cpp` | jw. (gmock) |

Do tego:

- **`test_ignore_pattern` nie jest opcją PlatformIO.** Konfiguracja zawierała
  `test_ignore_pattern = *_disabled.cpp`; PlatformIO wypisywał
  `Warning! Ignore unknown configuration option` i ignorował wpis. Opcja została
  usunięta, a nie przemianowana: `test_ignore` filtruje **nazwy zestawów testów**
  (katalogi `test_*`), a nie wzorce plików, więc pierwotnej intencji nie da się nim
  wyrazić. Żaden plik `*_disabled.cpp` i tak w repozytorium nie istnieje.
- **Brak `main()`.** Żaden plik nie dostarczał punktu wejścia →
  `undefined reference to 'main'`. Dodany `test/test_main.cpp` zakłada, że pakiet
  `google/googletest` **nie** linkuje `gtest_main` (tak jak w oficjalnym przykładzie
  PlatformIO). Założenia nie dało się zweryfikować w środowisku bez dostępu do
  rejestru — patrz §10.1.
- **Testy sprawdzały kopie kodu, nie kod.** `test_timesync.cpp` i
  `test_timestamp_regression.cpp` miały własne, wklejone implementacje `formatIso8601`
  i asertowały na nich. `test_telemetry_pt100.cpp` budował JSON ręcznie zamiast wołać
  `TelemetryPayload::build()`. Taki test przechodzi także wtedy, gdy firmware jest zepsuty.
- **Asercje były wprost fałszywe.** `test_timesync.cpp` oczekiwał, że znacznik
  `1786419922123` to `2026-08-10`; w rzeczywistości to `2026-08-11T03:45:22Z`. Test nigdy
  nie przeszedł, bo nigdy się nie skompilował.
- **Testy bez treści.** `test_isensor_pt100.cpp` kończył się `EXPECT_TRUE(true)` w dwóch
  przypadkach i komentarzem „just verify it doesn't crash".

**Wniosek:** realne pokrycie firmware przed tą zmianą wynosiło **zero bibliotek**, nie pięć.

Wszystkie pięć plików zostało **przepisane, a nie skasowane** — nazwy zostają, zmienia się
przedmiot testu:

| Plik | Było | Jest |
|---|---|---|
| `test_isensor_pt100.cpp` | `EXPECT_TRUE(true)`, nieistniejąca stała | prawdziwy `PT100Sensor` na atrapie MAX31865 (11) |
| `test_logger.cpp` | „czy makro się kompiluje" | format wpisu i filtrowanie poziomów na przechwyconym wyjściu (6) |
| `test_telemetry_pt100.cpp` | kopia równania CVD + ręcznie sklejany JSON | integracja `PT100Sensor` → `TelemetryPayload` (10) |
| `test_timestamp_regression.cpp` | kopia `formatIso8601` | regresja 1970 na prawdziwym `TelemetryPayload` i `TelemetrySender` (7) |
| `test_timesync.cpp` | kopia `formatIso8601`, błędna asercja daty | kontrakt szwu `IClock`, który zastąpił statyczny `TimeSync` (7) |

### Zepsuty hook `prebuild.py`

Brief wymieniał to jako osobny punkt; przyczyny były trzy, wszystkie prowadzące do tego,
że hook nigdy nie zadziałał w buildzie:

1. `validate()` używało ścieżek względnych (`Path("firmware/include/SensorRegistry.h")`),
   a PlatformIO uruchamia hooki z katalogu `firmware/` → `FileNotFoundError`.
2. `Path(__file__)` — SCons wykonuje `extra_scripts` przez `exec()` **bez** `__file__`,
   więc skrypt wywalał się na `NameError` przy samym ładowaniu środowiska.
3. `AddPreAction("$BUILD_DIR/firmware.elf")` wiąże hook z celem, który istnieje tylko
   w buildzie ESP32. Dla `env:native` celem jest `program`, więc hook nie odpalał się nigdy.

---

## 2. Inwentaryzacja bibliotek

Kolumna „ryzyko w terenie" opisuje, co się dzieje, gdy moduł zawiedzie u klienta.
Kolejność pisania testów wynikała z niej, nie z łatwości implementacji.

| # | Biblioteka | Odpowiada za | Zależność sprzętowa | Ryzyko w terenie | Testy `native` |
|---|---|---|---|---|---|
| 1 | `TelemetryPayload` | bufor okien, budowa JSON, bufor błędów | brak | **Krytyczne** — ciche gubienie pomiarów, pakiety odrzucane przez backend | ✅ 30 (`test_telemetry_payload`, `test_timestamp_regression`) |
| 2 | `TelemetrySender` | pętla wysyłki, retry, potwierdzanie | przez interfejsy | **Krytyczne** — brak danych albo duplikaty okien | ✅ 31 (`test_telemetry_sender` + 3 parametryzowane, `test_timesync`, `test_millis_rollover`) |
| 3 | `DeviceAuthClient` | challenge/verify, ważność tokenu | przez interfejsy | **Krytyczne** — urządzenie milknie bez żadnego sygnału | ✅ 26 (`test_device_auth_client`, `test_millis_rollover`) |
| 4 | `EnrollmentClient` | kod aktywacyjny, redeem | przez interfejsy | **Wysokie** — nie da się wdrożyć urządzenia; backoff chroni transfer SIM | ✅ 25 (`test_enrollment_client` + 3 parametryzowane, `test_millis_rollover`) |
| 5 | `Watchdog` | eskalacja przy zawieszeniu | przez interfejsy | **Wysokie** — martwe urządzenie albo pętla restartów | ✅ 13 (`test_watchdog`, `test_millis_rollover`) |
| 6 | `ModemLink` | podniesienie i utrzymanie LTE | TinyGSM + UART | **Wysokie** — brak łącza; pętle bez własnego limitu czasu | ✅ 15 (`test_modem_link`, atrapa nagłówka TinyGSM) |
| 7 | `ModemPower` | PWRKEY/RESET modemu | GPIO | **Wysokie** — jedyna droga wyjścia z zawieszonego A7670E | ✅ 6 (`test_modem_power`, zapis zdarzeń GPIO) |
| 8 | `Sensor` (`ISensor`, `PT100Sensor`) | odczyt MAX31865 → `SensorReading` | SPI + MAX31865 | **Średnie** — błędne wartości albo brak zgłoszenia awarii | ✅ 21 (`test_isensor_pt100`, `test_telemetry_pt100`) |
| 9 | `Logger` | jedyny kanał diagnostyczny | `Serial` | **Średnie** — bez logów diagnostyka zdalna nie istnieje | ✅ 6 (`test_logger`) |
| 10 | `TelemetryHttpClient` | HTTPS przez TinyGSM | TinyGSM + ArduinoHttpClient | **Krytyczne** | ❌ nietestowalne na hoście — zastąpione `IHttpClient` |
| 11 | `DeviceIdentity` | SN, klucz ECDSA, sesja | NVS (`Preferences`) + mbedTLS | **Krytyczne** | ❌ nietestowalne na hoście — zastąpione `IDeviceIdentity` |
| 12 | `TimeSync` | czas UTC z sieci | TinyGSM, pamięć RTC | **Krytyczne** — bez czasu wszystkie znaczniki są z 1970 | ❌ nietestowalne — zastąpione `IClock` |
| 13 | `StatusLed` | sygnalizacja stanu | NeoPixel | **Niskie** | ❌ nietestowalne — zastąpione `IStatusLed` |
| 14 | `Interfaces` (nowa) | abstrakcje (porty) | brak | — | nagłówkowa, bez własnej logiki |

Pokrycie: **9 z 13 istniejących bibliotek** ma testy na `native`. Cztery pozostałe są
z definicji sprzętowe; ich rolą po tej zmianie jest bycie *implementacją* interfejsu,
a nie miejscem, gdzie żyje logika.

---

## 3. Warstwa testowalna — projekt i uzasadnienie

### 3.1 Zasada

Każdy wprowadzony interfejs musi obsługiwać **co najmniej jeden konkretny test**.
Interfejs, który niczego nie odblokowuje, jest kosztem bez zwrotu — dlatego poniżej
przy każdym stoi lista modułów, które dzięki niemu dało się przetestować.

### 3.2 Wprowadzone interfejsy (`firmware/lib/Interfaces/src/`)

| Interfejs | Implementacja produkcyjna | Odblokowuje testy |
|---|---|---|
| `IHttpClient` (+ `HttpTypes.h`) | `TelemetryHttpClient` | `TelemetrySender`, `DeviceAuthClient`, `EnrollmentClient` |
| `IDeviceIdentity` | `DeviceIdentity` | `TelemetrySender`, `DeviceAuthClient`, `EnrollmentClient` |
| `IClock` | `SystemClock` (nad `TimeSync`) | `TelemetrySender`, `DeviceAuthClient` |
| `IModemLink` | `ModemLink` | `TelemetrySender`, `Watchdog` |
| `IModemPower` | `ModemPower` | `Watchdog` |
| `IStatusLed` | `StatusLed` | `TelemetrySender` |
| `ISystemControl` | `EspSystemControl` | `Watchdog` (restart i licznik RTC bez restartowania testu) |
| `ITelemetryHealth` | `TelemetrySender` | `Watchdog` (wąski szew — pełna zależność wciągnęłaby cały stos wysyłkowy) |

Trzy decyzje projektowe warte odnotowania:

1. **`IModemLink` nie wystawia `TinyGsm&`.** Surowy uchwyt modemu potrzebny jest tylko
   `TelemetryHttpClient` (klient TLS) i `TimeSync` (czas sieciowy) — obie te klasy trzymają
   konkretny `ModemLink`. Wystawienie `TinyGsm` na interfejsie zniszczyłoby całą korzyść.
2. **Dekodowanie challenge przeniesione za `IDeviceIdentity`.** `DeviceAuthClient` wołał
   `DeviceIdentity::decodeBase64Url()` (statyk na mbedTLS), przez co był nierozerwalnie
   związany z kryptografią. Zastąpione przez `signChallengeBase64(challenge)`: klient
   odpowiada za *przebieg* wymiany, nie za kodowanie nonce'a.
3. **Adaptery ESP32 (`SystemClock`, `EspSystemControl`) leżą w `src/RuntimeAdapters.h`,
   nie w `lib/`.** Należą do punktu złożenia aplikacji, a PlatformIO nie kompiluje `src/`
   przy `pio test` — dzięki temu nie mogą przypadkiem wejść do buildu testów.

### 3.3 Szwy na poziomie nagłówka (bez zmian w kodzie produkcyjnym)

Trzy zależności są wstrzykiwane przez podmianę nagłówka, a nie interfejs — bo obiekty
powstają wewnątrz testowanej klasy i nie da się ich przekazać konstruktorem:

| Atrapa | Zastępuje | Sterowanie z testu |
|---|---|---|
| `test/support/TinyGsmClient.h` | TinyGSM w `ModemLink` | `NativeModemState` |
| `test/support/Adafruit_MAX31865.h` | sterownik RTD w `PT100Sensor` | `NativeMax31865State` |
| `test/support/HardwareSerial.h`, `SPI.h` | UART i SPI | pola publiczne obiektu |

Zysk: `ModemLink.cpp` i `PT100Sensor.cpp` są testowane **w oryginalnej postaci**, bez
refaktoru pod testy. Koszt: atrapa może rozjechać się z prawdziwą biblioteką — dlatego
sekwencja modemu jest na liście weryfikacji sprzętowej (§8).

### 3.4 Warstwa zgodności `native` (`firmware/test/support/`)

Nagłówkowa (bez plików `.cpp`), widoczna wyłącznie przez `-Itest/support` w `[env:native]`.
Build ESP32 jest nią nietknięty.

`Arduino.h` daje trzy rzeczy sterowalne z testu:

- **`NativeClock`** — `millis()` nie płynie samo; `delay()` przesuwa zegar. Dzięki temu
  pętle `while (millis() - start < X)` w kodzie produkcyjnym kończą się, zamiast wisieć,
  i można asertować na *upływie czasu* (np. że impuls RESET trwa ≥ 2 s).
- **`NativeSerial`** — `Serial.printf()` pisze do bufora, więc test może sprawdzić treść
  logu. `FIRMWARE_TEST_ECHO_LOGS=1` przełącza echo na stdout przy debugowaniu.
- **`NativeGpio`** — `pinMode()`/`digitalWrite()` zapisują sekwencję zdarzeń wraz ze
  znacznikiem czasu; na tym opiera się test `ModemPower`.

Atrapy interfejsów są w `test/support/Fakes.h`, atrapa czujnika w `FakeSensor.h`.

---

## 4. Test kontraktowy payloadu

### 4.1 Problem

Firmware buduje JSON, backend waliduje go schematem `MeasurementPacketRequest`
(`v=2`, `extra="forbid"`). Rozjazd nie dawał żadnego sygnału po stronie urządzenia —
wychodził jako 422 na produkcji, **na całym pakiecie**, bo pydantic odrzuca go w całości.

### 4.2 Znaleziony rozjazd (naprawiony)

`TelemetryPayload::build()` przy nieudanym odczycie czujnika dodawał:

```cpp
addError("SENSOR_FAULT", sensor->pointId(), "error", "Read failed");
```

Dwa błędy naraz:

- `"SENSOR_FAULT"` **nie istnieje** w `sensor_registry.yaml` (są `SENSOR_READ_FAILED`
  i `SENSOR_FAULT_HW`), a backend waliduje kod rejestrem;
- `"error"` **nie należy** do `Literal["info", "warning", "critical"]`.

Skutek w terenie: **jedna awaria czujnika unieważniała każdy kolejny pakiet** — łącznie
z danymi z czujników, które działały. Do tego `build()` jest wołany przy każdej próbie
wysyłki, więc przy trwałej awarii bufor błędów zapełniał się kopiami tego samego wpisu.

Naprawa:

- kod błędu bierze się z `SensorReading::errorCode` (pole istniało, ale było ignorowane),
  z `SENSOR_READ_FAILED` jako wartością domyślną;
- `severity` **nie jest już podawana przez wywołującego** — `addError()` odczytuje ją
  z rejestru przez nową funkcję `SensorRegistry::severityForErrorCode()`. To eliminuje
  całą klasę rozjazdów: firmware nie ma własnej kopii poziomów;
- kod spoza rejestru jest odrzucany przy dodawaniu, a nie wysyłany;
- `addError()` deduplikuje po parze (kod, punkt).

### 4.3 Mechanizm

```
backend/…/measurement_packet.py
        │  generate_payload_contract.py (AST, tylko stdlib)
        ▼
firmware/test/contract/PayloadContract.h   ← generowany, w .gitignore
        │
        ├─ PayloadValidator.h              ← chodzi po JSON-ie i zwraca listę naruszeń
        ▼
test_payload_contract.cpp                  ← payload z TelemetryPayload::build()
```

Kody błędów **nie są tu powielane** — walidator woła `SensorRegistry::isValidErrorCode()`
i `severityForErrorCode()` z nagłówka generowanego z tego samego `sensor_registry.yaml`,
który backend ładuje w czasie działania.

Generator czyta schemat **statycznie (AST)**, a nie przez import. Import
`MeasurementPacketRequest` wciąga cały pakiet `app` (SQLAlchemy, pydantic, składnia
Pythona ≥ 3.14) — uzależnienie buildu testów firmware od środowiska backendu byłoby złym
zamianą. Ceną jest ryzyko, że generator źle odczyta zrefaktorowany schemat; dlatego
**przerywa z błędem**, gdy plik nie wygląda jak oczekiwany (brak klasy, brak
`extra="forbid"`, `severity` przestaje być `Literal`, zniknięcie `model_validator`).
Cichy, pusty kontrakt byłby gorszy niż jego brak.

### 4.4 Weryfikacja, że test faktycznie łapie rozjazd

Sprawdzone przez celowe zepsucie schematu backendu:

| Zmiana w `measurement_packet.py` | Wynik `pio test -e native` |
|---|---|
| `sent_at` → `transmitted_at` | 6 testów FAILED, komunikat: `$: brak wymaganego klucza 'transmitted_at'` |
| `Literal["info","warning","critical"]` → `Literal["info","warning"]` | 2 testy FAILED, komunikat: `$.errors[0].severity: poziom 'critical' spoza Literal akceptowanego przez backend` |

Po przywróceniu schematu: wszystkie 197 przypadków zielone.

Sam walidator też jest sprawdzony — 14 przypadków w `PayloadContractDetectionTest` podaje
mu celowo zepsute pakiety i wymaga, żeby je odrzucił. Bez tego „pakiet przeszedł walidację"
mogłoby znaczyć po prostu, że walidator niczego nie sprawdza.

---

## 5. Błędy produkcyjne znalezione przez testy

Poza rozjazdem kontraktu z §4.2 praca testowa i przegląd odsłoniły pięć defektów
w kodzie, który jest dziś na urządzeniu, oraz dwa w samym oprzyrządowaniu.
Wszystkie naprawione. Każdy defekt w firmware ma test, który **pada na wersji sprzed
poprawki** — sprawdzone przez tymczasowe cofnięcie zmiany, nie przez samo napisanie
asercji.

### 5.1 Provisioning po Serial nie działał w ogóle

`EnrollmentClient::readSerial()` był pustą funkcją z komentarzem
`// Serial input disabled - migrated away from direct Serial usage`. Ponieważ jest to
**jedyne** wywołanie `processLine()`, cały łańcuch aktywacji był martwy: świeżego
urządzenia nie dało się zaprovisionować, mimo że reszta ścieżki (walidacja kodu,
redeem, backoff) działała poprawnie.

Regresja weszła w commicie `70fb9f3` („Implement ISensor interface and PT100 sensor
class") — implementacja czytająca z `SerialMon` została usunięta razem z zależnością od
makra `SerialMon`, najwyraźniej przy okazji, nie celowo. Poprzednia wersja (`219b608`)
działała i jest opisana w
[`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md) jako
**zweryfikowana na sprzęcie 2026-08-23**.

Naprawa odtwarza odczyt linii z `Serial`, z trzema różnicami wobec wersji z `219b608`:
logowanie idzie przez `Logger` zamiast surowego `SerialMon.print`, kod jest w logu
**zamaskowany** (`maskCode`), a limit długości linii jest nazwaną stałą
`SERIAL_LINE_MAX`. Sześć testów w `test_enrollment_client.cpp` chodzi pełną ścieżką
bajty → `pending_code_`; pięć z nich pada na wypatroszonej wersji.

### 5.2 Przewinięcie `millis()` po ~49,7 dnia pracy

Trzy pętle porównywały czas w postaci, która przestaje działać po przekręceniu licznika
32-bitowego. Gateway w hydroforni ma chodzić miesiącami, więc to nie jest przypadek
teoretyczny.

| Miejsce | Zapis przed | Skutek po przewinięciu |
|---|---|---|
| `TelemetrySender::update()` — próbkowanie | `now >= last_sample_ms_ + interval` | prawa strona przepełnia się; próbkowanie w **każdej** iteracji pętli (co ~10 ms) przez kilkanaście sekund → 12-minutowy bufor okien zapełnia się i zaczyna gubić dane |
| `TelemetrySender::update()` — backoff wysyłki | `now < next_send_attempt_ms_` | termin ponowienia przewija się do małej liczby, `now` jeszcze nie → backoff przestaje obowiązywać, retry przy każdej iteracji |
| `DeviceAuthClient::update()` — dławienie pollingu | `nowMs < next_allowed_poll_ms_` | jw. — wymiana challenge/verify w pętli zamiast co 15 s |
| `EnrollmentClient::attemptRedeem()` — backoff aktywacji | `nowMs < next_allowed_retry_ms_` | jw. — redeem w pętli zamiast co 30 s |

Naprawa: porównania przez różnicę bez znaku (`(now - last) >= interval`,
`(long)(now - next) < 0`). Terminom towarzyszy flaga „termin w ogóle ustawiony", żeby
wartość początkowa `0` nie została po ~24,8 dnia uznana za termin w przyszłości.

`Watchdog::check()` używał już odpornej postaci (`now - lastSuccessMs`) — jest na to
osobny test strażniczy, żeby ktoś tego nie „poprawił".

Sprawdzone: 5 z 6 testów w `test_millis_rollover.cpp` pada po cofnięciu poprawki
(szósty to właśnie strażnik watchdoga, który ma przechodzić w obu wersjach).

### 5.3 Flaga błędu trwałego blokowała watchdoga na zawsze

`TelemetrySender::update()` ustawiał `last_error_was_permanent_` przy 403/409/410, ale
**nie zerował go** na ścieżkach wcześniejszego wyjścia: brak łącza (`ensureConnected()`
false) i brak ważnej sesji. `Watchdog::check()` pomija odzyskiwanie, gdy flaga jest
ustawiona — więc po jednym 409, jeśli potem padło łącze, watchdog przestawał działać
**na stałe**: żadnego resetu modemu, żadnego restartu, urządzenie martwe aż do ręcznego
wyłączenia zasilania.

Naprawa: obie ścieżki zerują flagę, bo brak łącza i odnawianie tokenu to stany
przejściowe, a nie odmowa backendu. Dwa testy, oba padają bez poprawki.

### 5.4 Parser ISO8601 przyjmował daty nieistniejące

Walidacja zakresu dopuszczała `day` do 31 w każdym miesiącu, więc `2026-02-30`
przechodziło i dawało znacznik przesunięty o dwa dni. Skutek: urządzenie uznawałoby
wygasły token za ważny i dostawało 401 przy każdej wysyłce, dopóki różnica sama się nie
wyrówna. Naprawa: dzień sprawdzany względem faktycznej długości miesiąca (z rokiem
przestępnym). `2026-02-29` też jest teraz odrzucane — 2026 nie jest przestępny.

### 5.5 `ensureConnected()` bez strażnika `nullptr`

`ModemLink::testAT()` sprawdzał `if (!modem_)`, a `ensureConnected()` nie — mimo że oba
działają na tym samym wskaźniku, tworzonym dopiero w `init()`. Dziś nieosiągalne
(`TelemetrySender` powstaje po udanym `init()`), ale asymetria zapraszała do awarii przy
pierwszej zmianie kolejności inicjalizacji. Dodany strażnik + test.

### 5.6 Defekty w samym oprzyrządowaniu

Dwa błędy w kodzie, który ma pilnować pozostałych — oba znalezione w przeglądzie:

| Defekt | Skutek | Naprawa |
|---|---|---|
| `generate_payload_contract.py` czytał `Field(..., max_length=128)` jako pole **opcjonalne** (traktował każdy argument pozycyjny jak wartość domyślną; w pydantic `...` oznacza „wymagane") | przepisanie schematu backendu bez zmiany znaczenia przenosiłoby klucze wymagane do `PACKET_OPTIONAL` i test kontraktowy **cicho** przestawałby wykrywać brakujące pole | rozpoznawanie `Ellipsis`; sprawdzone przepisaniem `device_id` na `Field(..., …)` — `PACKET_REQUIRED` pozostaje bez zmian |
| `except NameError: pass` w `prebuild.py` obejmowało całe ciało hooka, nie sam `Import("env")` | literówka w kodzie generacji zamieniała pre-build w cichy no-op, a build szedł dalej na nieaktualnym nagłówku | `except` zawężony do importu; sprawdzone wstrzyknięciem `NameError` — build teraz przerywa |

---

## 6. Uruchamianie

```bash
cd firmware
pio test -e native            # 197 przypadków
pio test -e native -v         # z pełnym wyjściem googletest

FIRMWARE_TEST_ECHO_LOGS=1 pio test -e native -v   # + logi firmware na stdout
```

Hook `pre:scripts/prebuild.py` odpala się w obu środowiskach i przed kompilacją:

1. generuje `firmware/include/SensorRegistry.h` z `sensor_registry.yaml`,
2. sprawdza zgodność wygenerowanego nagłówka z YAML-em,
3. **tylko dla `env:native`** — generuje `firmware/test/contract/PayloadContract.h`
   ze schematu backendu.

Krok 3 nie dotyczy buildu ESP32: kontrakt jest artefaktem testowym i nie trafia do binarki.

Do użycia w CI po stronie backendu:

```bash
python3 firmware/scripts/generate_payload_contract.py --check
```

zwraca kod ≠ 0, gdy zapisany nagłówek rozjechał się ze schematem.

---

## 7. Czego te testy nie sprawdzają

Świadome ograniczenia — warto je znać, zanim ktoś potraktuje zielony suite jako gwarancję:

- **Prawdziwy stos sieciowy.** `IHttpClient` zastępuje TinyGSM + ArduinoHttpClient + TLS.
  Testy mówią, co firmware zrobi z kodem 401; nie mówią, czy handshake TLS przejdzie.
- **NVS i mbedTLS.** `DeviceIdentity` (klucz ECDSA, `Preferences`) nie jest kompilowany
  na hoście. Podpis, zapis klucza i trwałość stanu po restarcie są tylko sprzętowe.
  `FakeDeviceIdentity` powtarza regułę ważności sesji — jeśli zmieni się ona w
  `DeviceIdentity`, atrapa się rozjedzie i testy tego nie zauważą.
- **Serializacja liczb zmiennoprzecinkowych.** Testy asertują na **sparsowanym** JSON-ie,
  nie na jego tekstowej postaci, żeby nie zależeć od formatowania konkretnej wersji
  ArduinoJson.
- **Atrapy TinyGSM i MAX31865 to nie są te biblioteki.** Sprawdzana jest logika
  `ModemLink` i `PT100Sensor`, nie zachowanie sterowników.
- **Zużycie pamięci i czas rzeczywisty.** Zegar na hoście jest sterowany, sterta ogromna.
  Fragmentacja pamięci przy `String` i realne opóźnienia AT wychodzą tylko na płytce.
- **`main.cpp`.** PlatformIO nie kompiluje `src/` przy `pio test`; kolejność inicjalizacji
  w `setup()` pozostaje niepokryta.

---

## 8. Lista zmian do weryfikacji na sprzęcie

Refaktor dotknął kodu, który rozmawia ze sprzętem i siecią. Testy `native` tej warstwy
**nie sprawdzają** — one ją zastępują. Poniżej jest to, co trzeba przejść na płytce
jednym uruchomieniem, z odczytem logów.

### 8.1 Kolejność sprawdzania

| # | Co sprawdzić | Czego dotyczy zmiana | Oczekiwany log / objaw |
|---|---|---|---|
| 1 | **Rozruch i tożsamość** | `DeviceIdentity : IDeviceIdentity` — dodane `override`, nowa metoda `signChallengeBase64()` | `[BOOT] DeviceIdentity initialized`, numer seryjny `WW-…` niezmieniony po restarcie |
| 2 | **Rejestracja w sieci LTE** | `ModemLink : IModemLink`; **nowy strażnik `nullptr` w `ensureConnected()`** | `[NET] Network connected`, `[DATA] GPRS/LTE connected`, `Local IP: …` |
| 3 | **Aktywacja kodem** (urządzenie nieprovisionowane) | **przywrócony odczyt `ACTIVATE` z Serial** (§5.1) + `EnrollmentClient` na `IDeviceIdentity&`/`IHttpClient*` | wpisanie `ACTIVATE <kod>` w monitorze daje `[ENROLL] Odebrano linię: ABCD-****-****`, potem redeem 200/201 i `[BOOT] Provisioning completed`. **To jest najważniejszy punkt listy** — przed poprawką ta ścieżka była martwa |
| 4 | **Challenge/response** | `DeviceAuthClient` bierze `IClock&`; podpis liczony przez `signChallengeBase64()` zamiast `decodeBase64Url()` + `signBase64()` w kliencie | dwa POST-y (`/devices/auth/challenge`, `/devices/auth/verify`), 200, token zapisany |
| 5 | **Walidacja `expires_at`** | **nowa walidacja zakresów** w `parseIso8601ToUnix()` | token z backendu przyjęty; brak `No valid session` w pętli |
| 6 | **Wysłanie pakietu** | `TelemetrySender` bierze `IClock&`, `IHttpClient&`, `IStatusLed&`, `IModemLink&` | `[LOOP] Send OK, seq=…`, backend przyjmuje **200/202, nie 422** |
| 7 | **Pakiet z błędem czujnika** | **zmieniony kontrakt błędów** — kod z rejestru + severity z rejestru | odłącz PT100 → pakiet z `SENSOR_FAULT_HW`/`critical` przyjęty przez backend (wcześniej: 422) |
| 8 | **Restart po watchdogu** | `Watchdog` bierze `ISystemControl&` zamiast wołać `esp_restart()` i ruszać `rtcRestartCounter` wprost | wyjmij antenę na > 5 min → AT, twardy reset modemu, restart; `Restart counter (RTC)` rośnie i **zatrzymuje się na 2** |
| 9 | **Licznik restartów przeżywa restart** | licznik idzie przez `EspSystemControl(rtcRestartCounter)` — referencja do pamięci RTC | po restarcie z pkt. 8 log pokazuje niezerowy licznik, a po udanej wysyłce wraca do 0 |
| 10 | **Sygnalizacja LED** | `StatusLed : IStatusLed` | jedno mignięcie po sukcesie, trzy po błędzie |
| 11 | **Rytm transmisji po dłuższej pracy** | porównania czasu przepisane na różnicę bez znaku (§5.2) | po kilku godzinach pracy odstęp między pakietami nadal ~60 s; brak serii pakietów jeden po drugim |

### 8.2 Ryzyka, na które warto patrzeć

- **Pkt 8 to jedyne miejsce, gdzie sprawdza się `EspSystemControl`.** `ISystemControl`
  jest z definicji nieuruchamialny w testach — restart w teście zabiłby test.
- **Pkt 2 i 6** przechodzą przez atrapy TinyGSM w testach. Jeśli sekwencja AT rozjechała
  się z rzeczywistością, wyjdzie to dopiero tutaj.
- **Pkt 3 i 7 to jedyne zmiany, które zmieniają zachowanie widoczne z zewnątrz** —
  odblokowanie provisioningu i treść wysyłanych błędów. Reszta listy to weryfikacja,
  że refaktor niczego nie zepsuł.
- **Pkt 11 nie da się sprawdzić w rozsądnym czasie na płytce** — przewinięcie `millis()`
  następuje po 49,7 dnia. Testy `native` pokrywają samą arytmetykę; na sprzęcie sprawdza
  się tylko to, że zmiana nie zepsuła normalnego rytmu.

### 8.3 Znalezione, nienaprawione — do decyzji

| Obserwacja | Miejsce | Dlaczego zostawione |
|---|---|---|
| `waitForNetwork()` nie ma własnego opóźnienia w pętli; kończy się tylko dlatego, że TinyGSM blokuje na czas timeoutu. Gdyby kiedyś zaczął zwracać natychmiast, ESP32 kręciłby się w pętli — a `esp_task_wdt_reset()` w środku karmi watchdoga, więc **task WDT by tego nie przerwał** | `ModemLink::waitForNetwork()` | zmiana zachowania pętli sieciowej wykracza poza zakres B-06; test `BrakRejestracjiWSieciKonczyInicjalizacjeNiepowodzeniem` dokumentuje obecną zależność |
| `extern const uint32_t TOKEN_REFRESH_MARGIN_SECONDS;` wewnątrz funkcji, przy już dołączonym `Config.h` | `DeviceIdentity::hasValidSession()` | działa (odwołuje się do tej samej stałej o wiązaniu wewnętrznym), ale jest mylące — kosmetyka |
| `char buffer[30]` w `formatIso8601()` — GCC ostrzega o możliwym obcięciu dla nierealistycznych lat | `TelemetryPayload::formatIso8601()` | `snprintf` obcina bezpiecznie; dla lat 1000–9999 wynik ma 24 znaki |
| **Watchdog nigdy nie eskaluje, dopóki modem odpowiada na AT.** Modem zarejestrowany, ale bez transmisji (np. brak APN, blokada operatora) w nieskończoność zostaje w kroku 0 — nie ma resetu ani restartu, mimo że dane nie wychodzą od godzin | `Watchdog::attemptRecovery()`, krok `recovery_attempts_ == 0` | zachowanie sprzed zmiany, świadomie zachowane; test `ModemOdpowiadaNaATWiecEskalacjaSieNieRozpoczyna` je dokumentuje. Zmiana wymaga decyzji: czy „AT odpowiada" ma wystarczać, żeby uznać łącze za sprawne |
| `WINDOW_DROPPED_BUFFER_FULL` po deduplikacji nie niesie **liczby** porzuconych okien | `TelemetryPayload` | licznik porzuceń należy do diagnostyki urządzenia — zakres **B-08** |

---

## 9. Pliki

| Ścieżka | Rola |
|---|---|
| `firmware/lib/Interfaces/src/` | abstrakcje (porty) — kod produkcyjny |
| `firmware/src/RuntimeAdapters.h` | `SystemClock`, `EspSystemControl` — punkt złożenia |
| `firmware/test/support/` | warstwa zgodności `native` + atrapy (tylko testy) |
| `firmware/test/contract/` | `PayloadContract.h` (generowany) + `PayloadValidator.h` |
| `firmware/test/test_*.cpp` | testy; `test_main.cpp` dostarcza `main()` |
| `firmware/scripts/prebuild.py` | hook: rejestr + kontrakt payloadu |
| `firmware/scripts/generate_payload_contract.py` | generator kontraktu ze schematu backendu |

Powiązane: [01_hardware.md](./01_hardware.md) (mapa pinów użyta w testach `ModemPower`
i `PT100Sensor`), [02_modem_a7670e_communication.md](./02_modem_a7670e_communication.md)
(sekwencja modemu), [06_adding_sensors.md](./06_adding_sensors.md) (rejestr czujników).


---

## 10. Czego nie udało się zweryfikować w tym środowisku

Poniższe punkty wymagają maszyny z dostępem do rejestru PlatformIO albo do fizycznej
płytki. Każdy ma podane: co uruchomić, czego szukać i co zrobić z wynikiem.

### 10.1 Build ESP32 (`pio run -e esp32-s3`) — **priorytet 1**

**Dlaczego nie zrobione:** platforma `espressif32`, TinyGSM, ArduinoHttpClient,
Adafruit NeoPixel i MAX31865 ściągane są z `api.registry.platformio.org`, który w tym
środowisku jest zablokowany przez politykę egress (odpowiedź 403 na CONNECT).

**Co uruchomić:**

```bash
cd firmware
pio run -e esp32-s3
```

**Czego szukać — trzy konkretne ryzyka, w kolejności prawdopodobieństwa:**

1. **Podwójny `main()`.** Jeśli pakiet `google/googletest` jednak linkuje `gtest_main`,
   `pio test -e native` zakończy się `multiple definition of 'main'`.
   *Objaw:* błąd linkera wskazujący `gtest_main.cc` i `test/test_main.cpp`.
   *Naprawa:* usuń `firmware/test/test_main.cpp` (nic poza `main()` w nim nie ma;
   przełącznik `FIRMWARE_TEST_ECHO_LOGS` przenieś do `SetUp()` wybranego testu albo
   porzuć). Dotyczy tylko `env:native`, nie buildu ESP32.
2. **Rozdzielczość biblioteki `Interfaces` przez LDF.** Nowa biblioteka nagłówkowa
   `firmware/lib/Interfaces` jest wciągana przez `#include <IHttpClient.h>` itd.
   *Objaw:* `fatal error: IHttpClient.h: No such file or directory` przy kompilacji
   `TelemetryHttpClient.cpp` lub `TelemetrySender.cpp`.
   *Naprawa:* dodaj `-Ilib/Interfaces/src` do `build_flags` w `[env:esp32-s3]`
   (LDF w trybie `chain` powinien poradzić sobie sam, ale to jest tani zapasowy plan).
3. **`RuntimeAdapters.h` i `esp_restart()`.** `EspSystemControl::restart()` woła
   `esp_restart()` przez `#include <Esp.h>`.
   *Objaw:* `'esp_restart' was not declared in this scope`.
   *Naprawa:* dopisz `#include <esp_system.h>` w `firmware/src/RuntimeAdapters.h`.
   (`main.cpp` wołał `esp_restart()` z tym samym zestawem nagłówków przed zmianą, więc
   to mało prawdopodobne.)

**Co zrobić z wynikiem:** jeśli build przechodzi — dopisz to do nagłówka tego dokumentu
i przejdź do §10.2. Jeśli nie — napraw według powyższego, uruchom `pio test -e native`
(musi dalej dawać 197/197) i dopiero wtedy wgrywaj.

### 10.2 `pio test -e native` na prawdziwych zależnościach — **priorytet 2**

**Dlaczego nie zrobione:** `bblanchon/ArduinoJson` i `google/googletest` też pochodzą
z zablokowanego rejestru. Testy uruchomiono na lokalnej namiastce ArduinoJson (nie jest
częścią repozytorium) i na googletest z pakietu systemowego.

**Co uruchomić:**

```bash
cd firmware
pio test -e native            # oczekiwane: 197/197
```

**Czego szukać:** testy asertują na **sparsowanym** JSON-ie, nie na jego tekstowej
postaci, więc różnice w formatowaniu liczb między wersjami ArduinoJson nie powinny nic
zmienić. Jedyne miejsce dotykające tekstu to
`Pt100PayloadTest.PakietSerializujeSieDoPoprawnegoJson`
(szuka podłańcucha `"type":"temperature"`). Jeśli padnie, to znaczy, że prawdziwe
ArduinoJson wstawia spacje — wtedy popraw asercję na porównanie sparsowanych wartości,
nie zmieniaj firmware.

Osobno sprawdź, czy w wyjściu nie ma ostrzeżenia
`Warning! Ignore unknown configuration option` — po tej zmianie nie powinno go już być.

### 10.3 Weryfikacja na płytce — **priorytet 3**

Pełna lista jest w §8 (11 punktów z oczekiwanymi logami). Kolejność ma znaczenie:
punkt 3 (aktywacja kodem `ACTIVATE`) wymaga **urządzenia bez zakończonego
provisioningu**, więc albo weź świeży egzemplarz, albo najpierw wyczyść przestrzeń NVS
`devid` (`nvs_flash_erase` albo `esptool.py erase_flash`).

Punkt 7 (pakiet z błędem czujnika) wymaga fizycznego odłączenia PT100 — to jedyny
sposób sprawdzenia, że naprawiony kontrakt błędów faktycznie przechodzi przez backend.
Potwierdzeniem jest **200/202 w odpowiedzi, nie 422**.

### 10.4 Test pydantic po stronie backendu — **do rozważenia**

**Dlaczego nie zrobione:** backend wymaga Pythona ≥ 3.14 (używa PEP 695 `class Foo[T]`
i odroczonych adnotacji z PEP 649). W tym środowisku dostępne były 3.10–3.13, więc
`app.modules.telemetry.schemas` nie dało się zaimportować, a testów backendu nie
uruchomiono.

**Co można dołożyć** (nie jest to wymagane przez B-06, ale domyka pętlę): pytest, który
bierze przykładowe pakiety firmware'owe i przepuszcza je przez **prawdziwy**
`MeasurementPacketRequest`. Dziś kontrakt jest odtwarzany statycznie z pliku źródłowego
(§4.3) — dobrze łapie zmiany kształtu, ale nie wykona walidatorów pydantica.

**Jak to zrobić:**

1. Uruchom `pio test -e native` z ustawionym `FIRMWARE_TEST_ECHO_LOGS=1` i wyłów
   z logu linie `[DATA] Payload: {...}` — to są pakiety wyprodukowane przez firmware.
2. Zapisz kilka z nich (typowy, z błędem czujnika, po przepełnieniu bufora) jako
   `backend/tests/fixtures/firmware_payloads.json`.
3. Dodaj `backend/tests/.../test_firmware_payload_contract.py`, który dla każdego
   pakietu robi `MeasurementPacketRequest.model_validate(pakiet)` i wymaga braku
   `ValidationError`.
4. Uruchom `pytest` w `.venv` backendu (Python 3.14).

Efekt: rozjazd łapany z obu stron — od firmware przez `PayloadContract.h`, od backendu
przez prawdziwy schemat.

### 10.5 Czego **nie** trzeba robić

- Nie ma potrzeby uruchamiania Playwrighta ani żadnego narzędzia przeglądarkowego —
  to zadanie nie dotyka frontendu.
- Nie trzeba odtwarzać lokalnej namiastki ArduinoJson: na maszynie z dostępem do
  rejestru `platformio.ini` zaciągnie prawdziwą bibliotekę.
