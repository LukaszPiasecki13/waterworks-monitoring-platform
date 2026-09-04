#pragma once

#include <Arduino.h>

class IDeviceIdentity;
class IHttpClient;

class EnrollmentClient {
 public:
  EnrollmentClient(IDeviceIdentity& identity, IHttpClient* http = nullptr);

  // Reads Serial for "ACTIVATE <code>", and once the modem is up, attempts
  // the activation-code redeem. Call every loop() iteration; non-blocking.
  void update(unsigned long nowMs);

  // True once a code has been accepted from Serial and the modem/network
  // needs to be brought up before the redeem POST can be attempted.
  bool needsModemBringUp() const;

  // Call once main.cpp has finished bringing the modem/network up.
  void onModemReady();
  void setHttpClient(IHttpClient* http);

  // Wystawione do testów: kod aktywacyjny przyjęty z Serial, ale jeszcze
  // niezrealizowany (czyszczony po sukcesie i po trwałym odrzuceniu).
  bool hasPendingCode() const { return !pending_code_.isEmpty(); }

  // Wystawione do testów: normalnie linia wchodzi z Serial przez readSerial().
  void submitLine(const String& line) { processLine(line); }

 private:
  IDeviceIdentity& identity_;
  IHttpClient* http_;

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
