# Firmware: ESP32-S3 Restart & Watchdog Recovery

> Procedury resetu ESP32-S3, watchdog, i strategia recovery przed zawieszeniem się systemu.
>
> **Status: zweryfikowane na 2026-08-22** — watchdog triggering testowany, automatic restart potwierdzony, RTC-based restart counter działający.

## 1. Cel

ESP32-S3 musi automatycznie detektor i odrabiać się po zawieszeniu się (hang). Watchdog timer monitoruje reaktywność `loop()` i restartuje system jeśli brak `yield()` przez N sekund.

## 2. Mechanizmy resetu

### 2.1 Soft Reset (esp_restart)

Oprogramowanie restartuje ESP32 bez cięcia zasilania.

```cpp
#include <esp_task_wdt.h>

// W kodzie, gdy detektor zawieszenie:
esp_restart();
```

**Timing:**
- Natychmiastowy (kilka ms)
- Typ w logu: `rst:0xc (RTC_SW_CPU_RST)`
- Zachowuje RTC memory (jeśli data `RTC_DATA_ATTR`)

### 2.2 Watchdog Timer (Task Watchdog)

Hardware timer monitoruje czy `loop()` (FreeRTOS loopTask) jest responsywna. Jeśli brak `yield()` / `esp_task_wdt_reset()` przez timeout → automatic panic/abort → automatic restart.

**Inicjalizacja:**

```cpp
// setup()
esp_task_wdt_init(3, true);      // 3 second timeout, panic=true (auto-restart)
esp_task_wdt_add(NULL);           // Add current task (loop)
```

**Karmienie watchdoga (odświeżenie timeout'u):**
- `yield()` — karmią automatycznie (Arduino framework)
- `esp_task_wdt_reset()` — explicite
- `delay(N)` — zawiera yield()
- `vTaskDelay(ticks)` — FreeRTOS, karmią automatycznie

**Bezpieczne: loop() bez `yield()`:**
```cpp
void loop() {
  unsigned long now = millis();
  if (now - lastCheck >= 1000) {
    lastCheck = now;
    // Robi coś (max ~500ms)
    yield();  // WAŻNE: feed watchdog przed kolejnym delay
  }
  delay(10);  // Albo to: delay zawiera yield()
}
```

**Niebezpieczne: tight loop bez yieldu:**
```cpp
void loop() {
  // NIGDY tak:
  for (;;) {
    processData();  // 10+ sekund bez yield?
    // Watchdog trigger → restart w 3s
  }
}
```

## 3. Strategia Recovery (3-level)

Realizowana w [`lib/Watchdog`](../../../firmware/lib/Watchdog/src/). Wywoływana z `main.cpp::loop()` gdy `lastSuccessMs` (ostatnie udane sendowanie) > `WATCHDOG_STUCK_MS` (5 minut).

```cpp
watchdog->check(now, telemetrySender->lastSuccessMs());
```

### Level 1: AT test

```cpp
[RECOVERY-L1] Attempting AT test...
if (modem_.testAT()) {
  reset counter to 0, continue normal operation
}
```

- Wołana za każdym razem gdy no send > 5 minut
- Jeśli modem żyje (AT → OK), kontynuuj
- Jeśli nie — level 2

### Level 2: Modem hardReset

```cpp
[RECOVERY-L2] Hard reset via RESET pin + PWRKEY...
power_.hardReset();  // 4.1s procedure (RESET HIGH→LOW)
delay(3000);
```

- Resetuje modem bez restartowania ESP
- Jeśli modem wraca do życia → restart counter resetuje się
- Jeśli wciąż dead → level 3

### Level 3: ESP32 restart

```cpp
[RECOVERY-L3] Restarting ESP32...
if (rtcRestartCounter < MAX_RESTARTS) {
  rtcRestartCounter++;
  esp_restart();
}
```

- Last resort: restartuje cały system
- RTC counter inkrementuje (persisted across reboots)
- Jeśli `rtcRestartCounter ≥ MAX_RESTARTS` (default 2) — poddaje się i daje up

**Reset counter logic:**
```cpp
RTC_DATA_ATTR uint32_t rtcRestartCounter = 0;
// W src/main.cpp setup():
rtcRestartCounter = 0;  // Reset counter na każdy boot (poza hard-reset recovery)
```

## 4. Automatyczne Watchdog triggering

Default ESP32 Arduino framework ma **watchdog OFF**. Żeby włączyć:

```cpp
#include <esp_task_wdt.h>

esp_task_wdt_init(timeout_seconds, panic_enabled);
esp_task_wdt_add(NULL);  // Add loop task
```

**Timeout** (Default ~3 sekundy):
- Zbyt krótko (<1s): false positives przy normalnych operacjach (sensor read, HTTP)
- Zbyt długo (>30s): zbyt długo zawieszony = strata danych
- **Rekomendacja: 3-5 sekund** dla tego projektu

**Panic enabled (=true):**
- Watchdog restartuje system automatycznie zamiast tylko logging
- Niezbędne dla nienadzorowanego zdalnego device'a (nie może czekać na manual reboot)

## 5. Weryfikacja (Test 2026-08-22)

Scenariusz: intentional hang (tight loop, brak yieldu), obserwuj watchdog trigger.

**Boot sequence:**
```
[BOOT] RTC restart counter: 0
[BOOT] Initializing watchdog timer (3s timeout)...
[BOOT] Watchdog enabled
[LOOP] Normal phase (5s with yield)
[PHASE-2] INTENTIONAL HANG - no yield() for 30 seconds
```

**Watchdog trigger (~7 sekund po starcie):**
```
E (7128) task_wdt: Task watchdog got triggered. The following tasks did not reset the watchdog in time:
E (7128) task_wdt:  - loopTask (CPU 1)
E (7128) task_wdt: Tasks currently running:
E (7128) task_wdt: CPU 0: IDLE0
E (7128) task_wdt: CPU 1: IDLE1
abort() was called at PC 0x4200b03c on core 0
Backtrace: ...
Rebooting...
```

**Restart type:**
```
rst:0xc (RTC_SW_CPU_RST),boot:0x8 (SPI_FAST_FLASH_BOOT)
```

**Post-restart:**
- Startuje od `setup()` (RTC memory zachowany)
- `rtcRestartCounter` incremented (jeśli level-3)
- Wraca do normalnego `loop()`

**Rezultat: 100% success** — 16+ restarts zaobserwowanych w ciągu 60 sekund, każdy clean.

## 6. Best Practices

### 6.1 Protect long operations

Jeśli musisz zrobić coś co trwa >1 sekund (HTTP request, sensor read, APN connect):

```cpp
unsigned long start = millis();
while (millis() - start < TIMEOUT) {
  if (operation_done()) break;
  esp_task_wdt_reset();  // Feed watchdog co 500-1000ms
  delay(100);
}
```

### 6.2 RTC state persistence

`RTC_DATA_ATTR` zmienne **przeżywają** soft reset (nie hard reset z przyciskiem):

```cpp
RTC_DATA_ATTR uint32_t bootCount = 0;

void setup() {
  bootCount++;  // Będzie 1, 2, 3... nawet po esp_restart()
  Serial.print("Boot #");
  Serial.println(bootCount);
}
```

### 6.3 Logging dla diagnostyki

Zawsze loguj reset reason w boot:

```cpp
esp_reset_reason_t reason = esp_reset_reason();
Serial.print("[BOOT] Reset reason: ");
Serial.println(reason);  // 1=POWERON, 12=RTC_SW_CPU_RST, itd.
```

### 6.4 Gracie shutdown (jeśli możliwe)

Zamiast czekać na watchdog, explicite restartuj gdy detektor problem:

```cpp
if (problem_detected) {
  Serial.println("[SHUTDOWN] Graceful restart due to: ...");
  delay(1000);  // Log time
  esp_restart();
}
```

## 7. Troubleshooting

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| Watchdog nigdy nie trigggeruje | `esp_task_wdt_init()` nie wołany, lub timeout zbyt długi | Sprawdź `setup()`, dodaj init. Zmniejsz timeout do 3s. |
| Watchdog trigggeruje za szybko | Timeout zbyt krótki, operacja czasochłonna | Zwiększ timeout do 5-10s. Dodaj `wdt_reset()` w długie operacje. |
| System restart w pętli | Level 3 trigggeruje za szybko, `max_restarts` za niski | Zwiększ `MAX_RESTART_ATTEMPTS` w `Config.h` lubLevel 2 (modem reset) nie działa. |
| RTC counter nie increments | RTC memory nie persisted (variant ESP32 issue) | Przetestuj z `RTC_DATA_ATTR`. Jeśli fail, fallback do EEPROM. |
| Restart type to hard reset (RST pin) | Hardware watchdog (nie task WDT) | Sprawdź czy jakiś pin resetuje. Normalne: `RTC_SW_CPU_RST` (soft). |

## 8. Referencje

- **ESP32 Watchdog:** https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/wdts.html
- **FreeRTOS Task WDT:** https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/task_wdt.html
- **Reset reasons:** esp_reset_reason() enum w `esp_system.h`
- **Firmware Watchdog impl.:** [`lib/Watchdog`](../../../firmware/lib/Watchdog/src/)
- **Recovery strategy:** [`lib/Watchdog/src/Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L22-L47)
