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
                                 StatusLed& led, DeviceIdentity& identity, unsigned long sampleIntervalMs,
                                 unsigned long errorRetryMs)
    : modem_(modem),
      http_(httpClient),
      payload_(payload),
      led_(led),
      identity_(identity),
      sample_interval_ms_(sampleIntervalMs),
      error_retry_ms_(errorRetryMs) {}

void TelemetrySender::update(unsigned long now) {
  if (!TimeSync::isSynced()) {
    return;
  }

  if (now >= last_sample_ms_ + sample_interval_ms_) {
    last_sample_ms_ = now;
    uint64_t utcMs = TimeSync::getUtcTimestamp();
    payload_.sample(utcMs);
  }

  if (now < next_send_attempt_ms_) {
    return;
  }

  if (!payload_.isReadyToSend()) {
    return;
  }

  if (!modem_.ensureConnected()) {
    LOG_WARN("[LOOP]", "Connection not ready");
    led_.blinkError();
    next_send_attempt_ms_ = now + error_retry_ms_;
    return;
  }

  // Note: uint32_t truncates Unix timestamp to 32-bit seconds. Valid until year 2106.
  uint32_t nowUnix = (uint32_t)(TimeSync::getUtcTimestamp() / 1000);

  if (!identity_.hasValidSession(nowUnix)) {
    LOG_WARN("[LOOP]", "No valid session, skipping telemetry");
    next_send_attempt_ms_ = now + error_retry_ms_;
    return;
  }

  send_seq_ = nowUnix;
  String payloadStr = payload_.build(send_seq_);
  LOG_INFO("[DATA]", "Payload: %s", payloadStr.c_str());

  String token = identity_.sessionToken();
  HttpResponse resp = http_.post(RESOURCE, payloadStr, token);

  if (resp.statusCode == 200 || resp.statusCode == 202) {
    LOG_INFO("[LOOP]", "Send OK, seq=%lu", send_seq_);
    payload_.acknowledge();
    led_.blinkSuccess();
    last_success_ms_ = now;
    last_error_was_permanent_ = false;
    next_send_attempt_ms_ = now + sample_interval_ms_;
  } else {
    LOG_ERROR("[LOOP]", "Send failed, seq=%lu", send_seq_);
    led_.blinkError();
    next_send_attempt_ms_ = now + error_retry_ms_;

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

    last_error_was_permanent_ = (resp.statusCode == 409 || resp.statusCode == 410 || resp.statusCode == 403);
  }
}
