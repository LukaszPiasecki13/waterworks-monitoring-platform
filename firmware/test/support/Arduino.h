#pragma once
//
// Warstwa zgodności Arduino dla środowiska `env:native` (testy googletest na PC).
//
// Nie trafia do buildu ESP32 — jest widoczna wyłącznie przez `-I test/support`
// w `[env:native]`. Dzięki temu biblioteki z `lib/`, które opierają się o
// `String`, `millis()`, `delay()` czy `Serial`, kompilują się na hoście bez
// frameworka Arduino.
//
// Trzy elementy są sterowalne z testu:
//   * NativeClock  — `millis()` nie płynie samo; test ustawia/przesuwa czas,
//                    a `delay()` przesuwa zegar (pętle `while (millis() - t < X)`
//                    w kodzie produkcyjnym kończą się zamiast wisieć).
//   * NativeSerial — `Serial.printf()` zapisuje do bufora, nie na stdout;
//                    test może asertować na treści logu.
//   * NativeGpio   — `pinMode()/digitalWrite()` zapisują sekwencję zdarzeń,
//                    co pozwala testować sterowanie zasilaniem modemu.
//
#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ostream>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// Atrybuty i stałe, których kod firmware używa bezwarunkowo
// ---------------------------------------------------------------------------

#define PROGMEM
#define RTC_DATA_ATTR
#define F(string_literal) (string_literal)

#ifndef HIGH
#define HIGH 1
#endif
#ifndef LOW
#define LOW 0
#endif
#ifndef INPUT
#define INPUT 0x01
#endif
#ifndef OUTPUT
#define OUTPUT 0x03
#endif
#ifndef SERIAL_8N1
#define SERIAL_8N1 0x800001cUL
#endif

// ---------------------------------------------------------------------------
// Zegar sterowany z testu
// ---------------------------------------------------------------------------

class NativeClock {
 public:
  static unsigned long millis() { return value(); }
  static void set(unsigned long ms) { value() = ms; }
  static void advance(unsigned long ms) { value() += ms; }
  static void reset() { value() = 0; }

 private:
  static unsigned long& value() {
    static unsigned long ms = 0;
    return ms;
  }
};

inline unsigned long millis() { return NativeClock::millis(); }
inline void delay(unsigned long ms) { NativeClock::advance(ms); }
inline void delayMicroseconds(unsigned int us) { NativeClock::advance(us / 1000); }
inline void yield() {}

// ---------------------------------------------------------------------------
// Zapis zdarzeń GPIO
// ---------------------------------------------------------------------------

struct GpioEvent {
  enum Kind { PinMode, DigitalWrite };
  Kind kind;
  int pin;
  int value;  // tryb dla PinMode, poziom dla DigitalWrite
  unsigned long atMs;
};

class NativeGpio {
 public:
  static std::vector<GpioEvent>& events() {
    static std::vector<GpioEvent> log;
    return log;
  }
  static void reset() { events().clear(); }

  // Poziomy zapisane dla danego pinu, w kolejności wystąpienia.
  static std::vector<int> writesFor(int pin) {
    std::vector<int> out;
    for (const GpioEvent& e : events()) {
      if (e.kind == GpioEvent::DigitalWrite && e.pin == pin) {
        out.push_back(e.value);
      }
    }
    return out;
  }
};

inline void pinMode(int pin, int mode) {
  NativeGpio::events().push_back({GpioEvent::PinMode, pin, mode, millis()});
}

inline void digitalWrite(int pin, int value) {
  NativeGpio::events().push_back({GpioEvent::DigitalWrite, pin, value, millis()});
}

inline int digitalRead(int) { return LOW; }

// ---------------------------------------------------------------------------
// String — podzbiór API Arduino WString używany przez firmware
// ---------------------------------------------------------------------------

class String {
 public:
  String() = default;
  String(const char* value) : buffer_(value ? value : "") {}
  String(const std::string& value) : buffer_(value) {}
  explicit String(char value) : buffer_(1, value) {}
  explicit String(int value) : buffer_(std::to_string(value)) {}
  explicit String(unsigned long value) : buffer_(std::to_string(value)) {}

  const char* c_str() const { return buffer_.c_str(); }
  size_t length() const { return buffer_.size(); }
  bool isEmpty() const { return buffer_.empty(); }
  void reserve(size_t capacity) { buffer_.reserve(capacity); }
  void clear() { buffer_.clear(); }

  const std::string& std_str() const { return buffer_; }

  char operator[](size_t index) const { return index < buffer_.size() ? buffer_[index] : '\0'; }

  String& operator+=(const String& other) {
    buffer_ += other.buffer_;
    return *this;
  }
  String& operator+=(const char* other) {
    if (other) buffer_ += other;
    return *this;
  }
  String& operator+=(char other) {
    buffer_ += other;
    return *this;
  }

  bool operator==(const String& other) const { return buffer_ == other.buffer_; }
  bool operator==(const char* other) const { return other && buffer_ == other; }
  bool operator!=(const String& other) const { return !(*this == other); }
  bool operator!=(const char* other) const { return !(*this == other); }

  void trim() {
    const char* whitespace = " \t\r\n\v\f";
    size_t first = buffer_.find_first_not_of(whitespace);
    if (first == std::string::npos) {
      buffer_.clear();
      return;
    }
    size_t last = buffer_.find_last_not_of(whitespace);
    buffer_ = buffer_.substr(first, last - first + 1);
  }

  void toUpperCase() {
    for (char& c : buffer_) {
      if (c >= 'a' && c <= 'z') c = static_cast<char>(c - 'a' + 'A');
    }
  }

  String substring(size_t from) const {
    if (from >= buffer_.size()) return String();
    return String(buffer_.substr(from));
  }

  String substring(size_t from, size_t to) const {
    if (from >= buffer_.size() || to <= from) return String();
    if (to > buffer_.size()) to = buffer_.size();
    return String(buffer_.substr(from, to - from));
  }

  int indexOf(char needle) const {
    size_t pos = buffer_.find(needle);
    return pos == std::string::npos ? -1 : static_cast<int>(pos);
  }

  int indexOf(const char* needle) const {
    if (!needle) return -1;
    size_t pos = buffer_.find(needle);
    return pos == std::string::npos ? -1 : static_cast<int>(pos);
  }

  bool startsWith(const char* prefix) const {
    if (!prefix) return false;
    size_t len = std::strlen(prefix);
    return buffer_.size() >= len && buffer_.compare(0, len, prefix) == 0;
  }

 private:
  std::string buffer_;
};

inline String operator+(const String& lhs, const String& rhs) {
  String out(lhs);
  out += rhs;
  return out;
}
inline String operator+(const String& lhs, const char* rhs) {
  String out(lhs);
  out += rhs;
  return out;
}
inline String operator+(const char* lhs, const String& rhs) {
  String out(lhs);
  out += rhs;
  return out;
}
inline bool operator==(const char* lhs, const String& rhs) { return rhs == lhs; }

// Czytelny komunikat błędu w googletest zamiast zrzutu bajtów.
inline void PrintTo(const String& value, std::ostream* os) { *os << '"' << value.c_str() << '"'; }

// ---------------------------------------------------------------------------
// Serial — logi trafiają do bufora zamiast na stdout
// ---------------------------------------------------------------------------

class NativeSerial {
 public:
  void begin(unsigned long = 0) {}
  void end() {}
  void flush() {}

  int available() { return static_cast<int>(rx_.size() - rx_pos_); }

  int read() {
    if (rx_pos_ >= rx_.size()) return -1;
    return static_cast<unsigned char>(rx_[rx_pos_++]);
  }

  int printf(const char* format, ...) {
    char scratch[1024];
    va_list args;
    va_start(args, format);
    int written = vsnprintf(scratch, sizeof(scratch), format, args);
    va_end(args);
    if (written > 0) captured_ += scratch;
    if (echo_) fputs(scratch, stdout);
    return written;
  }

  void print(const char* text) {
    if (text) captured_ += text;
  }
  void println(const char* text) {
    print(text);
    captured_ += '\n';
  }
  void println() { captured_ += '\n'; }

  // Interfejs dla testów
  const std::string& captured() const { return captured_; }
  void clearCaptured() { captured_.clear(); }
  void setEcho(bool enabled) { echo_ = enabled; }

  // Wstawia dane tak, jakby przyszły z monitora szeregowego.
  void feed(const std::string& data) { rx_ += data; }
  void clearInput() {
    rx_.clear();
    rx_pos_ = 0;
  }

 private:
  std::string captured_;
  std::string rx_;
  size_t rx_pos_ = 0;
  bool echo_ = false;
};

inline NativeSerial Serial;

// ---------------------------------------------------------------------------
// Nagłówki ESP-IDF używane przez firmware, sprowadzone do no-op
// ---------------------------------------------------------------------------

inline int esp_task_wdt_reset() { return 0; }
