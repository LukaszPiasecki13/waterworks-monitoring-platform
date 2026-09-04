#pragma once

#include <Arduino.h>
#include <ITelemetryHealth.h>

class IClock;
class IDeviceIdentity;
class IHttpClient;
class IModemLink;
class IStatusLed;
class TelemetryPayload;

class TelemetrySender : public ITelemetryHealth {
 public:
  TelemetrySender(IModemLink& modem, IHttpClient& httpClient, TelemetryPayload& payload, IStatusLed& led,
                  IDeviceIdentity& identity, IClock& clock, unsigned long sampleIntervalMs, unsigned long errorRetryMs);

  void update(unsigned long now);
  unsigned long lastSuccessMs() const { return last_success_ms_; }
  bool lastErrorWasPermanent() const override { return last_error_was_permanent_; }

  // Numer sekwencyjny ostatnio zbudowanego pakietu (0 zanim cokolwiek wysłano).
  uint32_t lastSeq() const { return send_seq_; }

 private:
  IModemLink& modem_;
  IHttpClient& http_;
  TelemetryPayload& payload_;
  IStatusLed& led_;
  IDeviceIdentity& identity_;
  IClock& clock_;

  unsigned long sample_interval_ms_;
  unsigned long error_retry_ms_;

  void scheduleNextAttempt(unsigned long atMs) {
    next_send_attempt_ms_ = atMs;
    send_attempt_scheduled_ = true;
  }

  unsigned long last_sample_ms_ = 0;
  unsigned long next_send_attempt_ms_ = 0;
  bool send_attempt_scheduled_ = false;
  unsigned long last_success_ms_ = 0;
  bool last_error_was_permanent_ = false;
  uint32_t send_seq_ = 0;
};
