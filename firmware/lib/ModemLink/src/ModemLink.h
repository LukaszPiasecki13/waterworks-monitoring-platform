#pragma once

#include <HardwareSerial.h>
#include <TinyGsmClient.h>

class ModemLink {
 public:
  ModemLink(HardwareSerial& serialAT, uint32_t baudRate);

  bool init(const char* apn, const char* gprsUser, const char* gprsPass, const char* simPin = "");
  bool ensureConnected();
  bool testAT();
  TinyGsm& modem() { return *modem_; }

 private:
  HardwareSerial& serial_at_;
  uint32_t baud_rate_;
  TinyGsm* modem_;

  const char* apn_;
  const char* gprs_user_;
  const char* gprs_pass_;

  bool waitForNetwork();
  bool connectGprs();
};
