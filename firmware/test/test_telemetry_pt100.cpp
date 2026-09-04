// Integracja PT100 -> payload: prawdziwy PT100Sensor podpięty pod prawdziwy
// TelemetryPayload, ze sterownikiem MAX31865 zastąpionym atrapą nagłówka.
//
// Poprzednia wersja tego pliku miała własną kopię równania Callendara-Van Dusena
// i ręcznie sklejany JSON — nie dotykała ani PT100Sensor, ani TelemetryPayload.
// Sprawdzała też pola `avg`/`min`/`max` i `"v":1`, których firmware nie wysyła.
#include <gtest/gtest.h>

#include <ArduinoJson.h>
#include <Config.h>
#include <PT100Sensor.h>
#include <TelemetryPayload.h>

#include <string>
#include <vector>

namespace {

constexpr uint64_t kBaseUtcMs = 1786419922000ULL;  // 2026-08-11T03:45:22.000Z

class Pt100PayloadTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeMax31865State::reset();
    Serial.clearCaptured();

    sensor = new PT100Sensor(PT100_SPI_CS);
    sensors.push_back(sensor);
    payload = new TelemetryPayload(String("WW-AABBCCDDEEFF"), sensors);
    payload->setGetUtcTime([]() { return kBaseUtcMs + 60000ULL; });
  }

  void TearDown() override {
    delete payload;
    delete sensor;
  }

  NativeMax31865State& driver() { return NativeMax31865State::instance(); }

  void sampleFullBatch() {
    for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
      payload->sample(kBaseUtcMs + i * 15000ULL);
    }
  }

  void buildInto(JsonDocument& doc) {
    String json = payload->build(1);
    ASSERT_FALSE(deserializeJson(doc, json)) << json.c_str();
  }

  // Wartość RTD odpowiadająca zadanej rezystancji przy Rref = 430 Ω.
  static uint16_t rawForOhms(double ohms) { return static_cast<uint16_t>(ohms / 430.0 * 32768.0); }

  PT100Sensor* sensor = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

// --- odczyt trafia do pakietu ----------------------------------------------

TEST_F(Pt100PayloadTest, KonstruktorPayloaduInicjalizujeCzujnik) {
  // TelemetryPayload woła init() na każdym czujniku przy tworzeniu.
  EXPECT_EQ(driver().begin_calls, 1);
}

TEST_F(Pt100PayloadTest, TemperaturaTrafiaDoPunktuPomiarowego) {
  driver().rtd_raw = rawForOhms(110.0);  // ~25 °C
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  JsonVariant point = doc["windows"][0]["points"][0];

  EXPECT_STREQ(point["point_id"].as<const char*>(), "pt100_temperature");
  EXPECT_STREQ(point["type"].as<const char*>(), "temperature");
  EXPECT_STREQ(point["unit"].as<const char*>(), "\xC2\xB0" "C");
  EXPECT_STREQ(point["quality"].as<const char*>(), "good");

  float value = point["value"].as<float>();
  EXPECT_GT(value, 20.0f);
  EXPECT_LT(value, 30.0f);
}

TEST_F(Pt100PayloadTest, KazdeOknoNiesieOsobnyOdczyt) {
  sampleFullBatch();

  EXPECT_EQ(driver().read_rtd_calls, static_cast<int>(TelemetryPayload::WINDOWS_PER_BATCH));

  JsonDocument doc;
  buildInto(doc);
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    EXPECT_EQ(doc["windows"][i]["points"].size(), 1u) << "okno " << i;
  }
}

TEST_F(Pt100PayloadTest, ZmianaTemperaturyMiedzyOknamiJestWidoczna) {
  driver().rtd_raw = rawForOhms(100.0);  // ~0 °C
  payload->sample(kBaseUtcMs);
  driver().rtd_raw = rawForOhms(120.0);  // ~52 °C
  payload->sample(kBaseUtcMs + 15000);
  payload->sample(kBaseUtcMs + 30000);
  payload->sample(kBaseUtcMs + 45000);

  JsonDocument doc;
  buildInto(doc);

  float first = doc["windows"][0]["points"][0]["value"].as<float>();
  float second = doc["windows"][1]["points"][0]["value"].as<float>();
  EXPECT_GT(second, first + 10.0f) << "payload zamroziłby pierwszy odczyt";
}

// --- awaria czujnika --------------------------------------------------------

TEST_F(Pt100PayloadTest, AwariaCzujnikaDajeBladZamiastPunktu) {
  driver().fault = MAX31865_FAULT_RTDINLOW;  // przerwany przewód RTD
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);

  EXPECT_EQ(doc["windows"][0]["points"].size(), 0u) << "nie wolno wysyłać wartości z zepsutego czujnika";
  ASSERT_GE(doc["errors"].size(), 1u);
  EXPECT_STREQ(doc["errors"][0]["code"].as<const char*>(), "SENSOR_FAULT_HW");
  EXPECT_STREQ(doc["errors"][0]["point_id"].as<const char*>(), "pt100_temperature");
  EXPECT_STREQ(doc["errors"][0]["severity"].as<const char*>(), "critical");
}

TEST_F(Pt100PayloadTest, ChwilowaAwariaNieBlokujeKolejnychOdczytow) {
  // clearFault() w PT100Sensor kasuje flagę, więc kolejne okno czyta normalnie.
  driver().fault = MAX31865_FAULT_OVUV;
  payload->sample(kBaseUtcMs);
  payload->sample(kBaseUtcMs + 15000);
  payload->sample(kBaseUtcMs + 30000);
  payload->sample(kBaseUtcMs + 45000);

  JsonDocument doc;
  buildInto(doc);

  EXPECT_EQ(doc["windows"][0]["points"].size(), 0u) << "pierwsze okno: awaria";
  EXPECT_EQ(doc["windows"][1]["points"].size(), 1u) << "drugie okno: czujnik już czyta";
}

TEST_F(Pt100PayloadTest, TrwalaAwariaDajeJedenWpisBleduNaPakiet) {
  driver().fault = MAX31865_FAULT_REFINLOW;
  // Atrapa kasuje flagę po zgłoszeniu, więc ustawiamy ją przed każdym oknem.
  for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
    driver().fault = MAX31865_FAULT_REFINLOW;
    payload->sample(kBaseUtcMs + i * 15000ULL);
  }

  JsonDocument doc;
  buildInto(doc);

  EXPECT_EQ(doc["errors"].size(), 1u) << "cztery awarie tego samego punktu to jeden wpis, nie cztery";
}

// --- kształt pakietu --------------------------------------------------------

TEST_F(Pt100PayloadTest, PakietMaWersje2IIdentyfikatorUrzadzenia) {
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);

  EXPECT_EQ(doc["v"].as<int>(), 2);
  EXPECT_STREQ(doc["device_id"].as<const char*>(), "WW-AABBCCDDEEFF");
  EXPECT_EQ(doc["windows"][0]["window_seconds"].as<int>(), static_cast<int>(TelemetryPayload::WINDOW_SECONDS));
}

TEST_F(Pt100PayloadTest, PunktNieNiesieAgregatowKtorychFirmwareNieLiczy) {
  // Firmware wysyła pojedynczą wartość na okno; avg/min/max są opcjonalne
  // po stronie backendu i nie mogą pojawiać się puste.
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  JsonVariant point = doc["windows"][0]["points"][0];

  EXPECT_TRUE(point["avg"].isNull());
  EXPECT_TRUE(point["min"].isNull());
  EXPECT_TRUE(point["max"].isNull());
  EXPECT_FALSE(point["value"].isNull());
}

TEST_F(Pt100PayloadTest, PakietSerializujeSieDoPoprawnegoJson) {
  sampleFullBatch();

  String json = payload->build(1);
  ASSERT_FALSE(json.isEmpty());

  JsonDocument doc;
  EXPECT_FALSE(deserializeJson(doc, json)) << json.c_str();
  EXPECT_NE(std::string(json.c_str()).find("\"type\":\"temperature\""), std::string::npos);
}

}  // namespace
