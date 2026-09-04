#pragma once
//
// Atrapa TinyGSM dla `env:native`.
//
// ModemLink tworzy `TinyGsm` sam (`new TinyGsm(serial)`), więc nie da się go
// wstrzyknąć konstruktorem. Zamiast tego podmieniamy nagłówek: w środowisku
// natywnym `ModemLink.cpp` kompiluje się przeciwko tej atrapie, a zachowanie
// modemu test ustawia przez `NativeModemState` przed wywołaniem.
//
// To jest szew na poziomie linkowania, a nie interfejsu — celowo, bo pozwala
// przetestować prawdziwą sekwencję z `ModemLink.cpp` bez zmieniania jej kodu.
//
#include <Arduino.h>
#include <HardwareSerial.h>

struct NativeIpAddress {
  String toString() const { return String("10.0.0.1"); }
};

// Zachowanie modemu sterowane z testu.
struct NativeModemState {
  // Odpowiedzi
  int init_failures_before_ok = 0;  // ile razy init() ma zwrócić false zanim się uda
  bool init_ever_succeeds = true;
  bool at_ok = true;
  bool wait_for_network_ok = true;
  bool network_connected = true;
  bool gprs_connect_ok = true;
  bool gprs_connected = true;
  int signal_quality = -75;

  // Liczniki wywołań
  int init_calls = 0;
  int test_at_calls = 0;
  int wait_for_network_calls = 0;
  int gprs_connect_calls = 0;
  int gprs_disconnect_calls = 0;
  int sim_unlock_calls = 0;

  static NativeModemState& instance() {
    static NativeModemState state;
    return state;
  }

  static void reset() { instance() = NativeModemState(); }
};

class TinyGsm {
 public:
  explicit TinyGsm(HardwareSerial& serial) : serial_(serial) {}

  bool init() {
    NativeModemState& s = NativeModemState::instance();
    ++s.init_calls;
    if (!s.init_ever_succeeds) return false;
    return s.init_calls > s.init_failures_before_ok;
  }

  bool testAT(unsigned long = 0) {
    NativeModemState& s = NativeModemState::instance();
    ++s.test_at_calls;
    return s.at_ok;
  }

  String getModemInfo() { return String("NATIVE-FAKE-A7670E"); }

  bool simUnlock(const char*) {
    ++NativeModemState::instance().sim_unlock_calls;
    return true;
  }

  bool waitForNetwork(long timeoutMs = 60000L, bool = false) {
    NativeModemState& s = NativeModemState::instance();
    ++s.wait_for_network_calls;
    if (!s.wait_for_network_ok) {
      // Prawdziwe TinyGSM blokuje na czas timeoutu — pętla w ModemLink polega
      // na tym, że millis() w tym czasie idzie do przodu.
      NativeClock::advance(static_cast<unsigned long>(timeoutMs));
    }
    return s.wait_for_network_ok;
  }

  bool isNetworkConnected() { return NativeModemState::instance().network_connected; }

  int getSignalQuality() { return NativeModemState::instance().signal_quality; }

  bool gprsConnect(const char*, const char* = "", const char* = "") {
    NativeModemState& s = NativeModemState::instance();
    ++s.gprs_connect_calls;
    return s.gprs_connect_ok;
  }

  bool gprsDisconnect() {
    ++NativeModemState::instance().gprs_disconnect_calls;
    return true;
  }

  bool isGprsConnected() { return NativeModemState::instance().gprs_connected; }

  NativeIpAddress localIP() { return NativeIpAddress(); }

 private:
  HardwareSerial& serial_;
};

// TinyGSM udostępnia to jako funkcję wolną; ModemLink::init() jej używa.
inline void TinyGsmAutoBaud(HardwareSerial&, uint32_t = 9600, uint32_t = 115200) {}
