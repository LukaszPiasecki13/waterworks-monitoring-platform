#include <Arduino.h>
#include <ArduinoJson.h>
#include <cstring>
#include <time.h>
#include "DeviceAuthClient.h"
#include <DeviceIdentity.h>
#include <TelemetryHttpClient.h>
#include <TimeSync.h>
#include <Config.h>

DeviceAuthClient::DeviceAuthClient(DeviceIdentity& identity, TelemetryHttpClient& http, unsigned long pollIntervalMs)
    : identity_(identity), http_(http), poll_interval_ms_(pollIntervalMs) {}

uint32_t DeviceAuthClient::parseIso8601ToUnix(const String& iso8601) {
  // Parse "2026-08-22T14:30:45.123Z" -> unix timestamp (seconds since 1970-01-01 00:00:00 UTC)
  // Format: YYYY-MM-DDTHH:MM:SS.sssZ
  int year, month, day, hour, minute, second, ms;
  int parsed = sscanf(iso8601.c_str(), "%d-%d-%dT%d:%d:%d.%d", &year, &month, &day, &hour, &minute, &second, &ms);

  if (parsed < 6) {
    return 0;
  }

  // Days per month (non-leap year)
  static const int daysPerMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

  // Count days from 1970-01-01 to target date
  uint32_t totalDays = 0;

  // Add days for full years from 1970 to year-1
  for (int y = 1970; y < year; y++) {
    totalDays += (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)) ? 366 : 365;
  }

  // Add days for full months in target year
  for (int m = 1; m < month; m++) {
    totalDays += daysPerMonth[m - 1];
    if (m == 2 && (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0))) {
      totalDays++;  // Feb has 29 days in leap year
    }
  }

  // Add days in current month
  totalDays += day - 1;  // -1 because we count from day 1

  // Convert to seconds and add time-of-day
  uint32_t totalSeconds = totalDays * 86400UL + (uint32_t)hour * 3600UL + (uint32_t)minute * 60UL + (uint32_t)second;

  return totalSeconds;
}

bool DeviceAuthClient::attemptAuth() {
  String sn = identity_.serialNumber();

  // Step 1: POST /devices/auth/challenge
  JsonDocument challengeReq;
  challengeReq["serial_number"] = sn;
  String challengePayload;
  serializeJson(challengeReq, challengePayload);

  HttpResponse challengeResp = http_.post(CHALLENGE_RESOURCE, challengePayload, "");

  if (challengeResp.statusCode == 404) {
    // If provisioning was completed, this means device was deleted from platform
    if (identity_.isProvisioningCompleted()) {
      identity_.clearProvisioningState();
    }
    return false;
  }
  if (challengeResp.statusCode == 401) {
    return false;
  }
  if (challengeResp.statusCode != 200) {
    return false;
  }

  JsonDocument challengeDoc;
  DeserializationError err = deserializeJson(challengeDoc, challengeResp.body);
  if (err) {
    return false;
  }

  String challenge = challengeDoc["challenge"];
  if (challenge.isEmpty()) {
    return false;
  }

  // Step 2: Decode base64url challenge to nonce bytes, then sign nonce
  uint8_t challengeBytes[64];
  size_t challengeBytesLen = 0;
  if (!DeviceIdentity::decodeBase64Url(challenge.c_str(), challenge.length(), challengeBytes, sizeof(challengeBytes),
                                       challengeBytesLen)) {
    return false;
  }

  String signature = identity_.signBase64(challengeBytes, challengeBytesLen);
  if (signature.isEmpty()) {
    return false;
  }

  // Step 3: POST /devices/auth/verify
  JsonDocument verifyReq;
  verifyReq["serial_number"] = sn;
  verifyReq["signature"] = signature;
  String verifyPayload;
  serializeJson(verifyReq, verifyPayload);

  HttpResponse verifyResp = http_.post(VERIFY_RESOURCE, verifyPayload, "");

  if (verifyResp.statusCode == 410 || verifyResp.statusCode == 401) {
    return false;
  }

  if (verifyResp.statusCode != 200) {
    return false;
  }

  JsonDocument verifyDoc;
  err = deserializeJson(verifyDoc, verifyResp.body);
  if (err) {
    return false;
  }

  String token = verifyDoc["token"];
  String expiresAtStr = verifyDoc["expires_at"];

  if (token.isEmpty() || expiresAtStr.isEmpty()) {
    return false;
  }

  uint32_t expiresAtUnix = parseIso8601ToUnix(expiresAtStr);
  if (expiresAtUnix == 0) {
    return false;
  }

  identity_.setSessionToken(token, expiresAtUnix);

  return true;
}

void DeviceAuthClient::update(unsigned long nowMs) {
  // Guard: NTP must be synced for unix-time comparisons
  if (!TimeSync::isSynced()) {
    return;
  }

  // Throttle polling
  if (nowMs < next_allowed_poll_ms_) {
    return;
  }

  uint32_t nowUnix = (uint32_t)(TimeSync::getUtcTimestamp() / 1000);

  // Check if session is still valid (with refresh margin)
  if (identity_.hasValidSession(nowUnix)) {
    next_allowed_poll_ms_ = nowMs + poll_interval_ms_;
    return;
  }

  attemptAuth();
  next_allowed_poll_ms_ = nowMs + poll_interval_ms_;
}
