#pragma once
// Atrapa magistrali SPI dla `env:native` — zapisuje tylko fakt inicjalizacji.
#include <Arduino.h>

class NativeSpi {
 public:
  void begin(int sck = -1, int miso = -1, int mosi = -1, int cs = -1) {
    began = true;
    sck_pin = sck;
    miso_pin = miso;
    mosi_pin = mosi;
    cs_pin = cs;
  }
  void end() { began = false; }

  bool began = false;
  int sck_pin = -1;
  int miso_pin = -1;
  int mosi_pin = -1;
  int cs_pin = -1;
};

inline NativeSpi SPI;
