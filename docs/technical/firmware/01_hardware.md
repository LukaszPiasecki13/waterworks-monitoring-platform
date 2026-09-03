# Mapa sprzętowa gatewaya

Źródło prawdy dla fizycznych połączeń ESP32-S3. Przed dotknięciem GPIO — sprawdź tutaj, nie zgaduj.
Schematy graficzne i szerszy kontekst: [`00_przeglad.md`](./00_przeglad.md).

Status każdej pozycji jest oznaczony w tabeli, wg legendy z
[`00_przeglad.md §1`](./00_przeglad.md#1-legenda-statusów):

- **zweryfikowane w kodzie** — pin jest używany w firmware ([`Config.h`](../../../firmware/include/Config.h)
  + biblioteka faktycznie go steruje). Nie mówi nic o tym, czy działa na płytce.
- **zweryfikowane na sprzęcie** — potwierdzone uruchomieniem, z datą próby.
- **draft** — plan albo pozostałość po wcześniejszej wersji; brak kodu lub brak potwierdzenia.

## 1. Komponenty

| Komponent | Rola | Status |
|---|---|---|
| **ESP32-S3-DevKitC-1** | główny mikrokontroler | zweryfikowane w kodzie; wariant modułu (N8R2/N8R8/N16R8) **do potwierdzenia** |
| **A7670E-FASE na płytce KAmod** | modem LTE (UART, komendy AT) | zweryfikowane na sprzęcie 2026-08-22 — [`ModemLink`](../../../firmware/lib/ModemLink/src/ModemLink.cpp), [`ModemPower`](../../../firmware/lib/ModemPower/src/ModemPower.cpp), zob. [`02_modem_a7670e_communication.md`](./02_modem_a7670e_communication.md) |
| **RGB LED on-board (WS2812, GPIO48)** | sygnalizacja stanu | zweryfikowane w kodzie — [`StatusLed`](../../../firmware/lib/StatusLed/src/StatusLed.cpp), Adafruit_NeoPixel |
| **PT100 + MAX31865** | czujnik temperatury (RTD przez konwerter SPI) | zweryfikowane na sprzęcie 2026-08-24 — [`PT100Sensor`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp), `adafruit/Adafruit MAX31865` |
| **PT-506 + ADS1015** | czujnik ciśnienia 4-20 mA przez zewnętrzny przetwornik A/C | **draft — nie istnieje w firmware** (zob. [§3](#3-ścieżka-ciśnienia--draft)) |

**Ważne sprostowanie.** Wcześniejsze wersje tego dokumentu twierdziły, że „PT-506 wysyła wartości
syntetyczne (funkcja sinus)". To **nieprawda w obecnym kodzie**: po refaktorze na interfejs
[`ISensor`](../../../firmware/lib/Sensor/include/ISensor.h) jedynym czujnikiem rejestrowanym w
[`initializeSensors()`](../../../firmware/src/main.cpp#L94-L99) jest `PT100Sensor`. W repozytorium
nie ma klasy czujnika ciśnienia, nie ma sterownika ADC, nie ma wywołania `analogRead()` ani biblioteki
I²C. Urządzenie **nie wysyła dziś żadnej wartości ciśnienia** — ani prawdziwej, ani udawanej.

## 2. Piny — zweryfikowane w kodzie

| GPIO | Funkcja | Podłączone do | Źródło |
|---|---|---|---|
| 17 | UART1 TX | A7670E RX (pin 8 złącza HAT) | `MODEM_TX_PIN`, [`Config.h:17`](../../../firmware/include/Config.h#L17) |
| 18 | UART1 RX | A7670E TX (pin 10 złącza HAT) | `MODEM_RX_PIN`, [`Config.h:16`](../../../firmware/include/Config.h#L16) |
| 4 | PWRKEY | A7670E (pin 7 złącza HAT) | `MODEM_PWRKEY_PIN`, [`Config.h:18`](../../../firmware/include/Config.h#L18) |
| 5 | RESET | A7670E (pin 12 złącza HAT) | `MODEM_RESET_PIN`, [`Config.h:19`](../../../firmware/include/Config.h#L19) |
| 11 | SPI MOSI | MAX31865 SDI | `PT100_SPI_MOSI`, [`Config.h:27`](../../../firmware/include/Config.h#L27) |
| 12 | SPI SCK | MAX31865 CLK | `PT100_SPI_SCK`, [`Config.h:29`](../../../firmware/include/Config.h#L29) |
| 13 | SPI MISO | MAX31865 SDO | `PT100_SPI_MISO`, [`Config.h:28`](../../../firmware/include/Config.h#L28) |
| 14 | SPI CS | MAX31865 CS | `PT100_SPI_CS`, [`Config.h:26`](../../../firmware/include/Config.h#L26) |
| 48 | RGB LED (WS2812, on-board) | — | `LED_PIN`, [`Config.h:15`](../../../firmware/include/Config.h#L15); zob. [§4](#4-led-rgb-gpio48) |
| — | POWER_ENABLE | nieużywane (`-1`) | `MODEM_POWER_ENABLE_PIN`, [`Config.h:20`](../../../firmware/include/Config.h#L20) — moduł A7670E na tej płytce nie ma osobnej linii enable |

Wszystkie cztery piny SPI są przekazywane jawnie do `SPI.begin()` w
[`PT100Sensor::init()`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L14) — nie polegamy na
domyślnych pinach frameworku. Sąsiadują fizycznie na listwie, co ułatwia okablowanie.

## 3. Ścieżka ciśnienia — draft

Docelowo przetwornik **PT-506** pracuje w pętli 4-20 mA zasilanej z szyny 24 V, a prąd zamieniany jest
na napięcie rezystorem pomiarowym na wejściu **AIN0 układu ADS1015** (przetwornik A/C na magistrali
I²C). Nic z tego nie ma dziś odpowiednika w firmware.

### 3.1. Rezystor pomiarowy — 136 Ω, nie 250 Ω

Wcześniejsze wersje tej dokumentacji podawały **250 Ω** na wejściu ADC. Ta wartość jest **porzucona**:

| R | U przy 4 mA | U przy 20 mA | Werdykt |
|---|---|---|---|
| 250 Ω | 1,00 V | **5,00 V** | Powyżej napięcia zasilania 3,3 V — przekracza absolutne maksimum wejścia przetwornika. Odrzucone. |
| **136 Ω** (2 × 68 Ω) | 0,54 V | **2,72 V** | W zakresie PGA ±4,096 V układu ADS1015 i poniżej napięcia zasilania. Przyjęte. |

To rachunek z danych katalogowych, **nie pomiar** — do potwierdzenia przy pierwszym uruchomieniu
kanału ciśnienia.

Porzucony jest też cały wariant „wejście ADC wbudowane w ESP32-S3" (GPIO1 / ADC1_CH0): poza problemem
napięcia powyżej, wewnętrzny przetwornik ESP32-S3 ma gorszą liniowość niż osobny układ. Nie
przenosimy tego wariantu dalej.

### 3.2. Czego nie wolno tu wpisać

**Numery GPIO dla SDA i SCL układu ADS1015 nie są ustalone.** Nie ma ich w `Config.h`, a wybór zależy
od wariantu modułu ESP32-S3 (patrz [§5](#5-piny-zajęte-i-ryzykowne)). Do czasu rozstrzygnięcia na
płytce w tym dokumencie **nie pojawia się żaden numer** — pozycje H-4 i H-5 na liście
[„do sprawdzenia na sprzęcie"](./00_przeglad.md#9-do-sprawdzenia-na-sprzęcie).

## 4. LED RGB (GPIO48)

**WS2812 NeoPixel** sterowany przez **Adafruit_NeoPixel**
([`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp)). Status:
zweryfikowane w kodzie.

| Sygnał | Wzór | Kiedy |
|---|---|---|
| Sukces | **1 mignięcie** zielone (0, 255, 0), 80 ms | `blinkSuccess()` — udana wysyłka telemetrii, koniec inicjalizacji |
| Błąd | **3 mignięcia** zielone (ten sam kolor), 120 ms | `blinkError()` — nieudana wysyłka, brak łączności, błąd startu modemu |

Nośnikiem znaczenia jest **liczba mignięć, nie kolor** — oba wzory używają tego samego zielonego.
Diagnostyka wzrokowa modemu to osobne diody na płytce HAT (zob. [§7](#7-a7670e-fase--moduł-kamod-lte-cat1-gnss-hat)).

`pixels_->begin()` jest celowo odroczone z konstruktora do `initializePixels()` wołanego w `setup()`,
żeby nie blokować przed inicjalizacją watchdoga.

## 5. Piny zajęte i ryzykowne

Poniższe wynika z **karty katalogowej ESP32-S3**, nie z oględzin tej konkretnej płytki — status:
draft, do potwierdzenia (pozycja H-4 na liście „do sprawdzenia na sprzęcie").

| GPIO | Dlaczego uważać |
|---|---|
| 0, 3, 45, 46 | Piny strappingowe — stan przy starcie decyduje o trybie bootowania |
| 19, 20 | USB D− / D+ na dev-kicie |
| 26–32 | Magistrala flash SPI0 |
| 33–37 | Zajęte przez PSRAM w wariantach z pamięcią w trybie oktalnym (N8R8, N16R8) |
| 48 | Zajęte przez RGB LED on-board |

Zanim przypiszesz nowy peryferial do GPIO, sprawdź go na tej liście i dopisz go do
[`Config.h`](../../../firmware/include/Config.h) — nie tylko do dokumentacji.

## 6. Interfejsy

| Interfejs | Zastosowanie | Status |
|---|---|---|
| **UART1** (115200 8N1) | ESP32-S3 ↔ A7670E, komendy AT przez TinyGSM | zweryfikowane na sprzęcie 2026-08-22 |
| **SPI** (4-przewodowe, jedno urządzenie na magistrali) | ESP32-S3 ↔ MAX31865 | zweryfikowane na sprzęcie 2026-08-24 |
| **Pętla prądowa 4-20 mA** | PT-506 → rezystor 136 Ω → AIN0 układu ADS1015 | **draft** — brak w kodzie, zob. [§3](#3-ścieżka-ciśnienia--draft) |
| **I²C** | ESP32-S3 ↔ ADS1015 | **draft** — piny nieustalone |
| **USB-C** | programowanie i logi szeregowe, 115200 8N1 | zweryfikowane w kodzie |

## 7. A7670E-FASE — moduł KAmod LTE CAT1-GNSS (HAT)

Konkretny moduł modemu użyty w projekcie to **KAmod LTE CAT1-GNSS z A7670E-FASE** — płytka typu
**HAT na 40-pinowe złącze GPIO Raspberry Pi**, nie gołe piny modemu. Sygnały opisane w dokumentacji
producenta noszą więc nazwy pinów RPi (numer fizyczny + funkcja BCM), a nie bezpośrednio „TXD modemu".
Poniżej przełożenie tych sygnałów na piny ESP32-S3, zgodnie z tym, jak okablowano
[`Config.h`](../../../firmware/include/Config.h).

**Status tej tabeli: draft.** Kod definiuje wyłącznie numery GPIO po stronie ESP32-S3; sposób
podłączenia do 40-pinowego złącza HAT-a nie wynika z repozytorium i wymaga oględzin okablowania
(pozycja H-3 na liście „do sprawdzenia na sprzęcie").

| Sygnał HAT (wg dok. RPi) | Nr fizyczny pinu złącza 40-pin | Kierunek (z perspektywy modemu) | ESP32-S3 GPIO (wg `Config.h`) |
|---|---|---|---|
| TXD modemu (opisane jako RXD/GPIO15 na RPi) | pin 10 | wyjście z modemu | 18 (`MODEM_RX_PIN`) |
| RXD modemu (opisane jako TXD/GPIO14 na RPi) | pin 8 | wejście do modemu | 17 (`MODEM_TX_PIN`) |
| RST (opisane jako GPIO18 na RPi) | pin 12 | wejście do modemu, aktywne stanem wysokim | 5 (`MODEM_RESET_PIN`) |
| PWK / PWRKEY (opisane jako GPIO4 na RPi) | pin 7 | wejście do modemu, aktywne stanem wysokim | 4 (`MODEM_PWRKEY_PIN`) |
| +5V | piny 2, 4 | zasilanie modułu | **zewnętrzne 5 V**, nie z ESP32 (patrz uwaga niżej) |
| GND | piny 6, 9, 14, 20, 25, 30, 34, 39 | masa | wspólna masa z ESP32-S3 |

### Uwagi krytyczne przed podłączeniem

- **Zasilanie 5 V / min. 2 A.** Moduł wymaga zasilania 5 V o wydajności min. 2 A (szczyty poboru przy
  transmisji LTE). USB dev-kitu ESP32-S3 tego nie zapewni w sposób pewny — potrzebne osobne zasilanie
  5 V podpięte do pinów 2/4 złącza HAT, ze wspólną masą z ESP32-S3. Pełne drzewo zasilania:
  [`00_przeglad.md §5`](./00_przeglad.md#5-drzewo-zasilania).
- **Zworki J2 muszą być założone.** Wg dokumentacji producenta: *„nie wszystkie sygnały sterujące
  (TXD, RXD, PWK i RST) muszą być połączone"* ze złączem 40-pin — każdy z tych czterech sygnałów ma
  osobną zworkę na J2. Bez założonej zworki dany sygnał nie pojawi się na pinie złącza, mimo
  poprawnego okablowania GPIO ESP32-S3.
- **Zworka J_APWK (spód płytki).** Steruje automatycznym pulsem power-on modemu przy starcie
  zasilania. [`ModemPower::powerOn()`](../../../firmware/lib/ModemPower/src/ModemPower.cpp) sam
  generuje puls na PWRKEY — jeśli J_APWK nie jest przecięta, może dojść do podwójnego/konfliktowego
  power-on. **Do zweryfikowania fizycznie na płytce** (pozycja H-1).
- **Antena LTE i GNSS to osobne złącza U.FL** — moduł ma dwie anteny, nie jedną. GNSS nieużywany w
  obecnym firmware (brak kodu GPS w repozytorium).
- **SIM**: gniazdo micro SIM, obsługuje karty 1,8 V / 3,0 V.
- **Diody LED na płytce HAT** (niezależne od `StatusLed`/GPIO48 na ESP32): PWR (D5, obecność
  zasilania), STA (D3, stan aktywności modemu), NET (D4, status sieci) — przydatne do diagnostyki
  wzrokowej niezależnie od logów.

### Źródła (dokumentacja producenta, nie repo)

- [Karta produktu KAmod na kamami.pl](https://kamami.pl/moduly-komunikacyjne/1200196-kamod-lte-cat1-gnss-hat-gsmgprsgnss-z-modulem-a7670e-fase-do-raspberry-pi-5902186333727.html)
- [Instrukcja PL (PDF)](https://download.kamami.pl/p1200196-KAmod%20LTE%20CAT1-GNSS%20z%20modu%C5%82em%20A7670E-FASE%20%28PL%29-2364.pdf)
- [Wiki KamamiLabs](https://wiki.kamamilabs.com/index.php?title=KAmod_LTE_CAT1-GNSS_z_modu%C5%82em_A7670E-FASE_(PL))

## 8. Znane ograniczenia

- **Kanał ciśnienia nie istnieje** — brak klasy czujnika, sterownika ADC i pinów I²C. Zob.
  [§3](#3-ścieżka-ciśnienia--draft).
- **Zestaw deweloperski, nie wyrób** — brak obudowy, ochrony przepięciowej i separacji galwanicznej
  wejść. Konsekwencje formalne: [`01_plan_biznesowy.md §6.2.1`](../../business/01_plan_biznesowy.md).
- **Bilans prądowy nie był liczony.** Wymóg 2 A dla modułu HAT pochodzi z dokumentacji producenta, nie
  z pomiaru na stanowisku.
- **Pełna lista pozycji wymagających płytki**: [`00_przeglad.md §9`](./00_przeglad.md#9-do-sprawdzenia-na-sprzęcie).
