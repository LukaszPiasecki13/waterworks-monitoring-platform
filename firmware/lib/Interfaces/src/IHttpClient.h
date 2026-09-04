#pragma once

#include <Arduino.h>
#include "HttpTypes.h"

// Szew nad warstwą HTTP. Produkcyjnie implementuje go TelemetryHttpClient
// (TinyGSM + ArduinoHttpClient); w testach `native` — atrapa ze skryptem
// odpowiedzi. Dzięki niemu TelemetrySender, DeviceAuthClient i EnrollmentClient
// są testowalne bez modemu.
class IHttpClient {
 public:
  virtual ~IHttpClient() = default;

  virtual HttpResponse post(const char* resource, const String& payload, const String& bearerToken) = 0;
};
