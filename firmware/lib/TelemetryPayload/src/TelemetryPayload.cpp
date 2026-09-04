#include <ArduinoJson.h>
#include <time.h>
#include "TelemetryPayload.h"
#include "Config.h"
#include <IStateSectionSource.h>
#include <Logger.h>

TelemetryPayload::TelemetryPayload(const String& deviceId, const std::vector<ISensor*>& sensors)
    : device_id_(deviceId), sensors_(sensors), getUtcTime_(nullptr) {
  for (auto sensor : sensors_) {
    if (sensor && !sensor->init()) {
      LOG_ERROR(sensor->getTag(), "Failed to initialize");
    }
  }
}

String TelemetryPayload::formatIso8601(uint64_t utcMs) {
  if (utcMs == 0) {
    return "";
  }

  time_t seconds = utcMs / 1000;
  uint32_t ms = utcMs % 1000;

  struct tm timeinfo;
  gmtime_r(&seconds, &timeinfo);

  char buffer[30];
  snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03luZ", timeinfo.tm_year + 1900, timeinfo.tm_mon + 1,
           timeinfo.tm_mday, timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec, (unsigned long)ms);

  return String(buffer);
}

void TelemetryPayload::sample(uint64_t utcMs) {
  if (windows_buffer_.size() >= RETAIN_WINDOWS_MAX) {
    dropOldestWindow();
    dropped_windows_total_++;
    addError("WINDOW_DROPPED_BUFFER_FULL", nullptr, "warning", "Buffer full");
  }

  MeasurementWindow window;
  window.window_start_ms = utcMs;
  window.window_seconds = WINDOW_SECONDS;

  for (auto sensor : sensors_) {
    if (sensor) {
      SensorReading reading = sensor->read();
      window.readings.push_back({sensor, reading});
    }
  }

  windows_buffer_.push_back(window);
}

void TelemetryPayload::dropOldestWindow() {
  if (!windows_buffer_.empty()) {
    windows_buffer_.erase(windows_buffer_.begin());
  }
}

bool TelemetryPayload::isReadyToSend() const { return windows_buffer_.size() >= WINDOWS_PER_BATCH; }

String TelemetryPayload::build(uint32_t seq) {
  JsonDocument doc;

  doc["v"] = 2;
  doc["device_id"] = device_id_;
  doc["seq"] = seq;

  uint64_t utcMs = getUtcTime_ ? getUtcTime_() : 0;
  String sentAt = formatIso8601(utcMs);
  doc["sent_at"] = sentAt;

  JsonArray windowsArr = doc["windows"].to<JsonArray>();
  for (size_t i = 0; i < WINDOWS_PER_BATCH && i < windows_buffer_.size(); ++i) {
    const MeasurementWindow& w = windows_buffer_[i];
    JsonObject windowObj = windowsArr.add<JsonObject>();

    String windowStart = formatIso8601(w.window_start_ms);
    windowObj["window_start"] = windowStart;
    windowObj["window_seconds"] = w.window_seconds;

    JsonArray pointsArr = windowObj["points"].to<JsonArray>();
    for (const auto& [sensor, reading] : w.readings) {
      if (reading.ok) {
        JsonObject pointObj = pointsArr.add<JsonObject>();
        pointObj["point_id"] = sensor->pointId();
        pointObj["type"] = sensor->pointType();
        pointObj["unit"] = sensor->unit();
        pointObj["quality"] = "good";
        pointObj["value"] = reading.value;
      } else {
        addError("SENSOR_FAULT", sensor->pointId(), "error", "Read failed");
      }
    }
  }
  windows_sent_count_ = (WINDOWS_PER_BATCH < windows_buffer_.size()) ? WINDOWS_PER_BATCH : windows_buffer_.size();

  state_sent_ = false;
  if (state_source_) {
    JsonArray stateArr = doc["state"].to<JsonArray>();
    if (state_source_->appendSections(stateArr, sentAt.c_str()) > 0) {
      state_sent_ = true;
    } else {
      doc.remove("state");
    }
  }

  if (!errors_buffer_.empty()) {
    JsonArray errorsArr = doc["errors"].to<JsonArray>();
    for (const auto& err : errors_buffer_) {
      JsonObject errObj = errorsArr.add<JsonObject>();
      errObj["code"] = err.code;
      if (err.point_id) {
        errObj["point_id"] = err.point_id;
      }
      errObj["severity"] = err.severity;
      if (err.message) {
        errObj["message"] = err.message;
      }
    }
  }

  String payload;
  serializeJson(doc, payload);
  return payload;
}

void TelemetryPayload::acknowledge() {
  if (windows_sent_count_ > 0 && windows_sent_count_ <= windows_buffer_.size()) {
    windows_buffer_.erase(windows_buffer_.begin(), windows_buffer_.begin() + windows_sent_count_);
    windows_sent_count_ = 0;
  }
  errors_buffer_.clear();

  if (state_source_ && state_sent_) {
    state_source_->onAcknowledged();
    state_sent_ = false;
  }
}

void TelemetryPayload::setStateSource(IStateSectionSource* source) { state_source_ = source; }

void TelemetryPayload::setGetUtcTime(std::function<uint64_t()> getUtcTime) { getUtcTime_ = getUtcTime; }

void TelemetryPayload::addError(const char* code, const char* pointId, const char* severity, const char* message) {
  if (!code || !severity) {
    LOG_ERROR("[PAYLOAD]", "addError: code and severity are required");
    return;
  }
  if (errors_buffer_.size() >= MAX_ERRORS) {
    errors_buffer_.erase(errors_buffer_.begin());
  }
  errors_buffer_.push_back({code, pointId, severity, message});
}
