#pragma once

#include <Arduino.h>

// Compile-time log level filtering
#if !defined(LOG_LEVEL)
#define LOG_LEVEL LOG_INFO
#endif

enum LogLevel {
  LOG_DEBUG = 0,
  LOG_INFO = 1,
  LOG_WARN = 2,
  LOG_ERROR = 3,
};

// Format: [millis][LEVEL][TAG] message
#define LOG_DEBUG(tag, fmt, ...)                                               \
  if (LOG_DEBUG >= LOG_LEVEL) {                                                \
    Serial.printf("[%lu][DEBUG][%s] " fmt "\n", millis(), tag, ##__VA_ARGS__); \
  }

#define LOG_INFO(tag, fmt, ...)                                               \
  if (LOG_INFO >= LOG_LEVEL) {                                                \
    Serial.printf("[%lu][INFO][%s] " fmt "\n", millis(), tag, ##__VA_ARGS__); \
  }

#define LOG_WARN(tag, fmt, ...)                                               \
  if (LOG_WARN >= LOG_LEVEL) {                                                \
    Serial.printf("[%lu][WARN][%s] " fmt "\n", millis(), tag, ##__VA_ARGS__); \
  }

#define LOG_ERROR(tag, fmt, ...)                                               \
  if (LOG_ERROR >= LOG_LEVEL) {                                                \
    Serial.printf("[%lu][ERROR][%s] " fmt "\n", millis(), tag, ##__VA_ARGS__); \
  }
