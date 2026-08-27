#pragma once

#include <Arduino.h>
#include <functional>
#include <vector>
#include "ISensor.h"

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

  String formatIso8601(uint64_t utcMs);
  void dropOldestWindow();
};
