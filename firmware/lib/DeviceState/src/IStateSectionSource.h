#pragma once

#include <ArduinoJson.h>
#include <stddef.h>

// The one canonical way a read is answered (B-08).
//
// TelemetryPayload knows nothing about *what* state is — it only offers the
// `state[]` array and the packet's timestamp. Every future read (device
// configuration, sensor inventory, ...) is another implementation of this
// interface plus a section id in sensor_registry.yaml. No new endpoint, no
// change to the packet contract.
class IStateSectionSource {
 public:
  virtual ~IStateSectionSource() = default;

  // Append zero or more sections to `target`. Each appended object must carry
  // "section", "schema_version", "captured_at" (use `capturedAtIso` verbatim,
  // so every section shares the packet's clock) and "data".
  // Returns the number of sections appended.
  virtual size_t appendSections(JsonArray target, const char* capturedAtIso) = 0;

  // Called once the backend has accepted the packet the sections rode on.
  // Until then nothing is marked as reported, so a failed send retries the
  // read instead of silently skipping an interval.
  virtual void onAcknowledged() = 0;
};
