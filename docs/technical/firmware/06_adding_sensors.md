# Dodawanie nowych czujników do systemu telemetrii

> Instrukcja dla firmware v2 i wyższych. Czujniki są zarejestrowane globalnie w [`sensor_registry.yaml`](../../sensor_registry.yaml) (project root), a każdy jest implementacją interfejsu `ISensor`.

## 1. Zarejestuj typ czujnika

Edytuj [`sensor_registry.yaml`](../../sensor_registry.yaml) w project root — dodaj wpis w sekcji `point_types`:

```yaml
point_types:
  # ... istniejące ...
  - id: new_sensor_type
    canonical_unit: "unit_symbol"
    description: "Brief description of what this sensor measures"
```

## 2. Build firmware (auto-generacja)

```bash
cd firmware
pio run
```

Pre-build script automatycznie:
1. Wczyta `sensor_registry.yaml`
2. Wygeneruje `firmware/include/SensorRegistry.h` z nowym typem
3. Zweryfikuje, że firmware i backend są synced
4. Jeśli nowy typ nie istnieje w backendzie → build error

Po sukcesie: `firmware/include/SensorRegistry.h` zawiera embedded JSON i validatory.

## 3. Implementuj czujnik na firmware

Stwórz nową klasę dziedziczącą z `ISensor` w `firmware/lib/`:

```cpp
// firmware/lib/NewSensor/include/NewSensor.h
#pragma once

#include "ISensor.h"

class NewSensor : public ISensor {
 public:
  explicit NewSensor(uint8_t pin = DEFAULT_PIN);
  
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

Implementacja `read()` **musi**:
- Zwrócić `{ok: true, value: X, errorCode: nullptr}` przy powodzeniu
- Zwrócić `{ok: false, value: 0.0f, errorCode: "SENSOR_READ_FAILED"}` przy błędzie czytania
- Zwrócić `{ok: false, value: 0.0f, errorCode: "SENSOR_FAULT_HW"}` przy awarii sprzętowej (odłączenie, overtemp, itp.)

```cpp
// firmware/lib/NewSensor/src/NewSensor.cpp
#include "NewSensor.h"
#include <SensorRegistry.h>
#include <Logger.h>

NewSensor::NewSensor(uint8_t pin) : pin_(pin) {}

bool NewSensor::init() {
  pinMode(pin_, INPUT);
  LOG_INFO("[NEW]", "Initialized on pin %d", pin_);
  return true;
}

SensorReading NewSensor::read() {
  int rawValue = analogRead(pin_);
  float value = convertRawToPhysical(rawValue);
  
  if (value < MIN_VALID || value > MAX_VALID) {
    LOG_ERROR("[NEW]", "Out of range: %.2f", value);
    return {ok: false, value: 0.0f, errorCode: "SENSOR_OUT_OF_RANGE"};
  }
  
  return {ok: true, value: value, errorCode: nullptr};
}

const char* NewSensor::pointId() const { return "new_sensor_instance_id"; }
const char* NewSensor::pointType() const { return "new_sensor_type"; }
const char* NewSensor::unit() const { return "unit_symbol"; }
const char* NewSensor::getTag() const { return "[NEW]"; }
```

## 4. Dodaj czujnik do listy na boot

Edytuj [firmware/src/main.cpp](../../firmware/src/main.cpp) — w `initializeSensors()`:

```cpp
void initializeSensors() {
  if (sensors.empty()) {
    sensors.push_back(new PT100Sensor(PT100_SPI_CS));
    sensors.push_back(new NewSensor(NEW_SENSOR_PIN));  // DODAJ TU
    LOG_INFO("[BOOT]", "Sensors initialized");
  }
}
```

## 5. Test — build i flash

```bash
cd firmware
pio run
pio run --target upload
```

Sprawdź logi monitoringu szeregowego:
- `[NEW] Initialized on pin X` powinien się pojawić podczas boot
- `[NEW] Read: X.XX` powinno się pojawić co `SAMPLE_INTERVAL_MS`

## 6. Weryfikacja na backendzie

Wyślij testowy pakiet z nowym czujnikiem. Backend automatycznie utworzy `MeasurementPoint` z `external_id="new_sensor_instance_id"` i `point_type="new_sensor_type"`.

Sprawdź:
```bash
curl -X GET http://localhost:8000/api/v1/orgs/{org_id}/measurement_points \
  -H "Authorization: Bearer $JWT_TOKEN" | jq '.[] | select(.point_type == "new_sensor_type")'
```

Powinien pojawić się wpis z `is_active: true`.

## Uwagi projektowe

**ID punktu vs typ punktu**: `point_id` (np. `"pt100_temperature"`) jest lokalnym identyfikatorem na urządzeniu, a `type` (np. `"temperature"`) jest typem z rejestru globalnego. Wiele czujników tego samego typu na urządzeniu musi mieć różne `point_id`, np. `"temp_sensor_1"`, `"temp_sensor_2"`.

**Walidacja**: `SensorRegistry.h` zawiera `isValidPointType()` — skompiluje się, jeśli typ jest w `sensor_registry.yaml`. Zmiana rejestru wymaga rebuild firmware'u (pre-build script to zweryfikuje).

