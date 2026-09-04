#pragma once
//
// Atrapa czujnika dla testów TelemetryPayload — pozwala sterować wynikiem
// odczytu i policzyć, ile razy payload faktycznie odpytał czujnik.
//
#include <ISensor.h>

#include <string>

class FakeSensor : public ISensor {
 public:
  FakeSensor(const char* pointId, const char* pointType, const char* unit, const char* tag)
      : point_id_(pointId), point_type_(pointType), unit_(unit), tag_(tag) {}

  bool init() override {
    ++init_calls;
    return init_ok;
  }

  SensorReading read() override {
    ++read_calls;
    SensorReading reading;
    reading.ok = read_ok;
    reading.value = next_value;
    reading.errorCode = read_ok ? nullptr : error_code;
    return reading;
  }

  const char* pointId() const override { return point_id_.c_str(); }
  const char* pointType() const override { return point_type_.c_str(); }
  const char* unit() const override { return unit_.c_str(); }
  const char* getTag() const override { return tag_.c_str(); }

  bool init_ok = true;
  bool read_ok = true;
  float next_value = 21.5f;
  const char* error_code = "SENSOR_FAULT_HW";

  int init_calls = 0;
  int read_calls = 0;

 private:
  std::string point_id_;
  std::string point_type_;
  std::string unit_;
  std::string tag_;
};
