#pragma once

// =========================
// Serial & UART
// =========================

#define SERIAL_BAUD 115200
#define MODEM_BAUD 115200

// =========================
// ESP32-S3 pins <-> A7670E
// see HARDWARE.md for full pin map
// =========================

const int LED_PIN = 48;
const int MODEM_RX_PIN = 18;
const int MODEM_TX_PIN = 17;
const int MODEM_PWRKEY_PIN = 4;
const int MODEM_RESET_PIN = 5;
const int MODEM_POWER_ENABLE_PIN = -1;

// =========================
// SPI & PT100 Sensor
// =========================

const int PT100_SPI_CS = 14;
const int PT100_SPI_MOSI = 11;
const int PT100_SPI_MISO = 13;
const int PT100_SPI_SCK = 12;

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

// =========================
// Device identity & provisioning
// =========================

// Reported in the `device` state section and mirrored onto Device.firmware_version
// by the backend. Bump on every release that changes what the device reports.
const char FIRMWARE_VERSION[] = "0.4.0";

const char SN_PREFIX[] = "WW-";
const char CHALLENGE_RESOURCE[] = "/devices/auth/challenge";
const char VERIFY_RESOURCE[] = "/devices/auth/verify";
const char ACTIVATION_RESOURCE[] = "/devices/activation/redeem";

// =========================
// Timings
// =========================

const unsigned long SAMPLE_INTERVAL_MS = 15000;
const unsigned long ERROR_RETRY_MS = 5000;
const unsigned long WATCHDOG_STUCK_MS = 5 * 60 * 1000;  // 5 minutes
const uint8_t MAX_RESTART_ATTEMPTS = 2;
const unsigned long CLAIM_POLL_INTERVAL_MS = 15000;        // Test interval; to be tuned after Phase B
const uint32_t TOKEN_REFRESH_MARGIN_SECONDS = 4 * 3600;    // 4h przed wygaśnięciem 36h tokenu
const unsigned long ACTIVATION_RETRY_INTERVAL_MS = 30000;  // backoff bazowy dla EnrollmentClient (błędy przejściowe)

// Jak często stan urządzenia dołącza do pakietu telemetrycznego (B-08).
// 15 min zgodnie z 01_plan_biznesowy.md §3.8.1; koszt jest niezależny od
// interwału transmisji, bo licznik chodzi po zegarze, nie po pakietach.
const unsigned long DEVICE_STATE_REPORT_INTERVAL_MS = 15UL * 60UL * 1000UL;
