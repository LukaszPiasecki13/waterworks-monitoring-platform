#pragma once

#include <Arduino.h>

class TelemetryPayload {
 public:
  TelemetryPayload(const char* deviceId, const char* orgId, const char* objectId);

  String build(uint32_t seq);

 private:
  const char* device_id_;
  const char* org_id_;
  const char* object_id_;
};
