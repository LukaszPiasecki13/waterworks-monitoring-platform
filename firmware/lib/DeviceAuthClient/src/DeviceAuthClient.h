#pragma once

#include <Arduino.h>

class DeviceIdentity;
class TelemetryHttpClient;

class DeviceAuthClient {
 public:
  DeviceAuthClient(DeviceIdentity& identity, TelemetryHttpClient& http, unsigned long pollIntervalMs);
  void update(unsigned long nowMs);

 private:
  DeviceIdentity& identity_;
  TelemetryHttpClient& http_;
  unsigned long poll_interval_ms_;
  unsigned long next_allowed_poll_ms_ = 0;

  bool attemptAuth();
  uint32_t parseIso8601ToUnix(const String& iso8601);
};
