#include <gtest/gtest.h>
#include <ctime>
#include <sys/time.h>

// Minimal test dla formatIso8601 logic
class TimeFormatTest : public ::testing::Test {
 protected:
  // Simuluje formatIso8601 bez zależności od TimeSync
  std::string formatIso8601(uint64_t utcMs) {
    if (utcMs == 0) {
      return "";
    }

    time_t seconds = utcMs / 1000;
    uint32_t ms = utcMs % 1000;

    struct tm timeinfo;
    gmtime_r(&seconds, &timeinfo);

    char buffer[30];
    snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03luZ",
             timeinfo.tm_year + 1900,
             timeinfo.tm_mon + 1,
             timeinfo.tm_mday,
             timeinfo.tm_hour,
             timeinfo.tm_min,
             timeinfo.tm_sec,
             (unsigned long)ms);

    return std::string(buffer);
  }
};

TEST_F(TimeFormatTest, FormatsValidTimestamp) {
  // 2026-08-10 13:45:22.123 UTC
  uint64_t utcMs = 1786419922123ULL;  // Unix timestamp
  std::string result = formatIso8601(utcMs);

  EXPECT_FALSE(result.empty());
  EXPECT_THAT(result, ::testing::HasSubstr("2026-08-10"));
  EXPECT_THAT(result, ::testing::HasSubstr("T"));
  EXPECT_THAT(result, ::testing::HasSubstr("Z"));
  EXPECT_THAT(result, ::testing::MatchesRegex("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z"));
}

TEST_F(TimeFormatTest, ReturnsEmptyForZero) {
  std::string result = formatIso8601(0);
  EXPECT_TRUE(result.empty());
}

TEST_F(TimeFormatTest, PreservesMilliseconds) {
  // Test z konkretnymi milisekundami
  uint64_t utcMs = 1786419922999ULL;
  std::string result = formatIso8601(utcMs);

  EXPECT_THAT(result, ::testing::HasSubstr(".999Z"));
}
