#include <Arduino.h>
#include <ArduinoJson.h>
#include <cstring>
#include "EnrollmentClient.h"
#include <DeviceIdentity.h>
#include <TelemetryHttpClient.h>
#include <Config.h>

EnrollmentClient::EnrollmentClient(DeviceIdentity& identity, TelemetryHttpClient* http)
    : identity_(identity), http_(http) {}

bool EnrollmentClient::needsModemBringUp() const { return !pending_code_.isEmpty() && !modem_ready_; }

void EnrollmentClient::onModemReady() { modem_ready_ = true; }

void EnrollmentClient::setHttpClient(TelemetryHttpClient* http) { http_ = http; }

String EnrollmentClient::maskCode(const String& code) {
  int firstDash = code.indexOf('-');
  if (firstDash < 0) {
    if (code.length() <= 4) {
      return code;
    }
    String visible = code.substring(0, 4);
    String stars;
    for (size_t i = 4; i < code.length(); i++) stars += '*';
    return visible + stars;
  }

  String visible = code.substring(0, firstDash);
  String rest = code.substring(firstDash);
  String masked;
  for (size_t i = 0; i < rest.length(); i++) {
    masked += (rest[i] == '-') ? '-' : '*';
  }
  return visible + masked;
}

bool EnrollmentClient::isValidCodeFormat(const String& code) const {
  static const char* kAllowedAlphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";  // excludes 0, O, 1, I

  int significantChars = 0;
  for (size_t i = 0; i < code.length(); i++) {
    char c = code[i];
    if (c == '-') {
      continue;
    }
    if (strchr(kAllowedAlphabet, c) == nullptr) {
      return false;
    }
    significantChars++;
  }
  return significantChars >= 10;
}

void EnrollmentClient::processLine(String line) {
  line.trim();
  if (!line.startsWith("ACTIVATE ")) {
    return;
  }

  String code = line.substring(9);
  code.trim();
  code.toUpperCase();

  if (identity_.isProvisioningCompleted()) {
    return;
  }

  if (!isValidCodeFormat(code)) {
    return;
  }

  pending_code_ = code;
  next_allowed_retry_ms_ = 0;
}

void EnrollmentClient::readSerial() {
  // Serial input disabled - migrated away from direct Serial usage
}

void EnrollmentClient::attemptRedeem(unsigned long nowMs) {
  if (!http_) {
    return;
  }

  if (nowMs < next_allowed_retry_ms_) {
    return;
  }

  JsonDocument req;
  req["serial_number"] = identity_.serialNumber();
  req["activation_code"] = pending_code_;
  req["public_key_point"] = identity_.publicKeyRawPointHex();
  String payload;
  serializeJson(req, payload);

  HttpResponse resp = http_->post(ACTIVATION_RESOURCE, payload, "");

  if (resp.statusCode == 200 || resp.statusCode == 201) {
    identity_.markProvisioningCompleted();
    pending_code_ = "";
    return;
  }

  if (resp.statusCode == 404 || resp.statusCode == 409 || resp.statusCode == 410) {
    pending_code_ = "";
    return;
  }

  next_allowed_retry_ms_ = nowMs + ACTIVATION_RETRY_INTERVAL_MS;
}

void EnrollmentClient::update(unsigned long nowMs) {
  static unsigned long lastLogMs = 0;
  if (nowMs - lastLogMs > 5000) {
    lastLogMs = nowMs;
  }

  readSerial();

  if (!pending_code_.isEmpty() && modem_ready_) {
    attemptRedeem(nowMs);
  }
}
