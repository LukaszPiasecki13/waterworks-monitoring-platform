#include <Arduino.h>
#include <HardwareSerial.h>
#include <Esp.h>
#include <esp_system.h>
#include <esp_task_wdt.h>
#include <vector>

#include <Config.h>
#include <RtcState.h>
#include <SensorRegistry.h>
#include <StatusLed.h>
#include <DeviceState.h>
#include <DeviceStateSource.h>
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
DeviceStateSource* deviceStateSource = nullptr;
bool modemBroughtUp = false;
bool keyGenerated = false;
unsigned long lastModemAttemptMs = 0;

// rtcRestartCounter is zeroed once telemetry comes up, so it counts the
// watchdog restarts since the last healthy start rather than since factory —
// captured before initializeTelemetry() resets it.
uint32_t restartCountAtBoot = 0;

// =========================
// Device state read channel (B-08)
// =========================

// device_state::RestartReason mirrors esp_reset_reason_t numerically. If the
// SDK ever renumbers these, fail the build instead of shipping firmware that
// mislabels every restart it reports.
static_assert(static_cast<int>(device_state::RestartReason::PowerOn) == ESP_RST_POWERON, "ESP_RST_POWERON drift");
static_assert(static_cast<int>(device_state::RestartReason::External) == ESP_RST_EXT, "ESP_RST_EXT drift");
static_assert(static_cast<int>(device_state::RestartReason::Software) == ESP_RST_SW, "ESP_RST_SW drift");
static_assert(static_cast<int>(device_state::RestartReason::Panic) == ESP_RST_PANIC, "ESP_RST_PANIC drift");
static_assert(static_cast<int>(device_state::RestartReason::IntWatchdog) == ESP_RST_INT_WDT, "ESP_RST_INT_WDT drift");
static_assert(static_cast<int>(device_state::RestartReason::TaskWatchdog) == ESP_RST_TASK_WDT,
              "ESP_RST_TASK_WDT drift");
static_assert(static_cast<int>(device_state::RestartReason::OtherWatchdog) == ESP_RST_WDT, "ESP_RST_WDT drift");
static_assert(static_cast<int>(device_state::RestartReason::DeepSleep) == ESP_RST_DEEPSLEEP, "ESP_RST_DEEPSLEEP drift");
static_assert(static_cast<int>(device_state::RestartReason::Brownout) == ESP_RST_BROWNOUT, "ESP_RST_BROWNOUT drift");
static_assert(static_cast<int>(device_state::RestartReason::Sdio) == ESP_RST_SDIO, "ESP_RST_SDIO drift");

// ArduinoJson stores `const char*` by reference, not by copy, so the serial
// must outlive the JsonDocument it is written into. A String owned here does
// that; `deviceIdentity.serialNumber().c_str()` would dangle immediately.
String deviceStateSerial;

device_state::Snapshot captureDeviceState() {
  device_state::Snapshot snapshot;
  deviceStateSerial = deviceIdentity.serialNumber();
  snapshot.serial_number = deviceStateSerial.c_str();
  snapshot.firmware_version = FIRMWARE_VERSION;
  snapshot.registry_schema_version = SensorRegistry::SCHEMA_VERSION;

  snapshot.uptime_seconds = (uint32_t)(millis() / 1000UL);
  snapshot.restart_count = restartCountAtBoot;
  snapshot.restart_reason = device_state::restartReasonFromCode((int)esp_reset_reason());

  snapshot.rssi_dbm =
      modemBroughtUp ? device_state::rssiDbmFromCsq(modemLink.signalQuality()) : device_state::RSSI_UNKNOWN;

  snapshot.free_heap_bytes = ESP.getFreeHeap();
  snapshot.min_free_heap_bytes = ESP.getMinFreeHeap();

  if (telemetryPayload) {
    snapshot.buffer_windows_used = (uint32_t)telemetryPayload->bufferedWindows();
    snapshot.buffer_windows_capacity = (uint32_t)TelemetryPayload::bufferCapacityWindows();
    snapshot.buffer_windows_dropped = telemetryPayload->droppedWindowsTotal();
  }

  return snapshot;
}

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

  deviceStateSource = new DeviceStateSource(
      SensorRegistry::STATE_SECTION_DEVICE, SensorRegistry::STATE_SECTION_DEVICE_SCHEMA_VERSION,
      (uint32_t)DEVICE_STATE_REPORT_INTERVAL_MS, captureDeviceState, []() { return (uint32_t)millis(); });
  telemetryPayload->setStateSource(deviceStateSource);

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
  restartCountAtBoot = rtcRestartCounter;
  LOG_INFO("[BOOT]", "Firmware %s, restart counter (RTC): %lu", FIRMWARE_VERSION, rtcRestartCounter);

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
