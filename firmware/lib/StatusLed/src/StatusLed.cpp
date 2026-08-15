#include <Arduino.h>
#include "StatusLed.h"

StatusLed::StatusLed(int pin) : pin_(pin) {
  if (pin_ >= 0) {
    pinMode(pin_, OUTPUT);
    digitalWrite(pin_, LOW);
  }
}

void StatusLed::blinkSuccess() { blink(1, 80); }

void StatusLed::blinkError() { blink(3, 120); }

void StatusLed::blink(int count, int delayMs) {
  if (pin_ < 0) {
    return;
  }

  for (int i = 0; i < count; i++) {
    digitalWrite(pin_, HIGH);
    delay(delayMs);
    digitalWrite(pin_, LOW);
    delay(delayMs);
  }
}
