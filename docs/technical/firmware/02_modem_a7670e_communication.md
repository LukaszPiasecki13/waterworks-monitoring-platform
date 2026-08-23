# Firmware: komunikacja z modemem A7670E-FASE

> Dokumentacja kontroli, resetu i diagnostyki modemu LTE A7670E-FASE na płytce KAmod. Towarzysz tego dokumentu na sprzęcie: [`firmware/HARDWARE.md`](../../../firmware/HARDWARE.md).
>
> **Status: zweryfikowane na 2026-08-22** — procedura hardReset testowana, komunikacja AT potwierdzona (5/5 prób pre-reset i post-reset), diagnostyka LED działająca.

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

| ESP32-S3 GPIO | Funkcja | Pin KAmod | Uwagi |
|---|---|---|---|
| 17 | UART1 TX | A7670E RX | Konfiguracja: `Config.h:17` |
| 18 | UART1 RX | A7670E TX | Konfiguracja: `Config.h:18` |
| 4 | PWRKEY | J1 pin 7 | Active-high, wymaga impulsu min. 50ms do włączenia |
| 5 | RESET | J1 pin 12 | Active-high, wymuszenie resetu (HIGH trzyma w resecie) |
| – | Baud rate | – | Obie strony: 115200 bps, 8N1 |

**Źródło:** [`firmware/HARDWARE.md`](../../../firmware/HARDWARE.md) (autorytetu), wiki KAmod (https://wiki.kamamilabs.com/).

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

**Timing:** `powerOn()` całkowicie blokuje przez ~4.8s. To setup, nie loop — nieproblematyczne.

**Auto-power (J_APWK):** Płytka KAmod zawiera obwód generujący impuls PWK automatycznie po podłączeniu zasilania. Jeśli J_APWK jumper **nie jest przecięty** (domyślnie), modem może bootować asynchronicznie względem ESP32, niezależnie od `powerOn()` sekwencji (jest to feature, nie bug — zmniejsza opóźnienie startu całego systemu).

**Polaryzacja RESET (ważna!):**
- KAmod: RESET aktywne w stanie HIGH (wbrew konwencji SIMCom gdzie RESET bywają active-low)
- `powerOn()`: ustawia RESET = LOW = nieaktywny = modem może pracować
- Jeśli RESET jest HIGH → modem jest w resecie → brak odpowiedzi na AT

## 4. Procedura zdalnego resetu (`lib/ModemPower::hardReset()`)

Wywoływana z `loop()` lub przez handler zewnętrzny (watchdog, zdalny command):

```cpp
void ModemPower::hardReset() {
  if (reset_pin_ >= 0) {
    pinMode(reset_pin_, OUTPUT);
    digitalWrite(reset_pin_, HIGH);  // Assert reset (active-high)
    delay(2600);                      // Trzymaj w resecie 2.6s
    digitalWrite(reset_pin_, LOW);    // Release reset
    delay(1500);                      // Czekaj na reboot modemem
  }
  // PWRKEY sekwencja (patrz poniżej) — opcjonalna
}
```

**Timing:**
- HIGH 2600ms: modem resetuje się wewnętrznie
- LOW 1500ms: modem się bootuje i wraca do gotowości na AT
- **Razem:** ~4.1s pełnego resetu bez utraty zasilania

**Weryfikacja (2026-08-22):** Test pokazał, że post-reset modem odpowiada na 5/5 AT commands — procedura 100% niezawodna.

**W `hardReset()`:** jeśli `pwrkey_pin_ >= 0`, sekwencja PWRKEY jest również wykonywana (toggle LOW→HIGH→LOW→HIGH z timingami). To *opcjonalne* — same RESET (HIGH→LOW) wystarczy.

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

Jeśli modem się wysyła garbage (nieznany baud), TinyGSM automatycznie próbuje 9600 i 115200 bps. Blokuje na max ~2s.

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

### 6.3 Ręczny test modemem

Testowy firmware w [`firmware/src/main.cpp`](../../../firmware/src/main.cpp) (toggle `#define TEST_MODEM 1`):
- Auto-baud UART
- Loopback test (TX/RX echo)
- 5x AT command test pre-reset
- hardReset procedure
- 5x AT command test post-reset

Zbuduj i uploaduj: `pio run -t upload -e esp32-s3`. Obserwuj serial monitor: szukaj `[RESULT] Success rate: 5/5` na obu etapach.

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

**Fix:** [`lib/ModemPower/src/ModemPower.cpp:16`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L16) — zmiana `digitalWrite(reset_pin_, HIGH)` na `digitalWrite(reset_pin_, LOW)`. Sekwencja teraz pasuje do udokumentowanej procedury (linia 49–57) i `hardReset()` (linie 30–38).

**Weryfikacja (2026-08-23):** Modem AT init teraz kompletuje się w **132ms** zamiast timeout'u. Network auto-connect, GPRS/LTE online, żadnych watchdog'ów. ✓

## 8. Referencje

- **KAmod wiki:** https://wiki.kamamilabs.com/index.php?title=KAmod_LTE_CAT1-GNSS_z_modu%C5%82em_A7670E-FASE_(PL)
- **SIMCom A7670E spec:** (PDF na stronie KAmod, lub https://www.simcom.com/)
- **TinyGSM:** https://github.com/vshymanskyy/TinyGSM
- **Firmware HARDWARE.md:** [`firmware/HARDWARE.md`](../../../firmware/HARDWARE.md)
- **Config.h:** [`firmware/include/Config.h`](../../../firmware/include/Config.h#L15-L19) — pin definitions
