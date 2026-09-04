// Priorytet 6 wg ryzyka: sekwencja podnoszenia łącza LTE.
// Testowany jest prawdziwy ModemLink.cpp — TinyGSM zastępuje atrapa nagłówka
// z test/support/TinyGsmClient.h, sterowana przez NativeModemState.
#include <gtest/gtest.h>

#include <Config.h>
#include <ModemLink.h>

namespace {

class ModemLinkTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    NativeModemState::reset();
    Serial.clearCaptured();
    uart = new HardwareSerial(1);
    link = new ModemLink(*uart, MODEM_BAUD);
  }

  void TearDown() override {
    delete link;
    delete uart;
  }

  bool init() { return link->init(APN, GPRS_USER, GPRS_PASS, SIM_PIN); }

  NativeModemState& modem() { return NativeModemState::instance(); }

  HardwareSerial* uart = nullptr;
  ModemLink* link = nullptr;
};

// --- inicjalizacja ---------------------------------------------------------

TEST_F(ModemLinkTest, UdanaInicjalizacjaOtwieraUartINawiazujeGprs) {
  EXPECT_TRUE(init());

  EXPECT_TRUE(uart->begun);
  EXPECT_EQ(uart->baud_rate, MODEM_BAUD);
  EXPECT_EQ(uart->rx_pin, MODEM_RX_PIN);
  EXPECT_EQ(uart->tx_pin, MODEM_TX_PIN);
  EXPECT_GE(modem().init_calls, 1);
  EXPECT_GE(modem().wait_for_network_calls, 1);
  EXPECT_GE(modem().gprs_connect_calls, 1);
}

TEST_F(ModemLinkTest, PustyPinSimNieUruchamiaOdblokowania) {
  ASSERT_STREQ(SIM_PIN, "");
  init();
  EXPECT_EQ(modem().sim_unlock_calls, 0);
}

TEST_F(ModemLinkTest, PodanyPinSimJestUzywany) {
  link->init(APN, GPRS_USER, GPRS_PASS, "1234");
  EXPECT_EQ(modem().sim_unlock_calls, 1);
}

TEST_F(ModemLinkTest, PrzejsciowyBladInitJestPonawiany) {
  modem().init_failures_before_ok = 3;

  EXPECT_TRUE(init());
  EXPECT_EQ(modem().init_calls, 4);
}

TEST_F(ModemLinkTest, TrwalyBladInitKonczySieNiepowodzeniemWLimicieCzasu) {
  modem().init_ever_succeeds = false;

  unsigned long before = millis();
  EXPECT_FALSE(init());
  unsigned long elapsed = millis() - before;

  EXPECT_GT(modem().init_calls, 1);
  // Pętla init ma twardy limit 10 s; do tego stałe opóźnienia rozruchu (~7 s).
  EXPECT_LT(elapsed, 30000u) << "brak modemu nie może zawieszać rozruchu";
  EXPECT_EQ(modem().wait_for_network_calls, 0) << "bez init nie ma sensu czekać na sieć";
}

TEST_F(ModemLinkTest, BrakRejestracjiWSieciKonczyInicjalizacjeNiepowodzeniem) {
  modem().wait_for_network_ok = false;

  unsigned long before = millis();
  EXPECT_FALSE(init());

  // Pętla oczekiwania na sieć ma limit 60 s i nie ma w niej własnego delay() —
  // opiera się wyłącznie na tym, że TinyGSM blokuje na czas timeoutu.
  EXPECT_GE(millis() - before, 60000u);
  EXPECT_EQ(modem().gprs_connect_calls, 0);
}

TEST_F(ModemLinkTest, SiecJestALePadaAktywacjaApn) {
  modem().gprs_connect_ok = false;

  EXPECT_FALSE(init());
  EXPECT_GT(modem().gprs_connect_calls, 1) << "aktywacja APN musi być ponawiana";
}

TEST_F(ModemLinkTest, SiecZglaszaGotowoscAlePotemNieJestPodlaczona) {
  // waitForNetwork() zwraca true, ale isNetworkConnected() już nie — realny
  // przypadek przy chwilowej rejestracji w sieci.
  modem().network_connected = false;

  EXPECT_FALSE(init());
  EXPECT_EQ(modem().gprs_connect_calls, 0);
}

// --- utrzymanie łącza ------------------------------------------------------

TEST_F(ModemLinkTest, EnsureConnectedPrzedInitZwracaFalseZamiastPadac) {
  EXPECT_FALSE(link->ensureConnected());
}

TEST_F(ModemLinkTest, TestATPrzedInitZwracaFalse) { EXPECT_FALSE(link->testAT()); }

TEST_F(ModemLinkTest, ZdrowyLinkNieWykonujeZadnychAkcjiNaprawczych) {
  ASSERT_TRUE(init());
  int gprsConnectsAfterInit = modem().gprs_connect_calls;

  EXPECT_TRUE(link->ensureConnected());

  EXPECT_EQ(modem().gprs_disconnect_calls, 0);
  EXPECT_EQ(modem().gprs_connect_calls, gprsConnectsAfterInit);
}

TEST_F(ModemLinkTest, UtrataSieciUruchamiaPonownaRejestracje) {
  ASSERT_TRUE(init());
  int waitsAfterInit = modem().wait_for_network_calls;
  modem().network_connected = false;
  modem().wait_for_network_ok = false;

  EXPECT_FALSE(link->ensureConnected());
  EXPECT_EQ(modem().wait_for_network_calls, waitsAfterInit + 1);
}

TEST_F(ModemLinkTest, UtrataApnUruchamiaRozlaczenieIPonowneZestawienie) {
  ASSERT_TRUE(init());
  int connectsAfterInit = modem().gprs_connect_calls;
  modem().gprs_connected = false;

  EXPECT_TRUE(link->ensureConnected());

  EXPECT_EQ(modem().gprs_disconnect_calls, 1);
  EXPECT_EQ(modem().gprs_connect_calls, connectsAfterInit + 1);
}

TEST_F(ModemLinkTest, NieudaneZestawienieApnZwracaFalse) {
  ASSERT_TRUE(init());
  modem().gprs_connected = false;
  modem().gprs_connect_ok = false;

  EXPECT_FALSE(link->ensureConnected());
}

TEST_F(ModemLinkTest, TestATPoInicjalizacjiOdzwierciedlaStanModemu) {
  ASSERT_TRUE(init());

  modem().at_ok = true;
  EXPECT_TRUE(link->testAT());

  modem().at_ok = false;
  EXPECT_FALSE(link->testAT());
}

}  // namespace
