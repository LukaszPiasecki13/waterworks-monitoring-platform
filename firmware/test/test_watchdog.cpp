// Priorytet 5 wg ryzyka: wychodzenie z zawieszenia.
// Zbyt ostrożny watchdog zostawia martwe urządzenie w szafie; zbyt agresywny
// wpada w pętlę restartów i nigdy nie dociąga danych.
#include <gtest/gtest.h>

#include <Fakes.h>
#include <Watchdog.h>

namespace {

constexpr unsigned long kStuckThresholdMs = 5 * 60 * 1000;
constexpr uint8_t kMaxRestarts = 2;

class WatchdogTest : public ::testing::Test {
 protected:
  void SetUp() override {
    watchdog = new Watchdog(modem, power, system, kStuckThresholdMs, kMaxRestarts);
    watchdog->setTelemetryHealth(&health);
  }

  void TearDown() override { delete watchdog; }

  // Jedno wywołanie check() w stanie „od dawna brak udanej wysyłki".
  void checkWhileStuck(unsigned long now = kStuckThresholdMs + 1) { watchdog->check(now, 0); }

  FakeModemLink modem;
  FakeModemPower power;
  FakeSystemControl system;
  FakeTelemetryHealth health;
  Watchdog* watchdog = nullptr;
};

// --- próg zadziałania ------------------------------------------------------

TEST_F(WatchdogTest, PonizejProguNicSieNieDzieje) {
  watchdog->check(kStuckThresholdMs, 0);

  EXPECT_EQ(modem.test_at_calls, 0);
  EXPECT_EQ(power.hard_reset_calls, 0);
  EXPECT_EQ(system.restart_calls, 0);
}

TEST_F(WatchdogTest, TuzPowyzejProguZaczynaSieEskalacja) {
  modem.at_ok = false;
  checkWhileStuck();
  EXPECT_EQ(modem.test_at_calls, 1);
}

TEST_F(WatchdogTest, SwiezaUdanaWysylkaZerujeLicznikCzasu) {
  // lastSuccessMs tuż przed „teraz" — mimo dużego `now` nie ma eskalacji.
  watchdog->check(10 * kStuckThresholdMs, 10 * kStuckThresholdMs - 1);
  EXPECT_EQ(modem.test_at_calls, 0);
}

// --- błąd trwały blokuje eskalację -----------------------------------------

TEST_F(WatchdogTest, TrwalyBladBackenduNieUruchamiaOdzyskiwania) {
  // 403/409/410 znaczą „backend odmawia", a nie „modem padł". Reset modemu
  // niczego by nie naprawił, a restart ESP32 zapętliłby urządzenie.
  health.permanent = true;
  modem.at_ok = false;

  for (int i = 0; i < 5; ++i) checkWhileStuck(kStuckThresholdMs + 1 + i);

  EXPECT_EQ(modem.test_at_calls, 0);
  EXPECT_EQ(power.hard_reset_calls, 0);
  EXPECT_EQ(system.restart_calls, 0);
}

TEST_F(WatchdogTest, BezPodpietegoZrodlaStanuEskalacjaDziala) {
  Watchdog standalone(modem, power, system, kStuckThresholdMs, kMaxRestarts);
  modem.at_ok = false;

  standalone.check(kStuckThresholdMs + 1, 0);

  EXPECT_EQ(modem.test_at_calls, 1);
}

// --- kolejność eskalacji ---------------------------------------------------

TEST_F(WatchdogTest, ModemOdpowiadaNaATWiecEskalacjaSieNieRozpoczyna) {
  modem.at_ok = true;

  for (int i = 0; i < 5; ++i) checkWhileStuck(kStuckThresholdMs + 1 + i);

  EXPECT_EQ(modem.test_at_calls, 5);
  EXPECT_EQ(power.hard_reset_calls, 0);
  EXPECT_EQ(system.restart_calls, 0);
  EXPECT_EQ(watchdog->recoveryAttempts(), 0);
}

TEST_F(WatchdogTest, BrakOdpowiedziNaATProwadziDoTwardegoResetuModemu) {
  modem.at_ok = false;

  checkWhileStuck();                        // krok 1: AT nie odpowiada
  EXPECT_EQ(power.hard_reset_calls, 0);

  checkWhileStuck(kStuckThresholdMs + 2);   // krok 2: twardy reset modemu
  EXPECT_EQ(power.hard_reset_calls, 1);
  EXPECT_EQ(system.restart_calls, 0);
}

TEST_F(WatchdogTest, PoResecieModemuNastepujeRestartUkladu) {
  modem.at_ok = false;

  checkWhileStuck(kStuckThresholdMs + 1);
  checkWhileStuck(kStuckThresholdMs + 2);
  checkWhileStuck(kStuckThresholdMs + 3);

  EXPECT_EQ(power.hard_reset_calls, 1);
  EXPECT_EQ(system.restart_calls, 1);
  EXPECT_EQ(system.restartCount(), 1u) << "licznik restartów w RTC musi rosnąć";
}

// --- limit restartów -------------------------------------------------------

TEST_F(WatchdogTest, LicznikRestartowJestRespektowany) {
  modem.at_ok = false;
  system.restart_count = kMaxRestarts;  // limit już wyczerpany

  checkWhileStuck(kStuckThresholdMs + 1);
  checkWhileStuck(kStuckThresholdMs + 2);
  checkWhileStuck(kStuckThresholdMs + 3);

  EXPECT_EQ(system.restart_calls, 0) << "urządzenie wpadłoby w pętlę restartów";
  EXPECT_EQ(watchdog->recoveryAttempts(), 0) << "eskalacja musi wrócić na początek";
}

TEST_F(WatchdogTest, PoWyczerpaniuLimituCyklEskalacjiStartujeOdNowa) {
  modem.at_ok = false;
  system.restart_count = kMaxRestarts;

  // Pierwszy pełny cykl kończy się bez restartu i zeruje licznik prób.
  for (int i = 1; i <= 3; ++i) checkWhileStuck(kStuckThresholdMs + i);
  ASSERT_EQ(system.restart_calls, 0);

  // Drugi cykl znowu próbuje AT i resetu modemu — to jest jedyne, co zostało.
  for (int i = 4; i <= 6; ++i) checkWhileStuck(kStuckThresholdMs + i);

  EXPECT_EQ(modem.test_at_calls, 2);
  EXPECT_EQ(power.hard_reset_calls, 2);
  EXPECT_EQ(system.restart_calls, 0);
}

TEST_F(WatchdogTest, PonizejLimituRestartJestWykonywany) {
  modem.at_ok = false;
  system.restart_count = kMaxRestarts - 1;

  for (int i = 1; i <= 3; ++i) checkWhileStuck(kStuckThresholdMs + i);

  EXPECT_EQ(system.restart_calls, 1);
  EXPECT_EQ(system.restartCount(), kMaxRestarts);
}

// --- opóźnienia ------------------------------------------------------------

TEST_F(WatchdogTest, ResetModemuIRestartCzekajaZanimZadzialaja) {
  // Modem potrzebuje czasu po twardym resecie; restart ESP32 — na spłukanie logów.
  modem.at_ok = false;

  checkWhileStuck(kStuckThresholdMs + 1);
  checkWhileStuck(kStuckThresholdMs + 2);
  EXPECT_EQ(system.total_delay_ms, 3000u);

  checkWhileStuck(kStuckThresholdMs + 3);
  EXPECT_EQ(system.total_delay_ms, 4000u);
}

}  // namespace
