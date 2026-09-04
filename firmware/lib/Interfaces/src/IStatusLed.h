#pragma once

// Szew nad diodą statusu. Pozwala testować TelemetrySender bez NeoPixela
// i sprawdzać, że sukces/błąd wysyłki są sygnalizowane.
class IStatusLed {
 public:
  virtual ~IStatusLed() = default;

  virtual void blinkSuccess() = 0;
  virtual void blinkError() = 0;
};
