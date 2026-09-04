#pragma once

// Wąski szew: Watchdog potrzebuje z TelemetrySendera jednej informacji —
// czy ostatni błąd wysyłki był trwały (403/409/410). Pełna zależność od
// TelemetrySendera wciągnęłaby do testu Watchdoga cały stos wysyłkowy.
class ITelemetryHealth {
 public:
  virtual ~ITelemetryHealth() = default;

  virtual bool lastErrorWasPermanent() const = 0;
};
