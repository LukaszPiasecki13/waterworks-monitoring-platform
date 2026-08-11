#pragma once

#include <Arduino.h>

class ModemLink;
class TelemetryHttpClient;
class TelemetryPayload;
class StatusLed;

class TelemetrySender {
 public:
  TelemetrySender(ModemLink& modem,
                  TelemetryHttpClient& httpClient,
                  TelemetryPayload& payload,
                  StatusLed& led,
                  unsigned long sendIntervalMs,
                  unsigned long errorRetryMs);

  void update(unsigned long now);
  unsigned long lastSuccessMs() const { return last_success_ms_; }

 private:
  ModemLink& modem_;
  TelemetryHttpClient& http_;
  TelemetryPayload& payload_;
  StatusLed& led_;

  unsigned long send_interval_ms_;
  unsigned long error_retry_ms_;

  unsigned long last_send_ms_ = 0;
  unsigned long next_allowed_send_ms_ = 0;
  unsigned long last_success_ms_ = 0;
};
