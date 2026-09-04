#pragma once

#include <IModemPower.h>

class ModemPower : public IModemPower {
 public:
  ModemPower(int pwrkeyPin, int resetPin, int powerEnablePin = -1);

  void powerOn() override;
  void hardReset() override;

 private:
  int pwrkey_pin_;
  int reset_pin_;
  int power_enable_pin_;
};
