# Testy firmware — pokrycie, warstwa testowalna, weryfikacja sprzętowa

> Stan: **do weryfikacji na sprzęcie** — testy `native` przechodzą, ale zmiany dotykają
> warstwy komunikacyjnej, której `native` z definicji nie sprawdza. Lista rzeczy do
> przejścia na płytce jest w [§7](#7-lista-zmian-do-weryfikacji-na-sprzęcie).

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
  `Warning! Ignore unknown configuration option`. Właściwa nazwa to `test_ignore`.
- **Brak `main()`.** Pakiet googletest w PlatformIO nie linkuje `gtest_main`, a żaden
  plik go nie dostarczał → `undefined reference to 'main'`.
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
| 2 | `TelemetrySender` | pętla wysyłki, retry, potwierdzanie | przez interfejsy | **Krytyczne** — brak danych albo duplikaty okien | ✅ 27 (`test_telemetry_sender`, + 3 parametryzowane, + `test_timesync`) |
| 3 | `DeviceAuthClient` | challenge/verify, ważność tokenu | przez interfejsy | **Krytyczne** — urządzenie milknie bez żadnego sygnału | ✅ 24 (`test_device_auth_client`) |
| 4 | `EnrollmentClient` | kod aktywacyjny, redeem | przez interfejsy | **Wysokie** — nie da się wdrożyć urządzenia; backoff chroni transfer SIM | ✅ 18 (`test_enrollment_client`, w tym 3 parametryzowane) |
| 5 | `Watchdog` | eskalacja przy zawieszeniu | przez interfejsy | **Wysokie** — martwe urządzenie albo pętla restartów | ✅ 12 (`test_watchdog`) |
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
sekwencja modemu jest na liście weryfikacji sprzętowej (§7).

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

Po przywróceniu schematu: wszystkie 182 przypadki zielone.

Sam walidator też jest sprawdzony — 14 przypadków w `PayloadContractDetectionTest` podaje
mu celowo zepsute pakiety i wymaga, żeby je odrzucił. Bez tego „pakiet przeszedł walidację"
mogłoby znaczyć po prostu, że walidator niczego nie sprawdza.

---

## 5. Uruchamianie

```bash
cd firmware
pio test -e native            # 182 przypadki
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

## 6. Czego te testy nie sprawdzają

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

## 7. Lista zmian do weryfikacji na sprzęcie

Refaktor dotknął kodu, który rozmawia ze sprzętem i siecią. Testy `native` tej warstwy
**nie sprawdzają** — one ją zastępują. Poniżej jest to, co trzeba przejść na płytce
jednym uruchomieniem, z odczytem logów.

### 7.1 Kolejność sprawdzania

| # | Co sprawdzić | Czego dotyczy zmiana | Oczekiwany log / objaw |
|---|---|---|---|
| 1 | **Rozruch i tożsamość** | `DeviceIdentity : IDeviceIdentity` — dodane `override`, nowa metoda `signChallengeBase64()` | `[BOOT] DeviceIdentity initialized`, numer seryjny `WW-…` niezmieniony po restarcie |
| 2 | **Rejestracja w sieci LTE** | `ModemLink : IModemLink`; **nowy strażnik `nullptr` w `ensureConnected()`** | `[NET] Network connected`, `[DATA] GPRS/LTE connected`, `Local IP: …` |
| 3 | **Aktywacja kodem** (urządzenie nieprovisionowane) | `EnrollmentClient` bierze `IDeviceIdentity&` i `IHttpClient*` | redeem kończy się 200/201, `[BOOT] Provisioning completed` |
| 4 | **Challenge/response** | `DeviceAuthClient` bierze `IClock&`; podpis liczony przez `signChallengeBase64()` zamiast `decodeBase64Url()` + `signBase64()` w kliencie | dwa POST-y (`/devices/auth/challenge`, `/devices/auth/verify`), 200, token zapisany |
| 5 | **Walidacja `expires_at`** | **nowa walidacja zakresów** w `parseIso8601ToUnix()` | token z backendu przyjęty; brak `No valid session` w pętli |
| 6 | **Wysłanie pakietu** | `TelemetrySender` bierze `IClock&`, `IHttpClient&`, `IStatusLed&`, `IModemLink&` | `[LOOP] Send OK, seq=…`, backend przyjmuje **200/202, nie 422** |
| 7 | **Pakiet z błędem czujnika** | **zmieniony kontrakt błędów** — kod z rejestru + severity z rejestru | odłącz PT100 → pakiet z `SENSOR_FAULT_HW`/`critical` przyjęty przez backend (wcześniej: 422) |
| 8 | **Restart po watchdogu** | `Watchdog` bierze `ISystemControl&` zamiast wołać `esp_restart()` i ruszać `rtcRestartCounter` wprost | wyjmij antenę na > 5 min → AT, twardy reset modemu, restart; `Restart counter (RTC)` rośnie i **zatrzymuje się na 2** |
| 9 | **Licznik restartów przeżywa restart** | licznik idzie przez `EspSystemControl(rtcRestartCounter)` — referencja do pamięci RTC | po restarcie z pkt. 8 log pokazuje niezerowy licznik, a po udanej wysyłce wraca do 0 |
| 10 | **Sygnalizacja LED** | `StatusLed : IStatusLed` | jedno mignięcie po sukcesie, trzy po błędzie |

### 7.2 Ryzyka, na które warto patrzeć

- **Pkt 8 to jedyne miejsce, gdzie sprawdza się `EspSystemControl`.** `ISystemControl`
  jest z definicji nieuruchamialny w testach — restart w teście zabiłby test.
- **Pkt 2 i 6** przechodzą przez atrapy TinyGSM w testach. Jeśli sekwencja AT rozjechała
  się z rzeczywistością, wyjdzie to dopiero tutaj.
- **Pkt 7 jest najważniejszy z całej listy** — to jedyna zmiana funkcjonalna, która
  zmienia treść wysyłanych danych.

### 7.3 Znalezione, nienaprawione — do decyzji

| Obserwacja | Miejsce | Dlaczego zostawione |
|---|---|---|
| `waitForNetwork()` nie ma własnego opóźnienia w pętli; kończy się tylko dlatego, że TinyGSM blokuje na czas timeoutu. Gdyby kiedyś zaczął zwracać natychmiast, ESP32 kręciłby się w pętli — a `esp_task_wdt_reset()` w środku karmi watchdoga, więc **task WDT by tego nie przerwał** | `ModemLink::waitForNetwork()` | zmiana zachowania pętli sieciowej wykracza poza zakres B-06; test `BrakRejestracjiWSieciKonczyInicjalizacjeNiepowodzeniem` dokumentuje obecną zależność |
| `extern const uint32_t TOKEN_REFRESH_MARGIN_SECONDS;` wewnątrz funkcji, przy już dołączonym `Config.h` | `DeviceIdentity::hasValidSession()` | działa (odwołuje się do tej samej stałej o wiązaniu wewnętrznym), ale jest mylące — kosmetyka |
| `char buffer[30]` w `formatIso8601()` — GCC ostrzega o możliwym obcięciu dla nierealistycznych lat | `TelemetryPayload::formatIso8601()` | `snprintf` obcina bezpiecznie; dla lat 1000–9999 wynik ma 24 znaki |
| `WINDOW_DROPPED_BUFFER_FULL` po deduplikacji nie niesie **liczby** porzuconych okien | `TelemetryPayload` | licznik porzuceń należy do diagnostyki urządzenia — zakres **B-08** |

---

## 8. Pliki

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
