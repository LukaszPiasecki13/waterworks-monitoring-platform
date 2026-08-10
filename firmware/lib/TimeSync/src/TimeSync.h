#pragma once

#include <Arduino.h>
#include <cstdint>

class ModemLink;

class TimeSync {
 public:
  static void init();
  static bool sync(ModemLink& modemLink);
  static uint64_t getUtcTimestamp();
  static bool isSynced();
  static uint32_t getLastSyncMs();

 private:
  static bool synced_;
  static uint32_t lastSyncMs_;
};
