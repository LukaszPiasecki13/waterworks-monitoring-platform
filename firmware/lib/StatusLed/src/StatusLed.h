#pragma once

class Adafruit_NeoPixel;

class StatusLed {
 public:
  explicit StatusLed(int pin);
  ~StatusLed();

  void initializePixels();  // Call from setup() to defer NeoPixel init from global scope
  void blinkSuccess();
  void blinkError();
  void blink(int count, int delayMs);

 private:
  int pin_;
  Adafruit_NeoPixel* pixels_;
  bool pixels_initialized_ = false;
};
