#include <Arduino.h>
#include "ModemPower.h"

ModemPower::ModemPower(int pwrkeyPin, int resetPin, int powerEnablePin)
    : pwrkey_pin_(pwrkeyPin),
      reset_pin_(resetPin),
      power_enable_pin_(powerEnablePin) {
}

void ModemPower::powerOn() {
  if (power_enable_pin_ >= 0) {
    pinMode(power_enable_pin_, OUTPUT);
    digitalWrite(power_enable_pin_, HIGH);
    delay(500);
  }

  if (pwrkey_pin_ >= 0) {
    pinMode(pwrkey_pin_, OUTPUT);
    digitalWrite(pwrkey_pin_, HIGH);
    delay(100);
    digitalWrite(pwrkey_pin_, LOW);
    delay(1200);
    digitalWrite(pwrkey_pin_, HIGH);
    delay(3000);
  }
}

void ModemPower::hardReset() {
  if (reset_pin_ >= 0) {
    pinMode(reset_pin_, OUTPUT);
    digitalWrite(reset_pin_, HIGH);
    delay(2600);
    digitalWrite(reset_pin_, LOW);
    delay(1500);
  }

  if (pwrkey_pin_ >= 0) {
    pinMode(pwrkey_pin_, OUTPUT);
    digitalWrite(pwrkey_pin_, LOW);
    delay(3000);
    digitalWrite(pwrkey_pin_, HIGH);
    delay(1000);
    digitalWrite(pwrkey_pin_, LOW);
    delay(1000);
    digitalWrite(pwrkey_pin_, HIGH);
    delay(5000);
  }
}
