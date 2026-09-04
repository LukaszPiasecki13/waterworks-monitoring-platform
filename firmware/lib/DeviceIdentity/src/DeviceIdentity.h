#pragma once

#include <Arduino.h>
#include <IDeviceIdentity.h>
#include <cstdint>

class DeviceIdentity : public IDeviceIdentity {
 public:
  void begin();
  void ensureKey();

  String serialNumber() const override;
  String publicKeyRawPointHex() const override;

  String signChallengeBase64(const String& challengeBase64Url) override;

  String signBase64(const uint8_t* msg, size_t len);

  static bool decodeBase64Url(const char* base64url_str, size_t b64url_len, uint8_t* out, size_t out_len,
                              size_t& decoded_len);

  bool isProvisioningCompleted() const override;
  void markProvisioningCompleted() override;
  void clearProvisioningState() override;

  bool hasValidSession(uint32_t nowUnixSec) const override;
  String sessionToken() const override;
  void setSessionToken(const String& token, uint32_t expiresAtUnixSec) override;

  bool needsReprovisioning() const { return needs_reprovisioning_; }

 private:
  static const size_t PRIV_KEY_SIZE = 32;

  String serial_number_;
  uint8_t priv_key_raw_[PRIV_KEY_SIZE];
  bool has_key_ = false;
  bool needs_reprovisioning_ = false;

  void loadOrGenerateKey();
  void generateSerialNumber();
};
