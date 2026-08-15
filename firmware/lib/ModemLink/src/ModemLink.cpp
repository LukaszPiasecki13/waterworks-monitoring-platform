#include <TinyGsmClient.h>
#include <Config.h>
#include "ModemLink.h"

#define SerialMon Serial

ModemLink::ModemLink(HardwareSerial& serialAT, uint32_t baudRate)
    : serial_at_(serialAT), baud_rate_(baudRate), modem_(nullptr) {}

bool ModemLink::init(const char* apn, const char* gprsUser, const char* gprsPass, const char* simPin) {
  apn_ = apn;
  gprs_user_ = gprsUser;
  gprs_pass_ = gprsPass;

  SerialMon.println("[MODEM] Starting UART...");
  serial_at_.begin(baud_rate_, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
  delay(3000);
  TinyGsmAutoBaud(serial_at_, 9600, 115200);

  SerialMon.println("[MODEM] Initializing modem...");
  modem_ = new TinyGsm(serial_at_);

  if (!modem_->restart()) {
    SerialMon.println("[MODEM] modem.restart() failed, trying init()...");
    if (!modem_->init()) {
      SerialMon.println("[MODEM] modem.init() failed");
      return false;
    }
  }

  String modemInfo = modem_->getModemInfo();
  SerialMon.print("[MODEM] Info: ");
  SerialMon.println(modemInfo);

  if (strlen(simPin) > 0) {
    SerialMon.println("[MODEM] Unlocking SIM...");
    modem_->simUnlock(simPin);
  }

  if (!waitForNetwork()) {
    return false;
  }

  if (!connectGprs()) {
    return false;
  }

  return true;
}

bool ModemLink::waitForNetwork() {
  SerialMon.println("[NET] Waiting for network...");

  if (!modem_->waitForNetwork(60000L)) {
    SerialMon.println("[NET] waitForNetwork() failed");
    return false;
  }

  if (!modem_->isNetworkConnected()) {
    SerialMon.println("[NET] Network not connected");
    return false;
  }

  SerialMon.println("[NET] Network connected");

  int signal = modem_->getSignalQuality();
  SerialMon.print("[NET] Signal quality: ");
  SerialMon.println(signal);

  return true;
}

bool ModemLink::connectGprs() {
  SerialMon.println("[DATA] Connecting GPRS/LTE...");

  if (!modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
    SerialMon.println("[DATA] gprsConnect() failed");
    return false;
  }

  if (!modem_->isGprsConnected()) {
    SerialMon.println("[DATA] GPRS/LTE not connected");
    return false;
  }

  SerialMon.println("[DATA] GPRS/LTE connected");
  SerialMon.print("[DATA] Local IP: ");
  SerialMon.println(modem_->localIP());

  return true;
}

bool ModemLink::ensureConnected() {
  if (!modem_->isNetworkConnected()) {
    SerialMon.println("[NET] Network lost, reconnecting...");

    if (!modem_->waitForNetwork(60000L)) {
      SerialMon.println("[NET] Reconnect network failed");
      return false;
    }
  }

  if (!modem_->isGprsConnected()) {
    SerialMon.println("[DATA] GPRS/LTE lost, reconnecting APN...");
    modem_->gprsDisconnect();
    delay(1000);

    if (!modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
      SerialMon.println("[DATA] Reconnect APN failed");
      return false;
    }
  }

  return true;
}

bool ModemLink::testAT() {
  if (!modem_) {
    return false;
  }
  return modem_->testAT();
}
