#pragma once

class StatusLed {
 public:
  explicit StatusLed(int pin);

  void blinkSuccess();
  void blinkError();
  void blink(int count, int delayMs);

 private:
  int pin_;
};
