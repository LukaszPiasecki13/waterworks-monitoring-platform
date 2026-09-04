// Punkt wejścia dla testów `env:native`. Pakiet googletest w PlatformIO nie
// linkuje `gtest_main`, więc `main()` musi dostarczyć projekt.
#include <gtest/gtest.h>

#include <Arduino.h>

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);

  // Logi firmware trafiają do bufora NativeSerial. `--gtest_also_run_disabled_tests`
  // ich nie włącza — do podglądu na stdout służy zmienna środowiskowa.
  if (const char* echo = std::getenv("FIRMWARE_TEST_ECHO_LOGS")) {
    if (echo[0] == '1') Serial.setEcho(true);
  }

  return RUN_ALL_TESTS();
}
