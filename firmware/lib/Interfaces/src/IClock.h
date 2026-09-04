#pragma once

#include <cstdint>

// Szew nad czasem UTC. Produkcyjnie opakowuje statyczny TimeSync (SystemClock),
// w testach pozwala ustawić dowolny moment i stan synchronizacji bez modemu.
class IClock {
 public:
  virtual ~IClock() = default;

  // Czy czas został zsynchronizowany z siecią; bez tego znaczniki czasu w
  // payloadzie byłyby liczone od startu urządzenia (błąd „1970").
  virtual bool isSynced() const = 0;

  // Bieżący czas UTC w milisekundach; 0 gdy brak synchronizacji.
  virtual uint64_t utcMs() const = 0;

  // Bieżący czas UTC w sekundach — używany do porównań z ważnością tokenu.
  // Uwaga: uint32_t obcina znacznik do 2106 roku (świadome ograniczenie).
  uint32_t utcSeconds() const { return static_cast<uint32_t>(utcMs() / 1000); }
};
