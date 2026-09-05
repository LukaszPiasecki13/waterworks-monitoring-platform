# Analiza portu ESP32-S3 → ESP-WROOM-32 (klasyczny ESP32)

> Analiza wykonalności i opłacalności przeniesienia firmware gatewaya z ESP32-S3 na klasyczny ESP32 (ESP-WROOM-32 / ESP32-WROOM-32E).
> **Zakres: wyłącznie dokument.** Implementacja portu jest osobnym, przyszłym zleceniem — w ramach tej pracy nie zmieniono ani jednej linii w `firmware/`.

| | |
|---|---|
| **Data analizy** | 2026-09-05 |
| **Podstawa** | brief B-10 z [`docs/plan/01_briefy_dla_agentow.md`](../../plan/01_briefy_dla_agentow.md) |
| **Stan repo** | commit `43116cd`, gałąź `claude/task-10-briefs-analysis-0id30e` |
| **Werdykt** | **nieopłacalny przy obecnej skali; opłacalny warunkowo dopiero przy ≥ ~120 szt.** |

---

## 1. Werdykt

**Port jest technicznie łatwy i ekonomicznie bezsensowny przy obecnej skali.**

Trzy liczby, które to rozstrzygają:

| | Wartość | Skąd |
|---|---|---|
| **Oszczędność na sztuce** | **25,10 zł** brutto (płytka deweloperska Espressif) | [§6.1](#61-ceny--stan-na-2026-09-05) |
| **Koszt jednorazowy portu** | **20–30 h pracy** (2 000–6 000 zł przy stawce 100–200 zł/h) | [§6.2](#62-koszt-pracy) |
| **Próg opłacalności** | **~80–240 sztuk** (zależnie od stawki), plus 32–128 szt./rok na pokrycie samego utrzymania dwóch wariantów | [§6.3](#63-próg-opłacalności) |

Przy zakładanej skali („kilka prototypów, brak planów skalowania") łączna oszczędność wynosi **75–250 zł** przy koszcie **2 000–6 000 zł**. Rachunek jest ujemny w stosunku **8:1 do 80:1**.

**Ale to nie jest cała odpowiedź.** Analiza wykazała trzy rzeczy, które są ważniejsze od samego rachunku:

1. **Firmware nie ma żadnego twardego przywiązania do S3.** Cała zależność sprowadza się do mapy pinów, typu diody statusu i wpisu `board =` w `platformio.ini`. Kod skompilował się na klasyczny ESP32 **bez ani jednej zmiany źródeł** ([§3](#3-dowód-kod-kompiluje-się-na-oba-targety-bez-zmian)). To znaczy, że port nie jest ryzykiem technicznym — jest tylko kosztem pracy przy bring-upie sprzętowym.
2. **„Punkt krytyczny" z briefu (kryptografia) nie istnieje.** Ani ESP32-S3, ani klasyczny ESP32 **nie mają akceleratora ECC** — obie rodziny liczą ECDSA P-256 programowo, tą samą ścieżką mbedTLS, z tym samym akceleratorem MPI. Port nie traci przyspieszenia, bo nie ma czego tracić ([§4.3](#43-kryptografia--punkt-krytyczny-który-okazał-się-niekrytyczny)).
3. **Hipoteza „droga do wersji przemysłowej i tak prowadzi przez klasyczny ESP32" jest w 2026 nieaktualna.** Rynek płytek przemysłowych DIN jest podzielony: część produktów siedzi na ESP-WROOM-32, ale najnowsze linie (Kincony v3, część NORVI) są już na ESP32-S3-WROOM-1U. Port przestaje być warunkiem wejścia ([§8](#8-alternatywa-płytki-przemysłowe-din--rozstrzygnięcie-hipotezy-z-briefu)).

**Rekomendacja:** nie robić portu teraz. Jeżeli motywem jest wyłącznie cena modułu, istnieje rozwiązanie za **0 godzin pracy** zamiast 20–30: zmiana wariantu w obrębie rodziny S3 (dziś kupowany `N8R8` ma 8 MB PSRAM, z których firmware nie używa **ani jednego bajtu** — patrz [§4.4](#44-pamięć--zmierzone-nie-szacowane)). Szczegóły w [§7.1](#71-tańsza-alternatywa-zamiast-portu).

Dokument daje jednocześnie wszystko, co potrzebne, żeby port **zlecić od ręki**, gdyby warunki z [§9](#9-warunki-przy-których-ten-werdykt-się-zmienia) zostały spełnione: gotową mapę pinów z uzasadnieniem każdego wyboru ([§4.1](#41-piny--kompletna-mapa-przeniesienia)), listę zmian w kodzie ([§10](#10-gotowe-wejście-do-przyszłego-zlecenia-portu)) i listę rzeczy do zweryfikowania na płytce ([§12](#12-do-zweryfikowania-na-fizycznym-sprzęcie)).

---

## 2. Metoda i status dowodów

Analiza opiera się na trzech rodzajach dowodów, oznaczonych w tekście:

| Etykieta | Znaczenie |
|---|---|
| **[zmierzone]** | Wynik uruchomienia narzędzia w tej sesji — kompilacja, dump środowiska, odczyt nagłówków SDK. Odtwarzalne. |
| **[dokumentacja]** | Cytat lub ustalenie z oficjalnej dokumentacji Espressif albo ze źródeł ESP-IDF. |
| **[przypuszczenie]** | Wniosek nie poparty bezpośrednim pomiarem ani źródłem pierwotnym. Każde takie miejsce jest oznaczone jawnie. |

**Czego nie zrobiono:** niczego nie weryfikowano na fizycznym sprzęcie. Nie ma tu ani jednego pomiaru z płytki. Lista rzeczy, które wymagają płytki, jest w [§12](#12-do-zweryfikowania-na-fizycznym-sprzęcie).

### 2.1. Środowisko pomiarowe

Kompilacje wykonano na **kopii roboczej poza repozytorium** (`/tmp/.../fwtest`), żeby nie naruszyć zakazu zmian w `firmware/` z briefu. Kopia zawierała identyczne źródła (`include/`, `lib/`, `src/`, `test/`, `scripts/`) i `platformio.ini` różniący się wyłącznie dodaniem drugiego środowiska `env:esp32-wroom` (`board = esp32dev`) o identycznych `build_flags` i `lib_deps`.

| Składnik | Wersja | Źródło |
|---|---|---|
| PlatformIO Core | 6.1.19 | [zmierzone] |
| platform `espressif32` | 7.1.0 | [zmierzone] |
| `framework-arduinoespressif32` | 3.20017.241212+sha.dcc1105b (Arduino core 2.0.17) | [zmierzone] |
| toolchain Xtensa | 8.4.0+2021r2-patch5 | [zmierzone] |

---

## 3. Dowód: kod kompiluje się na oba targety bez zmian

To jest najważniejszy pojedynczy wynik tej analizy.

```
esp32-s3      SUCCESS   RAM 19 688 B (6.0% z 327 680)   Flash 424 185 B (12.7% z 3 342 336)
esp32-wroom   SUCCESS   RAM 22 532 B (6.9% z 327 680)   Flash 432 273 B (33.0% z 1 310 720)
```
[zmierzone]

**Zero zmian w źródłach.** Ten sam `main.cpp`, te same 13 bibliotek w `lib/`, ten sam `Config.h` z pinami 11/12/13/14/48. Zmieniono wyłącznie `board = esp32-s3-devkitc-1` → `board = esp32dev`.

### 3.1. Co ten wynik znaczy, a czego nie znaczy

**Znaczy:** w kodzie nie ma żadnej konstrukcji specyficznej dla S3 — żadnego `#ifdef CONFIG_IDF_TARGET_ESP32S3`, żadnego USB CDC, żadnego PSRAM, żadnej instrukcji wektorowej. Wyszukanie w całym `firmware/` (poza `.pio/`) daje **cztery** wystąpienia ciągu „S3" i wszystkie są kosmetyczne:

| Miejsce | Charakter |
|---|---|
| [`main.cpp:169`](../../../firmware/src/main.cpp#L169) | tekst w logu startowym `"ESP32-S3 + A7670E telemetry sender"` |
| [`Config.h:11`](../../../firmware/include/Config.h#L11) | komentarz `// ESP32-S3 pins <-> A7670E` |
| [`platformio.ini:1`](../../../firmware/platformio.ini#L1) | nazwa środowiska `[env:esp32-s3]` |
| [`platformio.ini:3`](../../../firmware/platformio.ini#L3) | `board = esp32-s3-devkitc-1` |

[zmierzone: `grep -rn -iE "IDF_TARGET|ESP32S3|S3"` po `--include=*.cpp/*.h/*.ini/*.py`]

Nie znaleziono również: `HWCDC`, `USBCDC`, `ARDUINO_USB_*`, `Serial0`, `TinyUSB`, `psram`, `ps_malloc`, `heap_caps` [zmierzone].

**Nie znaczy:** że firmware zadziała na klasycznym ESP32. Kompilator nie sprawdza, czy GPIO 11 fizycznie istnieje i czy nie należy do magistrali flash. **Piny z `Config.h` są na klasycznym ESP32 częściowo niedozwolone i uruchomienie bez remapu skończy się awarią dostępu do flash.** To jest istota pracy portu i temat następnej sekcji.

---

## 4. Inwentaryzacja zależności — punkt po punkcie

### 4.1. Piny — kompletna mapa przeniesienia

#### 4.1.1. Sprostowanie do briefu

Brief B-10 zakłada, że `Config.h` używa GPIO **4, 5, 8, 9, 11, 12, 13, 14, 17, 18, 48** i że „to wymusza przemapowanie I2C (dziś 8/9)".

**Stan faktyczny:** [`Config.h`](../../../firmware/include/Config.h) definiuje GPIO **4, 5, 11, 12, 13, 14, 17, 18, 48** — dziewięć pinów, nie jedenaście. **GPIO 8 i 9 nie występują w repozytorium, a I2C nie istnieje w firmware w ogóle**: nie ma `Wire.begin()`, nie ma sterownika ADS1015, nie ma `analogRead()`. Czujnik ciśnienia PT-506 jest w kodzie nieobecny — [`01_hardware.md` §1](./01_hardware.md) opisuje go jako „draft, niepodłączony w kodzie". Wniosek: **przemapowanie I2C nie jest częścią portu**, bo nie ma czego mapować. Jest natomiast częścią projektu — dlatego w propozycji poniżej I2C jest zarezerwowane na przyszłość.

#### 4.1.2. Ograniczenia klasycznego ESP32

[dokumentacja — ESP-IDF GPIO & RTC GPIO, ESP32]

| Ograniczenie | Konsekwencja |
|---|---|
| „GPIO6-11 and GPIO16-17 are usually connected to the SPI flash and PSRAM integrated on the module and therefore should not be used for other purposes." | **GPIO 6–11 wykluczone.** GPIO 16/17 wykluczone tylko na modułach z PSRAM (WROVER); na WROOM-32 są wolne. |
| „GPIO34-39 can only be set as input mode and do not have software-enabled pullup or pulldown functions." | GPIO 34–39 tylko jako wejścia (nadają się na ADC1). |
| Piny strapujące: GPIO **0, 2, 5, 12 (MTDI), 15 (MTDO)** | Stan tych pinów przy starcie decyduje o trybie bootowania i napięciu flash. |
| GPIO 12–15 to interfejs JTAG | Użyteczne, ale generują aktywność przy starcie. |
| GPIO 1/3 to UART0 (konsola i flashowanie) | Wykluczone. |
| ADC2 nieużywalny przy aktywnym Wi-Fi | Bez znaczenia dziś (brak Wi-Fi w firmware), ale ADC1 to bezpieczniejszy wybór na przyszły pomiar 4-20 mA. |

Zakres numeracji na klasycznym ESP32 to 0–39, więc **GPIO 48 nie istnieje**.

#### 4.1.3. Proponowana mapa pinów

Płytka odniesienia: **ESP32-DevKitC-32E (moduł ESP-WROOM-32E, bez PSRAM)**. Piny wyprowadzone na goldpiny: 0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33, 34, 35, 36, 39.

| Stała w `Config.h` | S3 dziś | **WROOM-32 — propozycja** | Uzasadnienie wyboru |
|---|---|---|---|
| `MODEM_TX_PIN` | 17 | **17** | Wolny na WROOM-32, wyjściowy, nie strapujący. Bez zmiany — mniej różnic między wariantami. |
| `MODEM_RX_PIN` | 18 | **16** | GPIO 18 przenoszę na SPI SCK (natywny VSPI). GPIO 16 jest wolny na WROOM-32. ⚠️ Zajęty na modułach z PSRAM (WROVER) — wariant WROOM-32 staje się wymogiem, patrz [§4.1.4](#414-ryzyko-uboczne-tej-mapy). |
| `MODEM_PWRKEY_PIN` | 4 | **4** | Wolny, wyjściowy, nie strapujący. Bez zmiany. |
| `MODEM_RESET_PIN` | 5 | **25** | **Zmiana wymuszona.** GPIO 5 jest pinem strapującym z wewnętrznym pull-upem — przy każdym starcie ESP32 linia RESET modemu byłaby podciągana do stanu wysokiego. [`ModemPower::hardReset()`](../../../firmware/lib/ModemPower/src/ModemPower.cpp) traktuje stan wysoki jako aktywny reset, więc grozi to niezamierzonym resetem modemu przy każdym boocie. GPIO 25 jest wolny, dwukierunkowy, nie strapujący. |
| `PT100_SPI_SCK` | 12 | **18** | **Zmiana wymuszona.** GPIO 12 to MTDI — pin strapujący napięcia flash (`VDD_SDIO`). Podciągnięcie go do 3,3 V w chwili startu przełącza flash na 1,8 V i moduł nie wystartuje. Linia zegara SPI jest podciągana przez większość układów peryferyjnych → realne ryzyko cegły. GPIO 18 to natywny VSPI CLK. |
| `PT100_SPI_MISO` | 13 | **19** | Natywny VSPI MISO. GPIO 13 działałby, ale zwolnienie go pozwala trzymać cały SPI na sprzętowym VSPI. |
| `PT100_SPI_MOSI` | 11 | **23** | **Zmiana wymuszona.** GPIO 11 należy do magistrali flash SPI i nie jest wyprowadzony na module. Natywny VSPI MOSI to 23. |
| `PT100_SPI_CS` | 14 | **5** (alt. **32**) | GPIO 14 (MTMS/JTAG) działa, ale generuje impulsy przy starcie. GPIO 5 to domyślny VSPI CS i — mimo że jest pinem strapującym — jego domyślny stan przy starcie (pull-up, HIGH) to dokładnie stan nieaktywny dla CS. Bez taktowania SCK żaden impuls na CS nie zostanie zinterpretowany przez MAX31865. **Alternatywa dla puryzmu: GPIO 32** — całkowicie poza strappingiem, kosztem odejścia od domyślnych pinów VSPI. |
| `LED_PIN` | 48 | **2** lub **13** | **Zmiana wymuszona** (GPIO 48 nie istnieje). Dwa scenariusze — patrz [§4.2](#42-led-statusu). |
| *(rezerwa)* I2C SDA/SCL | — | **21 / 22** | Domyślne `Wire` na klasycznym ESP32. Rezerwacja pod przyszły ADS1015. |
| *(rezerwa)* ADC 4-20 mA | 1 *(draft)* | **34, 35, 36, 39** | ADC1, działa niezależnie od Wi-Fi. Piny tylko-wejściowe, co dla ADC jest bez znaczenia. |

**Bilans:** z dziewięciu używanych pinów **cztery muszą się zmienić obowiązkowo** (11, 12, 5, 48), **jeden zmienia się w konsekwencji przetasowania SPI** (18 → 16 dla UART), **cztery mogą zostać** (4, 17 oraz — gdyby zrezygnować z VSPI — 13, 14).

#### 4.1.4. Ryzyko uboczne tej mapy

- **Wymóg modułu bez PSRAM.** Użycie GPIO 16 na UART wyklucza moduły ESP32-WROVER. Jeżeli przyszły wybór płytki padnie na wariant z PSRAM, `MODEM_RX_PIN` trzeba przenieść na 26 lub 27. Alternatywa odporna na oba warianty: **UART na 26/27** od razu, kosztem odejścia od obecnych numerów.
- **GPIO 2 przy starcie.** Jeżeli LED wyląduje na GPIO 2, dioda z rezystorem do masy trzyma pin w stanie niskim — to jest stan wymagany przy starcie, więc konfiguracja jest bezpieczna. Odwrotne podłączenie (dioda do 3,3 V) zablokuje bootowanie.
- **Fizyczna wygoda okablowania.** [`01_hardware.md` §3](./01_hardware.md) chwali obecny układ za to, że wszystkie 4 piny SPI sąsiadują fizycznie. Proponowana mapa (18, 19, 23, 5) tę własność traci — SCK/MISO/MOSI sąsiadują, ale CS leży osobno. To argument za wariantem CS = 5 (rząd pinów) zamiast 32.

---

### 4.2. LED statusu

**Stan obecny:** [`StatusLed`](../../../firmware/lib/StatusLed/src/StatusLed.cpp) steruje adresowalną diodą WS2812 przez `Adafruit_NeoPixel`, wybierając ścieżkę **na podstawie numeru pinu**:

```cpp
if (pin_ == 48) { /* WS2812 */ } else { /* pinMode + digitalWrite */ }
```
[`StatusLed.cpp:8`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L8), [`:38`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L38)

#### 4.2.1. Dobra wiadomość: ścieżka awaryjna już istnieje

Klasa **już dziś obsługuje zwykłą diodę** — gałąź `else` robi `pinMode`/`digitalWrite`. Zmiana `LED_PIN` z 48 na 2 wystarczy, żeby firmware zaczął migać zwykłą diodą, bez dotykania biblioteki.

#### 4.2.2. Zła wiadomość: warunek jest zapisany na numerze pinu

Konsekwencja praktyczna: **zewnętrzna dioda WS2812 podłączona do dowolnego innego GPIO cicho zdegraduje się do sterowania cyfrowego** i nie zaświeci się w ogóle (WS2812 wymaga protokołu czasowego, nie poziomu). To jest błąd czekający na zdarzenie, niezależny od portu. Poprawka: rodzaj sterownika ma być parametrem konstruktora albo flagą kompilacji, nie funkcją numeru pinu. Szacunek: **3 h** wraz z testem.

#### 4.2.3. Ile faktycznie traci sygnalizacja kolorami

Brief pyta, „co to robi z sygnalizacją kolorami opisaną w [`01_hardware.md` §4](./01_hardware.md)". Odpowiedź jest zaskakująca: **nic, bo sygnalizacji kolorami nie ma.**

Obie metody publiczne — `blinkSuccess()` i `blinkError()` — wywołują `blink()`, które zapala **ten sam kolor zielony `Color(0, 255, 0)`** ([`StatusLed.cpp:40`](../../../firmware/lib/StatusLed/src/StatusLed.cpp#L40)). Różnią się wyłącznie liczbą mignięć: 1 vs 3. [`01_hardware.md` §4](./01_hardware.md) dokumentuje to zgodnie ze stanem kodu („Success: pojedynczy blink zielony", „Error: trzy blinki zielone").

**Nośnikiem informacji jest liczba mignięć, nie kolor.** Degradacja do zwykłej diody nie traci więc **żadnej informacji, którą firmware dziś przekazuje**. Utrata jest wyłącznie potencjalna — dotyczy sygnalizacji, której jeszcze nie zaprojektowano.

#### 4.2.4. Rozstrzygnięcie

**Zwykła dioda, nie zewnętrzny WS2812.** Uzasadnienie: koszt zerowy, zero dodatkowego okablowania w szafie, zero utraty obecnej funkcjonalności. Jeżeli w przyszłości powstanie projekt sygnalizacji kolorami (np. zielony / żółty / czerwony dla stanu łączności), zewnętrzny WS2812 na GPIO 13 kosztuje 2–5 zł i wymaga poprawki z [§4.2.2](#422-zła-wiadomość-warunek-jest-zapisany-na-numerze-pinu), którą i tak trzeba zrobić.

⚠️ **Uwaga zakupowa:** oryginalna płytka **ESP32-DevKitC-32E firmy Espressif nie ma diody użytkownika** — tylko diodę zasilania. Dioda na GPIO 2 występuje na tańszych płytkach zgodnych (klonach). Przy wariancie „oryginał Espressif" LED trzeba dolutować zewnętrznie. Ten szczegół zmienia rachunek z [§6](#6-rachunek-ekonomiczny) o kilka złotych i kilkanaście minut montażu na sztukę. [przypuszczenie — na podstawie schematu płytki, nie zweryfikowane fizycznie]

---

### 4.3. Kryptografia — „punkt krytyczny", który okazał się niekrytyczny

Brief nazywa ten punkt „punktem krytycznym analizy" i poleca sprawdzić, „czy używane jest przyspieszenie sprzętowe dostępne tylko na S3". **Odpowiedź brzmi: nie, bo takiego przyspieszenia nie ma na żadnym z dwóch układów.**

#### 4.3.1. Dowód — deklaracje możliwości SoC w ESP-IDF

Plik `components/soc/<target>/include/soc/soc_caps.h` (ESP-IDF, gałąź `release/v5.3`) jest źródłem prawdy o obecności peryferiów:

| Peryferium | ESP32 (klasyczny) | ESP32-S3 |
|---|---|---|
| `SOC_AES_SUPPORTED` | ✅ | ✅ |
| `SOC_SHA_SUPPORTED` | ✅ | ✅ |
| `SOC_MPI_SUPPORTED` (bignum/RSA) | ✅ | ✅ |
| `SOC_HMAC_SUPPORTED` | ❌ | ✅ |
| `SOC_DIG_SIGN_SUPPORTED` | ❌ | ✅ |
| **`SOC_ECC_SUPPORTED`** | **❌ (brak)** | **❌ (brak)** |

[zmierzone — odczyt `soc_caps.h` z repozytorium ESP-IDF]

Dedykowany akcelerator ECC mają dopiero układy z rodziny RISC-V (ESP32-C3, ESP32-H2) — nie S3. Potwierdza to dokumentacja mbedTLS dla obu targetów: ESP-IDF wystawia opcje `CONFIG_MBEDTLS_HARDWARE_AES`, `..._SHA` i `..._MPI` — i **żadnej opcji ECC** ani dla ESP32, ani dla ESP32-S3 [dokumentacja].

#### 4.3.2. Co z tego wynika dla `DeviceIdentity`

[`DeviceIdentity`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp) używa czystego mbedTLS: `mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1, ...)` ([`:198`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L198)) i `mbedtls_ecdsa_write_signature(...)` ([`:102`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L102)). Na obu targetach:

- mnożenie punktu na krzywej wykonuje **ta sama programowa implementacja `mbedtls_ecp`**,
- korzystając z **tego samego akceleratora MPI** dla arytmetyki wielkich liczb,
- **na obu układach dwurdzeniowo, 240 MHz.**

Jedyna różnica to wydajność rdzenia: Xtensa LX6 vs LX7. Publikowane wyniki CoreMark: **991,10 pkt (ESP32) vs 1181,60 pkt (ESP32-S3)** — czyli **S3 jest szybszy o ~19%** [źródło wtórne, nie Espressif].

**Wniosek:** operacje kryptograficzne na klasycznym ESP32 będą wolniejsze o rząd **~20%**, nie o rząd wielkości. Nie ma tu ryzyka projektowego.

#### 4.3.3. Bezwzględne czasy — co wiadomo, a czego nie

Nie zmierzono czasów na sprzęcie (brak płytki). Widełki z publicznych pomiarów mbedTLS na ESP32 @ 240 MHz są szerokie i sprzeczne: **weryfikacja** podpisu P-256 raportowana od ~240–390 ms (konfiguracja domyślna) do ~2 s (przy niekorzystnych ustawieniach optymalizacji). Podpis wymaga ok. **jednego** mnożenia punktu, weryfikacja ok. **dwóch** — więc podpis to rząd **100–250 ms**, a generowanie klucza jest kosztem porównywalnym z podpisem [przypuszczenie — wnioskowanie z liczby operacji, nie pomiar].

Nawet przy najbardziej pesymistycznym z tych wyników margines jest kilkukrotny. Kod dodatkowo rozbija generowanie klucza wywołaniami `esp_task_wdt_reset()` i `yield()` przed i po ([`DeviceIdentity.cpp:191–200`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L191)), a `ensureKey()` jest wywoływane raz, w `loop()`, po starcie ([`main.cpp:199–202`](../../../firmware/src/main.cpp#L199)) — nie w krytycznej ścieżce bootu.

#### 4.3.4. Sprostowanie: budżet watchdoga to nie 15 s

Brief zakłada „watchdog `esp_task_wdt` z timeoutem 15 s wg `platformio.ini`". **To założenie jest nieprawdziwe, i to na dwa niezależne sposoby — identycznie na obu targetach.**

**Po pierwsze — flaga `-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15` nie działa.** Log kompilacji pokazuje ostrzeżenie przy każdej jednostce kompilacji frameworka:

```
tools/sdk/esp32/dio_qspi/include/sdkconfig.h:345: warning: "CONFIG_ESP_TASK_WDT_TIMEOUT_S" redefined
 #define CONFIG_ESP_TASK_WDT_TIMEOUT_S 5
```
[zmierzone]

Framework Arduino jest dostarczany **skompilowany**. Makro z `build_flags` wpływa tylko na kompilację kodu użytkownika; sama implementacja TWDT siedzi w prekompilowanych bibliotekach zbudowanych z `CONFIG_ESP_TASK_WDT_TIMEOUT_S 5`. **Realny timeout to 5 s**, na ESP32 i na ESP32-S3 tak samo (potwierdzone odczytem obu `sdkconfig.h` — linie 345 i 389) [zmierzone].

**Po drugie — zadanie `loop()` w ogóle nie jest zapisane do watchdoga.** W `cores/esp32/main.cpp` Arduino ustawia `loopTaskWDTEnabled = false;` i resetuje TWDT tylko, gdy ta flaga jest prawdziwa. Firmware nigdy nie wywołuje `enableLoopWDT()` ani `esp_task_wdt_add(NULL)` [zmierzone — brak wystąpień w repo]. Zgodnie z nagłówkiem `esp_task_wdt.h` dostarczonym z frameworkiem, `esp_task_wdt_reset()` wywołane z niezapisanego zadania zwraca `ESP_ERR_NOT_FOUND` i nic nie robi. **Kilkanaście wywołań `esp_task_wdt_reset()` rozsianych po `main.cpp` i `DeviceIdentity.cpp` to dziś operacje puste.** Faktycznie pilnowane jest wyłącznie zadanie bezczynne rdzenia 0 (`CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0 1`), a `loop()` biegnie na rdzeniu 1.

**Wpływ na werdykt portu: żaden** — zachowanie jest identyczne na obu układach. **Wpływ na projekt: istotny** i wykracza poza to zlecenie — patrz [§11](#11-obserwacje-uboczne-poza-zakresem-tego-zlecenia).

#### 4.3.5. Co realnie traci się w warstwie bezpieczeństwa

To jedyny punkt, w którym port coś **rzeczywiście** zabiera — choć nie dziś:

| Mechanizm | ESP32-S3 | ESP32 klasyczny | Czy używane dziś? |
|---|---|---|---|
| Peryferium **Digital Signature (DS)** | ✅ | ❌ | **Nie.** Klucz prywatny leży jawnie w NVS (`prefs.putBytes("priv", ...)`, [`DeviceIdentity.cpp:205`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L205)). |
| Peryferium **HMAC** (klucz w eFuse) | ✅ | ❌ | Nie. |
| **Secure Boot V2** | ✅ | ✅ tylko od rewizji krzemu **v3.0** | Nie. |
| **Flash encryption** | ✅ | ✅ | Nie. |

Dwa zastrzeżenia, które osłabiają ten punkt jako argument przeciw portowi:

1. **Peryferium DS na S3 obsługuje wyłącznie RSA** — „The RSA Digital Signature Peripheral (RSA_DS) provides hardware acceleration of signing messages based on RSA" [dokumentacja]. Obecna tożsamość urządzenia opiera się na **ECDSA P-256**, więc DS nie dałoby się użyć bez zmiany całego schematu tożsamości po obu stronach (firmware + backend `device_identity`).
2. **Secure Boot V2 jest dostępny również na klasycznym ESP32** od rewizji v3.0 [dokumentacja]. Współczesne moduły ESP32-WROOM-32E są tej rewizji, więc ścieżka „podpisany bootloader + szyfrowany flash" pozostaje otwarta także po porcie. [przypuszczenie co do rewizji konkretnej dostawy — do sprawdzenia na etykiecie modułu]

**Podsumowanie:** port zamyka drogę do sprzętowej ochrony klucza opartej o HMAC/DS, ale ta droga i tak wymaga przejścia z ECDSA na RSA. Jeżeli platforma kiedyś podniesie wymagania bezpieczeństwa do poziomu „klucz nigdy nie opuszcza sprzętu", **będzie to argument za S3 dużo mocniejszy niż jakakolwiek oszczędność 25 zł** — i wtedy port trzeba będzie cofnąć. To realne ryzyko utopionego kosztu, warte odnotowania przy decyzji.

---

### 4.4. Pamięć — zmierzone, nie szacowane

| | ESP32-S3 (`esp32-s3-devkitc-1`) | ESP32 (`esp32dev`) | Różnica |
|---|---|---|---|
| **RAM statyczny** | 19 688 B (6,0%) | 22 532 B (6,9%) | **+2 844 B (+14,4%)** |
| **Flash (app)** | 424 185 B (12,7%) | 432 273 B (33,0%) | **+8 088 B (+1,9%)** |
| Rozmiar partycji app | 3 342 336 B (`default_8MB.csv`) | 1 310 720 B (`default.csv`) | |
| Dostępny RAM wg BSP | 327 680 B | 327 680 B | identyczny |
| Flash na module | 8 MB | 4 MB | |
| PSRAM | 8 MB (**nieużywane**) | brak | |

[zmierzone]

**Interpretacja:**

- **Flash nie jest wąskim gardłem.** 33% zajętości jednej partycji aplikacyjnej. Co ważne, `default.csv` dla 4 MB to układ **dwuslotowy** (app0 + app1 po 1,25 MiB) — czyli klasyczny ESP32 ma miejsce na OTA już przy obecnej konfiguracji, z zapasem 67% w każdym slocie. Sam brak PSRAM i mniejszy flash nie blokują niczego, co firmware dziś robi ani czego potrzebuje do OTA.
- **RAM nie jest wąskim gardłem.** Wzrost o 2,8 KB przy 320 KB dostępnych. Statyczne zużycie to 6,9%.
- **Bufor okien telemetrii jest tani.** [`TelemetryPayload`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L34) trzyma `RETAIN_WINDOWS_MAX = WINDOWS_PER_BATCH * 12 = 48` okien. Przy jednym czujniku PT100 jedno okno to `MeasurementWindow` (8 + 4 B) plus `std::vector` z jedną parą `(ISensor*, SensorReading)` — rzędu 40–60 B razem z narzutem alokatora. **48 okien ≈ 2–3 KB** [przypuszczenie — wyliczenie ze struktur, nie pomiar sterty]. Nawet przy pięciu czujnikach to rząd 10 KB. `TINY_GSM_RX_BUFFER=1024` to kolejny 1 KB. Największym pojedynczym konsumentem sterty jest `String payload` z `serializeJson` — rzędu jednostek KB przy 4 oknach.
- **Płacimy za PSRAM, którego nie używamy.** Firmware nie zawiera ani jednego odwołania do PSRAM [zmierzone]. Kupowany dziś `ESP32-S3-DevKitC-1-**N8R8**` ma 8 MB PSRAM w cenie. To jest bezpośrednia przesłanka dla alternatywy z [§7.1](#71-tańsza-alternatywa-zamiast-portu).

---

### 4.5. USB / Serial

Brief zakłada, że „S3 ma natywne USB CDC, klasyczny ESP32 wymaga konwertera UART — wpływ na logi i na proces flashowania w terenie".

**W obecnej konfiguracji ta różnica jest zerowa.** Dump środowiska pokazuje, że płytka S3 definiuje `-DARDUINO_USB_MODE=1`, ale **`ARDUINO_USB_CDC_ON_BOOT` nie jest ustawione** [zmierzone]. W Arduino core 2.0.17 oznacza to, że `Serial` jest mapowane na **UART0**, a nie na natywne USB CDC. Logi z [`Logger.h`](../../../firmware/lib/Logger/include/Logger.h) (`Serial.printf`) idą więc przez most USB-UART na płytce — **dokładnie tak samo jak na klasycznym ESP32-DevKitC.**

| | ESP32-S3-DevKitC-1 | ESP32-DevKitC-32E |
|---|---|---|
| Logi dziś | UART0 → most USB-UART na płytce | UART0 → most USB-UART na płytce |
| Flashowanie | przez ten sam most (albo natywne USB, opcjonalnie) | przez most |
| Odzyskiwanie „zamurowanej" płytki | możliwe przez natywne USB DFU | wymaga BOOT + EN |

**Wniosek:** przy pracy na płytkach deweloperskich różnica jest praktycznie żadna. Zaczyna mieć znaczenie dopiero **na własnej płytce PCB**, gdzie S3 pozwala oszczędzić układ mostka (CP2102/CH340, ~4–8 zł + miejsce). Ironia jest warta odnotowania: **na etapie własnego PCB — czyli tam, gdzie oszczędność na module byłaby realna — S3 częściowo tę oszczędność odbiera, bo nie wymaga mostka.**

---

### 4.6. `RTC_DATA_ATTR`

Trzy zmienne w [`RtcState.h`](../../../firmware/include/RtcState.h) (`rtcRestartCounter`, `rtcSyncedTimeUtcSec`, `rtcSyncMillis`) używają `RTC_DATA_ATTR`, żeby przetrwać `esp_restart()` wywoływane przez [`Watchdog::attemptRecovery()`](../../../firmware/lib/Watchdog/src/Watchdog.cpp).

**Zgodność: pełna.** Oba układy mają pamięć RTC slow (8 KB) i oba obsługują `RTC_DATA_ATTR` w identyczny sposób. Kod **skompilował się na oba targety bez zmian** [zmierzone], co obejmuje również te deklaracje.

⚠️ Jedno zastrzeżenie z istniejącej dokumentacji: [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md) sam wymienia w tabeli diagnostycznej przypadek „RTC counter nie increments → RTC memory nie persisted (variant ESP32 issue)". To jest **istniejąca, nierozstrzygnięta wątpliwość dokumentacyjna**, niezależna od portu — ale port jest dobrą okazją, żeby ją zamknąć pomiarem na obu płytkach. Do listy w [§12](#12-do-zweryfikowania-na-fizycznym-sprzęcie).

---

### 4.7. `platformio.ini`

Wymóg z briefu: nowe środowisko `env:esp32-wroom` **obok** istniejącego, bez usuwania `env:esp32-s3`.

Obecny plik ma 29 linii, z czego 15 to wspólne `lib_deps` i `build_flags` — dosłowne skopiowanie ich do drugiego środowiska stworzyłoby duplikat do rozjechania się. Sprawdzona w tej analizie struktura (użyta w kopii roboczej) rozwiązuje to sekcją `[common]` i interpolacją `${common.*}`:

```ini
[common]
framework = arduino
lib_deps = ...          ; jedna lista dla obu
build_flags = ...       ; jeden zestaw flag dla obu
lib_extra_dirs = ${PROJECT_DIR}/lib

[env:esp32-s3]
platform = espressif32
board = esp32-s3-devkitc-1
extra_scripts = scripts/prebuild.py
lib_deps = ${common.lib_deps}
build_flags = ${common.build_flags} -D BOARD_ESP32_S3

[env:esp32-wroom]
platform = espressif32
board = esp32dev
extra_scripts = scripts/prebuild.py
lib_deps = ${common.lib_deps}
build_flags = ${common.build_flags} -D BOARD_ESP32_WROOM
```

Flagi `-D BOARD_*` służyłyby do wyboru mapy pinów w `Config.h` (`#if defined(BOARD_ESP32_WROOM) ... #else ... #endif`) — to jedyna zmiana w `Config.h` poza samymi numerami. Konstrukcja została **zweryfikowana kompilacją obu środowisk** w tej analizie [zmierzone].

⚠️ **Uwaga:** `extra_scripts = scripts/prebuild.py` w obecnej postaci wywraca build — patrz [§11.1](#111-hook-prebuild-wywraca-build). Trzeba to naprawić **przed** portem, niezależnie od portu.

---

### 4.8. Pozostałe API — sprawdzone, bez zastrzeżeń

| Konstrukcja | Miejsce | Zgodność z ESP32 |
|---|---|---|
| `Preferences` / NVS | [`DeviceIdentity.cpp`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp) — 12 wywołań `prefs.begin()` | ✅ identyczne API, ta sama implementacja NVS |
| `esp_read_mac(mac, ESP_MAC_WIFI_STA)` | [`DeviceIdentity.cpp:217`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp#L217) | ✅ dostępne na obu; numer seryjny `WW-<MAC>` pozostaje unikalny |
| `HardwareSerial SerialAT(1)` | [`main.cpp:25`](../../../firmware/src/main.cpp#L25) | ✅ oba mają ≥ 3 UART-y sprzętowe; UART1 wolny na obu |
| `SPI.begin(SCK, MISO, MOSI, CS)` z pinami niestandardowymi | [`PT100Sensor.cpp:14`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L14) | ✅ macierz GPIO działa na obu; przy proponowanej mapie użyte są i tak natywne piny VSPI |
| `esp_restart()` | [`Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp) | ✅ |
| `TinyGsmClientSecure` (TLS w modemie) | [`TelemetryHttpClient.cpp:8`](../../../firmware/lib/TelemetryHttpClient/src/TelemetryHttpClient.cpp#L8) | ✅ **bez znaczenia dla portu** — TLS realizuje modem A7670E, nie ESP32. Ta decyzja architektoniczna zdejmuje z MCU cały stos TLS (i jego apetyt na RAM), co dodatkowo osłabia argument „S3 ma więcej pamięci". |
| `std::vector`, `std::function`, `std::pair` | [`TelemetryPayload`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) | ✅ ta sama biblioteka standardowa, ten sam toolchain Xtensa |
| `mktime`, `gmtime_r`, `settimeofday` | [`TimeSync.cpp`](../../../firmware/lib/TimeSync/src/TimeSync.cpp) | ✅ newlib identyczny |
| Testy `env:native` (googletest) | [`firmware/test/`](../../../firmware/test/) | ✅ **niewrażliwe na port** — nie kompilują się na target sprzętowy |

---

## 5. Tabela zbiorcza — co trzeba zrobić i jakie to ryzyko

| # | Obszar | Zmiana wymagana | Ryzyko | Nakład |
|---|---|---|---|---|
| 1 | `Config.h` — SPI MOSI (11) | **Tak, obowiązkowo** | 🔴 wysokie — pin flash, uruchomienie bez zmiany = brak dostępu do flash | 0,5 h |
| 2 | `Config.h` — SPI SCK (12) | **Tak, obowiązkowo** | 🔴 wysokie — strapping napięcia flash, ryzyko braku bootu | 0,5 h |
| 3 | `Config.h` — MODEM_RESET (5) | **Tak, zalecane** | 🟡 średnie — niezamierzony reset modemu przy starcie | 0,5 h |
| 4 | `Config.h` — LED (48) | **Tak, obowiązkowo** | 🟢 niskie — pin nie istnieje, kompilacja przechodzi, dioda nie działa | 0,5 h |
| 5 | `Config.h` — UART RX (18) | Tak, w konsekwencji SPI | 🟢 niskie | 0,5 h |
| 6 | `StatusLed` — sterownik zamiast `pin_ == 48` | Tak (i tak potrzebne) | 🟢 niskie | 3 h |
| 7 | `platformio.ini` — `[common]` + drugie env | Tak | 🟢 niskie — **zweryfikowane kompilacją** | 1 h |
| 8 | Kryptografia | **Nie** | 🟢 brak — brak akceleratora ECC po obu stronach | 0 h |
| 9 | Pamięć RAM/flash | **Nie** | 🟢 brak — zmierzone, z zapasem | 0 h |
| 10 | `RTC_DATA_ATTR` | **Nie** | 🟢 brak | 0 h |
| 11 | USB/Serial | **Nie** (przy płytkach dev) | 🟢 brak | 0 h |
| 12 | NVS, MAC, UART, SPI API | **Nie** | 🟢 brak | 0 h |
| 13 | Testy `env:native` | **Nie** | 🟢 brak | 0 h |
| 14 | **Bring-up sprzętowy** | **Tak** | 🟡 średnie — nieprzewidywalny, to zawsze najdroższa część | **8–16 h** |
| 15 | Dokumentacja (`01`, `02`, `03`, `05`) | Tak | 🟢 niskie | 3 h |

---

## 6. Rachunek ekonomiczny

### 6.1. Ceny — stan na 2026-09-05

Wszystkie ceny **brutto**, sprawdzone w dniu analizy (nie z pamięci).

**Poziom A — gotowe płytki deweloperskie (dzisiejsza skala, kilka prototypów):**

| Produkt | Cena | Sklep |
|---|---|---|
| ESP32-S3-DevKitC-1-N8R8 (8 MB flash + 8 MB PSRAM) — *stan obecny* | **99,00 zł** | Botland, wysyłka 24 h |
| ESP32-DevKitC-32E V4 (ESP-WROOM-32E, oryginał Espressif) | **73,90 zł** | Botland, wysyłka 24 h |
| ESP32 DevKit zgodny (ESP-WROOM-32, producent inny niż Espressif) | **49,90 zł** | Botland, wysyłka 24 h |

**Poziom B — moduły SMD (przyszłe własne PCB):**

| Produkt | Cena | Sklep |
|---|---|---|
| ESP32-WROOM-32E, 4 MB flash | **16,90 zł** | Botland |
| ESP-WROOM-32 | 38,93 zł | Kamami (1 szt. na stanie) |
| ESP32-S3-WROOM-1 | brak w detalu PL w chwili badania | — |

**Różnica na sztuce:**

| Porównanie | Δ | Uczciwość porównania |
|---|---|---|
| S3-DevKitC-1-N8R8 vs **DevKitC-32E (oryginał)** | **25,10 zł** | ✅ oryginał vs oryginał — **to jest liczba bazowa** |
| S3-DevKitC-1-N8R8 vs DevKit zgodny (klon) | 49,10 zł | ⚠️ oryginał vs klon; mieszają się dwie zmienne (rodzina układu + producent płytki) |
| moduł WROOM-32E vs moduł S3-WROOM-1 | ~5–11 zł | ⚠️ [przypuszczenie] — brak ceny detalicznej S3-WROOM-1 w PL; oparte na katalogowych 5–6,5 USD/szt. u dystrybutorów |

⚠️ **Uwaga metodologiczna:** różnica 49,10 zł kusi, ale porównuje oryginalną płytkę Espressif z klonem. Uczciwe porównanie „rodzina vs rodzina" to **25,10 zł**. Gdyby dopuścić klony, trzeba by je dopuścić po obu stronach — a klony płytek S3 również istnieją i są tańsze niż 99 zł.

**Dostępność:** oba warianty są u Botlanda oznaczone „Dostępny / wysyłka 24 h". **Przesłanka z briefu, że ESP-WROOM-32 jest „szerzej dostępny", nie potwierdza się dla ilości prototypowych na rynku polskim.** Może być prawdziwa dla zamówień produkcyjnych na tysiące sztuk — to nie jest dziś nasz przypadek.

**Cykl życia** [dokumentacja — Espressif Longevity Commitment]:

| Rodzina | Zobowiązanie | Koniec |
|---|---|---|
| ESP32 | 15 lat (od 2016-01-01) | **2031-01-01** |
| ESP32-S3 | 12 lat (od 2021-01-01) | **2033-01-01** |

Klasyczny ESP32 kończy wsparcie **dwa lata wcześniej** niż S3. Przy horyzoncie produktu liczonym w latach to argument przeciw portowi, nie za.

### 6.2. Koszt pracy

| Zadanie | h |
|---|---|
| A. Nowe środowisko `env:esp32-wroom` + `[common]` + remap w `Config.h` (bez ruszania S3) | 2 |
| B. Refaktor `StatusLed` — typ sterownika zamiast `pin_ == 48` + test | 3 |
| C. Weryfikacja NVS / `esp_read_mac` / `RTC_DATA_ATTR` na docelowej płytce | 1 |
| D. Kompilacja obu środowisk i usunięcie różnic | 1 |
| E. **Bring-up sprzętowy**: modem (UART / PWRKEY / RESET), MAX31865 na nowym SPI, pomiar czasu keygen i podpisu, pełny cykl enrollment → telemetria | **8–16** |
| F. Aktualizacja dokumentacji (`01_hardware.md`, `02_modem…`, `03_reset…`, `05_pt100…`) | 3 |
| G. Testy regresyjne `env:native` + poprawki | 2–3 |
| **Razem** | **20–30 h** |

Pozycja E dominuje i jest najsłabiej przewidywalna — to praca „na biurku z płytką", gdzie jeden nieoczywisty problem z zasilaniem modemu albo z impulsem na PWRKEY potrafi zjeść dzień. Widełki 8–16 h są **optymistyczne przy założeniu, że sprzęt jest pod ręką i działa**.

**Utrzymanie dwóch wariantów: 8–16 h/rok** [przypuszczenie — oparte na tempie zmian widocznym w historii repo]. Każdy nowy czujnik, każda zmiana mapy pinów i każda aktualizacja frameworka wymaga zbudowania i przetestowania na dwóch płytkach zamiast jednej.

### 6.3. Próg opłacalności

Wzór z briefu: **N = (koszt pracy nad portem + roczny koszt utrzymania × lata) ÷ oszczędność na module**.

**Próg jednorazowy (sam port, bez utrzymania):**

| Stawka pracy | Koszt portu (20–30 h) | Próg przy Δ = 25,10 zł | Próg przy Δ = 49,10 zł |
|---|---|---|---|
| 100 zł/h | 2 000 – 3 000 zł | **80 – 120 szt.** | 41 – 61 szt. |
| 150 zł/h | 3 000 – 4 500 zł | **120 – 179 szt.** | 61 – 92 szt. |
| 200 zł/h | 4 000 – 6 000 zł | **159 – 239 szt.** | 81 – 122 szt. |

**Próg utrzymaniowy (ile sztuk rocznie musi się sprzedać, żeby pokryć samo utrzymanie dwóch wariantów):**

| Stawka pracy | Utrzymanie 8–16 h/rok | Sztuk/rok przy Δ = 25,10 zł |
|---|---|---|
| 100 zł/h | 800 – 1 600 zł | **32 – 64 szt./rok** |
| 150 zł/h | 1 200 – 2 400 zł | **48 – 96 szt./rok** |
| 200 zł/h | 1 600 – 3 200 zł | **64 – 128 szt./rok** |

Ten drugi próg jest ważniejszy od pierwszego, bo **jest bezterminowy**. Nawet gdyby przyjąć, że praca nad portem jest darmowa (własny czas, koszt alternatywny pominięty), utrzymanie dwóch wariantów wymaga **stałej sprzedaży kilkudziesięciu sztuk rocznie**, żeby w ogóle wyjść na zero.

### 6.4. Konfrontacja ze skalą rzeczywistą

Skala z ustaleń wspólnych briefów: **kilka prototypów u pierwszego klienta, brak planów skalowania.** Przyjmijmy 3–10 sztuk.

| | Wartość |
|---|---|
| Łączna oszczędność (3–10 szt. × 25,10 zł) | **75 – 251 zł** |
| Koszt portu (150 zł/h) | **3 000 – 4 500 zł** |
| **Stosunek** | **12:1 do 60:1 na niekorzyść portu** |

Kontekst z planu biznesowego, [§4.2.2](../../business/01_plan_biznesowy.md) i [§4.1.1](../../business/01_plan_biznesowy.md):

| Pozycja | Wartość | Udział 25,10 zł |
|---|---|---|
| Sprzęt na obiekt (MVP / pole) | 1 400 – 3 500 zł | **0,7 – 1,8 %** |
| Koszt całkowity na obiekt (sprzęt + wdrożenie) | 2 900 – 8 300 zł | **0,3 – 0,9 %** |
| Sam dojazd instalatora | 200 – 500 zł | 25,10 zł to **5–13 % jednego dojazdu** |

**Cena modułu jest szumem w tym rachunku.** Jedna wizja lokalna kosztuje tyle, co moduły do dwudziestu urządzeń. Optymalizacja tej pozycji przy obecnej skali to optymalizacja niewłaściwej rzeczy.

---

## 7. Co się traci — funkcja po funkcji

| Funkcja | Traci się? | Waga |
|---|---|---|
| **Sygnalizacja kolorami (WS2812)** | Tylko potencjalnie. Dziś obie sygnalizacje są zielone i różnią się liczbą mignięć — patrz [§4.2.3](#423-ile-faktycznie-traci-sygnalizacja-kolorami). Zewnętrzny WS2812 przywraca funkcję za 2–5 zł. | 🟢 pomijalna |
| **Peryferium Digital Signature / HMAC** | Tak, bezpowrotnie. Ale wymaga przejścia z ECDSA na RSA po obu stronach systemu, więc dziś jest nieużywalne. Patrz [§4.3.5](#435-co-realnie-traci-się-w-warstwie-bezpieczeństwa). | 🟡 istotna dopiero przy podniesieniu wymagań bezpieczeństwa |
| **~19 % mocy obliczeniowej** | Tak (CoreMark 991 vs 1182). Bez wpływu — firmware jest zdominowany przez oczekiwanie na modem, nie przez obliczenia. | 🟢 pomijalna |
| **4 MB flash i 8 MB PSRAM** | Tak. Zapas spada z 87 % do 67 % w slocie OTA. PSRAM i tak nieużywany. | 🟢 pomijalna |
| **Natywne USB (DFU, odzyskiwanie)** | Tak, ale w obecnej konfiguracji nieużywane — logi i tak idą przez UART0. Patrz [§4.5](#45-usb--serial). | 🟢 pomijalna przy płytkach dev |
| **Bluetooth 5.0 LE / Wi-Fi 4** | Nieużywane w firmware (transmisja przez modem LTE). | 🟢 brak |
| **2 lata wsparcia producenta** | Tak — 2031 zamiast 2033. | 🟡 istotna przy horyzoncie > 5 lat |
| **Więcej wolnych GPIO** | Tak. S3 daje ~36 wyprowadzonych GPIO bez ograniczeń strappingowych tej skali; WROOM-32 ma 26 wyprowadzonych, z czego 4 tylko-wejściowe i 5 strapujących. Przy rozbudowie o kolejne czujniki (I2C + SPI + ADC + RS485) robi się ciasno. | 🟡 istotna przy rozbudowie |

### 7.1. Tańsza alternatywa zamiast portu

Jeżeli jedynym motywem jest cena, istnieją opcje **o rząd wielkości tańsze niż 20–30 h pracy**:

1. **Wariant S3 bez PSRAM.** Firmware nie używa PSRAM ani bajtu [zmierzone]. Płytki `ESP32-S3-DevKitC-1-N8` (bez `R8`) są tańsze od `N8R8`. Koszt zmiany: **0 h pracy inżynierskiej** — zmiana pozycji w zamówieniu. Blokada: Botland nie miał wariantu `N8` w chwili badania; trzeba sprawdzić Kamami/TME/Mouser.
2. **Płytka S3 innego producenta niż Espressif.** Analogicznie do klonów ESP32, klony płytek S3 są tańsze. Zero zmian w kodzie (ten sam `board`), zero zmian w mapie pinów.
3. **Negocjacja / zakup hurtowy przy pierwszym wdrożeniu.** Przy 10 sztukach rabat kilku procent daje porównywalną kwotę co cała różnica między rodzinami.

Każda z tych ścieżek zachowuje jeden wariant firmware — a więc **nie generuje kosztu utrzymaniowego z [§6.3](#63-próg-opłacalności), który jest realnym problemem, nie sam port.**

---

## 8. Alternatywa: płytki przemysłowe DIN — rozstrzygnięcie hipotezy z briefu

Brief stawia hipotezę, którą sam nazywa potencjalnie ważniejszą od rachunku cenowego:

> „jeśli droga do wersji przemysłowej i tak prowadzi przez klasyczny ESP32, port przestaje być kwestią oszczędności, a staje się warunkiem wejścia."

**Hipoteza w 2026 nie potwierdza się.** Rynek gotowych sterowników przemysłowych DIN na ESP32 jest podzielony między obie rodziny:

| Produkt | Układ | Forma | Cena | Uwagi |
|---|---|---|---|---|
| **Industrial Shields ESP32 PLC 14** | **ESP-WROOM-32U — klasyczny ESP32** | DIN 100×45×115 mm | **99,95 EUR** | 12–24 V DC, Ethernet, RS485, I2C, 4 AI / 3 DI / 4 DO / 1 przekaźnik. Zakres pracy **−20…+60 °C** — poniżej normy przemysłowej (−40…+85 °C) |
| **NORVI IIOT** | **ESP32-WROOM-32 — klasyczny ESP32** | DIN, 24 V | — | Wejścia 4-20 mA w wariantach AE02-I / AE04-I |
| **NORVI** (nowsze linie) | również **ESP32-S3-WROOM** | DIN | — | Producent buduje na obu rodzinach |
| **Kincony KC868-A8v3 / A16v3** | **ESP32-S3-WROOM-1U (N16R8)** | DIN | — | Najnowsza linia v3 przeszła **na S3**, nie na klasyczny |

**Wnioski:**

1. **Nie ma jednej „drogi przemysłowej".** Wybór rodziny układu podąża za wyborem konkretnego produktu, a produkty istnieją po obu stronach. Wybierając płytkę na S3 (Kincony v3, NORVI S3) **port jest zbędny**; wybierając Industrial Shields lub NORVI IIOT — port jest konieczny.
2. **Kolejność decyzji jest odwrotna niż zakłada brief.** Najpierw wybiera się płytkę przemysłową (kryteria: certyfikaty, zakres temperatur, IP, wejścia 4-20 mA, izolacja, dostępność w PL) — **a wybór rodziny MCU jest tego konsekwencją, nie przesłanką.** Robienie portu „na zapas", zanim ta decyzja padnie, ma 50 % szans być pracą wyrzuconą.
3. **Przy takich cenach różnica na module znika całkowicie.** Sterownik przemysłowy to ~430 zł (99,95 EUR) wobec 25,10 zł różnicy między rodzinami — czyli **6 %**. Oszczędność, która była marginalna przy płytkach deweloperskich, przy wersji przemysłowej przestaje istnieć jako pozycja.
4. **Uwaga do B-01 (wariant W3):** żaden ze sprawdzonych produktów nie deklaruje zakresu −40…+85 °C. Industrial Shields podaje −20…+60 °C, co dla nieogrzewanej hydroforni w Małopolsce zimą jest wartością do sprawdzenia, nie do przyjęcia na wiarę. To ustalenie należy do B-01, tu odnotowane jako produkt uboczny.

**Rozstrzygnięcie:** hipoteza „port jako warunek wejścia" **nie jest dziś prawdziwa**. Staje się prawdziwa **warunkowo** — dopiero po wyborze konkretnej płytki przemysłowej z rodziny klasycznego ESP32. To przenosi decyzję o porcie **po** decyzji o sprzęcie przemysłowym, a nie przed nią.

---

## 9. Warunki, przy których ten werdykt się zmienia

Werdykt „nie robić" nie jest bezterminowy. Trzy zdarzenia go odwracają — każde niezależnie:

| # | Warunek wyzwalający | Dlaczego zmienia werdykt | Jak to zauważyć |
|---|---|---|---|
| **W1** | **Wybór płytki przemysłowej DIN opartej na klasycznym ESP32** (Industrial Shields, NORVI IIOT) w ramach B-01 / W3 | Port przestaje być oszczędnością, staje się warunkiem uruchomienia sprzętu. Rachunek z [§6](#6-rachunek-ekonomiczny) przestaje obowiązywać — nie ma alternatywy. | Decyzja z B-01, wariant W3 |
| **W2** | **Zamówienie ≥ ~120 szt.** (przy stawce 150 zł/h) lub stała sprzedaż ≥ ~50 szt./rok | Próg z [§6.3](#63-próg-opłacalności) zostaje przekroczony i port zaczyna się zwracać, także z uwzględnieniem utrzymania. | Pipeline sprzedażowy |
| **W3** | **Trwały brak dostępności modułów S3** przy zachowanej dostępności WROOM-32 | Przesłanka z briefu, dziś niepotwierdzona ([§6.1](#61-ceny--stan-na-2026-09-05)), ale rynek półprzewodników bywa zmienny. | Monitorowanie stanów magazynowych przy zamówieniach |

Warunek, który **wzmacnia** werdykt „nie robić":

| # | Warunek | Skutek |
|---|---|---|
| **W4** | **Podniesienie wymagań bezpieczeństwa do „klucz prywatny nigdy nie opuszcza sprzętu"** (prawdopodobne przy NIS2/KSC — patrz B-01) | Wymusza peryferium DS/HMAC → **wyłącznie S3**. Port zrobiony wcześniej byłby kosztem utopionym. Patrz [§4.3.5](#435-co-realnie-traci-się-w-warstwie-bezpieczeństwa). |

---

## 10. Gotowe wejście do przyszłego zlecenia portu

Gdyby zaszedł którykolwiek warunek z [§9](#9-warunki-przy-których-ten-werdykt-się-zmienia), zlecenie portu można napisać bez ponownej analizy. Ten dokument dostarcza:

**Zakres prac (kolejność wykonania):**

1. **Najpierw naprawa hooka prebuild** ([§11.1](#111-hook-prebuild-wywraca-build)) — bez tego żaden build nie przejdzie, niezależnie od targetu.
2. Refaktor `StatusLed`: rodzaj sterownika jako parametr konstruktora (`LedType::Ws2812` / `LedType::Simple`) zamiast warunku `pin_ == 48`. Test jednostkowy w `env:native` na obu ścieżkach.
3. `platformio.ini`: sekcja `[common]` + `env:esp32-wroom` (`board = esp32dev`) obok istniejącego `env:esp32-s3`, flagi `-D BOARD_ESP32_S3` / `-D BOARD_ESP32_WROOM`. Struktura zweryfikowana kompilacją, gotowy szkielet w [§4.7](#47-platformioini).
4. `Config.h`: mapa pinów pod `#if defined(BOARD_ESP32_WROOM)` wg tabeli z [§4.1.3](#413-proponowana-mapa-pinów).
5. Kompilacja obu środowisk (oczekiwany wynik znany: [§3](#3-dowód-kod-kompiluje-się-na-oba-targety-bez-zmian)).
6. Bring-up sprzętowy wg listy z [§12](#12-do-zweryfikowania-na-fizycznym-sprzęcie).
7. Aktualizacja dokumentacji: `01_hardware.md` (druga kolumna mapy pinów, nie osobny dokument), `02_modem_a7670e_communication.md` §2.2, `03_esp32_reset_and_recovery.md` (tytuł i wstęp mówią „ESP32-S3"), `05_pt100_temperature_sensor.md` §SPI Pins.

**Czego zlecenie NIE musi już ustalać:** czy kod się skompiluje (tak, zweryfikowane), czy kryptografia się zmieści (tak, brak akceleratora po obu stronach), czy starczy RAM/flash (tak, zmierzone), czy `RTC_DATA_ATTR` działa (tak), które piny są niedozwolone (rozpisane), jak ma wyglądać `platformio.ini` (szkielet gotowy).

**Definicja ukończenia portu:** oba środowiska budują się z jednego źródła; urządzenie na WROOM-32 przechodzi pełen cykl `ACTIVATE <kod>` → enrollment → challenge/response → wysyłka telemetrii z PT100 → potwierdzenie w backendzie; zmierzone czasy `mbedtls_ecp_gen_key` i `mbedtls_ecdsa_write_signature` są zapisane w `01_hardware.md`; testy `env:native` przechodzą.

---

## 11. Obserwacje uboczne (poza zakresem tego zlecenia)

Trzy rzeczy znalezione przy okazji pomiarów. **Żadna nie wpływa na werdykt portu — dotyczą obu targetów tak samo — ale każda dotyczy działającego dziś firmware.** Odnotowane, żeby nie zginęły; do zlecenia osobno.

### 11.1. Hook prebuild wywraca build

`extra_scripts = scripts/prebuild.py` w [`platformio.ini:7`](../../../firmware/platformio.ini#L7) **powoduje niepowodzenie kompilacji na czystym repozytorium**, z dwóch niezależnych powodów [zmierzone]:

1. **Zły moment.** Hook jest zarejestrowany jako `env.AddPreAction("$BUILD_DIR/firmware.elf", ...)`, czyli uruchamia się przed **linkowaniem**. `SensorRegistry.h` jest potrzebny przy **kompilacji** ([`ISensor.h:3`](../../../firmware/lib/Sensor/include/ISensor.h#L3)), która następuje wcześniej. Wynik na czystym repo: `fatal error: SensorRegistry.h: No such file or directory`.
2. **`__file__` nie istnieje.** Gdy plik nagłówkowy już istnieje i build dochodzi do linkowania, hook przewraca się na `NameError: name '__file__' is not defined` ([`prebuild.py:33`](../../../firmware/scripts/prebuild.py#L33)) — SCons wykonuje skrypt w sposób, w którym `__file__` nie jest ustawione.

Obejście użyte w tej analizie: ręczne `python3 firmware/scripts/prebuild.py` z katalogu głównego (tryb standalone działa poprawnie), a następnie build. Poprawka: `env.AddPreAction` na obiektach źródłowych zamiast na `firmware.elf` (albo wykonanie generacji natychmiast przy imporcie skryptu) plus zastąpienie `__file__` ścieżką z `env["PROJECT_DIR"]`.

`SensorRegistry.h` jest w `.gitignore`, więc **każdy świeży klon repozytorium ma dziś zepsuty build firmware.**

### 11.2. Watchdog nie chroni pętli głównej

Rozpisane w [§4.3.4](#434-sprostowanie-budżet-watchdoga-to-nie-15-s). Skrót:

- flaga `-D CONFIG_ESP_TASK_WDT_TIMEOUT_S=15` jest ignorowana przez prekompilowany framework — realny timeout to **5 s**;
- zadanie `loop()` nie jest zapisane do TWDT (`loopTaskWDTEnabled = false` i brak `enableLoopWDT()`), więc wszystkie wywołania `esp_task_wdt_reset()` w `main.cpp` i `DeviceIdentity.cpp` zwracają `ESP_ERR_NOT_FOUND` i **nie robią nic**;
- pilnowane jest wyłącznie zadanie bezczynne rdzenia 0, a `loop()` biegnie na rdzeniu 1 — zawieszenie `loop()` nie wywoła resetu sprzętowego.

Zabezpieczeniem, które **działa**, jest [`Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp) na poziomie aplikacji (5 min bez sukcesu → test AT → hard reset modemu → `esp_restart()`). Dokumentacja w [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md) opisuje jednak TWDT jako aktywny mechanizm ochrony `loop()` — to jest rozjazd dokumentacji ze stanem faktycznym.

### 11.3. Niespójności w dokumentacji, potwierdzone przy okazji

Brief B-05 wymienia je jako zadanie do naprawy; ta analiza potwierdza dwie z nich niezależnie:

- **PT-506 / 4-20 mA nie istnieje w kodzie** — brak sterownika, brak `analogRead()`, brak I2C. [`01_hardware.md` §1 i §5](./01_hardware.md) mówią o tym poprawnie („draft"), ale §6 nazywa też SPI/PT100 „draftem", podczas gdy PT100 jest w pełni zaimplementowany ([`PT100Sensor.cpp`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp)) i wpięty w [`main.cpp:96`](../../../firmware/src/main.cpp#L96).
- **Rezystor 250 Ω w §6 wobec 136 Ω gdzie indziej** — nie do rozstrzygnięcia z kodu, bo w kodzie nie ma żadnej obsługi 4-20 mA. `Config.h` nie zawiera ani jednej stałej związanej z ADC.

---

## 12. Do zweryfikowania na fizycznym sprzęcie

Lista wprost do wykonania w ramach przyszłego bring-upu (pozycja E z [§6.2](#62-koszt-pracy)). Żadnej z tych rzeczy **nie da się rozstrzygnąć z kodu ani z dokumentacji**.

| # | Do sprawdzenia | Dlaczego to ważne |
|---|---|---|
| 1 | Czas `mbedtls_ecp_gen_key(SECP256R1)` na WROOM-32, w ms | Jedyna liczba w [§4.3.3](#433-bezwzględne-czasy--co-wiadomo-a-czego-nie), która jest przypuszczeniem. Zmierzyć też na S3, żeby mieć porównanie. |
| 2 | Czas `mbedtls_ecdsa_write_signature` na WROOM-32, w ms | j.w. |
| 3 | Czy `RTC_DATA_ATTR` przeżywa `esp_restart()` na WROOM-32 | [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md) sam sygnalizuje wątpliwość („variant ESP32 issue"). Dotyczy licznika restartów w [`Watchdog`](../../../firmware/lib/Watchdog/src/Watchdog.cpp). |
| 4 | Czy MAX31865 działa na nowej mapie SPI (18/19/23/5) | Zmiana z pinów niestandardowych na natywne VSPI — teoretycznie prostsza, praktycznie do potwierdzenia. |
| 5 | Czy GPIO 5 jako CS nie powoduje fałszywych transakcji przy starcie | Uzasadnienie w [§4.1.3](#413-proponowana-mapa-pinów) jest teoretyczne. Alternatywa GPIO 32 gotowa. |
| 6 | Czy modem nie resetuje się przy starcie ESP32 na nowym pinie RESET (25) | Powód przeniesienia z GPIO 5. Sprawdzić oscyloskopem albo po logach modemu. |
| 7 | Czy płytka docelowa ma diodę użytkownika na GPIO 2 | Oryginał Espressif prawdopodobnie nie ma — [§4.2.4](#424-rozstrzygnięcie). |
| 8 | Rewizja krzemu modułu WROOM-32E (v3.0+?) | Warunek dostępności Secure Boot V2 — [§4.3.5](#435-co-realnie-traci-się-w-warstwie-bezpieczeństwa). |
| 9 | Stabilność zasilania: modem 5 V / 2 A przy płytce WROOM | Uwaga krytyczna z [`01_hardware.md` §7](./01_hardware.md) dotyczy obu wariantów, ale rozkład masy i długość przewodów się zmieniają. |

---

## 13. Źródła

**Repozytorium (stan `43116cd`):** [`Config.h`](../../../firmware/include/Config.h), [`main.cpp`](../../../firmware/src/main.cpp), [`platformio.ini`](../../../firmware/platformio.ini), [`StatusLed.cpp`](../../../firmware/lib/StatusLed/src/StatusLed.cpp), [`DeviceIdentity.cpp`](../../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp), [`TelemetryPayload.h`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h), [`PT100Sensor.cpp`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp), [`Watchdog.cpp`](../../../firmware/lib/Watchdog/src/Watchdog.cpp), [`prebuild.py`](../../../firmware/scripts/prebuild.py), [`01_hardware.md`](./01_hardware.md), [`03_esp32_reset_and_recovery.md`](./03_esp32_reset_and_recovery.md), [`01_plan_biznesowy.md`](../../business/01_plan_biznesowy.md).

**Espressif — dokumentacja (dostęp 2026-09-05):**
- [ESP-IDF: mbedTLS Support, ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/protocols/mbedtls.html) — akceleracja AES / SHA / MPI, brak opcji ECC
- [ESP-IDF: mbedTLS Support, ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/protocols/mbedtls.html)
- [ESP-IDF: GPIO & RTC GPIO, ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) — GPIO 6–11 / 16–17, GPIO 34–39, piny strapujące
- [ESP-IDF: Digital Signature (DS), ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/ds.html) — „RSA Digital Signature Peripheral"
- [ESP-IDF: Secure Boot V2, ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/secure-boot-v2.html) — „supported on ESP32 (v3.0 onwards)"
- [Espressif Longevity Commitment](https://www.espressif.com/en/products/longevity-commitment) — ESP32 do 2031-01-01, ESP32-S3 do 2033-01-01
- `components/soc/esp32/include/soc/soc_caps.h` i `components/soc/esp32s3/include/soc/soc_caps.h`, gałąź `release/v5.3` — brak `SOC_ECC_SUPPORTED` na obu targetach
- `esp_task_wdt.h` i `sdkconfig.h` z `framework-arduinoespressif32 @ 3.20017.241212` (dostarczone lokalnie z toolchainem)

**Ceny (dostęp 2026-09-05):**
- [Botland — ESP32-S3-DevKitC-1-N8R8, 99,00 zł](https://botland.com.pl/moduly-wifi-i-bt-esp32/26547-esp32-s3-devkitc-1-n8r8-plytka-rozwojowa-wifi-bluetooth-z-ukladem-esp32-s3-wroom-1.html)
- [Botland — ESP32-DevKitC-32E V4, 73,90 zł](https://botland.com.pl/moduly-wifi-i-bt-esp32/8306-esp32-devkitc-32e-v4-wifi-bt-42-platforma-z-modulem-esp-wroom-32e-5904422336394.html)
- [Botland — ESP32 DevKit zgodny (ESP-WROOM-32), 49,90 zł](https://botland.com.pl/moduly-wifi-i-bt-esp32/8893-esp32-wifi-bt-42-platforma-z-modulem-esp-wroom-32-zgodna-z-esp32-devkit-5904422337438.html)
- [Botland — moduł ESP32-WROOM-32E SMD 4 MB, 16,90 zł](https://botland.com.pl/moduly-wifi-i-bt-esp32/20509-uklad-wifi-bluetooth-ble-espressif-esp32-wroom-32e-smd-32-mbit-4-mb-flash-5904422381417.html)
- [Kamami — moduł ESP-WROOM-32, 38,93 zł](https://kamami.pl/esp32/563420-modul-wifi-i-bluetooth-esp-wroom-32-5902186312623.html)

**Sterowniki przemysłowe DIN:**
- [Industrial Shields — ESP32 PLC (rodzina)](https://www.industrialshields.com/industrial-hardware-solutions-based-on-esp32) — ESP-WROOM-32U
- [CNX Software — Industrial Shields ESP32 PLC 14 (99,95 EUR)](https://www.cnx-software.com/2024/01/26/entry-level-industrial-shields-esp32-plc-14/)
- [CNX Software — NORVI IIOT (ESP32-WROOM-32)](https://www.cnx-software.com/2019/12/17/norvii-iiot-esp32-industrial-controller-comes-with-built-in-oled-or-tft-display-din-rail-mount/)
- [Kincony — KC868-A16v3 (ESP32-S3-WROOM-1U)](https://www.kincony.com/kincony-kc868-a16v3-esp32-s3-gpio-module-released.html)

**Wydajność (źródła wtórne, nie Espressif — oznaczone jako takie w tekście):**
- [PCBway — ESP32 vs ESP32-S3](https://www.pcbway.com/blog/14/ESP32_vs_ESP32_S3_Key_Differences_Performance_Comparison_and_PCB_Design_Consi_2c205f9a.html) — CoreMark 991,10 vs 1181,60
- [Forum ESP32 — „Signature verify seems SLOW with ECDSA and mbedtls"](https://esp32.com/viewtopic.php?t=25628) — pomiary weryfikacji podpisu P-256 na ESP32

---

## 14. Zastrzeżenia

- **Ceny są migawką z jednego dnia** (2026-09-05) i z detalicznego kanału sprzedaży. Przy zamówieniu produkcyjnym relacje mogą się zmienić — ale musiałyby zmienić się o rząd wielkości, żeby odwrócić werdykt.
- **Nakład pracy 20–30 h to szacunek**, nie oferta. Pozycja „bring-up sprzętowy" jest z natury nieprzewidywalna i historycznie bywa przekraczana.
- **Stawka godzinowa nie jest w tym dokumencie założona** — progi podano jako funkcję stawki, żeby czytelnik podstawił własną.
- **Nic nie zweryfikowano na fizycznej płytce.** Wszystkie wnioski o zachowaniu sprzętu są wnioskami z dokumentacji i z kodu.
