#pragma once
//
// Atrapa sterownika MAX31865 dla `env:native`.
//
// `PT100Sensor` trzyma sterownik przez wartość, więc — jak w przypadku TinyGSM —
// szew jest na poziomie nagłówka, a stan ustawia test przez `NativeMax31865State`.
// Przeliczenie RTD -> °C jest tu implementacją równania Callendara-Van Dusena
// (tą samą, którą liczy prawdziwa biblioteka), żeby asercje na temperaturze
// miały sens; sprawdzana jest logika `PT100Sensor`, nie sam sterownik.
//
#include <Arduino.h>
#include <SPI.h>
#include <cmath>

#define MAX31865_2WIRE 0
#define MAX31865_3WIRE 1
#define MAX31865_4WIRE 2

#define MAX31865_FAULT_HIGHTHRESH 0x80
#define MAX31865_FAULT_LOWTHRESH 0x40
#define MAX31865_FAULT_REFINLOW 0x20
#define MAX31865_FAULT_REFINHIGH 0x10
#define MAX31865_FAULT_RTDINLOW 0x08
#define MAX31865_FAULT_OVUV 0x04

struct NativeMax31865State {
  bool begin_ok = true;
  uint16_t rtd_raw = 7620;  // 100 Ω przy Rref = 430 Ω, czyli ~0 °C
  uint8_t fault = 0;

  int begin_calls = 0;
  int read_rtd_calls = 0;
  int read_fault_calls = 0;
  int clear_fault_calls = 0;

  static NativeMax31865State& instance() {
    static NativeMax31865State state;
    return state;
  }
  static void reset() { instance() = NativeMax31865State(); }
};

class Adafruit_MAX31865 {
 public:
  explicit Adafruit_MAX31865(uint8_t csPin) : cs_pin_(csPin) {}

  bool begin(uint8_t = MAX31865_2WIRE) {
    NativeMax31865State& s = NativeMax31865State::instance();
    ++s.begin_calls;
    return s.begin_ok;
  }

  uint16_t readRTD() {
    NativeMax31865State& s = NativeMax31865State::instance();
    ++s.read_rtd_calls;
    return s.rtd_raw;
  }

  uint8_t readFault() {
    NativeMax31865State& s = NativeMax31865State::instance();
    ++s.read_fault_calls;
    return s.fault;
  }

  void clearFault() {
    NativeMax31865State& s = NativeMax31865State::instance();
    ++s.clear_fault_calls;
    s.fault = 0;
  }

  float calculateTemperature(uint16_t rtdRaw, float rtdNominal, float refResistor) {
    const float a = 3.9083e-3f;
    const float b = -5.775e-7f;
    const float c = -4.183e-12f;

    float ratio = static_cast<float>(rtdRaw) / 32768.0f;
    float resistance = ratio * refResistor;

    float temp = (resistance - rtdNominal) / (a * rtdNominal);

    float poly = b * b;
    poly -= 4.0f * c * (resistance - rtdNominal);
    poly = std::sqrt(poly);
    poly += b;
    poly /= 2.0f;
    poly *= -1.0f;

    temp -= poly / (a * rtdNominal);
    return temp;
  }

 private:
  uint8_t cs_pin_;
};
