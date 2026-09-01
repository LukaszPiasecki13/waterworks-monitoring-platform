# Analiza portu ESP32-S3 → ESP-WROOM-32 (klasyczny ESP32)

> Analiza wykonalności i opłacalności przeniesienia firmware gatewaya z ESP32-S3-DevKitC-1 na klasyczny ESP32 (ESP-WROOM-32).
> **Zlecenie B-10.** Dokument kończy zlecenie — implementacja portu jest poza jego zakresem, niezależnie od werdyktu.
>
> **Status: analiza statyczna kodu + dokumentacji Espressif, bez weryfikacji na sprzęcie i bez buildu.** Zakres i wiarygodność każdej liczby opisuje [§2](#2-metoda-i-granice-tej-analizy). Wszystko, czego nie dało się zweryfikować w środowisku, jest oznaczone jako **do zmierzenia** albo **do zweryfikowania** i zebrane w [§11](#11-czego-nie-dało-się-zweryfikować--lista-do-domknięcia).
>
> Data: 2026-09-01

---

## 1. Werdykt

**Port jest technicznie łatwy i ekonomicznie nieopłacalny przy obecnej skali. Rekomendacja: nie portować.**

Trzy zdania uzasadnienia:

1. **Technicznie** — nie ma żadnej blokady. Zależności od S3 sprowadzają się do **ośmiu numerów GPIO i jednej diody**. Punkt, który brief wskazał jako krytyczny (kryptografia), okazał się **nie być zależnością od S3 w ogóle**: ani ESP32, ani ESP32-S3 nie mają sprzętowego akceleratora ECC, a `DeviceIdentity` liczy P-256 w całości programowo na obu chipach ([§4.3](#43-kryptografia--punkt-krytyczny-briefu-okazał-się-nie-istnieć)).
2. **Ekonomicznie** — przy najbardziej optymistycznym możliwym zestawie założeń (największa realna różnica ceny modułu, najniższy koszt pracy) próg opłacalności wychodzi **~40 sztuk**, a przy realistycznym **100–300 sztuk** ([§7](#7-próg-opłacalności)). Deklarowana skala to *kilka prototypów*. Rozjazd wynosi jeden–dwa rzędy wielkości i **nie zależy od tego, czy trafiłem w aktualną cenę modułu** — pokazuje to tabela wrażliwości.
3. **Strategicznie** — hipoteza z briefu, że droga do wersji przemysłowej i tak prowadzi przez klasyczny ESP32, **nie potwierdza się**. Rynek przemysłowych sterowników DIN jest podzielony: część rodzin stoi na ESP32-WROOM-32, ale nowsze (KinCony, EQSP32, LILYGO T-Connect Pro i inne) stoją na ESP32-S3 ([§9](#9-alternatywa-przemysłowe-płytki-din--czy-port-i-tak-będzie-potrzebny)). Wybór płytki przemysłowej jest **zmienną swobodną**, nie ograniczeniem — więc zamiast portować, wystarczy dopisać „rdzeń ESP32-S3" do kryteriów wyboru wariantu W3 w [B-01](../../plan/01_briefy_dla_agentow.md).

**Co zrobić zamiast portu:** jedno- lub dwugodzinna zmiana w `StatusLed` ([§4.2](#42-led-statusu)) i przypięcie kryterium „rdzeń S3" do zlecenia B-01 ([§10](#10-rekomendacja-i-warunki-które-zmieniłyby-werdykt)). To wyczerpuje wartość, jaką port miał dostarczyć, przy ~1% jego kosztu.

**Co odwróciłoby werdykt** — trzy konkretne warunki, wypisane w [§10](#10-rekomendacja-i-warunki-które-zmieniłyby-werdykt).

---

## 2. Metoda i granice tej analizy

Brief wymaga: *„Nie zakładaj, że coś działa — sprawdź w kodzie i w dokumentacji Espressif"*. Tak zrobiłem, ale środowisko nałożyło dwa ograniczenia, które trzeba znać przed czytaniem liczb.

### 2.1 Co zostało zweryfikowane bezpośrednio

| Obszar | Źródło | Wiarygodność |
|---|---|---|
| Użycie GPIO, peryferiów, API | pełny odczyt `firmware/` (2 516 linii, wszystkie 21 plików `.cpp`/`.h` + `platformio.ini`) | **wysoka** — kod, nie dokumentacja |
| Możliwości SoC (ECC, MPI, SHA, HMAC, DS, GPIO, RTC) | `soc_caps.h` dla `esp32` i `esp32s3` z ESP-IDF v5.3 | **wysoka** — źródło Espressif, nie strona WWW |
| Domyślne włączenie akceleracji sprzętowej w mbedTLS | `components/mbedtls/Kconfig`, ESP-IDF v5.3 | **wysoka** |
| Ograniczenia GPIO klasycznego ESP32 | `docs/en/api-reference/peripherals/gpio/esp32.inc` (źródło dokumentacji ESP-IDF) + `components/soc/esp32/gpio_periph.c` | **wysoka** |
| Rozmiary partycji, limity RAM, PSRAM | manifesty płytek `platform-espressif32` + `tools/partitions/*.csv` z arduino-esp32 | **wysoka** |
| Mapowanie `Serial` na UART0 vs USB CDC | `cores/esp32/HardwareSerial.h` z arduino-esp32 | **wysoka** |
| `LED_BUILTIN` per wariant płytki | `variants/*/pins_arduino.h` z arduino-esp32 | **wysoka** |

### 2.2 Czego nie dało się zweryfikować i dlaczego

| Czego brakuje | Powód | Jak to obeszedłem |
|---|---|---|
| **Statystyki RAM/flash z `pio run -e esp32-s3`** | rejestr PlatformIO zablokowany przez proxy sieciowe środowiska (`HTTPClientError` przy `pio pkg install`) — build niewykonalny | analiza strukturalna: policzone rozmiary buforów z kodu + porównanie **limitów partycji**, które są liczbami dokładnymi ([§4.4](#44-pamięć)). Realna liczba jest **jedyną brakującą wielkością blokującą** i wymaga jednego polecenia — [§11](#11-czego-nie-dało-się-zweryfikować--lista-do-domknięcia) |
| **Aktualne ceny modułów** | domeny dystrybutorów (Botland, Kamami, TME) zablokowane przez proxy | **rachunek przeprowadzony parametrycznie**: próg jest funkcją różnicy ceny Δ, z tabelą wrażliwości dla pełnego realnego zakresu Δ ([§7](#7-próg-opłacalności)). Werdykt jest niezmienniczy względem Δ w całym tym zakresie |
| **Czasy krypto zmierzone na obu chipach** | brak sprzętu i brak buildu | punkt odniesienia z repo (~2–3 s na S3, [`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md)) + argument architektoniczny (identyczna ścieżka programowa, identyczny zegar) → oszacowanie z jawnym marginesem i procedurą pomiaru ([§4.3](#43-kryptografia--punkt-krytyczny-briefu-okazał-się-nie-istnieć)) |

**Konsekwencja dla czytelnika:** werdykt z §1 **nie opiera się** na żadnej z trzech niezweryfikowanych wielkości. §7 pokazuje, że dla każdej wartości Δ w realnym zakresie wniosek jest ten sam. Gdyby jednak flash okazał się nie mieścić (§4.4), zmienia się *koszt* portu, nie werdykt.

---

## 3. Korekty do założeń briefu

Brief podał listę punktów zaczepienia jako „wyjściową, nie wyczerpującą". Trzy z nich nie zgadzają się ze stanem kodu na dziś, a jeden jest niepełny. Odnotowuję to, bo zmienia zakres pracy.

| Założenie briefu | Stan faktyczny | Skutek |
|---|---|---|
| *„`Config.h` używa GPIO 4, 5, **8, 9**, 11, 12, 13, 14, 17, 18, 48"*, *„wymusza przemapowanie **I2C (dziś 8/9)**"* | **W firmware nie ma I2C.** `Config.h` definiuje 9 pinów: 4, 5, 11, 12, 13, 14, 17, 18, 48 ([`Config.h:15-29`](../../../firmware/include/Config.h#L15-L29)). Grep po `firmware/` na `Wire`, `I2C`, `SDA`, `SCL`, `ADS1015`, `ADS1115` daje **zero trafień**. Tak samo `analogRead` i `ADC` | zakres portu **mniejszy** niż zakładano — nie ma magistrali I2C do przemapowania. Wzmianki o ADS1015 pochodzą z briefu B-11 i starszej wersji [`01_hardware.md`](./01_hardware.md); obecna wersja §3 wymienia tylko GPIO 1 (ADC1_CH0) dla PT-506, ze statusem **draft** |
| *„GPIO 6–11 są zajęte przez flash SPI"* | Prawda, ale **niepełna**. ESP-IDF wymienia także **GPIO 16–17** jako `SPI0/1`: *„GPIO6-11 and GPIO16-17 are usually connected to the SPI flash and PSRAM integrated on the module and therefore should not be used for other purposes"* | dotyczy `MODEM_TX_PIN = 17`. Na ESP32-WROOM-32 (bez PSRAM) 16/17 są fizycznie wolne, ale wiązanie się z nimi zamyka drogę do modułów WROVER. Mapa w [§4.1](#41-piny) omija je |
| *„S3 ma natywne USB CDC, klasyczny ESP32 wymaga konwertera UART — wpływ na logi i na proces flashowania"* | **Bieżący build nie używa USB CDC.** `ARDUINO_USB_CDC_ON_BOOT` domyślnie `0` (arduino-esp32, `HardwareSerial.h:438-439`) i `platformio.ini` go nie ustawia; manifest płytki ustawia tylko `ARDUINO_USB_MODE=1`. Przy `ARDUINO_USB_CDC_ON_BOOT == 0` obowiązuje `#define Serial Serial0` — czyli **UART0**, przez mostek USB-UART na płytce | **zerowy wpływ.** Firmware już dziś loguje przez zwykły UART0. Punkt 5 briefu odpada w całości — [§4.5](#45-usbserial) |
| *„watchdog `esp_task_wdt` z timeoutem 15 s wg `platformio.ini`"* | `platformio.ini:19` faktycznie ustawia `-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15`, ale **nigdzie w `firmware/` nie ma `esp_task_wdt_init()` ani `esp_task_wdt_add()`** (grep: 0 trafień; jest wyłącznie `esp_task_wdt_reset()`). Dodatkowo `-D` w `build_flags` nie wpływa na prekompilowane biblioteki ESP-IDF w frameworku Arduino — `sdkconfig` jest już zapieczony | realnym budżetem czasowym przy generowaniu klucza jest **RTC WDT bootloadera**, nie Task WDT — i to jest zgodne z tym, co mówi [`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md) („~9s budżetu na cały boot"). Szczegóły i skutki: [§4.3](#43-kryptografia--punkt-krytyczny-briefu-okazał-się-nie-istnieć). **To obserwacja poboczna wobec portu — dotyczy tak samo obu chipów** |

---

## 4. Inwentarz zależności od ESP32-S3

### 4.1 Piny

#### 4.1.1 Twarde fakty o klasycznym ESP32

Ze źródła dokumentacji ESP-IDF v5.3 (`docs/en/api-reference/peripherals/gpio/esp32.inc`) i z `components/soc/esp32/gpio_periph.c`:

- **34 fizyczne GPIO:** 0–19, 21–23, 25–27, 32–39. GPIO **24, 28, 29, 30, 31 nie istnieją** (w `GPIO_PIN_MUX_REG[]` mają wartość `0`); GPIO 20 tylko w obudowie ESP32-PICO-V3.
- **GPIO 6–11 oraz 16–17** — `SPI0/1`, flash i PSRAM modułu.
- **GPIO 34–39** — tylko wejście (`GPI`), bez programowych podciągnięć. Potwierdza to `soc_caps.h`: `SOC_GPIO_IN_RANGE_MAX 39` przy `SOC_GPIO_OUT_RANGE_MAX 33`.
- **Piny strappingowe: 0, 2, 5, 12 (MTDI), 15 (MTDO).** Stany domyślne przy resecie: GPIO0 ↑, GPIO2 ↓, GPIO5 ↑, GPIO12 ↓, GPIO15 ↑.
- **GPIO 1/3** — konsola UART0 (flashowanie i logi).
- **ADC1: GPIO 32–39. ADC2** (0, 2, 4, 12–15, 25–27) nie działa przy aktywnym Wi-Fi.
- Na modułach ESP-WROOM-32 **GPIO 37 i 38 nie są wyprowadzone**.

Dla kontrastu, na ESP32-S3 pinami strappingowymi są **0, 3, 45, 46** — czyli **żaden z pinów używanych dziś przez firmware**. Na klasycznym ESP32 dwa z nich (5 i 12) już nimi są. To jest źródło większości pracy przy porcie.

#### 4.1.2 Audyt bieżącej mapy

| GPIO | Funkcja | Źródło | Na klasycznym ESP32 | Werdykt |
|---|---|---|---|---|
| 4 | `MODEM_PWRKEY_PIN` | [`Config.h:18`](../../../firmware/include/Config.h#L18) | wolny, wyjściowy, nie strappingowy | ✅ **zostaje bez zmian** |
| 5 | `MODEM_RESET_PIN` | [`Config.h:19`](../../../firmware/include/Config.h#L19) | **pin strappingowy, domyślnie podciągnięty w górę** | ⚠️ **do przeniesienia — patrz pułapka 4.1.4** |
| 11 | `PT100_SPI_MOSI` | [`Config.h:27`](../../../firmware/include/Config.h#L27) | **flash SPI** | ❌ **musi się zmienić** |
| 12 | `PT100_SPI_SCK` | [`Config.h:29`](../../../firmware/include/Config.h#L29) | **MTDI — strapping napięcia flash** | ❌ **musi się zmienić** |
| 13 | `PT100_SPI_MISO` | [`Config.h:28`](../../../firmware/include/Config.h#L28) | wolny (JTAG) | ✅ da się zostawić |
| 14 | `PT100_SPI_CS` | [`Config.h:26`](../../../firmware/include/Config.h#L26) | wolny (JTAG) | ✅ da się zostawić |
| 17 | `MODEM_TX_PIN` | [`Config.h:17`](../../../firmware/include/Config.h#L17) | oznaczony `SPI0/1` (flash/PSRAM) | ⚠️ wolny na WROOM-32 bez PSRAM, ale odradzany |
| 18 | `MODEM_RX_PIN` | [`Config.h:16`](../../../firmware/include/Config.h#L16) | wolny (domyślny VSPI SCK) | ✅ da się zostawić |
| 48 | `LED_PIN` | [`Config.h:15`](../../../firmware/include/Config.h#L15) | **nie istnieje** (zakres 0–39) | ❌ **musi się zmienić** |

**Bilans: 3 kolizje twarde (11, 12, 48), 2 miękkie (5, 17), 4 piny bez zmian.** To mniej, niż sugerował brief — bo nie ma I2C.

#### 4.1.3 Proponowana mapa dla ESP-WROOM-32

Kryteria doboru, w kolejności: (1) zero pinów strappingowych i zero `SPI0/1`; (2) SPI na natywnych pinach IO_MUX magistrali VSPI, gdzie są wolne; (3) zachować to, co da się zachować, żeby ograniczyć przelutowanie; (4) zarezerwować ADC1 pod PT-506 z [`01_hardware.md §3`](./01_hardware.md).

| Funkcja | S3 dziś | **WROOM-32 propozycja** | Uzasadnienie wyboru |
|---|---|---|---|
| `MODEM_PWRKEY_PIN` | 4 | **4** | Wolny, wyjściowy, nie strappingowy. Zero powodów do ruszania — jedno połączenie mniej do przepięcia i do pomylenia |
| `MODEM_RESET_PIN` | 5 | **32** | GPIO 5 jest strappingowy i **domyślnie podciągnięty w górę**, a RESET modemu jest **active-HIGH** ([`02_modem §2.2`](./02_modem_a7670e_communication.md)) — patrz pułapka 4.1.4. GPIO 32 jest wyjściowy, nie strappingowy, poza ADC1_CH0/CH3 zarezerwowanymi pod PT-506 |
| `MODEM_TX_PIN` (→ RX modemu) | 17 | **25** | GPIO 17 jest oznaczony `SPI0/1`; 25 jest bezwarunkowo wolny i wyjściowy. Świadomie **nie** biorę pary 16/17 (naturalne UART2), żeby mapa działała także na modułach z PSRAM |
| `MODEM_RX_PIN` (← TX modemu) | 18 | **26** | Para z 25, fizycznie sąsiaduje. GPIO 18 przejmuje SPI SCK. UART1 jest przekierowywany przez macierz GPIO — `ModemLink` już dziś podaje piny jawnie w [`ModemLink.cpp:18`](../../../firmware/lib/ModemLink/src/ModemLink.cpp#L18), a rdzeń Arduino honoruje piny jawne nad domyślnymi |
| `PT100_SPI_SCK` | 12 | **18** | GPIO 12 = MTDI, wybór napięcia flash — nie ma powodu ryzykować (pułapka 4.1.4). GPIO 18 to natywny **IO_MUX VSPI CLK** → sygnał omija macierz GPIO |
| `PT100_SPI_MISO` | 13 | **19** | Natywny **IO_MUX VSPI MISO**. Trzymanie całej czwórki SPI na IO_MUX daje spójny, przewidywalny timing |
| `PT100_SPI_MOSI` | 11 | **23** | GPIO 11 to flash. GPIO 23 to natywny **IO_MUX VSPI MOSI** |
| `PT100_SPI_CS` | 14 | **21** | CS jest sterowany **programowo** przez `Adafruit_MAX31865`, więc nie musi być na IO_MUX. Natywny VSPI CS0 to GPIO 5 — pin strappingowy, dlatego świadomie z niego rezygnuję. GPIO 21 jest wolny |
| `LED_PIN` | 48 | **2** | GPIO 48 nie istnieje. GPIO 2 to `LED_BUILTIN` na wariancie `doitESP32devkitV1`. **Uwaga na wybór płytki — patrz [§4.2](#42-led-statusu)** |
| PT-506 ADC (*draft*) | 1 | **36** (ADC1_CH0) | Wejście analogowe nie potrzebuje trybu wyjściowego, więc pin *input-only* jest tu idealny — nie marnujemy pinu dwukierunkowego. ADC1 działa niezależnie od radia. Rezerwa: 39 (ADC1_CH3) na drugi kanał |

**Piny wolne po tej mapie:** 13, 14, 22, 27, 33, 34, 35, 39 (+16, 17 z zastrzeżeniem PSRAM). Dziewięć pinów zajętych na dwadzieścia kilka wyprowadzonych — **liczba pinów nie jest ograniczeniem** klasycznego ESP32 w tym zastosowaniu i nie powinna pojawiać się jako argument przeciw.

**Wariant minimalizujący przelutowanie** (gdyby czas bring-upu okazał się głównym kosztem): zostawić MISO na 13 i CS na 14, przenieść tylko MOSI 11→23 i SCK 12→18, a modem przesunąć na 25/26. Wtedy zmieniają się 4 połączenia zamiast 8, kosztem routingu MISO przez macierz GPIO — przy zegarze SPI rzędu 1 MHz dla MAX31865 to różnica bez znaczenia praktycznego.

#### 4.1.4 Dwie pułapki strappingowe — najważniejsza część mapy pinów

**Pułapka A — GPIO 5 jako RESET modemu (potencjalna powtórka regresji z 2026-08-23).**

Na płytce KAmod RESET jest **active-HIGH**: `HIGH = modem trzymany w resecie` ([`02_modem §2.2`](./02_modem_a7670e_communication.md)). Na klasycznym ESP32 GPIO 5 jest pinem strappingowym z **domyślnym podciągnięciem w górę** — przez cały czas od podania zasilania do momentu, w którym `ModemPower::powerOn()` ustawi go w stan LOW ([`ModemPower.cpp:16`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L16)), linia RESET stoi w stanie wysokim, czyli **modem jest trzymany w resecie przez cały boot ESP32**. Na ESP32-S3 GPIO 5 nie jest strappingowy i takiego podciągnięcia nie ma.

To jest dokładnie ta klasa błędu, która w tym projekcie **już raz kosztowała cykl debugowania**: [`02_modem §7.3`](./02_modem_a7670e_communication.md) opisuje regresję „RESET pin held HIGH" — timeout inicjalizacji modemu 10,3 s, root cause w jednej linii polaryzacji, po naprawie init w 132 ms. Objaw byłby ten sam, a przyczyna inna i trudniejsza do znalezienia, bo tym razem leżałaby w krzemie, nie w kodzie. **Dlatego mapa przenosi RESET na GPIO 32** — a nie dlatego, że GPIO 5 „nie zadziała".

**Pułapka B — GPIO 12 (MTDI) jako SPI SCK.**

MTDI przy starcie wybiera napięcie flash: stan niski → 3,3 V, stan wysoki → 1,8 V. Wysoki stan przy starcie na module z flashem 3,3 V oznacza brown-out i **płytkę, która się nie bootuje**. `Adafruit_MAX31865` pracuje w SPI Mode 1 (CPOL=0), więc SCK spoczywa w stanie niskim i w typowym przypadku byłoby to bezpieczne — ale wystarczy podciągnięcie na module breakout albo inne urządzenie na magistrali i płytka przestaje wstawać. Przy dziesięciu wolnych, bezpiecznych pinach **nie ma powodu podejmować tego ryzyka**.

---

### 4.2 LED statusu

**Ustalenie, które rozstrzyga ten punkt: sygnalizacja kolorami nie istnieje w kodzie.**

[`StatusLed::blink()`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L36-L54) w gałęzi WS2812 ustawia **wyłącznie** `Color(0, 255, 0)` — zielony — zarówno dla sukcesu, jak i dla błędu. Stany rozróżnia **liczba i długość mignięć**, nie barwa:

| Metoda | Wywołanie | Sygnał |
|---|---|---|
| `blinkSuccess()` | `blink(1, 80)` | 1 mignięcie, 80 ms |
| `blinkError()` | `blink(3, 120)` | 3 mignięcia, 120 ms |

Potwierdza to sama dokumentacja sprzętowa, w [`01_hardware.md §4`](./01_hardware.md): *„Success: pojedynczy blink zielony / **Error: trzy blinki zielone**"*.

**Wniosek: degradacja do zwykłej diody jednokolorowej nie traci nic, co dziś istnieje.** Cały przekaz — 1 mignięcie vs 3 mignięcia — przenosi się jeden do jednego. To rozstrzyga pytanie briefu bez potrzeby ważenia kompromisów: nie ma czego ważyć.

**Ale wybór płytki ma znaczenie i łatwo go przeoczyć:**

| Wariant arduino-esp32 | Płytka | `LED_BUILTIN` |
|---|---|---|
| `esp32` (board `esp32dev` — „ESP32 Dev Module", oficjalny DevKitC) | oficjalna Espressif | **brak — wariant nie definiuje `LED_BUILTIN` w ogóle** |
| `doitESP32devkitV1` (board `esp32doit-devkit-v1` — popularny 30-pinowy) | DOIT | **GPIO 2**, zwykła dioda niebieska |
| `esp32s3` (dziś) | DevKitC-1 | RGB WS2812 przez `PIN_RGB_LED` |

Czyli: na **oficjalnym** ESP32-DevKitC nie ma żadnej diody użytkownika i trzeba by dołożyć LED z rezystorem albo zewnętrzny WS2812. Na klonie DOIT DevKit V1 dioda na GPIO 2 jest i wystarcza.

**Rekomendacja: zwykła dioda na GPIO 2, płytka klasy DOIT DevKit V1.** Zewnętrzny WS2812 to doposażenie za kilka złotych i jeden przewód — sensowne dopiero wtedy, gdy sygnalizacja kolorami zostanie faktycznie zaimplementowana, co dziś nie ma miejsca.

**Dług techniczny wart naprawienia niezależnie od portu.** `StatusLed` rozpoznaje typ diody przez **porównanie numeru pinu z literałem `48`** — dwa razy, w [konstruktorze (linia 8)](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L8) i w [`blink()` (linia 38)](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L38). Numer pinu pełni tu rolę ukrytego przełącznika typu sprzętu. Port by to wymusił, ale zmiana jest sensowna sama w sobie: jawny tryb (enum albo flaga w konstruktorze) zamiast magicznej stałej, ~20 linii, przy okazji czyni klasę testowalną w środowisku `native`. **To jedyna zmiana w kodzie z tej analizy, którą warto zrobić niezależnie od decyzji o porcie.**

---

### 4.3 Kryptografia — punkt krytyczny briefu okazał się nie istnieć

Brief nazwał ten punkt krytycznym dla całej analizy. Odpowiedź jest jednoznaczna i idzie w przeciwną stronę niż sugerowała hipoteza.

#### Ustalenie: żaden z dwóch chipów nie ma sprzętowego akceleratora ECC

W ESP-IDF v5.3 opcja akceleracji ECC w mbedTLS jest warunkowana wprost:

```kconfig
config MBEDTLS_HARDWARE_ECC
    bool "Enable hardware ECC acceleration"
    default y
    depends on SOC_ECC_SUPPORTED
    help
        Enable hardware accelerated ECC point multiplication and point verification
        for points on curve SECP192R1 and SECP256R1 in mbedTLS
```

**`SOC_ECC_SUPPORTED` nie jest zdefiniowane ani w `components/soc/esp32/include/soc/soc_caps.h`, ani w `components/soc/esp32s3/include/soc/soc_caps.h`.** (Akcelerator ECC mają rodziny RISC-V: C3, H2, C6 — nie Xtensa.)

Wniosek: `mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1, ...)` w [`DeviceIdentity.cpp:198`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L198) i `mbedtls_ecdsa_write_signature()` w [`DeviceIdentity.cpp:102`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L102) **już dziś, na ESP32-S3, wykonują się w całości programowo**. Port niczego tu nie odbiera, bo nie ma czego odebrać.

#### Porównanie tego, co obu chipom faktycznie pomaga

| Możliwość | `soc_caps.h` esp32 | `soc_caps.h` esp32s3 | Znaczenie dla `DeviceIdentity` |
|---|---|---|---|
| `SOC_ECC_SUPPORTED` | **brak** | **brak** | ECC programowo na obu — bez różnicy |
| `SOC_MPI_SUPPORTED` (bignum) | ✅ | ✅ | `MBEDTLS_HARDWARE_MPI` `default y` na obu; ESP-IDF przechwytuje `mbedtls_mpi_mul_mpi`/`exp_mod`, z czego ECP częściowo korzysta — **bez różnicy** |
| `SOC_SHA_SUPPORTED` | ✅ | ✅ | `mbedtls_sha256()` sprzętowo na obu — bez różnicy |
| `SOC_AES_SUPPORTED` | ✅ | ✅ | bez różnicy |
| `MBEDTLS_MPI_USE_INTERRUPT` | **wyłączone** (`depends on !IDF_TARGET_ESP32`) | ✅ włączone | **jedyna realna różnica**: na klasycznym ESP32 CPU czeka w pętli zamiast oddać rdzeń. Dla ECC (wiele krótkich mnożeń, brak długich `exp_mod`) wpływ pomijalny; miałoby to znaczenie przy RSA |
| Rdzeń / zegar | 2× Xtensa LX6 @ 240 MHz | 2× Xtensa LX7 @ 240 MHz | ten sam zegar; LX7 nieznacznie wydajniejszy na cykl |

#### Budżet czasowy — czy się mieści

Punkt odniesienia z repozytorium: [`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md) — generowanie klucza *„trwa ~2-3s CPU-intensywnie"* na ESP32-S3.

Na WROOM-32 przy identycznej ścieżce programowej, identycznym zegarze i nieco starszym rdzeniu spodziewam się **~2,5–4 s** (*oszacowanie — do zmierzenia, procedura w [§11](#11-czego-nie-dało-się-zweryfikować--lista-do-domknięcia)*). Ale sam budżet trzeba postawić poprawnie, bo brief postawił go na Task WDT, a tam go nie ma:

- **Task WDT nie pilnuje `loopTask`.** W całym `firmware/` nie ma `esp_task_wdt_init()` ani `esp_task_wdt_add(NULL)` — jest tylko `esp_task_wdt_reset()`. Bez subskrypcji zadania `esp_task_wdt_reset()` zwraca `ESP_ERR_NOT_FOUND` i nic nie robi. Dodatkowo `-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15` z [`platformio.ini:19`](../../../firmware/platformio.ini#L19) nie sięga prekompilowanych bibliotek frameworku Arduino (`sdkconfig` jest zapieczony) — to samo dotyczy `CONFIG_BOOTLOADER_WDT_DISABLE=1` z linii 20.
- **Realnym ograniczeniem jest RTC WDT bootloadera** (~9 s na cały boot) — i to właśnie dlatego kod **już to poprawnie obchodzi**: generowanie klucza jest celowo odłożone z `setup()` do pierwszej iteracji `loop()` przez flagę `keyGenerated` ([`main.cpp:199-202`](../../../firmware/src/main.cpp#L199-L202)), poza okno bootu. Dodatkowo `loadOrGenerateKey()` woła `esp_task_wdt_reset()` i `yield()` **przed i po** `mbedtls_ecp_gen_key` ([`DeviceIdentity.cpp:191-200`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L191-L200)).

**Wniosek:** nawet górna granica oszacowania (~4 s) mieści się z zapasem, bo operacja wykonuje się **poza oknem RTC WDT**, w `loop()`. Zabezpieczenie jest architektoniczne, nie zależy od marginesu czasowego, i przenosi się na WROOM-32 bez zmian. **Kryptografia nie jest przeszkodą w porcie i nie jest zależnością od S3.**

**Uwaga poboczna, niezwiązana z portem:** rozbieżność między [`03_esp32_reset_and_recovery.md §4`](./03_esp32_reset_and_recovery.md) („żeby włączyć: `esp_task_wdt_init()` + `esp_task_wdt_add(NULL)`") a kodem, który tego nie robi, jest warta osobnego zgłoszenia — Task WDT prawdopodobnie **nie chroni dziś `loop()` na żadnym chipie**. To nie zmienia niczego w rachunku portu i nie należy do zakresu B-10.

---

### 4.4 Pamięć

#### RAM — nie jest problemem, i to da się pokazać bez buildu

| | ESP32-S3-DevKitC-1 (dziś) | ESP32 Dev Module |
|---|---|---|
| `maximum_ram_size` w manifeście płytki | **327 680 B** (320 KiB) | **327 680 B** (320 KiB) |
| PSRAM | wariant **N8 — „No PSRAM"** wg nazwy w manifeście; `platformio.ini` nie ustawia `-DBOARD_HAS_PSRAM` | brak w podstawowych WROOM-32 |

**Limit RAM jest liczbowo identyczny, a PSRAM nie jest dziś używany** — więc port nie odbiera ani bajta dostępnej pamięci. To rozstrzyga pytanie z briefu o „brak PSRAM w podstawowych wariantach": jest bez znaczenia, bo obecny build i tak z PSRAM nie korzysta.

Rozmiary buforów, policzone ze stałych w kodzie:

| Bufor | Wyliczenie | Szacunek |
|---|---|---|
| `windows_buffer_` | `RETAIN_WINDOWS_MAX = WINDOWS_PER_BATCH(4) × 12 = 48` okien ([`TelemetryPayload.h:34-35`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L34-L35)); `MeasurementWindow` = `uint64_t` + `uint32_t` + `std::vector` ≈ 24 B, plus blok sterty na 1 czujnik (`pair<ISensor*, SensorReading>` ≈ 16 B + narzut alokatora) | **~2,5 KB** |
| `errors_buffer_` | `MAX_ERRORS = 64` ([`TelemetryPayload.h:36`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L36)) × `ErrorItem` (4 wskaźniki = 16 B) | **~1 KB** |
| `TINY_GSM_RX_BUFFER` | [`platformio.ini:18`](../../../firmware/platformio.ini#L18) | **1 KB** |
| `JsonDocument` przy `build()` | ArduinoJson 7, sterta elastyczna; 4 okna × 1 punkt | **~1–2 KB** chwilowo |

Razem **rzędu 5–7 KB przy 320 KB dostępnych.** Bufor okien z briefu (12 minut historii) jest o dwa rzędy wielkości mniejszy niż limit.

**Dodatkowo — czynnik, który dopiero czyni RAM nieproblematycznym:** `-D TINY_GSM_MODEM_A76XXSSL` ([`platformio.ini:17`](../../../firmware/platformio.ini#L17)) oznacza, że **TLS terminuje modem A7670E, nie mikrokontroler**. Gdyby HTTPS szło przez mbedTLS na ESP32, doszłoby kilkadziesiąt kilobajtów sterty na sesję TLS i rozmowa o RAM wyglądałaby zupełnie inaczej — także dziś, na S3.

#### Flash — **to jest jedyne miejsce, gdzie port faktycznie coś zabiera**

Różnica nie leży w rozmiarze kości, tylko w **domyślnej tablicy partycji**, którą manifest płytki narzuca:

| | ESP32-S3-DevKitC-1 | ESP32 Dev Module |
|---|---|---|
| Flash | 8 MB | 4 MB |
| Tablica partycji | `default_8MB.csv` (jawnie w manifeście) | `default.csv` (brak wpisu → domyślna) |
| **Partycja aplikacji `app0`** | `0x330000` = **3 342 336 B ≈ 3,19 MiB** | `0x140000` = **1 310 720 B = 1,25 MiB** |
| Partycja NVS | `0x5000` = 20 KiB | `0x5000` = 20 KiB — **identyczna** |

**Miejsce na aplikację kurczy się 2,55×.** To jedyna wielkość w całej analizie, przy której odpowiedź „mieści się / nie mieści" wymaga realnego buildu — a buildu nie dało się wykonać ([§2.2](#22-czego-nie-dało-się-zweryfikować-i-dlaczego)).

**Ale to nie jest ryzyko blokujące, bo istnieją gotowe wyjścia**, i warto je znać z góry:

| Tablica partycji | `app0` | OTA | Koszt |
|---|---|---|---|
| `default.csv` (domyślna dla 4 MB) | 1,25 MiB | dwa sloty | — |
| **`min_spiffs.csv`** | **1,875 MiB** (`0x1E0000`) | **dwa sloty zachowane** | SPIFFS spada do 128 KiB — **projekt nie używa SPIFFS** (tylko `Preferences`/NVS), więc realny koszt to zero |
| `no_ota.csv` | 2 MiB (`0x200000`) | **jeden slot — OTA znika** | wysoki: brak aktualizacji zdalnej |
| moduł ESP32-WROOM-32**E** 8 MB + `default_8MB.csv` | 3,19 MiB | dwa sloty | wyższa cena modułu — a to była **jedyna** motywacja portu |

**Zatem:** jeśli obecny binarny obraz mieści się w 1,875 MiB (co przy tym zestawie bibliotek jest bardzo prawdopodobne — Arduino core + mbedTLS + TinyGSM + ArduinoJson + NVS, bez stosu TLS na MCU), to `min_spiffs.csv` rozwiązuje sprawę bezkosztowo i **OTA zostaje zachowane**. Ostatni wariant jest sam w sobie pouczający: ratowanie flasha przez moduł 8 MB unieważnia cel portu, bo podnosi cenę, którą port miał obniżyć.

**Drobiazg, ale przy ciasnym flashu warto:** `Adafruit_NeoPixel` jest w [`lib_deps`](../../../firmware/platformio.ini#L13) i jest bezwarunkowo dołączany przez [`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L2). W wariancie ze zwykłą diodą byłby to martwy kod — jego wycięcie za `#ifdef` odzyskuje kilka kilobajtów i naturalnie łączy się z refaktorem `StatusLed` z [§4.2](#42-led-statusu).

---

### 4.5 USB/Serial

**Wpływ zerowy. Punkt odpada w całości** — uzasadnienie w [§3](#3-korekty-do-założeń-briefu).

W skrócie: `Serial` w bieżącym buildzie to `Serial0`, czyli **UART0**, bo `ARDUINO_USB_CDC_ON_BOOT` domyślnie wynosi `0` i `platformio.ini` go nie nadpisuje. Logi z [`Logger.h`](../../../firmware/lib/Logger/include/Logger.h) i flashowanie idą dziś przez mostek USB-UART na płytce DevKitC-1 — **dokładnie tak samo, jak szłyby przez CP2102/CH340 na płytce z klasycznym ESP32**. Firmware nigdy nie korzystał z natywnego USB CDC układu S3.

Poboczna obserwacja: `EnrollmentClient::readSerial()` jest **pustą metodą** z komentarzem *„Serial input disabled - migrated away from direct Serial usage"* ([`EnrollmentClient.cpp:95-97`](../../../firmware/lib/EnrollmentClient/src/EnrollmentClient.cpp)). Ścieżka `ACTIVATE <kod>` opisana w [`04_device_provisioning_flow.md §3.2`](./04_device_provisioning_flow.md) **nie ma dziś czym odbierać kodu** — `processLine()` istnieje, ale nikt go nie woła. To nie dotyczy portu (jest tak samo złamane na obu chipach), ale skoro brief kazał sprawdzić wpływ portu na proces uruchamiania w terenie: **ten proces jest dziś przerwany niezależnie od chipu** i warto to zgłosić osobno.

---

### 4.6 `RTC_DATA_ATTR`

**Kompatybilne bez zmian.** Obie karty możliwości deklarują `SOC_RTC_FAST_MEM_SUPPORTED 1` i `SOC_RTC_SLOW_MEM_SUPPORTED 1`. Na klasycznym ESP32 obszar `RTC_DATA` to `0x50000000`–`0x50002000`, czyli **8 KiB** (`components/soc/esp32/include/soc/soc.h`).

Bieżące użycie to trzy zmienne — `rtcRestartCounter`, `rtcSyncedTimeUtcSec`, `rtcSyncMillis` ([`main.cpp:27-29`](../../../firmware/src/main.cpp#L27-L29), deklaracje w [`RtcState.h`](../../../firmware/include/RtcState.h)) — łącznie **12 bajtów przy 8 192 dostępnych**. Semantyka przetrwania `esp_restart()`, na której opiera się licznik restartów w [`Watchdog::attemptRecovery()`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L38-L42) i utrzymanie czasu w [`TimeSync`](../../../firmware/lib/TimeSync/src/TimeSync.cpp), jest na obu chipach taka sama. **Zero pracy.**

---

### 4.7 `platformio.ini`

Brief wymaga środowiska `env:esp32-wroom` **obok** istniejącego `env:esp32-s3`, bez usuwania. Struktura, która to realizuje przy minimalnej duplikacji:

```ini
[env]                      ; wspólna baza — dziś wszystko jest wklejone w [env:esp32-s3]
platform = espressif32
framework = arduino
monitor_speed = 115200
extra_scripts = scripts/prebuild.py
lib_extra_dirs = ${PROJECT_DIR}/lib
lib_deps = ...             ; bez zmian
build_flags =
    -D TINY_GSM_MODEM_A76XXSSL
    -D TINY_GSM_RX_BUFFER=1024
    -D LOG_LEVEL=LOG_INFO
    -Iinclude

[env:esp32-s3]
extends = env
board = esp32-s3-devkitc-1
build_flags = ${env.build_flags} -D BOARD_ESP32_S3

[env:esp32-wroom]
extends = env
board = esp32doit-devkit-v1        ; wariant z LED_BUILTIN = GPIO 2 (§4.2)
board_build.partitions = min_spiffs.csv   ; 1,875 MiB na app, OTA zachowane (§4.4)
build_flags = ${env.build_flags} -D BOARD_ESP32_WROOM
```

`Config.h` rozgałęzia się wtedy na `#if defined(BOARD_ESP32_WROOM)` / `#else`, a `StatusLed` dostaje jawny tryb zamiast porównania `pin_ == 48` ([§4.2](#42-led-statusu)).

**Ale są dwa haczyki, które zjedzą więcej czasu niż samo napisanie tego pliku:**

1. **`CONFIG_ESP_TASK_WDT_TIMEOUT_S` i `CONFIG_BOOTLOADER_WDT_DISABLE` z linii 19–20 nie działają tak, jak sugeruje ich obecność** — `-D` nie sięga prekompilowanych bibliotek ESP-IDF frameworku Arduino ([§3](#3-korekty-do-założeń-briefu)). Przeniesienie ich do `[env]` niczego nie naprawi. Jeśli te ustawienia mają zacząć obowiązywać, potrzebny jest osobny mechanizm (własny `sdkconfig` / framework `espidf`) — i to jest **decyzja niezależna od portu**, dotycząca tak samo dzisiejszego S3.
2. **`test_ignore_pattern` w `[env:native]`** (linia 28) jest nieznaną opcją i PlatformIO wypisuje na nią ostrzeżenie (`Warning! Ignore unknown configuration option 'test_ignore_pattern' in section [env:native]` — zaobserwowane bezpośrednio przy próbie uruchomienia narzędzia). Do posprzątania przy okazji, nie ma związku z portem.

**Dobra wiadomość: pięć plików testowych w `firmware/test/` działa w środowisku `native`** i nie zależy od chipu — pokrycie testowe przenosi się na drugi wariant za darmo.

---

### 4.8 Zależności spoza listy briefu

Cztery rzeczy, których brief nie wymienił, a które zmieniają obraz.

#### A. Numer seryjny pochodzi z adresu MAC — **każdy moduł to osobna tożsamość urządzenia**

`generateSerialNumber()` buduje SN z sześciu bajtów MAC Wi-Fi ([`DeviceIdentity.cpp:217`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L217)), a klucz prywatny EC i flaga `claimed` żyją w NVS konkretnego modułu.

Skutek praktyczny: przełożenie firmware na inny fizyczny moduł to **nowe urządzenie w backendzie** — nowy SN, nowa para kluczy, konieczny nowy kod aktywacyjny i pełny cykl provisioningu ([`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md)). Nie jest to przeszkoda w porcie, ale trzeba to wiedzieć przy planowaniu bring-upu (**każdy test na drugiej płytce zużywa kod aktywacyjny**) i przy ewentualnej wymianie sprzętu w terenie.

#### B. HMAC + Digital Signature — jedyna realna funkcja, którą port zamyka na trwałe

| Peryferium | esp32 | esp32s3 | Do czego służy |
|---|---|---|---|
| `SOC_HMAC_SUPPORTED` | **brak** | ✅ | klucz w eFuse, niedostępny dla oprogramowania |
| `SOC_DIG_SIGN_SUPPORTED` | **brak** | ✅ | podpisywanie kluczem, którego firmware nie może odczytać |
| `SOC_FLASH_ENC_SUPPORTED` | ✅ | ✅ | szyfrowanie flasha — **dostępne na obu** |
| `SOC_SECURE_BOOT_SUPPORTED` | ✅ | ✅ | secure boot — **dostępne na obu** |

Dziś klucz prywatny leży w NVS **jawnym tekstem** ([`DeviceIdentity.cpp:205`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L205): `prefs.putBytes("priv", ...)`), więc projekt z peryferium DS i tak nie korzysta. Ale to jest **naturalna ścieżka utwardzenia** tożsamości urządzenia, a szyfrowanie flasha (dostępne na obu chipach) chroni klucz tylko przed odczytem kości — nie przed odczytem przez własne oprogramowanie.

Waga tego punktu zależy od [B-01](../../plan/01_briefy_dla_agentow.md): jeśli gmina jako podmiot kluczowy NIS2/KSC postawi wymagania kontraktowe co do ochrony tożsamości urządzenia, ESP32-S3 ma na to sprzętową odpowiedź, a klasyczny ESP32 nie. **Port zamyka tę furtkę nieodwracalnie** — i to jest najmocniejszy techniczny argument przeciwko niemu, mocniejszy niż cokolwiek z listy briefu.

#### C. Rzeczy, które przenoszą się bez pracy

Warto to wypisać, żeby przy wycenie nikt nie doliczał kosztu tam, gdzie go nie ma: `Preferences`/NVS, `esp_read_mac()`, `esp_restart()`, `esp_task_wdt_reset()`, `HardwareSerial SerialAT(1)` (`SOC_UART_NUM = 3` na klasycznym ESP32, więc UART1 istnieje), `SPI.begin(sck, miso, mosi, cs)` z jawnymi pinami ([`PT100Sensor.cpp:14`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L14)), `Adafruit_MAX31865`, `Adafruit_NeoPixel` (wspiera klasyczny ESP32), TinyGSM, ArduinoJson, `ArduinoHttpClient`. **Identyczne API na obu chipach.**

#### D. Peryferia S3, których projekt nie używa

USB OTG, USB-Serial-JTAG, wektory SIMD/DSP, `SOC_SPIRAM_XIP_SUPPORTED`, akcelerator dotyku v2. **Żadne nie występuje w kodzie** — nie ma tu nic do stracenia.

---

## 5. Co się traci — funkcja po funkcji

| Funkcja | Traci się? | Waga |
|---|---|---|
| Sygnalizacja kolorami LED | **Nie** — kod używa wyłącznie zieleni; stany rozróżnia liczba mignięć ([§4.2](#42-led-statusu)) | zerowa |
| Kryptografia P-256 (klucz + podpis) | **Nie** — programowa na obu chipach, akcelerator ECC nie istnieje ani na S3, ani na ESP32 ([§4.3](#43-kryptografia--punkt-krytyczny-briefu-okazał-się-nie-istnieć)) | zerowa |
| Dostępna pamięć RAM | **Nie** — limit identyczny (320 KiB), PSRAM nieużywany ([§4.4](#44-pamięć)) | zerowa |
| Natywne USB CDC | **Nie** — firmware go nie używa, `Serial` = UART0 ([§4.5](#45-usbserial)) | zerowa |
| `RTC_DATA_ATTR` | **Nie** — 8 KiB na obu, użycie 12 B ([§4.6](#46-rtc_data_attr)) | zerowa |
| Testy jednostkowe (`env:native`) | **Nie** — niezależne od chipu | zerowa |
| **Miejsce na aplikację** | **Tak: 3,19 MiB → 1,25 MiB** (2,55×). Odzyskiwalne do 1,875 MiB przez `min_spiffs.csv`, z zachowaniem OTA ([§4.4](#44-pamięć)) | **średnia** — wymaga jednorazowej weryfikacji buildem |
| **Swoboda pinów** | **Tak** — znika 5 pinów (6–11 flash), 6 pinów staje się tylko-wejściowych, dochodzą 4 piny strappingowe. Po nowej mapie zostaje jednak **8+ wolnych pinów** ([§4.1.3](#413-proponowana-mapa-dla-esp-wroom-32)) | niska |
| **Peryferium HMAC + Digital Signature** | **Tak, nieodwracalnie** — nie da się ich dodać do klasycznego ESP32. Zamyka drogę do klucza urządzenia niedostępnego dla oprogramowania ([§4.8 B](#b-hmac--digital-signature--jedyna-realna-funkcja-którą-port-zamyka-na-trwałe)) | **wysoka, jeśli B-01 wykaże wymagania NIS2 dot. tożsamości urządzenia** |
| **Ścieżka rozwoju platformy** | **Tak** — klasyczny ESP32 jest w fazie dojrzałej, nowe rodziny Espressif (S3, C6, P4) dostają nowe funkcje pierwsze | niska–średnia |

**Podsumowanie: z ośmiu punktów briefu sześć nie traci nic.** Realne są dwa: miejsce na aplikację (rozwiązywalne) i peryferium DS (nierozwiązywalne).

---

## 6. Koszt portu

Wycena z podziałem na kod, sprzęt i dokumentację. Podstawą jest odczytany zakres zmian, nie wrażenie.

### 6.1 Zmiany w kodzie — **mały, dobrze ograniczony zakres**

| Plik | Zmiana | Skala |
|---|---|---|
| [`Config.h`](../../../firmware/include/Config.h) | nowa mapa pinów za `#if defined(BOARD_ESP32_WROOM)` | ~30 linii |
| [`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp) + `.h` | jawny tryb diody zamiast `pin_ == 48` w dwóch miejscach; opcjonalnie `#ifdef` na `Adafruit_NeoPixel` | ~40 linii |
| [`platformio.ini`](../../../firmware/platformio.ini) | sekcja `[env]` + nowe `[env:esp32-wroom]` z `min_spiffs.csv` | ~20 linii |
| [`01_hardware.md`](./01_hardware.md), [`02_modem…md §2.2`](./02_modem_a7670e_communication.md) | druga mapa pinów, oznaczenie która dotyczy którego wariantu | dokumentacja |

**Razem ~90 linii kodu produkcyjnego.** Żadnej zmiany logiki, żadnej zmiany protokołu, żadnej zmiany w bibliotekach. **4–8 h** wraz z buildem obu środowisk.

### 6.2 Sprzęt i uruchomienie — **tu leży 60–70% kosztu**

Osiem połączeń zmienia pin ([§4.1.3](#413-proponowana-mapa-dla-esp-wroom-32)). To przepinanie przewodów, nie projekt PCB — moduł KAmod jest dziś podłączany kablami, bo to HAT na złącze 40-pin Raspberry Pi, a nie płytka pasująca do ESP32 ([`01_hardware.md §7`](./01_hardware.md), status *draft*).

Weryfikacja musi objąć pełny łańcuch, bo to jedyny sposób, żeby wyłapać różnice krzemowe: `powerOn()` → auto-baud → rejestracja w LTE → APN → NTP → generowanie klucza → `ACTIVATE` → redeem → challenge/verify → telemetria (~55 s wg [`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md)) + trzypoziomowy recovery watchdoga ([`03_esp32_reset_and_recovery.md §3`](./03_esp32_reset_and_recovery.md)) + odczyt PT100 na nowych pinach SPI.

**Kalibracja tej pozycji na historii tego projektu:** [`02_modem §7.3`](./02_modem_a7670e_communication.md) pokazuje, że **jedna linia z odwrotną polaryzacją GPIO** dała timeout 10,3 s i wymagała pełnego cyklu diagnostycznego. Port zmienia osiem pinów i wchodzi na chip z dwoma nowymi pułapkami strappingowymi ([§4.1.4](#414-dwie-pułapki-strappingowe--najważniejsza-część-mapy-pinów)). Zakładanie, że pójdzie za pierwszym razem, byłoby wbrew własnym danym projektu.

**8–16 h**, z rozrzutem zależnym głównie od tego, ile razy zadziała pułapka strappingowa.

### 6.3 Bilans jednorazowy

| Pozycja | Godziny |
|---|---|
| Kod + build obu środowisk | 4–8 |
| Bring-up sprzętowy i weryfikacja pełnego łańcucha | 8–16 |
| Dokumentacja (druga mapa pinów w dwóch dokumentach) | 2–4 |
| **Razem** | **14–28 h ≈ 2–3,5 dnia roboczego** |

### 6.4 Koszt powracający — utrzymanie dwóch wariantów

Podstawa: `firmware/` był ruszany w **8 z 50 commitów** w widocznej historii (klon płytki, 2026-08-15 → 2026-09-01), czyli ~3 commity/tydzień. **Firmware jest w fazie aktywnego rozwoju, nie zamrożenia** — a to jest wielkość, która najbardziej podbija koszt drugiego wariantu.

| Pozycja | Godziny/rok |
|---|---|
| Podwójna weryfikacja zmian dotykających pinów/peryferiów (~1–3 h/mies.) | 12–36 |
| Każdy nowy czujnik: kroki 5–6 z [`06_adding_sensors.md`](./06_adding_sensors.md) (flash + odczyt logów + weryfikacja w backendzie) razy dwa, plus dobór pinu w dwóch mapach — 4–8 h za czujnik | 4–16 (przy 1–2 czujnikach) |
| **Razem** | **16–52 h/rok ≈ 2–6,5 dnia/rok** |

---

## 7. Próg opłacalności

Brief żąda progu, nie rachunku na zmyślonym wolumenie. Zgoda — i idę o krok dalej: skoro **cen nie dało się zweryfikować** ([§2.2](#22-czego-nie-dało-się-zweryfikować-i-dlaczego)), przeprowadzam rachunek **parametrycznie**, tak żeby wniosek nie zależał od tego, czy trafiłem w cenę.

### 7.1 Wzór

```
N = (P + U) / Δ

P = jednorazowy koszt portu        = 14–28 h × R
U = roczny koszt dwóch wariantów   = 16–52 h × R
Δ = oszczędność na module          [PLN/szt.]
R = stawka godzinowa               [PLN/h]
N = próg opłacalności              [szt.]
```

### 7.2 Koszt pracy dla dwóch stawek

| Scenariusz | Godziny (P + U, rok 1) | R = 100 PLN/h | R = 150 PLN/h |
|---|---|---|---|
| **Optymistyczny** (wszystko idzie gładko, 1 wariant czujnika) | 30 h | 3 000 PLN | 4 500 PLN |
| **Realistyczny** | 50 h | 5 000 PLN | 7 500 PLN |
| **Pesymistyczny** (pułapka strappingowa + 2 nowe czujniki) | 80 h | 8 000 PLN | 12 000 PLN |

### 7.3 Tabela wrażliwości — próg N w sztukach

Wiersze to różnica ceny modułu Δ; kolumny to koszt pracy w roku pierwszym. Δ **nie jest zweryfikowana** ([§11](#11-czego-nie-dało-się-zweryfikować--lista-do-domknięcia)), dlatego przebiegam cały realny zakres dla płytek deweloperskich.

| Δ [PLN/szt.] | 3 000 PLN | 5 000 PLN | 7 500 PLN | 12 000 PLN |
|---|---|---|---|---|
| **20** | 150 szt. | 250 szt. | 375 szt. | 600 szt. |
| **40** | 75 szt. | 125 szt. | 188 szt. | 300 szt. |
| **60** | 50 szt. | 83 szt. | 125 szt. | 200 szt. |
| **80** *(nierealistycznie wysoka)* | **38 szt.** | 63 szt. | 94 szt. | 150 szt. |

### 7.4 Odczyt

**Najbardziej optymistyczna komórka całej tabeli — nierealistycznie duża różnica ceny 80 PLN przy najniższym koszcie pracy — daje próg 38 sztuk.** Realistyczny środek tabeli to **125–250 sztuk**.

Deklarowana skala to **kilka prototypów**. Rozjazd wynosi **jeden do dwóch rzędów wielkości**.

**Dlatego brak zweryfikowanych cen nie osłabia tego wniosku:** żeby port zwrócił się przy pięciu sztukach, różnica ceny modułu musiałaby wynosić **600–1 000 PLN za sztukę**. Płytka deweloperska ESP32 w tym przedziale cenowym nie istnieje. Wniosek jest niezmienniczy względem Δ w całym realnym zakresie — i **to jest właśnie powód, żeby nie odkładać decyzji do czasu sprawdzenia cen**.

**Odpowiedź na pytanie z briefu — czy stały koszt dwóch wariantów przewyższa całą oszczędność, wprost:** tak. Przy pięciu sztukach i Δ = 40 PLN oszczędność wynosi **200 PLN** jednorazowo. Sam roczny koszt utrzymania drugiego wariantu (16–52 h) to **1 600–7 800 PLN**. Utrzymanie kosztuje **8–39 razy więcej niż całkowita oszczędność**, i to co roku, podczas gdy oszczędność jest jednorazowa.

---

## 8. Ryzyko utrzymania dwóch wariantów

Poza rachunkiem godzinowym z §6.4 dochodzą trzy ryzyka, których nie widać w tabeli.

1. **Dywergencja map pinów.** Dwie mapy w jednym `Config.h` za `#if` to dwa źródła prawdy o sprzęcie. [`01_hardware.md`](./01_hardware.md) jest zadeklarowany jako *„źródło prawdy dla fizycznych połączeń"* i musiałby prowadzić dwie tabele. **Już dziś widać dryf dokumentacji** przy jednym wariancie: brief B-10 wymienia I2C na GPIO 8/9, brief B-11 odsyła do kanałów AIN1–3 układu ADS1015 „wg `01_hardware.md §3`" — a obecna §3 wymienia wyłącznie GPIO 1 dla PT-506 i w kodzie nie ma ani I2C, ani ADS1015 ([§3](#3-korekty-do-założeń-briefu)). Drugi wariant podwaja powierzchnię, na której taki dryf zachodzi.

2. **Brak CI.** W repozytorium nie ma `.github/workflows/` — nic nie zbuduje automatycznie drugiego środowiska. Każde „czy to się jeszcze kompiluje na WROOM" jest czynnością ręczną, a więc pomijalną pod presją czasu. **Ta pozycja rośnie w koszcie dokładnie wtedy, gdy jest najmniej czasu.**

3. **Podwójna weryfikacja sprzętowa nowego czujnika.** [`06_adding_sensors.md`](./06_adding_sensors.md) kroki 5–6 wymagają flashowania, odczytu logów i potwierdzenia w backendzie. Przy dwóch wariantach to podwójnie — plus dobór pinu spełniającego jednocześnie ograniczenia obu chipów, co przy `SOC_GPIO_OUT_RANGE_MAX 33` i pinach tylko-wejściowych 34–39 jest realnym zawężeniem, nie formalnością. Wynik: **wybór pinów dla nowego czujnika zaczyna być dyktowany przez słabszy z dwóch chipów** — czyli projekt na S3 traci swobodę, mimo że S3 jej nie traci.

**Konkluzja:** przy kilku prototypach koszt stały jest nie tylko większy niż oszczędność (§7.4) — on jest **większy o rząd wielkości i powracający co roku**, podczas gdy oszczędność jest jednorazowa. Utrzymywanie dwóch wariantów przy tej skali to strukturalnie zła transakcja niezależnie od cen modułów.

---

## 9. Alternatywa: przemysłowe płytki DIN — czy port i tak będzie potrzebny?

Brief słusznie wskazał, że **to może być ważniejsze niż sam rachunek cenowy**: jeśli droga do wersji przemysłowej i tak prowadzi przez klasyczny ESP32, port przestaje być kwestią oszczędności i staje się warunkiem wejścia.

**Sprawdziłem. Hipoteza się nie potwierdza — rynek jest podzielony, a to zmienia charakter decyzji.**

| Rodzina | Rdzeń | Uwagi |
|---|---|---|
| NORVI IIOT (serie AE01/AE02/AE03) | **ESP32-WROOM-32** | montaż DIN, RS485, wejścia 0–10 V i 4–20 mA, OLED; nowsze serie NORVI deklarują także rdzeń ESP32-S3 |
| Industrial Shields ESP32 PLC / M-DUINO | **ESP32** (klasyczny) | DIN, Modbus, deklarowane CE |
| KinCony (płytka rdzeniowa DIN) | **ESP32-S3-WROOM-1U** (N16R8) | montaż DIN |
| EQSP32 / EQSP32CE | **ESP32-S3** | 16 I/O, DIN, Ethernet w wariancie CE |
| LILYGO T-Connect Pro | **ESP32-S3** | DIN, przekaźnik 10 A, wyświetlacz |
| KLAYERS / eletechsup (płytki w obudowach DIN) | **ESP32-S3** | RS485, obudowa DIN |

*(Zestawienie z przeglądu ofert producentów — **do potwierdzenia** konkretnymi kartami katalogowymi i dostępnością w PL/UE, co i tak należy do zakresu [B-01](../../plan/01_briefy_dla_agentow.md), wariant W3. Tutaj potrzebna jest tylko odpowiedź jakościowa: czy istnieją przemysłowe płytki DIN na S3. Istnieją.)*

**Wnioski — i to jest, jak sądzę, najważniejszy praktyczny rezultat całej analizy:**

1. **Port nie jest warunkiem wejścia na ścieżkę przemysłową.** Skoro istnieją sterowniki DIN na ESP32-S3, można przejść do wersji przemysłowej **bez portu**. Argument, który mógł odwrócić werdykt, odpada.
2. **Wybór płytki przemysłowej jest zmienną swobodną — więc zamiast portować, wystarczy odpowiednio wybrać.** Do kryteriów wariantu W3 w B-01 należy dopisać **„rdzeń ESP32-S3"** obok stopnia IP, zakresu temperatur, CE i dostępności w PL/UE. Koszt tego kroku: jedno zdanie w briefie. Koszt alternatywy: 14–28 h plus 16–52 h/rok.
3. **Ale jeśli wygra płytka na klasycznym ESP32, port trzeba wtedy wycenić w porównaniu W3, a nie potraktować jako darmowy.** Gdyby NORVI albo Industrial Shields okazały się wyraźnie lepsze na pozostałych kryteriach, **koszt portu (14–28 h) jest częścią ceny tej płytki** i tak ma wejść do zestawienia. Wtedy nie jest to już inwestycja w oszczędność na module, tylko **koszt wejścia w konkretny, świadomie wybrany produkt** — i to jest zupełnie inna decyzja, podejmowana na innych przesłankach.

**Ta analiza staje się więc wejściem do B-01**: dostarcza cenę pozycji „port" w porównaniu wariantów sprzętowych, zamiast rozstrzygać sprawę samodzielnie.

---

## 10. Rekomendacja i warunki, które zmieniłyby werdykt

### Rekomendacja

**Nie portować. Zamiast tego wykonać dwie tanie czynności:**

1. **Refaktor `StatusLed`** — zastąpić `pin_ == 48` jawnym trybem diody ([§4.2](#42-led-statusu)). ~20 linii, 1–2 h. Uzasadnienie niezależne od portu: usuwa numer pinu w roli ukrytego przełącznika typu sprzętu i czyni klasę testowalną w `env:native`. **Robi ~80% tego, co port miałby zrobić w kodzie, za ~1% jego kosztu** — i sprawia, że gdyby port kiedyś wrócił, zaczyna się od gotowej abstrakcji.
2. **Dopisać kryterium „rdzeń ESP32-S3" do wariantu W3 w [B-01](../../plan/01_briefy_dla_agentow.md)** ([§9](#9-alternatywa-przemysłowe-płytki-din--czy-port-i-tak-będzie-potrzebny)). Koszt: jedno zdanie. Efekt: usuwa jedyny scenariusz, w którym port byłby wymuszony.

### Trzy warunki, z których **każdy z osobna** odwraca werdykt

| # | Warunek | Dlaczego zmienia rachunek | Jak sprawdzić |
|---|---|---|---|
| 1 | **Skala rośnie do ≥ 100 sztuk** rocznie | Wchodzimy w środek tabeli §7.3, gdzie próg jest przekroczony przy realistycznych założeniach | decyzja biznesowa; sygnał: drugi lub trzeci klient z powtarzalnym zamówieniem |
| 2 | **Wybrana płytka przemysłowa DIN stoi na klasycznym ESP32** (np. NORVI, Industrial Shields) i wygrywa na pozostałych kryteriach | Port przestaje być oszczędnością, a staje się kosztem wejścia — i wtedy wchodzi do rachunku W3 jako pozycja, nie jako alternatywa | wynik [B-01](../../plan/01_briefy_dla_agentow.md), wariant W3 |
| 3 | **Trwały brak dostępności modułów ESP32-S3** w PL/UE | Wtedy to nie jest już rachunek opłacalności, tylko ciągłość dostaw — a wtedy port jest jedynym wyjściem i jego koszt przestaje mieć znaczenie | monitoring stanów u dystrybutorów; sygnał: czas realizacji > 12 tygodni |

**Warunki 1 i 2 są rozstrzygane poza tym dokumentem** — pierwszy przez rozwój sprzedaży, drugi przez B-01. Dlatego rekomendacja brzmi „nie portować **teraz**", nie „nie portować nigdy”. Ta analiza zachowuje ważność jako wejście do przyszłego zlecenia.

---

## 11. Czego nie dało się zweryfikować — lista do domknięcia

Trzy pozycje. Żadna nie zmienia werdykt z §1; pierwsza zmienia oszacowanie kosztu, jeśli port kiedyś ruszy.

### 11.1 Realny rozmiar obrazu binarnego — **jedyna pozycja o realnych konsekwencjach**

**Dlaczego brakuje:** rejestr PlatformIO zablokowany przez proxy sieciowe środowiska; `pio pkg install -e esp32-s3` kończy się `HTTPClientError`, więc build był niewykonalny.

**Jak domknąć — jedno polecenie na maszynie z dostępem do sieci:**

```bash
cd firmware
pio run -e esp32-s3          # odczytaj wiersz "Flash: [==   ] xx.x% (used NNNNNN bytes ...)"
```

**Jak zinterpretować wynik** (limity z [§4.4](#44-pamięć), liczby dokładne):

| Rozmiar `.bin` | Znaczenie |
|---|---|
| **< 1 310 720 B** (1,25 MiB) | mieści się w domyślnym `default.csv`, żadna zmiana partycji niepotrzebna |
| **1 310 720 – 1 966 080 B** | wymaga `board_build.partitions = min_spiffs.csv`; **OTA zachowane, koszt zerowy** (projekt nie używa SPIFFS) |
| **> 1 966 080 B** (1,875 MiB) | trzeba wybierać: rezygnacja z OTA (`no_ota.csv`), moduł WROOM-32E 8 MB (**unieważnia cel portu**, bo podnosi cenę), albo odchudzenie obrazu. **Dopiero ten przedział podnosi koszt portu ponad wycenę z §6** |

### 11.2 Aktualne ceny modułów

**Dlaczego brakuje:** domeny dystrybutorów (Botland, Kamami, TME) zablokowane przez proxy środowiska.

**Do sprawdzenia:** cena ESP32-S3-DevKitC-1-N8 vs ESP32 DevKit V1 / ESP-WROOM-32, oraz **dostępność i czas realizacji** — bo drugi motyw z briefu, obok ceny, to dostępność, a przy kilku prototypach dostępność waży więcej niż cena.

**Jak użyć wyniku:** wstawić Δ do tabeli w [§7.3](#73-tabela-wrażliwości--próg-n-w-sztukach). **Werdykt zmieniłby się dopiero przy Δ rzędu 600–1 000 PLN/szt.**, co nie występuje w tej klasie sprzętu.

### 11.3 Czasy operacji kryptograficznych na obu chipach

**Dlaczego brakuje:** brak sprzętu i brak buildu.

**Procedura pomiaru** (~1 h, wymaga obu płytek):

```cpp
// tymczasowo w loop(), przed deviceIdentity.ensureKey() — main.cpp:199-202
unsigned long t0 = millis();
deviceIdentity.ensureKey();
LOG_INFO("[BENCH]", "keygen: %lu ms", millis() - t0);

uint8_t nonce[32] = {0};                       // podpis: DeviceIdentity.cpp:79
t0 = millis();
deviceIdentity.signBase64(nonce, sizeof(nonce));
LOG_INFO("[BENCH]", "sign: %lu ms", millis() - t0);
```

Punkt odniesienia: **~2–3 s** dla generowania klucza na S3 ([`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md)). Oczekiwane na WROOM-32: **~2,5–4 s**.

**Uwaga: to pomiar dla kompletności, nie dla decyzji.** Operacja wykonuje się poza oknem RTC WDT, w `loop()` ([§4.3](#43-kryptografia--punkt-krytyczny-briefu-okazał-się-nie-istnieć)), więc nawet dwukrotnie gorszy wynik niczego nie łamie. Pamiętaj, że `ensureKey()` działa raz w życiu urządzenia — do powtórzenia pomiaru trzeba wyczyścić NVS (`pio run -t erase`), co **kasuje tożsamość urządzenia i wymaga nowego kodu aktywacyjnego** ([§4.8 A](#a-numer-seryjny-pochodzi-z-adresu-mac--każdy-moduł-to-osobna-tożsamość-urządzenia)).

---

## 12. Materiał wejściowy dla przyszłego zlecenia „port"

Zgodnie z ograniczeniem briefu **nie piszę tu planu wdrożenia**. Poniżej wyłącznie wskazanie, gdzie leży materiał, żeby takie zlecenie dało się sformułować od razu, bez powtarzania analizy:

| Potrzebne zleceniu | Gdzie jest |
|---|---|
| Kompletna mapa pinów z uzasadnieniem każdego wyboru | [§4.1.3](#413-proponowana-mapa-dla-esp-wroom-32) |
| Pułapki, które wywrócą bring-up, jeśli się ich nie zna | [§4.1.4](#414-dwie-pułapki-strappingowe--najważniejsza-część-mapy-pinów) |
| Rozstrzygnięcie sprawy diody + wybór płytki | [§4.2](#42-led-statusu) |
| Szkielet `platformio.ini` z dwoma środowiskami | [§4.7](#47-platformioini) |
| Wybór tablicy partycji z progami decyzyjnymi | [§4.4](#44-pamięć), [§11.1](#111-realny-rozmiar-obrazu-binarnego--jedyna-pozycja-o-realnych-konsekwencjach) |
| Lista plików do zmiany z oszacowaniem skali | [§6.1](#61-zmiany-w-kodzie--mały-dobrze-ograniczony-zakres) |
| Zakres weryfikacji sprzętowej | [§6.2](#62-sprzęt-i-uruchomienie--tu-leży-6070-kosztu) |
| Co trzeba zmierzyć **przed** startem | [§11](#11-czego-nie-dało-się-zweryfikować--lista-do-domknięcia) |

**Warunek wstępny takiego zlecenia:** spełnienie **co najmniej jednego** z trzech warunków z [§10](#10-rekomendacja-i-warunki-które-zmieniłyby-werdykt). Bez tego zlecenie kupuje ujemną wartość.

---

## 13. Źródła

### Kod i dokumentacja repozytorium

- [`firmware/include/Config.h`](../../../firmware/include/Config.h), [`firmware/platformio.ini`](../../../firmware/platformio.ini), [`firmware/src/main.cpp`](../../../firmware/src/main.cpp)
- [`lib/StatusLed/src/StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp), [`lib/DeviceIdentity/src/DeviceIdentity.cpp`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp), [`lib/TelemetryPayload/src/TelemetryPayload.cpp`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp), [`lib/ModemLink/src/ModemLink.cpp`](../../../firmware/lib/ModemLink/src/ModemLink.cpp), [`lib/ModemPower/src/ModemPower.cpp`](../../../firmware/lib/ModemPower/src/ModemPower.cpp), [`lib/Watchdog/src/Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp), [`lib/Sensor/src/PT100Sensor.cpp`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp), [`lib/EnrollmentClient/src/EnrollmentClient.cpp`](../../../firmware/lib/EnrollmentClient/src/EnrollmentClient.cpp)
- [`01_hardware.md`](./01_hardware.md), [`02_modem_a7670e_communication.md`](./02_modem_a7670e_communication.md), [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md), [`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md), [`06_adding_sensors.md`](./06_adding_sensors.md)
- [`docs/plan/01_briefy_dla_agentow.md`](../../plan/01_briefy_dla_agentow.md) — briefy B-01 (warianty sprzętowe), B-10, B-11

### Źródła Espressif (kod źródłowy, nie materiały marketingowe)

- `components/soc/esp32/include/soc/soc_caps.h` i `components/soc/esp32s3/include/soc/soc_caps.h`, ESP-IDF v5.3 — możliwości SoC: `SOC_ECC_SUPPORTED` (brak na obu), `SOC_MPI/SHA/AES_SUPPORTED`, `SOC_HMAC/DIG_SIGN_SUPPORTED` (tylko S3), `SOC_GPIO_IN_RANGE_MAX`/`OUT_RANGE_MAX`, `SOC_UART_NUM`, `SOC_RTC_*_MEM_SUPPORTED`
- `components/mbedtls/Kconfig`, ESP-IDF v5.3 — `MBEDTLS_HARDWARE_ECC` (`depends on SOC_ECC_SUPPORTED`), `MBEDTLS_HARDWARE_MPI`, `MBEDTLS_MPI_USE_INTERRUPT` (`depends on !IDF_TARGET_ESP32`)
- `components/soc/esp32/gpio_periph.c`, ESP-IDF v5.3 — nieistniejące GPIO 24, 28–31
- `components/soc/esp32/include/soc/soc.h`, ESP-IDF v5.3 — `SOC_RTC_DATA_LOW/HIGH` (8 KiB)
- `docs/en/api-reference/peripherals/gpio/esp32.inc` i `esp32s3.inc`, ESP-IDF v5.3 — tabele GPIO, piny strappingowe, `SPI0/1`, ograniczenia ADC2
- `cores/esp32/HardwareSerial.h` (linie 438–452), `variants/esp32/pins_arduino.h`, `variants/doitESP32devkitV1/pins_arduino.h`, `variants/esp32s3/pins_arduino.h`, `tools/partitions/{default,default_8MB,min_spiffs,no_ota}.csv` — arduino-esp32
- `boards/{esp32dev,esp32-s3-devkitc-1}.json` — platform-espressif32

### Źródła zewnętrzne (do potwierdzenia kartami katalogowymi)

- Stany domyślne pinów strappingowych ESP32 (GPIO0 ↑, GPIO2 ↓, GPIO5 ↑, GPIO12 ↓, GPIO15 ↑) oraz skutek wysokiego MTDI: [Boot Mode Selection — esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html), [ESP32 Series Datasheet](https://www.mouser.com/datasheet/2/813/esp32_datasheet_en_1223853-1919342.pdf), [ESP32 Strapping Pins](https://www.espboards.dev/blog/esp32-strapping-pins/)
- Przemysłowe sterowniki DIN — rdzenie ([§9](#9-alternatywa-przemysłowe-płytki-din--czy-port-i-tak-będzie-potrzebny)): [NORVI IIOT](https://norvi.io/norvi-iiot-esp32-industrial-controller/), [Industrial Shields ESP32 PLC](https://www.industrialshields.com/industrial-hardware-solutions-based-on-esp32), [KinCony ESP32-S3](https://www.kincony.com/kincony-esp32-s3-core-board.html), [EQSP32](https://erqos.com/resources/eqsp32x-industrial-iot-controller/), [LILYGO T-Connect Pro](https://www.hackster.io/news/lilygo-goes-after-the-industrial-automators-with-the-din-mountable-t-connect-pro-9c4db04fb48e)
- **Ceny modułów: nie zweryfikowane** — patrz [§11.2](#112-aktualne-ceny-modułów)
