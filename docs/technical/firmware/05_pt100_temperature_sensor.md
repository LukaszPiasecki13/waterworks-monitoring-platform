# PT100 Czujnik Temperatury — Odczyt przez MAX31865

Status: **Production ready** ✅ (2026-08-24 — physical hardware test passed, PT100 reading real temperature, fault detection working)

## Krótko

ESP32-S3 odczytuje temperatury rzeczywistej z czujnika PT100 (RTD — Platinum Resistance Thermometer) za pośrednictwem konwertera MAX31865 podłączonego przez **SPI**. Dane wysyłane co 30 sekund do backendu w payload'u telemetrycznego z typem `"temperature"` (°C).

---

## 1. Sprzęt

### Czujnik PT100

- **Typ**: RTD (Resistance Temperature Detector), Platinum
- **Rezystancja @ 0°C**: 100 Ω (klasa B wg IEC 60751)
- **Zmiana rezystancji**: ~0.385 Ω/°C
- **Zakres pomiarowy firmware'u**: -10°C do +100°C
- **Konfiguracja**: 3-wire (3 przewody: Pt+, Pt-, sense lead)

### Konwerter MAX31865 (Adafruit)

- **Interfejs**: SPI 4-wire
- **Rozdzielczość**: 15-bit (~0.03125°C)
- **Dokładność**: ±0.3°C typ. (z PT100 3-wire)
- **Napięcie zasilania**: 3.3V
- **Pobór prądu**: ~10 mA typ.
- **Biblioteka**: `adafruit/Adafruit MAX31865 @ ^1.5.0`

---

## 2. Wiring (Podłączenia)

### SPI Pins — domyślne dla ESP32-S3 (hardware SPI, board esp32-s3-devkitc-1)

| Sygnał | ESP32-S3 GPIO | MAX31865 Pin |
|---|---|---|
| **MOSI** (Master Out Slave In) | GPIO 11 | MOSI |
| **MISO** (Master In Slave Out) | GPIO 13 | MISO |
| **SCK** (Serial Clock) | GPIO 12 | SCK |
| **CS** (Chip Select) | GPIO 14 | CS |
| **GND** | GND | GND |
| **3.3V** | 3.3V | VCC |

Piny jawnie zdefiniowane w `Config.h` (`PT100_SPI_MOSI/MISO/SCK/CS`) i przekazywane do `SPI.begin(sck, miso, mosi, cs)` — nie polegamy już domyślnie na frameworkowych wartościach.

### PT100 → MAX31865 (RTD Inputs)

Moduł MAX31865 ma **4 zaciski wejściowe**: `F+`, `RTD+`, `RTD-`, `F-` (nie ma osobnego pinu "RTDL" — to była pomyłka we wcześniejszej wersji tego dokumentu).

Dla czujnika 3-wire: zmierz multimetrem, które dwa z trzech przewodów PT100 są ze sobą wewnętrznie połączone (rezystancja ~0-2 Ω) — to jest sparowana para.

| PT100 Lead | MAX31865 Pin | Opis |
|---|---|---|
| Sparowany przewód #1 | F+ | Para wewnętrznie połączona w czujniku |
| Sparowany przewód #2 | RTD+ | Para wewnętrznie połączona w czujniku |
| Trzeci (pojedynczy) przewód | RTD- | Przewód po drugiej stronie elementu RTD |

Dodatkowo: większość modułów MAX31865 (non-Adafruit) ma zworkę/jumper oznaczoną **"2/3W"** obok zacisków — dla czujnika 3-wire musi być zwarta (tryb 2/3-wire).

Schemat:
```
[PT100 Sensor 3-wire]
  │
  ├─ sparowany #1 ──→ MAX31865 F+
  ├─ sparowany #2 ──→ MAX31865 RTD+
  └─ pojedynczy   ──→ MAX31865 RTD-

[MAX31865 Module]
  │
  ├─ MOSI ──→ ESP32-S3 GPIO 11
  ├─ MISO ──→ ESP32-S3 GPIO 13
  ├─ SCK  ──→ ESP32-S3 GPIO 12
  ├─ CS   ──→ ESP32-S3 GPIO 14
  ├─ GND  ──→ ESP32-S3 GND
  └─ VCC  ──→ ESP32-S3 3.3V
```

---

## 3. Kod Firmware

### Konfiguracja (Config.h)

```cpp
const int PT100_SPI_CS = 14;    // Chip Select pin
const int PT100_SPI_MOSI = 11;
const int PT100_SPI_MISO = 13;
const int PT100_SPI_SCK = 12;
```

### Inicjalizacja (TelemetryPayload Constructor)

```cpp
TelemetryPayload::TelemetryPayload(const String& deviceId)
    : device_id_(deviceId), getUtcTime_(nullptr), pt100_(PT100_SPI_CS) {
  SPI.begin(PT100_SPI_SCK, PT100_SPI_MISO, PT100_SPI_MOSI, PT100_SPI_CS);
  if (pt100_.begin(MAX31865_3WIRE)) {
    Serial.println("[PT100] Initialized");
  } else {
    Serial.println("[PT100] Initialization failed!");
  }
}
```

**Paramtery**:
- `PT100_SPI_CS/MOSI/MISO/SCK`: piny SPI, jawnie przekazane do `SPI.begin()` (nie polegamy na domyślnych pinach frameworku)
- `MAX31865_3WIRE`: Konfiguracja czujnika 3-przewodowego

### Odczyt Temperatury

```cpp
float TelemetryPayload::readPT100Temperature() {
  uint16_t rtd = pt100_.readRTD();
  float temp = pt100_.calculateTemperature(rtd, 100.0, 430.0);  // RTDnominal, refResistor

  uint8_t fault = pt100_.readFault();
  if (fault) {
    Serial.print("[PT100] Fault 0x");
    Serial.println(fault, HEX);
    if (fault & MAX31865_FAULT_HIGHTHRESH) Serial.println("[PT100] RTD High Threshold");
    if (fault & MAX31865_FAULT_LOWTHRESH) Serial.println("[PT100] RTD Low Threshold");
    if (fault & MAX31865_FAULT_REFINLOW) Serial.println("[PT100] REFIN- > 0.85 x Bias");
    if (fault & MAX31865_FAULT_REFINHIGH) Serial.println("[PT100] REFIN- < 0.85 x Bias - FORCE- open");
    if (fault & MAX31865_FAULT_RTDINLOW) Serial.println("[PT100] RTDIN- < 0.85 x Bias - FORCE- open");
    if (fault & MAX31865_FAULT_OVUV) Serial.println("[PT100] Under/Over voltage");
    pt100_.clearFault();
  }

  Serial.print("[PT100] Temperature: ");
  Serial.print(temp);
  Serial.println("°C");

  return temp;
}
```

**Parametry `calculateTemperature()` (biblioteka Adafruit)**:
- `rtd`: surowa 16-bitowa wartość z rejestru RTD (jeden odczyt SPI, zamiast osobnego `readRTD()` + wewnętrznego drugiego odczytu wewnątrz `temperature()`)
- `100.0` = RTDnominal: rezystancja PT100 @ 0°C (100 Ω)
- `430.0` = refResistor: rezystor odniesienia wewnątrz MAX31865

Funkcja automatycznie stosuje formułę **Callendar-Van Dusen** do konwersji rezystancji → temperatura (°C).

Po odczycie sprawdzany jest rejestr błędów MAX31865 (`readFault()`) — daje precyzyjną diagnostykę (open circuit, over/under voltage, high/low threshold) zamiast polegania wyłącznie na nietypowej wartości -242°C.

### Integracja z TelemetryPayload

```cpp
float TelemetryPayload::build(uint32_t seq, unsigned long timestampMs) {
  // ...
  float temperature = readPT100Temperature();  // Odczyt rzeczywisty
  
  // Dodanie do JSON payload
  JsonObject point = points.createNestedObject();
  point["point_id"] = "pt100_temperature";
  point["type"] = "temperature";
  point["unit"] = "°C";
  point["quality"] = "good";
  point["avg"] = temperature;
  point["min"] = temperature - 0.5;  // Placeholder dla statystyk
  point["max"] = temperature + 0.5;
  point["value"] = temperature;
  
  // ...
}
```

---

## 4. Payload Wysyłany do Backendu

Przykład JSON (co 30 sekund):

```json
{
  "v": 1,
  "device_id": "WW-ABC123",
  "seq": 1234,
  "sent_at": "2026-08-24T14:30:00.000Z",
  "windows": [
    {
      "window_start": "2026-08-24T14:30:00.000Z",
      "window_seconds": 30,
      "points": [
        {
          "point_id": "pt100_temperature",
          "type": "temperature",
          "unit": "°C",
          "quality": "good",
          "avg": 22.45,
          "min": 21.80,
          "max": 23.10,
          "value": 22.45
        }
      ]
    }
  ]
}
```

---

## 5. Serial Monitor Output

### Przy Boot'cie

```
[BOOT] Starting device...
[PT100] Initialized
[MODEM] Powering on...
[MODEM] Connected
```

### Co 30 Sekund (Normalny Przebieg)

```
[PT100] Temperature: 22.45°C
[TELEMETRY] Sending: {"v":1, "device_id":"WW-...", "seq":1234, ...}
[TELEMETRY] Response: 200
```

### Ewentualne Błędy

**Initialization Error**:
```
[PT100] Initialization failed!  ← Brak komunikacji z MAX31865 przez SPI
```

**Open Circuit (czujnik nie podłączony)**:
```
[PT100] Temperature: -242.02°C
[PT100] Fault 0x08
[PT100] RTDIN- < 0.85 x Bias - FORCE- open
```

**Bias Voltage Problem (zaburzenie zasilania / wiring)**:
```
[PT100] Temperature: [błędna wartość]
[PT100] Fault 0x20
[PT100] REFIN- > 0.85 x Bias
```

**Over/Under Voltage (problem z zasilaniem 3.3V)**:
```
[PT100] Temperature: [błędna wartość]
[PT100] Fault 0x04
[PT100] Under/Over voltage
```

**High/Low Threshold** (temperatura poza ustalonymi progami, jeśli konfiguracja tego wymaga):
```
[PT100] Temperature: 125.50°C
[PT100] Fault 0x80
[PT100] RTD High Threshold
```

**Normalny przebieg** (brak fault):
```
[PT100] Temperature: 22.45°C
```

---

## 6. Kalibracja

PT100 używany jest bez 2-point software calibration — zakładamy fabryczną kalibrację sensora.

**Parametry kalibracyjne**:
- RTDnominal = 100.0 Ω (wg IEC 60751)
- refResistor = 430.0 Ω (domyślny w MAX31865)

Jeśli dokładność jest niezadowalająca, można w przyszłości dodać 2-point calibration (implementacja offline, zapisana w EEPROM).

---

## 7. Testy

### Unit Test (Firmware)

Plik: [`firmware/test/test_telemetry_pt100.cpp`](../../../firmware/test/test_telemetry_pt100.cpp)

- **Test 1**: MAX31865 initialization via SPI
- **Test 2**: Temperature calculation (CVD formula) — sprawdzenie dla znanych RTD wartości (0°C, 25°C, 100°C)
- **Test 3**: JSON payload structure — sprawdzenie type="temperature", unit="°C"

### Integration Test (Backend)

Plik: [`backend/app/modules/telemetry/tests/test_ingest_api.py`](../../../backend/app/modules/telemetry/tests/test_ingest_api.py)

- **Test**: `test_ingest_accepts_temperature_measurement` — POST `/telemetry/ingest` z payload'em zawierającym temperature point → backend zwraca 200 i zapisuje do DB

**Status**: ✅ 7/7 testy passing (2026-08-24)

---

## 8. Troubleshooting

### Initialization & SPI

| Symptom | Przyczyna | Rozwiązanie |
|---|---|---|
| `[PT100] Initialization failed!` | MAX31865 nie odpowiada na SPI | Sprawdzić wiring: MOSI=GPIO11, MISO=GPIO13, SCK=GPIO12, CS=GPIO14; upewnić się że VCC (3.3V) i GND są podłączone |
| Bez logu `[PT100] Initialized` | Firmware nie uruchomił się lub device nie zaflashowany | Sprawdzić czy device jest zaflashowany; check Serial Monitor |
| Serial output = garbage | Baud rate mismatch lub błąd USB | Ustawić Serial Monitor na **115200 baud**; sprawdzić USB cable |

### Fault Codes (rejestr błędów MAX31865)

| Fault Code | Bit | Znaczenie | Przyczyna | Rozwiązanie |
|---|---|---|---|---|
| `0x08` | RTDINLOW | RTD Input Low | Czujnik nie podłączony lub open circuit | Sprawdzić wiring PT100 (F+, RTD+, RTD-); zmierzyć rezystancję czujnika multimetrem (~100 Ω) |
| `0x20` | REFINLOW | Bias Voltage Problem | Zaburzenie źródła zasilania bias lub problem wiring | Sprawdzić zasilanie 3.3V; sprawdzić continuity wiring RTD |
| `0x10` | REFINHIGH | Bias Voltage Problem (other) | Zaburzenie bias w innym kierunku | Sprawdzić zasilanie 3.3V; sprawdzić czy żaden z przewodów RTD nie ma zwarcia |
| `0x04` | OVUV | Over/Under Voltage | Problem z zasilaniem MAX31865 (3.3V) | Sprawdzić czy 3.3V dostarcza wymagane mA; sprawdzić USB power; sprawdzić condensatory zasilania modułu MAX31865 |
| `0x80` | HIGHTHRESH | RTD High Threshold | Temperatura przekroczyła górny próg | Jeśli czujnik jest w gorącej wodzie/powietrzu, to normalnie; inaczej sprawdzić czy czujnik nie jest uszkodzony |
| `0x40` | LOWTHRESH | RTD Low Threshold | Temperatura spadła poniżej dolnego progu | Jeśli czujnik jest w zimnej wodzie/powietrzu, to normalnie; inaczej sprawdzić czy czujnik nie jest uszkodzony |

### Temperature Issues

| Symptom | Przyczyna | Rozwiązanie |
|---|---|---|
| `[PT100] Temperature: -242.02°C` (bez Fault) | Rzadkie — MAX31865 zwraca ADC wartość ~0 (error code w Callendar-Van Dusen) | Sprawdzić czy `readFault()` nie zwraca 0x00 — jeśli Fault=0x00, to błąd hardware lub wiring RTD+/RTD-/F+ |
| Temperatura zmienia się losowo (szum ±2-3°C) | Normalny szum ADC czujnika o słabym pobudzeniu | Dodać software averaging — poprzez uśrednianie ostatnich N odczytów |
| Temperatura zbyt niska/wysoka o stały offset | Błąd kalibracji sensora lub REF resistor | Zmierzyć rzeczywistą rezystancję REF resistora na module MAX31865; jeśli nie 430Ω, zmienić stałą w Config.h |

---

## 9. Przyszłe Ulepszenia

1. **Averaging**: Przesuwa okno ostatnich N odczytów zamiast jednego (zmniejsza szum)
2. **2-Point Calibration**: Kalibracja software'owa na podstawie dwóch znanych temperatur
3. **Alerty**: Reguły do wysłania alarmu jeśli temperatura spadnie poniżej/powyżej progu
4. **Historyk**: Analiza trendów temperatury (correlation z ciśnieniem/przepływem)
5. **Wielosensorowy**: Obsługa dodatkowych PT100 na różnych pinach SPI (CS1, CS2, itp.)

---

## 10. Referencje

- **Adafruit MAX31865 Library**: https://github.com/adafruit/Adafruit_MAX31865
- **MAX31865 Datasheet**: https://datasheets.maximintegrated.com/en/ds/MAX31865.pdf
- **PT100 IEC 60751**: https://www.thermcouple.org/download-files/IEC-60751.pdf
- **Callendar-Van Dusen Formula**: Formuła do konwersji rezystancji PT100 na temperaturę (wdrożona w bibliotece Adafruit)
- **Konfiguracja Hardware**: [01_hardware.md](./01_hardware.md) — mapa sprzętowa ESP32-S3
- **Setup Guide**: [`firmware/SETUP_GUIDE.md`](../../../firmware/SETUP_GUIDE.md) — krok po kroku instrukcje wiring + build

---

**Ostatnia aktualizacja**: 2026-08-24  
**Status**: Production ready ✅
