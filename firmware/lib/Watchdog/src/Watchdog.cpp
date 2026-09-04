#include <Arduino.h>
#include "Watchdog.h"
#include <IModemLink.h>
#include <IModemPower.h>
#include <ISystemControl.h>
#include <ITelemetryHealth.h>

Watchdog::Watchdog(IModemLink& modem, IModemPower& power, ISystemControl& system, unsigned long stuckThresholdMs,
                   uint8_t maxRestarts)
    : modem_(modem), power_(power), system_(system), stuck_threshold_ms_(stuckThresholdMs), max_restarts_(maxRestarts) {}

void Watchdog::check(unsigned long now, unsigned long lastSuccessMs) {
  if (now - lastSuccessMs <= stuck_threshold_ms_) {
    return;
  }

  // If last error was permanent (409, 410, 403), don't trigger recovery
  // Device is waiting for backend configuration, not a modem issue
  if (telemetry_health_ && telemetry_health_->lastErrorWasPermanent()) {
    return;
  }

  attemptRecovery(now);
}

void Watchdog::attemptRecovery(unsigned long now) {
  if (recovery_attempts_ == 0) {
    if (modem_.testAT()) {
      recovery_attempts_ = 0;
    } else {
      recovery_attempts_++;
    }
  } else if (recovery_attempts_ == 1) {
    power_.hardReset();
    system_.delayMs(3000);
    recovery_attempts_++;
  } else if (recovery_attempts_ == 2) {
    if (system_.restartCount() < max_restarts_) {
      system_.setRestartCount(system_.restartCount() + 1);
      system_.delayMs(1000);
      system_.restart();
    } else {
      recovery_attempts_ = 0;
    }
  }
}
