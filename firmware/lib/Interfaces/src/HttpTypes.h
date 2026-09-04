#pragma once

#include <Arduino.h>

// Odpowiedź HTTP w postaci, w jakiej widzą ją moduły wyższego poziomu.
// statusCode == -1 oznacza brak odpowiedzi (błąd transportu/timeout).
struct HttpResponse {
  int statusCode;
  unsigned long durationMs;
  String body;
};
