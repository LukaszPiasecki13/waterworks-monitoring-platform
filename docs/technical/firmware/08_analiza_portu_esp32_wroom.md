# Port ESP32-S3 → ESP-WROOM-32: wykonalność i lista zmian

> Analiza wykonalności przeniesienia firmware gatewaya z ESP32-S3-DevKitC-1 na klasyczny ESP32 (ESP-WROOM-32) oraz kompletna specyfikacja tego, co trzeba zmienić.
> **Zlecenie B-10**, zawężone zgodnie z ustaleniem: **etap prototypu, okablowanie i układ swobodnie zmienialne, rachunek opłacalności poza zakresem.**
>
> Dokument kończy się na specyfikacji — implementacja jest osobnym krokiem. Fragmenty kodu w [§6](#6-zmiany-w-kodzie) są gotowe do wklejenia, nie szkicowe.
>
> **Status: analiza statyczna kodu i źródeł Espressif. Bez buildu i bez weryfikacji na sprzęcie** — granice opisuje [§2](#2-metoda-i-granice-tej-analizy). Jedna otwarta kwestia wykonalności ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)) rozstrzyga się jednym poleceniem.
>
> Data: 2026-09-01

---

## 1. Odpowiedź

**Tak, da się. Nie ma blokady technicznej.**

Zależności od ESP32-S3 w całym firmware sprowadzają się do **ośmiu numerów GPIO i jednej diody**. Nie ma ani jednego wywołania API, peryferium ani biblioteki, które istnieją tylko na S3.

Trzy rzeczy, które warto wiedzieć zanim zaczniesz przepinać kable:

1. **Punkt, który brief wskazał jako krytyczny, nie jest zależnością od S3.** Kryptografia P-256 w `DeviceIdentity` liczy się **programowo na obu chipach** — ani ESP32, ani ESP32-S3 nie mają sprzętowego akceleratora ECC ([§8.1](#81-kryptografia--brak-akceleratora-ecc-na-obu-chipach)). Nie ma tu nic do przenoszenia ani do naprawiania.
2. **Jedyna otwarta kwestia to rozmiar obrazu binarnego.** Nie zmienia się rozmiar pamięci RAM ani flasha jako takich, tylko **domyślna partycja aplikacji: 3,19 MiB → 1,25 MiB**. Sprawdzenie zajmuje 30 sekund, a gdyby nie wystarczyło, `min_spiffs.csv` daje 1,875 MiB **z zachowaniem OTA** ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)).
3. **Trzy pułapki elektryczne zjedzą Ci wieczór, jeśli o nich nie wiesz** — GPIO 5 i GPIO 12 (strapping) oraz pływające linie RESET/PWRKEY modemu, które dotyczą też dzisiejszego S3. Objaw pierwszej jest identyczny z regresją, która w tym projekcie już raz kosztowała cykl diagnostyczny. Mapa w [§5](#5-mapa-pinów) omija je; uzasadnienie w [§5.3](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli).

**Nakład: ~90 linii kodu w trzech plikach + przepięcie 9 połączeń.** Praca leży w uruchomieniu na sprzęcie, nie w pisaniu kodu.

**Jedyna funkcja tracona bezpowrotnie** — peryferium HMAC + Digital Signature, którego klasyczny ESP32 nie ma. Dziś nieużywane, ale to naturalna droga utwardzenia tożsamości urządzenia ([§9](#9-co-realnie-tracisz)). Warto o tym wiedzieć świadomie, a nie odkryć później.

---

## 2. Metoda i granice tej analizy

### 2.1 Co zostało zweryfikowane bezpośrednio

| Obszar | Źródło | Wiarygodność |
|---|---|---|
| Użycie GPIO, peryferiów, API | pełny odczyt `firmware/` — 2 516 linii, wszystkie 21 plików `.cpp`/`.h` + `platformio.ini` | **wysoka** — kod, nie dokumentacja |
| Możliwości SoC (ECC, MPI, SHA, HMAC, DS, GPIO, RTC, UART) | `soc_caps.h` dla `esp32` i `esp32s3`, ESP-IDF v5.3 | **wysoka** — kod źródłowy Espressif |
| Akceleracja sprzętowa w mbedTLS | `components/mbedtls/Kconfig`, ESP-IDF v5.3 | **wysoka** |
| Ograniczenia GPIO klasycznego ESP32 | `docs/en/api-reference/peripherals/gpio/esp32.inc` + `components/soc/esp32/gpio_periph.c` | **wysoka** |
| Partycje, limity RAM, PSRAM | manifesty płytek `platform-espressif32` + `tools/partitions/*.csv` z arduino-esp32 | **wysoka** |
| Mapowanie `Serial` na UART0 vs USB CDC | `cores/esp32/HardwareSerial.h` | **wysoka** |
| `LED_BUILTIN` per wariant płytki | `variants/*/pins_arduino.h` | **wysoka** |

### 2.2 Czego nie dało się zrobić

**Buildu.** Rejestr PlatformIO jest zablokowany przez proxy sieciowe tego środowiska — `api.registry.platformio.org` i `dl.registry.platformio.org` nie odpowiadają w ogóle, przy dostępnym GitHubie. Samą platformę udało się zainstalować z gita (`espressif32@7.1.0+sha.b753f4d`), ale toolchain `espressif/toolchain-xtensa-esp32s3` nadal rozwiązuje się przez rejestr i kończy `HTTPClientError`.

**Konsekwencja:** nie mam realnego rozmiaru obrazu binarnego. To jedyna liczba potrzebna do domknięcia wykonalności w 100% — i u Ciebie jest to jedno polecenie ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)). Wszystko inne, co poniżej, jest ustalone z dokładnych źródeł, nie oszacowane.

**Fizyczny układ listwy DevKitu.** Mapa pinów w [§5](#5-mapa-pinów) jest poprawna elektrycznie (to wynika ze źródeł Espressif). Uwagi o **sąsiedztwie pinów na listwie** to wskazówka pod wygodę okablowania — **zweryfikuj na silkscreenie swojej płytki**, bo warianty 30- i 36-pinowe różnią się układem.

---

## 3. Korekty do założeń briefu

Trzy punkty briefu nie zgadzają się ze stanem kodu, a jeden jest niepełny. Zmienia to zakres pracy — na mniejszy.

| Założenie briefu | Stan faktyczny | Skutek |
|---|---|---|
| *„`Config.h` używa GPIO 4, 5, **8, 9**, 11, 12…"*, *„wymusza przemapowanie **I2C (dziś 8/9)**"* | **W firmware nie ma I2C.** `Config.h` definiuje 9 pinów: 4, 5, 11, 12, 13, 14, 17, 18, 48 ([`Config.h:15-29`](../../../firmware/include/Config.h#L15-L29)). Grep po `firmware/` na `Wire`, `I2C`, `SDA`, `SCL`, `ADS1015`, `ADS1115`, `analogRead`, `ADC` → **zero trafień** | **mniej pracy** — nie ma magistrali I2C do przemapowania. Wzmianki o ADS1015 pochodzą z briefu B-11 i starszej wersji [`01_hardware.md`](./01_hardware.md); obecna §3 wymienia tylko GPIO 1 (ADC1_CH0) pod PT-506, ze statusem **draft** |
| *„GPIO 6–11 są zajęte przez flash SPI"* | Prawda, ale **niepełna**. ESP-IDF wymienia także **GPIO 16–17**: *„GPIO6-11 and GPIO16-17 are usually connected to the SPI flash and PSRAM integrated on the module"* | dotyczy `MODEM_TX_PIN = 17`. Na WROOM-32 (bez PSRAM) 16/17 są wolne, ale wiązanie się z nimi zamyka drogę do modułów WROVER. Mapa w [§5](#5-mapa-pinów) ich nie używa |
| *„S3 ma natywne USB CDC, klasyczny ESP32 wymaga konwertera UART"* | **Bieżący build nie używa USB CDC.** `ARDUINO_USB_CDC_ON_BOOT` domyślnie `0` (arduino-esp32, `HardwareSerial.h:438-439`); `platformio.ini` go nie ustawia, manifest płytki ustawia tylko `ARDUINO_USB_MODE=1`. Przy `== 0` obowiązuje `#define Serial Serial0` → **UART0** | **zerowy wpływ** — firmware już dziś loguje przez zwykły UART0 i mostek USB-UART. Punkt 5 briefu odpada w całości ([§8.4](#84-usbserial--już-dziś-uart0)) |
| *„watchdog `esp_task_wdt` z timeoutem 15 s wg `platformio.ini`"* | `platformio.ini:19` ustawia `-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15`, ale **nigdzie w `firmware/` nie ma `esp_task_wdt_init()` ani `esp_task_wdt_add()`** (grep: 0 trafień; jest tylko `esp_task_wdt_reset()`). Dodatkowo `-D` w `build_flags` nie sięga prekompilowanych bibliotek ESP-IDF frameworku Arduino — `sdkconfig` jest zapieczony | realnym budżetem czasowym przy generowaniu klucza jest **RTC WDT bootloadera**, nie Task WDT — zgodnie z tym, co mówi [`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md) („~9s budżetu na cały boot"). **To dotyczy tak samo dzisiejszego S3 — nie jest problemem portu**, ale warto zgłosić osobno ([§8.1](#81-kryptografia--brak-akceleratora-ecc-na-obu-chipach)) |

---

## 4. Lista zmian — skrót

Wszystko, co trzeba ruszyć. Szczegóły w kolejnych sekcjach.

| # | Co | Gdzie | Rodzaj | Nakład |
|---|---|---|---|---|
| 1 | Nowa mapa pinów za `#if defined(BOARD_ESP32_WROOM)` | [`Config.h`](../../../firmware/include/Config.h) | kod, ~30 linii | 1 h |
| 2 | Jawny typ diody zamiast porównania `pin_ == 48` w dwóch miejscach | [`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp) + `.h` | kod, ~40 linii | 1–2 h |
| 3 | Sekcja `[env]` + nowe `[env:esp32-wroom]` z wyborem partycji | [`platformio.ini`](../../../firmware/platformio.ini) | konfiguracja, ~20 linii | 1 h |
| 4 | Przepięcie 9 połączeń wg [tabeli przepięć](#54-tabela-przepięć--co-gdzie-przełożyć) | sprzęt | okablowanie | 1–2 h |
| 5 | **Rezystory 10 kΩ do GND na liniach RESET i PWRKEY modemu** ([§5.3 C](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli)) | sprzęt | 2 rezystory | 15 min |
| 6 | Sprawdzenie rozmiaru obrazu i ewentualnie `min_spiffs.csv` | build | weryfikacja | 5 min |
| 7 | Uruchomienie i weryfikacja pełnego łańcucha | sprzęt | bring-up | 6–12 h |
| 8 | Druga mapa pinów w dokumentacji sprzętowej | [`01_hardware.md`](./01_hardware.md), [`02_modem…md §2.2`](./02_modem_a7670e_communication.md) | dokumentacja | 2 h |

**Bez zmian zostaje cała logika:** protokół telemetrii, provisioning, autoryzacja, watchdog, sterowniki czujników, testy jednostkowe. **Żadnej zmiany w bibliotekach zewnętrznych.**

Największa pozycja to #7, i tak ma być — [§10](#10-kolejność-uruchomienia) rozpisuje ją na kroki, żeby błędy wychodziły pojedynczo, a nie wszystkie naraz.

---

## 5. Mapa pinów

### 5.1 Ograniczenia klasycznego ESP32 — twarde fakty

Ze źródła dokumentacji ESP-IDF v5.3 (`docs/en/api-reference/peripherals/gpio/esp32.inc`) i `components/soc/esp32/gpio_periph.c`:

- **34 fizyczne GPIO:** 0–19, 21–23, 25–27, 32–39. GPIO **24, 28, 29, 30, 31 nie istnieją** (w `GPIO_PIN_MUX_REG[]` mają wartość `0`); GPIO 20 tylko w obudowie ESP32-PICO-V3.
- **GPIO 6–11 oraz 16–17** — `SPI0/1`, flash i PSRAM modułu.
- **GPIO 34–39** — tylko wejście, bez programowych podciągnięć. Potwierdza `soc_caps.h`: `SOC_GPIO_IN_RANGE_MAX 39` przy `SOC_GPIO_OUT_RANGE_MAX 33`.
- **Piny strappingowe: 0, 2, 5, 12 (MTDI), 15 (MTDO).** Stany domyślne przy resecie: GPIO0 ↑, GPIO2 ↓, GPIO5 ↑, GPIO12 ↓, GPIO15 ↑.
- **GPIO 1/3** — konsola UART0 (flashowanie i logi).
- **ADC1: GPIO 32–39.** ADC2 (0, 2, 4, 12–15, 25–27) nie działa przy aktywnym Wi-Fi — u nas Wi-Fi nie jest używane, ale trzymanie pomiarów na ADC1 zdejmuje ten temat na zawsze.
- Na modułach ESP-WROOM-32 **GPIO 37 i 38 nie są wyprowadzone**.

Dla kontrastu: na ESP32-S3 pinami strappingowymi są **0, 3, 45, 46** — czyli **żaden z pinów używanych dziś przez firmware**. Na klasycznym ESP32 dwa z nich (5 i 12) już nimi są, i stąd bierze się większość pracy.

### 5.2 Proponowana mapa

Kryteria, w kolejności: (1) zero pinów strappingowych i zero `SPI0/1`; (2) SPI na natywnych pinach IO_MUX magistrali VSPI; (3) każda magistrala w jednym zwartym bloku, żeby okablowanie było czytelne; (4) zostawić wolne kanały ADC1 pod PT-506 i przyszłe czujniki analogowe.

Skoro okablowanie jest swobodne, mapa jest optymalizowana **pod czystość układu, nie pod minimum przelutowania**.

| Funkcja | S3 dziś | **WROOM-32** | Uzasadnienie |
|---|---|---|---|
| `MODEM_RESET_PIN` | 5 | **33** | GPIO 5 jest strappingowy i **domyślnie podciągnięty w górę**, a RESET modemu jest **active-HIGH** — patrz pułapka A w [§5.3](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli). GPIO 33 jest wyjściowy i nie strappingowy. *Kosztuje jeden kanał ADC1 (CH5)* — jeśli kiedyś zabraknie wejść analogowych, przenieś RESET na **GPIO 4**, które jest wolne i leży poza ADC1 (ADC2 nas nie interesuje, bo Wi-Fi nie jest używane) |
| `MODEM_TX_PIN` (→ RX modemu) | 17 | **25** | GPIO 17 jest oznaczony `SPI0/1`. Świadomie **nie** biorę pary 16/17 (naturalne UART2), żeby mapa działała także na modułach z PSRAM |
| `MODEM_RX_PIN` (← TX modemu) | 18 | **26** | Para z 25; GPIO 18 przejmuje SPI SCK. UART1 idzie przez macierz GPIO — `ModemLink` już dziś podaje piny jawnie ([`ModemLink.cpp:18`](../../../firmware/lib/ModemLink/src/ModemLink.cpp#L18)), a rdzeń Arduino honoruje piny jawne nad domyślnymi |
| `MODEM_PWRKEY_PIN` | 4 | **27** | GPIO 4 jest wolny i mógłby zostać, ale przy swobodnym okablowaniu lepiej trzymać **wszystkie cztery sygnały modemu w jednym bloku 33/25/26/27** niż oszczędzić jedno przepięcie |
| `PT100_SPI_SCK` | 12 | **18** | GPIO 12 = MTDI, wybór napięcia flash — pułapka B w [§5.3](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli). GPIO 18 to natywny **IO_MUX VSPI CLK** |
| `PT100_SPI_MISO` | 13 | **19** | Natywny **IO_MUX VSPI MISO** |
| `PT100_SPI_CS` | 14 | **22** | CS jest sterowany **programowo** przez `Adafruit_MAX31865`, więc nie musi być na IO_MUX. Natywny VSPI CS0 to GPIO 5 — strappingowy, dlatego świadomie odpada. GPIO 22 leży obok 23 |
| `PT100_SPI_MOSI` | 11 | **23** | GPIO 11 to flash. GPIO 23 to natywny **IO_MUX VSPI MOSI** |
| `LED_PIN` | 48 | **2** | GPIO 48 nie istnieje na klasycznym ESP32. GPIO 2 to `LED_BUILTIN` wariantu `doitESP32devkitV1` — **wybór płytki ma tu znaczenie**, patrz [§5.5](#55-dioda-statusu) |
| PT-506 ADC (*draft*) | 1 | **34** (ADC1_CH6) | Wejście analogowe nie potrzebuje trybu wyjściowego, więc pin *input-only* jest tu idealny — nie marnujemy pinu dwukierunkowego. **Celowo nie 36/39 (VP/VN):** ESP-IDF ostrzega, że na tych dwóch nie należy używać przerwań przy aktywnym ADC (errata ESP32 §3.11). Odczyt PT-506 byłby odpytywany, nie przerwaniowy, więc 36 też by działało — ale 34 zdejmuje ten przypis całkowicie. Wolne rezerwy ADC1: 35, 36, 39 |

**Układ, który z tego wychodzi:** cztery sygnały modemu w bloku **33/25/26/27**, cztery sygnały SPI w bloku **18/19/22/23**, dioda na **2**, analog na **36** — trzy zwarte grupy zamiast sygnałów rozrzuconych po całej listwie. *(Na typowym 30-pinowym DevKit V1 obie grupy wypadają po przeciwnych stronach płytki, co dodatkowo porządkuje wiązkę — **zweryfikuj na silkscreenie**, [§2.2](#22-czego-nie-dało-się-zrobić).)*

**Wolne po tej mapie:** 4, 12*, 13, 14, 15*, 21, 32, 34, 35, 39 (+16, 17 z zastrzeżeniem PSRAM; `*` = strappingowe, używać ostrożnie). **Dziewięć pinów zajętych, dziesięć wolnych** — zapas na kolejne czujniki jest spory i liczba pinów nie będzie ograniczeniem.

### 5.3 Trzy pułapki elektryczne — przeczytaj przed przepięciem kabli

To jest najważniejsza część mapy. Wszystkie trzy dają objawy trudne do powiązania z przyczyną.

**Pułapka A — GPIO 5 jako RESET modemu.**

Na płytce KAmod RESET jest **active-HIGH**: `HIGH = modem trzymany w resecie` ([`02_modem §2.2`](./02_modem_a7670e_communication.md)). Na klasycznym ESP32 GPIO 5 jest strappingowy z **domyślnym podciągnięciem w górę** — więc od podania zasilania aż do momentu, w którym `ModemPower::powerOn()` ustawi go w stan LOW ([`ModemPower.cpp:16`](../../../firmware/lib/ModemPower/src/ModemPower.cpp#L16)), linia RESET stoi wysoko i **modem jest trzymany w resecie przez cały boot ESP32**. Na S3 GPIO 5 nie jest strappingowy i tego podciągnięcia nie ma.

To dokładnie ta klasa błędu, która **w tym projekcie już raz kosztowała cykl diagnostyczny**: [`02_modem §7.3`](./02_modem_a7670e_communication.md) opisuje regresję „RESET pin held HIGH" — timeout inicjalizacji modemu 10,3 s, przyczyna w jednej linii polaryzacji, po naprawie init w 132 ms. Objaw byłby ten sam, a przyczyna tym razem leżałaby w krzemie, nie w kodzie — czyli szukałbyś jej znacznie dłużej. **Dlatego RESET idzie na GPIO 33.**

**Pułapka B — GPIO 12 (MTDI) jako SPI SCK.**

MTDI przy starcie wybiera napięcie flash: niski → 3,3 V, wysoki → 1,8 V. Wysoki stan przy starcie na module z flashem 3,3 V oznacza brown-out i **płytkę, która się nie bootuje**. `Adafruit_MAX31865` pracuje w SPI Mode 1 (CPOL=0), więc SCK spoczywa nisko i w typowym przypadku byłoby bezpiecznie — ale wystarczy podciągnięcie na module breakout albo drugie urządzenie na magistrali. Przy dziesięciu wolnych pinach nie ma powodu podejmować tego ryzyka.

**Pułapka C — obie linie sterujące modemu wiszą w powietrzu przez cały boot. Dotyczy tak samo dzisiejszego S3.**

To znalazłem dopiero przy przeglądzie własnej mapy i jest to jedyna pułapka, która **nie jest specyficzna dla portu** — ale port jest dobrym momentem, żeby ją zamknąć.

RESET i PWRKEY są **oba active-HIGH** ([`02_modem §2.2`](./02_modem_a7670e_communication.md)). Na ESP32 wszystkie GPIO poza strappingowymi startują jako **wejścia bez podciągnięcia** — czyli od podania zasilania aż do `pinMode(..., OUTPUT)` w [`ModemPower::powerOn()`](../../../firmware/lib/ModemPower/src/ModemPower.cpp) obie linie są **pływające**, a nie zdefiniowane jako niskie. Stan wejść modemu w tym oknie zależy wtedy wyłącznie od tego, czy płytka KAmod ma własne rezystory ściągające — czego nie udało mi się potwierdzić w dokumentacji producenta.

Konsekwencje, gdyby ich nie miała: przypadkowy reset lub przypadkowy impuls power-on modemu przy każdym starcie i przy każdym `esp_restart()` z recovery ([`Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp)) — czyli objaw okresowy i trudny do odtworzenia na żądanie.

**Zalecenie: rezystory ściągające 10 kΩ do masy na obu liniach, po stronie modemu.** Kosztują grosze, są neutralne dla działania (ESP32 i tak wysteruje je twardo po `pinMode`) i zdejmują całą klasę problemu. Przy prototypie, gdzie i tak przepinasz kable, to najtańszy moment, żeby to zrobić.

**Uwaga do pułapki A:** przeniesienie RESET z GPIO 5 na 33 usuwa problem *podciągnięcia w górę*, ale **nie zastępuje rezystora ściągającego** — 33 pływa zamiast być podciągnięte wysoko, co jest lepsze, ale wciąż nie jest stanem zdefiniowanym.

**Rzecz czwarta, drobna — GPIO 2 pod diodę.** GPIO 2 też jest strappingowy (domyślnie ↓) i przy starcie nie może być trzymany wysoko. Dioda z rezystorem szeregowym do masy — czyli standardowy układ na DevKit V1 — jest bezpieczna. Zewnętrzna dioda podpięta „do plusa" **nie byłaby**.

### 5.4 Tabela przepięć — co gdzie przełożyć

Mapa z [§5.2](#52-proponowana-mapa) podaje piny po stronie ESP32. Przy lutownicy potrzebna jest druga strona, więc tu jest komplet „z czego → na co". Piny po stronie KAmod pochodzą z [`01_hardware.md §7`](./01_hardware.md) (status **draft** — przełożenie na złącze 40-pin nie jest zweryfikowane w kodzie, tylko docelowe GPIO).

| Przewód | Druga strona | ESP32-S3 (odepnij z) | **WROOM-32 (wepnij w)** |
|---|---|---|---|
| TXD modemu → RX ESP32 | KAmod, **pin 10** złącza 40-pin | 18 | **26** |
| RXD modemu ← TX ESP32 | KAmod, **pin 8** | 17 | **25** |
| RST modemu (active-HIGH) | KAmod, **pin 12** | 5 | **33** + rezystor 10 kΩ do GND ([§5.3 C](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli)) |
| PWRKEY modemu (active-HIGH) | KAmod, **pin 7** | 4 | **27** + rezystor 10 kΩ do GND |
| CLK | MAX31865, pad `CLK` | 12 | **18** |
| SDO (wyjście z MAX31865) | MAX31865, pad `SDO` | 13 | **19** |
| SDI (wejście do MAX31865) | MAX31865, pad `SDI` | 11 | **23** |
| CS | MAX31865, pad `CS` | 14 | **22** |
| Dioda statusu | on-board | 48 (WS2812) | **2** (zwykła LED, [§5.5](#55-dioda-statusu)) |
| PT-506, 4-20 mA przez 250 Ω (*draft*) | — | 1 | **34** |

**Bez zmian, ale sprawdź przy okazji:**

- **Zasilanie modemu** — osobne 5 V / min. 2 A na piny **2 i 4** złącza KAmod, **nie z ESP32** ([`01_hardware.md §7`](./01_hardware.md)).
- **Wspólna masa** ESP32 ↔ KAmod (piny GND: 6, 9, 14, 20, 25, 30, 34, 39) — obowiązkowa, bez niej UART nie zadziała albo zadziała niestabilnie.
- **Zworki J2** na KAmodzie muszą być założone dla TXD, RXD, PWK i RST — bez zworki sygnał nie pojawi się na złączu mimo poprawnego okablowania po stronie ESP32. To najczęstsza przyczyna „przepiąłem wszystko, a nie działa".
- **Zworka J_APWK** (spód płytki) — steruje automatycznym impulsem power-on. `ModemPower::powerOn()` generuje własny impuls, więc niezprzecięta zworka może dawać konflikt.

**Uwaga o krzyżowaniu UART:** TX jednej strony idzie do RX drugiej. Nazwy `MODEM_TX_PIN` / `MODEM_RX_PIN` w `Config.h` są **z perspektywy ESP32** — `MODEM_TX_PIN` to pin, którym ESP32 *nadaje* do modemu. Przy przepinaniu łatwo o tym zapomnieć i to jest klasyczna przyczyna ciszy na magistrali; objaw z [`02_modem §6.2`](./02_modem_a7670e_communication.md) („UART garbage" albo brak odpowiedzi na AT) wygląda wtedy identycznie jak awaria sprzętowa.

### 5.5 Dioda statusu

**Ustalenie, które rozstrzyga sprawę: sygnalizacja kolorami nie istnieje w kodzie.**

[`StatusLed::blink()`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L36-L54) w gałęzi WS2812 ustawia **wyłącznie** `Color(0, 255, 0)` — zielony — zarówno dla sukcesu, jak i błędu. Stany rozróżnia **liczba i długość mignięć**:

| Metoda | Wywołanie | Sygnał |
|---|---|---|
| `blinkSuccess()` | `blink(1, 80)` | 1 mignięcie, 80 ms |
| `blinkError()` | `blink(3, 120)` | 3 mignięcia, 120 ms |

Potwierdza to sama dokumentacja sprzętowa: [`01_hardware.md §4`](./01_hardware.md) — *„Success: pojedynczy blink zielony / **Error: trzy blinki zielone**"*.

**Zwykła dioda jednokolorowa nie traci więc nic, co dziś istnieje.** Cały przekaz przenosi się jeden do jednego.

**Ale wybór płytki ma znaczenie i łatwo go przeoczyć:**

| Wariant arduino-esp32 | Płytka | `LED_BUILTIN` |
|---|---|---|
| `esp32` (board `esp32dev` — „ESP32 Dev Module", oficjalny DevKitC) | oficjalna Espressif | **brak — wariant nie definiuje `LED_BUILTIN` w ogóle** |
| `doitESP32devkitV1` (board `esp32doit-devkit-v1`) | DOIT, 30-pin | **GPIO 2**, zwykła dioda niebieska |
| `esp32s3` (dziś) | DevKitC-1 | RGB WS2812 przez `PIN_RGB_LED` |

Na **oficjalnym** ESP32-DevKitC nie ma żadnej diody użytkownika — trzeba dołożyć LED z rezystorem albo zewnętrzny WS2812. Na DOIT DevKit V1 dioda na GPIO 2 jest i wystarcza.

**Rekomendacja: płytka klasy DOIT DevKit V1, zwykła dioda na GPIO 2.** Zewnętrzny WS2812 to doposażenie za kilka złotych i jeden przewód — sensowne dopiero wtedy, gdy sygnalizacja kolorami zostanie faktycznie zaimplementowana.

---

## 6. Zmiany w kodzie

Trzy pliki. Fragmenty są gotowe do wklejenia.

### 6.1 `Config.h` — mapa pinów pod dwie płytki

```cpp
// =========================
// Pin map — per board
// =========================

#if defined(BOARD_ESP32_WROOM)
// Klasyczny ESP32 (ESP-WROOM-32). Ograniczenia i uzasadnienie doboru:
// docs/technical/firmware/08_analiza_portu_esp32_wroom.md §5
const int LED_PIN = 2;   // LED_BUILTIN na DOIT DevKit V1; strappingowy — tylko LED z rezystorem do GND

const int MODEM_RX_PIN    = 26;
const int MODEM_TX_PIN    = 25;
const int MODEM_PWRKEY_PIN = 27;
const int MODEM_RESET_PIN = 33;  // NIE GPIO 5: strappingowy z pull-upem, a RESET jest active-HIGH (§5.3 A)

const int PT100_SPI_CS   = 22;   // CS programowy; VSPI CS0 (GPIO 5) odpada — strappingowy
const int PT100_SPI_MOSI = 23;   // IO_MUX VSPI MOSI
const int PT100_SPI_MISO = 19;   // IO_MUX VSPI MISO
const int PT100_SPI_SCK  = 18;   // IO_MUX VSPI CLK; NIE GPIO 12 = MTDI, wybór napięcia flash (§5.3 B)

#elif defined(BOARD_ESP32_S3)
// ESP32-S3-DevKitC-1 — mapa dotychczasowa, bez zmian
const int LED_PIN = 48;

const int MODEM_RX_PIN    = 18;
const int MODEM_TX_PIN    = 17;
const int MODEM_PWRKEY_PIN = 4;
const int MODEM_RESET_PIN = 5;

const int PT100_SPI_CS   = 14;
const int PT100_SPI_MOSI = 11;
const int PT100_SPI_MISO = 13;
const int PT100_SPI_SCK  = 12;

#else
#error "Nie wybrano plytki: zdefiniuj BOARD_ESP32_S3 albo BOARD_ESP32_WROOM w build_flags"
#endif

const int MODEM_POWER_ENABLE_PIN = -1;  // wspólne: moduł A7670E nie ma osobnej linii enable
```

Reszta `Config.h` (APN, adresy backendu, timingi) jest niezależna od płytki i zostaje bez zmian.

**Dlaczego `#error`, a nie `#else` z mapą S3 jako domyślną:** przy `#else` build bez żadnej flagi (np. z IDE, ze skryptu, z pomyłkowo skopiowanego środowiska) **po cichu wgrałby piny S3 na płytkę WROOM-32**. Objawem byłaby martwa magistrala SPI i modem nieodpowiadający na AT — czyli dokładnie ten obraz, który w [§10](#10-kolejność-uruchomienia) każe szukać błędu w okablowaniu. `#error` zamienia godzinę diagnozowania sprzętu w komunikat kompilatora. W dokumencie o tym, jak kosztowne są pomyłki w mapie pinów, domyślna cicha gałąź byłaby niekonsekwencją.

### 6.2 `StatusLed` — jawny typ diody zamiast magicznej „48"

Dziś klasa rozpoznaje typ diody przez **porównanie numeru pinu z literałem `48`** — dwa razy, w [konstruktorze (linia 8)](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L8) i w [`blink()` (linia 38)](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L38). Numer pinu pełni rolę ukrytego przełącznika typu sprzętu, więc na WROOM-32 klasa po cichu wybrałaby złą gałąź. Zamiast dodawać drugi magiczny numer — jawny typ:

```cpp
// StatusLed.h
#pragma once

class Adafruit_NeoPixel;

class StatusLed {
 public:
  enum class Type { Simple, NeoPixel };

  StatusLed(int pin, Type type);   // tylko zapamiętuje pola — zero I/O
  ~StatusLed();

  void begin();                    // całe I/O tutaj; wołane z setup() dla obu typów
  void blinkSuccess();
  void blinkError();
  void blink(int count, int delayMs);

 private:
  int pin_;
  Type type_;
  Adafruit_NeoPixel* pixels_ = nullptr;
  bool begun_ = false;
};
```

Gałęzie w `.cpp` zmieniają warunek z `pin_ == 48` na `type_ == Type::NeoPixel`. Konstrukcja w [`main.cpp:35`](../../../firmware/src/main.cpp#L35):

```cpp
#if defined(BOARD_ESP32_WROOM)
StatusLed led(LED_PIN, StatusLed::Type::Simple);
#else
StatusLed led(LED_PIN, StatusLed::Type::NeoPixel);
#endif
```

`led.initializePixels()` w [`main.cpp:164`](../../../firmware/src/main.cpp#L164) zmienia się na `led.begin()`. To jedyne wywołanie w repozytorium, więc zmiana nazwy jest bezpieczna.

**Dlaczego `begin()` zamiast zostawienia `initializePixels()`:** dziś konstruktor dla diody innej niż WS2812 woła `pinMode()` i `digitalWrite()` **w konstruktorze**, czyli przy inicjalizacji statycznej — zanim wystartuje `setup()` ([`StatusLed.cpp:12-13`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L12-L13)). Na S3 ta gałąź jest martwa (`pin_ == 48` zawsze prawdziwe), więc problem nie występuje — **ale na WROOM-32 to jest właśnie gałąź, która się wykona**. Autor kodu był tego świadomy przy NeoPixelu: komentarz *„Defer `pixels_->begin()` to `setup()` to avoid blocking at global scope before watchdog resets"* mówi dokładnie o tym ryzyku. Byłoby niekonsekwencją odziedziczyć je w wariancie prostym. `begin()` przenosi całe I/O do `setup()`, symetrycznie dla obu typów.

**To jest zmiana warta zrobienia niezależnie od portu:** usuwa numer pinu w roli przełącznika typu sprzętu, zdejmuje I/O z inicjalizacji statycznej i czyni klasę testowalną w środowisku `native`.

**Opcjonalnie, jeśli flash okaże się ciasny** ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)): `Adafruit_NeoPixel` jest bezwarunkowo dołączany przez [`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L2) i w wariancie ze zwykłą diodą byłby martwym kodem. Schowanie go za `#if !defined(BOARD_ESP32_WROOM)` odzyskuje kilka kilobajtów.

### 6.3 `platformio.ini` — drugie środowisko obok istniejącego

```ini
[env]                      ; wspólna baza — dziś wszystko jest wklejone w [env:esp32-s3]
platform = espressif32
framework = arduino
monitor_speed = 115200
extra_scripts = scripts/prebuild.py
lib_extra_dirs = ${PROJECT_DIR}/lib
lib_deps =
    https://github.com/lewisxhe/TinyGSM-fork.git
    arduino-libraries/ArduinoHttpClient @ ^0.6.1
    bblanchon/ArduinoJson @ ^7.0.4
    adafruit/Adafruit NeoPixel @ ^1.12.0
    adafruit/Adafruit BusIO @ ^1.14.1
    adafruit/Adafruit MAX31865 library @ ^1.3.0
build_flags =
    -D TINY_GSM_MODEM_A76XXSSL
    -D TINY_GSM_RX_BUFFER=1024
    -D LOG_LEVEL=LOG_INFO
    -Iinclude

[env:esp32-s3]
board = esp32-s3-devkitc-1
build_flags = ${env.build_flags} -D BOARD_ESP32_S3

[env:esp32-wroom]
board = esp32doit-devkit-v1              ; wariant z LED_BUILTIN = GPIO 2 (§5.5)
board_build.partitions = min_spiffs.csv  ; dopiero jeśli obraz nie mieści się w 1,25 MiB (§7)
build_flags = ${env.build_flags} -D BOARD_ESP32_WROOM
```

**Ten fragment jest zweryfikowany narzędziowo,** nie tylko napisany: przepuściłem go przez `pio project config` i potwierdziłem, że interpolacja `${env.build_flags}` rozwija się poprawnie, obie flagi `BOARD_*` trafiają do właściwych środowisk, a `board_build.partitions` jest przenoszone. Przy okazji wyszło, że `extends = env` jest **zbędne** — sekcja `[env]` jest dziedziczona globalnie i wynik `pio project config` jest identyczny z nią i bez niej. Dlatego jej tu nie ma.

**Dwie uwagi, żeby nie zdziwiło:**

1. **Nie przenoś `CONFIG_ESP_TASK_WDT_TIMEOUT_S` ani `CONFIG_BOOTLOADER_WDT_DISABLE` do `[env]` w przekonaniu, że coś naprawiasz.** Te `-D` nie sięgają prekompilowanych bibliotek ESP-IDF frameworku Arduino ([§3](#3-korekty-do-założeń-briefu)) — nie działają dziś na S3 i nie zadziałają na WROOM. Jeśli mają zacząć obowiązywać, potrzebny jest własny `sdkconfig` albo framework `espidf`, i to jest **decyzja niezależna od portu**. Świadomie pominąłem je we fragmencie wyżej.
2. **`test_ignore_pattern` w `[env:native]`** (linia 28) jest nieznaną opcją — PlatformIO wypisuje na nią ostrzeżenie (`Warning! Ignore unknown configuration option 'test_ignore_pattern'`, zaobserwowane bezpośrednio). Do posprzątania przy okazji, bez związku z portem.

**Dobra wiadomość:** pięć plików testowych w `firmware/test/` działa w środowisku `native` i nie zależy od chipu — pokrycie testowe przenosi się za darmo.

### 6.4 Zostawiać `env:esp32-s3`, czy przechodzić na WROOM na stałe?

Brief wymagał drugiego środowiska **obok** istniejącego i to jest też dobra rada praktyczna, ale z innego powodu niż formalny: **działający S3 jest Twoim jedynym punktem odniesienia w trakcie bring-upu.** Kiedy modem przestanie odpowiadać, jedyne sensowne pytanie brzmi „czy to samo dzieje się na S3?" — a bez działającego drugiego środowiska nie da się go zadać.

Decyzję o ewentualnym porzuceniu wariantu S3 podejmij **po** zamknięciu [§10](#10-kolejność-uruchomienia), nie przed. Warto natomiast wiedzieć, że utrzymywanie obu wariantów na dłuższą metę **nie jest darmowe**: każda zmiana dotykająca pinów lub peryferiów wymaga weryfikacji na dwóch płytkach, a przy dodawaniu czujnika kroki 5–6 z [`06_adding_sensors.md`](./06_adding_sensors.md) (flash → odczyt logów → potwierdzenie w backendzie) wykonują się dwa razy. Dochodzi do tego wybór pinu spełniającego jednocześnie ograniczenia obu chipów — czyli **projekt na S3 zaczyna tracić swobodę, której S3 sam nie traci**. W repozytorium nie ma `.github/workflows/`, więc nic tego nie pilnuje automatycznie.

---

## 7. Flash i partycje — jedyna otwarta kwestia wykonalności

Różnica nie leży w rozmiarze kości, tylko w **domyślnej tablicy partycji**, którą narzuca manifest płytki:

| | ESP32-S3-DevKitC-1 | ESP32 Dev Module / DevKit V1 |
|---|---|---|
| Flash | 8 MB | 4 MB |
| Tablica partycji | `default_8MB.csv` (jawnie w manifeście) | `default.csv` (brak wpisu → domyślna) |
| **Partycja aplikacji `app0`** | `0x330000` = **3 342 336 B ≈ 3,19 MiB** | `0x140000` = **1 310 720 B = 1,25 MiB** |
| Partycja NVS | `0x5000` = 20 KiB | `0x5000` = 20 KiB — **identyczna** |

**Miejsce na aplikację kurczy się 2,55×.** NVS zostaje bez zmian, więc numer seryjny, klucz i token przeżywają zmianę partycji bez migracji.

### Sprawdź to jednym poleceniem

```bash
cd firmware
pio run -e esp32-s3        # odczytaj wiersz: Flash: [==   ] xx.x% (used NNNNNN bytes from ...)
```

### Jak odczytać wynik

| Rozmiar obrazu | Co zrobić |
|---|---|
| **< 1 310 720 B** (1,25 MiB) | nic — domyślna `default.csv` wystarczy, usuń `board_build.partitions` z [§6.3](#63-platformioini--drugie-środowisko-obok-istniejącego) |
| **1 310 720 – 1 966 080 B** | zostaw `board_build.partitions = min_spiffs.csv` → **1,875 MiB, OTA zachowane**. Projekt nie używa SPIFFS (tylko `Preferences`/NVS), więc zejście SPIFFS do 128 KiB **nic nie kosztuje** |
| **> 1 966 080 B** (1,875 MiB) | trzy wyjścia: `no_ota.csv` (2 MiB, **ale OTA znika**), moduł ESP32-WROOM-32**E** z 8 MB flasha, albo odchudzenie obrazu (zacznij od `#ifdef` na `Adafruit_NeoPixel`, [§6.2](#62-statusled--jawny-typ-diody-zamiast-magicznej-48)) |

Wartości partycji pochodzą z `tools/partitions/*.csv` arduino-esp32 i są dokładne, nie szacowane:

| Tablica | `app0` | OTA |
|---|---|---|
| `default.csv` | `0x140000` = 1,25 MiB | dwa sloty |
| `min_spiffs.csv` | `0x1E0000` = 1,875 MiB | dwa sloty |
| `no_ota.csv` | `0x200000` = 2 MiB | **jeden slot** |
| `default_8MB.csv` | `0x330000` = 3,19 MiB | dwa sloty |

**Ocena prawdopodobieństwa:** obraz obejmuje rdzeń Arduino, mbedTLS, TinyGSM, ArduinoJson, NVS i sterowniki czujników — **ale nie stos TLS na mikrokontrolerze**, bo `-D TINY_GSM_MODEM_A76XXSSL` ([`platformio.ini:17`](../../../firmware/platformio.ini#L17)) oznacza, że **TLS terminuje modem A7670E**. To zdejmuje z obrazu największą pojedynczą pozycję, jakiej można by się tu spodziewać. Zmieszczenie się w 1,875 MiB jest bardzo prawdopodobne; w 1,25 MiB — możliwe, ale mniej pewne. **Sprawdź, zamiast zgadywać.**

---

## 8. Co przenosi się bez żadnej pracy

Ta sekcja istnieje po to, żeby nie budżetować czasu tam, gdzie go nie trzeba.

### 8.1 Kryptografia — brak akceleratora ECC na obu chipach

Brief wskazał ten punkt jako krytyczny. Odpowiedź idzie w przeciwną stronę niż hipoteza.

W ESP-IDF v5.3 akceleracja ECC w mbedTLS jest warunkowana wprost:

```kconfig
config MBEDTLS_HARDWARE_ECC
    bool "Enable hardware ECC acceleration"
    default y
    depends on SOC_ECC_SUPPORTED
```

**`SOC_ECC_SUPPORTED` nie jest zdefiniowane ani w `components/soc/esp32/include/soc/soc_caps.h`, ani w `components/soc/esp32s3/include/soc/soc_caps.h`.** (Akcelerator ECC mają rodziny RISC-V: C3, H2, C6 — nie Xtensa.)

Czyli `mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1, ...)` ([`DeviceIdentity.cpp:198`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L198)) i `mbedtls_ecdsa_write_signature()` ([`DeviceIdentity.cpp:102`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L102)) **już dziś, na S3, wykonują się w całości programowo**. Port niczego nie odbiera.

| Możliwość | esp32 | esp32s3 | Znaczenie |
|---|---|---|---|
| `SOC_ECC_SUPPORTED` | **brak** | **brak** | ECC programowo na obu — bez różnicy |
| `SOC_MPI_SUPPORTED` (bignum) | ✅ | ✅ | `MBEDTLS_HARDWARE_MPI` `default y` na obu — bez różnicy |
| `SOC_SHA_SUPPORTED` | ✅ | ✅ | `mbedtls_sha256()` sprzętowo na obu |
| `SOC_AES_SUPPORTED` | ✅ | ✅ | bez różnicy |
| `MBEDTLS_MPI_USE_INTERRUPT` | **wyłączone** (`depends on !IDF_TARGET_ESP32`) | ✅ | jedyna realna różnica: CPU czeka w pętli zamiast oddać rdzeń. Dla ECC (wiele krótkich mnożeń, brak długich `exp_mod`) wpływ pomijalny |
| Rdzeń / zegar | 2× Xtensa LX6 @ 240 MHz | 2× Xtensa LX7 @ 240 MHz | ten sam zegar; LX7 nieznacznie wydajniejszy na cykl |

**Budżet czasowy.** Punkt odniesienia z repo: generowanie klucza *„trwa ~2-3s"* na S3 ([`04_device_provisioning_flow.md §2.2`](./04_device_provisioning_flow.md)). Na WROOM-32 przy identycznej ścieżce programowej i tym samym zegarze spodziewam się **~2,5–4 s** (*oszacowanie — procedura pomiaru w [§11](#11-co-zweryfikować)*).

I to się mieści, ale nie dzięki marginesowi — **dzięki architekturze**: generowanie klucza jest celowo odłożone z `setup()` do pierwszej iteracji `loop()` przez flagę `keyGenerated` ([`main.cpp:199-202`](../../../firmware/src/main.cpp#L199-L202)), czyli **poza okno RTC WDT bootloadera**. Dodatkowo `loadOrGenerateKey()` woła `esp_task_wdt_reset()` i `yield()` przed i po `mbedtls_ecp_gen_key` ([`DeviceIdentity.cpp:191-200`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L191-L200)). Zabezpieczenie przenosi się na WROOM-32 bez zmian i nawet dwukrotnie gorszy wynik niczego nie łamie.

> **Uwaga poboczna, nie dotyczy portu:** [`03_esp32_reset_and_recovery.md §4`](./03_esp32_reset_and_recovery.md) opisuje włączanie Task WDT przez `esp_task_wdt_init()` + `esp_task_wdt_add(NULL)`, a kod tego nie robi — więc **Task WDT prawdopodobnie nie chroni dziś `loop()` na żadnym chipie**. Na wynik portu nie wpływa; zebrane do zgłoszenia w [§14](#14-ustalenia-poboczne--do-osobnego-zgłoszenia).

### 8.2 RAM — limit identyczny

| | ESP32-S3-DevKitC-1 | ESP32 Dev Module |
|---|---|---|
| `maximum_ram_size` w manifeście płytki | **327 680 B** (320 KiB) | **327 680 B** (320 KiB) |
| PSRAM | wariant **N8 — „No PSRAM"**; `platformio.ini` nie ustawia `-DBOARD_HAS_PSRAM` | brak w podstawowych WROOM-32 |

**Limit jest liczbowo identyczny, a PSRAM nie jest dziś używany** — port nie odbiera ani bajta. To rozstrzyga obawę briefu o „brak PSRAM w podstawowych wariantach": jest bez znaczenia, bo obecny build i tak z PSRAM nie korzysta.

Bufory, policzone ze stałych w kodzie:

| Bufor | Wyliczenie | Szacunek |
|---|---|---|
| `windows_buffer_` | `RETAIN_WINDOWS_MAX = 4 × 12 = 48` okien ([`TelemetryPayload.h:34-35`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L34-L35)); `MeasurementWindow` ≈ 24 B + blok sterty na czujnik ≈ 16 B + narzut alokatora | **~2,5 KB** |
| `errors_buffer_` | `MAX_ERRORS = 64` ([`TelemetryPayload.h:36`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L36)) × `ErrorItem` (4 wskaźniki = 16 B) | **~1 KB** |
| `TINY_GSM_RX_BUFFER` | [`platformio.ini:18`](../../../firmware/platformio.ini#L18) | **1 KB** |
| `JsonDocument` przy `build()` | ArduinoJson 7, sterta elastyczna; 4 okna × 1 punkt | **~1–2 KB** chwilowo |

**Rzędu 5–7 KB przy 320 KB dostępnych.** Bufor 12 minut historii z briefu jest o dwa rzędy wielkości mniejszy niż limit. Gdyby HTTPS szło przez mbedTLS na ESP32 zamiast przez modem, doszłoby kilkadziesiąt kilobajtów sterty na sesję TLS i ta rozmowa wyglądałaby inaczej — także dziś, na S3.

### 8.3 `RTC_DATA_ATTR` — kompatybilne

Obie karty możliwości deklarują `SOC_RTC_FAST_MEM_SUPPORTED 1` i `SOC_RTC_SLOW_MEM_SUPPORTED 1`. Na klasycznym ESP32 obszar `RTC_DATA` to `0x50000000`–`0x50002000`, czyli **8 KiB**.

Użycie to trzy zmienne — `rtcRestartCounter`, `rtcSyncedTimeUtcSec`, `rtcSyncMillis` ([`main.cpp:27-29`](../../../firmware/src/main.cpp#L27-L29), deklaracje w [`RtcState.h`](../../../firmware/include/RtcState.h)) — **12 bajtów przy 8 192 dostępnych**. Semantyka przetrwania `esp_restart()`, na której stoi licznik restartów w [`Watchdog::attemptRecovery()`](../../../firmware/lib/Watchdog/src/Watchdog.cpp#L38-L42) i utrzymanie czasu w [`TimeSync`](../../../firmware/lib/TimeSync/src/TimeSync.cpp), jest na obu chipach taka sama. **Zero pracy.**

### 8.4 USB/Serial — już dziś UART0

`Serial` w bieżącym buildzie to `Serial0`, czyli **UART0**, bo `ARDUINO_USB_CDC_ON_BOOT` domyślnie wynosi `0` i `platformio.ini` go nie nadpisuje ([§3](#3-korekty-do-założeń-briefu)). Logi z [`Logger.h`](../../../firmware/lib/Logger/include/Logger.h) i flashowanie idą przez mostek USB-UART na płytce — **dokładnie tak samo jak przez CP2102/CH340 na płytce z klasycznym ESP32**. Firmware nigdy nie korzystał z natywnego USB CDC układu S3. **Zero pracy.**

> **Uwaga poboczna:** `EnrollmentClient::readSerial()` jest **pustą metodą** z komentarzem *„Serial input disabled - migrated away from direct Serial usage"* ([`EnrollmentClient.cpp:95-97`](../../../firmware/lib/EnrollmentClient/src/EnrollmentClient.cpp)). Ścieżka `ACTIVATE <kod>` z [`04_device_provisioning_flow.md §3.2`](./04_device_provisioning_flow.md) **nie ma dziś czym odbierać kodu** — `processLine()` istnieje, ale nikt go nie woła. To jest złamane tak samo na obu chipach, ale **uderzy Cię w kroku 6 z [§10](#10-kolejność-uruchomienia)** — to jedyne ustalenie poboczne, które realnie blokuje pracę, więc napraw je **przed** startem portu. Zebrane w [§14](#14-ustalenia-poboczne--do-osobnego-zgłoszenia).

### 8.5 API i biblioteki bez zmian

`Preferences`/NVS, `esp_read_mac()`, `esp_restart()`, `esp_task_wdt_reset()`, `HardwareSerial SerialAT(1)` (`SOC_UART_NUM = 3` na klasycznym ESP32, więc UART1 istnieje), `SPI.begin(sck, miso, mosi, cs)` z jawnymi pinami ([`PT100Sensor.cpp:14`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L14)), `Adafruit_MAX31865`, `Adafruit_NeoPixel`, TinyGSM, ArduinoJson, `ArduinoHttpClient`. **Identyczne API na obu chipach.**

Peryferia S3, których projekt w ogóle nie używa: USB OTG, USB-Serial-JTAG, wektory SIMD/DSP, `SOC_SPIRAM_XIP_SUPPORTED`, dotyk v2. **Zero trafień w kodzie.**

---

## 9. Co realnie tracisz

Po odjęciu wszystkiego, co się przenosi, zostają trzy rzeczy.

**1. Peryferium HMAC + Digital Signature — jedyna strata nieodwracalna.**

| Peryferium | esp32 | esp32s3 | Do czego |
|---|---|---|---|
| `SOC_HMAC_SUPPORTED` | **brak** | ✅ | klucz w eFuse, niedostępny dla oprogramowania |
| `SOC_DIG_SIGN_SUPPORTED` | **brak** | ✅ | podpisywanie kluczem, którego firmware nie może odczytać |
| `SOC_FLASH_ENC_SUPPORTED` | ✅ | ✅ | szyfrowanie flasha — **na obu** |
| `SOC_SECURE_BOOT_SUPPORTED` | ✅ | ✅ | secure boot — **na obu** |

Dziś klucz prywatny leży w NVS **jawnym tekstem** ([`DeviceIdentity.cpp:205`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L205)), więc projekt z peryferium DS i tak nie korzysta. Ale to jest naturalna ścieżka utwardzenia tożsamości urządzenia, a szyfrowanie flasha (dostępne na obu) chroni klucz tylko przed odczytem kości — **nie przed odczytem przez własne oprogramowanie**.

Waga zależy od [B-01](../../plan/01_briefy_dla_agentow.md): jeśli gmina jako podmiot objęty NIS2/KSC postawi wymagania kontraktowe co do ochrony tożsamości urządzenia, S3 ma na to odpowiedź sprzętową, a klasyczny ESP32 nie ma i mieć nie będzie. **Na etapie prototypu to nie blokuje niczego — ale to jedyna pozycja, której nie da się później odkręcić bez zmiany chipu.**

**2. Zapas miejsca na aplikację.** 3,19 MiB → 1,25 MiB, odzyskiwalne do 1,875 MiB ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)). Dziś prawdopodobnie bez znaczenia, ale sufit jest realnie niżej i przy rozbudowie firmware'u kiedyś się o niego uderzysz.

**3. Swoboda doboru pinów.** Znika 6 pinów (flash), 6 staje się tylko-wejściowych, dochodzą 4 strappingowe. Po nowej mapie zostaje jednak **dziesięć wolnych pinów** ([§5.2](#52-proponowana-mapa)) — realnie nie odczujesz tego przy tej liczbie czujników.

**Czego NIE tracisz** (bo to najczęstsze nieporozumienie): sygnalizacji LED ([§5.5](#55-dioda-statusu)), wydajności krypto ([§8.1](#81-kryptografia--brak-akceleratora-ecc-na-obu-chipach)), RAM ([§8.2](#82-ram--limit-identyczny)), `RTC_DATA_ATTR` ([§8.3](#83-rtc_data_attr--kompatybilne)), logów i flashowania ([§8.4](#84-usbserial--już-dziś-uart0)), testów jednostkowych.

---

## 10. Kolejność uruchomienia

Sens kolejności: **każdy krok dokłada jedną nową rzecz, która może się zepsuć.** Przy ośmiu przepiętych sygnałach i dwóch pułapkach strappingowych uruchamianie wszystkiego naraz oznacza zgadywanie, który z ośmiu kabli jest winny.

| # | Krok | Kryterium przejścia dalej |
|---|---|---|
| 1 | Zmiany w kodzie ([§6](#6-zmiany-w-kodzie)), build **obu** środowisk bez podłączonego sprzętu | `pio run -e esp32-s3` i `pio run -e esp32-wroom` przechodzą; odczytaj rozmiar obrazu i rozstrzygnij partycję ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności)) |
| 2 | Sama płytka WROOM-32, **nic nie podłączone**, flash i boot | Płytka wstaje, logi lecą przez UART0, dioda na GPIO 2 miga. **To weryfikuje pułapkę B i GPIO 2** — jeśli płytka nie bootuje na tym etapie, przyczyna jest w mapie pinów, nie w peryferiach |
| 3 | Podłącz **tylko** MAX31865 (18/19/22/23), bez modemu | `[PT100] Initialized` w logu i sensowna temperatura. **Weryfikuje blok SPI w izolacji** |
| 4 | Podłącz **tylko** modem (33/25/26/27), odłącz MAX31865 | `[MODEM] Init OK` i `[MODEM] Info: ...`. **To jest moment prawdy dla pułapki A** — jeśli zobaczysz timeout ~10 s, porównaj z [`02_modem §7.3`](./02_modem_a7670e_communication.md) i sprawdź stan GPIO 33 przy starcie |
| 5 | Modem + sieć | `[NET] Network connected`, `[DATA] GPRS/LTE connected`, sensowny `Local IP` |
| 6 | Pełny provisioning — `ACTIVATE <kod>` → redeem → challenge/verify | Token zapisany, przejście do telemetrii. **Uwaga: `readSerial()` jest puste** ([§8.4](#84-usbserial--już-dziś-uart0)) — bez naprawy tej metody nie da się wprowadzić kodu przez serial |
| 7 | Wszystko razem: telemetria end-to-end | Dane widoczne w backendzie; cały cykl ~55 s wg [`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md) |
| 8 | Recovery watchdoga — trzy poziomy | Zgodnie z [`03_esp32_reset_and_recovery.md §3`](./03_esp32_reset_and_recovery.md): AT test → `hardReset()` modemu → `esp_restart()` z licznikiem w RTC |

**Zanim zaczniesz krok 6, przeczytaj to:** numer seryjny powstaje z adresu MAC Wi-Fi ([`DeviceIdentity.cpp:217`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L217)), a klucz prywatny i flaga `claimed` żyją w NVS konkretnego modułu. **Płytka WROOM-32 to dla backendu nowe urządzenie** — inny SN, nowa para kluczy, **potrzebny osobny kod aktywacyjny**. To samo dotyczy każdego `pio run -t erase`: kasuje tożsamość i zużywa kolejny kod. Przy prototypowaniu, gdzie flashuje się dziesiątki razy, warto **przygotować sobie zapas kodów aktywacyjnych z góry**, zamiast odkryć ten problem w środku sesji debugowania.

**Drobiazg zasilania, ale realny:** dokumentacja KAmod ostrzega o **5 V / min. 2 A** przy szczytach transmisji LTE ([`01_hardware.md §7`](./01_hardware.md)) i modem ma osobne zasilanie — ale tani DevKit V1 ma słabszy stabilizator 3V3 niż DevKitC-1. Jeśli zobaczysz losowe restarty **skorelowane z transmisją**, sprawdź napięcie 3V3 pod obciążeniem, zanim zaczniesz szukać błędu w kodzie. Wspólna masa z modemem jest obowiązkowa.

---

## 11. Co zweryfikować

Trzy pozycje. Pierwsza jest jedyną, która realnie zmienia plan.

*Ta sekcja mówi **co** sprawdzić i jak odczytać wynik. Jeśli zlecasz to komuś innemu — człowiekowi albo agentowi — [§13](#13-instrukcja-dla-kolejnego-agenta--czego-nie-dało-się-tu-zrobić) zawiera to samo w formie zadań, razem z powodem, dla którego nie dało się tego zrobić przy pisaniu tego dokumentu, i z instrukcją, gdzie wpisać wyniki.*

### 11.1 Rozmiar obrazu binarnego — **przed rozpoczęciem**

```bash
cd firmware
pio run -e esp32-s3        # wiersz "Flash: [==   ] xx.x% (used NNNNNN bytes ...)"
```

Interpretacja i progi decyzyjne: [§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności). **Nie udało mi się tego sprawdzić** — rejestr PlatformIO jest zablokowany w środowisku, w którym pracowałem ([§2.2](#22-czego-nie-dało-się-zrobić)).

### 11.2 Układ listwy Twojej płytki — przed lutowaniem

Mapa z [§5.2](#52-proponowana-mapa) jest poprawna **elektrycznie**. Uwagi o sąsiedztwie pinów zakładają typowy 30-pinowy DevKit V1 — **sprawdź silkscreen**, bo warianty 30- i 36-pinowe różnią się układem, a błąd tu kosztuje przelutowanie, nie tylko czas.

### 11.3 Czasy operacji kryptograficznych — opcjonalnie

Pomiar dla kompletności, nie dla decyzji — operacja wykonuje się poza oknem RTC WDT ([§8.1](#81-kryptografia--brak-akceleratora-ecc-na-obu-chipach)), więc nawet dwukrotnie gorszy wynik niczego nie łamie.

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

Punkt odniesienia: **~2–3 s** dla generowania klucza na S3. Oczekiwane na WROOM-32: **~2,5–4 s**. `ensureKey()` działa raz w życiu urządzenia — powtórzenie pomiaru wymaga `pio run -t erase`, co **kasuje tożsamość i zużywa kod aktywacyjny** ([§10](#10-kolejność-uruchomienia)).

---

## 12. Uwaga kontekstowa: płytki przemysłowe DIN

Poza zakresem tej analizy, ale warto mieć w tyle głowy przy [B-01](../../plan/01_briefy_dla_agentow.md), wariant W3: rynek przemysłowych sterowników DIN jest **podzielony między oba chipy**. NORVI IIOT (serie AE01/AE02/AE03) i Industrial Shields ESP32 PLC stoją na klasycznym ESP32-WROOM-32; KinCony, EQSP32/EQSP32CE, LILYGO T-Connect Pro i szereg płytek RS485 w obudowach DIN — na ESP32-S3.

Praktyczny wniosek: **wybór chipu nie jest wymuszony przez ścieżkę przemysłową w żadną stronę.** Ten port nie zamyka drogi do wersji przemysłowej ani jej nie otwiera — po prostu poszerza pulę płytek, wśród których będziesz wybierał. *(Zestawienie z przeglądu ofert producentów — **do potwierdzenia** kartami katalogowymi i dostępnością w PL/UE, co i tak należy do zakresu B-01.)*

---

## 13. Instrukcja dla kolejnego agenta — czego nie dało się tu zrobić

Ta sekcja istnieje, bo trzy rzeczy w tej analizie są **oszacowaniami zamiast pomiarów**, a wszystkie trzy da się domknąć w środowisku bez blokad sieciowych. Poniżej dokładnie co uruchomić, gdzie i co wpisać z powrotem do tego dokumentu. Kolejność jest wg wartości: **zadanie 1 jest jedynym, które może zmienić plan pracy** — reszta poprawia precyzję.

### Zadanie 1 — zmierzyć rozmiar obrazu i rozstrzygnąć partycję ⚠️ **priorytet**

**Dlaczego ja tego nie zrobiłem:** rejestr PlatformIO jest zablokowany przez proxy sieciowe środowiska, w którym pracowałem. `api.registry.platformio.org` i `dl.registry.platformio.org` nie odpowiadają w ogóle (`curl` → kod 000), przy dostępnym GitHubie. Samą platformę zainstalowałem obejściem z gita (`pio pkg install -p "https://github.com/platformio/platform-espressif32.git"` → `espressif32@7.1.0+sha.b753f4d`), ale toolchain `espressif/toolchain-xtensa-esp32s3` nadal rozwiązuje się przez rejestr i kończy `HTTPClientError`. **Nie próbuj powtarzać tego obejścia — ono nie wystarcza.** Potrzebne jest środowisko z dostępem do rejestru PlatformIO.

**Co uruchomić:**

```bash
cd firmware
pio run -e esp32-s3
```

**Czego szukać w wyjściu:** wiersza `RAM:   [= ] x.x% (used NNNNN bytes from 327680 bytes)` oraz `Flash: [== ] x.x% (used NNNNNN bytes from ...)`. **Istotna jest liczba bajtów `Flash`, nie procent** — procent odnosi się do partycji 3,19 MiB środowiska S3, a pytanie dotyczy tego, czy zmieści się w 1,25 MiB środowiska WROOM.

**Co z tym zrobić — progi są w [§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności), skrótowo:**

| Wynik | Wniosek | Akcja w dokumencie |
|---|---|---|
| < 1 310 720 B | mieści się w domyślnej `default.csv` | usuń `board_build.partitions` ze snippetu w [§6.3](#63-platformioini--drugie-środowisko-obok-istniejącego); w [§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności) zamień „do sprawdzenia" na zmierzoną wartość |
| 1 310 720 – 1 966 080 B | wymaga `min_spiffs.csv`, OTA zachowane | zostaw snippet jak jest, wpisz zmierzoną wartość |
| > 1 966 080 B | **podnosi koszt portu ponad wycenę z [§4](#4-lista-zmian--skrót)** | to jedyny wynik zmieniający plan — rozpisz warianty z [§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności) i oznacz w [§1](#1-odpowiedź), że wykonalność wymaga decyzji o OTA lub module 8 MB |

**Bonus, jeśli toolchain WROOM też się zainstaluje:** po wprowadzeniu zmian z [§6](#6-zmiany-w-kodzie) uruchom `pio run -e esp32-wroom` i porównaj oba rozmiary. Różnica powinna być niewielka (inny wariant `StatusLed`, inny rdzeń), ale to potwierdzi, że drugie środowisko w ogóle się kompiluje — czego również nie mogłem sprawdzić.

### Zadanie 2 — potwierdzić fizyczny układ listwy DevKitu

**Dlaczego ja tego nie zrobiłem:** domeny dystrybutorów i baz pinoutów (`botland.store`, `tme.eu`, `espboards.dev`, `oryx-embedded.com`) są zablokowane przez proxy. Mapa w [§5.2](#52-proponowana-mapa) jest **poprawna elektrycznie** — to wynika ze źródeł Espressif, które udało się przeczytać — ale twierdzenia o **sąsiedztwie pinów na listwie** opierają się na typowym układzie 30-pinowego DevKit V1 i nie zostały zweryfikowane.

**Co zrobić — najprościej bez internetu:** spójrz na silkscreen fizycznej płytki i spisz kolejność obu kolumn. Alternatywnie pobierz schemat DOIT ESP32 DevKit V1 albo wysokorozdzielczy pinout (np. `mischianti.org`, `circuitstate.com`, repozytorium `playelek/pinout-doit-32devkitv1`).

**Co sprawdzić konkretnie:** czy GPIO **33, 25, 26, 27** leżą w jednym ciągu (blok modemu) i czy **18, 19, 22, 23** leżą blisko siebie (blok SPI). Jeśli tak — zamień w [§5.2](#52-proponowana-mapa) ostrożne *„na typowym 30-pinowym DevKit V1… zweryfikuj na silkscreenie"* na twierdzenie wprost. Jeśli nie — **przestaw piny w obrębie tej samej klasy** (dowolny wolny, nie-strappingowy, wyjściowy pin z listy w [§5.2](#52-proponowana-mapa)) tak, żeby bloki wyszły zwarte, i zaktualizuj [tabelę przepięć](#54-tabela-przepięć--co-gdzie-przełożyć).

**Uwaga:** wariant 36-pinowy ma inny układ niż 30-pinowy. Zanotuj, którą płytkę weryfikowałeś.

### Zadanie 3 — potwierdzić rezystory ściągające na KAmodzie

**Dlaczego ja tego nie zrobiłem:** wymaga karty katalogowej albo schematu KAmod, których nie mogłem pobrać (blokada proxy), albo pomiaru na fizycznej płytce.

**Pytanie:** czy moduł KAmod LTE CAT1-GNSS ma własne rezystory ściągające na liniach **RST** (pin 12 złącza 40-pin) i **PWK** (pin 7)? Od tego zależy, czy zalecenie z [§5.3 C](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli) jest konieczne, czy tylko zapasowe.

**Jak sprawdzić:**
1. Schemat lub instrukcja producenta — [karta produktu](https://kamami.pl/moduly-komunikacyjne/1200196-kamod-lte-cat1-gnss-hat-gsmgprsgnss-z-modulem-a7670e-fase-do-raspberry-pi-5902186333727.html), [instrukcja PDF](https://download.kamami.pl/p1200196-KAmod%20LTE%20CAT1-GNSS%20z%20modu%C5%82em%20A7670E-FASE%20%28PL%29-2364.pdf), [wiki KamamiLabs](https://wiki.kamamilabs.com/index.php?title=KAmod_LTE_CAT1-GNSS_z_modu%C5%82em_A7670E-FASE_(PL)).
2. Albo pomiar: **przy odłączonym ESP32** zmierz rezystancję między pinem 12 a GND i między pinem 7 a GND. Wartość rzędu kilku–kilkudziesięciu kΩ = rezystor jest. Rozwarcie = linie pływają i rezystory trzeba dodać.

**Co z tym zrobić:** wpisz wynik do [§5.3 C](#53-trzy-pułapki-elektryczne--przeczytaj-przed-przepięciem-kabli) i odpowiednio osłab albo wzmocnij zalecenie. Jeśli okaże się, że rezystorów nie ma — **zgłoś to jako defekt istniejącego układu na S3**, nie jako element portu, bo dotyczy obu płytek tak samo.

### Zadanie 4 — zmierzyć czasy krypto (opcjonalne)

**Dlaczego ja tego nie zrobiłem:** brak sprzętu i brak buildu.

Procedura, snippet i punkt odniesienia: [§11.3](#113-czasy-operacji-kryptograficznych--opcjonalnie). **To pomiar dla kompletności, nie dla decyzji** — operacja wykonuje się poza oknem RTC WDT, więc nawet dwukrotnie gorszy wynik niczego nie łamie. Rób to dopiero po zamknięciu zadań 1–3.

**Pamiętaj:** `ensureKey()` wykonuje się raz w życiu urządzenia, więc powtórzenie pomiaru wymaga `pio run -t erase`, co kasuje tożsamość urządzenia i **zużywa kolejny kod aktywacyjny** ([§10](#10-kolejność-uruchomienia)).

### Czego NIE trzeba już weryfikować

Żeby kolejny agent nie palił czasu na to, co jest zamknięte — poniższe zostało ustalone z kodu źródłowego Espressif i arduino-esp32, nie z materiałów wtórnych, i nie wymaga powtórki:

- brak `SOC_ECC_SUPPORTED` na obu chipach i wynikający z tego brak akceleracji ECC ([§8.1](#81-kryptografia--brak-akceleratora-ecc-na-obu-chipach));
- identyczny limit RAM 327 680 B w obu manifestach płytek ([§8.2](#82-ram--limit-identyczny));
- `ARDUINO_USB_CDC_ON_BOOT == 0` → `Serial` = UART0 ([§8.4](#84-usbserial--już-dziś-uart0));
- dokładne rozmiary partycji z `tools/partitions/*.csv` ([§7](#7-flash-i-partycje--jedyna-otwarta-kwestia-wykonalności));
- ograniczenia GPIO klasycznego ESP32, piny strappingowe, nieistniejące GPIO 24/28–31 ([§5.1](#51-ograniczenia-klasycznego-esp32--twarde-fakty));
- `LED_BUILTIN` per wariant płytki ([§5.5](#55-dioda-statusu));
- `Adafruit_MAX31865` używa `SPI_MODE1` przy 1 MHz (sprawdzone w źródle biblioteki, uzasadnia analizę GPIO 12);
- snippet `platformio.ini` przepuszczony przez `pio project config` ([§6.3](#63-platformioini--drugie-środowisko-obok-istniejącego)).

---

## 14. Ustalenia poboczne — do osobnego zgłoszenia

Rzeczy znalezione przy okazji tej analizy. **Żadna nie dotyczy portu** — wszystkie występują tak samo na dzisiejszym ESP32-S3 — ale skoro wyszły przy czytaniu całego firmware'u, zapisuję je tutaj zamiast zgubić. Uporządkowane wg tego, jak mocno mogą zaboleć.

| # | Ustalenie | Dowód | Dlaczego to istotne |
|---|---|---|---|
| 1 | **Ścieżka `ACTIVATE <kod>` nie ma czym odbierać kodu.** `EnrollmentClient::readSerial()` jest pustą metodą (*„Serial input disabled - migrated away from direct Serial usage"*); `processLine()` istnieje, ale nikt go nie woła | [`EnrollmentClient.cpp:95-97`](../../../firmware/lib/EnrollmentClient/src/EnrollmentClient.cpp) vs [`04_device_provisioning_flow.md §3.2`](./04_device_provisioning_flow.md) | **Blokuje pierwszy provisioning nowego urządzenia.** Uderzy w kroku 6 z [§10](#10-kolejność-uruchomienia) — i uderzyłoby tak samo na S3 przy każdej nowej płytce |
| 2 | **Task WDT prawdopodobnie nie chroni dziś `loop()` na żadnym chipie.** W całym `firmware/` nie ma `esp_task_wdt_init()` ani `esp_task_wdt_add(NULL)` — jest tylko `esp_task_wdt_reset()`, który bez subskrypcji zadania zwraca `ESP_ERR_NOT_FOUND` i nic nie robi | grep po `firmware/`: 0 trafień, vs [`03_esp32_reset_and_recovery.md §4`](./03_esp32_reset_and_recovery.md) opisujący włączanie WDT | Dokument jest oznaczony jako *„zweryfikowane na 2026-08-22"*, więc opisuje zamiar, a nie stan. Recovery trzypoziomowy w [`Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp) działa niezależnie i **nie jest tym dotknięty** — chodzi wyłącznie o zabezpieczenie przed zawieszeniem `loop()` |
| 3 | **`-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15` i `-D CONFIG_BOOTLOADER_WDT_DISABLE=1` nie działają.** `build_flags` nie sięgają prekompilowanych bibliotek ESP-IDF frameworku Arduino — `sdkconfig` jest zapieczony | [`platformio.ini:19-20`](../../../firmware/platformio.ini#L19-L20) | Flagi sugerują konfigurację, której nie ma. Albo je usunąć, albo przejść na własny `sdkconfig`/framework `espidf` — **decyzja niezależna od portu** |
| 4 | **`firmware/HARDWARE.md` nie istnieje**, a [`02_modem…md`](./02_modem_a7670e_communication.md) odwołuje się do niego trzykrotnie, w tym raz jako do **„autorytetu"** dla mapy pinów (linia 35). Wskazuje na niego też komentarz w [`Config.h:12`](../../../firmware/include/Config.h#L12) | `ls firmware/HARDWARE.md` → brak | **Dwa dokumenty roszczą sobie prawo do bycia źródłem prawdy o pinach**, a jeden z nich nie istnieje. Kto robi port, pójdzie tym tropem w pustkę. Najprościej: przekierować te odwołania na [`01_hardware.md`](./01_hardware.md) |
| 5 | **Trzy dalsze martwe linki względne** w dokumentacji firmware: `05_pt100…md` → `firmware/SETUP_GUIDE.md` (nie istnieje); `06_adding_sensors.md` → `../../firmware/src/main.cpp` i `../../sensor_registry.yaml` (zła głębokość — powinno być `../../../`) | sprawdzone `test -e` na wszystkich linkach względnych w `docs/technical/firmware/` | Drobne, ale `06_adding_sensors.md` to instrukcja operacyjna — psujące się linki w instrukcji, którą ktoś wykonuje krok po kroku |
| 6 | **Brief B-10 i B-11 opisują sprzęt, którego nie ma w kodzie** — I2C na GPIO 8/9, ADS1015 z kanałami AIN1–3. Zero trafień na `Wire`, `I2C`, `ADS1015`, `analogRead` | [§3](#3-korekty-do-założeń-briefu) | Briefy są nieaktualne względem [`01_hardware.md`](./01_hardware.md), który został poprawiony. Warto poprawić briefy, zanim ktoś zaplanuje pracę na ich podstawie — **B-11 (budżet energetyczny) opiera projekt detekcji zaniku zasilania na wolnych kanałach ADS1015, którego nie ma** |

**Nic z powyższego nie zostało zmienione w ramach B-10** — zlecenie kończy się na dokumencie, a cztery z sześciu pozycji dotyczą plików spoza jego zakresu. Pozycja 1 jest jedyną, która realnie blokuje pracę, i warto ją naprawić **przed** rozpoczęciem portu, bo bez niej krok 6 z [§10](#10-kolejność-uruchomienia) nie przejdzie.

---

## 15. Źródła

### Kod i dokumentacja repozytorium

- [`firmware/include/Config.h`](../../../firmware/include/Config.h), [`firmware/platformio.ini`](../../../firmware/platformio.ini), [`firmware/src/main.cpp`](../../../firmware/src/main.cpp), [`firmware/include/RtcState.h`](../../../firmware/include/RtcState.h)
- [`lib/StatusLed/src/StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp), [`lib/DeviceIdentity/src/DeviceIdentity.cpp`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp), [`lib/TelemetryPayload/src/TelemetryPayload.h`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h), [`lib/ModemLink/src/ModemLink.cpp`](../../../firmware/lib/ModemLink/src/ModemLink.cpp), [`lib/ModemPower/src/ModemPower.cpp`](../../../firmware/lib/ModemPower/src/ModemPower.cpp), [`lib/Watchdog/src/Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp), [`lib/Sensor/src/PT100Sensor.cpp`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp), [`lib/EnrollmentClient/src/EnrollmentClient.cpp`](../../../firmware/lib/EnrollmentClient/src/EnrollmentClient.cpp), [`lib/TimeSync/src/TimeSync.cpp`](../../../firmware/lib/TimeSync/src/TimeSync.cpp), [`lib/Logger/include/Logger.h`](../../../firmware/lib/Logger/include/Logger.h)
- [`01_hardware.md`](./01_hardware.md), [`02_modem_a7670e_communication.md`](./02_modem_a7670e_communication.md), [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md), [`04_device_provisioning_flow.md`](./04_device_provisioning_flow.md), [`06_adding_sensors.md`](./06_adding_sensors.md)
- [`docs/plan/01_briefy_dla_agentow.md`](../../plan/01_briefy_dla_agentow.md) — briefy B-01, B-10, B-11

### Źródła Espressif (kod źródłowy, nie materiały marketingowe)

- `components/soc/esp32/include/soc/soc_caps.h` i `components/soc/esp32s3/include/soc/soc_caps.h`, ESP-IDF v5.3 — `SOC_ECC_SUPPORTED` (brak na obu), `SOC_MPI/SHA/AES_SUPPORTED`, `SOC_HMAC/DIG_SIGN_SUPPORTED` (tylko S3), `SOC_GPIO_IN_RANGE_MAX`/`OUT_RANGE_MAX`, `SOC_UART_NUM`, `SOC_RTC_*_MEM_SUPPORTED`
- `components/mbedtls/Kconfig`, ESP-IDF v5.3 — `MBEDTLS_HARDWARE_ECC` (`depends on SOC_ECC_SUPPORTED`), `MBEDTLS_HARDWARE_MPI`, `MBEDTLS_MPI_USE_INTERRUPT` (`depends on !IDF_TARGET_ESP32`)
- `components/soc/esp32/gpio_periph.c`, ESP-IDF v5.3 — nieistniejące GPIO 24, 28–31
- `components/soc/esp32/include/soc/soc.h`, ESP-IDF v5.3 — `SOC_RTC_DATA_LOW/HIGH` (8 KiB)
- `docs/en/api-reference/peripherals/gpio/esp32.inc` i `esp32s3.inc`, ESP-IDF v5.3 — tabele GPIO, piny strappingowe, `SPI0/1`, ADC
- `cores/esp32/HardwareSerial.h` (linie 438–452), `variants/{esp32,doitESP32devkitV1,esp32s3}/pins_arduino.h`, `tools/partitions/{default,default_8MB,min_spiffs,no_ota}.csv` — arduino-esp32
- `boards/{esp32dev,esp32doit-devkit-v1,esp32-s3-devkitc-1}.json` — platform-espressif32

### Źródła zewnętrzne (do potwierdzenia kartami katalogowymi)

- Stany domyślne pinów strappingowych ESP32 (GPIO0 ↑, GPIO2 ↓, GPIO5 ↑, GPIO12 ↓, GPIO15 ↑) i skutek wysokiego MTDI: [Boot Mode Selection — esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html), [ESP32 Series Datasheet](https://www.mouser.com/datasheet/2/813/esp32_datasheet_en_1223853-1919342.pdf), [ESP32 Strapping Pins](https://www.espboards.dev/blog/esp32-strapping-pins/)
- Płytki DIN, rdzenie ([§12](#12-uwaga-kontekstowa-płytki-przemysłowe-din)): [NORVI IIOT](https://norvi.io/norvi-iiot-esp32-industrial-controller/), [Industrial Shields ESP32 PLC](https://www.industrialshields.com/industrial-hardware-solutions-based-on-esp32), [KinCony ESP32-S3](https://www.kincony.com/kincony-esp32-s3-core-board.html), [EQSP32](https://erqos.com/resources/eqsp32x-industrial-iot-controller/), [LILYGO T-Connect Pro](https://www.hackster.io/news/lilygo-goes-after-the-industrial-automators-with-the-din-mountable-t-connect-pro-9c4db04fb48e)
- Pinout DOIT ESP32 DevKit V1: [playelek/pinout-doit-32devkitv1](https://github.com/playelek/pinout-doit-32devkitv1), [Mischianti](https://mischianti.org/doit-esp32-dev-kit-v1-high-resolution-pinout-and-specs/) — **zweryfikuj na silkscreenie swojej płytki** ([§11.2](#112-układ-listwy-twojej-płytki--przed-lutowaniem))
