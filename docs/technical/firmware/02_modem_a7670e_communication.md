# Firmware: komunikacja z modemem A7670E-FASE

> Dokumentacja kontroli, resetu i diagnostyki modemu LTE A7670E-FASE na płytce KAmod. Mapa pinów i uwagi o module: [`01_hardware.md`](./01_hardware.md). Przegląd całości: [`00_przeglad.md`](./00_przeglad.md).
>
> **Status: zweryfikowane na sprzęcie 2026-08-22** — procedura hardReset testowana, komunikacja AT potwierdzona (5/5 prób pre-reset i post-reset), diagnostyka LED działająca.
> **Uzgodnione z kodem: 2026-09-03** — poprawione czasy sekwencji, tabela pinów i sekcja diagnostyki.

## 1. Cel

Modem A7670E-FASE dostarcza łączność LTE-M do backendu. Firmware musi:
- Inicjować modem po starcie (sekwencja PWRKEY + oczekiwanie na autoboot)
- Wysyłać komendy AT (testowanie, konfiguracja)
- Zdolność do zdalenego resetu sprzętowego bez rebootowania ESP32
- Monitorować status (LED, diagnostyka)

## 2. Architektura

### 2.1 Biblioteki

| Biblioteka | Odpowiedzialność |
|---|---|
| `lib/ModemPower` | Zarządzanie pinami PWRKEY i RESET. `powerOn()` — sekwencja startu. `hardReset()` — procedura resetu bez wyłączania zasilania. |
| `lib/ModemLink` | Komunikacja UART (TinyGSM wrapper). `init()` — auto-baud, połączenie do APN. `ensureConnected()` — utrzymanie sieci w `loop()`. `testAT()` — test żywotności. |
| `lib/TelemetryHttpClient` | HTTP nad GPRS (używa `ModemLink`). |

### 2.2 Pin mapping (ESP32-S3 ↔ A7670E, KAmod HAT)

| ESP32-S3 GPIO | Funkcja | Pin złącza 40-pin HAT | Uwagi |
|---|---|---|---|
| 17 | UART1 TX | pin 8 (RXD modemu) | [`Config.h:17`](../../../firmware/include/Config.h#L17) |
| 18 | UART1 RX | pin 10 (TXD modemu) | [`Config.h:16`](../../../firmware/include/Config.h#L16) |
| 4 | PWRKEY | pin 7 | Active-high, [`Config.h:18`](../../../firmware/include/Config.h#L18) |
| 5 | RESET | pin 12 | Active-high, HIGH trzyma modem w resecie, [`Config.h:19`](../../../firmware/include/Config.h#L19) |
| – | Baud rate | – | Obie strony: 115200 bps, 8N1 (`MODEM_BAUD`) |

**Źródło:** [`Config.h`](../../../firmware/include/Config.h) dla numerów GPIO,
[`01_hardware.md §7`](./01_hardware.md#7-a7670e-fase--moduł-kamod-lte-cat1-gnss-hat) dla przełożenia
na piny złącza HAT (status: draft), wiki KAmod (https://wiki.kamamilabs.com/).

### 2.3 LED Indicators (KAmod płytka)

| Dioda | Pin | Znaczenie |
|---|---|---|
| PWR (D5) | – | Zasilanie obecne (powinna świecić zawsze) |
| STA (D3) | – | Modem aktywny (świeci gdy modem się bootuje/pracuje) |
| NET (D4) | – | Szukanie/połączenie sieciowe (miga = szukanie, stała = podłączony) |

## 3. Sekwencja inicjalizacji (`lib/ModemPower::powerOn()`)

Wywoływana raz w `setup()`:

1. **Jeśli POWER_ENABLE dostępny** (GPIO -1 = brak): ustaw HIGH, czekaj 500ms
2. **RESET pin**: ustaw OUTPUT, postaw na LOW (zwolnienie resetu, bo active-high)
3. **PWRKEY sekwencja** (active-high):
   - Postaw HIGH
   - Czekaj 100ms
   - Postaw LOW (zwolnienie przycisku)
   - Czekaj 1200ms (trzymanie w trakcie bootupu)
   - Postaw HIGH
   - Czekaj 3000ms (modem się bootuje, J_APWK autopower tworzy własny impuls)

**Timing:** `powerOn()` blokuje przez **~4,3 s** (100 + 1200 + 3000 ms; POWER_ENABLE jest wyłączone,
`-1`). Wołane z `setup()` albo z `handleEnrollmentPhase()`, nie z gorącej ścieżki `loop()`.
Weryfikacja: [`ModemPower.cpp:7-28`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L7-L28).

**Auto-power (J_APWK):** Płytka KAmod zawiera obwód generujący impuls PWK automatycznie po podłączeniu zasilania. Jeśli J_APWK jumper **nie jest przecięty** (domyślnie), modem może bootować asynchronicznie względem ESP32, niezależnie od `powerOn()` sekwencji (jest to feature, nie bug — zmniejsza opóźnienie startu całego systemu).

**Polaryzacja RESET (ważna!):**
- KAmod: RESET aktywne w stanie HIGH (wbrew konwencji SIMCom gdzie RESET bywają active-low)
- `powerOn()`: ustawia RESET = LOW = nieaktywny = modem może pracować
- Jeśli RESET jest HIGH → modem jest w resecie → brak odpowiedzi na AT

## 4. Procedura zdalnego resetu (`lib/ModemPower::hardReset()`)

Wywoływana z `loop()` lub przez handler zewnętrzny (watchdog, zdalny command):

Pełne źródło: [`ModemPower.cpp:30-50`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L30-L50).

**Timing — dwie fazy, obie wykonywane zawsze:**

| Faza | Kroki | Czas |
|---|---|---|
| RESET | HIGH 2600 ms (reset wewnętrzny) → LOW 1500 ms (boot modemu) | 4,1 s |
| PWRKEY | LOW 3000 → HIGH 1000 → LOW 1000 → HIGH 5000 ms | 10,0 s |
| **Razem** | | **~14,1 s** |

**Sprostowanie wobec wcześniejszej wersji tego dokumentu.** Pisała ona o „~4,1 s pełnego resetu",
a sekwencję PWRKEY nazywała *opcjonalną*. W kodzie jest bezwarunkowa dla `pwrkey_pin_ >= 0`, a
`MODEM_PWRKEY_PIN` = 4, więc **wykonuje się zawsze** — realny czas twardego resetu to ~14,1 s.

**Uwaga o watchdogu.** `hardReset()` nie wywołuje w środku `esp_task_wdt_reset()`, a wołający ją
[`Watchdog::attemptRecovery()`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L32-L35) dokłada
jeszcze `delay(3000)` — łącznie ~17 s blokady w jednej iteracji `loop()`, przy limicie Task WDT
ustawionym na 15 s ([`platformio.ini:19`](../../../firmware/platformio.ini#L19)). Czy kończy się to
zadziałaniem watchdoga, zależy od tego, czy zadanie `loopTask` jest w ogóle zapisane do Task WDT —
tego nie da się rozstrzygnąć z samego kodu tego repozytorium. **Do sprawdzenia na sprzęcie:**
obserwuj, czy po recovery poziomu 2 pojawia się w logu `task_wdt: Task watchdog got triggered`.

**Weryfikacja (2026-08-22):** Test pokazał, że post-reset modem odpowiada na 5/5 komend AT.

## 5. Komunikacja AT (TinyGSM / UART)

### 5.1 Podstawowe komendy

```
AT              — Test żywotności. Odpowiedź: "OK"
ATI             — Info o modemie (model, revision, IMEI)
AT+CSQ          — Signal quality (0-31, 99=unknown)
AT+CREG?        — Registration status (2=registered)
AT+CGDCONT?     — PDP context (APN)
AT+CGACT?       — GPRS active
```

### 5.2 Obsługa w firmware

`lib/ModemLink::init()`:
```cpp
modem_->init()                  // Handshake TinyGSM
modem_->waitForNetwork(60000)   // Czekaj na rejestrację (timeout 60s)
modem_->gprsConnect(apn, "", "")  // GPRS/LTE łączność do APN
modem_->localIP()               // Pokaż IP (powinno być != "0.0.0.0")
```

### 5.3 Auto-baud (`ModemLink::init()`)

```cpp
TinyGsmAutoBaud(serial_at_, 9600, 115200);
```

Jeśli modem wysyła śmieci (nieznany baud), TinyGSM próbuje kolejno 9600 i 115200 bps.

**Cała sekwencja `ModemLink::init()` blokuje 7–17 s**: `delay(5000)` na stabilizację UART →
2 × `delay(500)` na czyszczenie bufora RX → `delay(1000)` po auto-baudzie → do 10 s prób
`modem_->init()` co 500 ms. Każdy krok jest otoczony `esp_task_wdt_reset()`
([`ModemLink.cpp:15-52`](../../../firmware/lib/ModemLink/src/ModemLink.cpp#L15-L52)). Dalej dochodzi
do 60 s oczekiwania na rejestrację w sieci i do 30 s na kontekst GPRS.

## 6. Diagnostyka i troubleshooting

### 6.1 Serial log tagging

Wszystkie sygnifikantne eventy loguję z tagiem `[TAG]`:
- `[MODEM]` — inicjalizacja, komunikacja AT
- `[NET]` — szukanie sieci, rejestracja
- `[DATA]` — GPRS/LTE połączenie
- `[RESET]` — procedury powerOn/hardReset
- `[UART]` — konfiguracja portu szeregowego

Przykład:
```
[MODEM] Starting UART...
[MODEM] Auto-bauding...
[MODEM] Initializing modem (modem.init())...
[NET] Waiting for network (timeout 60s)...
[NET] Network connected
[DATA] Connecting GPRS/LTE (timeout 30s)...
[DATA] GPRS/LTE connected
```

### 6.2 Scenariusze błędów

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| Brak odpowiedzi na AT | RESET = HIGH (modem w resecie) | Sprawdź GPIO 5. Powinno być LOW w normalnym stanie. Wgraj `ModemPower::powerOn()` ponownie. |
| `modem.init()` timeout | Baud mismatch, brak zasilania | Sprawdź D5 (PWR LED). Jeśli nie świeci, zasilanie w hardware'u. Jeśli świeci, spróbuj hardReset. |
| `waitForNetwork()` timeout | Brak sygnału, błędy SIM | Sprawdź D4 (NET LED). Jeśli nie miga, brak pokrycia. Sprawdzić SIM i APN. |
| Zły IP (`0.0.0.0`) | GPRS connection failed | Spróbuj `modem_->gprsDisconnect()` i reconnect, lub hardReset. |
| UART garbage | Auto-baud fail, hardware problem | Sprawdź GPIO17/18. Jeśli hardware jest OK, baud problem — spróbuj ręcznie `serial_at_.begin(115200, SERIAL_8N1, 18, 17)` w testowym sketch. |

### 6.3 Diagnostyka na żywo

**Trybu testowego `#define TEST_MODEM` już nie ma** — opisywał on wersję `main.cpp` sprzed refaktoru
i został usunięty z kodu. Dostępne dziś narzędzia diagnostyczne to:

1. **Log startowy.** `pio run -t upload -e esp32-s3 && pio device monitor -b 115200`. Prawidłowa
   sekwencja to `[MODEM] Starting UART...` → `[MODEM] Init OK` → `[NET] Network connected` →
   `[DATA] GPRS/LTE connected` → `[DATA] Local IP: ...`. Zatrzymanie się na którymkolwiek z tych
   kroków wskazuje etap z tabeli w [§6.2](#62-scenariusze-błędów).
2. **Czas inicjalizacji.** `main.cpp` mierzy go i loguje: `[BOOT] Modem ready in NNNN ms`. Wartość
   rzędu 100–200 ms oznacza modem już wystartowany (np. przez J_APWK); kilkanaście sekund — pełną
   sekwencję power-on; brak linii — porażkę.
3. **Diody na płytce HAT** (PWR/STA/NET) — patrz [§2.3](#23-led-indicators-kamod-płytka). Dają obraz
   niezależny od logów, przydatny gdy UART w ogóle nie odpowiada.
4. **Test AT z poziomu recovery.** `Watchdog` poziomu 1 woła `ModemLink::testAT()` po 5 minutach bez
   udanej wysyłki. **Uwaga: [`Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp) nie
   loguje niczego** — recovery przebiega bezgłośnie, więc w logu widać tylko jego skutki (przerwa w
   komunikatach na czas twardego resetu, ewentualny restart ESP32). Zob.
   [`03_esp32_reset_and_recovery.md §3`](./03_esp32_reset_and_recovery.md#3-strategia-recovery-3-level).

## 7. Znane problemy i obejścia

### 7.1 Potencjalny problem: brak soft-reset AT+CRESET w `init()`

Pierwotnie `ModemLink::init()` zawierało `modem_->restart()` (komenda AT+CRESET). Usunięto, bo:
- Modem jest już power-cycled przez `ModemPower::powerOn()` (PWRKEY sekwencja)
- Dodatkowy soft-reset wymusza drugi reboot, który może czekać na "SMS Ready" przez minuty, co blokuje boot

Jeśli w przyszłości wymaga się soft-resetu (np. do cofnięcia zmian APN bez rebootowania), użyj `hardReset()` zamiast AT+CRESET.

### 7.2 Watchdog safety

`ModemLink::init()`, `waitForNetwork()` i `connectGprs()` zawierają pętle czekające. Wewnątrz każdej: `esp_task_wdt_reset()` co 200-500ms, aby nie triggerować watchdoga. W `main.cpp::setup()` ogólnie (np. okno na INFO, pętle AT): również `esp_task_wdt_reset()` dostępny.

### 7.3 Regression: RESET pin held HIGH (2026-08-23, FIXED)

**Problem:** Modem AT init timeout po 10.3s. Przyczyna: `ModemPower::powerOn()` ustawiała pin RESET na HIGH ale nigdy go nie zwalniała, trzymając modem w trwałym resecie. Modem nie mógł się bootować.

**Root cause:** Na płytce KAmod pin RESET jest active-HIGH (HIGH = reset asserted, LOW = normal operation). Kodeks musiał ustawiać RESET = LOW po inicjalizacji, aby zwolnić modem.

**Fix:** [`lib/ModemPower/src/ModemPower.cpp:16`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L16) — zmiana `digitalWrite(reset_pin_, HIGH)` na `digitalWrite(reset_pin_, LOW)`. Sekwencja pasuje teraz do procedury opisanej w [§3](#3-sekwencja-inicjalizacji-libmodempowerpoweron) i do `hardReset()` z [§4](#4-procedura-zdalnego-resetu-libmodempowerhardreset).

**Weryfikacja (2026-08-23):** Modem AT init teraz kompletuje się w **132ms** zamiast timeout'u. Network auto-connect, GPRS/LTE online, żadnych watchdog'ów. ✓

## 8. Referencje

- **KAmod wiki:** https://wiki.kamamilabs.com/index.php?title=KAmod_LTE_CAT1-GNSS_z_modu%C5%82em_A7670E-FASE_(PL)
- **SIMCom A7670E spec:** (PDF na stronie KAmod, lub https://www.simcom.com/)
- **TinyGSM (fork używany w projekcie):** https://github.com/lewisxhe/TinyGSM-fork — zob. [`platformio.ini:10`](../../../firmware/platformio.ini#L10)
- **Mapa sprzętowa:** [`01_hardware.md`](./01_hardware.md)
- **Config.h:** [`firmware/include/Config.h`](../../../firmware/include/Config.h#L15-L20) — definicje pinów
