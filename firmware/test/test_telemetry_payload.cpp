// Priorytet 1 wg ryzyka: bufor okien pomiarowych.
// Awaria tej warstwy w terenie oznacza ciche gubienie danych albo pakiety,
// których backend nie przyjmie — jedno i drugie widać dopiero po fakcie.
#include <gtest/gtest.h>

#include <ArduinoJson.h>
#include <FakeSensor.h>
#include <TelemetryPayload.h>

#include <string>
#include <vector>

namespace {

constexpr uint64_t kBaseUtcMs = 1786419922000ULL;  // 2026-08-11T03:45:22.000Z

class TelemetryPayloadTest : public ::testing::Test {
 protected:
  void SetUp() override {
    sensor = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-TEST"), sensors);
    payload->setGetUtcTime([]() { return kBaseUtcMs + 60000ULL; });
  }

  void TearDown() override {
    delete payload;
    delete sensor;
  }

  // Próbkuje `count` okien, każde 15 s po poprzednim.
  void sampleWindows(size_t count, uint64_t startMs = kBaseUtcMs) {
    for (size_t i = 0; i < count; ++i) {
      payload->sample(startMs + i * 15000ULL);
    }
  }

  JsonDocument buildAndParse(uint32_t seq = 1) {
    String json = payload->build(seq);
    JsonDocument doc;
    EXPECT_FALSE(deserializeJson(doc, json)) << "payload nie jest poprawnym JSON-em: " << json.c_str();
    return doc;
  }

  FakeSensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

// --- gotowość do wysyłki ---------------------------------------------------

TEST_F(TelemetryPayloadTest, NieJestGotowyPonizejPelnejPaczki) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH - 1);
  EXPECT_FALSE(payload->isReadyToSend());
}

TEST_F(TelemetryPayloadTest, JestGotowyPoPelnejPaczce) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);
  EXPECT_TRUE(payload->isReadyToSend());
}

// --- kolejność i zawartość okien -------------------------------------------

TEST_F(TelemetryPayloadTest, BuildEmitujeDokladnieJednaPaczke) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH + 3);

  JsonDocument doc = buildAndParse();
  EXPECT_EQ(doc["windows"].size(), TelemetryPayload::WINDOWS_PER_BATCH);
}

TEST_F(TelemetryPayloadTest, OknaWychodzaWKolejnosciProbkowania) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  std::string previous;
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    std::string current = doc["windows"][i]["window_start"].as<std::string>();
    ASSERT_FALSE(current.empty());
    if (!previous.empty()) {
      EXPECT_LT(previous, current) << "okno " << i << " ma wcześniejszy znacznik niż poprzednie";
    }
    previous = current;
  }
}

TEST_F(TelemetryPayloadTest, PunktPomiaruNiesieTypJednostkeIWartosc) {
  sensor->next_value = 21.5f;
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  JsonVariant point = doc["windows"][0]["points"][0];

  EXPECT_STREQ(point["point_id"].as<const char*>(), "pt100_temperature");
  EXPECT_STREQ(point["type"].as<const char*>(), "temperature");
  EXPECT_STREQ(point["unit"].as<const char*>(), "\xC2\xB0" "C");
  EXPECT_STREQ(point["quality"].as<const char*>(), "good");
  EXPECT_FLOAT_EQ(point["value"].as<float>(), 21.5f);
}

TEST_F(TelemetryPayloadTest, ZnacznikiCzasuSaZUtcANieOdStartuUrzadzenia) {
  // Regresja: przekazanie millis() zamiast czasu UTC dawało pakiety z 1970 roku.
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  std::string windowStart = doc["windows"][0]["window_start"].as<std::string>();
  std::string sentAt = doc["sent_at"].as<std::string>();

  EXPECT_EQ(windowStart.rfind("2026-08-11T03:45:22", 0), 0u) << windowStart;
  EXPECT_EQ(sentAt.rfind("2026-08-11T03:46:22", 0), 0u) << sentAt;
  EXPECT_EQ(windowStart.find("1970"), std::string::npos);
}

TEST_F(TelemetryPayloadTest, BrakZrodlaCzasuDajePustySentAt) {
  // Gdy setGetUtcTime() nie zostało wywołane, sent_at jest pusty — backend
  // odrzuci taki pakiet (sent_at: datetime), więc to musi być widoczne.
  TelemetryPayload bare(String("WW-TEST"), sensors);
  bare.sample(kBaseUtcMs);
  bare.sample(kBaseUtcMs + 15000);
  bare.sample(kBaseUtcMs + 30000);
  bare.sample(kBaseUtcMs + 45000);

  JsonDocument doc;
  ASSERT_FALSE(deserializeJson(doc, bare.build(1)));
  EXPECT_STREQ(doc["sent_at"].as<const char*>(), "");
}

// --- czyszczenie po wysyłce ------------------------------------------------

TEST_F(TelemetryPayloadTest, AcknowledgeUsuwaTylkoWyslanaPaczke) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH + 2);
  ASSERT_EQ(payload->bufferedWindows(), TelemetryPayload::WINDOWS_PER_BATCH + 2);

  payload->build(1);
  payload->acknowledge();

  EXPECT_EQ(payload->bufferedWindows(), 2u);
}

TEST_F(TelemetryPayloadTest, KolejnyBuildStartujeOdNiewyslanychOkien) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH + 1);

  JsonDocument first = buildAndParse(1);
  std::string lastOfFirstBatch =
      first["windows"][TelemetryPayload::WINDOWS_PER_BATCH - 1]["window_start"].as<std::string>();
  payload->acknowledge();

  JsonDocument second = buildAndParse(2);
  ASSERT_EQ(second["windows"].size(), 1u);
  std::string firstOfSecondBatch = second["windows"][0]["window_start"].as<std::string>();

  EXPECT_LT(lastOfFirstBatch, firstOfSecondBatch) << "okno powtórzone albo pominięte";
}

TEST_F(TelemetryPayloadTest, BrakAcknowledgeZachowujeOknaDoPonownejWysylki) {
  // Nieudana wysyłka nie potwierdza pakietu; dane muszą przetrwać do retry.
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument first = buildAndParse(1);
  JsonDocument retry = buildAndParse(2);

  EXPECT_EQ(payload->bufferedWindows(), TelemetryPayload::WINDOWS_PER_BATCH);
  EXPECT_EQ(first["windows"][0]["window_start"].as<std::string>(),
            retry["windows"][0]["window_start"].as<std::string>());
}

TEST_F(TelemetryPayloadTest, AcknowledgeBezBuildaNieUsuwaNiczego) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);
  payload->acknowledge();
  EXPECT_EQ(payload->bufferedWindows(), TelemetryPayload::WINDOWS_PER_BATCH);
}

// --- przepełnienie bufora --------------------------------------------------

TEST_F(TelemetryPayloadTest, BuforNiePrzekraczaRetainWindowsMax) {
  sampleWindows(TelemetryPayload::RETAIN_WINDOWS_MAX + 10);
  EXPECT_EQ(payload->bufferedWindows(), TelemetryPayload::RETAIN_WINDOWS_MAX);
}

TEST_F(TelemetryPayloadTest, PrzepelnienieZglaszaWindowDroppedBufferFull) {
  sampleWindows(TelemetryPayload::RETAIN_WINDOWS_MAX + 1);

  JsonDocument doc = buildAndParse();
  ASSERT_EQ(doc["errors"].size(), 1u);
  EXPECT_STREQ(doc["errors"][0]["code"].as<const char*>(), "WINDOW_DROPPED_BUFFER_FULL");
  EXPECT_STREQ(doc["errors"][0]["severity"].as<const char*>(), "warning");
}

TEST_F(TelemetryPayloadTest, PrzepelnienieGubiNajstarszeOknoANieNajnowsze) {
  // Przy zapełnionym buforze najstarsze dane odpadają; świeży pomiar zostaje.
  const uint64_t start = kBaseUtcMs;
  sampleWindows(TelemetryPayload::RETAIN_WINDOWS_MAX, start);
  const uint64_t overflowWindowMs = start + TelemetryPayload::RETAIN_WINDOWS_MAX * 15000ULL;
  payload->sample(overflowWindowMs);

  ASSERT_EQ(payload->bufferedWindows(), TelemetryPayload::RETAIN_WINDOWS_MAX);

  JsonDocument doc = buildAndParse();
  // Pierwsze okno w paczce to teraz drugie próbkowane, nie pierwsze.
  EXPECT_EQ(doc["windows"][0]["window_start"].as<std::string>(), "2026-08-11T03:45:37.000Z");
}

// --- bufor błędów ----------------------------------------------------------

TEST_F(TelemetryPayloadTest, BladOdczytuTrafiaDoErrorsZKodemZOdczytu) {
  sensor->read_ok = false;
  sensor->error_code = "SENSOR_FAULT_HW";
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  ASSERT_EQ(doc["errors"].size(), 1u);
  EXPECT_STREQ(doc["errors"][0]["code"].as<const char*>(), "SENSOR_FAULT_HW");
  EXPECT_STREQ(doc["errors"][0]["point_id"].as<const char*>(), "pt100_temperature");
  // Severity pochodzi z rejestru, nie z kodu firmware.
  EXPECT_STREQ(doc["errors"][0]["severity"].as<const char*>(), "critical");
}

TEST_F(TelemetryPayloadTest, BladOdczytuBezKoduDajeSensorReadFailed) {
  sensor->read_ok = false;
  sensor->error_code = nullptr;
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  ASSERT_EQ(doc["errors"].size(), 1u);
  EXPECT_STREQ(doc["errors"][0]["code"].as<const char*>(), "SENSOR_READ_FAILED");
  EXPECT_STREQ(doc["errors"][0]["severity"].as<const char*>(), "warning");
}

TEST_F(TelemetryPayloadTest, NieudanyOdczytNieDodajePunktuPomiarowego) {
  sensor->read_ok = false;
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  JsonDocument doc = buildAndParse();
  EXPECT_EQ(doc["windows"][0]["points"].size(), 0u);
}

TEST_F(TelemetryPayloadTest, PowtarzaneBuildyNieMnozaTegoSamegoBledu) {
  // build() jest wołany przy każdej próbie wysyłki. Bez deduplikacji jeden
  // trwały błąd czujnika zapełniłby bufor błędów w kilka minut.
  sensor->read_ok = false;
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);

  for (int attempt = 0; attempt < 10; ++attempt) {
    payload->build(attempt + 1);
  }

  EXPECT_EQ(payload->pendingErrors(), 1u);
}

TEST_F(TelemetryPayloadTest, BuforBledowNiePrzekraczaMaxErrors) {
  // Każdy wpis dotyczy innego punktu, więc deduplikacja go nie pochłania —
  // inaczej ten test nigdy nie dobiłby do limitu i niczego by nie sprawdzał.
  // Identyfikatory muszą przeżyć do acknowledge(), stąd statyczna tablica.
  static std::vector<std::string> pointIds;
  const size_t total = TelemetryPayload::MAX_ERRORS + 20;
  pointIds.clear();
  pointIds.reserve(total);
  for (size_t i = 0; i < total; ++i) {
    pointIds.push_back("punkt_" + std::to_string(i));
  }

  for (size_t i = 0; i < total; ++i) {
    payload->addError("SENSOR_READ_FAILED", pointIds[i].c_str(), "x");
  }

  EXPECT_EQ(payload->pendingErrors(), TelemetryPayload::MAX_ERRORS);
}

TEST_F(TelemetryPayloadTest, PrzepelnienieBuforaBledowUsuwaNajstarszeWpisy) {
  static std::vector<std::string> pointIds;
  const size_t total = TelemetryPayload::MAX_ERRORS + 1;
  pointIds.clear();
  pointIds.reserve(total);
  for (size_t i = 0; i < total; ++i) {
    pointIds.push_back("punkt_" + std::to_string(i));
  }
  for (size_t i = 0; i < total; ++i) {
    payload->addError("SENSOR_READ_FAILED", pointIds[i].c_str(), "x");
  }

  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);
  JsonDocument doc = buildAndParse();

  ASSERT_EQ(doc["errors"].size(), TelemetryPayload::MAX_ERRORS);
  EXPECT_STREQ(doc["errors"][0]["point_id"].as<const char*>(), "punkt_1")
      << "najstarszy wpis musi wypaść, a nie najnowszy";
}

TEST_F(TelemetryPayloadTest, KodSpozaRejestruJestOdrzucany) {
  // Kod nieznany rejestrowi unieważniłby cały pakiet po stronie backendu.
  payload->addError("NIE_MA_TAKIEGO_KODU", nullptr, "x");
  EXPECT_EQ(payload->pendingErrors(), 0u);
}

TEST_F(TelemetryPayloadTest, AcknowledgeCzysciBufoBledow) {
  payload->addError("POWER_LOW", nullptr, "x");
  ASSERT_EQ(payload->pendingErrors(), 1u);

  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);
  payload->build(1);
  payload->acknowledge();

  EXPECT_EQ(payload->pendingErrors(), 0u);
}

TEST_F(TelemetryPayloadTest, PakietBezBledowNieMaKluczaErrors) {
  sampleWindows(TelemetryPayload::WINDOWS_PER_BATCH);
  JsonDocument doc = buildAndParse();
  EXPECT_TRUE(doc["errors"].isNull());
}

}  // namespace
