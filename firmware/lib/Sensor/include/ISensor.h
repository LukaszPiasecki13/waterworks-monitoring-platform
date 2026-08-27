#pragma once

#include "SensorRegistry.h"

struct SensorReading {
  bool ok;
  float value;
  const char* errorCode;  // nullptr when ok
};

class ISensor {
 public:
  virtual ~ISensor() = default;

  virtual bool init() = 0;

  virtual SensorReading read() = 0;

  // Returns the sensor's point ID (e.g., "pt100_temperature")
  virtual const char* pointId() const = 0;

  // Returns the point type from SensorRegistry (e.g., POINT_TYPE_TEMPERATURE)
  virtual const char* pointType() const = 0;

  // Returns the canonical unit (e.g., "°C")
  virtual const char* unit() const = 0;

  // Get the sensor's log tag (e.g., "[PT100]")
  virtual const char* getTag() const = 0;
};
