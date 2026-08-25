#include <Arduino.h>
#include <ArduinoJson.h>
#include <Config.h>
#include "TelemetrySender.h"
#include <ModemLink.h>
#include <Logger.h>
#include <TelemetryHttpClient.h>
#include <TelemetryPayload.h>
#include <StatusLed.h>
#include <TimeSync.h>
#include <DeviceIdentity.h>

TelemetrySender::TelemetrySender(ModemLink& modem, TelemetryHttpClient& httpClient, TelemetryPayload& payload,
                                 StatusLed& led, DeviceIdentity& identity, unsigned long sendIntervalMs,
                                 unsigned long errorRetryMs)
    : modem_(modem),
      http_(httpClient),
      payload_(payload),
      led_(led),
      identity_(identity),
      send_interval_ms_(sendIntervalMs),
      error_retry_ms_(errorRetryMs) {}

void TelemetrySender::update(unsigned long now) {
  if (now < next_allowed_send_ms_) {
    return;
  }

  unsigned long send_start_ms = millis();
  next_allowed_send_ms_ = send_start_ms + send_interval_ms_;

  if (!modem_.ensureConnected()) {
    LOG_WARN("[LOOP]", "Connection not ready");
    led_.blinkError();
    next_allowed_send_ms_ = millis() + error_retry_ms_;
    return;
  }

  if (!TimeSync::isSynced()) {
    LOG_WARN("[LOOP]", "Time not synced, skipping telemetry");
    next_allowed_send_ms_ = millis() + error_retry_ms_;
    return;
  }

  uint32_t nowUnix = (uint32_t)(TimeSync::getUtcTimestamp() / 1000);

  if (!identity_.hasValidSession(nowUnix)) {
    LOG_WARN("[LOOP]", "No valid session, skipping telemetry");
    next_allowed_send_ms_ = millis() + error_retry_ms_;
    return;
  }

  uint32_t seq = nowUnix;
  String payloadStr = payload_.build(seq, send_start_ms);
  LOG_INFO("[DATA]", "Payload: %s", payloadStr.c_str());

  String token = identity_.sessionToken();
  HttpResponse resp = http_.post(RESOURCE, payloadStr, token);

  if (resp.statusCode == 200 || resp.statusCode == 202) {
    LOG_INFO("[LOOP]", "Send OK, seq=%lu", seq);

    led_.blinkSuccess();
    last_success_ms_ = now;
    last_error_was_permanent_ = false;
  } else {
    LOG_ERROR("[LOOP]", "Send failed, seq=%lu", seq);

    led_.blinkError();
    next_allowed_send_ms_ = millis() + error_retry_ms_;

    // Check if device was deleted from platform (401 Device not found)
    if (resp.statusCode == 401) {
      JsonDocument doc;
      DeserializationError err = deserializeJson(doc, resp.body);
      if (!err) {
        const char* detail = doc["detail"];
        if (detail && strcmp(detail, "Device not found") == 0) {
          LOG_WARN("[LOOP]", "Device deleted from platform, clearing provisioning state");
          identity_.clearProvisioningState();
        }
      }
    }

    // Track if error is permanent (device not assigned, etc.)
    last_error_was_permanent_ = (resp.statusCode == 409 || resp.statusCode == 410 || resp.statusCode == 403);
  }
}
