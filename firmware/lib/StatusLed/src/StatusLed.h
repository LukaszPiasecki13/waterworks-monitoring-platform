#pragma once

class Adafruit_NeoPixel;

class StatusLed {
 public:
  explicit StatusLed(int pin);
  ~StatusLed();

  void blinkSuccess();
  void blinkError();
  void blink(int count, int delayMs);

 private:
  int pin_;
  Adafruit_NeoPixel* pixels_;
};
