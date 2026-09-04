// Priorytet 2 wg ryzyka: pętla wysyłki telemetrii.
// Tu decyduje się, czy dane w ogóle wychodzą z urządzenia i czy po błędzie
// backendu urządzenie nie zgubi ani nie zduplikuje okien pomiarowych.
#include <gtest/gtest.h>

#include <ArduinoJson.h>
#include <Config.h>
#include <FakeSensor.h>
#include <Fakes.h>
#include <TelemetryPayload.h>
#include <TelemetrySender.h>

#include <string>
#include <vector>

namespace {

constexpr unsigned long kSampleIntervalMs = 15000;
constexpr unsigned long kErrorRetryMs = 5000;
constexpr uint32_t kNowUnix = 1786419922;  // 2026-08-11T03:45:22Z

class TelemetrySenderTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();

    sensor = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-TEST"), sensors);
    payload->setGetUtcTime([this]() { return clock_.utcMs(); });

    clock_.synced = true;
    clock_.setUtcSeconds(kNowUnix);

    identity.token = "session-token";
    identity.token_expires_at = kNowUnix + 36 * 3600;

    sender = new TelemetrySender(modem, http, *payload, led, identity, clock_, kSampleIntervalMs, kErrorRetryMs);
  }

  void TearDown() override {
    delete sender;
    delete payload;
    delete sensor;
  }

  // Doprowadza bufor do pełnej paczki, omijając pętlę sendera — inaczej próby
  // wysyłki z fazy przygotowania zaburzałyby liczniki atrap.
  void fillBatch(size_t windows = TelemetryPayload::WINDOWS_PER_BATCH) {
    for (size_t i = 0; i < windows; ++i) {
      payload->sample(clock_.utcMs());
      clock_.utc_ms += kSampleIntervalMs;
    }
  }

  FakeClock clock_;
  FakeHttpClient http;
  FakeModemLink modem;
  FakeStatusLed led;
  FakeDeviceIdentity identity;

  FakeSensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
  TelemetrySender* sender = nullptr;
};

// --- warunki wstępne -------------------------------------------------------

TEST_F(TelemetrySenderTest, BezSynchronizacjiCzasuNicSieNieDzieje) {
  clock_.synced = false;

  for (unsigned long now = kSampleIntervalMs; now <= 10 * kSampleIntervalMs; now += kSampleIntervalMs) {
    sender->update(now);
  }

  EXPECT_EQ(payload->bufferedWindows(), 0u) << "próbkowanie bez czasu UTC dałoby znaczniki z 1970";
  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(TelemetrySenderTest, ProbkujeCoSampleInterval) {
  modem.connected = false;
  sender->update(kSampleIntervalMs);
  sender->update(kSampleIntervalMs + 1);  // za wcześnie na kolejne okno
  sender->update(2 * kSampleIntervalMs);

  EXPECT_EQ(payload->bufferedWindows(), 2u);
}

TEST_F(TelemetrySenderTest, NiepelnaPaczkaNieJestWysylana) {
  unsigned long now = 0;
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH - 1; ++i) {
    now += kSampleIntervalMs;
    sender->update(now);
  }
  EXPECT_EQ(http.callCount(), 0u);
}

// --- ścieżka sukcesu -------------------------------------------------------

TEST_F(TelemetrySenderTest, PelnaPaczkaIdzieNaEndpointIngestZTokenem) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(200, "{}");

  now += kSampleIntervalMs;
  sender->update(now);

  ASSERT_EQ(http.callCount(), 1u);
  EXPECT_EQ(http.lastRequest().resource, std::string(RESOURCE));
  EXPECT_EQ(http.lastRequest().bearerToken, "session-token");
  EXPECT_EQ(led.success_blinks, 1);
  EXPECT_EQ(led.error_blinks, 0);
}

TEST_F(TelemetrySenderTest, SukcesPotwierdzaPaczkeIOproznaBufor) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(202, "");

  now += kSampleIntervalMs;
  sender->update(now);

  // Jedno okno z tego wywołania zostało dopróbkowane, cztery potwierdzone.
  EXPECT_EQ(payload->bufferedWindows(), 1u);
  EXPECT_EQ(sender->lastSuccessMs(), now);
}

TEST_F(TelemetrySenderTest, SeqOdpowiadaCzasowiUnixPakietu) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(200, "{}");

  now += kSampleIntervalMs;
  sender->update(now);

  JsonDocument doc;
  ASSERT_FALSE(deserializeJson(doc, http.lastRequest().payload));
  EXPECT_EQ(doc["seq"].as<unsigned long>(), clock_.utcSeconds());
  EXPECT_EQ(sender->lastSeq(), clock_.utcSeconds());
}

TEST_F(TelemetrySenderTest, KolejnaWysylkaMaWyzszeSeq) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(200, "{}");
  now += kSampleIntervalMs;
  sender->update(now);
  uint32_t firstSeq = sender->lastSeq();

  fillBatch();
  http.queueResponse(200, "{}");
  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_GT(sender->lastSeq(), firstSeq);
}

// --- ścieżki błędów --------------------------------------------------------

TEST_F(TelemetrySenderTest, BladSerweraNiePotwierdzaPaczki) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(500, "");

  now += kSampleIntervalMs;
  sender->update(now);

  // 4 okna z paczki + 1 dopróbkowane w tym wywołaniu; nic nie przepadło.
  EXPECT_EQ(payload->bufferedWindows(), TelemetryPayload::WINDOWS_PER_BATCH + 1);
  EXPECT_EQ(led.error_blinks, 1);
  EXPECT_EQ(sender->lastSuccessMs(), 0u);
}

TEST_F(TelemetrySenderTest, TeSameOknaIdaPonownieDopieroPoErrorRetry) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(500, "");

  now += kSampleIntervalMs;
  sender->update(now);
  ASSERT_EQ(http.callCount(), 1u);
  std::string firstPayload = http.lastRequest().payload;

  // Przed upływem error_retry — bez kolejnej próby.
  sender->update(now + kErrorRetryMs - 1);
  EXPECT_EQ(http.callCount(), 1u);

  // Po upływie — retry z tymi samymi (i nowszymi) oknami.
  http.queueResponse(200, "{}");
  sender->update(now + kErrorRetryMs);
  ASSERT_EQ(http.callCount(), 2u);

  JsonDocument first, second;
  ASSERT_FALSE(deserializeJson(first, firstPayload));
  ASSERT_FALSE(deserializeJson(second, http.lastRequest().payload));
  EXPECT_EQ(first["windows"][0]["window_start"].as<std::string>(),
            second["windows"][0]["window_start"].as<std::string>())
      << "po nieudanej wysyłce najstarsze okno musi wrócić, a nie przepaść";
}

TEST_F(TelemetrySenderTest, PoSukcesieToSamoOknoNieIdzieDrugiRaz) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(200, "{}");
  now += kSampleIntervalMs;
  sender->update(now);
  ASSERT_EQ(http.callCount(), 1u);

  JsonDocument first;
  ASSERT_FALSE(deserializeJson(first, http.lastRequest().payload));
  std::string firstWindow = first["windows"][0]["window_start"].as<std::string>();

  // Dozbieraj kolejną paczkę i wyślij ponownie.
  fillBatch();
  http.queueResponse(200, "{}");
  now += kSampleIntervalMs;
  sender->update(now);
  ASSERT_EQ(http.callCount(), 2u);

  JsonDocument second;
  ASSERT_FALSE(deserializeJson(second, http.lastRequest().payload));
  for (size_t i = 0; i < second["windows"].size(); ++i) {
    EXPECT_NE(second["windows"][i]["window_start"].as<std::string>(), firstWindow)
        << "okno potwierdzone przez backend zostało wysłane ponownie";
  }
}

TEST_F(TelemetrySenderTest, TimeoutTraktowanyJakBladPrzejsciowy) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(-1, "");  // brak odpowiedzi / timeout transportu

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_FALSE(sender->lastErrorWasPermanent());
  EXPECT_EQ(led.error_blinks, 1);
}

// 403/409/410 to stan „backend świadomie odmawia" — watchdog nie ma wtedy
// resetować modemu, bo problem nie leży po stronie łącza.
class TelemetrySenderPermanentErrorTest : public TelemetrySenderTest,
                                          public ::testing::WithParamInterface<int> {};

TEST_P(TelemetrySenderPermanentErrorTest, OznaczaBladJakoTrwaly) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(GetParam(), "");

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_TRUE(sender->lastErrorWasPermanent());
}

INSTANTIATE_TEST_SUITE_P(KodyTrwale, TelemetrySenderPermanentErrorTest, ::testing::Values(403, 409, 410));

TEST_F(TelemetrySenderTest, Status500NieJestBledemTrwalym) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(500, "");

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_FALSE(sender->lastErrorWasPermanent());
}

TEST_F(TelemetrySenderTest, SukcesKasujeFlageBleduTrwalego) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(409, "");
  now += kSampleIntervalMs;
  sender->update(now);
  ASSERT_TRUE(sender->lastErrorWasPermanent());

  http.queueResponse(200, "{}");
  sender->update(now + kErrorRetryMs);

  EXPECT_FALSE(sender->lastErrorWasPermanent());
}

// --- 401: urządzenie usunięte z platformy ----------------------------------

TEST_F(TelemetrySenderTest, Status401ZDeviceNotFoundCzysciStanProvisioningu) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(401, "{\"detail\":\"Device not found\"}");

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(identity.clear_state_calls, 1);
  EXPECT_FALSE(identity.isProvisioningCompleted());
}

TEST_F(TelemetrySenderTest, Status401ZInnymDetailNieCzysciProvisioningu) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(401, "{\"detail\":\"Token expired\"}");

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(identity.clear_state_calls, 0);
}

TEST_F(TelemetrySenderTest, Status401ZNieparsowalnymBodyNieWywracaWysylki) {
  unsigned long now = 0;
  fillBatch();
  http.queueResponse(401, "to nie jest json");

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(identity.clear_state_calls, 0);
  EXPECT_EQ(led.error_blinks, 1);
}

// --- brak łącza i brak sesji -----------------------------------------------

TEST_F(TelemetrySenderTest, BrakPolaczeniaWstrzymujeWysylkeIZapalaBlad) {
  unsigned long now = 0;
  fillBatch();
  modem.connected = false;

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(http.callCount(), 0u);
  EXPECT_EQ(led.error_blinks, 1);
  EXPECT_GE(payload->bufferedWindows(), TelemetryPayload::WINDOWS_PER_BATCH);
}

TEST_F(TelemetrySenderTest, BrakWaznejSesjiWstrzymujeWysylke) {
  unsigned long now = 0;
  fillBatch();
  identity.token_expires_at = 0;  // brak tokenu

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(TelemetrySenderTest, TokenTuzPrzedWygasnieciemJestUznanyZaNiewazny) {
  // Margines odświeżania ma sprawić, że urządzenie nie wysyła z tokenem,
  // który wygaśnie w trakcie transmisji.
  unsigned long now = 0;
  fillBatch();
  identity.token_expires_at = kNowUnix + identity.refresh_margin_seconds - 1;

  now += kSampleIntervalMs;
  sender->update(now);

  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(TelemetrySenderTest, DaneNiePrzepadajaPodczasDlugiegoBrakuSieci) {
  // Ok. 12 minut bez łącza: bufor zapełnia się do RETAIN_WINDOWS_MAX,
  // a po powrocie sieci wysyłka rusza od najstarszych zachowanych okien.
  modem.connected = false;
  unsigned long now = 0;
  for (size_t i = 0; i < TelemetryPayload::RETAIN_WINDOWS_MAX + 5; ++i) {
    now += kSampleIntervalMs;
    sender->update(now);
  }
  ASSERT_EQ(payload->bufferedWindows(), TelemetryPayload::RETAIN_WINDOWS_MAX);

  modem.connected = true;
  http.queueResponse(200, "{}");
  now += kErrorRetryMs;
  sender->update(now);

  EXPECT_EQ(http.callCount(), 1u);
  JsonDocument doc;
  ASSERT_FALSE(deserializeJson(doc, http.lastRequest().payload));
  EXPECT_EQ(doc["windows"].size(), TelemetryPayload::WINDOWS_PER_BATCH);
  // Przepełnienie musi być zaraportowane, inaczej utrata danych jest niewidoczna.
  ASSERT_GE(doc["errors"].size(), 1u);
  EXPECT_STREQ(doc["errors"][0]["code"].as<const char*>(), "WINDOW_DROPPED_BUFFER_FULL");
}

}  // namespace
