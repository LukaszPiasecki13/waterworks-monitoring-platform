#pragma once

#include <Arduino.h>
#include <functional>

class TelemetryPayload {
 public:
  TelemetryPayload(const char* deviceId, const char* orgId, const char* objectId);

  String build(uint32_t seq, unsigned long timestampMs);
  void setGetUtcTime(std::function<uint64_t()> getUtcTime);

 private:
  const char* device_id_;
  const char* org_id_;
  const char* object_id_;
  std::function<uint64_t()> getUtcTime_;

  float calculateSineValue(uint32_t seq);
  String formatIso8601(uint64_t utcMs);
};
