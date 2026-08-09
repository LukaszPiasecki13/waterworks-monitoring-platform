# Instrukcja dla Agenta AI: ESP32-S3 + A7670E wysyłka danych telemetrycznych do backendu


## 1. Cel zadania


Przygotuj program dla **ESP32-S3 z modemem LTE A7670E**, który będzie wysyłał dane telemetryczne do publicznego backendu FastAPI.


Program ma działać bez Wi-Fi, wyłącznie przez kartę SIM i modem A7670E.


Backend ma już działający endpoint:


```text
POST /telemetry/ingest
```


Backend wymaga nagłówka:


```http
X-Device-Key: Test1
```


Dane mają być wysyłane cyklicznie, np. co 1 sekundę. Każda paczka ma zawierać inkrementowany licznik `seq`, a wartość pomiarowa `value` ma być równa `seq`, żeby łatwo potwierdzić poprawność danych w bazie.


---


## 2. Założenia techniczne


### Sprzęt


```text
ESP32-S3
modem LTE A7670E
karta SIM z aktywnym pakietem danych
antena LTE
stabilne zasilanie dla modemu
połączenie UART ESP32-S3 ↔ A7670E
wspólna masa GND
```


### Biblioteki Arduino


Program ma używać:


```text
TinyGSM
ArduinoHttpClient
ArduinoJson
```


### Ważne założenia


1. Nie używać Wi-Fi.
2. Modem A7670E obsługiwać przez UART i komendy AT przez TinyGSM.
3. JSON budować przez ArduinoJson, a nie przez ręczne sklejanie dużego stringa.
4. Wysyłać HTTP POST na publiczny backend.
5. Nie zwiększać `seq`, jeśli wysyłka się nie udała.
6. Zwiększać `seq` tylko po odpowiedzi HTTP `200` albo `202`.
7. Logować wszystko w Serial Monitorze.
8. Dioda LED ma sygnalizować sukces i błąd.


---


## 3. Konfiguracja endpointu backendu


Backend testowo przyjął taki request:


```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/telemetry/ingest' \
  -H 'accept: application/json' \
  -H 'X-Device-Key: Test1' \
  -H 'Content-Type: application/json' \
  -d '{
  "v": 1,
  "device_id": "string",
  "org_id": "string",
  "object_id": "string",
  "seq": 1,
  "sent_at": "2026-08-05T10:31:09.492Z",
  "windows": [
    {
      "window_start": "2026-08-05T10:31:09.492Z",
      "window_seconds": 1,
      "points": [
        {
          "point_id": "string",
          "type": "string",
          "unit": "string",
          "quality": "string",
          "avg": 1,
          "min": 0,
          "max": 0,
          "value": 0
        }
      ]
    }
  ]
}'
```


W programie ESP32 **nie wolno używać**:


```text
127.0.0.1
localhost
```


Adres `127.0.0.1` oznacza urządzenie lokalne. Dla ESP32 byłby to sam ESP32, a nie komputer ani serwer.


W programie należy użyć publicznego hosta backendu, np.:


```cpp
const char SERVER[] = "api.twojadomena.pl";
const int PORT = 80;
const char RESOURCE[] = "/telemetry/ingest";
```


Jeśli backend działa po HTTPS:


```cpp
const char SERVER[] = "api.twojadomena.pl";
const int PORT = 443;
const char RESOURCE[] = "/telemetry/ingest";
```


Wartości do uzupełnienia przez developera:


```cpp
const char SERVER[] = "TWOJ_PUBLICZNY_BACKEND_HOST";
const int PORT = 80;
const char RESOURCE[] = "/telemetry/ingest";
const char DEVICE_KEY[] = "Test1";
```


---


## 4. Payload wysyłany przez ESP32


Program ma wysyłać payload w takim formacie:


```json
{
  "v": 1,
  "device_id": "esp32-a7670e-0001",
  "org_id": "test-org",
  "object_id": "test-object",
  "seq": 1,
  "sent_at": "2026-08-05T10:31:09.492Z",
  "windows": [
    {
      "window_start": "2026-08-05T10:31:09.492Z",
      "window_seconds": 1,
      "points": [
        {
          "point_id": "test-counter",
          "type": "debug_counter",
          "unit": "count",
          "quality": "good",
          "avg": 1,
          "min": 1,
          "max": 1,
          "value": 1
        }
      ]
    }
  ]
}
```


Dla kolejnych wysyłek:


```text
seq = 1, value = 1, avg = 1, min = 1, max = 1
seq = 2, value = 2, avg = 2, min = 2, max = 2
seq = 3, value = 3, avg = 3, min = 3, max = 3
...
```


Dzięki temu w bazie łatwo sprawdzić, czy ESP32 faktycznie wysyła nowe dane i czy backend zapisuje je po kolei.


---


## 5. Logika działania programu


Program ma realizować następujący flow:


```text
setup()
  1. Uruchom Serial Monitor 115200.
  2. Skonfiguruj LED.
  3. Uruchom zasilanie / PWRKEY modemu, jeśli używany.
  4. Uruchom UART do A7670E.
  5. Zainicjalizuj modem.
  6. Poczekaj na rejestrację w sieci komórkowej.
  7. Połącz APN.
  8. Wypisz status w Serial Monitorze.


loop()
  1. Co 1 sekundę sprawdź połączenie.
  2. Jeśli brak sieci lub APN, wykonaj reconnect.
  3. Zbuduj JSON z aktualnym seq.
  4. Wyślij HTTP POST.
  5. Wypisz HTTP status i response body.
  6. Jeśli HTTP status to 200 albo 202, zwiększ seq.
  7. Jeśli błąd, nie zwiększaj seq i ponów za kilka sekund.
```


---


## 6. Uwagi specyficzne dla ESP32-S3


ESP32-S3 różni się od klasycznego ESP32 głównie pinami i obsługą portów szeregowych. Dlatego w kodzie należy jawnie wskazać UART oraz piny RX/TX dla modemu.


Najważniejsze zasady dla ESP32-S3:


1. Nie zakładaj, że `GPIO16/GPIO17` zawsze są poprawne dla Twojej płytki. Sprawdź pinout konkretnego modułu lub devkita.
2. Nie używaj portu `Serial` do modemu, bo `Serial` zostawiamy dla Serial Monitora i debugowania.
3. Dla modemu użyj oddzielnego UART, np. `HardwareSerial SerialAT(1);`.
4. W `SerialAT.begin(...)` jawnie podaj piny RX i TX.
5. Jeżeli płytka ESP32-S3 ma natywne USB, `Serial` może działać przez USB CDC, a nie klasyczny UART0. To jest OK, ale modem nadal powinien pracować na osobnym UART.
6. Wbudowana dioda LED na ESP32-S3 zależy od konkretnej płytki. Często nie jest to `GPIO2`. Jeśli LED nie działa, ustaw `LED_PIN = -1` albo podaj właściwy pin LED/RGB dla swojej płytki.


Rekomendowana domyślna konfiguracja do sprawdzenia:


```cpp
HardwareSerial SerialAT(1);


const int MODEM_RX_PIN = 18; // ESP32-S3 RX, podłączony do TX modemu
const int MODEM_TX_PIN = 17; // ESP32-S3 TX, podłączony do RX modemu
```


Jeśli Twoja płytka ma już opisane piny UART dla gniazda modemu, użyj pinów z dokumentacji płytki zamiast powyższych.


---


## 7. Wymagane logi w Serial Monitorze


Program ma wypisywać minimum:


```text
[BOOT] start programu
[MODEM] inicjalizacja
[MODEM] informacje o modemie
[NET] oczekiwanie na sieć
[NET] jakość sygnału
[DATA] łączenie z APN
[DATA] lokalny IP modemu
[HTTP] server, port, resource
[HTTP] seq
[HTTP] payload length
[HTTP] status
[HTTP] response body
[LOOP] decyzja: sukces / retry
```


Przykładowy poprawny log:


```text
[BOOT] ESP32-S3 + A7670E telemetry sender
[MODEM] Info: A7670E...
[NET] Network connected
[NET] Signal quality: 20
[DATA] GPRS/LTE connected
[DATA] Local IP: 10.x.x.x
[HTTP] POST seq=1
[HTTP] Status: 202
[HTTP] Response: {"status":"accepted","device_id":"esp32-a7670e-0001","seq":1}
[LOOP] Send OK, next seq=2
```


---


## 8. Obsługa błędów


### Brak modemu


Objawy:


```text
modem.init() failed
modem.restart() failed
```


Program powinien:


```text
1. wypisać błąd,
2. zamigać LED 3 razy,
3. spróbować ponownie po kilku sekundach albo pozostać w trybie retry.
```


### Brak sieci


Objawy:


```text
waitForNetwork() failed
Network not connected
```


Program powinien:


```text
1. nie wysyłać HTTP,
2. nie zwiększać seq,
3. ponowić próbę połączenia po kilku sekundach.
```


### Brak APN / transmisji danych


Objawy:


```text
gprsConnect() failed
GPRS/LTE not connected
```


Program powinien:


```text
1. rozłączyć dane,
2. spróbować ponownie połączyć APN,
3. nie zwiększać seq.
```


### HTTP 403


Znaczenie:


```text
zły albo brakujący X-Device-Key
```


Sprawdzić:


```cpp
const char DEVICE_KEY[] = "Test1";
```


### HTTP 422


Znaczenie:


```text
payload nie pasuje do schematu Pydantic po stronie backendu
```


Sprawdzić:


```text
sent_at
window_start
windows
points
value / avg / min / max
Content-Type
JSON syntax
```


### HTTP 500


Znaczenie:


```text
problem po stronie backendu lub bazy danych
```


Program powinien:


```text
1. nie zwiększać seq,
2. ponowić ten sam seq po opóźnieniu.
```


### Timeout / status ujemny


Znaczenie:


```text
problem z siecią, DNS, portem, HTTP/HTTPS albo backendiem
```


Sprawdzić:


```text
SERVER
PORT
RESOURCE
czy backend jest HTTP czy HTTPS
czy karta SIM ma internet
czy APN jest poprawny
czy jest zasięg LTE
```


---


## 9. LED jako status


Program ma wykorzystywać LED:


```text
1 krótkie mignięcie  → wysyłka OK
3 szybkie mignięcia  → błąd wysyłki / połączenia
```


Opcjonalnie później:


```text
wolne ciągłe miganie   → brak sieci
szybkie ciągłe miganie → brak modemu lub SIM
```


---


## 10. Kod programu Arduino: HTTP


> Uwaga: to jest wersja HTTP na port `80`. Jeśli backend działa tylko po HTTPS, trzeba użyć wariantu z klientem secure i portem `443`.


```cpp
#define TINY_GSM_MODEM_A7672X
#define TINY_GSM_RX_BUFFER 1024


#include <Arduino.h>
#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>


// =========================
// Serial
// =========================


#define SerialMon Serial
HardwareSerial SerialAT(1);


// =========================
// Piny ESP32 <-> A7670E
// Dostosuj do swojej płytki/modułu
// =========================


// Na ESP32-S3 wbudowany LED zależy od płytki.
// Jeśli nie znasz pinu LED albo płytka ma RGB LED bez prostego GPIO, ustaw -1.
const int LED_PIN = 2;


// ESP32-S3 RX odbiera z TX modemu.
// ESP32-S3 TX nadaje do RX modemu.
// Dostosuj do pinoutu swojej płytki ESP32-S3.
const int MODEM_RX_PIN = 18;
const int MODEM_TX_PIN = 17;


// Jeśli Twój moduł ma PWRKEY podłączony do ESP32, ustaw pin.
// Jeśli nie masz sterowania PWRKEY z ESP32, ustaw -1.
const int MODEM_PWRKEY_PIN = 4;


// Jeśli Twój moduł ma osobny pin ENABLE/POWER, ustaw go tutaj.
// Jeśli nie używasz, zostaw -1.
const int MODEM_POWER_ENABLE_PIN = -1;


const uint32_t MODEM_BAUD = 115200;


// =========================
// Konfiguracja SIM/APN
// =========================


// Uzupełnij APN operatora.
// Często w Polsce jest to "internet", ale sprawdź dla swojej karty SIM.
const char APN[] = "internet";
const char GPRS_USER[] = "";
const char GPRS_PASS[] = "";


// Jeśli karta SIM ma PIN, wpisz go tutaj.
// Jeśli nie ma PIN-u, zostaw pusty string.
const char SIM_PIN[] = "";


// =========================
// Backend
// =========================


// UWAGA:
// SERVER bez "http://" i bez "https://"
// Przykład:
// const char SERVER[] = "api.twojadomena.pl";
const char SERVER[] = "TWOJ_PUBLICZNY_BACKEND_HOST";


// HTTP port.
const int PORT = 80;


// Sama ścieżka endpointu.
const char RESOURCE[] = "/telemetry/ingest";


// Header wymagany przez backend.
const char DEVICE_KEY[] = "Test1";


// =========================
// Dane telemetryczne
// =========================


const char DEVICE_ID[] = "esp32-a7670e-0001";
const char ORG_ID[] = "test-org";
const char OBJECT_ID[] = "test-object";


const unsigned long SEND_INTERVAL_MS = 1000;
const unsigned long ERROR_RETRY_MS = 5000;


uint32_t seq = 1;
unsigned long lastSendMs = 0;
unsigned long nextAllowedSendMs = 0;


// TinyGSM
TinyGsm modem(SerialAT);
TinyGsmClient client(modem);


// HTTP client
HttpClient http(client, SERVER, PORT);


// =========================
// LED helpers
// =========================


void blinkLed(int count, int delayMs) {
  if (LED_PIN < 0) {
    return;
  }


  for (int i = 0; i < count; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}


void blinkOk() {
  blinkLed(1, 80);
}


void blinkError() {
  blinkLed(3, 120);
}


// =========================
// Modem power
// =========================


void powerOnModem() {
  if (MODEM_POWER_ENABLE_PIN >= 0) {
    pinMode(MODEM_POWER_ENABLE_PIN, OUTPUT);
    digitalWrite(MODEM_POWER_ENABLE_PIN, HIGH);
    delay(500);
  }


  if (MODEM_PWRKEY_PIN >= 0) {
    pinMode(MODEM_PWRKEY_PIN, OUTPUT);


    // Typowy impuls PWRKEY dla modułów SIMCom:
    // HIGH -> LOW -> HIGH.
    digitalWrite(MODEM_PWRKEY_PIN, HIGH);
    delay(100);
    digitalWrite(MODEM_PWRKEY_PIN, LOW);
    delay(1200);
    digitalWrite(MODEM_PWRKEY_PIN, HIGH);
    delay(3000);
  }
}


// =========================
// Network
// =========================


bool setupModem() {
  SerialMon.println();
  SerialMon.println("[MODEM] Power on...");
  powerOnModem();


  SerialMon.println("[MODEM] Starting UART...");
  SerialAT.begin(MODEM_BAUD, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
  delay(3000);


  SerialMon.println("[MODEM] Initializing modem...");


  if (!modem.init()) {
    SerialMon.println("[MODEM] modem.init() failed, trying restart...");
    if (!modem.restart()) {
      SerialMon.println("[MODEM] modem.restart() failed");
      return false;
    }
  }


  String modemInfo = modem.getModemInfo();
  SerialMon.print("[MODEM] Info: ");
  SerialMon.println(modemInfo);


  if (strlen(SIM_PIN) > 0) {
    SerialMon.println("[MODEM] Unlocking SIM...");
    modem.simUnlock(SIM_PIN);
  }


  return true;
}


bool connectNetwork() {
  SerialMon.println("[NET] Waiting for network...");


  if (!modem.waitForNetwork(60000L)) {
    SerialMon.println("[NET] waitForNetwork() failed");
    return false;
  }


  if (!modem.isNetworkConnected()) {
    SerialMon.println("[NET] Network not connected");
    return false;
  }


  SerialMon.println("[NET] Network connected");


  int signal = modem.getSignalQuality();
  SerialMon.print("[NET] Signal quality: ");
  SerialMon.println(signal);


  SerialMon.print("[DATA] Connecting APN: ");
  SerialMon.println(APN);


  if (!modem.gprsConnect(APN, GPRS_USER, GPRS_PASS)) {
    SerialMon.println("[DATA] gprsConnect() failed");
    return false;
  }


  if (!modem.isGprsConnected()) {
    SerialMon.println("[DATA] GPRS/LTE not connected");
    return false;
  }


  SerialMon.println("[DATA] GPRS/LTE connected");
  SerialMon.print("[DATA] Local IP: ");
  SerialMon.println(modem.localIP());


  return true;
}


bool ensureConnection() {
  if (!modem.isNetworkConnected()) {
    SerialMon.println("[NET] Network lost, reconnecting...");


    if (!modem.waitForNetwork(60000L)) {
      SerialMon.println("[NET] Reconnect network failed");
      return false;
    }
  }


  if (!modem.isGprsConnected()) {
    SerialMon.println("[DATA] GPRS/LTE lost, reconnecting APN...");


    modem.gprsDisconnect();
    delay(1000);


    if (!modem.gprsConnect(APN, GPRS_USER, GPRS_PASS)) {
      SerialMon.println("[DATA] Reconnect APN failed");
      return false;
    }
  }


  return true;
}


// =========================
// Payload
// =========================


String buildPayload(uint32_t currentSeq) {
  StaticJsonDocument<1024> doc;


  doc["v"] = 1;
  doc["device_id"] = DEVICE_ID;
  doc["org_id"] = ORG_ID;
  doc["object_id"] = OBJECT_ID;
  doc["seq"] = currentSeq;


  // Na start używamy stałego timestampu.
  // Backend i tak ustawia received_at po swojej stronie.
  doc["sent_at"] = "2026-08-05T10:31:09.492Z";


  JsonArray windows = doc.createNestedArray("windows");
  JsonObject window = windows.createNestedObject();


  window["window_start"] = "2026-08-05T10:31:09.492Z";
  window["window_seconds"] = 1;


  JsonArray points = window.createNestedArray("points");
  JsonObject point = points.createNestedObject();


  point["point_id"] = "test-counter";
  point["type"] = "debug_counter";
  point["unit"] = "count";
  point["quality"] = "good";


  // Celowo wszystkie wartości są równe seq,
  // żeby w bazie łatwo było sprawdzić poprawność.
  point["avg"] = currentSeq;
  point["min"] = currentSeq;
  point["max"] = currentSeq;
  point["value"] = currentSeq;


  String payload;
  serializeJson(doc, payload);
  return payload;
}


// =========================
// HTTP POST
// =========================


bool sendTelemetry(uint32_t currentSeq) {
  String payload = buildPayload(currentSeq);


  SerialMon.println();
  SerialMon.print("[HTTP] POST seq=");
  SerialMon.println(currentSeq);


  SerialMon.print("[HTTP] Server: ");
  SerialMon.print(SERVER);
  SerialMon.print(":");
  SerialMon.println(PORT);


  SerialMon.print("[HTTP] Resource: ");
  SerialMon.println(RESOURCE);


  SerialMon.print("[HTTP] Payload bytes: ");
  SerialMon.println(payload.length());


  SerialMon.print("[HTTP] Payload: ");
  SerialMon.println(payload);


  unsigned long startMs = millis();


  http.stop();


  http.beginRequest();
  http.post(RESOURCE);
  http.sendHeader("Content-Type", "application/json");
  http.sendHeader("Accept", "application/json");
  http.sendHeader("X-Device-Key", DEVICE_KEY);
  http.sendHeader("Content-Length", payload.length());
  http.beginBody();
  http.print(payload);
  http.endRequest();


  int statusCode = http.responseStatusCode();
  String response = http.responseBody();


  unsigned long durationMs = millis() - startMs;


  SerialMon.print("[HTTP] Status: ");
  SerialMon.println(statusCode);


  SerialMon.print("[HTTP] Duration ms: ");
  SerialMon.println(durationMs);


  SerialMon.print("[HTTP] Response: ");
  SerialMon.println(response);


  http.stop();


  if (statusCode == 200 || statusCode == 202) {
    return true;
  }


  return false;
}


// =========================
// Arduino setup/loop
// =========================


void setup() {
  if (LED_PIN >= 0) {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
  }


  SerialMon.begin(115200);
  delay(2000);


  SerialMon.println();
  SerialMon.println("========================================");
  SerialMon.println("[BOOT] ESP32-S3 + A7670E telemetry sender");
  SerialMon.println("========================================");


  bool modemOk = setupModem();
  if (!modemOk) {
    SerialMon.println("[BOOT] Modem setup failed");
    blinkError();
    nextAllowedSendMs = millis() + ERROR_RETRY_MS;
    return;
  }


  bool networkOk = connectNetwork();
  if (!networkOk) {
    SerialMon.println("[BOOT] Network setup failed");
    blinkError();
    nextAllowedSendMs = millis() + ERROR_RETRY_MS;
    return;
  }


  SerialMon.println("[BOOT] Ready");
  blinkOk();
}


void loop() {
  unsigned long now = millis();


  if (now < nextAllowedSendMs) {
    delay(10);
    return;
  }


  if (now - lastSendMs < SEND_INTERVAL_MS) {
    delay(10);
    return;
  }


  lastSendMs = now;


  if (!ensureConnection()) {
    SerialMon.println("[LOOP] Connection not ready");
    blinkError();
    nextAllowedSendMs = millis() + ERROR_RETRY_MS;
    return;
  }


  bool ok = sendTelemetry(seq);


  if (ok) {
    SerialMon.print("[LOOP] Send OK, next seq=");
    SerialMon.println(seq + 1);


    seq++;
    blinkOk();


    nextAllowedSendMs = millis() + SEND_INTERVAL_MS;
  } else {
    SerialMon.print("[LOOP] Send failed, will retry same seq=");
    SerialMon.println(seq);


    blinkError();


    // Nie zwiększamy seq przy błędzie.
    nextAllowedSendMs = millis() + ERROR_RETRY_MS;
  }
}
```


---


## 11. Wariant HTTPS


Jeżeli backend jest dostępny tylko przez HTTPS, program HTTP nie wystarczy.


Wtedy zmień:


```cpp
TinyGsmClient client(modem);
HttpClient http(client, SERVER, PORT);
const int PORT = 80;
```


na:


```cpp
TinyGsmClientSecure client(modem);
HttpClient http(client, SERVER, PORT);
const int PORT = 443;
```


Czyli sekcja klienta powinna wyglądać tak:


```cpp
TinyGsm modem(SerialAT);
TinyGsmClientSecure client(modem);
HttpClient http(client, SERVER, PORT);
```


W niektórych konfiguracjach A7670E/TinyGSM HTTPS może wymagać dodatkowej konfiguracji certyfikatów albo innej biblioteki TLS. Na pierwszy test, jeśli to możliwe, użyj HTTP, a dopiero później przejdź na HTTPS.


---


## 12. Ustawienia do podmiany przed kompilacją


Developer musi koniecznie sprawdzić i uzupełnić:


```cpp
const char APN[] = "internet";
const char GPRS_USER[] = "";
const char GPRS_PASS[] = "";
const char SIM_PIN[] = "";


const char SERVER[] = "TWOJ_PUBLICZNY_BACKEND_HOST";
const int PORT = 80;
const char RESOURCE[] = "/telemetry/ingest";
const char DEVICE_KEY[] = "Test1";


const int MODEM_RX_PIN = 18;
const int MODEM_TX_PIN = 17;
const int MODEM_PWRKEY_PIN = 4;
const int MODEM_POWER_ENABLE_PIN = -1;
```


---


## 13. Test przed uruchomieniem ESP32-S3


Przed testem z ESP32 sprawdź publiczny backend z komputera:


```bash
curl -i -X POST "http://TWOJ_PUBLICZNY_BACKEND_HOST/telemetry/ingest" \
  -H "accept: application/json" \
  -H "X-Device-Key: Test1" \
  -H "Content-Type: application/json" \
  -d '{
    "v": 1,
    "device_id": "esp32-a7670e-0001",
    "org_id": "test-org",
    "object_id": "test-object",
    "seq": 999,
    "sent_at": "2026-08-05T10:31:09.492Z",
    "windows": [
      {
        "window_start": "2026-08-05T10:31:09.492Z",
        "window_seconds": 1,
        "points": [
          {
            "point_id": "test-counter",
            "type": "debug_counter",
            "unit": "count",
            "quality": "good",
            "avg": 999,
            "min": 999,
            "max": 999,
            "value": 999
          }
        ]
      }
    ]
  }'
```


Oczekiwane odpowiedzi:


```text
pierwsze wysłanie: HTTP 202 accepted
ponowne wysłanie tego samego seq: HTTP 200 duplicate
```


---


## 14. Test po uruchomieniu ESP32-S3


W Serial Monitorze powinno pojawić się:


```text
[BOOT] ESP32-S3 + A7670E telemetry sender
[MODEM] Info: ...
[NET] Network connected
[DATA] GPRS/LTE connected
[HTTP] POST seq=1
[HTTP] Status: 202
[HTTP] Response: {"status":"accepted","device_id":"esp32-a7670e-0001","seq":1}
[LOOP] Send OK, next seq=2
```


Kolejne wysyłki:


```text
seq=2 → HTTP 202
seq=3 → HTTP 202
seq=4 → HTTP 202
```


---


## 15. Sprawdzenie w bazie danych


Po stronie backendu wykonaj:


```sql
SELECT
    device_id,
    seq,
    received_at,
    payload -> 'windows' -> 0 -> 'points' -> 0 ->> 'value' AS value
FROM telemetry_packets
WHERE device_id = 'esp32-a7670e-0001'
ORDER BY seq DESC
LIMIT 20;
```


Oczekiwany wynik:


```text
seq    value
20     20
19     19
18     18
17     17
...
```


---


## 16. Najczęstsze problemy


### Modem nie odpowiada


Sprawdź:


```text
RX/TX są zamienione poprawnie
GND ESP32 i modemu jest wspólne
modem ma osobne stabilne zasilanie
MODEM_BAUD jest poprawny
PWRKEY jest poprawnie obsłużony
```


### Brak internetu przez SIM


Sprawdź:


```text
APN
aktywność karty SIM
pakiet danych
zasięg LTE
antena
PIN karty SIM
```


### HTTP 403


Sprawdź:


```cpp
const char DEVICE_KEY[] = "Test1";
```


### HTTP 422


Sprawdź wygenerowany payload w Serial Monitorze.


Najczęstsze błędy:


```text
brak pola sent_at
brak pola windows
brak pola points
niepoprawny JSON
zły Content-Type
brak value/avg/min/max
```


### Timeout lub status ujemny


Sprawdź:


```text
czy SERVER jest bez http:// i https://
czy PORT pasuje do HTTP/HTTPS
czy RESOURCE to dokładnie /telemetry/ingest
czy backend jest dostępny publicznie
czy DNS działa przez operatora SIM
```


---


## 17. Kryterium zakończenia zadania


Program można uznać za działający, jeśli:


```text
1. ESP32-S3 łączy się z modemem A7670E.
2. Modem rejestruje się w sieci.
3. Modem łączy się z APN.
4. ESP32-S3 wysyła payload co 1 sekundę.
5. Backend zwraca HTTP 202 dla nowych seq.
6. Backend zwraca HTTP 200 duplicate przy powtórzeniu tego samego seq.
7. W bazie widać rosnące seq.
8. payload.windows[0].points[0].value jest równe seq.
```


---


## 18. Oczekiwany wynik pracy Agenta AI


Agent AI ma dostarczyć:


```text
1. Jeden kompletny plik .ino.
2. Kod bez użycia Wi-Fi.
3. Kod z TinyGSM, ArduinoHttpClient i ArduinoJson.
4. Konfigurację APN, backendu i pinów na początku pliku.
5. Wysyłkę co 1 sekundę.
6. Inkrementowany seq i value.
7. Retry bez zwiększania seq po błędzie.
8. Logi diagnostyczne w Serial Monitorze.
9. Obsługę LED dla sukcesu i błędu.
10. Oddzielną informację, co zmienić dla HTTPS.
```


