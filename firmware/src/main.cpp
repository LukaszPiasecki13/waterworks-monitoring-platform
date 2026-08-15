#include <Arduino.h>
#include <HardwareSerial.h>

#include <Config.h>
#include <RtcState.h>
#include <StatusLed.h>
#include <ModemPower.h>
#include <ModemLink.h>
#include <TelemetryHttpClient.h>
#include <TelemetryPayload.h>
#include <TelemetrySender.h>
#include <TimeSync.h>
#include <Watchdog.h>

#define SerialMon Serial
HardwareSerial SerialAT(1);

RTC_DATA_ATTR uint32_t rtcRestartCounter = 0;  // Definition for linking
RTC_DATA_ATTR uint32_t rtcSyncedTimeUtcSec = 0;
RTC_DATA_ATTR uint32_t rtcSyncMillis = 0;

// =========================
// Global instances
// =========================

StatusLed led(LED_PIN);
ModemPower modemPower(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);
ModemLink modemLink(SerialAT, MODEM_BAUD);
TelemetryPayload telemetryPayload(DEVICE_ID);

TelemetryHttpClient* httpClient = nullptr;
TelemetrySender* telemetrySender = nullptr;
Watchdog* watchdog = nullptr;

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

  TimeSync::init();
  SerialMon.println("[TIME] Attempting NTP sync...");
  if (!TimeSync::sync(modemLink)) {
    SerialMon.println("[TIME] NTP sync failed, will use boot-relative time");
    SerialMon.print("[TIME] Synced before: ");
    SerialMon.println(TimeSync::isSynced() ? "yes" : "no");
  } else {
    SerialMon.println("[TIME] NTP sync SUCCESS");
    SerialMon.print("[TIME] UTC timestamp: ");
    SerialMon.println(TimeSync::getUtcTimestamp());
  }

  httpClient = new TelemetryHttpClient(modemLink, SERVER, PORT, DEVICE_KEY);
  telemetryPayload.setGetUtcTime([]() { return TimeSync::getUtcTimestamp(); });
  telemetrySender =
      new TelemetrySender(modemLink, *httpClient, telemetryPayload, led, SEND_INTERVAL_MS, ERROR_RETRY_MS);
  watchdog = new Watchdog(modemLink, modemPower, WATCHDOG_STUCK_MS, MAX_RESTART_ATTEMPTS);

  rtcRestartCounter = 0;
  telemetrySender->update(millis());  // Initialize last_success_ms
  SerialMon.println("[BOOT] Ready");
  led.blinkSuccess();
}

void loop() {
  if (!telemetrySender || !watchdog) {
    delay(10);
    return;
  }

  unsigned long now = millis();

  watchdog->check(now, telemetrySender->lastSuccessMs());
  telemetrySender->update(now);

  delay(10);
}
