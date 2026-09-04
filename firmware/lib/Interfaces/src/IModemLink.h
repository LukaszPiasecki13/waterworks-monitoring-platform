#pragma once

// Szew nad łączem modemu widziany przez moduły, które tylko potrzebują wiedzieć,
// czy transmisja jest możliwa. Świadomie nie wystawia `TinyGsm&` — ten dostęp
// mają wyłącznie TelemetryHttpClient i TimeSync, przez konkretny ModemLink.
class IModemLink {
 public:
  virtual ~IModemLink() = default;

  // Doprowadza łącze do stanu zdatnego do wysyłki (rejestracja w sieci + APN).
  virtual bool ensureConnected() = 0;

  // Sprawdza, czy modem odpowiada na AT.
  virtual bool testAT() = 0;
};
