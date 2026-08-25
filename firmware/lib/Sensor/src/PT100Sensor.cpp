#include "PT100Sensor.h"
#include <Logger.h>
#include <Config.h>

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

bool PT100Sensor::read(float& outValue) {
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
  }

  LOG_INFO("[PT100]", "Temperature: %.2f°C", temp);
  outValue = temp;
  return true;  // DEC-15: zawsze true, fault bits tylko logowane (zachowanie 1:1 ze stanem przed refaktorem)
}

const char* PT100Sensor::getTag() const { return "[PT100]"; }
