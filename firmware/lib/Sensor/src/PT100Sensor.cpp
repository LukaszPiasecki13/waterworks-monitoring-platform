#include "PT100Sensor.h"
#include <Logger.h>
#include <Config.h>
#include <SensorRegistry.h>

// Compile-time validation: point_type and error codes must be in registry
static_assert(SensorRegistry::isValidPointType("temperature"), "ERROR: 'temperature' not registered in SensorRegistry");
static_assert(SensorRegistry::isValidErrorCode("SENSOR_FAULT_HW"),
              "ERROR: 'SENSOR_FAULT_HW' not registered in SensorRegistry");

PT100Sensor::PT100Sensor(uint8_t csPin) : pt100_(csPin), cs_pin_(csPin) {}

bool PT100Sensor::init() {
  SPI.begin(PT100_SPI_SCK, PT100_SPI_MISO, PT100_SPI_MOSI, cs_pin_);
  if (pt100_.begin(MAX31865_3WIRE)) {
    LOG_INFO("[PT100]", "Initialized");
    return true;
  } else {
    LOG_ERROR("[PT100]", "Initialization failed!");
    return false;
  }
}

SensorReading PT100Sensor::read() {
  uint16_t rtd = pt100_.readRTD();
  float temp = pt100_.calculateTemperature(rtd, RTD_NOMINAL_OHMS, REF_RESISTOR_OHMS);

  uint8_t fault = pt100_.readFault();
  if (fault) {
    LOG_ERROR("[PT100]", "Fault 0x%02X", fault);
    if (fault & MAX31865_FAULT_HIGHTHRESH) LOG_ERROR("[PT100]", "RTD High Threshold");
    if (fault & MAX31865_FAULT_LOWTHRESH) LOG_ERROR("[PT100]", "RTD Low Threshold");
    if (fault & MAX31865_FAULT_REFINLOW) LOG_ERROR("[PT100]", "REFIN- > 0.85 x Bias");
    if (fault & MAX31865_FAULT_REFINHIGH) LOG_ERROR("[PT100]", "REFIN- < 0.85 x Bias");
    if (fault & MAX31865_FAULT_RTDINLOW) LOG_ERROR("[PT100]", "RTDIN- < 0.85 x Bias");
    if (fault & MAX31865_FAULT_OVUV) LOG_ERROR("[PT100]", "Under/Over voltage");
    pt100_.clearFault();
    SensorReading result;
    result.ok = false;
    result.value = 0.0f;
    result.errorCode = "SENSOR_FAULT_HW";
    return result;
  }

  LOG_INFO("[PT100]", "Temperature: %.2f°C", temp);
  SensorReading result;
  result.ok = true;
  result.value = temp;
  result.errorCode = nullptr;
  return result;
}

const char* PT100Sensor::pointId() const { return "pt100_temperature"; }
const char* PT100Sensor::pointType() const { return "temperature"; }
const char* PT100Sensor::unit() const { return "°C"; }
const char* PT100Sensor::getTag() const { return "[PT100]"; }
