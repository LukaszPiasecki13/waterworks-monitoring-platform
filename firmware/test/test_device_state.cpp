// Native tests for the device state read channel (B-08).
//
// Everything here runs without hardware: the snapshot is supplied by the test,
// the clock is a plain counter, and the JSON is inspected in memory. What is
// being pinned down is the part that decides *when* a read is answered and
// *what shape* the answer has — the two things a wrong firmware build would
// break silently.

#include <gtest/gtest.h>

#include <ArduinoJson.h>

#include <DeviceState.h>
#include <DeviceStateSource.h>

namespace {

constexpr uint32_t kIntervalMs = 15UL * 60UL * 1000UL;
constexpr const char* kCapturedAt = "2026-09-03T12:00:00.000Z";

device_state::Snapshot makeSnapshot() {
  device_state::Snapshot snapshot;
  snapshot.serial_number = "WW-TEST-0001";
  snapshot.firmware_version = "0.4.0";
  snapshot.registry_schema_version = 2;
  snapshot.uptime_seconds = 3600;
  snapshot.restart_count = 2;
  snapshot.restart_reason = device_state::RestartReason::TaskWatchdog;
  snapshot.rssi_dbm = -67;
  snapshot.free_heap_bytes = 184320;
  snapshot.min_free_heap_bytes = 151000;
  snapshot.buffer_windows_used = 8;
  snapshot.buffer_windows_capacity = 48;
  snapshot.buffer_windows_dropped = 3;
  return snapshot;
}

// A DeviceStateSource driven by a test-controlled clock and snapshot.
class SourceFixture : public ::testing::Test {
 protected:
  void SetUp() override {
    snapshot_ = makeSnapshot();
    source_.reset(
        new DeviceStateSource("device", 1, kIntervalMs, [this]() { return snapshot_; }, [this]() { return now_ms_; }));
  }

  size_t build(JsonDocument& doc) {
    JsonArray target = doc["state"].to<JsonArray>();
    return source_->appendSections(target, kCapturedAt);
  }

  uint32_t now_ms_ = 0;
  device_state::Snapshot snapshot_;
  std::unique_ptr<DeviceStateSource> source_;
};

}  // namespace

// ---------------------------------------------------------------- scheduler

TEST(ReportScheduler, ReportsOnceBeforeAnythingHasBeenSent) {
  device_state::ReportScheduler scheduler(kIntervalMs);

  EXPECT_TRUE(scheduler.shouldReport(0));
  EXPECT_FALSE(scheduler.hasReported());
}

TEST(ReportScheduler, StaysQuietUntilTheIntervalElapses) {
  device_state::ReportScheduler scheduler(kIntervalMs);
  scheduler.markReported(1000);

  EXPECT_FALSE(scheduler.shouldReport(1000));
  EXPECT_FALSE(scheduler.shouldReport(1000 + kIntervalMs - 1));
  EXPECT_TRUE(scheduler.shouldReport(1000 + kIntervalMs));
}

TEST(ReportScheduler, SurvivesMillisRollover) {
  // millis() wraps after ~49 days; the device must keep reporting afterwards.
  device_state::ReportScheduler scheduler(kIntervalMs);
  const uint32_t justBeforeWrap = 0xFFFFFFFFu - 1000u;
  scheduler.markReported(justBeforeWrap);

  EXPECT_FALSE(scheduler.shouldReport(justBeforeWrap + 500u));
  EXPECT_TRUE(scheduler.shouldReport(justBeforeWrap + kIntervalMs));
}

// ------------------------------------------------------------- value mapping

TEST(RestartReason, MapsEspCodesToTheNamesTheBackendAccepts) {
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(1)), "power_on");
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(4)), "panic");
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(6)), "task_watchdog");
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(9)), "brownout");
}

TEST(RestartReason, UnknownCodeDegradesToUnknownRatherThanAWrongLabel) {
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(-1)), "unknown");
  EXPECT_STREQ(device_state::restartReasonName(device_state::restartReasonFromCode(99)), "unknown");
}

TEST(SignalQuality, ConvertsCsqToDbm) {
  EXPECT_EQ(device_state::rssiDbmFromCsq(0), -113);
  EXPECT_EQ(device_state::rssiDbmFromCsq(20), -73);
  EXPECT_EQ(device_state::rssiDbmFromCsq(31), -51);
}

TEST(SignalQuality, UndetectableSignalIsNotAValue) {
  EXPECT_EQ(device_state::rssiDbmFromCsq(99), device_state::RSSI_UNKNOWN);
  EXPECT_EQ(device_state::rssiDbmFromCsq(-1), device_state::RSSI_UNKNOWN);
}

// ------------------------------------------------------------- section shape

TEST_F(SourceFixture, FirstPacketAfterBootCarriesTheSection) {
  JsonDocument doc;

  EXPECT_EQ(build(doc), 1u);

  JsonObject section = doc["state"][0];
  EXPECT_STREQ(section["section"], "device");
  EXPECT_EQ(section["schema_version"].as<int>(), 1);
  EXPECT_STREQ(section["captured_at"], kCapturedAt);
}

TEST_F(SourceFixture, SectionCarriesEveryFieldTheContractPromises) {
  JsonDocument doc;
  build(doc);

  JsonObject data = doc["state"][0]["data"];
  EXPECT_STREQ(data["serial_number"], "WW-TEST-0001");
  EXPECT_STREQ(data["firmware_version"], "0.4.0");
  EXPECT_EQ(data["registry_schema_version"].as<int>(), 2);
  EXPECT_EQ(data["uptime_seconds"].as<uint32_t>(), 3600u);
  EXPECT_EQ(data["restart_count"].as<uint32_t>(), 2u);
  EXPECT_STREQ(data["restart_reason"], "task_watchdog");
  EXPECT_EQ(data["rssi_dbm"].as<int>(), -67);
  EXPECT_EQ(data["free_heap_bytes"].as<uint32_t>(), 184320u);
  EXPECT_EQ(data["min_free_heap_bytes"].as<uint32_t>(), 151000u);
  EXPECT_EQ(data["buffer_windows_used"].as<uint32_t>(), 8u);
  EXPECT_EQ(data["buffer_windows_capacity"].as<uint32_t>(), 48u);
  EXPECT_EQ(data["buffer_windows_dropped"].as<uint32_t>(), 3u);
}

TEST_F(SourceFixture, UnknownRssiIsOmittedNotFaked) {
  snapshot_.rssi_dbm = device_state::RSSI_UNKNOWN;
  JsonDocument doc;

  build(doc);

  EXPECT_FALSE(doc["state"][0]["data"]["rssi_dbm"].is<int>());
}

TEST_F(SourceFixture, SectionStaysWithinItsTransferBudget) {
  // The whole point of piggybacking is that state is cheap. Roughly 0.4 KB
  // every 15 minutes is ~1.2 MB/month; a section that grew past 512 B would
  // quietly change that arithmetic.
  JsonDocument doc;
  build(doc);

  std::string serialised;
  serializeJson(doc["state"][0], serialised);

  EXPECT_LT(serialised.size(), 512u) << serialised;
}

// -------------------------------------------------------------- send cadence

TEST_F(SourceFixture, StaysSilentUntilTheIntervalElapses) {
  JsonDocument first;
  ASSERT_EQ(build(first), 1u);
  source_->onAcknowledged();

  now_ms_ += 60000;
  JsonDocument second;
  EXPECT_EQ(build(second), 0u);

  now_ms_ += kIntervalMs;
  JsonDocument third;
  EXPECT_EQ(build(third), 1u);
}

TEST_F(SourceFixture, FailedSendRetriesTheReadInsteadOfSkippingTheInterval) {
  JsonDocument attempt;
  ASSERT_EQ(build(attempt), 1u);
  // No onAcknowledged(): the backend never took the packet.

  now_ms_ += 5000;
  JsonDocument retry;
  EXPECT_EQ(build(retry), 1u) << "a dropped packet must not consume the interval";
}

TEST_F(SourceFixture, RetryReCapturesRatherThanReplayingStaleNumbers) {
  JsonDocument attempt;
  ASSERT_EQ(build(attempt), 1u);

  snapshot_.uptime_seconds = 7200;
  now_ms_ += 5000;

  JsonDocument retry;
  ASSERT_EQ(build(retry), 1u);
  EXPECT_EQ(retry["state"][0]["data"]["uptime_seconds"].as<uint32_t>(), 7200u);
}

TEST_F(SourceFixture, AcknowledgingWithoutAPendingSectionIsHarmless) {
  source_->onAcknowledged();

  JsonDocument doc;
  EXPECT_EQ(build(doc), 1u) << "the first read of this boot is still owed";
}
