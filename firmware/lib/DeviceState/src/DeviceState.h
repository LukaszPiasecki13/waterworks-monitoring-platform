#pragma once

#include <stddef.h>
#include <stdint.h>

// Device state read channel (B-08).
//
// The gateway sits behind carrier NAT, so the backend can never pull from it.
// Every read is therefore answered by the device on its next contact, as a
// *section* attached to the telemetry packet it was going to send anyway.
//
// This header is deliberately free of Arduino, ESP-IDF and ArduinoJson: the
// snapshot shape, the restart-reason mapping and the reporting cadence are the
// parts worth testing on `env:native`, and none of them need hardware.

namespace device_state {

// Reported when the modem gives no usable signal reading (CSQ 99 or out of
// range). Serialised as an omitted field, never as a fake -113 dBm.
inline constexpr int32_t RSSI_UNKNOWN = INT32_MIN;

// Numeric values mirror esp_reset_reason_t; main.cpp static_asserts the match
// so a future ESP-IDF renumbering fails the build instead of mislabelling
// every restart in the field.
enum class RestartReason : uint8_t {
  Unknown = 0,
  PowerOn = 1,
  External = 2,
  Software = 3,
  Panic = 4,
  IntWatchdog = 5,
  TaskWatchdog = 6,
  OtherWatchdog = 7,
  DeepSleep = 8,
  Brownout = 9,
  Sdio = 10,
};

// Wire names, matching the backend's accepted set.
const char* restartReasonName(RestartReason reason);

// Anything outside the known range maps to Unknown rather than to a wrong
// label — an unrecognised restart is still a fact worth reporting.
RestartReason restartReasonFromCode(int code);

// Convert a modem CSQ reading (0..31, 99 = unknown) into dBm.
int32_t rssiDbmFromCsq(int csq);

struct Snapshot {
  const char* serial_number = "";
  const char* firmware_version = "";
  int registry_schema_version = 0;

  uint32_t uptime_seconds = 0;
  uint32_t restart_count = 0;
  RestartReason restart_reason = RestartReason::Unknown;

  int32_t rssi_dbm = RSSI_UNKNOWN;

  uint32_t free_heap_bytes = 0;
  uint32_t min_free_heap_bytes = 0;

  // Local buffer state. The platform promises 72 h of offline retention while
  // the device holds roughly 12 minutes in RAM, so without these three fields
  // nobody can tell that a gateway is quietly dropping windows.
  uint32_t buffer_windows_used = 0;
  uint32_t buffer_windows_capacity = 0;
  uint32_t buffer_windows_dropped = 0;
};

// Decides *when* a state section rides along. Attaching state to every packet
// would multiply its cost by the transmission rate; attaching it on a fixed
// wall-clock interval keeps the cost flat no matter how the telemetry cadence
// is retuned later.
class ReportScheduler {
 public:
  explicit ReportScheduler(uint32_t intervalMs);

  // True until the first report of this boot, then once per interval.
  bool shouldReport(uint32_t nowMs) const;

  void markReported(uint32_t nowMs);

  bool hasReported() const { return has_reported_; }

 private:
  uint32_t interval_ms_;
  uint32_t last_report_ms_ = 0;
  bool has_reported_ = false;
};

}  // namespace device_state
