#pragma once
// Atrapa UART dla `env:native` — ModemLink trzyma referencję do HardwareSerial,
// więc typ musi istnieć, ale w teście nie przenosi żadnych danych.
#include <Arduino.h>

class HardwareSerial {
 public:
  explicit HardwareSerial(int uartNumber = 0) : uart_number_(uartNumber) {}

  void begin(unsigned long baud, unsigned long config = SERIAL_8N1, int rxPin = -1, int txPin = -1) {
    begun = true;
    baud_rate = baud;
    config_ = config;
    rx_pin = rxPin;
    tx_pin = txPin;
    ++begin_calls;
  }
  void end() { begun = false; }

  int available() { return rx_queue_.empty() ? 0 : static_cast<int>(rx_queue_.size()); }
  int read() {
    if (rx_queue_.empty()) return -1;
    char c = rx_queue_.front();
    rx_queue_.erase(rx_queue_.begin(), rx_queue_.begin() + 1);
    return static_cast<unsigned char>(c);
  }
  size_t write(uint8_t) { return 1; }
  void flush() {}

  // Interfejs dla testów
  void feed(const std::string& data) { rx_queue_ += data; }

  bool begun = false;
  unsigned long baud_rate = 0;
  int rx_pin = -1;
  int tx_pin = -1;
  int begin_calls = 0;

 private:
  int uart_number_;
  unsigned long config_ = 0;
  std::string rx_queue_;
};
