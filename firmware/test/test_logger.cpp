// Logger jest jedynym kanałem diagnostycznym urządzenia w terenie — format
// wpisu jest de facto kontraktem z człowiekiem czytającym monitor szeregowy.
// Poprzednia wersja tego pliku sprawdzała tylko, czy makra się kompilują.
#include <gtest/gtest.h>

#include <Arduino.h>
#include <Logger.h>

#include <string>

namespace {

class LoggerTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    Serial.clearCaptured();
  }

  const std::string& output() const { return Serial.captured(); }
};

TEST_F(LoggerTest, WpisMaFormatMillisPoziomTagWiadomosc) {
  NativeClock::set(12345);
  LOG_INFO("[TEST]", "Uruchomiono");

  EXPECT_EQ(output(), "[12345][INFO][[TEST]] Uruchomiono\n");
}

TEST_F(LoggerTest, KazdyPoziomMaWlasnaEtykiete) {
  LOG_INFO("[T]", "i");
  LOG_WARN("[T]", "w");
  LOG_ERROR("[T]", "e");

  EXPECT_NE(output().find("[INFO]"), std::string::npos);
  EXPECT_NE(output().find("[WARN]"), std::string::npos);
  EXPECT_NE(output().find("[ERROR]"), std::string::npos);
}

TEST_F(LoggerTest, FormatowanieWStyluPrintfDziala) {
  NativeClock::set(7);
  LOG_INFO("[PT100]", "Temperatura: %.2f, prob: %d", 21.375f, 3);

  EXPECT_EQ(output(), "[7][INFO][[PT100]] Temperatura: 21.38, prob: 3\n");
}

TEST_F(LoggerTest, ZnacznikCzasuIdzieZaMillis) {
  NativeClock::set(100);
  LOG_INFO("[T]", "pierwszy");
  NativeClock::advance(900);
  LOG_INFO("[T]", "drugi");

  EXPECT_NE(output().find("[100][INFO]"), std::string::npos);
  EXPECT_NE(output().find("[1000][INFO]"), std::string::npos);
}

TEST_F(LoggerTest, PoziomDebugJestOdfiltrowanyPrzyLogLevelInfo) {
  // Build ustawia -D LOG_LEVEL=LOG_INFO; DEBUG nie może trafić do wyjścia.
  ASSERT_EQ(LOG_LEVEL, LOG_INFO);
  LOG_DEBUG("[T]", "nie powinno się pojawić");

  EXPECT_TRUE(output().empty()) << output();
}

TEST_F(LoggerTest, LogowanieWewnatrzInstrukcjiWarunkowejNiePrzejmujeElse) {
  // Makra LOG_* rozwijają się do `if (...) { ... }` bez `do/while(0)`, więc
  // użycie ich w gałęzi `if` bez klamer wiąże `else` z makrem. Ten test
  // pilnuje, żeby taki zapis w kodzie firmware nie zmienił znaczenia.
  bool warunek = false;
  if (warunek) {
    LOG_INFO("[T]", "gałąź prawdziwa");
  } else {
    LOG_WARN("[T]", "gałąź fałszywa");
  }

  EXPECT_NE(output().find("[WARN]"), std::string::npos);
  EXPECT_EQ(output().find("[INFO]"), std::string::npos);
}

}  // namespace
