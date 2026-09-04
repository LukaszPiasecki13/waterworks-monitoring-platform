#pragma once

#include <IStatusLed.h>

class Adafruit_NeoPixel;

class StatusLed : public IStatusLed {
 public:
  explicit StatusLed(int pin);
  ~StatusLed() override;

  void initializePixels();  // Call from setup() to defer NeoPixel init from global scope
  void blinkSuccess() override;
  void blinkError() override;
  void blink(int count, int delayMs);

 private:
  int pin_;
  Adafruit_NeoPixel* pixels_;
  bool pixels_initialized_ = false;
};
