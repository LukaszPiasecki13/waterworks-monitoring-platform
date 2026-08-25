#include <gtest/gtest.h>
#include <cmath>
#include <ArduinoJson.h>

// Define PT100 wiring mode before use
#define MAX31865_3WIRE 1

// Mock the Adafruit_MAX31865 class for testing
class Adafruit_MAX31865 {
 public:
  Adafruit_MAX31865(uint8_t cs_pin) : cs_pin_(cs_pin), initialized_(false), rtd_value_(3200) {}

  bool begin(uint8_t wires) {
    initialized_ = true;
    return true;
  }

  uint16_t readRTD() { return rtd_value_; }

  void setRTDValue(uint16_t rtd) { rtd_value_ = rtd; }

 private:
  uint8_t cs_pin_;
  bool initialized_;
  uint16_t rtd_value_;
};

// Simulate the PT100 temperature calculation logic using Callendar-Van Dusen equation
class PT100TemperatureCalculator {
 public:
  static float calculateTemperature(uint16_t rtd) {
    // PT100 constants
    const float RTDNOMINAL = 100.0;   // 100Ω at 0°C
    const float REFRESISTOR = 430.0;  // 430Ω reference resistor

    // Callendar-Van Dusen coefficients for PT100
    const float a = 3.9083e-3;
    const float b = -5.775e-7;
    const float c = -4.183e-12;

    // Convert RTD raw value to resistance in Ohms
    float rtratio = rtd;
    rtratio /= 32768.0;
    float R = rtratio * REFRESISTOR;  // R in Ohms

    // Calculate temperature using Callendar-Van Dusen equation
    float Rpoly = b * b;
    Rpoly -= (4.0 * c * (R - RTDNOMINAL));
    Rpoly = sqrt(Rpoly);
    Rpoly += b;
    Rpoly /= 2.0;
    Rpoly *= -1.0;

    float temp = (R - RTDNOMINAL) / (a * RTDNOMINAL);
    temp -= Rpoly / (a * RTDNOMINAL);

    return temp;
  }
};

// Test Suite for PT100 Sensor Integration
class PT100SensorTest : public ::testing::Test {
 protected:
  void SetUp() override {
    sensor_.reset(new Adafruit_MAX31865(39));
    EXPECT_TRUE(sensor_->begin(MAX31865_3WIRE));
  }

  std::unique_ptr<Adafruit_MAX31865> sensor_;
};

// Test 1: MAX31865 Initialization
TEST_F(PT100SensorTest, MAX31865Initialization) { EXPECT_TRUE(sensor_->begin(MAX31865_3WIRE)); }

// Test 2: PT100 Temperature Calculation with Known RTD Values
TEST_F(PT100SensorTest, CalculateTemperatureFromRTD) {
  // Test case 1: RTD value corresponding to ~0°C
  // For PT100: R(0°C) = 100Ω, ratio = 100/32768 ≈ 0.00305
  float temp_0c = PT100TemperatureCalculator::calculateTemperature(100);
  EXPECT_NEAR(temp_0c, 0.0, 2.0);  // Tolerance of ±2°C due to calibration

  // Test case 2: RTD value for ~25°C (typical room temperature)
  // Approximately 110Ω at 25°C
  float temp_25c = PT100TemperatureCalculator::calculateTemperature(819);  // ~25°C
  EXPECT_GE(temp_25c, 20.0);
  EXPECT_LE(temp_25c, 30.0);

  // Test case 3: RTD value for ~100°C
  // Approximately 139Ω at 100°C
  float temp_100c = PT100TemperatureCalculator::calculateTemperature(4554);  // ~100°C
  EXPECT_GE(temp_100c, 95.0);
  EXPECT_LE(temp_100c, 105.0);
}

// Test 3: Temperature Range Validation
TEST_F(PT100SensorTest, TemperatureInValidRange) {
  // Test that calculated temperature is within -10°C to +100°C range
  for (uint16_t rtd = 400; rtd <= 4600; rtd += 200) {
    float temperature = PT100TemperatureCalculator::calculateTemperature(rtd);
    EXPECT_GE(temperature, -10.0);
    EXPECT_LE(temperature, 100.0);
  }
}

// Test 4: JSON Payload Structure with Temperature
class TelemetryPayloadStructureTest : public ::testing::Test {
 protected:
  JsonDocument createPayloadWithTemperature(float temperature) {
    JsonDocument doc;

    doc["v"] = 1;
    doc["device_id"] = "test-device-001";
    doc["seq"] = 1;
    doc["sent_at"] = "2026-08-24T12:00:00.000Z";

    JsonArray windows = doc["windows"].to<JsonArray>();
    JsonObject window = windows.add<JsonObject>();

    window["window_start"] = "2026-08-24T12:00:00.000Z";
    window["window_seconds"] = 30;

    JsonArray points = window["points"].to<JsonArray>();
    JsonObject point = points.add<JsonObject>();

    point["point_id"] = "pt100_temperature";
    point["type"] = "temperature";
    point["unit"] = "°C";
    point["quality"] = "good";
    point["avg"] = roundf(temperature * 100.0f) / 100.0f;
    point["min"] = -10;
    point["max"] = 100;
    point["value"] = roundf(temperature * 100.0f) / 100.0f;

    return doc;
  }
};

TEST_F(TelemetryPayloadStructureTest, ContainsTemperatureType) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  EXPECT_STREQ(doc["windows"][0]["points"][0]["type"], "temperature");
}

TEST_F(TelemetryPayloadStructureTest, ContainsCorrectUnit) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  EXPECT_STREQ(doc["windows"][0]["points"][0]["unit"], "°C");
}

TEST_F(TelemetryPayloadStructureTest, ContainsPointId) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  EXPECT_STREQ(doc["windows"][0]["points"][0]["point_id"], "pt100_temperature");
}

TEST_F(TelemetryPayloadStructureTest, ContainsValidTemperatureValue) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  float value = doc["windows"][0]["points"][0]["value"];
  EXPECT_FLOAT_EQ(value, 22.5);
}

TEST_F(TelemetryPayloadStructureTest, ContainsQualityField) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  EXPECT_STREQ(doc["windows"][0]["points"][0]["quality"], "good");
}

TEST_F(TelemetryPayloadStructureTest, MinMaxValuesCorrect) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  int min_val = doc["windows"][0]["points"][0]["min"];
  int max_val = doc["windows"][0]["points"][0]["max"];

  EXPECT_EQ(min_val, -10);
  EXPECT_EQ(max_val, 100);
}

// Test 5: Serialization to JSON String
TEST_F(TelemetryPayloadStructureTest, SerializesToValidJSON) {
  float temp = 22.5;
  JsonDocument doc = createPayloadWithTemperature(temp);

  String payload;
  serializeJson(doc, payload);

  EXPECT_FALSE(payload.isEmpty());
  EXPECT_GT(payload.length(), 0);
  EXPECT_THAT(std::string(payload.c_str()), ::testing::HasSubstr("\"type\":\"temperature\""));
  EXPECT_THAT(std::string(payload.c_str()), ::testing::HasSubstr("\"unit\":\"°C\""));
  EXPECT_THAT(std::string(payload.c_str()), ::testing::HasSubstr("\"point_id\":\"pt100_temperature\""));
}
