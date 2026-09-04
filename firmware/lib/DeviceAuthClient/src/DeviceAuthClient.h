#pragma once

#include <Arduino.h>
#include <cstdint>

class IClock;
class IDeviceIdentity;
class IHttpClient;

class DeviceAuthClient {
 public:
  DeviceAuthClient(IDeviceIdentity& identity, IHttpClient& http, IClock& clock, unsigned long pollIntervalMs);
  void update(unsigned long nowMs);

  // Wystawione do testów: konwersja "YYYY-MM-DDTHH:MM:SS.sssZ" -> unix (s).
  // 0 oznacza łańcuch nieparsowalny.
  static uint32_t parseIso8601ToUnix(const String& iso8601);

 private:
  IDeviceIdentity& identity_;
  IHttpClient& http_;
  IClock& clock_;
  unsigned long poll_interval_ms_;
  unsigned long next_allowed_poll_ms_ = 0;

  bool attemptAuth();
};
