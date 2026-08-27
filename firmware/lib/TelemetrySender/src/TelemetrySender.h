#pragma once

#include <Arduino.h>

class ModemLink;
class TelemetryHttpClient;
class TelemetryPayload;
class StatusLed;
class DeviceIdentity;

class TelemetrySender {
 public:
  TelemetrySender(ModemLink& modem, TelemetryHttpClient& httpClient, TelemetryPayload& payload, StatusLed& led,
                  DeviceIdentity& identity, unsigned long sampleIntervalMs, unsigned long errorRetryMs);

  void update(unsigned long now);
  unsigned long lastSuccessMs() const { return last_success_ms_; }
  bool hasLastErrorWasPermanent() const { return last_error_was_permanent_; }

 private:
  ModemLink& modem_;
  TelemetryHttpClient& http_;
  TelemetryPayload& payload_;
  StatusLed& led_;
  DeviceIdentity& identity_;

  unsigned long sample_interval_ms_;
  unsigned long error_retry_ms_;

  unsigned long last_sample_ms_ = 0;
  unsigned long next_send_attempt_ms_ = 0;
  unsigned long last_success_ms_ = 0;
  bool last_error_was_permanent_ = false;
  uint32_t send_seq_ = 0;
};
