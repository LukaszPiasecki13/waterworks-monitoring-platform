#pragma once

#include <Arduino.h>

class DeviceIdentity;
class TelemetryHttpClient;

class EnrollmentClient {
 public:
  EnrollmentClient(DeviceIdentity& identity, TelemetryHttpClient* http = nullptr);

  // Reads Serial for "ACTIVATE <code>", and once the modem is up, attempts
  // the activation-code redeem. Call every loop() iteration; non-blocking.
  void update(unsigned long nowMs);

  // True once a code has been accepted from Serial and the modem/network
  // needs to be brought up before the redeem POST can be attempted.
  bool needsModemBringUp() const;

  // Call once main.cpp has finished bringing the modem/network up.
  void onModemReady();
  void setHttpClient(TelemetryHttpClient* http);

 private:
  DeviceIdentity& identity_;
  TelemetryHttpClient* http_;

  String serial_buffer_;
  String pending_code_;
  bool modem_ready_ = false;
  unsigned long next_allowed_retry_ms_ = 0;

  void readSerial();
  void processLine(String line);
  bool isValidCodeFormat(const String& code) const;
  void attemptRedeem(unsigned long nowMs);
  static String maskCode(const String& code);
};
