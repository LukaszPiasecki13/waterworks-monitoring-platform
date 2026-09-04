#include "DeviceStateSource.h"

DeviceStateSource::DeviceStateSource(const char* sectionId, int schemaVersion, uint32_t reportIntervalMs,
                                     CaptureFn capture, ClockFn nowMs)
    : section_id_(sectionId),
      schema_version_(schemaVersion),
      scheduler_(reportIntervalMs),
      capture_(capture),
      now_ms_(nowMs) {}

size_t DeviceStateSource::appendSections(JsonArray target, const char* capturedAtIso) {
  if (!capture_ || !now_ms_) {
    return 0;
  }

  uint32_t now = now_ms_();
  if (!pending_ && !scheduler_.shouldReport(now)) {
    return 0;
  }

  // A rebuild after a failed send re-captures rather than replaying the old
  // snapshot: uptime, RSSI and buffer fill have all moved on, and stale
  // numbers stamped with a fresh captured_at would be a lie.
  device_state::Snapshot snapshot = capture_();

  JsonObject section = target.add<JsonObject>();
  section["section"] = section_id_;
  section["schema_version"] = schema_version_;
  section["captured_at"] = capturedAtIso;

  JsonObject data = section["data"].to<JsonObject>();
  data["serial_number"] = snapshot.serial_number;
  data["firmware_version"] = snapshot.firmware_version;
  data["registry_schema_version"] = snapshot.registry_schema_version;
  data["uptime_seconds"] = snapshot.uptime_seconds;
  data["restart_count"] = snapshot.restart_count;
  data["restart_reason"] = device_state::restartReasonName(snapshot.restart_reason);

  // Omitted rather than faked when the modem has no reading — a missing RSSI
  // and a very weak one must not look the same on the dashboard.
  if (snapshot.rssi_dbm != device_state::RSSI_UNKNOWN) {
    data["rssi_dbm"] = snapshot.rssi_dbm;
  }

  data["free_heap_bytes"] = snapshot.free_heap_bytes;
  data["min_free_heap_bytes"] = snapshot.min_free_heap_bytes;
  data["buffer_windows_used"] = snapshot.buffer_windows_used;
  data["buffer_windows_capacity"] = snapshot.buffer_windows_capacity;
  data["buffer_windows_dropped"] = snapshot.buffer_windows_dropped;

  pending_ = true;
  pending_at_ms_ = now;
  return 1;
}

void DeviceStateSource::onAcknowledged() {
  if (!pending_) {
    return;
  }
  scheduler_.markReported(pending_at_ms_);
  pending_ = false;
}
