// Regresja: pakiety ze znacznikami z 1970 roku.
//
// Objaw z terenu: `sample(millis())` zamiast `sample(utcMs)` dawało
// "window_start":"1970-01-01T00:00:15.000Z". Backend przyjmował takie pakiety
// (data jest formalnie poprawna), więc dane trafiały do bazy z bezużytecznym
// czasem i nikt tego nie zauważał.
//
// Poprzednia wersja tego pliku miała własną kopię `formatIso8601` i asertowała
// na kopii — przechodziłaby także wtedy, gdyby firmware był zepsuty. Tu
// sprawdzany jest prawdziwy TelemetryPayload i prawdziwy TelemetrySender.
#include <gtest/gtest.h>

#include <ArduinoJson.h>
#include <FakeSensor.h>
#include <Fakes.h>
#include <TelemetryPayload.h>
#include <TelemetrySender.h>

#include <string>
#include <vector>

namespace {

class TimestampRegressionTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    sensor = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-TEST"), sensors);
  }

  void TearDown() override {
    delete payload;
    delete sensor;
  }

  std::string firstWindowStart(uint64_t sampleUtcMs) {
    for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
      payload->sample(sampleUtcMs + i * 15000ULL);
    }
    JsonDocument doc;
    EXPECT_FALSE(deserializeJson(doc, payload->build(1)));
    return doc["windows"][0]["window_start"].as<std::string>();
  }

  FakeSensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

// --- sedno regresji --------------------------------------------------------

TEST_F(TimestampRegressionTest, CzasUtcDajeBiezacaDate) {
  payload->setGetUtcTime([]() { return 1786419982000ULL; });

  std::string windowStart = firstWindowStart(1786419922000ULL);

  EXPECT_EQ(windowStart, "2026-08-11T03:45:22.000Z");
  EXPECT_EQ(windowStart.find("1970"), std::string::npos);
}

TEST_F(TimestampRegressionTest, CzasOdStartuUrzadzeniaDaje1970) {
  // Dokładne odtworzenie błędu: 15 000 ms od bootu potraktowane jak czas UTC.
  payload->setGetUtcTime([]() { return 15000ULL; });

  std::string windowStart = firstWindowStart(15000ULL);

  EXPECT_EQ(windowStart.rfind("1970-01-01T00:00:15", 0), 0u)
      << "gdyby to się zmieniło, powyższy test straciłby sens";
}

TEST_F(TimestampRegressionTest, ZerowyCzasDajePustyZnacznik) {
  payload->setGetUtcTime([]() { return 0ULL; });
  payload->sample(0);
  payload->sample(15000);
  payload->sample(30000);
  payload->sample(45000);

  JsonDocument doc;
  ASSERT_FALSE(deserializeJson(doc, payload->build(1)));

  // Pusty łańcuch zamiast daty z 1970 — backend odrzuci pakiet zamiast
  // przyjąć go z bezużytecznym czasem.
  EXPECT_STREQ(doc["sent_at"].as<const char*>(), "");
  EXPECT_STREQ(doc["windows"][0]["window_start"].as<const char*>(), "");
}

// --- warstwa wyżej: sender w ogóle nie próbkuje bez czasu ------------------

TEST_F(TimestampRegressionTest, SenderNiePróbkujeDopokiCzasNieJestZsynchronizowany) {
  FakeClock clock;
  FakeHttpClient http;
  FakeModemLink modem;
  FakeStatusLed led;
  FakeDeviceIdentity identity;
  clock.synced = false;

  TelemetrySender sender(modem, http, *payload, led, identity, clock, 15000, 5000);
  for (unsigned long now = 15000; now <= 150000; now += 15000) {
    sender.update(now);
  }

  EXPECT_EQ(payload->bufferedWindows(), 0u)
      << "bez synchronizacji NTP każde okno miałoby znacznik z 1970";
}

TEST_F(TimestampRegressionTest, SenderPróbkujeGdyCzasJestZsynchronizowany) {
  FakeClock clock;
  FakeHttpClient http;
  FakeModemLink modem;
  FakeStatusLed led;
  FakeDeviceIdentity identity;
  clock.synced = true;
  clock.setUtcSeconds(1786419922);
  modem.connected = false;  // blokuje wysyłkę, zostawia samo próbkowanie
  payload->setGetUtcTime([&clock]() { return clock.utcMs(); });

  TelemetrySender sender(modem, http, *payload, led, identity, clock, 15000, 5000);
  sender.update(15000);

  ASSERT_EQ(payload->bufferedWindows(), 1u);
}

// --- format i zakres -------------------------------------------------------

TEST_F(TimestampRegressionTest, ZnacznikMaFormatIso8601ZeStrefaZ) {
  payload->setGetUtcTime([]() { return 1786419982123ULL; });
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    payload->sample(1786419922456ULL + i * 15000ULL);
  }

  JsonDocument doc;
  ASSERT_FALSE(deserializeJson(doc, payload->build(1)));

  std::string sentAt = doc["sent_at"].as<std::string>();
  ASSERT_EQ(sentAt.size(), 24u) << sentAt;  // YYYY-MM-DDTHH:MM:SS.sssZ
  EXPECT_EQ(sentAt[4], '-');
  EXPECT_EQ(sentAt[7], '-');
  EXPECT_EQ(sentAt[10], 'T');
  EXPECT_EQ(sentAt[19], '.');
  EXPECT_EQ(sentAt.back(), 'Z');
  EXPECT_EQ(sentAt.substr(20, 3), "123") << "milisekundy muszą przetrwać";
}

TEST_F(TimestampRegressionTest, ZnacznikPozaRokiem2038JestPoprawny) {
  // uint64_t w milisekundach; limit 2038 (32-bitowy time_t) nie obowiązuje.
  payload->setGetUtcTime([]() { return 2524608000000ULL; });  // 2050-01-01T00:00:00Z
  std::string windowStart = firstWindowStart(2524608000000ULL);

  EXPECT_EQ(windowStart, "2050-01-01T00:00:00.000Z");
}

}  // namespace
