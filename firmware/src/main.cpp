#include <Arduino.h>
#include <HardwareSerial.h>
#include <Esp.h>
#include <esp_task_wdt.h>
#include <vector>

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
#include <Logger.h>
#include <ISensor.h>
#include <PT100Sensor.h>

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
std::vector<ISensor*> sensors;
TelemetryPayload* telemetryPayload = nullptr;

TelemetryHttpClient* httpClient = nullptr;
TelemetrySender* telemetrySender = nullptr;
DeviceAuthClient* deviceAuthClient = nullptr;
EnrollmentClient* enrollmentClient = nullptr;
Watchdog* watchdog = nullptr;
bool modemBroughtUp = false;
bool keyGenerated = false;
unsigned long lastModemAttemptMs = 0;

// =========================
// Initialization functions
// =========================

void initializeDeviceIdentity() {
  LOG_INFO("[BOOT]", "Initializing DeviceIdentity...");
  deviceIdentity.begin();
  LOG_INFO("[BOOT]", "DeviceIdentity initialized");
  esp_task_wdt_reset();
}

bool initializeModemAndNetwork() {
  LOG_INFO("[BOOT]", "Powering on modem...");
  modemPower.powerOn();
  delay(3000);
  LOG_INFO("[BOOT]", "Modem power: ON");
  esp_task_wdt_reset();

  LOG_INFO("[BOOT]", "Initializing modem link (this may take up to 90s if no signal)...");
  unsigned long modemInitStart = millis();
  if (!modemLink.init(APN, GPRS_USER, GPRS_PASS, SIM_PIN)) {
    LOG_ERROR("[BOOT]", "Modem/Network setup failed after %lu ms", millis() - modemInitStart);
    led.blinkError();
    return false;
  }
  LOG_INFO("[BOOT]", "Modem ready in %lu ms", millis() - modemInitStart);
  modemBroughtUp = true;
  esp_task_wdt_reset();
  return true;
}

void initializeTimeSync() {
  LOG_INFO("[BOOT]", "Initializing time sync...");
  TimeSync::init();
  LOG_INFO("[TIME]", "Attempting NTP sync...");
  if (!TimeSync::sync(modemLink)) {
    LOG_WARN("[TIME]", "NTP sync failed, will use boot-relative time");
  } else {
    LOG_INFO("[TIME]", "NTP sync SUCCESS (UTC: %llu)", TimeSync::getUtcTimestamp());
  }
  esp_task_wdt_reset();
}

void initializeSensors() {
  if (sensors.empty()) {
    sensors.push_back(new PT100Sensor(PT100_SPI_CS));
    LOG_INFO("[BOOT]", "Sensors initialized");
  }
}

void initializeHttpClient() {
  if (!httpClient) {
    httpClient = new TelemetryHttpClient(modemLink, SERVER, PORT, "");
    LOG_INFO("[BOOT]", "HTTP client initialized");
  }
}

void initializeTelemetry() {
  initializeSensors();
  initializeHttpClient();

  telemetryPayload = new TelemetryPayload(deviceIdentity.serialNumber(), sensors);
  telemetryPayload->setGetUtcTime([]() { return TimeSync::getUtcTimestamp(); });
  deviceAuthClient = new DeviceAuthClient(deviceIdentity, *httpClient, CLAIM_POLL_INTERVAL_MS);
  telemetrySender = new TelemetrySender(modemLink, *httpClient, *telemetryPayload, led, deviceIdentity,
                                        SAMPLE_INTERVAL_MS, ERROR_RETRY_MS);
  watchdog->setTelemetrySender(telemetrySender);

  rtcRestartCounter = 0;
  telemetrySender->update(millis());
  LOG_INFO("[BOOT]", "Ready");
  led.blinkSuccess();
  esp_task_wdt_reset();
}

void handleEnrollmentPhase(unsigned long now) {
  if (!enrollmentClient) {
    if (!httpClient) return;
    enrollmentClient = new EnrollmentClient(deviceIdentity, httpClient);
  }

  enrollmentClient->update(now);

  if (enrollmentClient->needsModemBringUp() && !modemBroughtUp) {
    if (now - lastModemAttemptMs < ACTIVATION_RETRY_INTERVAL_MS) return;
    lastModemAttemptMs = now;

    LOG_INFO("[BOOT]", "Activation code accepted, powering on modem...");
    if (initializeModemAndNetwork()) {
      initializeTimeSync();
      initializeHttpClient();
      enrollmentClient->setHttpClient(httpClient);
      enrollmentClient->onModemReady();
    }
  }

  if (deviceIdentity.isProvisioningCompleted() && modemBroughtUp && !telemetryPayload) {
    LOG_INFO("[BOOT]", "Provisioning completed, initializing telemetry...");
    initializeTelemetry();
  }
}

// =========================
// Arduino setup/loop
// =========================

void setup() {
  esp_task_wdt_reset();

  SerialMon.begin(SERIAL_BAUD);
  delay(200);
  esp_task_wdt_reset();

  led.initializePixels();
  esp_task_wdt_reset();

  LOG_INFO("[BOOT]", "");
  LOG_INFO("[BOOT]", "========================================");
  LOG_INFO("[BOOT]", "ESP32-S3 + A7670E telemetry sender");
  LOG_INFO("[BOOT]", "========================================");

  initializeDeviceIdentity();
  LOG_INFO("[BOOT]", "Restart counter (RTC): %lu", rtcRestartCounter);

  watchdog = new Watchdog(modemLink, modemPower, WATCHDOG_STUCK_MS, MAX_RESTART_ATTEMPTS);
  esp_task_wdt_reset();

  if (!deviceIdentity.isProvisioningCompleted()) {
    LOG_INFO("[BOOT]", "Provisioning not completed — waiting for ACTIVATE <code>");
    LOG_INFO("[BOOT]", "Modem stays off until a valid activation code is accepted");
    enrollmentClient = new EnrollmentClient(deviceIdentity, nullptr);
    return;
  }

  if (!initializeModemAndNetwork()) return;
  initializeTimeSync();
  initializeTelemetry();
}

void loop() {
  esp_task_wdt_reset();

  if (deviceIdentity.needsReprovisioning()) {
    LOG_INFO("[BOOT]", "Device deleted from platform, restarting...");
    delay(1000);
    esp_restart();
  }

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
    handleEnrollmentPhase(now);
    if (!telemetrySender) {
      watchdog->check(now, now);
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
