#include <Arduino.h>
#include <Config.h>
#include "TelemetrySender.h"
#include <ModemLink.h>
#include <TelemetryHttpClient.h>
#include <TelemetryPayload.h>
#include <StatusLed.h>

#define SerialMon Serial

TelemetrySender::TelemetrySender(ModemLink& modem,
                                 TelemetryHttpClient& httpClient,
                                 TelemetryPayload& payload,
                                 StatusLed& led,
                                 unsigned long sendIntervalMs,
                                 unsigned long errorRetryMs)
    : modem_(modem),
      http_(httpClient),
      payload_(payload),
      led_(led),
      send_interval_ms_(sendIntervalMs),
      error_retry_ms_(errorRetryMs) {
}

void TelemetrySender::update(unsigned long now) {
  if (now < next_allowed_send_ms_) {
    return;
  }

  unsigned long send_start_ms = millis();
  next_allowed_send_ms_ = send_start_ms + send_interval_ms_;

  if (!modem_.ensureConnected()) {
    SerialMon.println("[LOOP] Connection not ready");
    led_.blinkError();
    next_allowed_send_ms_ = millis() + error_retry_ms_;
    return;
  }

  String payloadStr = payload_.build(seq_, send_start_ms);
  SerialMon.print("[DATA] Payload: ");
  SerialMon.println(payloadStr);

  HttpResponse resp = http_.post(RESOURCE, payloadStr);

  if (resp.statusCode == 200 || resp.statusCode == 202) {
    SerialMon.print("[LOOP] Send OK, next seq=");
    SerialMon.println(seq_ + 1);

    seq_++;
    led_.blinkSuccess();
    last_success_ms_ = now;
  } else {
    SerialMon.print("[LOOP] Send failed, will retry same seq=");
    SerialMon.println(seq_);

    led_.blinkError();
    next_allowed_send_ms_ = millis() + error_retry_ms_;
  }
}
