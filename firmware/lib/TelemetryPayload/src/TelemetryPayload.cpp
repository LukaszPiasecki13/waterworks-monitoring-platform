#include <ArduinoJson.h>
#include <cmath>
#include <time.h>
#include "TelemetryPayload.h"

TelemetryPayload::TelemetryPayload(const char* deviceId) : device_id_(deviceId), getUtcTime_(nullptr) {}

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
  float sineValue = calculateSineValue(seq);

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
  JsonObject point = points.add<JsonObject>();

  point["point_id"] = "sensor_data";
  point["type"] = "sensor_value";
  point["unit"] = "mm";
  point["quality"] = "good";
  point["avg"] = roundf(sineValue * 100.0f) / 100.0f;
  point["min"] = 50;
  point["max"] = 150;
  point["value"] = roundf(sineValue * 100.0f) / 100.0f;

  String payload;
  serializeJson(doc, payload);
  return payload;
}

void TelemetryPayload::setGetUtcTime(std::function<uint64_t()> getUtcTime) { getUtcTime_ = getUtcTime; }
