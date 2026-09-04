#pragma once

#include <HardwareSerial.h>
#include <IModemLink.h>
#include <TinyGsmClient.h>

class ModemLink : public IModemLink {
 public:
  ModemLink(HardwareSerial& serialAT, uint32_t baudRate);

  bool init(const char* apn, const char* gprsUser, const char* gprsPass, const char* simPin = "");
  bool ensureConnected() override;
  bool testAT() override;

  // Surowy uchwyt TinyGSM — celowo poza IModemLink. Potrzebują go tylko
  // TelemetryHttpClient (klient TLS) i TimeSync (NTP/czas sieci).
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
