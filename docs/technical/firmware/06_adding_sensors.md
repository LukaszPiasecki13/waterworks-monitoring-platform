# Dodawanie nowych czujników do systemu telemetrii

> Czujniki są zarejestrowane globalnie w [`sensor_registry.yaml`](../../../sensor_registry.yaml)
> (katalog główny repozytorium), a każdy jest implementacją interfejsu
> [`ISensor`](../../../firmware/lib/Sensor/include/ISensor.h).
> Wzór do skopiowania: [`PT100Sensor`](../../../firmware/lib/Sensor/src/PT100Sensor.cpp).
>
> **Uzgodnione z kodem: 2026-09-03.**

## 1. Zarejestruj typ punktu pomiarowego

Edytuj [`sensor_registry.yaml`](../../../sensor_registry.yaml) — dodaj wpis w sekcji `point_types`:

```yaml
point_types:
  # ... istniejące ...
  - id: new_sensor_type
    canonical_unit: "unit_symbol"
    description: "Krótki opis tego, co czujnik mierzy"
```

**Ten plik jest jedynym źródłem prawdy dla obu stron systemu:**

- **backend** wczytuje go w czasie działania
  ([`registry.py`](../../../backend/app/modules/core_data/registry.py) — `REGISTRY_PATH` wskazuje na
  katalog główny repozytorium) i odrzuca payloady z nieznanym kodem błędu;
- **firmware** dostaje go w postaci wygenerowanego nagłówka z osadzonym JSON-em i walidatorami
  `constexpr`.

Jeśli typ punktu już istnieje w rejestrze (np. dokładasz drugi czujnik temperatury), ten krok pomijasz.

## 2. Zbuduj firmware — nagłówek generuje się sam

```bash
cd firmware
pio run
```

Hook przed budowaniem ([`scripts/prebuild.py`](../../../firmware/scripts/prebuild.py), podpięty przez
`extra_scripts` w [`platformio.ini:7`](../../../firmware/platformio.ini#L7)) wykonuje dwa kroki:

1. **Generuje** `firmware/include/SensorRegistry.h` z YAML-a
   ([`generate_sensor_registry.py`](../../../firmware/scripts/generate_sensor_registry.py)) —
   osadzony JSON, `SCHEMA_VERSION` oraz `constexpr` walidatory `isValidPointType()` i
   `isValidErrorCode()`.
2. **Weryfikuje**, że wygenerowany nagłówek i YAML mają zgodne `schema_version`, listę typów punktów
   i listę kodów błędów. Rozjazd zatrzymuje budowanie.

`SensorRegistry.h` **nie jest wersjonowany w repozytorium** — powstaje przy każdym budowaniu. Nie
edytuj go ręcznie; nadpisze się przy najbliższym `pio run`.

## 3. Zaimplementuj czujnik

Nowa biblioteka w `firmware/lib/`, zgodnie z układem katalogów PlatformIO (`lib/<Nazwa>/src/`):

```cpp
// firmware/lib/NewSensor/src/NewSensor.h
#pragma once

#include "ISensor.h"

class NewSensor : public ISensor {
 public:
  explicit NewSensor(uint8_t pin);

  bool init() override;
  SensorReading read() override;
  const char* pointId() const override;
  const char* pointType() const override;
  const char* unit() const override;
  const char* getTag() const override;

 private:
  uint8_t pin_;
};
```

```cpp
// firmware/lib/NewSensor/src/NewSensor.cpp
#include <Arduino.h>
#include "NewSensor.h"
#include <Logger.h>
#include <SensorRegistry.h>

// Walidacja w czasie kompilacji — literówka zatrzyma budowanie
static_assert(SensorRegistry::isValidPointType("new_sensor_type"),
              "ERROR: 'new_sensor_type' nie jest zarejestrowany w SensorRegistry");
static_assert(SensorRegistry::isValidErrorCode("SENSOR_READ_FAILED"),
              "ERROR: 'SENSOR_READ_FAILED' nie jest zarejestrowany w SensorRegistry");

NewSensor::NewSensor(uint8_t pin) : pin_(pin) {}

// Zaślepki do zastąpienia własną obsługą magistrali i skalowaniem
static bool readRaw(int* out) { *out = analogRead(/* pin */ 0); return true; }
static float convertRawToPhysical(int raw) { return raw * 0.01f; }

bool NewSensor::init() {
  pinMode(pin_, INPUT);
  LOG_INFO("[NEW]", "Initialized on pin %d", pin_);
  return true;
}

SensorReading NewSensor::read() {
  SensorReading result;

  int raw = 0;
  if (!readRaw(&raw)) {  // odczyt specyficzny dla czujnika: SPI, I²C, ADC…
    LOG_ERROR("[NEW]", "Read failed");
    result.ok = false;
    result.value = 0.0f;
    result.errorCode = "SENSOR_READ_FAILED";
    return result;
  }

  float value = convertRawToPhysical(raw);
  LOG_INFO("[NEW]", "Read: %.2f", value);
  result.ok = true;
  result.value = value;
  result.errorCode = nullptr;
  return result;
}

const char* NewSensor::pointId() const { return "new_sensor_instance_id"; }
const char* NewSensor::pointType() const { return "new_sensor_type"; }
const char* NewSensor::unit() const { return "unit_symbol"; }
const char* NewSensor::getTag() const { return "[NEW]"; }
```

Kontrakt `read()`:

| Sytuacja | Zwróć |
|---|---|
| Odczyt udany | `ok = true`, `value = <wartość>`, `errorCode = nullptr` |
| Nie udało się odczytać | `ok = false`, `value = 0.0f`, `errorCode = "SENSOR_READ_FAILED"` |
| Awaria sprzętowa (przerwa w obwodzie, bity błędu przetwornika) | `ok = false`, `value = 0.0f`, `errorCode = "SENSOR_FAULT_HW"` |
| Wartość poza zakresem sprzętowym | `ok = false`, `value = 0.0f`, `errorCode = "SENSOR_OUT_OF_RANGE"` |

**`errorCode` musi być stałą łańcuchową z rejestru** — czas życia wskaźnika ma sięgać co najmniej do
`acknowledge()`, a wartość musi przejść walidację po stronie backendu. Nie twórz własnych kodów;
jeśli potrzebujesz nowego, dopisz go najpierw do `error_codes` w YAML-u.

> ⚠️ **Zanim polegniesz na ścieżce błędu:** dziś `TelemetryPayload::build()` **ignoruje `errorCode`
> zwrócony przez czujnik** i dopisuje własny, nieistniejący w rejestrze kod `SENSOR_FAULT` z
> niedozwoloną wartością `severity`. Backend odrzuca wtedy całą paczkę. To usterka U-2 —
> [`00_przeglad.md §10`](./00_przeglad.md#10-usterki-w-kodzie-znalezione-przy-uzgadnianiu-dokumentacji).
> Dopóki nie jest naprawiona, **awaria dowolnego czujnika zatrzymuje telemetrię całego urządzenia**.

## 4. Dodaj czujnik do listy na starcie

Edytuj [`firmware/src/main.cpp`](../../../firmware/src/main.cpp) — funkcja `initializeSensors()`:

```cpp
void initializeSensors() {
  if (sensors.empty()) {
    sensors.push_back(new PT100Sensor(PT100_SPI_CS));
    sensors.push_back(new NewSensor(NEW_SENSOR_PIN));  // ← TUTAJ
    LOG_INFO("[BOOT]", "Sensors initialized");
  }
}
```

Numer pinu **zdefiniuj w [`Config.h`](../../../firmware/include/Config.h)**, nie wpisuj go wprost w
`main.cpp` — `Config.h` jest źródłem prawdy dla przypisania GPIO, a
[`01_hardware.md`](./01_hardware.md) ma być z nim zgodny. Przed wyborem pinu sprawdź listę pinów
zajętych i ryzykownych: [`01_hardware.md §5`](./01_hardware.md#5-piny-zajęte-i-ryzykowne).

**Kto woła `init()`:** nie `main.cpp`, tylko konstruktor
[`TelemetryPayload`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp#L9-L13), dla
każdego czujnika z listy. Nieudana inicjalizacja jest wyłącznie logowana — czujnik zostaje na liście
i będzie odpytywany mimo to.

## 5. Zbuduj, przetestuj, wgraj

```bash
cd firmware
pio test -e native          # testy jednostkowe na hoście
pio run                     # kompilacja na ESP32-S3 (generuje SensorRegistry.h)
pio run --target upload
pio device monitor -b 115200
```

Czego szukać w logu:

- `[NEW] Initialized on pin X` — jednorazowo, przy inicjalizacji telemetrii
- `[NEW] Read: X.XX` — co `SAMPLE_INTERVAL_MS` (15 s)
- `[DATA] Payload: {...}` z nowym `point_id` — co ok. 60 s, po czterech oknach
- `[LOOP] Send OK, seq=...` — potwierdzenie przyjęcia przez backend

Warto dopisać test kontraktu na wzór
[`test_isensor_pt100.cpp`](../../../firmware/test/test_isensor_pt100.cpp) — sprawdza `pointId()`,
`pointType()`, `unit()`, `getTag()` i kształt `SensorReading` bez potrzeby posiadania sprzętu.

## 6. Weryfikacja po stronie backendu

Backend tworzy `MeasurementPoint` automatycznie przy pierwszym pakiecie zawierającym nieznany
`point_id` — z `external_id` równym `point_id` i typem z `type`.

```bash
curl -X GET "http://localhost:8000/api/v1/orgs/{org_id}/measurement_points" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq '.[] | select(.point_type == "new_sensor_type")'
```

Powinien pojawić się wpis z `is_active: true`.

## 7. Uwagi projektowe

**`point_id` a `point_type`.** `point_id` (np. `"pt100_temperature"`) to lokalny identyfikator
**instancji** czujnika na urządzeniu; `type` (np. `"temperature"`) to typ z rejestru globalnego. Dwa
czujniki tego samego typu na jednym urządzeniu muszą mieć różne `point_id` — np. `"temp_zasilanie"` i
`"temp_powrot"`.

**Jednostka.** `unit()` powinno zwracać `canonical_unit` z rejestru dla danego typu. Backend
porównuje typ i jednostkę z już zarejestrowanym punktem pomiarowym i przy rozjeździe odrzuca
**ten punkt** (kod `POINT_TYPE_MISMATCH`), nie całą paczkę.

**Zmiana rejestru wymaga przebudowania firmware.** Nagłówek `SensorRegistry.h` jest generowany przy
budowaniu; urządzenie z wgraną starszą binarką nie zna nowych typów. Hook przed budowaniem to
wychwyci, ale dopiero przy `pio run` — nie w czasie działania urządzenia.

**Koszt w buforze.** Każdy czujnik dokłada jeden odczyt do każdego z 48 okien trzymanych w RAM-ie.
Przy dokładaniu wielu czujników warto zerknąć na `RETAIN_WINDOWS_MAX` w
[`TelemetryPayload.h`](../../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L35).
