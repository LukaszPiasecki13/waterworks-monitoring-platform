#pragma once

#include <Arduino.h>
#include <cstdint>

// Szew nad tożsamością urządzenia. Implementacja produkcyjna (DeviceIdentity)
// opiera się o NVS (Preferences) i mbedTLS — obu nie da się skompilować na
// hoście, dlatego konsumenci (TelemetrySender, DeviceAuthClient,
// EnrollmentClient) zależą wyłącznie od tego interfejsu.
class IDeviceIdentity {
 public:
  virtual ~IDeviceIdentity() = default;

  virtual String serialNumber() const = 0;
  virtual String publicKeyRawPointHex() const = 0;

  // Dekoduje challenge (base64url), podpisuje nonce kluczem urządzenia
  // i zwraca podpis w base64. Pusty łańcuch = niepowodzenie.
  // Całość kryptografii jest po stronie implementacji: DeviceAuthClient
  // odpowiada za przebieg wymiany, nie za kodowanie nonce'a.
  virtual String signChallengeBase64(const String& challengeBase64Url) = 0;

  virtual bool isProvisioningCompleted() const = 0;
  virtual void markProvisioningCompleted() = 0;
  virtual void clearProvisioningState() = 0;

  virtual bool hasValidSession(uint32_t nowUnixSec) const = 0;
  virtual String sessionToken() const = 0;
  virtual void setSessionToken(const String& token, uint32_t expiresAtUnixSec) = 0;
};
