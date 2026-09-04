#pragma once

// Szew nad sterowaniem zasilaniem modemu (PWRKEY/RESET). Używany przez Watchdog.
class IModemPower {
 public:
  virtual ~IModemPower() = default;

  virtual void powerOn() = 0;
  virtual void hardReset() = 0;
};
