#pragma once

class ModemPower {
 public:
  ModemPower(int pwrkeyPin, int resetPin, int powerEnablePin = -1);

  void powerOn();
  void hardReset();

 private:
  int pwrkey_pin_;
  int reset_pin_;
  int power_enable_pin_;
};
