#include <Arduino.h>
#include "Watchdog.h"
#include "ModemLink.h"
#include "ModemPower.h"

#define SerialMon Serial

extern RTC_DATA_ATTR uint32_t rtcRestartCounter;

Watchdog::Watchdog(ModemLink& modem,
                   ModemPower& power,
                   unsigned long stuckThresholdMs,
                   uint8_t maxRestarts)
    : modem_(modem),
      power_(power),
      stuck_threshold_ms_(stuckThresholdMs),
      max_restarts_(maxRestarts) {
}

void Watchdog::check(unsigned long now, unsigned long lastSuccessMs) {
  if (now - lastSuccessMs <= stuck_threshold_ms_) {
    return;
  }

  SerialMon.println();
  SerialMon.println("[WATCHDOG] No successful send for 5+ minutes - triggering recovery!");
  attemptRecovery(now);
}

void Watchdog::attemptRecovery(unsigned long now) {
  if (recovery_attempts_ == 0) {
    SerialMon.println("[RECOVERY-L1] Attempting AT test...");
    if (modem_.testAT()) {
      SerialMon.println("[RECOVERY-L1] AT test OK - resetting recovery counter");
      recovery_attempts_ = 0;
    } else {
      recovery_attempts_++;
    }
  } else if (recovery_attempts_ == 1) {
    SerialMon.println("[RECOVERY-L2] Hard reset via RESET pin + PWRKEY...");
    power_.hardReset();
    delay(3000);
    recovery_attempts_++;
  } else if (recovery_attempts_ == 2) {
    if (rtcRestartCounter < max_restarts_) {
      rtcRestartCounter++;
      SerialMon.println("[RECOVERY-L3] Restarting ESP32...");
      delay(1000);
      esp_restart();
    } else {
      SerialMon.println("[RECOVERY-L3] Max restarts reached - giving up");
      recovery_attempts_ = 0;
    }
  }
}
