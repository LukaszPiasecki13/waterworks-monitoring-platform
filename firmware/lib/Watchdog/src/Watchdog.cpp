#include <Arduino.h>
#include <RtcState.h>
#include "Watchdog.h"
#include <ModemLink.h>
#include <ModemPower.h>
#include <TelemetrySender.h>

Watchdog::Watchdog(ModemLink& modem, ModemPower& power, unsigned long stuckThresholdMs, uint8_t maxRestarts)
    : modem_(modem), power_(power), stuck_threshold_ms_(stuckThresholdMs), max_restarts_(maxRestarts) {}

void Watchdog::check(unsigned long now, unsigned long lastSuccessMs) {
  if (now - lastSuccessMs <= stuck_threshold_ms_) {
    return;
  }

  // If last error was permanent (409, 410, 403), don't trigger recovery
  // Device is waiting for backend configuration, not a modem issue
  if (telemetry_sender_ && telemetry_sender_->hasLastErrorWasPermanent()) {
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
    delay(3000);
    recovery_attempts_++;
  } else if (recovery_attempts_ == 2) {
    if (rtcRestartCounter < max_restarts_) {
      rtcRestartCounter++;
      delay(1000);
      esp_restart();
    } else {
      recovery_attempts_ = 0;
    }
  }
}
