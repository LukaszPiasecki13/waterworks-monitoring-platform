#include <ArduinoJson.h>
#include "TelemetryPayload.h"

TelemetryPayload::TelemetryPayload(const char* deviceId, const char* orgId, const char* objectId)
    : device_id_(deviceId),
      org_id_(orgId),
      object_id_(objectId) {
}

String TelemetryPayload::build(uint32_t seq) {
  JsonDocument doc;

  doc["v"] = 1;
  doc["device_id"] = device_id_;
  doc["org_id"] = org_id_;
  doc["object_id"] = object_id_;
  doc["seq"] = seq;
  doc["sent_at"] = "2026-08-05T10:31:09.492Z";

  JsonArray windows = doc["windows"].to<JsonArray>();
  JsonObject window = windows.add<JsonObject>();

  window["window_start"] = "2026-08-05T10:31:09.492Z";
  window["window_seconds"] = 1;

  JsonArray points = window["points"].to<JsonArray>();
  JsonObject point = points.add<JsonObject>();

  point["point_id"] = "test-counter";
  point["type"] = "debug_counter";
  point["unit"] = "count";
  point["quality"] = "good";
  point["avg"] = seq;
  point["min"] = seq;
  point["max"] = seq;
  point["value"] = seq;

  String payload;
  serializeJson(doc, payload);
  return payload;
}
