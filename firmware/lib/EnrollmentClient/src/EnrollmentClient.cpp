#include <Arduino.h>
#include <ArduinoJson.h>
#include <cstring>
#include "EnrollmentClient.h"
#include <DeviceIdentity.h>
#include <TelemetryHttpClient.h>
#include <Config.h>

#define SerialMon Serial

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
    SerialMon.println("DEVICE_ALREADY_PROVISIONED");
    return;
  }

  if (!isValidCodeFormat(code)) {
    SerialMon.println("ACTIVATION_CODE_INVALID_FORMAT");
    return;
  }

  pending_code_ = code;
  next_allowed_retry_ms_ = 0;
  SerialMon.println("ACTIVATION_CODE_ACCEPTED");
}

void EnrollmentClient::readSerial() {
  while (SerialMon.available()) {
    char c = SerialMon.read();
    SerialMon.print(c);  // Echo character normalnie

    if (c == '\n' || c == '\r') {
      if (serial_buffer_.length() > 0) {
        SerialMon.print("[ENROLL] Processing line: ");
        SerialMon.println(maskCode(serial_buffer_));
        processLine(serial_buffer_);
        serial_buffer_ = "";
      }
    } else {
      serial_buffer_ += c;
      if (serial_buffer_.length() > 64) {
        SerialMon.println("[ENROLL] Buffer overflow, dropping");
        serial_buffer_ = "";
      }
    }
  }
}

void EnrollmentClient::attemptRedeem(unsigned long nowMs) {
  if (!http_) {
    SerialMon.println("[ENROLL] HTTP client not ready, deferring redeem");
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

  SerialMon.print("[ENROLL] Redeeming for SN=");
  SerialMon.print(identity_.serialNumber());
  SerialMon.print(" code=");
  SerialMon.println(maskCode(pending_code_));

  HttpResponse resp = http_->post(ACTIVATION_RESOURCE, payload, "");

  if (resp.statusCode == 200 || resp.statusCode == 201) {
    SerialMon.println("[ENROLL] SUCCESS: activation redeemed, provisioning completed");
    identity_.markProvisioningCompleted();
    pending_code_ = "";
    return;
  }

  if (resp.statusCode == 404 || resp.statusCode == 409 || resp.statusCode == 410) {
    SerialMon.print("[ENROLL] Activation rejected (code=");
    SerialMon.print(maskCode(pending_code_));
    SerialMon.print(", status=");
    SerialMon.print(resp.statusCode);
    SerialMon.println("), a new code is required");
    pending_code_ = "";
    return;
  }

  SerialMon.print("[ENROLL] Transient error (status=");
  SerialMon.print(resp.statusCode);
  SerialMon.println("), will retry");
  next_allowed_retry_ms_ = nowMs + ACTIVATION_RETRY_INTERVAL_MS;
}

void EnrollmentClient::update(unsigned long nowMs) {
  static unsigned long lastLogMs = 0;
  if (nowMs - lastLogMs > 5000) {
    SerialMon.print("[ENROLL] update() called, pending_code_=");
    SerialMon.print(pending_code_.isEmpty() ? "empty" : maskCode(pending_code_).c_str());
    SerialMon.print(", modem_ready_=");
    SerialMon.println(modem_ready_);
    lastLogMs = nowMs;
  }

  readSerial();

  if (!pending_code_.isEmpty() && modem_ready_) {
    attemptRedeem(nowMs);
  }
}
