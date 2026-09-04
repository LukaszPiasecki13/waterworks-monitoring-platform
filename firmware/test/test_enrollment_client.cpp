// Priorytet 4 wg ryzyka: przyjęcie kodu aktywacyjnego i przejście do telemetrii.
// Błąd tutaj oznacza urządzenie, którego nie da się wdrożyć w terenie — albo
// takie, które w kółko wali w backend nieważnym kodem.
#include <gtest/gtest.h>

#include <Config.h>
#include <EnrollmentClient.h>
#include <Fakes.h>

#include <string>

namespace {

// Alfabet kodów wyklucza 0/O/1/I; kod musi mieć min. 10 znaków znaczących.
constexpr const char* kValidCode = "ABCD-EFGH-JKLM";

class EnrollmentClientTest : public ::testing::Test {
 protected:
  void SetUp() override {
    Serial.clearInput();
    Serial.clearCaptured();
    identity.provisioning_completed = false;
    client = new EnrollmentClient(identity, &http);
  }

  void TearDown() override { delete client; }

  void acceptCode(const char* code = kValidCode) { client->submitLine(String(std::string("ACTIVATE ") + code)); }

  FakeHttpClient http;
  FakeDeviceIdentity identity;
  EnrollmentClient* client = nullptr;
};

// --- odczyt z monitora szeregowego -----------------------------------------
//
// To jedyna droga wprowadzenia kodu do urządzenia. Między commitami 219b608
// a 70fb9f3 `readSerial()` został wypatroszony do pustej funkcji z komentarzem
// „Serial input disabled" — czyli świeżego urządzenia nie dało się w ogóle
// zaprovisionować, mimo że reszta łańcucha (processLine → redeem) działała.
// Te testy chodzą pełną ścieżką: bajty na Serial → pending_code_.

TEST_F(EnrollmentClientTest, KodWpisanyNaSerialJestPrzyjmowany) {
  Serial.feed("ACTIVATE ABCD-EFGH-JKLM\n");

  client->update(0);

  EXPECT_TRUE(client->hasPendingCode()) << "readSerial() nie czyta z monitora szeregowego";
  EXPECT_TRUE(client->needsModemBringUp());
}

TEST_F(EnrollmentClientTest, LiniaZakonczonaCrJestPrzyjmowana) {
  // Terminale na Windows wysyłają CRLF, na Linuksie LF — oba muszą działać.
  Serial.feed("ACTIVATE ABCD-EFGH-JKLM\r\n");

  client->update(0);

  EXPECT_TRUE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, LiniaPrzychodzacaWKawalkachJestSklejana) {
  // Monitor szeregowy dostarcza bajty porcjami; kod nie może zależeć od tego,
  // że cała linia pojawi się w jednym wywołaniu update().
  Serial.feed("ACTIVATE ABC");
  client->update(0);
  EXPECT_FALSE(client->hasPendingCode()) << "linia bez znaku końca nie może być przetwarzana";

  Serial.feed("D-EFGH-JKLM\n");
  client->update(10);

  EXPECT_TRUE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, PelnyKodNieTrafiaDoLogu) {
  Serial.feed("ACTIVATE ABCD-EFGH-JKLM\n");

  client->update(0);

  EXPECT_EQ(Serial.captured().find("ABCD-EFGH-JKLM"), std::string::npos)
      << "kod aktywacyjny w logu to wyciek danych uwierzytelniających";
  EXPECT_NE(Serial.captured().find("ABCD"), std::string::npos) << "zamaskowany prefiks pomaga w diagnostyce";
}

TEST_F(EnrollmentClientTest, ZalanieSmieciamiNieBlokujePrzyjeciaKodu) {
  // Bufor ma twardy limit; po jego przekroczeniu linia jest odrzucana,
  // ale klient musi dalej działać.
  Serial.feed(std::string(500, 'X'));
  client->update(0);
  EXPECT_FALSE(client->hasPendingCode());

  Serial.feed("\nACTIVATE ABCD-EFGH-JKLM\n");
  client->update(10);

  EXPECT_TRUE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, PusteLinieSaIgnorowane) {
  Serial.feed("\n\r\n\n");
  client->update(0);
  EXPECT_FALSE(client->hasPendingCode());
}

// --- walidacja kodu --------------------------------------------------------

TEST_F(EnrollmentClientTest, PoprawnyKodJestPrzyjmowany) {
  acceptCode();
  EXPECT_TRUE(client->hasPendingCode());
  EXPECT_TRUE(client->needsModemBringUp()) << "przyjęty kod musi wywołać podniesienie modemu";
}

TEST_F(EnrollmentClientTest, KodJestNormalizowanyDoWielkichLiter) {
  client->submitLine(String("ACTIVATE abcd-efgh-jklm"));
  ASSERT_TRUE(client->hasPendingCode());

  client->onModemReady();
  http.queueResponse(200, "{}");
  client->update(0);

  ASSERT_EQ(http.callCount(), 1u);
  EXPECT_NE(http.lastRequest().payload.find("ABCD-EFGH-JKLM"), std::string::npos);
}

TEST_F(EnrollmentClientTest, LiniaBezPrefiksuActivateJestIgnorowana) {
  client->submitLine(String("ABCD-EFGH-JKLM"));
  EXPECT_FALSE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, ZaKrotkiKodJestOdrzucany) {
  acceptCode("ABCD-EFG");  // 7 znaków znaczących, minimum to 10
  EXPECT_FALSE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, KodZeZnakamiSpozaAlfabetuJestOdrzucany) {
  // 0, O, 1, I są wyłączone celowo — mylą się przy przepisywaniu z etykiety.
  acceptCode("ABCD-EFGH-JK0M");
  EXPECT_FALSE(client->hasPendingCode());
  acceptCode("ABCD-EFGH-JKLM!");
  EXPECT_FALSE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, KodPoZakonczonymProvisioninguJestIgnorowany) {
  identity.provisioning_completed = true;
  acceptCode();
  EXPECT_FALSE(client->hasPendingCode());
}

TEST_F(EnrollmentClientTest, NadmiaroweSpacjeSaObcinane) {
  client->submitLine(String("  ACTIVATE   ABCD-EFGH-JKLM  \r\n"));
  EXPECT_TRUE(client->hasPendingCode());
}

// --- realizacja kodu -------------------------------------------------------

TEST_F(EnrollmentClientTest, BezModemuNieMaProbyRealizacji) {
  acceptCode();
  client->update(0);
  EXPECT_EQ(http.callCount(), 0u);
}

TEST_F(EnrollmentClientTest, PoPodniesieniuModemuIdzieRedeem) {
  acceptCode();
  client->onModemReady();
  http.queueResponse(200, "{}");

  client->update(0);

  ASSERT_EQ(http.callCount(), 1u);
  EXPECT_EQ(http.lastRequest().resource, std::string(ACTIVATION_RESOURCE));
  EXPECT_NE(http.lastRequest().payload.find("WW-AABBCCDDEEFF"), std::string::npos);
  EXPECT_NE(http.lastRequest().payload.find("04aabbcc"), std::string::npos)
      << "backend potrzebuje klucza publicznego, żeby później weryfikować podpisy";
}

TEST_F(EnrollmentClientTest, SukcesOznaczaProvisioningJakoZakonczony) {
  acceptCode();
  client->onModemReady();
  http.queueResponse(201, "{}");

  client->update(0);

  EXPECT_EQ(identity.mark_completed_calls, 1);
  EXPECT_TRUE(identity.isProvisioningCompleted());
  EXPECT_FALSE(client->hasPendingCode()) << "po sukcesie kod nie może zostać w kolejce";
}

TEST_F(EnrollmentClientTest, PoSukcesieNieMaKolejnychProbRealizacji) {
  acceptCode();
  client->onModemReady();
  http.queueResponse(200, "{}");
  client->update(0);
  ASSERT_EQ(http.callCount(), 1u);

  client->update(ACTIVATION_RETRY_INTERVAL_MS * 10);

  EXPECT_EQ(http.callCount(), 1u);
}

// --- odrzucenia i backoff --------------------------------------------------

class EnrollmentClientPermanentRejectionTest : public EnrollmentClientTest,
                                               public ::testing::WithParamInterface<int> {};

TEST_P(EnrollmentClientPermanentRejectionTest, TrwaleOdrzucenieKasujeKodBezPonawiania) {
  // 404/409/410 = kod nie istnieje, już zużyty albo wygasł. Ponawianie nie ma
  // sensu i tylko pali transfer na karcie SIM.
  acceptCode();
  client->onModemReady();
  http.queueResponse(GetParam(), "");

  client->update(0);
  EXPECT_FALSE(client->hasPendingCode());
  EXPECT_EQ(identity.mark_completed_calls, 0);

  client->update(ACTIVATION_RETRY_INTERVAL_MS * 10);
  EXPECT_EQ(http.callCount(), 1u);
}

INSTANTIATE_TEST_SUITE_P(KodyTrwale, EnrollmentClientPermanentRejectionTest, ::testing::Values(404, 409, 410));

TEST_F(EnrollmentClientTest, BladPrzejsciowyZachowujeKodIPonawiaPoBackoffie) {
  acceptCode();
  client->onModemReady();
  http.queueResponse(500, "");

  client->update(0);
  ASSERT_EQ(http.callCount(), 1u);
  EXPECT_TRUE(client->hasPendingCode());

  // Przed upływem backoffu nie ma kolejnej próby.
  client->update(ACTIVATION_RETRY_INTERVAL_MS - 1);
  EXPECT_EQ(http.callCount(), 1u);

  // Po upływie — jest.
  http.queueResponse(200, "{}");
  client->update(ACTIVATION_RETRY_INTERVAL_MS);
  EXPECT_EQ(http.callCount(), 2u);
  EXPECT_EQ(identity.mark_completed_calls, 1);
}

TEST_F(EnrollmentClientTest, KolejneBledyPrzejscioweNieOmijajaBackoffu) {
  acceptCode();
  client->onModemReady();

  unsigned long now = 0;
  for (int attempt = 1; attempt <= 3; ++attempt) {
    http.queueResponse(503, "");
    client->update(now);
    EXPECT_EQ(http.callCount(), static_cast<size_t>(attempt));

    // Sto wywołań pętli w środku backoffu nie może wygenerować ruchu.
    for (unsigned long tick = 1; tick < ACTIVATION_RETRY_INTERVAL_MS; tick += ACTIVATION_RETRY_INTERVAL_MS / 100) {
      client->update(now + tick);
    }
    EXPECT_EQ(http.callCount(), static_cast<size_t>(attempt)) << "backoff przeciekł przy próbie " << attempt;

    now += ACTIVATION_RETRY_INTERVAL_MS;
  }
}

TEST_F(EnrollmentClientTest, BrakKlientaHttpNieWywracaPetli) {
  EnrollmentClient bare(identity, nullptr);
  bare.submitLine(String(std::string("ACTIVATE ") + kValidCode));
  bare.onModemReady();

  bare.update(0);  // nie może się wywalić ani nic wysłać

  EXPECT_TRUE(bare.hasPendingCode());
}

TEST_F(EnrollmentClientTest, SetHttpClientPozwalaDokonczycRealizacje) {
  // Ścieżka z main.cpp: klient HTTP powstaje dopiero po podniesieniu modemu.
  EnrollmentClient late(identity, nullptr);
  late.submitLine(String(std::string("ACTIVATE ") + kValidCode));
  late.update(0);

  late.setHttpClient(&http);
  late.onModemReady();
  http.queueResponse(200, "{}");
  late.update(0);

  EXPECT_EQ(http.callCount(), 1u);
  EXPECT_EQ(identity.mark_completed_calls, 1);
}

}  // namespace
