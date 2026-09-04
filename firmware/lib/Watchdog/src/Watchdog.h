#pragma once

#include <Arduino.h>

class IModemLink;
class IModemPower;
class ISystemControl;
class ITelemetryHealth;

// Trzystopniowa eskalacja przy braku udanej wysyłki dłużej niż `stuckThresholdMs`:
//   1. sprawdź, czy modem odpowiada na AT (jeśli tak — nic więcej),
//   2. twardy reset modemu,
//   3. restart ESP32, o ile nie wyczerpano limitu restartów z pamięci RTC.
class Watchdog {
 public:
  Watchdog(IModemLink& modem, IModemPower& power, ISystemControl& system, unsigned long stuckThresholdMs,
           uint8_t maxRestarts);

  void setTelemetryHealth(ITelemetryHealth* health) { telemetry_health_ = health; }
  void check(unsigned long now, unsigned long lastSuccessMs);

  // Wystawione do testów: numer kolejnego kroku eskalacji (0 = brak eskalacji).
  uint8_t recoveryAttempts() const { return recovery_attempts_; }

 private:
  IModemLink& modem_;
  IModemPower& power_;
  ISystemControl& system_;
  unsigned long stuck_threshold_ms_;
  uint8_t max_restarts_;
  ITelemetryHealth* telemetry_health_ = nullptr;

  uint8_t recovery_attempts_ = 0;

  void attemptRecovery(unsigned long now);
};
