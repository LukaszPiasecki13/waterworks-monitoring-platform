#pragma once

#include <Arduino.h>
#include <functional>
#include <vector>
#include "ISensor.h"

class IStateSectionSource;

struct MeasurementWindow {
  uint64_t window_start_ms;
  uint32_t window_seconds;
  std::vector<std::pair<ISensor*, SensorReading>> readings;
};

struct ErrorItem {
  // All pointers must be string literals or have guaranteed lifetime until acknowledge() is called
  const char* code;
  const char* point_id;
  const char* severity;
  const char* message;
};

class TelemetryPayload {
 public:
  TelemetryPayload(const String& deviceId, const std::vector<ISensor*>& sensors);

  void sample(uint64_t utcMs);
  String build(uint32_t seq);
  void acknowledge();
  void setGetUtcTime(std::function<uint64_t()> getUtcTime);
  bool isReadyToSend() const;
  void addError(const char* code, const char* pointId, const char* severity, const char* message);

  // Device state read channel (B-08). One source, attached once; sections it
  // appends ride along with the packet that was going out anyway.
  void setStateSource(IStateSectionSource* source);

  // Local buffer telemetry about the local buffer — the only way the platform
  // can notice a gateway silently discarding windows.
  size_t bufferedWindows() const { return windows_buffer_.size(); }
  static constexpr size_t bufferCapacityWindows() { return RETAIN_WINDOWS_MAX; }
  uint32_t droppedWindowsTotal() const { return dropped_windows_total_; }

 private:
  static constexpr size_t WINDOWS_PER_BATCH = 4;
  static constexpr size_t RETAIN_WINDOWS_MAX = WINDOWS_PER_BATCH * 12;
  static constexpr size_t MAX_ERRORS = 64;
  static constexpr uint32_t WINDOW_SECONDS = 15;

  String device_id_;
  std::vector<ISensor*> sensors_;
  std::function<uint64_t()> getUtcTime_;

  std::vector<MeasurementWindow> windows_buffer_;
  std::vector<ErrorItem> errors_buffer_;
  size_t windows_sent_count_ = 0;
  IStateSectionSource* state_source_ = nullptr;
  bool state_sent_ = false;

  // Counts every window dropped since boot, not just the ones still described
  // by an unacknowledged error entry — the errors buffer is cleared on each
  // successful send, so it cannot carry a running total.
  uint32_t dropped_windows_total_ = 0;

  String formatIso8601(uint64_t utcMs);
  void dropOldestWindow();
};
