#include <TinyGsmClient.h>
#include <Config.h>
#include <esp_task_wdt.h>
#include <Logger.h>
#include "ModemLink.h"

ModemLink::ModemLink(HardwareSerial& serialAT, uint32_t baudRate)
    : serial_at_(serialAT), baud_rate_(baudRate), modem_(nullptr) {}

bool ModemLink::init(const char* apn, const char* gprsUser, const char* gprsPass, const char* simPin) {
  apn_ = apn;
  gprs_user_ = gprsUser;
  gprs_pass_ = gprsPass;

  LOG_INFO("[MODEM]", "Starting UART...");
  esp_task_wdt_reset();
  serial_at_.begin(baud_rate_, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
  delay(5000);
  esp_task_wdt_reset();

  LOG_INFO("[MODEM]", "Clearing RX buffer...");
  delay(500);
  esp_task_wdt_reset();
  while (serial_at_.available()) {
    serial_at_.read();
  }
  delay(500);
  esp_task_wdt_reset();

  LOG_INFO("[MODEM]", "Auto-bauding...");
  TinyGsmAutoBaud(serial_at_, 9600, 115200);
  delay(1000);
  esp_task_wdt_reset();

  modem_ = new TinyGsm(serial_at_);

  LOG_INFO("[MODEM]", "Initializing modem (modem.init())...");
  unsigned long initStart = millis();
  bool initOk = false;
  int initAttempts = 0;
  while (millis() - initStart < 10000) {
    initAttempts++;
    LOG_INFO("[MODEM]", "Init attempt %d", initAttempts);
    esp_task_wdt_reset();
    if (modem_->init()) {
      initOk = true;
      LOG_INFO("[MODEM]", "Init OK");
      break;
    }
    LOG_WARN("[MODEM]", "Init failed, elapsed: %lu ms", millis() - initStart);
    delay(500);
  }

  if (!initOk) {
    LOG_ERROR("[MODEM]", "modem.init() failed after all attempts");
    return false;
  }

  LOG_INFO("[MODEM]", "Getting modem info...");
  String modemInfo = modem_->getModemInfo();
  LOG_INFO("[MODEM]", "Info: %s", modemInfo.c_str());

  if (strlen(simPin) > 0) {
    LOG_INFO("[MODEM]", "Unlocking SIM...");
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
  LOG_INFO("[NET]", "Waiting for network (timeout 60s)...");
  unsigned long netStart = millis();
  bool netOk = false;

  while (millis() - netStart < 60000) {
    if (modem_->waitForNetwork(5000L)) {
      netOk = true;
      break;
    }
    esp_task_wdt_reset();
    LOG_DEBUG("[NET]", ".");
  }

  if (!netOk) {
    LOG_ERROR("[NET]", "Network connection timeout");
    return false;
  }

  if (!modem_->isNetworkConnected()) {
    LOG_ERROR("[NET]", "Network not connected");
    return false;
  }

  LOG_INFO("[NET]", "Network connected");

  int signal = modem_->getSignalQuality();
  LOG_INFO("[NET]", "Signal quality: %d", signal);

  return true;
}

bool ModemLink::connectGprs() {
  LOG_INFO("[DATA]", "Connecting GPRS/LTE (timeout 30s)...");
  unsigned long gprsStart = millis();
  bool gprsOk = false;

  while (millis() - gprsStart < 30000) {
    if (modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
      gprsOk = true;
      break;
    }
    esp_task_wdt_reset();
    LOG_DEBUG("[NET]", ".");
    delay(500);
  }

  if (!gprsOk) {
    LOG_ERROR("[DATA]", "GPRS/LTE connection timeout");
    return false;
  }

  if (!modem_->isGprsConnected()) {
    LOG_ERROR("[DATA]", "GPRS/LTE not connected");
    return false;
  }

  LOG_INFO("[DATA]", "GPRS/LTE connected");
  LOG_INFO("[DATA]", "Local IP: %s", modem_->localIP().toString().c_str());

  return true;
}

bool ModemLink::ensureConnected() {
  if (!modem_->isNetworkConnected()) {
    LOG_WARN("[NET]", "Network lost, reconnecting...");

    esp_task_wdt_reset();
    if (!modem_->waitForNetwork(60000L)) {
      esp_task_wdt_reset();
      LOG_ERROR("[NET]", "Reconnect network failed");
      return false;
    }
    esp_task_wdt_reset();
  }

  if (!modem_->isGprsConnected()) {
    LOG_WARN("[DATA]", "GPRS/LTE lost, reconnecting APN...");
    modem_->gprsDisconnect();
    esp_task_wdt_reset();
    delay(1000);
    esp_task_wdt_reset();

    if (!modem_->gprsConnect(apn_, gprs_user_, gprs_pass_)) {
      esp_task_wdt_reset();
      LOG_ERROR("[DATA]", "Reconnect APN failed");
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
