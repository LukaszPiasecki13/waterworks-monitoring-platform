# Mapa sprzętowa gatewaya

Źródło prawdy dla fizycznych połączeń ESP32-S3. Przed dotknięciem GPIO — sprawdź tutaj, nie zgaduj.

Status każdej pozycji jest oznaczony w tabeli:
- **zweryfikowane** — pin jest używany w kodzie firmware ([`Config.h`](../../../firmware/include/Config.h) + biblioteka go faktycznie steruje).
- **draft** — planowane podłączenie, nieobecne w obecnym kodzie firmware (brak biblioteki/odczytu).

## 1. Komponenty

| Komponent | Rola | Status w firmware |
|---|---|---|
| **ESP32-S3-DevKitC-1** | główny mikrokontroler | zweryfikowane |
| **A7670E** | modem LTE-M/2G (UART, AT-command) | zweryfikowane — [`ModemLink`](../../../firmware/lib/ModemLink/src/ModemLink.cpp), [`ModemPower`](../../../firmware/lib/ModemPower/src/ModemPower.cpp) |
| **RGB LED on-board (WS2812, GPIO48)** | sygnalizacja stanu | zweryfikowane — [`StatusLed`](../../../firmware/lib/StatusLed/src/StatusLed.cpp), Adafruit_NeoPixel |
| **PT-506** | czujnik ciśnienia, wyjście 4-20mA | **draft, niepodłączony w kodzie** — brak biblioteki odczytu, brak `analogRead()` w repo |
| **PT100 + MAX31865** | czujnik temperatury (RTD przez konwerter SPI) | **zweryfikowane** — [`TelemetryPayload`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp), `adafruit/Adafruit MAX31865 @ 1.5.0` |

`TelemetryPayload` od wersji 2026-08-24 odczytuje PT100 przez MAX31865 (SPI). PT-506 wciąż generuje wartości syntetyczne (funkcja sinus).

## 2. Piny — zweryfikowane w kodzie

| GPIO | Funkcja | Podłączone do | Źródło |
|---|---|---|---|
| 17 | UART1 TX | A7670E RX | `MODEM_TX_PIN`, [`Config.h:17`](../../../firmware/include/Config.h#L17) |
| 18 | UART1 RX | A7670E TX | `MODEM_RX_PIN`, [`Config.h:16`](../../../firmware/include/Config.h#L16) |
| 4 | PWRKEY | A7670E | `MODEM_PWRKEY_PIN`, [`Config.h:18`](../../../firmware/include/Config.h#L18) |
| 5 | RESET | A7670E | `MODEM_RESET_PIN`, [`Config.h:19`](../../../firmware/include/Config.h#L19) |
| 11 | SPI MOSI | MAX31865 (PT100) | `PT100_SPI_MOSI`, [`Config.h:27`](../../../firmware/include/Config.h#L27) |
| 12 | SPI SCK | MAX31865 (PT100) | `PT100_SPI_SCK`, [`Config.h:29`](../../../firmware/include/Config.h#L29) |
| 13 | SPI MISO | MAX31865 (PT100) | `PT100_SPI_MISO`, [`Config.h:28`](../../../firmware/include/Config.h#L28) |
| 14 | SPI CS | MAX31865 (PT100) | `PT100_SPI_CS`, [`Config.h:26`](../../../firmware/include/Config.h#L26) — Chip Select |
| 48 | RGB LED (WS2812, on-board) | — | `LED_PIN`, [`Config.h:15`](../../../firmware/include/Config.h#L15); zob. [§4](#4-led-rgb-gpio48) |
| — | POWER_ENABLE | nieużywane (`-1`) | `MODEM_POWER_ENABLE_PIN`, [`Config.h:20`](../../../firmware/include/Config.h#L20) — moduł A7670E na tej płytce nie ma osobnej linii enable |

## 3. Piny — draft (planowane, nie w kodzie)

Poniższe piny pochodzą z pierwotnej wersji tego dokumentu i **nie mają odpowiednika w obecnym firmware** (brak biblioteki sensora, brak inicjalizacji ADC w `src/main.cpp`). Do potwierdzenia na fizycznej płytce przed lutowaniem i przed napisaniem sterownika — część GPIO na ESP32-S3-DevKitC-1 może być zajęta pod PSRAM/flash lub pełnić funkcję strappingową, zależnie od wariantu modułu.

| GPIO | Funkcja | Podłączone do | Uwagi |
|---|---|---|---|
| 1 | ADC1_CH0 | PT-506 (4-20mA) | przez rezystor 250Ω |
| 2 | ADC1_CH1 | dzielnik napięcia szyny 24 V | **propozycja** z [09_budzet_energetyczny.md §5.2](./09_budzet_energetyczny.md#52-dzielnik-napięcia--dwa-warianty) — wariant dla zestawu **bez** ADS1015. Dzielnik 100 kΩ / 8,2 kΩ + 100 nF, tłumienie `ADC_ATTEN_DB_12`. Wybrany, bo należy do ADC1, nie jest pinem strappingowym ESP32-S3 (GPIO0/3/45/46) i nie koliduje z SPI MAX31865 |

**Uwaga**: Piny PT100/MAX31865 (od 2026-08-24) są jawnie zdefiniowane w `Config.h` i przekazywane do `SPI.begin()`: 11 (MOSI), 12 (SCK), 13 (MISO), 14 (CS). Wszystkie 4 piny SPI sąsiadują fizycznie, co ułatwia okablowanie. Zob. [sekcja 2](#2-piny--zweryfikowane-w-kodzie) i [05_pt100_temperature_sensor.md](./05_pt100_temperature_sensor.md).

## 4. LED RGB (GPIO48)

**WS2812 NeoPixel** sterowany via **Adafruit_NeoPixel** (biblioteka dodana w `platformio.ini`). Blink LED:
- **Success**: pojedynczy blink zielony (0, 255, 0)
- **Error**: trzy blinki zielone

Zapalanie LED: `pixels.setPixelColor(0, pixels.Color(R, G, B)); pixels.show();`

## 5. Znane ograniczenia

- **PT-506 (czujnik ciśnienia) — draft.** Brak biblioteki odczytu ADC; telemetria PT-506 wciąż wysyła dane syntetyczne (sinus).
- **PT100 (czujnik temperatury) — zweryfikowany.** Odczyt przez MAX31865 (SPI), biblioteka `adafruit/Adafruit MAX31865`. Zob. [05_pt100_temperature_sensor.md](./05_pt100_temperature_sensor.md) po szczegóły.
- **Brak pomiaru napięcia zasilania i detekcji zaniku 230 V.** Kod błędu `POWER_LOW` istnieje w [`sensor_registry.yaml`](../../../sensor_registry.yaml), ale nic go nie ustawia. Projekt dzielnika, progów i ścieżki transmisji zdarzenia — [09_budzet_energetyczny.md §5](./09_budzet_energetyczny.md#5-detekcja-zaniku-zasilania-i-pomiar-napięcia).
- **Brak kondensatora bulk na szynie 5 V przy złączu HAT-a.** Modem wymaga szczytowo 2 A, a przetwornica nie nadąża za impulsem nadawania GSM (577 µs). Obliczenie i wymagana wartość — [09_budzet_energetyczny.md §3.3](./09_budzet_energetyczny.md#33-pojemność-bulk-na-szynie-5-v--obliczenie).
- **Wariant modułu ESP32-S3-WROOM-1 (z PSRAM czy bez) nie jest udokumentowany.** Rozstrzyga o górnym zakresie pracy: 65 °C (R8/R16V) albo 85 °C. Zob. [09_budzet_energetyczny.md §8](./09_budzet_energetyczny.md#8-temperatura-pracy).

## 5a. Zasilanie

Pełne drzewo zasilania (230 V AC → 24 V DC → 5 V → 3,3 V), bilans prądowy per faza pracy, dobór przetwornicy, wymagania dla przewodów i pojemności buforowej, podtrzymanie przy zaniku 230 V oraz zakresy temperatur komponentów: **[09_budzet_energetyczny.md](./09_budzet_energetyczny.md)**.

Elementy toru zasilania (zasilacz DIN 24 V / 1 A, przetwornica XL4015 24 → 5 V) **nie są dziś potwierdzone w repozytorium** — pochodzą z opisu zadania. Po weryfikacji na fizycznym zestawie powinny trafić do tego dokumentu jako pełnoprawna sekcja.

## 6. Interfejsy

- **Pętla 4-20mA (PT-506, draft)**: prąd zamieniany na napięcie rezystorem 250Ω przed wejściem ADC.
- **SPI (PT100/MAX31865, draft)**: standardowe 4-wire SPI, jedno urządzenie na magistrali.

## 7. A7670E-FASE — moduł KAmod LTE CAT1-GNSS (HAT)

Konkretny moduł modemu użyty w projekcie to **KAmod LTE CAT1-GNSS z A7670E-FASE** — płytka typu **HAT na 40-pinowe złącze GPIO Raspberry Pi**, nie gołe piny modemu. Sygnały opisane w dokumentacji producenta noszą więc nazwy pinów RPi (numer fizyczny + funkcja BCM), a nie bezpośrednio "TXD modemu" itd. Poniżej przełożenie tych sygnałów na piny ESP32-S3, zgodnie z tym, jak faktycznie okablowano [`Config.h`](../../../firmware/include/Config.h) (status: **draft** — to przełożenie nie jest zweryfikowane w kodzie, kod tylko definiuje docelowe GPIO na ESP32-S3, a nie sposób podłączenia do 40-pinowego złącza HAT-a).

| Sygnał HAT (wg dok. RPi) | Nr fizyczny pinu złącza 40-pin | Kierunek (z perspektywy modemu) | ESP32-S3 GPIO (wg `Config.h`) |
|---|---|---|---|
| TXD modemu (opisane jako RXD/GPIO15 na RPi) | pin 10 | wyjście z modemu | 18 (`MODEM_RX_PIN`) |
| RXD modemu (opisane jako TXD/GPIO14 na RPi) | pin 8 | wejście do modemu | 17 (`MODEM_TX_PIN`) |
| RST (opisane jako GPIO18 na RPi) | pin 12 | wejście do modemu, aktywne stanem wysokim | 5 (`MODEM_RESET_PIN`) |
| PWK / PWRKEY (opisane jako GPIO4 na RPi) | pin 7 | wejście do modemu, aktywne stanem wysokim | 4 (`MODEM_PWRKEY_PIN`) |
| +5V | piny 2, 4 | zasilanie modułu | **zewnętrzne 5V**, nie z ESP32 (patrz uwaga niżej) |
| GND | piny 6, 9, 14, 20, 25, 30, 34, 39 | masa | wspólna masa z ESP32-S3 |

### Uwagi krytyczne przed podłączeniem

- **Zasilanie 5V / min. 2A.** Moduł wymaga zasilania 5V o wydajności min. 2A (szczyty poboru przy transmisji LTE). USB dev-kitu ESP32-S3 tego nie zapewni w sposób pewny — potrzebne osobne zasilanie 5V podpięte do pinów 2/4 złącza HAT, ze wspólną masą z ESP32-S3.
- **Zworki J2 muszą być założone.** Wg dokumentacji: *"nie wszystkie sygnały sterujące (TXD, RXD, PWK i RST) muszą być połączone"* ze złączem 40-pin — każdy z tych czterech sygnałów ma osobną zworkę na J2. Bez założonej zworki dany sygnał nie pojawi się na pinie złącza, mimo poprawnego okablowania GPIO ESP32-S3.
- **Zworka J_APWK (spód płytki).** Steruje automatycznym pulsem power-on modemu przy starcie zasilania. [`ModemPower::powerOn()`](../../../firmware/lib/ModemPower/src/ModemPower.cpp) sam generuje puls na PWRKEY — jeśli J_APWK nie jest przecięta, może dojść do podwójnego/konfliktowego power-on. Do zweryfikowania fizycznie na płytce.
- **Antena LTE i GNSS to osobne złącza U.FL** — moduł ma dwie anteny (LTE i GNSS), nie jedną. GNSS nieużywany w obecnym firmware (brak kodu GPS w repo).
- **SIM**: gniazdo micro SIM, obsługuje karty 1.8V/3.0V.
- **Diody LED na płytce HAT** (niezależne od `StatusLed`/GPIO48 na ESP32): PWR (D5, obecność zasilania), STA (D3, stan aktywności modemu), NET (D4, status sieci) — przydatne do diagnostyki wzrokowej niezależnie od logów.

### Źródła (dokumentacja producenta, nie repo)

- [Karta produktu KAmod na kamami.pl](https://kamami.pl/moduly-komunikacyjne/1200196-kamod-lte-cat1-gnss-hat-gsmgprsgnss-z-modulem-a7670e-fase-do-raspberry-pi-5902186333727.html)
- [Instrukcja PL (PDF)](https://download.kamami.pl/p1200196-KAmod%20LTE%20CAT1-GNSS%20z%20modu%C5%82em%20A7670E-FASE%20%28PL%29-2364.pdf)
- [Wiki KamamiLabs](https://wiki.kamamilabs.com/index.php?title=KAmod_LTE_CAT1-GNSS_z_modu%C5%82em_A7670E-FASE_(PL))
