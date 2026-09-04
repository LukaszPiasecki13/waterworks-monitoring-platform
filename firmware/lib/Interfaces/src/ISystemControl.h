#pragma once

#include <cstdint>

// Szew nad operacjami, które w testach nie mogą się wydarzyć naprawdę:
// restartem układu i licznikiem restartów trzymanym w pamięci RTC.
class ISystemControl {
 public:
  virtual ~ISystemControl() = default;

  virtual void delayMs(unsigned long ms) = 0;
  virtual void restart() = 0;

  virtual uint32_t restartCount() const = 0;
  virtual void setRestartCount(uint32_t value) = 0;
};
