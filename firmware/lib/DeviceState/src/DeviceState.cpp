#include "DeviceState.h"

namespace device_state {

const char* restartReasonName(RestartReason reason) {
  switch (reason) {
    case RestartReason::PowerOn:
      return "power_on";
    case RestartReason::External:
      return "external";
    case RestartReason::Software:
      return "software";
    case RestartReason::Panic:
      return "panic";
    case RestartReason::IntWatchdog:
      return "int_watchdog";
    case RestartReason::TaskWatchdog:
      return "task_watchdog";
    case RestartReason::OtherWatchdog:
      return "other_watchdog";
    case RestartReason::DeepSleep:
      return "deep_sleep";
    case RestartReason::Brownout:
      return "brownout";
    case RestartReason::Sdio:
      return "sdio";
    case RestartReason::Unknown:
    default:
      return "unknown";
  }
}

RestartReason restartReasonFromCode(int code) {
  if (code < static_cast<int>(RestartReason::Unknown) || code > static_cast<int>(RestartReason::Sdio)) {
    return RestartReason::Unknown;
  }
  return static_cast<RestartReason>(code);
}

int32_t rssiDbmFromCsq(int csq) {
  // AT+CSQ maps 0..31 linearly onto -113..-51 dBm; 99 means "not detectable",
  // and any other value is a modem answering something we do not understand.
  if (csq < 0 || csq > 31) {
    return RSSI_UNKNOWN;
  }
  return -113 + 2 * csq;
}

ReportScheduler::ReportScheduler(uint32_t intervalMs) : interval_ms_(intervalMs) {}

bool ReportScheduler::shouldReport(uint32_t nowMs) const {
  if (!has_reported_) {
    return true;
  }
  // Unsigned subtraction, so a millis() rollover after ~49 days still yields
  // the elapsed time rather than a half-century of "not yet".
  return (nowMs - last_report_ms_) >= interval_ms_;
}

void ReportScheduler::markReported(uint32_t nowMs) {
  last_report_ms_ = nowMs;
  has_reported_ = true;
}

}  // namespace device_state
