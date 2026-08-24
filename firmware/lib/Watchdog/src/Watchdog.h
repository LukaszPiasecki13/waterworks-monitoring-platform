#pragma once

#include <Arduino.h>

class ModemLink;
class ModemPower;
class TelemetrySender;

class Watchdog {
 public:
  Watchdog(ModemLink& modem, ModemPower& power, unsigned long stuckThresholdMs, uint8_t maxRestarts);

  void setTelemetrySender(TelemetrySender* sender) { telemetry_sender_ = sender; }
  void check(unsigned long now, unsigned long lastSuccessMs);

 private:
  ModemLink& modem_;
  ModemPower& power_;
  unsigned long stuck_threshold_ms_;
  uint8_t max_restarts_;
  TelemetrySender* telemetry_sender_ = nullptr;

  uint8_t recovery_attempts_ = 0;

  void attemptRecovery(unsigned long now);
};
