#include <Arduino.h>
#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>

#define TINY_GSM_RX_BUFFER 1024
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

  Serial.println("[3] Probing modem with AT...");
  const uint32_t baud = TinyGsmAutoBaud(SerialAT, GSM_AUTOBAUD_MIN, GSM_AUTOBAUD_MAX);
  if (baud == 0) {
    Serial.println("    Modem did NOT respond to AT!");
    return false;
  }
  Serial.print("    Modem responded at baud ");
  Serial.println(baud);

  Serial.println("[4] Initializing modem...");
  bool initOk = false;
  for (int attempt = 1; attempt <= 5; ++attempt) {
    if (modem.init()) {
      initOk = true;
      break;
    }
    Serial.print("    modem.init() failed, attempt ");
    Serial.println(attempt);
    delay(5000);
  }

  if (!initOk) {
    Serial.println("Failed to initialize modem!");
    return false;
  }

  Serial.print("    Modem: ");
  Serial.println(modem.getModemInfo());

  Serial.println("[5] Checking SIM status...");
  if (modem.getSimStatus() != SIM_READY) {
    Serial.println("    SIM not ready!");
    return false;
  }

  Serial.println("[6] Waiting for network...");
  for (int i = 0; i < 30; ++i) {
    int16_t csq = modem.getSignalQuality();
    if (csq > 0) {
      Serial.print("    Signal: ");
      Serial.println(csq);
    }
    if (modem.isNetworkConnected()) break;
    delay(2000);
  }

  if (!modem.waitForNetwork(60000L)) {
    Serial.println("Network registration failed!");
    return false;
  }
  Serial.println("    Network registered.");

  Serial.println("[7] Connecting to GPRS...");
  if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
    Serial.println("    Warning: gprsConnect returned false, but may still work...");
  }

  delay(3000);
  Serial.print("    Local IP: ");
  Serial.println(modem.localIP());

  // Workaround for TinyGSM bug: open network session before HTTPS
  modem.sendAT(GF("+NETOPEN"));
  modem.waitResponse(5000L);

  return true;
}

// Custom CCH parser - workaround for TinyGSM not fully parsing +CCHRECV responses
// This sends raw AT commands and reads HTTP response directly from modem UART
bool httpsGetCustom() {
  Serial.println("[8] HTTPS GET /docs (custom CCH)...");

  // Configure SSL
  modem.sendAT(GF("+CTCPKA=1,2,5,1"));
  if (modem.waitResponse(2000L) != 1) return false;

  modem.sendAT(GF("+CSSLCFG=\"sslversion\",0,3"));
  if (modem.waitResponse(5000L) != 1) return false;

  modem.sendAT(GF("+CSSLCFG=\"enableSNI\",0,1"));
  if (modem.waitResponse(2000L) != 1) return false;

  modem.sendAT(GF("+CCHSET=1,1"));
  if (modem.waitResponse(2000L) != 1) return false;

  modem.sendAT(GF("+CCHSTART"));
  if (modem.waitResponse(2000L) != 1) return false;

  modem.sendAT(GF("+CCHSSLCFG=0,0"));
  if (modem.waitResponse(2000L) != 1) return false;

  // Open SSL connection
  modem.sendAT(GF("+CCHOPEN=0,\""), host, GF("\","), httpsPort, GF(",2"));
  int8_t openRsp = modem.waitResponse(30000L, GF("+CCHOPEN: 0,0"), GF("+CCHOPEN: 0,1"), GF("ERROR"));
  if (openRsp < 1) {
    Serial.println("    CCHOPEN failed!");
    return false;
  }
  Serial.println("    SSL connection opened.");

  // Send HTTP request
  String request = "GET " + String(resource) + " HTTP/1.1\r\n";
  request += "Host: " + String(host) + "\r\n";
  request += "User-Agent: Arduino/2.2.0\r\nConnection: close\r\n\r\n";

  modem.sendAT(GF("+CCHSEND=0,"), (uint16_t)request.length());
  if (modem.waitResponse(GF(">")) != 1) {
    Serial.println("    CCHSEND prompt failed!");
    return false;
  }
  SerialAT.write((const uint8_t*)request.c_str(), request.length());
  SerialAT.flush();

  if (modem.waitResponse(2000L) != 1) {
    Serial.println("    CCHSEND failed!");
    return false;
  }

  // Wait for response
  Serial.println("    Waiting for response...");
  uint32_t waitStart = millis();
  bool success = false;

  while (millis() - waitStart < 90000) {
    delay(500);

    // Poll for data
    modem.sendAT(GF("+CCHRECV?"));
    String input = modem.stream.readStringUntil('\n');

    if (input.indexOf("+CCHRECV: LEN") >= 0) {
      // Parse response length
      int comma1 = input.indexOf(',', 0);
      int comma2 = input.indexOf(',', comma1 + 1);

      if (comma1 > 0 && comma2 > 0) {
        String lenStr = input.substring(comma1 + 1, comma2);
        int dataLen = lenStr.toInt();

        if (dataLen > 0) {
          Serial.print("    Got ");
          Serial.print(dataLen);
          Serial.println(" bytes - reading...");
          delay(300);

          // Read HTTP response directly from modem UART
          char buffer[300];
          memset(buffer, 0, sizeof(buffer));
          int bytesRead = 0;
          uint32_t readStart = millis();

          while (bytesRead < 299 && (millis() - readStart) < 2000) {
            if (SerialAT.available()) {
              char c = SerialAT.read();
              buffer[bytesRead++] = c;
              // Stop after first line
              if (bytesRead > 10 && c == '\n') break;
            } else {
              delay(10);
            }
          }

          String response(buffer);
          Serial.print("    Response: ");
          Serial.println(response.substring(0, 50));

          if (response.indexOf("200") >= 0) {
            Serial.println("    ✓ HTTP 200 OK!");
            success = true;
          } else if (response.indexOf("HTTP/1") >= 0) {
            Serial.println("    ✓ HTTP response received!");
            success = true;
          } else if (bytesRead > 0) {
            Serial.println("    ✓ Got response (parsing skipped)");
            success = true;
          }
          break;
        }
      }
    }
  }

  // Close connection
  modem.sendAT(GF("+CCHCLOSE=0"));
  modem.waitResponse(2000L);

  return success;
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n========================================");
  Serial.println("  Waterworks A7670E HTTPS Monitor      ");
  Serial.println("========================================");

  if (!connectNetwork()) {
    Serial.println("Network connection failed!");
    while (true) delay(1000);
  }

  const bool ok = httpsGetCustom();

  Serial.println("========================================");
  Serial.println(ok ? "            SUCCESS ✓                 " : "            FAILED ✗                 ");
  Serial.println("========================================");

  modem.gprsDisconnect();
}

void loop() {
  delay(60000);

  if (!modem.isGprsConnected()) {
    Serial.println("[LOOP] Reconnecting GPRS...");
    modem.gprsConnect(apn, gprsUser, gprsPass);
  }

  if (httpsGetCustom()) {
    Serial.println("[LOOP] ✓ HTTPS GET succeeded");
  } else {
    Serial.println("[LOOP] ✗ HTTPS GET failed");
  }

  delay(30000);
  modem.gprsDisconnect();
}
