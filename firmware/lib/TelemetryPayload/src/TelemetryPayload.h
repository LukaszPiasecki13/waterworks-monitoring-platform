#pragma once

#include <Arduino.h>
#include <functional>
#include "ISensor.h"

class TelemetryPayload {
 public:
  TelemetryPayload(const String& deviceId, ISensor* sensor);

  String build(uint32_t seq, unsigned long timestampMs);
  void setGetUtcTime(std::function<uint64_t()> getUtcTime);

 private:
  String device_id_;
  std::function<uint64_t()> getUtcTime_;
  ISensor* pt100_sensor_;

  float calculateSineValue(uint32_t seq);
  String formatIso8601(uint64_t utcMs);
};
