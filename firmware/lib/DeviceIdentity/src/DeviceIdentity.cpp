#include "DeviceIdentity.h"
#include <Config.h>
#include <Preferences.h>
#include <mbedtls/ecp.h>
#include <mbedtls/ecdsa.h>
#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/base64.h>
#include <mbedtls/sha256.h>
#include <esp_mac.h>
#include <esp_task_wdt.h>

static Preferences prefs;

void DeviceIdentity::begin() {
#ifdef OVERRIDE_SERIAL_NUMBER
  serial_number_ = OVERRIDE_SERIAL_NUMBER;
  Serial.print("[DEVID] Using override serial number: ");
  Serial.println(serial_number_);
#else
  prefs.begin("devid", true);
  serial_number_ = prefs.getString("sn", "");
  bool has_priv = prefs.isKey("priv");
  if (has_priv) {
    size_t len = prefs.getBytesLength("priv");
    if (len == PRIV_KEY_SIZE) {
      prefs.getBytes("priv", priv_key_raw_, PRIV_KEY_SIZE);
      has_key_ = true;
    }
  }
  prefs.end();

  if (serial_number_.isEmpty()) {
    generateSerialNumber();
  } else {
    Serial.print("[DEVID] Loaded serial number from NVS: ");
    Serial.println(serial_number_);
  }

  if (has_key_) {
    Serial.println("[DEVID] Loaded EC key from NVS");
  }
#endif
}

void DeviceIdentity::ensureKey() {
  if (has_key_) {
    return;
  }
  loadOrGenerateKey();
}

String DeviceIdentity::serialNumber() const { return serial_number_; }

String DeviceIdentity::publicKeyRawPointHex() const {
  if (!has_key_) {
    return "";
  }

  mbedtls_ecp_keypair key;
  mbedtls_ecp_keypair_init(&key);
  mbedtls_ecp_group_load(&key.grp, MBEDTLS_ECP_DP_SECP256R1);

  mbedtls_mpi_read_binary(&key.d, priv_key_raw_, PRIV_KEY_SIZE);
  mbedtls_ecp_mul(&key.grp, &key.Q, &key.d, &key.grp.G, nullptr, nullptr);

  uint8_t point_buf[65];
  size_t olen = 0;
  mbedtls_ecp_point_write_binary(&key.grp, &key.Q, MBEDTLS_ECP_PF_UNCOMPRESSED, &olen, point_buf, 65);

  String result;
  result.reserve(130);
  for (size_t i = 0; i < olen; i++) {
    char hex[3];
    snprintf(hex, sizeof(hex), "%02x", point_buf[i]);
    result += hex;
  }

  mbedtls_ecp_keypair_free(&key);

  return result;
}

String DeviceIdentity::signBase64(const uint8_t* msg, size_t len) {
  if (!has_key_) {
    return "";
  }

  mbedtls_entropy_context entropy;
  mbedtls_ctr_drbg_context ctr_drbg;
  mbedtls_entropy_init(&entropy);
  mbedtls_ctr_drbg_init(&ctr_drbg);
  mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy, nullptr, 0);

  mbedtls_ecp_keypair key;
  mbedtls_ecp_keypair_init(&key);
  mbedtls_ecp_group_load(&key.grp, MBEDTLS_ECP_DP_SECP256R1);

  mbedtls_mpi_read_binary(&key.d, priv_key_raw_, PRIV_KEY_SIZE);
  mbedtls_ecp_mul(&key.grp, &key.Q, &key.d, &key.grp.G, nullptr, nullptr);

  uint8_t hash[32];
  mbedtls_sha256(msg, len, hash, 0);

  uint8_t der_sig[72];
  size_t sig_len = 0;
  int sign_ret = mbedtls_ecdsa_write_signature(&key, MBEDTLS_MD_SHA256, hash, 32, der_sig, &sig_len,
                                               mbedtls_ctr_drbg_random, &ctr_drbg);
  if (sign_ret != 0) {
    Serial.print("[DEVID] ecdsa_write_signature failed: ");
    Serial.println(sign_ret);
    mbedtls_ecp_keypair_free(&key);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return "";
  }
  Serial.print("[DEVID] DER signature length: ");
  Serial.println(sig_len);

  uint8_t b64_buf[128];
  size_t b64_len = 0;
  int b64_ret = mbedtls_base64_encode(b64_buf, sizeof(b64_buf), &b64_len, der_sig, sig_len);
  if (b64_ret != 0) {
    Serial.print("[DEVID] base64_encode failed: ");
    Serial.println(b64_ret);
    mbedtls_ecp_keypair_free(&key);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return "";
  }

  String result;
  result.reserve(b64_len);
  for (size_t i = 0; i < b64_len; i++) {
    result += (char)b64_buf[i];
  }

  mbedtls_ecp_keypair_free(&key);
  mbedtls_ctr_drbg_free(&ctr_drbg);
  mbedtls_entropy_free(&entropy);

  return result;
}

bool DeviceIdentity::isProvisioningCompleted() const {
  prefs.begin("devid", true);
  bool claimed = prefs.getBool("claimed", false);
  prefs.end();
  return claimed;
}

void DeviceIdentity::markProvisioningCompleted() {
  prefs.begin("devid", false);
  prefs.putBool("claimed", true);
  prefs.end();
}

void DeviceIdentity::clearProvisioningState() {
  prefs.begin("devid", false);
  prefs.putBool("claimed", false);
  prefs.remove("tok");
  prefs.remove("tok_exp");
  prefs.end();
  needs_reprovisioning_ = true;
  Serial.println("[DEVID] Provisioning state cleared, device needs reprovisioning");
}

bool DeviceIdentity::hasValidSession(uint32_t nowUnixSec) const {
  prefs.begin("devid", true);
  uint32_t expires_at = prefs.getUInt("tok_exp", 0);
  prefs.end();

  extern const uint32_t TOKEN_REFRESH_MARGIN_SECONDS;
  if (expires_at == 0 || expires_at < TOKEN_REFRESH_MARGIN_SECONDS) {
    return false;
  }
  return nowUnixSec < (expires_at - TOKEN_REFRESH_MARGIN_SECONDS);
}

String DeviceIdentity::sessionToken() const {
  prefs.begin("devid", true);
  String token = prefs.getString("tok", "");
  prefs.end();
  return token;
}

void DeviceIdentity::setSessionToken(const String& token, uint32_t expiresAtUnixSec) {
  prefs.begin("devid", false);
  prefs.putString("tok", token);
  prefs.putUInt("tok_exp", expiresAtUnixSec);
  prefs.end();
}

void DeviceIdentity::loadOrGenerateKey() {
  if (has_key_) {
    return;
  }

  Serial.println("[DEVID] Generating new EC key (SECP256R1)...");

  mbedtls_entropy_context entropy;
  mbedtls_ctr_drbg_context ctr_drbg;
  mbedtls_entropy_init(&entropy);
  mbedtls_ctr_drbg_init(&ctr_drbg);
  esp_task_wdt_reset();
  mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy, nullptr, 0);

  mbedtls_ecp_keypair key;
  mbedtls_ecp_keypair_init(&key);
  esp_task_wdt_reset();
  yield();
  mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1, &key, mbedtls_ctr_drbg_random, &ctr_drbg);
  esp_task_wdt_reset();
  yield();

  mbedtls_mpi_write_binary(&key.d, priv_key_raw_, PRIV_KEY_SIZE);

  prefs.begin("devid", false);
  prefs.putBytes("priv", priv_key_raw_, PRIV_KEY_SIZE);
  prefs.end();

  has_key_ = true;

  mbedtls_ecp_keypair_free(&key);
  mbedtls_ctr_drbg_free(&ctr_drbg);
  mbedtls_entropy_free(&entropy);

  Serial.println("[DEVID] EC key generated and saved");
}

void DeviceIdentity::generateSerialNumber() {
  uint8_t mac[6];
  esp_read_mac(mac, ESP_MAC_WIFI_STA);

  String sn = SN_PREFIX;
  for (int i = 0; i < 6; i++) {
    char hex[3];
    snprintf(hex, sizeof(hex), "%02X", mac[i]);
    sn += hex;
  }

  serial_number_ = sn;

  prefs.begin("devid", false);
  prefs.putString("sn", serial_number_);
  prefs.end();

  Serial.print("[DEVID] Generated serial number: ");
  Serial.println(serial_number_);
}

bool DeviceIdentity::decodeBase64Url(const char* base64url_str, size_t b64url_len, uint8_t* out, size_t out_len,
                                     size_t& decoded_len) {
  char b64_buf[256];
  if (b64url_len > sizeof(b64_buf) - 4) {
    return false;
  }

  size_t b64_len = 0;
  for (size_t i = 0; i < b64url_len && base64url_str[i] != '\0'; i++) {
    char c = base64url_str[i];
    if (c == '-')
      c = '+';
    else if (c == '_')
      c = '/';
    b64_buf[b64_len++] = c;
  }

  while (b64_len % 4 != 0) {
    b64_buf[b64_len++] = '=';
  }

  int ret = mbedtls_base64_decode(out, out_len, &decoded_len, (const uint8_t*)b64_buf, b64_len);
  return ret == 0;
}
