#pragma once

#include <Adafruit_MAX31865.h>
#include "ISensor.h"

class PT100Sensor : public ISensor {
 public:
  explicit PT100Sensor(uint8_t csPin = 14);  // Default from Config.h

  bool init() override;
  bool read(float& outValue) override;
  const char* getTag() const override;

 private:
  Adafruit_MAX31865 pt100_;
  uint8_t cs_pin_;

  // Constants
  static constexpr float RTD_NOMINAL_OHMS = 100.0f;
  static constexpr float REF_RESISTOR_OHMS = 430.0f;
};
