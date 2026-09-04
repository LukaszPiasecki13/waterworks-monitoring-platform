#pragma once

#include <Arduino.h>
#include <IHttpClient.h>

class ModemLink;
class HttpClient;

class TelemetryHttpClient : public IHttpClient {
 public:
  TelemetryHttpClient(ModemLink& modem, const char* server, int port, const char* deviceKey);
  ~TelemetryHttpClient() override;

  HttpResponse post(const char* resource, const String& payload, const String& bearerToken) override;

 private:
  ModemLink& modem_;
  const char* server_;
  int port_;
  const char* device_key_;
  HttpClient* http_;
};
