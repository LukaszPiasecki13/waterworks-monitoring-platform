// Sterowanie zasilaniem modemu: to jedyna ścieżka wyjścia z zawieszonego
// A7670E, a błąd w sekwencji PWRKEY/RESET widać dopiero na płytce.
// Test opiera się o zapis zdarzeń GPIO z warstwy zgodności (NativeGpio).
#include <gtest/gtest.h>

#include <Arduino.h>
#include <Config.h>
#include <ModemPower.h>

#include <vector>

namespace {

class ModemPowerTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    NativeGpio::reset();
  }
};

TEST_F(ModemPowerTest, PowerOnDajeImpulsPwrkeyIZwalniaReset) {
  ModemPower power(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);

  power.powerOn();

  // RESET trzymany nisko = układ zwolniony z resetu.
  std::vector<int> resetLevels = NativeGpio::writesFor(MODEM_RESET_PIN);
  ASSERT_FALSE(resetLevels.empty());
  EXPECT_EQ(resetLevels.back(), LOW);

  // PWRKEY: HIGH -> LOW (impuls ~1,2 s) -> HIGH.
  EXPECT_EQ(NativeGpio::writesFor(MODEM_PWRKEY_PIN), (std::vector<int>{HIGH, LOW, HIGH}));
}

TEST_F(ModemPowerTest, PowerOnPomijaLinieZasilaniaGdyNieskonfigurowana) {
  ASSERT_EQ(MODEM_POWER_ENABLE_PIN, -1) << "domyślna konfiguracja nie ma sterowania zasilaniem";
  ModemPower power(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, -1);

  power.powerOn();

  for (const GpioEvent& e : NativeGpio::events()) {
    EXPECT_GE(e.pin, 0) << "ujemny numer pinu nie może trafić do pinMode/digitalWrite";
  }
}

TEST_F(ModemPowerTest, PowerOnUzywaLiniiZasilaniaGdyJestSkonfigurowana) {
  constexpr int kPowerEnablePin = 21;
  ModemPower power(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, kPowerEnablePin);

  power.powerOn();

  EXPECT_EQ(NativeGpio::writesFor(kPowerEnablePin), (std::vector<int>{HIGH}));
}

TEST_F(ModemPowerTest, HardResetPodnosiResetIPotemWykonujeCyklPwrkey) {
  ModemPower power(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);

  power.hardReset();

  EXPECT_EQ(NativeGpio::writesFor(MODEM_RESET_PIN), (std::vector<int>{HIGH, LOW}));
  EXPECT_EQ(NativeGpio::writesFor(MODEM_PWRKEY_PIN), (std::vector<int>{LOW, HIGH, LOW, HIGH}));
}

TEST_F(ModemPowerTest, ImpulsResetuTrwaConajmniejDwieSekundy) {
  // Nota katalogowa A7670E: RESET musi być aktywny > 2 s, inaczej układ
  // zignoruje sygnał i watchdog straci swój drugi krok eskalacji.
  ModemPower power(MODEM_PWRKEY_PIN, MODEM_RESET_PIN, MODEM_POWER_ENABLE_PIN);

  power.hardReset();

  bool sawHigh = false;
  unsigned long resetHighAt = 0;
  unsigned long resetLowAt = 0;
  bool sawLowAfterHigh = false;
  for (const GpioEvent& e : NativeGpio::events()) {
    if (e.kind != GpioEvent::DigitalWrite || e.pin != MODEM_RESET_PIN) continue;
    if (e.value == HIGH && !sawHigh) {
      sawHigh = true;
      resetHighAt = e.atMs;
    } else if (e.value == LOW && sawHigh && !sawLowAfterHigh) {
      sawLowAfterHigh = true;
      resetLowAt = e.atMs;
    }
  }

  ASSERT_TRUE(sawLowAfterHigh) << "RESET nigdy nie wrócił do stanu niskiego";
  EXPECT_GE(resetLowAt - resetHighAt, 2000u);
}

TEST_F(ModemPowerTest, BrakSkonfigurowanychPinowNieWywolujeZadnychOperacjiGpio) {
  ModemPower power(-1, -1, -1);

  power.powerOn();
  power.hardReset();

  EXPECT_TRUE(NativeGpio::events().empty());
}

}  // namespace
