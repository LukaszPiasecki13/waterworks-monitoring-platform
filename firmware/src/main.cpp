#include <Arduino.h>
#include <HardwareSerial.h>

#include "Config.h"
#include "StatusLed.h"
#include "ModemPower.h"
#include "ModemLink.h"
#include "TelemetryHttpClient.h"
#include "TelemetryPayload.h"
#include "TelemetrySender.h"
#include "Watchdog.h"

#define SerialMon Serial
HardwareSerial SerialAT(1);

RTC_DATA_ATTR uint32_t rtcRestartCounter = 0;

// =========================
// Global instances
// =========================

StatusLed led(LED_PIN);
ModemPower modemPower(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);
ModemLink modemLink(SerialAT, MODEM_BAUD);
TelemetryHttpClient httpClient(modemLink, SERVER, PORT, DEVICE_KEY);
TelemetryPayload telemetryPayload(DEVICE_ID, ORG_ID, OBJECT_ID);
TelemetrySender telemetrySender(modemLink, httpClient, telemetryPayload, led, SEND_INTERVAL_MS, ERROR_RETRY_MS);
Watchdog watchdog(modemLink, modemPower, WATCHDOG_STUCK_MS, MAX_RESTART_ATTEMPTS);

// =========================
// Arduino setup/loop
// =========================

void setup() {
  SerialMon.begin(SERIAL_BAUD);
  delay(2000);

  SerialMon.println();
  SerialMon.println("========================================");
  SerialMon.println("[BOOT] ESP32-S3 + A7670E telemetry sender");
  SerialMon.println("========================================");
  SerialMon.print("[BOOT] Restart counter (RTC): ");
  SerialMon.println(rtcRestartCounter);

  modemPower.powerOn();

  if (!modemLink.init(APN, GPRS_USER, GPRS_PASS, SIM_PIN)) {
    SerialMon.println("[BOOT] Modem/Network setup failed");
    led.blinkError();
    return;
  }

  rtcRestartCounter = 0;
  telemetrySender.update(millis());  // Initialize last_success_ms
  SerialMon.println("[BOOT] Ready");
  led.blinkSuccess();
}

void loop() {
  unsigned long now = millis();

  watchdog.check(now, telemetrySender.lastSuccessMs());
  telemetrySender.update(now);

  delay(10);
}
