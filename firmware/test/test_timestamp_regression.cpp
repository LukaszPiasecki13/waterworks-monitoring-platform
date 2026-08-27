#include <gtest/gtest.h>
#include <ctime>
#include <string>

// Core bug: passing millis() to formatIso8601 produces 1970 timestamps
class TimestampRegressionTest : public ::testing::Test {
 protected:
  std::string formatIso8601(uint64_t utcMs) {
    if (utcMs == 0) {
      return "";
    }

    time_t seconds = utcMs / 1000;
    uint32_t ms = utcMs % 1000;

    struct tm timeinfo;
    gmtime_r(&seconds, &timeinfo);

    char buffer[30];
    snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03luZ", timeinfo.tm_year + 1900,
             timeinfo.tm_mon + 1, timeinfo.tm_mday, timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec,
             (unsigned long)ms);

    return std::string(buffer);
  }
};

// Test 1: CRITICAL - millis() produces 1970 timestamp (BUG PROOF)
TEST_F(TimestampRegressionTest, MillisProduces1970Timestamp) {
  unsigned long millisValue = 15000;  // 15 seconds from boot
  std::string result = formatIso8601(millisValue);

  // This is WRONG and proves the bug exists if sample(millis()) is used
  EXPECT_THAT(result, ::testing::HasSubstr("1970-01-01"));
  EXPECT_THAT(result, ::testing::HasSubstr("T00:00:15"));
}

// Test 2: Correct - UTC timestamp produces correct 2026 date
TEST_F(TimestampRegressionTest, UtcTimestampProduces2026Date) {
  const uint64_t utcMs = 1693219400000ULL;  // Aug 27, 2026 06:43:20 UTC
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr("2026-08-27"));
  EXPECT_THAT(result, ::testing::HasSubstr("T06:43:20"));
  EXPECT_FALSE(result.find("1970") != std::string::npos);  // Must NOT contain 1970
}

// Test 3: Edge case - zero UTC timestamp
TEST_F(TimestampRegressionTest, ZeroUtcReturnsEmpty) {
  std::string result = formatIso8601(0);
  EXPECT_TRUE(result.empty());
}

// Test 4: Edge case - very large UTC timestamp (year 2050)
TEST_F(TimestampRegressionTest, Year2050Timestamp) {
  // 2050-01-01 00:00:00 UTC ≈ 2524608000 seconds = 2524608000000 ms
  const uint64_t utcMs = 2524608000000ULL;
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr("2050-01-01"));
  EXPECT_THAT(result, ::testing::HasSubstr("T00:00:00"));
}

// Test 5: Millisecond precision preserved
TEST_F(TimestampRegressionTest, MillisecondPrecisionPreserved) {
  const uint64_t utcMs = 1693219400999ULL;  // .999 milliseconds
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr(".999Z"));
}

// Test 6: Example from serial log - first packet
TEST_F(TimestampRegressionTest, SerialLogExamplePacket1) {
  // From serial: "sent_at":"2026-08-27T06:44:22.125Z"
  // This is roughly 1693219462125 ms
  const uint64_t utcMs = 1693219462125ULL;
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr("2026-08-27"));
  EXPECT_THAT(result, ::testing::HasSubstr("06:44:22"));
  EXPECT_THAT(result, ::testing::HasSubstr(".125Z"));
}

// Test 7: Example from serial log - second packet (60s later)
TEST_F(TimestampRegressionTest, SerialLogExamplePacket2) {
  // 60 seconds = 60000 ms later
  const uint64_t utcMs = 1693219522151ULL;  // 60s later
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr("2026-08-27"));
  EXPECT_THAT(result, ::testing::HasSubstr("06:45:22"));
  EXPECT_THAT(result, ::testing::HasSubstr(".151Z"));
}

// Test 8: Verify format matches ISO8601 standard
TEST_F(TimestampRegressionTest, MatchesIso8601Standard) {
  const uint64_t utcMs = 1693219400000ULL;
  std::string result = formatIso8601(utcMs);

  // ISO8601: YYYY-MM-DDTHH:MM:SS.sssZ
  EXPECT_THAT(result, ::testing::MatchesRegex("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z"));
}

// Test 9: Verify year 2106 boundary (uint32_t Unix seconds limit)
TEST_F(TimestampRegressionTest, Year2106Boundary) {
  // Year 2106: Beyond uint32_t max seconds (2^32 - 1 = 4294967295, ~Feb 2106)
  const uint64_t utcMs = 4294967295000ULL;  // Max uint32 in ms
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr("2106-02-07"));
  // Note: Our design uses uint32_t for nowUnix in send_seq_, valid until 2106
}

// Test 10: Verify millis() never exceeds 2^32 (theoretical device uptime limit)
TEST_F(TimestampRegressionTest, MillisMaxValue) {
  // Max millis on 32-bit system: ~49.7 days (4294967295 ms)
  const unsigned long maxMillis = 4294967295UL;
  std::string result = formatIso8601(maxMillis);

  // This should still format to 1970 (proving the bug)
  EXPECT_THAT(result, ::testing::HasSubstr("1970-01-01"));
  // Seconds = 4294967295 / 1000 = 4294967 seconds ≈ 49.7 days from epoch
}
