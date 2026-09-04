#pragma once

#include <functional>

#include "DeviceState.h"
#include "IStateSectionSource.h"

// Answers the `device` read: health and identity of the gateway itself.
//
// Everything hardware-specific arrives through the injected `capture` and
// `nowMs` callables, which is what lets the whole class run under
// `pio test -e native`.
class DeviceStateSource : public IStateSectionSource {
 public:
  using CaptureFn = std::function<device_state::Snapshot()>;
  using ClockFn = std::function<uint32_t()>;

  // `sectionId` and `schemaVersion` come from the generated SensorRegistry.h,
  // so the registry stays the single source of truth for both ends of the
  // contract and this library never includes a generated header.
  DeviceStateSource(const char* sectionId, int schemaVersion, uint32_t reportIntervalMs, CaptureFn capture,
                    ClockFn nowMs);

  size_t appendSections(JsonArray target, const char* capturedAtIso) override;
  void onAcknowledged() override;

 private:
  const char* section_id_;
  int schema_version_;
  device_state::ReportScheduler scheduler_;
  CaptureFn capture_;
  ClockFn now_ms_;
  bool pending_ = false;
  uint32_t pending_at_ms_ = 0;
};
