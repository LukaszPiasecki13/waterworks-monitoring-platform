#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>
#include "TelemetryHttpClient.h"
#include "ModemLink.h"

#define SerialMon Serial

TelemetryHttpClient::TelemetryHttpClient(ModemLink& modem, const char* server, int port, const char* deviceKey)
    : modem_(modem),
      server_(server),
      port_(port),
      device_key_(deviceKey),
      http_(nullptr) {
  TinyGsmClientSecure* client = new TinyGsmClientSecure(modem_.modem());
  http_ = new HttpClient(*client, server_, port_);
}

TelemetryHttpClient::~TelemetryHttpClient() {
  if (http_) {
    delete http_;
  }
}

HttpResponse TelemetryHttpClient::post(const char* resource, const String& payload) {
  HttpResponse resp = {-1, 0, ""};

  SerialMon.print("[HTTP] POST size=");
  SerialMon.println(payload.length());

  unsigned long startMs = millis();

  http_->stop();
  http_->setHttpResponseTimeout(30000);
  http_->connectionKeepAlive();

  http_->beginRequest();
  http_->post(resource);
  http_->sendHeader("Content-Type", "application/json");
  http_->sendHeader("Accept", "application/json");
  http_->sendHeader("X-Device-Key", device_key_);
  http_->sendHeader("Content-Length", payload.length());
  http_->beginBody();
  http_->print(payload);
  http_->endRequest();

  resp.statusCode = http_->responseStatusCode();
  resp.body = http_->responseBody();
  resp.durationMs = millis() - startMs;

  SerialMon.print("[HTTP] Status: ");
  SerialMon.println(resp.statusCode);

  SerialMon.print("[HTTP] Duration ms: ");
  SerialMon.println(resp.durationMs);

  SerialMon.print("[HTTP] Response: ");
  SerialMon.println(resp.body);

  http_->stop();

  return resp;
}
