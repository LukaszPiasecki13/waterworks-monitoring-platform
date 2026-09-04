// PT100Sensor: przejście z odczytu MAX31865 na SensorReading.
// Poprzednia wersja tego pliku nie kompilowała się (odwoływała się do
// nieistniejącej stałej POINT_TYPE_TEMPERATURE) i sprawdzała `EXPECT_TRUE(true)`.
// Tu sterownik zastępuje atrapa z test/support/Adafruit_MAX31865.h.
#include <gtest/gtest.h>

#include <Arduino.h>
#include <Config.h>
#include <PT100Sensor.h>
#include <SensorRegistry.h>

#include <string>

namespace {

class PT100SensorTest : public ::testing::Test {
 protected:
  void SetUp() override {
    NativeMax31865State::reset();
    Serial.clearCaptured();
    sensor = new PT100Sensor(PT100_SPI_CS);
  }

  void TearDown() override { delete sensor; }

  NativeMax31865State& driver() { return NativeMax31865State::instance(); }

  PT100Sensor* sensor = nullptr;
};

// --- metadane punktu pomiarowego -------------------------------------------

TEST_F(PT100SensorTest, MetadanePunktuZgadzajaSieZRejestrem) {
  EXPECT_STREQ(sensor->pointId(), "pt100_temperature");
  EXPECT_STREQ(sensor->pointType(), "temperature");
  EXPECT_STREQ(sensor->unit(), "\xC2\xB0" "C");
  EXPECT_STREQ(sensor->getTag(), "[PT100]");

  // Typ punktu musi istnieć w rejestrze — inaczej backend odrzuci pomiar.
  EXPECT_TRUE(SensorRegistry::isValidPointType(sensor->pointType()));
}

TEST_F(PT100SensorTest, DzialaPrzezInterfejsISensor) {
  ISensor* iface = sensor;
  EXPECT_STREQ(iface->pointId(), "pt100_temperature");
  EXPECT_STREQ(iface->pointType(), "temperature");
}

// --- inicjalizacja ---------------------------------------------------------

TEST_F(PT100SensorTest, InitOtwieraSpiNaPinachZKonfiguracji) {
  ASSERT_TRUE(sensor->init());

  EXPECT_TRUE(SPI.began);
  EXPECT_EQ(SPI.sck_pin, PT100_SPI_SCK);
  EXPECT_EQ(SPI.miso_pin, PT100_SPI_MISO);
  EXPECT_EQ(SPI.mosi_pin, PT100_SPI_MOSI);
  EXPECT_EQ(SPI.cs_pin, PT100_SPI_CS);
  EXPECT_EQ(driver().begin_calls, 1);
}

TEST_F(PT100SensorTest, NieudanyInitJestZglaszanyIZalogowany) {
  driver().begin_ok = false;

  EXPECT_FALSE(sensor->init());
  EXPECT_NE(Serial.captured().find("[ERROR]"), std::string::npos);
}

// --- odczyt ----------------------------------------------------------------

TEST_F(PT100SensorTest, PoprawnyOdczytZwracaTemperatureBezKoduBledu) {
  driver().rtd_raw = 7620;  // 100 Ω, czyli ~0 °C
  driver().fault = 0;

  SensorReading reading = sensor->read();

  EXPECT_TRUE(reading.ok);
  EXPECT_EQ(reading.errorCode, nullptr);
  EXPECT_NEAR(reading.value, 0.0f, 1.0f);
}

TEST_F(PT100SensorTest, OdczytWZakresieRoboczymJestSensowny) {
  // ~110 Ω to około 25 °C: raw = 110/430 * 32768.
  driver().rtd_raw = static_cast<uint16_t>(110.0 / 430.0 * 32768.0);

  SensorReading reading = sensor->read();

  ASSERT_TRUE(reading.ok);
  EXPECT_GT(reading.value, 20.0f);
  EXPECT_LT(reading.value, 30.0f);
}

TEST_F(PT100SensorTest, TemperaturaRosnieWrazZRezystancja) {
  driver().rtd_raw = 7620;
  float atZero = sensor->read().value;

  driver().rtd_raw = 10000;
  float higher = sensor->read().value;

  EXPECT_GT(higher, atZero);
}

// --- błędy sprzętowe -------------------------------------------------------

TEST_F(PT100SensorTest, FlagaBleduDajeSensorFaultHw) {
  driver().fault = MAX31865_FAULT_RTDINLOW;  // np. przerwany przewód RTD

  SensorReading reading = sensor->read();

  EXPECT_FALSE(reading.ok);
  ASSERT_NE(reading.errorCode, nullptr);
  EXPECT_STREQ(reading.errorCode, "SENSOR_FAULT_HW");
  EXPECT_FLOAT_EQ(reading.value, 0.0f) << "przy błędzie nie wolno podawać wartości pomiaru";
}

TEST_F(PT100SensorTest, KodBleduIstniejeWRejestrze) {
  driver().fault = MAX31865_FAULT_OVUV;

  SensorReading reading = sensor->read();

  ASSERT_NE(reading.errorCode, nullptr);
  EXPECT_TRUE(SensorRegistry::isValidErrorCode(reading.errorCode));
  EXPECT_STREQ(SensorRegistry::severityForErrorCode(reading.errorCode), "critical");
}

TEST_F(PT100SensorTest, BladJestKasowanyPoZgloszeniu) {
  // Bez clearFault() rejestr błędu MAX31865 zostaje ustawiony na zawsze
  // i czujnik nigdy nie wróciłby do normalnej pracy.
  driver().fault = MAX31865_FAULT_HIGHTHRESH;

  ASSERT_FALSE(sensor->read().ok);
  EXPECT_EQ(driver().clear_fault_calls, 1);

  SensorReading afterClear = sensor->read();
  EXPECT_TRUE(afterClear.ok) << "po skasowaniu flagi czujnik musi znowu czytać";
}

TEST_F(PT100SensorTest, KazdaFlagaBleduJestRozpoznawana) {
  const uint8_t faults[] = {MAX31865_FAULT_HIGHTHRESH, MAX31865_FAULT_LOWTHRESH, MAX31865_FAULT_REFINLOW,
                            MAX31865_FAULT_REFINHIGH,  MAX31865_FAULT_RTDINLOW,  MAX31865_FAULT_OVUV};
  for (uint8_t fault : faults) {
    NativeMax31865State::reset();
    driver().fault = fault;

    SensorReading reading = sensor->read();

    EXPECT_FALSE(reading.ok) << "flaga 0x" << std::hex << static_cast<int>(fault);
    EXPECT_STREQ(reading.errorCode, "SENSOR_FAULT_HW");
  }
}

}  // namespace
