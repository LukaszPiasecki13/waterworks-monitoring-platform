#include "TimeSync.h"
#include <ModemLink.h>
#include <sys/time.h>
#include <time.h>
#include <Arduino.h>
#include <Logger.h>

extern RTC_DATA_ATTR uint32_t rtcSyncedTimeUtcSec;
extern RTC_DATA_ATTR uint32_t rtcSyncMillis;

bool TimeSync::synced_ = false;
uint32_t TimeSync::lastSyncMs_ = 0;

void TimeSync::init() {
  synced_ = false;
  lastSyncMs_ = 0;
}

bool TimeSync::sync(ModemLink& modemLink) {
  TinyGsm& modem = modemLink.modem();

  LOG_INFO("[TIME]", "Attempting NTP sync via pool.ntp.org...");
  bool ntpSuccess = modem.NTPServerSync("pool.ntp.org", 0);
  if (!ntpSuccess) {
    LOG_INFO("[TIME]", "NTPServerSync via pool.ntp.org FAILED, trying time.nist.gov...");
    ntpSuccess = modem.NTPServerSync("time.nist.gov", 0);
    if (!ntpSuccess) {
      LOG_INFO("[TIME]", "NTPServerSync via time.nist.gov also FAILED");
      LOG_INFO("[TIME]", "Will try reading modem's cached time...");
    }
  } else {
    LOG_INFO("[TIME]", "NTPServerSync OK");
  }

  delay(500);  // Give modem time to process

  int year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0;
  float tz = 0.0f;
  LOG_INFO("[TIME]", "Reading network time from modem...");
  if (!modem.getNetworkTime(&year, &month, &day, &hour, &minute, &second, &tz)) {
    LOG_INFO("[TIME]", "getNetworkTime FAILED - no time available");
    return false;
  }

  if (year < 2020) {
    LOG_WARN("[TIME]", "Got invalid time from modem (year=%d) - retrying", year);
    delay(1000);
    if (!modem.getNetworkTime(&year, &month, &day, &hour, &minute, &second, &tz)) {
      LOG_INFO("[TIME]", "Retry failed");
      return false;
    }
  }

  LOG_INFO("[TIME]", "Got valid time: %04d-%02d-%02d %02d:%02d:%02d TZ:%.1f", year, month, day, hour, minute, second,
           tz);

  struct tm timeinfo = {};
  timeinfo.tm_year = year - 1900;
  timeinfo.tm_mon = month - 1;
  timeinfo.tm_mday = day;
  timeinfo.tm_hour = hour;
  timeinfo.tm_min = minute;
  timeinfo.tm_sec = second;
  timeinfo.tm_isdst = 0;

  time_t utc_time = mktime(&timeinfo);
  if (utc_time < 0) {
    return false;
  }

  struct timeval tv;
  tv.tv_sec = utc_time;
  tv.tv_usec = 0;
  settimeofday(&tv, nullptr);

  rtcSyncedTimeUtcSec = (uint32_t)utc_time;
  rtcSyncMillis = millis();
  lastSyncMs_ = rtcSyncMillis;
  synced_ = true;

  return true;
}

uint64_t TimeSync::getUtcTimestamp() {
  if (!synced_ || rtcSyncedTimeUtcSec == 0) {
    return 0;
  }

  uint32_t elapsed_ms = millis() - rtcSyncMillis;
  uint64_t current_utc_ms = ((uint64_t)rtcSyncedTimeUtcSec * 1000) + elapsed_ms;
  return current_utc_ms;
}

bool TimeSync::isSynced() { return synced_; }

uint32_t TimeSync::getLastSyncMs() { return lastSyncMs_; }
