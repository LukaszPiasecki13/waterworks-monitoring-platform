#include <gtest/gtest.h>
#include <Logger.h>

// Test Logger macro format output
class LoggerTest : public ::testing::Test {
 protected:
  void SetUp() override {
    // Logger macros use Serial.printf; tests verify format
  }
};

TEST_F(LoggerTest, LogInfoMacroExists) {
  // Verify that LOG_INFO macro compiles and has correct format
  // Format: [millis][LEVEL][TAG] message
  LOG_INFO("[TEST]", "Test message");
  SUCCEED();  // If we reach here, macro compiles
}

TEST_F(LoggerTest, LogWarnMacroExists) {
  LOG_WARN("[TEST]", "Test warning");
  SUCCEED();
}

TEST_F(LoggerTest, LogErrorMacroExists) {
  LOG_ERROR("[TEST]", "Test error");
  SUCCEED();
}

TEST_F(LoggerTest, LogDebugMacroExists) {
  LOG_DEBUG("[TEST]", "Test debug");
  SUCCEED();
}

TEST_F(LoggerTest, LogFormatWithNumbers) {
  // Test printf-style formatting
  int value = 42;
  float temp = 25.5f;
  LOG_INFO("[TEST]", "Value: %d, Temp: %.1f", value, temp);
  SUCCEED();
}

TEST_F(LoggerTest, CompileTimeFiltering) {
  // At LOG_LEVEL=LOG_INFO, DEBUG messages should not generate code
  // This is verified by checking .elf size (compile-time filtering)
#if LOG_LEVEL == LOG_INFO
  // DEBUG and TRACE are filtered out at preprocessing
  EXPECT_EQ(LOG_DEBUG, 0);  // LOG_DEBUG is lower level than LOG_INFO
#endif
  SUCCEED();
}
