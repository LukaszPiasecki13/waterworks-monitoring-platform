# PT100 — czujnik temperatury przez MAX31865

> **Status sprzętu: zweryfikowane na sprzęcie 2026-08-24** — odczyt rzeczywistej temperatury z PT100
> potwierdzony na fizycznej płytce, detekcja błędów MAX31865 działająca.
> **Uzgodnione z kodem: 2026-09-03** — sekcje 3, 4, 5 i 7 opisywały API sprzed refaktoru na interfejs
> `ISensor` i zostały przepisane.

## Krótko

ESP32-S3 odczytuje temperaturę z czujnika PT100 (RTD) przez konwerter MAX31865 na magistrali **SPI**.
Odczyt jest wykonywany co `SAMPLE_INTERVAL_MS` = **15 s**, a paczka telemetryczna z czterema oknami
wychodzi na backend co ok. 60 s, z typem punktu `temperature` i jednostką `°C`.

Kod czujnika: [`lib/Sensor/src/PT100Sensor.cpp`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp),
za interfejsem [`ISensor`](../../../firmware/lib/Sensor/include/ISensor.h).

---

## 1. Sprzęt

### Czujnik PT100

- **Typ**: RTD (Resistance Temperature Detector), platynowy
- **Rezystancja @ 0 °C**: 100 Ω (klasa B wg IEC 60751)
- **Zmiana rezystancji**: ~0,385 Ω/°C
- **Konfiguracja**: 3-przewodowa (`MAX31865_3WIRE`)

**Sprostowanie:** wcześniejsza wersja tego dokumentu podawała „zakres pomiarowy firmware'u: -10 °C do
+100 °C". **W firmware nie ma żadnej kontroli zakresu** — `PT100Sensor::read()` zwraca to, co wyliczy
biblioteka, bez sprawdzania widełek. Kod błędu `SENSOR_OUT_OF_RANGE` z
[`sensor_registry.yaml`](../../../sensor_registry.yaml) nie jest przez firmware nigdy generowany.
Przedział -10…+100 °C występuje wyłącznie jako asercja w teście jednostkowym
([`test_telemetry_pt100.cpp:96`](../../../firmware/test/test_telemetry_pt100.cpp#L96)), nie w kodzie
produkcyjnym.

### Konwerter MAX31865

- **Interfejs**: SPI 4-przewodowe
- **Rozdzielczość**: 15-bit
- **Dokładność**: ±0,3 °C typ. (z PT100 3-przewodowym)
- **Napięcie zasilania**: 3,3 V
- **Pobór prądu**: ~10 mA typ.
- **Biblioteka**: `adafruit/Adafruit MAX31865 library @ ^1.3.0`
  ([`platformio.ini:15`](../../../firmware/platformio.ini#L15))

---

## 2. Podłączenie

### Piny SPI

| Sygnał | ESP32-S3 GPIO | MAX31865 | Stała w `Config.h` |
|---|---|---|---|
| **MOSI** | GPIO 11 | SDI | `PT100_SPI_MOSI` |
| **MISO** | GPIO 13 | SDO | `PT100_SPI_MISO` |
| **SCK** | GPIO 12 | CLK | `PT100_SPI_SCK` |
| **CS** | GPIO 14 | CS | `PT100_SPI_CS` |
| **GND** | GND | GND | — |
| **3,3 V** | 3V3 | VIN | — |

Piny są przekazywane jawnie do `SPI.begin(sck, miso, mosi, cs)` w
[`PT100Sensor::init()`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp#L14) — nie polegamy na
domyślnych wartościach frameworku. Schemat graficzny:
[`00_przeglad.md §4`](./00_przeglad.md#4-schemat-połączeń).

### PT100 → MAX31865 (wejścia RTD)

Moduł MAX31865 ma **cztery zaciski wejściowe**: `F+`, `RTD+`, `RTD-`, `F-`.

Dla czujnika 3-przewodowego: zmierz multimetrem, które dwa z trzech przewodów PT100 są ze sobą
wewnętrznie połączone (rezystancja ~0–2 Ω) — to jest para sparowana.

| Przewód PT100 | Zacisk MAX31865 | Opis |
|---|---|---|
| Sparowany #1 | F+ | Para zwarta wewnętrznie w czujniku |
| Sparowany #2 | RTD+ | Para zwarta wewnętrznie w czujniku |
| Trzeci (pojedynczy) | RTD- | Przewód po drugiej stronie elementu RTD |

Większość modułów MAX31865 (poza oryginalnym Adafruit) ma zworkę **„2/3W"** obok zacisków — dla
czujnika 3-przewodowego musi być zwarta. Pozycja H-6 na liście
[„do sprawdzenia na sprzęcie"](./00_przeglad.md#9-do-sprawdzenia-na-sprzęcie).

```
[PT100, 3 przewody]
  ├─ sparowany #1 ──→ MAX31865 F+
  ├─ sparowany #2 ──→ MAX31865 RTD+
  └─ pojedynczy   ──→ MAX31865 RTD-

[MAX31865]
  ├─ SDI  ──→ ESP32-S3 GPIO 11
  ├─ SDO  ──→ ESP32-S3 GPIO 13
  ├─ CLK  ──→ ESP32-S3 GPIO 12
  ├─ CS   ──→ ESP32-S3 GPIO 14
  ├─ GND  ──→ ESP32-S3 GND
  └─ VIN  ──→ ESP32-S3 3V3
```

---

## 3. Kod firmware

Od refaktoru czujnik jest samodzielną klasą za interfejsem `ISensor`.
**`TelemetryPayload` nie zna już MAX31865** — dostaje listę wskaźników `ISensor*` i tyle. Wcześniejsza
wersja tego dokumentu pokazywała metodę `TelemetryPayload::readPT100Temperature()`; **taka metoda nie
istnieje**.

### Kontrakt `ISensor`

```cpp
struct SensorReading {
  bool ok;
  float value;
  const char* errorCode;  // nullptr gdy ok
};

class ISensor {
 public:
  virtual bool init() = 0;
  virtual SensorReading read() = 0;
  virtual const char* pointId() const = 0;    // "pt100_temperature"
  virtual const char* pointType() const = 0;  // "temperature"
  virtual const char* unit() const = 0;       // "°C"
  virtual const char* getTag() const = 0;     // "[PT100]"
};
```

### Walidacja w czasie kompilacji

`PT100Sensor.cpp` sprawdza swoje stałe wobec wygenerowanego rejestru, jeszcze zanim powstanie binarka:

```cpp
static_assert(SensorRegistry::isValidPointType("temperature"), ...);
static_assert(SensorRegistry::isValidErrorCode("SENSOR_FAULT_HW"), ...);
```

`SensorRegistry.h` jest generowany przed każdym budowaniem z
[`sensor_registry.yaml`](../../../sensor_registry.yaml) przez
[`scripts/prebuild.py`](../../../firmware/scripts/prebuild.py) — plik nie jest wersjonowany, powstaje
przy `pio run`. Literówka w nazwie typu albo kodu błędu zatrzymuje kompilację.

### Inicjalizacja

```cpp
bool PT100Sensor::init() {
  SPI.begin(PT100_SPI_SCK, PT100_SPI_MISO, PT100_SPI_MOSI, cs_pin_);
  if (pt100_.begin(MAX31865_3WIRE)) {
    LOG_INFO("[PT100]", "Initialized");
    return true;
  }
  LOG_ERROR("[PT100]", "Initialization failed!");
  return false;
}
```

`init()` jest wołane **z konstruktora `TelemetryPayload`**, dla każdego czujnika z listy
([`TelemetryPayload.cpp:9-13`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp#L9-L13)),
a nie bezpośrednio z `main.cpp`. Nieudana inicjalizacja jest tylko logowana — czujnik zostaje na
liście i będzie odpytywany mimo to.

### Odczyt

```cpp
SensorReading PT100Sensor::read() {
  uint16_t rtd = pt100_.readRTD();
  float temp = pt100_.calculateTemperature(rtd, RTD_NOMINAL_OHMS, REF_RESISTOR_OHMS);

  uint8_t fault = pt100_.readFault();
  if (fault) {
    LOG_ERROR("[PT100]", "Fault 0x%02X", fault);
    // ... rozbicie bitów rejestru błędów na osobne linie logu ...
    pt100_.clearFault();
    return { .ok = false, .value = 0.0f, .errorCode = "SENSOR_FAULT_HW" };
  }

  LOG_INFO("[PT100]", "Temperature: %.2f°C", temp);
  return { .ok = true, .value = temp, .errorCode = nullptr };
}
```

Stałe kalibracyjne są polami klasy, nie parametrami z `Config.h`
([`PT100Sensor.h:21-22`](../../../firmware/lib/Sensor/src/PT100Sensor.h#L21-L22)):

- `RTD_NOMINAL_OHMS` = 100,0 Ω — rezystancja PT100 przy 0 °C wg IEC 60751
- `REF_RESISTOR_OHMS` = 430,0 Ω — rezystor odniesienia na module MAX31865

Konwersję rezystancja → temperatura robi formuła **Callendar–Van Dusen** wewnątrz biblioteki Adafruit.
Rejestr błędów jest odczytywany po każdym pomiarze — to daje konkretną diagnozę (przerwa w obwodzie,
przekroczenie napięcia) zamiast zgadywania z nietypowej wartości -242 °C.

### Ścieżka do payloadu

```
TelemetrySender::update()  →  TelemetryPayload::sample(utcMs)  →  PT100Sensor::read()
                              zapis {sensor, reading} do okna w buforze RAM
                              ↓ po czterech oknach
                              TelemetryPayload::build(seq)  →  JSON
```

W [`build()`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp#L83-L94) odczyt udany
trafia do tablicy `points` jako **pojedyncze `value`** — bez `avg`, `min` ani `max`. Wcześniejsza
wersja tego dokumentu pokazywała `min`/`max` liczone jako `temperature ∓ 0.5`; tego kodu już nie ma.

Odczyt nieudany **nie trafia** do `points` — zamiast tego dopisywany jest wpis do tablicy `errors`.
Tu kryje się usterka: dopisywany kod to `SENSOR_FAULT` z `severity: "error"`, podczas gdy rejestr zna
`SENSOR_FAULT_HW`, a backend przyjmuje wyłącznie `info`/`warning`/`critical`. Kod błędu zwrócony przez
sam czujnik jest w tym miejscu gubiony. Skutek: backend odrzuca całą paczkę. Opis: usterka U-2 w
[`00_przeglad.md §10`](./00_przeglad.md#10-usterki-w-kodzie-znalezione-przy-uzgadnianiu-dokumentacji).

---

## 4. Payload wysyłany do backendu

Paczka `v: 2` z czterema oknami po 15 s (poniżej skrócona do jednego okna):

```json
{
  "v": 2,
  "device_id": "WW-3CDC756F6DC0",
  "seq": 1787497190,
  "sent_at": "2026-08-24T14:30:00.000Z",
  "windows": [
    {
      "window_start": "2026-08-24T14:30:00.000Z",
      "window_seconds": 15,
      "points": [
        {
          "point_id": "pt100_temperature",
          "type": "temperature",
          "unit": "°C",
          "quality": "good",
          "value": 22.45
        }
      ]
    }
  ]
}
```

`quality` jest dziś stałą `"good"` dla każdego udanego odczytu — nie ma stopniowania jakości.

---

## 5. Logi na porcie szeregowym

Format ustala [`Logger.h`](../../../firmware/lib/Logger/include/Logger.h): `[millis][POZIOM][TAG] treść`.
Domyślny próg to `LOG_INFO` ([`platformio.ini:21`](../../../firmware/platformio.ini#L21)).

### Przy starcie

```
[1240][INFO][BOOT] Initializing DeviceIdentity...
[1310][INFO][BOOT] DeviceIdentity initialized
[4820][INFO][MODEM] Init OK
[8110][INFO][PT100] Initialized
[8115][INFO][BOOT] Sensors initialized
[8230][INFO][BOOT] Ready
```

### W normalnej pracy

```
[68230][INFO][PT100] Temperature: 22.45°C
[83240][INFO][PT100] Temperature: 22.48°C
[98250][INFO][PT100] Temperature: 22.44°C
[113260][INFO][PT100] Temperature: 22.51°C
[113310][INFO][DATA] Payload: {"v":2,"device_id":"WW-...","seq":1787497190,...}
[114980][INFO][LOOP] Send OK, seq=1787497190
```

Cztery odczyty co 15 s, po nich jedna wysyłka — to jest wzorzec, którego szuka się w logu przy
diagnostyce.

### Błędy

**Nieudana inicjalizacja** (brak komunikacji SPI z MAX31865):
```
[8110][ERROR][PT100] Initialization failed!
```

**Przerwa w obwodzie RTD** (czujnik odłączony):
```
[68230][ERROR][PT100] Fault 0x08
[68231][ERROR][PT100] RTDIN- < 0.85 x Bias
```

**Problem z napięciem bias / okablowaniem:**
```
[68230][ERROR][PT100] Fault 0x20
[68231][ERROR][PT100] REFIN- > 0.85 x Bias
```

**Przekroczenie napięcia zasilania:**
```
[68230][ERROR][PT100] Fault 0x04
[68231][ERROR][PT100] Under/Over voltage
```

Po każdym błędzie rejestr jest czyszczony (`clearFault()`), a odczyt wraca jako nieudany —
w tym cyklu nie ma wartości temperatury w payloadzie.

---

## 6. Kalibracja

PT100 pracuje bez programowej kalibracji dwupunktowej — zakładamy kalibrację fabryczną czujnika.

**Parametry:**
- `RTD_NOMINAL_OHMS` = 100,0 Ω (IEC 60751)
- `REF_RESISTOR_OHMS` = 430,0 Ω

**Uwaga praktyczna:** część modułów MAX31865 dostępnych na rynku ma rezystor odniesienia **400 Ω**,
nie 430 Ω. Przy takim module stała w kodzie daje stały błąd temperatury rzędu kilku stopni. Wartość
rezystora warto zmierzyć na module przed pierwszym uruchomieniem — pozycja H-7 na liście
[„do sprawdzenia na sprzęcie"](./00_przeglad.md#9-do-sprawdzenia-na-sprzęcie).

Jeśli dokładność okaże się niewystarczająca, kalibracja dwupunktowa jest naturalnym następnym krokiem
(§9).

---

## 7. Testy

### Firmware — środowisko `native` + googletest

| Plik | Co sprawdza | Uwagi |
|---|---|---|
| [`test_isensor_pt100.cpp`](../../../firmware/test/test_isensor_pt100.cpp) | Kontrakt `ISensor` na klasie `PT100Sensor`: `pointId()`, `pointType()`, `unit()`, `getTag()`, kształt `SensorReading`, konstruktor z pinem CS | Testuje faktyczną klasę produkcyjną |
| [`test_telemetry_pt100.cpp`](../../../firmware/test/test_telemetry_pt100.cpp) | Formuła Callendar–Van Dusen na atrapie MAX31865 oraz struktura JSON payloadu | **Nie testuje `TelemetryPayload`.** Buduje własny dokument JSON z `v: 1`, oknem 30 s i polami `min`/`max` — czyli kształt, którego kod produkcyjny już nie wytwarza |

Druga pozycja jest **przestarzała względem kodu** i przy najbliższej pracy nad testami firmware powinna
zostać przepisana na rzeczywisty `TelemetryPayload::build()`. Odnotowane tu, żeby zielone testy nie
były mylone z potwierdzeniem, że payload ma właściwy kształt.

Uruchomienie: `pio test -e native`.

### Backend — test integracyjny

[`test_ingest_api.py::test_ingest_accepts_temperature_measurement`](../../../backend/app/modules/telemetry/tests/test_ingest_api.py)
— `POST /telemetry/ingest` z paczką zawierającą punkt `temperature` kończy się przyjęciem i zapisem
do bazy.

---

## 8. Troubleshooting

### Inicjalizacja i SPI

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| `[PT100] Initialization failed!` | MAX31865 nie odpowiada na SPI | Sprawdź okablowanie: MOSI=GPIO11, MISO=GPIO13, SCK=GPIO12, CS=GPIO14; upewnij się, że VIN (3,3 V) i GND są podłączone |
| Brak linii `[PT100] Initialized` | Firmware nie wystartował albo urządzenie nie zaprogramowane | Sprawdź, czy binarka została wgrana; obejrzyj monitor szeregowy od resetu |
| Śmieci na porcie szeregowym | Niezgodna prędkość transmisji | Ustaw monitor na **115200 baud**; sprawdź kabel USB |

### Kody błędów (rejestr MAX31865)

| Kod | Bit | Znaczenie | Przyczyna | Rozwiązanie |
|---|---|---|---|---|
| `0x08` | RTDINLOW | RTD Input Low | Czujnik odłączony lub przerwa w obwodzie | Sprawdź okablowanie PT100 (F+, RTD+, RTD-); zmierz rezystancję czujnika (~100 Ω przy pokojowej) |
| `0x20` | REFINLOW | Problem z napięciem bias | Zaburzenie źródła bias lub błąd okablowania | Sprawdź zasilanie 3,3 V; sprawdź ciągłość przewodów RTD |
| `0x10` | REFINHIGH | Problem z napięciem bias (drugi kierunek) | jw. | Sprawdź, czy żaden przewód RTD nie jest zwarty |
| `0x04` | OVUV | Przekroczenie napięcia | Problem z zasilaniem 3,3 V modułu | Sprawdź wydajność prądową 3,3 V i kondensatory na module |
| `0x80` | HIGHTHRESH | Przekroczony próg górny | Temperatura powyżej progu w rejestrze | Jeśli czujnik jest w gorącym medium — normalne; inaczej sprawdź czujnik |
| `0x40` | LOWTHRESH | Przekroczony próg dolny | Temperatura poniżej progu | jw. |

Wszystkie te przypadki dają ten sam efekt w telemetrii: odczyt nieudany, brak punktu w payloadzie
i wpis w `errors` — z zastrzeżeniem z usterki U-2.

### Wartości temperatury

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| `-242,02 °C` bez zgłoszonego błędu | MAX31865 zwraca surową wartość ~0, formuła CVD daje wartość skrajną | Sprawdź, czy `readFault()` naprawdę zwraca `0x00`; jeśli tak — problem z okablowaniem RTD+/RTD-/F+ |
| Szum ±2–3 °C | Normalny szum przetwornika przy słabym pobudzeniu | Uśrednianie kilku odczytów (§9) |
| Stały offset temperatury | Rezystor odniesienia inny niż 430 Ω albo rozkalibrowany czujnik | Zmierz rezystor odniesienia na module; przy 400 Ω popraw `REF_RESISTOR_OHMS` |
| Brak jakichkolwiek pomiarów mimo poprawnych logów `[PT100]` | Brak zsynchronizowanego czasu albo brak ważnego tokenu — `TelemetrySender` wychodzi przed wysyłką | Zob. [`00_przeglad.md §8.1`](./00_przeglad.md#81-gdzie-dane-mogą-zginąć), punkty U-C i U-D |

---

## 9. Możliwe ulepszenia

1. **Uśrednianie** — okno ostatnich N odczytów zamiast pojedynczego pomiaru (zmniejsza szum).
   Naturalnie łączy się z wypełnieniem pól `avg`/`min`/`max`, które payload dopuszcza, a firmware
   dziś nie używa.
2. **Kontrola zakresu** — sprawdzenie widełek i zgłaszanie `SENSOR_OUT_OF_RANGE`; dziś ten kod błędu
   istnieje w rejestrze, ale nie ma w firmware nikogo, kto by go wystawił.
3. **Kalibracja dwupunktowa** — na podstawie dwóch znanych temperatur, ze stałymi w NVS.
4. **Wiele czujników PT100** — po jednym CS na czujnik, wspólna magistrala SPI. Interfejs `ISensor`
   jest już na to gotowy; trzeba tylko nadać różne `pointId()`.

---

## 10. Referencje

- **Biblioteka Adafruit MAX31865**: https://github.com/adafruit/Adafruit_MAX31865
- **Nota katalogowa MAX31865**: https://www.analog.com/en/products/max31865.html (Maxim Integrated został przejęty przez Analog Devices — stare odnośniki `datasheets.maximintegrated.com` przekierowują tutaj)
- **PT100 wg IEC 60751** — norma definiująca charakterystykę czujników platynowych
- **Mapa sprzętowa**: [`01_hardware.md`](./01_hardware.md)
- **Schematy i przegląd**: [`00_przeglad.md`](./00_przeglad.md)
- **Instrukcja montażu**: [`07_montaz_krok_po_kroku.md`](./07_montaz_krok_po_kroku.md)
- **Dodawanie kolejnych czujników**: [`06_adding_sensors.md`](./06_adding_sensors.md)
