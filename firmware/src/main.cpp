#include <Arduino.h>

#define TINY_GSM_RX_BUFFER 1024

#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>

#define GSM_AUTOBAUD_MIN 9600
#define GSM_AUTOBAUD_MAX 115200

#define MODEM_RX 18
#define MODEM_TX 17
#define MODEM_BAUD 115200

const char apn[] = "internet";
const char gprsUser[] = "";
const char gprsPass[] = "";

const int MODEM_PWRKEY_PIN = 4;
const int MODEM_POWER_ENABLE_PIN = -1;

const char host[] = "waterworks-monitoring-platform.onrender.com";
const char resource[] = "/docs";
const uint16_t httpsPort = 443;

HardwareSerial SerialAT(1);
TinyGsm modem(SerialAT);
TinyGsmClientSecure netClient(modem);
HttpClient http(netClient, host, httpsPort);

void powerOnModem() {
  if (MODEM_POWER_ENABLE_PIN >= 0) {
    pinMode(MODEM_POWER_ENABLE_PIN, OUTPUT);
    digitalWrite(MODEM_POWER_ENABLE_PIN, HIGH);
    delay(500);
  }

  if (MODEM_PWRKEY_PIN >= 0) {
    pinMode(MODEM_PWRKEY_PIN, OUTPUT);
    digitalWrite(MODEM_PWRKEY_PIN, HIGH);
    delay(100);
    digitalWrite(MODEM_PWRKEY_PIN, LOW);
    delay(1200);
    digitalWrite(MODEM_PWRKEY_PIN, HIGH);
    delay(3000);
  }
}

bool connectNetwork() {
  Serial.println("[1] Powering modem...");
  powerOnModem();

  Serial.println("[2] Starting UART...");
  SerialAT.begin(MODEM_BAUD, SERIAL_8N1, MODEM_RX, MODEM_TX);
  delay(3000);
  TinyGsmAutoBaud(SerialAT, GSM_AUTOBAUD_MIN, GSM_AUTOBAUD_MAX);

  Serial.println("[3] Initializing modem...");
  if (!modem.restart()) {
    Serial.println("Failed to restart modem! Trying init()...");
    if (!modem.init()) {
      Serial.println("Failed to initialize modem! Halt.");
      return false;
    }
  }

  Serial.print("    Modem info: ");
  Serial.println(modem.getModemInfo());

  Serial.println("[4] Waiting for network...");
  if (!modem.waitForNetwork(60000L)) {
    Serial.println("Network fail! Halt.");
    return false;
  }
  Serial.println("    Network registered.");

  Serial.println("[5] Connecting to GPRS...");
  if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
    Serial.println("GPRS fail! Halt.");
    return false;
  }

  Serial.print("    Local IP: ");
  Serial.println(modem.localIP());
  return true;
}

bool probeDocs() {
  Serial.println("[6] Performing HTTPS GET /docs...");
  http.setHttpResponseTimeout(60000);
  http.connectionKeepAlive();  // required for HTTPS with this library

  const int connectError = http.get(resource);
  if (connectError != 0) {
    Serial.print("    HTTP connect failed, err = ");
    Serial.println(connectError);
    return false;
  }

  const int statusCode = http.responseStatusCode();
  Serial.print("    HTTP status: ");
  Serial.println(statusCode);

  if (statusCode <= 0) {
    http.stop();
    return false;
  }

  String body = http.responseBody();
  Serial.print("    Body length: ");
  Serial.println(body.length());
  Serial.println("    First 200 chars:");
  Serial.println(body.substring(0, 200));

  http.stop();
  return statusCode == 200;
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n========================================");
  Serial.println("       A7670E HTTPS PROBE               ");
  Serial.println("========================================");

  if (!connectNetwork()) {
    while (true) {
      delay(1000);
    }
  }

  const bool ok = probeDocs();
  Serial.println("========================================");
  Serial.println(ok ? "            GET /docs OK              " : "         GET /docs FAILED             ");
  Serial.println("========================================");

  modem.gprsDisconnect();
}

void loop() {
  delay(60000);

  if (modem.isGprsConnected()) {
    return;
  }

  if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
    Serial.println("Retry GPRS failed.");
    return;
  }

  probeDocs();
  modem.gprsDisconnect();
}
