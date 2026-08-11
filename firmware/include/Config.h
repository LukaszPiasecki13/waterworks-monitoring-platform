#pragma once

// =========================
// Serial & UART
// =========================

#define SERIAL_BAUD 115200
#define MODEM_BAUD 115200

// =========================
// ESP32-S3 pins <-> A7670E
// =========================

const int LED_PIN = -1;
const int MODEM_RX_PIN = 18;
const int MODEM_TX_PIN = 17;
const int MODEM_PWRKEY_PIN = 4;
const int MODEM_RESET_PIN = 5;
const int MODEM_POWER_ENABLE_PIN = -1;

// =========================
// SIM / Network
// =========================

const char APN[] = "internet";
const char GPRS_USER[] = "";
const char GPRS_PASS[] = "";
const char SIM_PIN[] = "";

// =========================
// Backend (Render, HTTPS)
// =========================

const char SERVER[] = "waterworks-monitoring-platform.onrender.com";
const int PORT = 443;
const char RESOURCE[] = "/telemetry/ingest";
const char DEVICE_KEY[] = "Test1";

// =========================
// Device identity
// =========================

const char DEVICE_ID[] = "esp32-a7670e-0001";

// =========================
// Timings
// =========================

const unsigned long SEND_INTERVAL_MS = 15000;
const unsigned long ERROR_RETRY_MS = 5000;
const unsigned long WATCHDOG_STUCK_MS = 5 * 60 * 1000;  // 5 minutes
const uint8_t MAX_RESTART_ATTEMPTS = 2;
