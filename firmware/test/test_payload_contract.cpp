// Test kontraktowy: pakiet zbudowany przez firmware musi przejść walidację
// schematem backendu (MeasurementPacketRequest, v=2, extra="forbid").
//
// Do tej pory rozjazd między firmware a backendem wychodził dopiero jako 422
// na produkcji — i to na całym pakiecie, bo pydantic odrzuca go w całości.
// Reguły pochodzą z generowanego test/contract/PayloadContract.h; kody błędów
// z SensorRegistry.h. Zmiana schematu backendu bez regeneracji jest łapana
// osobno, przez `generate_payload_contract.py --check` w hooku prebuild.
#include <gtest/gtest.h>

#include <ArduinoJson.h>
#include <FakeSensor.h>
#include <PayloadValidator.h>
#include <TelemetryPayload.h>

#include <string>
#include <vector>

namespace {

using payload_contract::Validator;
using payload_contract::Violation;

constexpr uint64_t kBaseUtcMs = 1786419922000ULL;  // 2026-08-11T03:45:22.000Z

class PayloadContractTest : public ::testing::Test {
 protected:
  void SetUp() override {
    temperature = new FakeSensor("pt100_temperature", "temperature", "\xC2\xB0" "C", "[PT100]");
    pressure = new FakeSensor("pt506_pressure", "pressure", "bar", "[PT506]");
    sensors.push_back(temperature);
    sensors.push_back(pressure);

    payload = new TelemetryPayload(String("WW-AABBCCDDEEFF"), sensors);
    payload->setGetUtcTime([]() { return kBaseUtcMs + 60000ULL; });
  }

  void TearDown() override {
    delete payload;
    delete temperature;
    delete pressure;
  }

  void sampleFullBatch() {
    for (size_t i = 0; i < TelemetryPayload::WINDOWS_PER_BATCH; ++i) {
      payload->sample(kBaseUtcMs + i * 15000ULL);
    }
  }

  // Buduje pakiet firmware'owy i zwraca go sparsowanego.
  void buildInto(JsonDocument& doc, uint32_t seq = 1786419982) {
    String json = payload->build(seq);
    ASSERT_FALSE(deserializeJson(doc, json)) << json.c_str();
  }

  static void expectValid(JsonDocument& doc) {
    std::vector<Violation> violations = Validator::validate(doc);
    EXPECT_TRUE(violations.empty()) << "backend odrzuciłby ten pakiet:" << Validator::describe(violations);
  }

  FakeSensor* temperature = nullptr;
  FakeSensor* pressure = nullptr;
  std::vector<ISensor*> sensors;
  TelemetryPayload* payload = nullptr;
};

// --- pakiety produkcyjne przechodzą walidację ------------------------------

TEST_F(PayloadContractTest, TypowyPakietPomiarowyJestZgodnyZeSchematem) {
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  expectValid(doc);
}

TEST_F(PayloadContractTest, PakietZBledemCzujnikaJestZgodnyZeSchematem) {
  // To jest przypadek, który wcześniej wywracał cały pakiet: firmware wysyłał
  // kod "SENSOR_FAULT" (spoza rejestru) z severity "error" (spoza Literal).
  temperature->read_ok = false;
  temperature->error_code = "SENSOR_FAULT_HW";
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  expectValid(doc);
}

TEST_F(PayloadContractTest, PakietPoPrzepelnieniuBuforaJestZgodnyZeSchematem) {
  for (size_t i = 0; i < TelemetryPayload::RETAIN_WINDOWS_MAX + 3; ++i) {
    payload->sample(kBaseUtcMs + i * 15000ULL);
  }

  JsonDocument doc;
  buildInto(doc);
  expectValid(doc);
}

TEST_F(PayloadContractTest, PakietZObydwomaCzujnikamiNiesprawnymiJestZgodnyZeSchematem) {
  temperature->read_ok = false;
  pressure->read_ok = false;
  pressure->error_code = "SENSOR_READ_FAILED";
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  // Okna bez punktów są dozwolone (points: min_length=0), ale błędy muszą być
  // poprawne — inaczej backend odrzuci pakiet, którego i tak brakuje danych.
  expectValid(doc);
}

TEST_F(PayloadContractTest, WersjaProtokoluZgadzaSieZOczekiwanaPrzezBackend) {
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  EXPECT_GE(doc["v"].as<int>(), PayloadContract::V_MIN);
  EXPECT_LE(doc["v"].as<int>(), PayloadContract::V_MAX);
}

TEST_F(PayloadContractTest, DlugoscOknaMiesciSieWLimicieBackendu) {
  sampleFullBatch();

  JsonDocument doc;
  buildInto(doc);
  int seconds = doc["windows"][0]["window_seconds"].as<int>();
  EXPECT_GT(seconds, PayloadContract::WINDOW_SECONDS_MIN_EXCLUSIVE);
  EXPECT_LE(seconds, PayloadContract::WINDOW_SECONDS_MAX);
}

// --- walidator ma zęby: celowe rozjazdy muszą być łapane -------------------
//
// Bez tych przypadków „pakiet przeszedł walidację" nie znaczyłoby nic — mógłby
// przechodzić także dlatego, że walidator niczego nie sprawdza.

class PayloadContractDetectionTest : public ::testing::Test {
 protected:
  // Poprawny pakiet jako punkt wyjścia do mutacji.
  static std::string validPacket() {
    return R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
           R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,)"
           R"("points":[{"point_id":"p","type":"temperature","unit":"C","quality":"good","value":21.5}]}]})";
  }

  static std::vector<Violation> validate(const std::string& json) {
    JsonDocument doc;
    EXPECT_FALSE(deserializeJson(doc, json)) << json;
    return Validator::validate(doc);
  }

  // Czy któreś naruszenie dotyczy wskazanego fragmentu ścieżki.
  static bool hasPath(const std::vector<Violation>& violations, const std::string& pathFragment) {
    for (const Violation& v : violations) {
      if (v.path.find(pathFragment) != std::string::npos) return true;
    }
    return false;
  }
};

TEST_F(PayloadContractDetectionTest, PunktOdniesieniaJestPoprawny) {
  EXPECT_TRUE(validate(validPacket()).empty());
}

TEST_F(PayloadContractDetectionTest, WykrywaBrakWymaganegoKlucza) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}]})";
  EXPECT_FALSE(validate(json).empty()) << "brak sent_at powinien zostać wykryty";
}

TEST_F(PayloadContractDetectionTest, WykrywaNadmiarowyKlucz) {
  // Backend ma extra="forbid": dodatkowe pole odrzuca cały pakiet.
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z","rssi":-70,)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}]})";
  EXPECT_FALSE(validate(json).empty());
}

TEST_F(PayloadContractDetectionTest, WykrywaZlaWersjeProtokolu) {
  std::string json = R"({"v":1,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}]})";
  std::vector<Violation> violations = validate(json);
  EXPECT_TRUE(hasPath(violations, "$.v"));
}

TEST_F(PayloadContractDetectionTest, WykrywaSeverityPozaLiteralBackendu) {
  // Dokładnie ten rozjazd żył w firmware: severity "error".
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}],)"
                     R"("errors":[{"code":"SENSOR_FAULT_HW","severity":"error","message":"x"}]})";
  std::vector<Violation> violations = validate(json);
  EXPECT_TRUE(hasPath(violations, "severity"));
}

TEST_F(PayloadContractDetectionTest, WykrywaKodBleduSpozaRejestru) {
  // Drugi element tego samego rozjazdu: kod "SENSOR_FAULT" nie istnieje.
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}],)"
                     R"("errors":[{"code":"SENSOR_FAULT","severity":"critical","message":"x"}]})";
  std::vector<Violation> violations = validate(json);
  EXPECT_TRUE(hasPath(violations, "code"));
}

TEST_F(PayloadContractDetectionTest, WykrywaSeverityNiezgodnaZRejestrem) {
  // Kod i poziom osobno poprawne, ale para się nie zgadza z sensor_registry.yaml.
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}],)"
                     R"("errors":[{"code":"SENSOR_FAULT_HW","severity":"info"}]})";
  EXPECT_TRUE(hasPath(validate(json), "severity"));
}

TEST_F(PayloadContractDetectionTest, WykrywaTypPunktuSpozaRejestru) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,)"
                     R"("points":[{"point_id":"p","type":"wilgotnosc","unit":"%","quality":"good","value":1}]}]})";
  EXPECT_TRUE(hasPath(validate(json), "type"));
}

TEST_F(PayloadContractDetectionTest, WykrywaPunktBezWartosciIBezAgregatu) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,)"
                     R"("points":[{"point_id":"p","type":"temperature","unit":"C","quality":"good"}]}]})";
  EXPECT_FALSE(validate(json).empty());
}

TEST_F(PayloadContractDetectionTest, AkceptujePunktZSamymiAgregatami) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,)"
                     R"("points":[{"point_id":"p","type":"temperature","unit":"C","quality":"good",)"
                     R"("avg":21.5,"min":20.0,"max":22.0}]}]})";
  EXPECT_TRUE(validate(json).empty());
}

TEST_F(PayloadContractDetectionTest, WykrywaZnacznikCzasuZ1970) {
  // Regresja: sample(millis()) zamiast sample(utcMs).
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"1970-01-01T00:00:15.000Z",)"
                     R"("windows":[{"window_start":"1970-01-01T00:00:15.000Z","window_seconds":15,"points":[]}]})";
  EXPECT_FALSE(validate(json).empty());
}

TEST_F(PayloadContractDetectionTest, WykrywaPustySentAt) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":15,"points":[]}]})";
  EXPECT_TRUE(hasPath(validate(json), "sent_at"));
}

TEST_F(PayloadContractDetectionTest, WykrywaPakietBezOkien) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z","windows":[]})";
  EXPECT_TRUE(hasPath(validate(json), "windows"));
}

TEST_F(PayloadContractDetectionTest, WykrywaZbytDlugieOkno) {
  std::string json = R"({"v":2,"device_id":"WW-1","seq":1,"sent_at":"2026-08-11T03:46:22.000Z",)"
                     R"("windows":[{"window_start":"2026-08-11T03:45:22.000Z","window_seconds":7200,"points":[]}]})";
  EXPECT_TRUE(hasPath(validate(json), "window_seconds"));
}

}  // namespace
