#include <TinyGsmClient.h>
#include <Config.h>
#include <esp_task_wdt.h>
#include "ModemLink.h"

#define SerialMon Serial

ModemLink::ModemLink(HardwareSerial& serialAT, uint32_t baudRate)
    : serial_at_(serialAT), baud_rate_(baudRate), modem_(nullptr) {}

bool ModemLink::init(const char* apn, const char* gprsUser, const char* gprsPass, const char* simPin) {
  apn_ = apn;
  gprs_user_ = gprsUser;
  gprs_pass_ = gprsPass;

  SerialMon.println("[MODEM] Starting UART...");
  esp_task_wdt_reset();
  serial_at_.begin(baud_rate_, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
  delay(5000);
  esp_task_wdt_reset();

  SerialMon.println("[MODEM] Clearing RX buffer...");
  delay(500);
  esp_task_wdt_reset();
  while (serial_at_.available()) {
    serial_at_.read();
  }
  delay(500);
  esp_task_wdt_reset();

  SerialMon.println("[MODEM] Auto-bauding...");
  TinyGsmAutoBaud(serial_at_, 9600, 115200);
  delay(1000);
  esp_task_wdt_reset();

  modem_ = new TinyGsm(serial_at_);

  SerialMon.println("[MODEM] Initializing modem (modem.init())...");
  unsigned long initStart = millis();
  bool initOk = false;
  int initAttempts = 0;
  while (millis() - initStart < 10000) {
    initAttempts++;
    SerialMon.print("[MODEM] Init attempt ");
    SerialMon.println(initAttempts);
    esp_task_wdt_reset();
    if (modem_->init()) {
      initOk = true;
      SerialMon.println("[MODEM] Init OK");
      break;
    }
    SerialMon.print("[MODEM] Init failed, elapsed: ");
    SerialMon.print(millis() - initStart);
    SerialMon.println("ms");
    delay(500);
  }

  if (!initOk) {
    SerialMon.println("[MODEM] modem.init() failed after all attempts");
    return false;
  }

  SerialMon.println("[MODEM] Getting modem info...");
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
  SerialMon.println("[NET] Waiting for network (timeout 60s)...");
  unsigned long netStart = millis();
  bool netOk = false;

  while (millis() - netStart < 60000) {
    if (modem_->waitForNetwork(5000L)) {
      netOk = true;
      break;
    }
    esp_task_wdt_reset();
    SerialMon.print(".");
  }

  if (!netOk) {
    SerialMon.println();
    SerialMon.println("[NET] Network connection timeout");
    return false;
  }

  SerialMon.println();

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
  SerialMon.println("[DATA] Connecting GPRS/LTE (timeout 30s)...");
  unsigned long gprsStart = millis();
  bool gprsOk = false;

  while (millis() - gprsStart < 30000) {
    if (modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
      gprsOk = true;
      break;
    }
    esp_task_wdt_reset();
    SerialMon.print(".");
    delay(500);
  }

  if (!gprsOk) {
    SerialMon.println();
    SerialMon.println("[DATA] GPRS/LTE connection timeout");
    return false;
  }

  SerialMon.println();

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

    esp_task_wdt_reset();
    if (!modem_->waitForNetwork(60000L)) {
      esp_task_wdt_reset();
      SerialMon.println("[NET] Reconnect network failed");
      return false;
    }
    esp_task_wdt_reset();
  }

  if (!modem_->isGprsConnected()) {
    SerialMon.println("[DATA] GPRS/LTE lost, reconnecting APN...");
    modem_->gprsDisconnect();
    esp_task_wdt_reset();
    delay(1000);
    esp_task_wdt_reset();

    if (!modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
      esp_task_wdt_reset();
      SerialMon.println("[DATA] Reconnect APN failed");
      return false;
    }
    esp_task_wdt_reset();
  }

  return true;
}

bool ModemLink::testAT() {
  if (!modem_) {
    return false;
  }
  return modem_->testAT();
}
