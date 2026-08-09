#pragma once

#include <Arduino.h>

class ModemLink;
class HttpClient;

struct HttpResponse {
  int statusCode;
  unsigned long durationMs;
  String body;
};

class TelemetryHttpClient {
 public:
  TelemetryHttpClient(ModemLink& modem, const char* server, int port, const char* deviceKey);
  ~TelemetryHttpClient();

  HttpResponse post(const char* resource, const String& payload);

 private:
  ModemLink& modem_;
  const char* server_;
  int port_;
  const char* device_key_;
  HttpClient* http_;
};
