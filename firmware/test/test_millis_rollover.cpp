// Przewinięcie millis() po ~49,7 dnia pracy urządzenia.
//
// Gateway w hydroforni ma chodzić miesiącami bez restartu, więc licznik
// millis() (uint32_t) na pewno przekręci się przez zero. Porównania w postaci
// `now >= last + interval` i `now < next` przestają wtedy działać: pierwsze
// przepełnia się po prawej stronie, drugie porównuje wartość sprzed
// przewinięcia z wartością po nim.
//
// Każdy test poniżej pada na zapisie sprzed poprawki i przechodzi na
// porównaniach przez różnicę bez znaku.
#include <gtest/gtest.h>

#include <Config.h>
#include <DeviceAuthClient.h>
#include <EnrollmentClient.h>
#include <FakeSensor.h>
#include <Fakes.h>
#include <TelemetryPayload.h>
#include <TelemetrySender.h>
#include <Watchdog.h>

#include <string>
#include <vector>

namespace {

// 5 s przed przewinięciem licznika 32-bitowego. Wartość dobrana tak, żeby
// `kBeforeWrap + SAMPLE_INTERVAL_MS` faktycznie przepełniło uint32_t — inaczej
// stary zapis przypadkiem dalby poprawny wynik i test niczego by nie dowodził.
constexpr unsigned long kBeforeWrap = 0UL - 5000UL;
constexpr unsigned long kSampleIntervalMs = 15000;
constexpr unsigned long kErrorRetryMs = 5000;
constexpr uint32_t kNowUnix = 1786419922;

class MillisRolloverTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeClock::reset();
    Serial.clearInput();
    Serial.clearCaptured();

    sensor = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-TEST"), sensors);
    payload->setGetUtcTime([this]() { return clock_.utcMs(); });

    clock_.synced = true;
    clock_.setUtcSeconds(kNowUnix);
    identity.token = "session-token";
    identity.token_expires_at = kNowUnix + 36 * 3600;
  }

  void TearDown() override {
    delete payload;
    delete sensor;
  }

  FakeClock clock_;
  FakeHttpClient http;
  FakeModemLink modem;
  FakeStatusLed led;
  FakeDeviceIdentity identity;

  FakeSensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

// --- próbkowanie -----------------------------------------------------------

TEST_F(MillisRolloverTest, ProbkowanieTrzymaInterwalPrzezPrzewiniecie) {
  // Stary zapis `now >= last_sample_ms_ + interval` przepełniał prawą stronę
  // tuż przed przewinięciem i próbkował w KAŻDEJ iteracji pętli (co ~10 ms),
  // zasypując 12-minutowy bufor okien w kilkanaście sekund.
  modem.connected = false;  // interesuje nas samo próbkowanie
  TelemetrySender sender(modem, http, *payload, led, identity, clock_, kSampleIntervalMs, kErrorRetryMs);

  // Pierwsze okno tuż przed granicą.
  sender.update(kBeforeWrap);
  ASSERT_EQ(payload->bufferedWindows(), 1u);

  // 1500 iteracji pętli po 10 ms = 15 s, przechodząc przez zero.
  unsigned long now = kBeforeWrap;
  for (int tick = 0; tick < 1500; ++tick) {
    now += 10;
    sender.update(now);
  }

  // W 15 s mieści się dokładnie jedno kolejne okno.
  EXPECT_EQ(payload->bufferedWindows(), 2u)
      << "próbkowanie oderwało się od interwału przy przewinięciu millis()";
}

TEST_F(MillisRolloverTest, ProbkowanieNiePrzyspieszaTuzPrzedPrzewinieciem) {
  modem.connected = false;
  TelemetrySender sender(modem, http, *payload, led, identity, clock_, kSampleIntervalMs, kErrorRetryMs);

  sender.update(kBeforeWrap);
  ASSERT_EQ(payload->bufferedWindows(), 1u);

  // Wywołania w środku interwału nie mogą dokładać okien.
  for (unsigned long delta = 1; delta < kSampleIntervalMs; delta += 500) {
    sender.update(kBeforeWrap + delta);
  }

  EXPECT_EQ(payload->bufferedWindows(), 1u);
}

// --- backoff wysyłki -------------------------------------------------------

TEST_F(MillisRolloverTest, BackoffPoBledzieObowiazujeTakzePoPrzewinieciu) {
  // Stary zapis `now < next_send_attempt_ms_`: po błędzie tuż przed granicą
  // `next` przewijało się do małej liczby, a duże `now` przestawało być
  // mniejsze — urządzenie ponawiało wysyłkę w każdej iteracji pętli.
  TelemetrySender sender(modem, http, *payload, led, identity, clock_, kSampleIntervalMs, kErrorRetryMs);
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    payload->sample(clock_.utcMs());
    clock_.utc_ms += kSampleIntervalMs;
  }

  // Nieudana wysyłka 3 s przed przewinięciem: backoff 5 s przechodzi przez zero.
  const unsigned long failAt = 0UL - 3000UL;
  http.queueResponse(500, "");
  sender.update(failAt);
  ASSERT_EQ(http.callCount(), 1u);

  // 2 s później, wciąż w backoffie (już po przewinięciu millis()).
  // Termin ponowienia (failAt + 5 s) przewinął się, `now` jeszcze nie.
  sender.update(0UL - 1000UL);
  EXPECT_EQ(http.callCount(), 1u) << "backoff przeciekł na przewinięciu";

  // Po upływie 5 s próba wraca.
  http.queueResponse(200, "{}");
  sender.update(failAt + kErrorRetryMs);
  EXPECT_EQ(http.callCount(), 2u);
}

// --- odpytywanie o token ---------------------------------------------------

TEST_F(MillisRolloverTest, DlawienieDeviceAuthClientDzialaPoPrzewinieciu) {
  identity.token_expires_at = 0;  // brak sesji, więc klient chce się uwierzytelnić
  DeviceAuthClient auth(identity, http, clock_, CLAIM_POLL_INTERVAL_MS);

  const unsigned long firstPoll = 0UL - 3000UL;
  http.queueResponse(500, "");
  auth.update(firstPoll);
  ASSERT_EQ(http.callCount(), 1u);

  // Termin kolejnej próby (firstPoll + 15 s) już się przewinął, ale `now`
  // jeszcze nie — to jest moment, w którym stary zapis `now < next` zawodził.
  auth.update(0UL - 1000UL);
  EXPECT_EQ(http.callCount(), 1u) << "dławienie pollingu przeciekło na przewinięciu";

  http.queueResponse(500, "");
  auth.update(firstPoll + CLAIM_POLL_INTERVAL_MS);
  EXPECT_EQ(http.callCount(), 2u);
}

// --- backoff aktywacji -----------------------------------------------------

TEST_F(MillisRolloverTest, BackoffAktywacjiDzialaPoPrzewinieciu) {
  identity.provisioning_completed = false;
  EnrollmentClient enrollment(identity, &http);
  enrollment.submitLine(String("ACTIVATE ABCD-EFGH-JKLM"));
  enrollment.onModemReady();

  const unsigned long firstTry = 0UL - 3000UL;
  http.queueResponse(500, "");
  enrollment.update(firstTry);
  ASSERT_EQ(http.callCount(), 1u);

  // Jak wyżej: termin ponowienia przewinął się, `now` jeszcze nie.
  enrollment.update(0UL - 1000UL);
  EXPECT_EQ(http.callCount(), 1u) << "backoff aktywacji przeciekł na przewinięciu";

  http.queueResponse(200, "{}");
  enrollment.update(firstTry + ACTIVATION_RETRY_INTERVAL_MS);
  EXPECT_EQ(http.callCount(), 2u);
}

// --- watchdog --------------------------------------------------------------

TEST_F(MillisRolloverTest, WatchdogNieUznajeUrzadzeniaZaZawieszonePoPrzewinieciu) {
  // Ten warunek (`now - lastSuccessMs`) był już odporny; test pilnuje, żeby
  // ktoś go nie „poprawił" na zapis z dodawaniem.
  FakeModemPower power;
  FakeSystemControl system;
  Watchdog watchdog(modem, power, system, WATCHDOG_STUCK_MS, MAX_RESTART_ATTEMPTS);
  modem.at_ok = false;

  const unsigned long lastSuccess = 0UL - 1000UL;  // 1 s przed przewinięciem
  watchdog.check(lastSuccess + 2000, lastSuccess);  // 2 s później, już po zerze

  EXPECT_EQ(modem.test_at_calls, 0) << "2 s bez wysyłki to nie jest zawieszenie";
}

}  // namespace
