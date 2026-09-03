# Firmware: ESP32-S3 Restart & Watchdog Recovery

> Procedury resetu ESP32-S3, watchdog i strategia odzyskiwania po zawieszeniu.
>
> **Status: zweryfikowane na sprzęcie 2026-08-22** — wyzwolenie watchdoga testowane, automatyczny
> restart potwierdzony, licznik restartów w pamięci RTC działający.
> **Uzgodnione z kodem: 2026-09-03** — poprawiona konfiguracja Task WDT (§2.2, §4) i opis
> faktycznej implementacji recovery (§3).

## 1. Cel

Urządzenie pracuje bez nadzoru, w szafie, często bez dostępu fizycznego. Musi więc samo wykryć, że
przestało dostarczać dane, i spróbować się z tego wygrzebać. Realizują to **dwa niezależne
mechanizmy**, których nie należy mylić:

| Mechanizm | Co obserwuje | Limit | Reakcja |
|---|---|---|---|
| **Task Watchdog (sprzętowy)** | Czy zadanie `loopTask` w ogóle oddaje sterowanie | 15 s ([`platformio.ini:19`](../../../firmware/platformio.ini#L19)) | Panic i restart całego układu |
| **Watchdog aplikacyjny** ([`lib/Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp)) | Czy od ostatniej **udanej wysyłki** nie minęło za dużo czasu | 5 min (`WATCHDOG_STUCK_MS`) | Trzy poziomy recovery, patrz [§3](#3-strategia-recovery-3-level) |

Pierwszy łapie zawieszenie kodu. Drugi łapie sytuację, w której kod działa poprawnie, ale dane i tak
nie docierają — najczęściej z winy modemu albo sieci.

## 2. Mechanizmy resetu

### 2.1 Soft Reset (esp_restart)

Restart bez odcięcia zasilania.

```cpp
esp_restart();
```

**Timing:**
- Natychmiastowy (kilka ms)
- Typ w logu: `rst:0xc (RTC_SW_CPU_RST)`
- **Zachowuje pamięć RTC** — zmienne z `RTC_DATA_ATTR` przeżywają (zob. [§6.2](#62-rtc-state-persistence))

W repozytorium `esp_restart()` jest wołane z dwóch miejsc:
[`Watchdog::attemptRecovery()`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L36-L40) (recovery
poziomu 3) oraz [`main.cpp:196`](../../../firmware/src/main.cpp#L196), gdy urządzenie zostało usunięte
z platformy i wymaga ponownego provisioningu.

### 2.2 Task Watchdog — jak jest skonfigurowany w tym projekcie

**Uwaga: `main.cpp` nie wywołuje ani `esp_task_wdt_init()`, ani `esp_task_wdt_add()`.** Wcześniejsza
wersja tego dokumentu pokazywała taki fragment w `setup()` — w obecnym kodzie go nie ma. Konfiguracja
pochodzi wyłącznie z flag budowania:

```ini
; firmware/platformio.ini
build_flags =
    -D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15
    -D CONFIG_BOOTLOADER_WDT_DISABLE=1
```

Kod natomiast **gęsto karmi** watchdoga przez `esp_task_wdt_reset()` — w `setup()`, po każdym etapie
inicjalizacji, oraz na początku każdej iteracji `loop()`
([`main.cpp:191`](../../../firmware/src/main.cpp#L191)). Robią to też pętle oczekujące wewnątrz
`ModemLink` i operacje kryptograficzne w `DeviceIdentity`.

**Karmienie watchdoga:**
- `esp_task_wdt_reset()` — jawnie, tak robi ten projekt
- `delay(N)` i `yield()` — karmią pośrednio, bo oddają sterowanie
- `vTaskDelay(ticks)` — jw.

**Bezpieczny wzorzec pętli:**
```cpp
void loop() {
  esp_task_wdt_reset();     // pierwsza linia loop() w tym projekcie
  // ... praca ...
  delay(10);                // oddaj sterowanie
}
```

**Wzorzec niebezpieczny** — długa operacja bez oddania sterowania:
```cpp
for (;;) {
  processData();            // 10+ sekund bez yield → watchdog
}
```

## 3. Strategia Recovery (3-level)

Realizowana w [`lib/Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp). Wołana z
[`main.cpp:224`](../../../firmware/src/main.cpp#L224) w każdej iteracji `loop()`:

```cpp
watchdog->check(now, telemetrySender->lastSuccessMs());
```

`check()` nic nie robi, dopóki `now - lastSuccessMs` nie przekroczy `WATCHDOG_STUCK_MS` (5 minut).

**Dwa zachowania, które warto znać, zanim zacznie się to diagnozować:**

1. **Recovery jest bezgłośne.** W całym `Watchdog.cpp` nie ma ani jednego wywołania loggera. Pokazane
   niżej linie `[RECOVERY-Lx]` to **opis, nie cytat z logu** — w rzeczywistym logu ich nie zobaczysz.
   To luka diagnostyczna warta zamknięcia przy najbliższej okazji.
2. **Błąd trwały wstrzymuje recovery.** Jeśli ostatnia wysyłka skończyła się kodem 409, 410 albo 403,
   `check()` wraca bez działania ([`Watchdog.cpp:16-20`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L16-L20)).
   Uzasadnienie: to nie awaria modemu, tylko urządzenie czeka na konfigurację po stronie backendu
   (np. `409 DEVICE_NOT_ASSIGNED` — nieprzypisane do obiektu wodociągowego). Resetowanie modemu nic
   by tu nie dało.

Poziomy są wybierane licznikiem `recovery_attempts_`, który rośnie o jeden przy każdym wejściu
w `attemptRecovery()`:

### Level 1: test AT (`recovery_attempts_ == 0`)

```
[opis] modem_.testAT()
```

- Jeśli modem odpowiada → licznik wraca do 0, urządzenie pracuje dalej.
- Jeśli nie odpowiada → licznik rośnie do 1, następne wejście trafi w poziom 2.

### Level 2: twardy reset modemu (`recovery_attempts_ == 1`)

```
[opis] power_.hardReset(); delay(3000);
```

- Resetuje modem **bez restartu ESP32**. Procedura trwa ~14,1 s plus 3 s odczekania — łącznie ok. 17 s
  blokady w jednej iteracji `loop()`, bez karmienia watchdoga w środku. Szczegóły i zastrzeżenie:
  [`02_modem_a7670e_communication.md §4`](./02_modem_a7670e_communication.md#4-procedura-zdalnego-resetu-libmodempowerhardreset).
- Licznik rośnie do 2.

### Level 3: restart ESP32 (`recovery_attempts_ == 2`)

```
[opis] if (rtcRestartCounter < MAX_RESTART_ATTEMPTS) { rtcRestartCounter++; esp_restart(); }
```

- Ostatnia deska ratunku. Licznik `rtcRestartCounter` leży w pamięci RTC, więc przeżywa restart.
- Po osiągnięciu `MAX_RESTART_ATTEMPTS` (domyślnie 2) urządzenie **przestaje się restartować** i
  zeruje `recovery_attempts_`, wracając do poziomu 1. Kolejne cykle recovery będą się więc powtarzać
  bez restartu, dopóki modem nie odpowie.

**Gdzie zeruje się licznik restartów.** Nie w `setup()`, tylko w
[`initializeTelemetry()`](../../../firmware/src/main.cpp#L119) — czyli dopiero wtedy, gdy urządzenie
faktycznie doszło do stanu pracy z telemetrią. To celowe: restart, po którym urządzenie nie wstało do
pracy, nie kasuje historii prób.

## 4. Konfiguracja Task WDT — dlaczego 15 s

Limit `CONFIG_ESP_TASK_WDT_TIMEOUT_S=15` jest wyraźnie dłuższy niż typowe 3–5 s dla prostego
firmware, i to jest **decyzja wymuszona przez blokujące operacje** w tym projekcie:

| Operacja | Czas blokady | Czy karmi watchdoga w środku |
|---|---|---|
| `ModemLink::init()` | 7–17 s | tak, `esp_task_wdt_reset()` między krokami |
| `waitForNetwork()` | do 60 s | tak, w pętli |
| `connectGprs()` | do 30 s | tak, w pętli |
| `ModemPower::powerOn()` | ~4,3 s | **nie** |
| `ModemPower::hardReset()` | ~14,1 s | **nie** |
| Generowanie klucza EC P-256 | ~2–3 s | tak, przed i po |
| HTTPS POST | do 30 s (timeout odpowiedzi) | nie w trakcie oczekiwania |

Dwie ostatnie pozycje z kolumny „nie" są powodem, dla którego skrócenie limitu poniżej ~15 s wymagałoby
najpierw rozbicia `ModemPower` na kroki nieblokujące. Nie robimy tego przy okazji dokumentacji, ale
**nie należy zmniejszać tej flagi bez tej przeróbki** — zamieni sprawny reset modemu w pętlę restartów.

`CONFIG_BOOTLOADER_WDT_DISABLE=1` wyłącza osobny watchdog bootloadera, który przy dłuższym starcie
(generowanie klucza, oczekiwanie na modem) potrafi zresetować układ jeszcze przed wejściem w `setup()`.

## 5. Weryfikacja (test 2026-08-22)

Scenariusz: celowe zawieszenie (ciasna pętla bez oddania sterowania), obserwacja wyzwolenia watchdoga.

> **Kontekst historyczny.** Ten test przeprowadzono, gdy limit Task WDT wynosił 3 s i był ustawiany
> jawnie w `setup()`. Obecna konfiguracja to 15 s z flagi budowania (§2.2), więc czasy w logu poniżej
> nie odpowiadają dzisiejszemu zachowaniu. Sam mechanizm — panic, restart, zachowanie pamięci RTC —
> pozostaje ten sam.

**Sekwencja startowa:**
```
[BOOT] RTC restart counter: 0
[BOOT] Initializing watchdog timer (3s timeout)...
[BOOT] Watchdog enabled
[LOOP] Normal phase (5s with yield)
[PHASE-2] INTENTIONAL HANG - no yield() for 30 seconds
```

**Wyzwolenie watchdoga (~7 s po starcie):**
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

**Typ restartu:**
```
rst:0xc (RTC_SW_CPU_RST),boot:0x8 (SPI_FAST_FLASH_BOOT)
```

**Po restarcie:**
- Start od `setup()`, pamięć RTC zachowana
- `rtcRestartCounter` inkrementowany (jeśli to był poziom 3)
- Powrót do normalnego `loop()`

**Rezultat: 100% skuteczności** — 16+ restartów zaobserwowanych w ciągu 60 s, każdy czysty.

## 6. Dobre praktyki

### 6.1 Ochrona długich operacji

Operacja trwająca ponad sekundę (żądanie HTTP, odczyt czujnika, zestawienie APN) powinna karmić
watchdoga w pętli:

```cpp
unsigned long start = millis();
while (millis() - start < TIMEOUT) {
  if (operation_done()) break;
  esp_task_wdt_reset();
  delay(100);
}
```

### 6.2 RTC state persistence

Zmienne `RTC_DATA_ATTR` (zebrane w [`RtcState.h`](../../../firmware/include/RtcState.h)) **przeżywają
`esp_restart()`**, ale **nie przeżywają zaniku zasilania** ani resetu przyciskiem.

```cpp
RTC_DATA_ATTR uint32_t rtcRestartCounter = 0;    // licznik restartów recovery
RTC_DATA_ATTR uint32_t rtcSyncedTimeUtcSec = 0;  // moment ostatniej synchronizacji czasu
RTC_DATA_ATTR uint32_t rtcSyncMillis = 0;        // millis() w chwili synchronizacji
```

Czego tam **nie ma**, a bywa mylone: bufor okien pomiarowych. Leży w zwykłym RAM-ie i ginie przy każdym
restarcie — patrz [`00_przeglad.md §8.1`](./00_przeglad.md#81-gdzie-dane-mogą-zginąć).

### 6.3 Logowanie dla diagnostyki

Warto logować przyczynę resetu na starcie — **dziś tego w kodzie nie ma**, a jest to najtańszy sposób
odróżnienia watchdoga od zaniku zasilania w terenie:

```cpp
esp_reset_reason_t reason = esp_reset_reason();
LOG_INFO("[BOOT]", "Reset reason: %d", reason);  // 1=POWERON, 12=RTC_SW_CPU_RST, ...
```

### 6.4 Kontrolowany restart zamiast czekania na watchdoga

Tak robi `main.cpp` po wykryciu, że urządzenie zostało usunięte z platformy:

```cpp
if (deviceIdentity.needsReprovisioning()) {
  LOG_INFO("[BOOT]", "Device deleted from platform, restarting...");
  delay(1000);   // czas na wypchnięcie logu
  esp_restart();
}
```

## 7. Troubleshooting

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| Watchdog nigdy nie wyzwala | Zadanie `loopTask` nie jest zapisane do Task WDT albo limit jest zbyt długi | Sprawdź, czy `CONFIG_ESP_TASK_WDT_TIMEOUT_S` trafiło do buildu (`pio run -v`). Zob. zastrzeżenie w [`02 §4`](./02_modem_a7670e_communication.md#4-procedura-zdalnego-resetu-libmodempowerhardreset) |
| Watchdog wyzwala w trakcie recovery poziomu 2 | ~17 s blokady w `hardReset()` przy limicie 15 s | Nie skracaj limitu; docelowo rozbij `ModemPower` na kroki nieblokujące |
| Restart w pętli | Poziom 3 wyzwala się szybciej, niż urządzenie zdąża wysłać pierwszą paczkę | Sprawdź, czy telemetria w ogóle rusza — bez `initializeTelemetry()` licznik RTC nie jest zerowany. Rozważ zwiększenie `MAX_RESTART_ATTEMPTS` |
| Urządzenie wisi bez restartu po nieudanym starcie modemu | `setup()` kończy się bez utworzenia `telemetrySender`, a `loop()` tego nie ponawia | Znana usterka U-3, [`00_przeglad.md §10`](./00_przeglad.md#10-usterki-w-kodzie-znalezione-przy-uzgadnianiu-dokumentacji) |
| Licznik RTC nie rośnie | Był zanik zasilania, nie soft reset — pamięć RTC nie przeżywa odcięcia zasilania | To zachowanie poprawne. Do rozróżnienia obu przypadków potrzebny `esp_reset_reason()` (§6.3) |

## 8. Referencje

- **ESP32 Watchdogs:** https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/wdts.html
- **FreeRTOS Task WDT:** https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/task_wdt.html
- **Przyczyny resetu:** `esp_reset_reason()` w `esp_system.h`
- **Implementacja recovery:** [`lib/Watchdog/src/Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L11-L45)
- **Stan w pamięci RTC:** [`include/RtcState.h`](../../../firmware/include/RtcState.h)
