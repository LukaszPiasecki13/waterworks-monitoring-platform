// Kontrakt szwu czasu (IClock), który zastąpił statyczne wołania TimeSync
// w TelemetrySender i DeviceAuthClient.
//
// Samego `TimeSync` nie da się zbudować na hoście (TinyGSM + zmienne w pamięci
// RTC z main.cpp), więc pokrywalna jest tu granica: jak konsumenci zachowują
// się wobec czasu i jak liczona jest sekundowa postać znacznika, po której
// porównywana jest ważność tokenu sesji.
//
// Poprzednia wersja tego pliku miała wklejoną kopię `formatIso8601` i błędną
// asercję (twierdziła, że 1786419922123 to 2026-08-10, a to 2026-08-11).
#include <gtest/gtest.h>

#include <DeviceAuthClient.h>
#include <FakeSensor.h>
#include <Fakes.h>
#include <TelemetryPayload.h>
#include <TelemetrySender.h>

#include <vector>

namespace {

constexpr uint32_t kNowUnix = 1786419922;  // 2026-08-11T03:45:22Z

// --- konwersja ms -> s -----------------------------------------------------

TEST(ClockContract, SekundyToObcieteMilisekundy) {
  FakeClock clock;
  clock.utc_ms = 1786419922999ULL;
  EXPECT_EQ(clock.utcSeconds(), 1786419922u) << "ułamek sekundy musi być obcięty, nie zaokrąglony";
}

TEST(ClockContract, BrakSynchronizacjiOznaczaZerowyCzas) {
  FakeClock clock;
  clock.synced = false;
  clock.utc_ms = 0;

  EXPECT_FALSE(clock.isSynced());
  EXPECT_EQ(clock.utcSeconds(), 0u);
}

TEST(ClockContract, ZnacznikPrzedGranica2106MiesciSieWUint32) {
  // Numer sekwencyjny pakietu i porównania ważności tokenu są na uint32_t.
  FakeClock clock;
  clock.utc_ms = 4294967295000ULL;  // 2106-02-07, maksimum uint32_t w sekundach
  EXPECT_EQ(clock.utcSeconds(), 4294967295u);
}

// --- konsumenci wobec braku synchronizacji ---------------------------------

class ClockConsumersTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    sensor = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-TEST"), sensors);
    clock.setUtcSeconds(kNowUnix);
  }

  void TearDown() override {
    delete payload;
    delete sensor;
  }

  FakeClock clock;
  FakeHttpClient http;
  FakeModemLink modem;
  FakeStatusLed led;
  FakeDeviceIdentity identity;

  FakeSensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

TEST_F(ClockConsumersTest, DeviceAuthClientNiePukaDoBackenduBezCzasu) {
  // Bez czasu nie da się ocenić ważności tokenu — każda próba byłaby zgadywaniem.
  clock.synced = false;
  DeviceAuthClient auth(identity, http, clock, 15000);

  for (unsigned long now = 0; now <= 300000; now += 15000) {
    auth.update(now);
  }

  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(ClockConsumersTest, DeviceAuthClientRuszaPoSynchronizacji) {
  clock.synced = false;
  DeviceAuthClient auth(identity, http, clock, 15000);
  auth.update(0);
  ASSERT_EQ(http.callCount(), 0u);

  clock.synced = true;
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
  http.queueResponse(200, "{\"token\":\"tok\",\"expires_at\":\"2026-08-12T15:45:22.000Z\"}");
  auth.update(15000);

  EXPECT_EQ(identity.set_token_calls, 1);
}

TEST_F(ClockConsumersTest, WaznoscSesjiLiczonaJestWSekundachZZegara) {
  // Token wygasa dokładnie na granicy marginesu odświeżania.
  identity.token = "tok";
  identity.token_expires_at = kNowUnix + identity.refresh_margin_seconds;
  EXPECT_FALSE(identity.hasValidSession(clock.utcSeconds())) << "granica marginesu = już nieważny";

  identity.token_expires_at = kNowUnix + identity.refresh_margin_seconds + 1;
  EXPECT_TRUE(identity.hasValidSession(clock.utcSeconds()));
}

TEST_F(ClockConsumersTest, ZnacznikPakietuPochodziZTegoSamegoZegaraCoSeq) {
  // Rozjazd między źródłem `sent_at` a źródłem `seq` dałby pakiety, w których
  // numer sekwencyjny nie odpowiada momentowi wysyłki.
  payload->setGetUtcTime([this]() { return clock.utcMs(); });
  TelemetrySender sender(modem, http, *payload, led, identity, clock, 15000, 5000);
  identity.token = "tok";
  identity.token_expires_at = kNowUnix + 36 * 3600;

  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    payload->sample(clock.utcMs());
    clock.utc_ms += 15000;
  }
  http.queueResponse(200, "{}");
  sender.update(15000);

  ASSERT_EQ(http.callCount(), 1u);
  EXPECT_EQ(sender.lastSeq(), clock.utcSeconds());
}

}  // namespace
