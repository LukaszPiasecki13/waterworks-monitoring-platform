#include <Arduino.h>
#include <HardwareSerial.h>
#include <Esp.h>
#include <esp_task_wdt.h>

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
#include <DeviceIdentity.h>
#include <DeviceAuthClient.h>
#include <EnrollmentClient.h>

#define SerialMon Serial
HardwareSerial SerialAT(1);

RTC_DATA_ATTR uint32_t rtcRestartCounter = 0;
RTC_DATA_ATTR uint32_t rtcSyncedTimeUtcSec = 0;
RTC_DATA_ATTR uint32_t rtcSyncMillis = 0;

// =========================
// Global instances
// =========================

StatusLed led(LED_PIN);
DeviceIdentity deviceIdentity;
ModemPower modemPower(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);
ModemLink modemLink(SerialAT, MODEM_BAUD);
TelemetryPayload* telemetryPayload = nullptr;

TelemetryHttpClient* httpClient = nullptr;
TelemetrySender* telemetrySender = nullptr;
DeviceAuthClient* deviceAuthClient = nullptr;
EnrollmentClient* enrollmentClient = nullptr;
Watchdog* watchdog = nullptr;
bool modemBroughtUp = false;
bool keyGenerated = false;             // Track first-boot key generation (expensive operation)
unsigned long lastModemAttemptMs = 0;  // Throttle modem bring-up retries

// =========================
// Arduino setup/loop
// =========================

void setup() {
  esp_task_wdt_reset();

  SerialMon.begin(SERIAL_BAUD);
  delay(200);
  esp_task_wdt_reset();

  // Initialize NeoPixel LED now that watchdog resets are active
  led.initializePixels();
  esp_task_wdt_reset();

  SerialMon.println();
  SerialMon.println("========================================");
  SerialMon.println("[BOOT] ESP32-S3 + A7670E telemetry sender");
  SerialMon.println("========================================");
  SerialMon.println("[BOOT] Initializing DeviceIdentity...");
  deviceIdentity.begin();
  // Note: ensureKey() moved to loop() first iteration to avoid blocking setup()
  // and triggering watchdog during expensive EC key generation (mbedtls_ecp_gen_key)
  SerialMon.println("[BOOT] DeviceIdentity initialized");
  esp_task_wdt_reset();

  SerialMon.print("[BOOT] Restart counter (RTC): ");
  SerialMon.println(rtcRestartCounter);

  // Don't create httpClient yet - modem isn't initialized
  httpClient = nullptr;
  watchdog = new Watchdog(modemLink, modemPower, WATCHDOG_STUCK_MS, MAX_RESTART_ATTEMPTS);
  esp_task_wdt_reset();

  if (!deviceIdentity.isProvisioningCompleted()) {
    SerialMon.println("[BOOT] Provisioning not completed — waiting for ACTIVATE <code> over Serial");
    SerialMon.println("[BOOT] Modem stays off until a valid activation code is accepted");
    // Create EnrollmentClient for serial input processing (HTTP redeem waits for modem)
    enrollmentClient = new EnrollmentClient(deviceIdentity, nullptr);
    return;
  }

  SerialMon.println("[BOOT] Powering on modem...");
  modemPower.powerOn();
  delay(3000);
  SerialMon.println("[BOOT] Modem power: ON");
  esp_task_wdt_reset();

  SerialMon.println("[BOOT] Initializing modem link (this may take up to 90s if no signal)...");
  unsigned long modemInitStart = millis();
  if (!modemLink.init(APN, GPRS_USER, GPRS_PASS, SIM_PIN)) {
    SerialMon.print("[BOOT] Modem/Network setup failed after ");
    SerialMon.print(millis() - modemInitStart);
    SerialMon.println("ms");
    led.blinkError();
    return;
  }
  SerialMon.print("[BOOT] Modem ready in ");
  SerialMon.print(millis() - modemInitStart);
  SerialMon.println("ms");
  esp_task_wdt_reset();

  SerialMon.println("[BOOT] Initializing time sync...");
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
  esp_task_wdt_reset();

  modemBroughtUp = true;

  if (!httpClient) {
    httpClient = new TelemetryHttpClient(modemLink, SERVER, PORT, "");
  }
  telemetryPayload = new TelemetryPayload(deviceIdentity.serialNumber());
  telemetryPayload->setGetUtcTime([]() { return TimeSync::getUtcTimestamp(); });
  deviceAuthClient = new DeviceAuthClient(deviceIdentity, *httpClient, CLAIM_POLL_INTERVAL_MS);
  telemetrySender = new TelemetrySender(modemLink, *httpClient, *telemetryPayload, led, deviceIdentity,
                                        SEND_INTERVAL_MS, ERROR_RETRY_MS);
  watchdog->setTelemetrySender(telemetrySender);

  rtcRestartCounter = 0;
  telemetrySender->update(millis());
  SerialMon.println("[BOOT] Ready");
  led.blinkSuccess();
  esp_task_wdt_reset();
}

void loop() {
  esp_task_wdt_reset();

  // Check if device was deleted from platform and needs to restart
  if (deviceIdentity.needsReprovisioning()) {
    SerialMon.println("[BOOT] Device deleted from platform, clearing state and restarting...");
    delay(1000);
    esp_restart();
  }

  // Generate EC key on first iteration if needed (expensive: mbedtls_ecp_gen_key)
  // This was moved from setup() to avoid blocking and triggering watchdog
  if (!keyGenerated) {
    keyGenerated = true;
    deviceIdentity.ensureKey();
  }

  unsigned long now = millis();

  if (!deviceIdentity.isProvisioningCompleted()) {
    if (!watchdog) {
      delay(10);
      return;
    }

    // Create enrollmentClient lazily after httpClient is ready
    if (!enrollmentClient) {
      if (!httpClient) {
        delay(10);
        return;
      }
      enrollmentClient = new EnrollmentClient(deviceIdentity, httpClient);
    }

    if (enrollmentClient) {
      enrollmentClient->update(now);
    }

    if (enrollmentClient && enrollmentClient->needsModemBringUp() && !modemBroughtUp) {
      unsigned long now = millis();
      if (now - lastModemAttemptMs < ACTIVATION_RETRY_INTERVAL_MS) {
        return;  // Throttle: wait before retrying modem power-on
      }
      lastModemAttemptMs = now;

      SerialMon.println("[BOOT] Activation code accepted, powering on modem...");
      esp_task_wdt_reset();
      modemPower.powerOn();
      delay(3000);
      SerialMon.println("[BOOT] Modem power: ON");
      esp_task_wdt_reset();

      SerialMon.println("[BOOT] Initializing modem link (timeout 30s)...");
      esp_task_wdt_reset();
      unsigned long modemInitStart = millis();
      if (!modemLink.init(APN, GPRS_USER, GPRS_PASS, SIM_PIN)) {
        SerialMon.print("[BOOT] Modem/Network setup failed after ");
        SerialMon.print(millis() - modemInitStart);
        SerialMon.println("ms");
        led.blinkError();
      } else {
        SerialMon.print("[BOOT] Modem ready in ");
        SerialMon.print(millis() - modemInitStart);
        SerialMon.println("ms");
        esp_task_wdt_reset();

        SerialMon.println("[BOOT] Initializing time sync...");
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
        esp_task_wdt_reset();

        // Create httpClient now that modem is initialized
        if (!httpClient) {
          httpClient = new TelemetryHttpClient(modemLink, SERVER, PORT, "");
        }
        esp_task_wdt_reset();

        modemBroughtUp = true;
        if (enrollmentClient) {
          enrollmentClient->setHttpClient(httpClient);
          enrollmentClient->onModemReady();
        }
      }
    }

    if (deviceIdentity.isProvisioningCompleted() && modemBroughtUp && !telemetryPayload) {
      // Phase D: transition to normal operation once provisioning succeeds and modem is ready
      SerialMon.println("[BOOT] Provisioning completed, initializing telemetry...");

      telemetryPayload = new TelemetryPayload(deviceIdentity.serialNumber());
      telemetryPayload->setGetUtcTime([]() { return TimeSync::getUtcTimestamp(); });
      deviceAuthClient = new DeviceAuthClient(deviceIdentity, *httpClient, CLAIM_POLL_INTERVAL_MS);
      telemetrySender = new TelemetrySender(modemLink, *httpClient, *telemetryPayload, led, deviceIdentity,
                                            SEND_INTERVAL_MS, ERROR_RETRY_MS);
      watchdog->setTelemetrySender(telemetrySender);

      rtcRestartCounter = 0;
      telemetrySender->update(millis());
      SerialMon.println("[BOOT] Ready");
      led.blinkSuccess();
      // Continue to normal operation below (no return)
    } else if (!telemetrySender) {
      // Still in enrollment, haven't transitioned yet
      watchdog->check(now, now);  // nothing to consider "stuck" yet — no telemetry attempted during enrollment
      delay(10);
      return;
    }
  }

  if (!telemetrySender || !telemetryPayload || !deviceAuthClient || !watchdog) {
    delay(10);
    return;
  }

  watchdog->check(now, telemetrySender->lastSuccessMs());
  deviceAuthClient->update(now);
  telemetrySender->update(now);

  delay(10);
}
