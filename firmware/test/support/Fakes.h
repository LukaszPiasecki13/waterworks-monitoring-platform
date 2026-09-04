#pragma once
//
// Atrapy interfejsów z `lib/Interfaces` używane przez testy `env:native`.
// Wszystkie są sterowalne i zapisują wywołania, żeby test mógł sprawdzić nie
// tylko wynik, ale i to, czy moduł w ogóle sięgnął po zależność.
//
#include <Arduino.h>
#include <IClock.h>
#include <IDeviceIdentity.h>
#include <IHttpClient.h>
#include <IModemLink.h>
#include <IModemPower.h>
#include <IStatusLed.h>
#include <ISystemControl.h>
#include <ITelemetryHealth.h>

#include <map>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------

class FakeClock : public IClock {
 public:
  bool isSynced() const override { return synced; }
  uint64_t utcMs() const override { return utc_ms; }

  void setUtcSeconds(uint32_t seconds) { utc_ms = static_cast<uint64_t>(seconds) * 1000ULL; }

  bool synced = true;
  uint64_t utc_ms = 1786419922123ULL;  // 2026-08-10T13:45:22.123Z
};

// ---------------------------------------------------------------------------

struct RecordedRequest {
  std::string resource;
  std::string payload;
  std::string bearerToken;
};

// Kolejka zaplanowanych odpowiedzi: kolejne wywołania post() zdejmują kolejne
// pozycje. Po wyczerpaniu kolejki zwracana jest `defaultResponse`.
class FakeHttpClient : public IHttpClient {
 public:
  HttpResponse post(const char* resource, const String& payload, const String& bearerToken) override {
    requests.push_back({resource ? resource : "", payload.std_str(), bearerToken.std_str()});

    if (!queued.empty()) {
      HttpResponse next = queued.front();
      queued.erase(queued.begin());
      return next;
    }
    return defaultResponse;
  }

  void queueResponse(int statusCode, const std::string& body = "") {
    queued.push_back(HttpResponse{statusCode, 10, String(body)});
  }

  void queueFor(const std::string& /*resourceHint*/, int statusCode, const std::string& body = "") {
    queueResponse(statusCode, body);
  }

  size_t callCount() const { return requests.size(); }
  const RecordedRequest& lastRequest() const { return requests.back(); }

  // Ile razy trafiono pod dany zasób.
  size_t countFor(const std::string& resource) const {
    size_t count = 0;
    for (const RecordedRequest& r : requests) {
      if (r.resource == resource) ++count;
    }
    return count;
  }

  std::vector<RecordedRequest> requests;
  std::vector<HttpResponse> queued;
  HttpResponse defaultResponse{500, 10, String("")};
};

// ---------------------------------------------------------------------------

class FakeModemLink : public IModemLink {
 public:
  bool ensureConnected() override {
    ++ensure_connected_calls;
    return connected;
  }
  bool testAT() override {
    ++test_at_calls;
    return at_ok;
  }

  bool connected = true;
  bool at_ok = true;
  int ensure_connected_calls = 0;
  int test_at_calls = 0;
};

// ---------------------------------------------------------------------------

class FakeModemPower : public IModemPower {
 public:
  void powerOn() override { ++power_on_calls; }
  void hardReset() override { ++hard_reset_calls; }

  int power_on_calls = 0;
  int hard_reset_calls = 0;
};

// ---------------------------------------------------------------------------

class FakeStatusLed : public IStatusLed {
 public:
  void blinkSuccess() override { ++success_blinks; }
  void blinkError() override { ++error_blinks; }

  int success_blinks = 0;
  int error_blinks = 0;
};

// ---------------------------------------------------------------------------

class FakeSystemControl : public ISystemControl {
 public:
  void delayMs(unsigned long ms) override { total_delay_ms += ms; }
  void restart() override { ++restart_calls; }

  uint32_t restartCount() const override { return restart_count; }
  void setRestartCount(uint32_t value) override { restart_count = value; }

  unsigned long total_delay_ms = 0;
  int restart_calls = 0;
  uint32_t restart_count = 0;
};

// ---------------------------------------------------------------------------

class FakeTelemetryHealth : public ITelemetryHealth {
 public:
  bool lastErrorWasPermanent() const override { return permanent; }
  bool permanent = false;
};

// ---------------------------------------------------------------------------

// Atrapa tożsamości: stan sesji trzymany w pamięci, bez NVS i mbedTLS.
// Reguła ważności sesji celowo powtarza tę z DeviceIdentity (margines odświeżania),
// bo testowanym zachowaniem jest reakcja konsumentów na "sesja wygasa", a nie
// implementacja NVS.
class FakeDeviceIdentity : public IDeviceIdentity {
 public:
  String serialNumber() const override { return serial_number; }
  String publicKeyRawPointHex() const override { return public_key_hex; }

  String signChallengeBase64(const String& challengeBase64Url) override {
    last_signed_challenge = challengeBase64Url.std_str();
    ++sign_calls;
    return String(signature_to_return);
  }

  bool isProvisioningCompleted() const override { return provisioning_completed; }
  void markProvisioningCompleted() override {
    provisioning_completed = true;
    ++mark_completed_calls;
  }
  void clearProvisioningState() override {
    provisioning_completed = false;
    token.clear();
    token_expires_at = 0;
    ++clear_state_calls;
  }

  bool hasValidSession(uint32_t nowUnixSec) const override {
    if (token_expires_at == 0 || token_expires_at < refresh_margin_seconds) return false;
    return nowUnixSec < (token_expires_at - refresh_margin_seconds);
  }

  String sessionToken() const override { return String(token); }

  void setSessionToken(const String& newToken, uint32_t expiresAtUnixSec) override {
    token = newToken.std_str();
    token_expires_at = expiresAtUnixSec;
    ++set_token_calls;
  }

  String serial_number = "WW-AABBCCDDEEFF";
  String public_key_hex = "04aabbcc";
  std::string signature_to_return = "c2lnbmF0dXJl";
  std::string last_signed_challenge;
  std::string token;
  uint32_t token_expires_at = 0;
  uint32_t refresh_margin_seconds = 4 * 3600;
  bool provisioning_completed = true;

  int sign_calls = 0;
  int set_token_calls = 0;
  int clear_state_calls = 0;
  int mark_completed_calls = 0;
};
