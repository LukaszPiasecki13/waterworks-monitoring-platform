#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include "StatusLed.h"

StatusLed::StatusLed(int pin) : pin_(pin), pixels_(nullptr) {
  if (pin_ < 0) return;

  if (pin_ == 48) {
    pixels_ = new Adafruit_NeoPixel(1, pin_, NEO_GRB + NEO_KHZ800);
    pixels_->begin();
    pixels_->setBrightness(255);
    pixels_->setPixelColor(0, pixels_->Color(0, 0, 0));
    pixels_->show();
  } else {
    pinMode(pin_, OUTPUT);
    digitalWrite(pin_, LOW);
  }
}

StatusLed::~StatusLed() {
  if (pixels_) delete pixels_;
}

void StatusLed::blinkSuccess() { blink(1, 80); }

void StatusLed::blinkError() { blink(3, 120); }

void StatusLed::blink(int count, int delayMs) {
  if (pin_ < 0) return;

  if (pin_ == 48) {
    for (int i = 0; i < count; i++) {
      pixels_->setPixelColor(0, pixels_->Color(0, 255, 0));
      pixels_->show();
      delay(delayMs);
      pixels_->setPixelColor(0, pixels_->Color(0, 0, 0));
      pixels_->show();
      delay(delayMs);
    }
  } else {
    for (int i = 0; i < count; i++) {
      digitalWrite(pin_, HIGH);
      delay(delayMs);
      digitalWrite(pin_, LOW);
      delay(delayMs);
    }
  }
}
