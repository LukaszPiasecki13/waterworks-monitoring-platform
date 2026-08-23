#pragma once

#include <Arduino.h>
#include <functional>

class TelemetryPayload {
 public:
  TelemetryPayload(const String& deviceId);

  String build(uint32_t seq, unsigned long timestampMs);
  void setGetUtcTime(std::function<uint64_t()> getUtcTime);

 private:
  String device_id_;
  std::function<uint64_t()> getUtcTime_;

  float calculateSineValue(uint32_t seq);
  String formatIso8601(uint64_t utcMs);
};
