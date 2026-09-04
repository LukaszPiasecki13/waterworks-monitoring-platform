#pragma once
//
// Adaptery wiążące abstrakcje z `lib/Interfaces` z konkretną platformą ESP32.
// Leżą w `src/`, a nie w `lib/`, bo należą do punktu złożenia aplikacji
// (main.cpp) i nie mają być widoczne dla testów `env:native` — PlatformIO nie
// kompiluje `src/` przy `pio test`.
//
#include <Arduino.h>
#include <Esp.h>
#include <IClock.h>
#include <ISystemControl.h>
#include <TimeSync.h>

// IClock nad statycznym TimeSync.
class SystemClock : public IClock {
 public:
  bool isSynced() const override { return TimeSync::isSynced(); }
  uint64_t utcMs() const override { return TimeSync::getUtcTimestamp(); }
};

// ISystemControl nad ESP-IDF. Licznik restartów żyje w pamięci RTC
// (przeżywa `esp_restart()`), dlatego jest wstrzykiwany przez referencję.
class EspSystemControl : public ISystemControl {
 public:
  explicit EspSystemControl(uint32_t& restartCounter) : restart_counter_(restartCounter) {}

  void delayMs(unsigned long ms) override { delay(ms); }
  void restart() override { esp_restart(); }

  uint32_t restartCount() const override { return restart_counter_; }
  void setRestartCount(uint32_t value) override { restart_counter_ = value; }

 private:
  uint32_t& restart_counter_;
};
