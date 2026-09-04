// Priorytet 3 wg ryzyka: cykl challenge/verify i utrzymanie sesji.
// Bez ważnego tokenu urządzenie milczy — i robi to cicho, bez żadnego sygnału
// po stronie backendu.
#include <gtest/gtest.h>

#include <Config.h>
#include <DeviceAuthClient.h>
#include <Fakes.h>

#include <string>

namespace {

constexpr unsigned long kPollIntervalMs = 15000;
constexpr uint32_t kNowUnix = 1786419922;             // 2026-08-11T03:45:22Z
constexpr uint32_t kExpiresUnix = 1786419922 + 36 * 3600;
constexpr const char* kExpiresIso = "2026-08-12T15:45:22.000Z";

class DeviceAuthClientTest : public ::testing::Test {
 protected:
  void SetUp() override {
    clock_.synced = true;
    clock_.setUtcSeconds(kNowUnix);
    identity.provisioning_completed = true;
    client = new DeviceAuthClient(identity, http, clock_, kPollIntervalMs);
  }

  void TearDown() override { delete client; }

  // Standardowa udana para odpowiedzi challenge + verify.
  void queueSuccessfulHandshake(const std::string& expiresIso = kExpiresIso) {
    http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
    http.queueResponse(200, std::string("{\"token\":\"tok-123\",\"expires_at\":\"") + expiresIso + "\"}");
  }

  FakeClock clock_;
  FakeHttpClient http;
  FakeDeviceIdentity identity;
  DeviceAuthClient* client = nullptr;
};

// --- parsowanie ISO8601 ----------------------------------------------------

TEST(DeviceAuthClientIso8601, ParsujePoprawnyZnacznik) {
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-08-11T03:45:22.000Z")), 1786419922u);
}

TEST(DeviceAuthClientIso8601, ParsujeBezCzesciMilisekundowej) {
  // sscanf wymaga co najmniej 6 pól; ".sss" jest opcjonalne.
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-08-11T03:45:22Z")), 1786419922u);
}

TEST(DeviceAuthClientIso8601, ObslugujeRokPrzestepny) {
  // 2024-02-29 to data istniejąca; 2024-03-01 musi wypaść dzień później.
  uint32_t feb29 = DeviceAuthClient::parseIso8601ToUnix(String("2024-02-29T00:00:00.000Z"));
  uint32_t mar01 = DeviceAuthClient::parseIso8601ToUnix(String("2024-03-01T00:00:00.000Z"));
  EXPECT_EQ(feb29, 1709164800u);
  EXPECT_EQ(mar01 - feb29, 86400u);
}

TEST(DeviceAuthClientIso8601, ObslugujeRokNieprzestepnyPodzielnyPrzez100) {
  // 1900 nie było przestępne, 2000 było — reguła gregoriańska.
  uint32_t y2000feb28 = DeviceAuthClient::parseIso8601ToUnix(String("2000-02-28T00:00:00.000Z"));
  uint32_t y2000mar01 = DeviceAuthClient::parseIso8601ToUnix(String("2000-03-01T00:00:00.000Z"));
  EXPECT_EQ(y2000mar01 - y2000feb28, 2 * 86400u);
}

TEST(DeviceAuthClientIso8601, OdrzucaSmieciowyZnacznik) {
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("nie-data")), 0u);
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("")), 0u);
}

TEST(DeviceAuthClientIso8601, OdrzucaDzienPozaDlugosciaMiesiaca) {
  // Sam limit 31 dni przepuszczał "2026-02-30" i dawał znacznik przesunięty
  // o dwa dni — urządzenie uznawałoby wygasły token za ważny i dostawało 401
  // przy każdej wysyłce, aż do naturalnego dogonienia różnicy.
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-02-30T00:00:00.000Z")), 0u);
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-04-31T00:00:00.000Z")), 0u);
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-02-29T00:00:00.000Z")), 0u)
      << "2026 nie jest rokiem przestępnym";

  // Daty istniejące muszą przechodzić.
  EXPECT_NE(DeviceAuthClient::parseIso8601ToUnix(String("2026-02-28T00:00:00.000Z")), 0u);
  EXPECT_NE(DeviceAuthClient::parseIso8601ToUnix(String("2024-02-29T00:00:00.000Z")), 0u)
      << "2024 jest przestępny";
  EXPECT_NE(DeviceAuthClient::parseIso8601ToUnix(String("2026-01-31T00:00:00.000Z")), 0u);
}

TEST(DeviceAuthClientIso8601, OdrzucaDateSpozaKalendarza) {
  // Bez walidacji zakresów "13. miesiąc" dałby przypadkowy, ale niezerowy
  // znacznik — i token uznany za ważny przez lata.
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("2026-13-45T99:99:99.000Z")), 0u);
  EXPECT_EQ(DeviceAuthClient::parseIso8601ToUnix(String("1969-12-31T23:59:59.000Z")), 0u);
}

// --- warunki wstępne pętli -------------------------------------------------

TEST_F(DeviceAuthClientTest, BezSynchronizacjiCzasuNieProbujeSieUwierzytelnic) {
  clock_.synced = false;
  client->update(0);
  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(DeviceAuthClientTest, WaznaSesjaNieUruchamiaWymianyChallenge) {
  identity.token = "tok";
  identity.token_expires_at = kExpiresUnix;

  client->update(0);

  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(DeviceAuthClientTest, PollingJestDlawionyPollInterval) {
  queueSuccessfulHandshake();
  client->update(0);
  size_t afterFirst = http.callCount();

  client->update(kPollIntervalMs - 1);
  EXPECT_EQ(http.callCount(), afterFirst) << "próba przed upływem interwału";
}

// --- pełna wymiana ---------------------------------------------------------

TEST_F(DeviceAuthClientTest, UdanaWymianaZapisujeTokenIWaznosc) {
  queueSuccessfulHandshake();

  client->update(0);

  ASSERT_EQ(http.callCount(), 2u);
  EXPECT_EQ(http.requests[0].resource, std::string(CHALLENGE_RESOURCE));
  EXPECT_EQ(http.requests[1].resource, std::string(VERIFY_RESOURCE));
  EXPECT_EQ(identity.set_token_calls, 1);
  EXPECT_EQ(identity.token, "tok-123");
  EXPECT_EQ(identity.token_expires_at, kExpiresUnix);
}

TEST_F(DeviceAuthClientTest, PodpisPowstajeZChallengeZOdpowiedzi) {
  queueSuccessfulHandshake();

  client->update(0);

  EXPECT_EQ(identity.sign_calls, 1);
  EXPECT_EQ(identity.last_signed_challenge, "YWJjZGVmZ2g");
}

TEST_F(DeviceAuthClientTest, ZadaniaNiosaNumerSeryjnyUrzadzenia) {
  queueSuccessfulHandshake();

  client->update(0);

  ASSERT_EQ(http.callCount(), 2u);
  EXPECT_NE(http.requests[0].payload.find("WW-AABBCCDDEEFF"), std::string::npos);
  EXPECT_NE(http.requests[1].payload.find("WW-AABBCCDDEEFF"), std::string::npos);
  // Wymiana challenge/verify idzie bez tokenu — token dopiero z niej wynika.
  EXPECT_TRUE(http.requests[0].bearerToken.empty());
  EXPECT_TRUE(http.requests[1].bearerToken.empty());
}

// --- odświeżanie z marginesem ----------------------------------------------

TEST_F(DeviceAuthClientTest, TokenWMarginesieOdswiezaniaJestOdnawiany) {
  // Token formalnie jeszcze ważny, ale wygasa wewnątrz marginesu — musi zostać
  // wymieniony zanim padnie w środku transmisji.
  identity.token = "stary";
  identity.token_expires_at = kNowUnix + identity.refresh_margin_seconds - 60;
  queueSuccessfulHandshake();

  client->update(0);

  EXPECT_EQ(identity.set_token_calls, 1);
  EXPECT_EQ(identity.token, "tok-123");
}

TEST_F(DeviceAuthClientTest, TokenPozaMarginesemNieJestRuszany) {
  identity.token = "stary";
  identity.token_expires_at = kNowUnix + identity.refresh_margin_seconds + 60;

  client->update(0);

  EXPECT_EQ(http.callCount(), 0u);
  EXPECT_EQ(identity.token, "stary");
}

// --- odrzucenia ------------------------------------------------------------

TEST_F(DeviceAuthClientTest, Challenge404PoProvisioninguCzysciStan) {
  // Urządzenie skasowane z platformy: nie ma sensu dalej pukać tym samym SN.
  http.queueResponse(404, "");

  client->update(0);

  EXPECT_EQ(identity.clear_state_calls, 1);
  EXPECT_EQ(http.callCount(), 1u) << "po 404 nie powinno być kroku verify";
}

TEST_F(DeviceAuthClientTest, Challenge404PrzedProvisioningiemNieCzysciStanu) {
  identity.provisioning_completed = false;
  http.queueResponse(404, "");

  client->update(0);

  EXPECT_EQ(identity.clear_state_calls, 0);
}

TEST_F(DeviceAuthClientTest, OdrzuconyPodpisNieZapisujeTokenu) {
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
  http.queueResponse(401, "");  // backend nie uznał podpisu

  client->update(0);

  EXPECT_EQ(identity.set_token_calls, 0);
  EXPECT_TRUE(identity.token.empty());
}

TEST_F(DeviceAuthClientTest, Verify410NieZapisujeTokenu) {
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
  http.queueResponse(410, "");

  client->update(0);

  EXPECT_EQ(identity.set_token_calls, 0);
}

TEST_F(DeviceAuthClientTest, PustyChallengePrzerywaWymiane) {
  http.queueResponse(200, "{\"challenge\":\"\"}");

  client->update(0);

  EXPECT_EQ(http.callCount(), 1u);
  EXPECT_EQ(identity.sign_calls, 0);
}

TEST_F(DeviceAuthClientTest, NieparsowalnaOdpowiedzChallengePrzerywaWymiane) {
  http.queueResponse(200, "{to nie jest json");

  client->update(0);

  EXPECT_EQ(http.callCount(), 1u);
  EXPECT_EQ(identity.set_token_calls, 0);
}

TEST_F(DeviceAuthClientTest, PustyPodpisPrzerywaWymianePrzedVerify) {
  identity.signature_to_return = "";
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");

  client->update(0);

  EXPECT_EQ(http.callCount(), 1u);
  EXPECT_EQ(identity.set_token_calls, 0);
}

TEST_F(DeviceAuthClientTest, BrakExpiresAtNieZapisujeTokenu) {
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
  http.queueResponse(200, "{\"token\":\"tok-123\"}");

  client->update(0);

  EXPECT_EQ(identity.set_token_calls, 0);
}

TEST_F(DeviceAuthClientTest, NiepoprawnyExpiresAtNieZapisujeTokenu) {
  // Gdyby przeszedł, token wyglądałby na ważny mimo braku sensownej daty.
  http.queueResponse(200, "{\"challenge\":\"YWJjZGVmZ2g\"}");
  http.queueResponse(200, "{\"token\":\"tok-123\",\"expires_at\":\"kiedys-tam\"}");

  client->update(0);

  EXPECT_EQ(identity.set_token_calls, 0);
}

TEST_F(DeviceAuthClientTest, NieudanaWymianaJestPonawianaPoPollInterval) {
  http.queueResponse(500, "");
  client->update(0);
  ASSERT_EQ(http.callCount(), 1u);

  queueSuccessfulHandshake();
  client->update(kPollIntervalMs);

  EXPECT_EQ(identity.set_token_calls, 1);
}

}  // namespace
