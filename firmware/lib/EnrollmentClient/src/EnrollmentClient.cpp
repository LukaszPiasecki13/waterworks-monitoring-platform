#include <Arduino.h>
#include <ArduinoJson.h>
#include <cstring>
#include "EnrollmentClient.h"
#include <Config.h>
#include <IDeviceIdentity.h>
#include <IHttpClient.h>
#include <Logger.h>

EnrollmentClient::EnrollmentClient(IDeviceIdentity& identity, IHttpClient* http)
    : identity_(identity), http_(http) {}

bool EnrollmentClient::needsModemBringUp() const { return !pending_code_.isEmpty() && !modem_ready_; }

void EnrollmentClient::onModemReady() { modem_ready_ = true; }

void EnrollmentClient::setHttpClient(IHttpClient* http) { http_ = http; }

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
  retry_pending_ = false;
}

void EnrollmentClient::readSerial() {
  // Jedyna droga wprowadzenia kodu aktywacyjnego do urządzenia
  // (patrz docs/technical/firmware/04_device_provisioning_flow.md, faza B).
  while (Serial.available()) {
    char c = static_cast<char>(Serial.read());

    if (c == '\n' || c == '\r') {
      if (!serial_buffer_.isEmpty()) {
        // Kod logowany wyłącznie zamaskowany — pełny nie może trafić do logu.
        LOG_INFO("[ENROLL]", "Odebrano linię: %s", maskCode(serial_buffer_).c_str());
        processLine(serial_buffer_);
        serial_buffer_ = "";
      }
      continue;
    }

    serial_buffer_ += c;
    if (serial_buffer_.length() > SERIAL_LINE_MAX) {
      LOG_WARN("[ENROLL]", "Przepełnienie bufora linii, odrzucono");
      serial_buffer_ = "";
    }
  }
}

void EnrollmentClient::attemptRedeem(unsigned long nowMs) {
  if (!http_) {
    return;
  }

  // Odporne na przewinięcie millis() (co ~49,7 dnia): różnica bez znaku
  // jest poprawna także wtedy, gdy licznik przeskoczył przez zero.
  if (retry_pending_ && (long)(nowMs - next_allowed_retry_ms_) < 0) {
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
  retry_pending_ = true;
}

void EnrollmentClient::update(unsigned long nowMs) {
  readSerial();

  if (!pending_code_.isEmpty() && modem_ready_) {
    attemptRedeem(nowMs);
  }
}
