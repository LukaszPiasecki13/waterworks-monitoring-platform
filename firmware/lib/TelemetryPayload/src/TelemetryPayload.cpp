#include <ArduinoJson.h>
#include <cmath>
#include <time.h>
#include "TelemetryPayload.h"
#include "Config.h"
#include <Logger.h>

TelemetryPayload::TelemetryPayload(const String& deviceId, ISensor* sensor)
    : device_id_(deviceId), getUtcTime_(nullptr), pt100_sensor_(sensor) {
  if (pt100_sensor_ && !pt100_sensor_->init()) {
    LOG_ERROR("[PT100]", "Failed to initialize sensor");
  }
}

float TelemetryPayload::calculateSineValue(uint32_t seq) {
  const float BASE_VALUE = 100.0f;
  const float AMPLITUDE = 50.0f;
  const float PERIOD = 100.0f;

  float angle = (seq % (uint32_t)PERIOD) * 2.0f * M_PI / PERIOD;
  return BASE_VALUE + AMPLITUDE * sin(angle);
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

String TelemetryPayload::build(uint32_t seq, unsigned long timestampMs) {
  float temperature = 0.0f;
  bool hasReading = pt100_sensor_ && pt100_sensor_->read(temperature);
  if (!hasReading) {
    LOG_WARN(pt100_sensor_ ? pt100_sensor_->getTag() : "[SENSOR]", "Read failed, skipping point");
  }

  JsonDocument doc;

  doc["v"] = 1;
  doc["device_id"] = device_id_;
  doc["seq"] = seq;

  String timestamp;
  if (getUtcTime_) {
    uint64_t utcMs = getUtcTime_();
    timestamp = formatIso8601(utcMs);
  }
  if (timestamp.isEmpty()) {
    unsigned long seconds = timestampMs / 1000;
    unsigned long ms = timestampMs % 1000;
    unsigned long minutes = (seconds / 60) % 60;
    unsigned long secs = seconds % 60;
    char buffer[30];
    snprintf(buffer, sizeof(buffer), "2026-08-10T%02lu:%02lu:%02lu.%03luZ", (seconds / 3600) % 24, minutes, secs, ms);
    timestamp = String(buffer);
  }
  doc["sent_at"] = timestamp;

  JsonArray windows = doc["windows"].to<JsonArray>();
  JsonObject window = windows.add<JsonObject>();

  window["window_start"] = timestamp;
  window["window_seconds"] = 30;

  JsonArray points = window["points"].to<JsonArray>();
  if (hasReading) {
    JsonObject point = points.add<JsonObject>();

    point["point_id"] = "pt100_temperature";
    point["type"] = "temperature";
    point["unit"] = "°C";
    point["quality"] = "good";
    point["avg"] = roundf(temperature * 100.0f) / 100.0f;
    point["min"] = -10;
    point["max"] = 100;
    point["value"] = roundf(temperature * 100.0f) / 100.0f;
  }

  String payload;
  serializeJson(doc, payload);
  return payload;
}

void TelemetryPayload::setGetUtcTime(std::function<uint64_t()> getUtcTime) { getUtcTime_ = getUtcTime; }
