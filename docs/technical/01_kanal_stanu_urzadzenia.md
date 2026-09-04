# Kanał odczytu stanu z urządzenia (B-08)

> Dokument przekrojowy — kanał obejmuje firmware, backend i frontend naraz, dlatego leży w `docs/technical/`, a nie w katalogu jednej warstwy. Szczegóły warstwowe: [`04_telemetry_module.md`](./backend/04_telemetry_module.md) (backend), [`03_esp32_reset_and_recovery.md`](./firmware/03_esp32_reset_and_recovery.md) (firmware), [`frontend-architecture.md`](./frontend/frontend-architecture.md).

## 1. Po co ten kanał istnieje

Do tej pory komunikacja była **wyłącznie jednokierunkowa**: urządzenie wysyła pakiet, backend odpowiada statusem. `TelemetryHttpClient` miał tylko `post()`, bez `get()`. Gateway siedzi za NAT-em operatora komórkowego, więc backend **nie może** się do niego odezwać z własnej inicjatywy — nie ma publicznego adresu, pod który dałoby się zapukać.

Każdy odczyt z urządzenia musi więc być **odpowiedzią urządzenia przy jego następnym kontakcie**. Model jest pull, nie push, i wynika z topologii sieci, nie z wygody.

To zlecenie wprowadza **dokładnie jeden** kanoniczny mechanizm takiego odczytu. Kolejne odczyty (konfiguracja urządzenia, inwentarz czujników, cokolwiek) idą tą samą ścieżką: nowa **sekcja** w rejestrze, nie nowy endpoint i nie nowa tabela.

## 2. Decyzja: dlaczego blok w istniejącym POST-cie, a nie osobny endpoint

Rozważane były trzy warianty. Wszystkie liczby poniżej pochodzą z kodu, nie z założeń.

**Punkt odniesienia z kodu:**

| Parametr | Wartość | Źródło |
|---|---|---|
| `SAMPLE_INTERVAL_MS` | 15 000 | [`Config.h`](../../firmware/include/Config.h) |
| `WINDOW_SECONDS` | 15 | [`TelemetryPayload.h`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) |
| `WINDOWS_PER_BATCH` | 4 → transmisja co **~60 s** | jw. |
| `RETAIN_WINDOWS_MAX` | 48 → bufor RAM **~12 min** | jw. |
| Rozmiar sekcji `device` na drucie | **418 B** (zmierzone, realistyczne wartości pól) | test `SectionStaysWithinItsTransferBudget` |
| Docelowy rytm wg planu biznesowego | 1–5 min | [`01_plan_biznesowy.md` §3.5](../business/01_plan_biznesowy.md) |
| Budżet SIM | 50–200 MB/mies. | [`01_plan_biznesowy.md` §3.8.5](../business/01_plan_biznesowy.md) |
| Telemetria sama w sobie | ~31,5 MB/mies. na obiekt | [`01_plan_biznesowy.md` §3.8.2](../business/01_plan_biznesowy.md) |

**Wariant A — blok stanu doczepiony do pakietu telemetrycznego.** Zero nowych rund komunikacji: sekcja jedzie w pakiecie, który i tak wychodzi.

**Wariant B — osobny `POST /telemetry/diagnostics` z własnym interwałem.** Czysty rozdział danych, ale każdy POST to pełny nowy koszt transportu. Kod zamyka połączenie przed i po każdym żądaniu ([`TelemetryHttpClient::post`](../../firmware/lib/TelemetryHttpClient/src/TelemetryHttpClient.cpp) woła `http_->stop()` po obu stronach), więc **każdy POST to nowy handshake TLS**: uzgodnienie TCP + ServerHello + łańcuch certyfikatów + wymiana kluczy to ~4 KB, nagłówki żądania z tokenem bearer ~0,5 KB, odpowiedź ~0,3 KB. Realistycznie **~5 KB narzutu na jedno żądanie** — ponad dziesięciokrotność samych danych.

**Wariant C — backend zwraca w odpowiedzi na ingest flagę „prześlij stan przy następnym kontakcie".** Sama flaga jest tania (~20 B na odpowiedź), ale ona nie *jest* transportem stanu — po niej i tak trzeba wysłać stan wariantem A albo B, więc koszt się dodaje, a nie zastępuje.

### Koszt transferu, oba rytmy

| Wariant | Przy transmisji co 60 s | Przy transmisji co 5 min |
|---|---|---|
| A — sekcja w **każdym** pakiecie | 1440 × 418 B ≈ **18,2 MB/mies.** | 288 × 418 B ≈ **3,6 MB/mies.** |
| **A + interwał 15 min (wybrany)** | 96 × 418 B ≈ **1,2 MB/mies.** | **1,2 MB/mies.** (bez zmian) |
| B — osobny endpoint co 15 min | 96 × ~5 KB ≈ **14,4 MB/mies.** | **14,4 MB/mies.** (bez zmian) |
| B — osobny endpoint co 60 s | 1440 × ~5 KB ≈ **216 MB/mies.** | — |
| C — flaga + transport A/B | koszt A lub B **plus** ~0,85 MB/mies. na same flagi | jw. |

### Rekomendacja i uzasadnienie

**Wybrany: wariant A z własnym interwałem 15 minut.** Sekcja stanu dołącza do pakietu telemetrycznego, ale nie do każdego — o tym, kiedy dołączy, decyduje zegar (`DEVICE_STATE_REPORT_INTERVAL_MS`, domyślnie 15 min, zgodnie z założeniem §3.8.1 planu biznesowego).

Powody, w kolejności wagi:

1. **Koszt.** 1,2 MB/mies. to **~4 % budżetu telemetrii** i ~0,6 % najtańszego planu SIM. Wariant B kosztuje 14,4 MB — dwanaście razy więcej za dokładnie te same dane, bo płaci się za handshake, nie za treść.
2. **Odporność na zmianę rytmu.** Licznik chodzi po zegarze, nie po pakietach, więc **koszt jest identyczny przy 60 s i przy 5 min**. Rekomendacja nie zestarzeje się przy pierwszym przestrojeniu interwału transmisji — a to był jawny wymóg tego zlecenia.
3. **Zero nowych trybów awarii.** Nie ma drugiej ścieżki sieciowej, która mogłaby zawieść niezależnie, drugiego tokenu do odświeżenia ani drugiego endpointu do zabezpieczenia. Stan jest dostarczony dokładnie wtedy, gdy telemetria działa — a gdy nie działa, brak stanu *jest* informacją (patrz `no_comm`).
4. **Świeżość gratis.** Wariant C dodaje rundę: backend prosi, urządzenie odpowiada dopiero przy kolejnym kontakcie — nawet 2 cykle opóźnienia. Wariant A dostarcza stan uchwycony w momencie wysyłki.

Koszt wyboru, świadomie przyjęty: pakiet telemetryczny miesza dwa rodzaje danych. Łagodzi to kształt kontraktu — stan siedzi w osobnej tablicy `state[]`, w osobnej tabeli i za osobną walidacją; jedyne, co dzieli z telemetrią, to koperta HTTP.

Wariant C nie jest odrzucony na zawsze — gdy pojawi się potrzeba odczytu **na żądanie** („pokaż konfigurację tego urządzenia teraz"), flaga w odpowiedzi na ingest będzie właściwym uzupełnieniem tego kanału. Wtedy nadal wykorzysta ten sam transport i ten sam kontrakt: zmieni się tylko to, *kto* wyzwala sekcję, nie *jak* ona jedzie.

## 3. Kontrakt

Pakiet telemetryczny v2 zyskuje **opcjonalne** pole `state[]`. Firmware, które go nie wysyła, pozostaje poprawnym klientem v2.

```json
{
  "v": 2,
  "device_id": "WW-2026-000123",
  "seq": 1756900000,
  "sent_at": "2026-09-03T12:00:00.000Z",
  "windows": [ ... ],
  "errors": [ ... ],
  "state": [
    {
      "section": "device",
      "schema_version": 1,
      "captured_at": "2026-09-03T12:00:00.000Z",
      "data": {
        "serial_number": "WW-2026-000123",
        "firmware_version": "0.4.0",
        "registry_schema_version": 2,
        "uptime_seconds": 864000,
        "restart_count": 12,
        "restart_reason": "task_watchdog",
        "rssi_dbm": -67,
        "free_heap_bytes": 184320,
        "min_free_heap_bytes": 151000,
        "buffer_windows_used": 48,
        "buffer_windows_capacity": 48,
        "buffer_windows_dropped": 1234
      }
    }
  ]
}
```

**Koperta sekcji jest ścisła** (`extra="forbid"`): `section`, `schema_version`, `captured_at`, `data` — nic więcej. **Zawartość `data` jest luźna** (`extra="allow"`): znane pola są typowane, nieznane przechodzą i lądują w bazie. Ten podział jest celowy — koperta to protokół, `data` to treść, która ma prawo wyprzedzić backend.

Luźne nie znaczy nieograniczone: skoro `data` trafia do JSONB dosłownie, jego rozmiar jest ucinany na wejściu — **64 klucze i 8 KB** na sekcję, maksymalnie **16 sekcji** w pakiecie. Realna sekcja `device` to ~330 B w 12 kluczach, więc zapas na rozwój jest duży, a uwierzytelnione, ale zepsute lub przejęte urządzenie nie zapisze wiersza bez granic.

### Pola sekcji `device` (schema_version 1)

| Pole | Znaczenie | Skąd |
|---|---|---|
| `serial_number` | numer seryjny | `DeviceIdentity::serialNumber()` |
| `firmware_version` | wersja firmware | `FIRMWARE_VERSION` w `Config.h` |
| `registry_schema_version` | wersja schematu rejestru czujników | `SensorRegistry::SCHEMA_VERSION` |
| `uptime_seconds` | czas od startu | `device_state::UptimeTracker` (patrz niżej) |
| `restart_count` | restarty od ostatniego zdrowego startu | `rtcRestartCounter` (RTC, przeżywa reset) |
| `restart_reason` | przyczyna ostatniego restartu | `esp_reset_reason()` |
| `rssi_dbm` | siła sygnału | `AT+CSQ` → `-113 + 2·CSQ` |
| `free_heap_bytes`, `min_free_heap_bytes` | wolna pamięć teraz i minimum od startu | `ESP.getFreeHeap()` / `getMinFreeHeap()` |
| `buffer_windows_used`, `buffer_windows_capacity` | zapełnienie bufora lokalnego | `TelemetryPayload` |
| `buffer_windows_dropped` | okna porzucone od startu | licznik w `TelemetryPayload::sample()` |

Dwa ostatnie wiersze są w zestawie **nie przypadkiem**: bufor RAM mieści ~12 minut, a [`CONTEXT.md`](../business/CONTEXT.md) obiecuje klientowi 72 h retencji offline. Trwały bufor to osobne zadanie, ale **bez tych pól nikt nie zauważy, że urządzenie po cichu gubi dane**. Kod błędu `WINDOW_DROPPED_BUFFER_FULL` sygnalizuje pojedyncze zdarzenie i znika po potwierdzeniu pakietu; `buffer_windows_dropped` niesie sumę od startu.

`rssi_dbm` jest **pomijane**, a nie zerowane, gdy modem zwraca CSQ 99 („nie do wykrycia"). Brak odczytu i bardzo słaby sygnał nie mogą wyglądać tak samo.

`uptime_seconds` **nie** jest liczone jako `millis() / 1000`. `millis()` przewija się co ~49,7 dnia, więc gateway działający dwa miesiące raportowałby się jako świeżo zrestartowany — dokładnie odwrotny sygnał niż ten, po który sięga się do diagnostyki. [`device_state::UptimeTracker`](../../firmware/lib/DeviceState/src/DeviceState.h) zlicza przewinięcia; jest odpytywany z `loop()` (co ~10 ms), a nie przy zbieraniu snapshotu co 15 minut, bo przeoczonego przewinięcia nie da się później odtworzyć.

### Zasada nadrzędna kanału

> **Diagnostyka nigdy nie może kosztować telemetrii.**

Nieznana sekcja, rozjazd wersji schematu, popsuty payload, duplikat sekcji w jednym pakiecie — każdy z tych przypadków tworzy wpis w `errors[]` i pozwala pakietowi przejść. Pakiet z dobrymi pomiarami nie zostaje odrzucony przez wadliwy blok diagnostyczny.

| Sytuacja | Kod błędu | Czy sekcja jest zapisana |
|---|---|---|
| Sekcja spoza rejestru | `STATE_SECTION_UNKNOWN` (warning) | nie |
| `schema_version` inny niż w rejestrze | `STATE_SCHEMA_VERSION_MISMATCH` (info) | tak, bez zmian |
| `data` nie przechodzi walidacji typów | `STATE_SECTION_INVALID` (warning) | tak, surowe |
| Ta sama sekcja dwa razy w pakiecie | `STATE_SECTION_INVALID` (warning) | tylko pierwsza |
| `captured_at` z przyszłości | `STATE_CLOCK_AHEAD` (warning) | tak, z `captured_at` przyciętym do czasu odbioru |

Sekcja oflagowana jako niewiarygodna (rozjazd wersji albo błąd walidacji) **nie aktualizuje `Device.firmware_version`**. Odpowiedź na odczyt to jedno — `last_diagnostics_at` jest ustawiane tak czy owak, bo urządzenie faktycznie odpowiedziało — ale wypromowanie pola z blobu na wiersz `Device` to inne twierdzenie i sekcja, którą właśnie zakwestionowaliśmy, na nie nie zasłużyła.

## 4. Źródło prawdy o schemacie

Katalog sekcji **dołącza do istniejącego mechanizmu** [`sensor_registry.yaml`](../../sensor_registry.yaml) — tego samego, który już trzyma typy punktów i kody błędów. Nie powstaje drugi rejestr.

```yaml
schema_version: 2

state_sections:
  - id: device
    schema_version: 1
    description: "Device health and identity: firmware, uptime, restarts, RSSI, free heap, local buffer fill"
```

- **Backend** ładuje to przy starcie (`SensorRegistry.state_sections()`) i odrzuca sekcje spoza katalogu.
- **Firmware** dostaje z generatora stałe `SensorRegistry::STATE_SECTION_DEVICE` i `STATE_SECTION_DEVICE_SCHEMA_VERSION` oraz `constexpr` walidator — nie ma literałów przepisanych ręcznie.
- **Pre-build** ([`prebuild.py`](../../firmware/scripts/prebuild.py)) porównuje identyfikatory **i wersje per sekcja**; rozjazd wersji to błąd builda, nie cicha niezgodność na produkcji.

**Granica świadomie postawiona:** rejestr trzyma *słownik* (jakie sekcje istnieją i w której wersji), a nie *kształt pól*. Kształt `device` żyje w `DeviceStateData` (Pydantic) po stronie backendu i w `DeviceStateSource` po stronie firmware. Wpisywanie listy pól do YAML-a oznaczałoby wynalezienie własnego języka schematów — a rejestr od początku jest wspólnym słownikiem, nie wspólnym typem.

**Dodanie nowego odczytu** (np. konfiguracji urządzenia) to zatem: wpis `state_sections` w YAML → regeneracja nagłówka → nowa implementacja `IStateSectionSource` w firmware → opcjonalny model Pydantic. **Bez** nowego endpointu, **bez** migracji, **bez** zmiany kontraktu pakietu.

## 5. Świeżość odczytu

Odczyt z urządzenia jest z definicji stary — pytanie tylko, jak bardzo. Dane nigdy nie są pokazywane bez wieku.

Każdy wiersz trzyma **dwa** znaczniki czasu:

- `captured_at` — zegar **urządzenia** w chwili zebrania stanu (NTP-synchronizowany, ten sam co `sent_at` pakietu),
- `received_at` — zegar **platformy** w chwili odbioru.

Rozdzielenie ich ma konkretny skutek: pakiet retransmitowany po przerwie w łączności przychodzi teraz, ale opisuje stan sprzed dwóch godzin. Odczyt „najnowszej" sekcji jest dlatego rankowany po `captured_at`, nie po `received_at` — spóźniona retransmisja **nie wypiera** świeższego raportu, który przeszedł wcześniej ([`DeviceStateReportRepository.list_latest_sections`](../../backend/app/modules/telemetry/repositories/device_state.py)).

Zegar urządzenia nie jest jednak przyjmowany na wiarę. Pomiar nie mógł powstać po tym, jak dotarł, więc `captured_at` wyprzedzające czas odbioru o więcej niż 5 minut jest **przycinane do czasu odbioru** i oznaczane kodem `STATE_CLOCK_AHEAD`. Bez tego urządzenie z zepsutym NTP, którego zegar skoczył w przyszłość, wygrywałoby ranking „najnowszej sekcji" na zawsze — i przy wieku przyciętym do zera czytałoby się jako świeże. Zamrożone dane udające żywe to dokładnie ta awaria, której ten mechanizm ma zapobiegać. Pięć minut to tolerancja na dryf, nie na błąd: urządzenie stempluje `captured_at` tym samym zegarem co `sent_at`, zsynchronizowanym NTP przy starcie.

Endpoint dolicza przy każdym żądaniu:

- `age_seconds` — wiek liczony od `captured_at` (przycięty do 0 jako druga linia obrony; po przycięciu przy zapisie nie powinien już wyjść ujemny),
- `is_stale` — czy wiek przekracza `settings.telemetry_stale_after_seconds`, **ten sam próg**, którego dashboard używa do statusu `no_comm`. Urządzenie nie może być „nieświeże" w jednym widoku i „w porządku" w drugim.

Frontend pokazuje wiek jako etykietę przy nagłówku sekcji („sprzed 20 min"), a nie przy każdym polu — wszystkie pola sekcji pochodzą z jednego pomiaru.

## 6. Model danych i API

### Tabela `device_state_reports`

Jeden wiersz na parę (pakiet, sekcja). Tabela jest **świadomie agnostyczna wobec sekcji** — nowy odczyt to nowa wartość w kolumnie `section`, nie nowa tabela.

| Kolumna | Uwagi |
|---|---|
| `packet_id` | FK → `telemetry_packets.id`, `ON DELETE CASCADE` |
| `device_id` | `external_id` urządzenia, spójnie z `telemetry_packets.device_id` |
| `section`, `schema_version` | z koperty sekcji |
| `captured_at`, `received_at` | zegar urządzenia / zegar platformy |
| `data` | JSONB — surowa treść sekcji, nic nie jest gubione |

- `UniqueConstraint(packet_id, section)` — **idempotencja jedzie na idempotencji pakietu**. Dedup `(device_id, seq)` już nie wpuści retransmisji dwa razy, więc sekcje nie potrzebują własnego mechanizmu.
- `Index(device_id, section, captured_at)` — obsługuje jedyne zapytanie odczytu.
- Kasowanie telemetrii urządzenia kasuje raporty stanu przez FK, bez osobnego kroku w `DeviceLifecycleService`.

### Endpointy

| Metoda | Ścieżka | Uprawnienie |
|---|---|---|
| `GET` | `/api/v1/orgs/{org_id}/telemetry/devices/{device_id}/state` | `CAN_VIEW_ASSETS` w organizacji |
| `GET` | `/api/v1/platform/telemetry/devices/{device_id}/state` | `PLATFORM_MANAGE_DEVICE_PROVISIONING` |

Endpointy żyją w module `telemetry`, nie w `core_data`, mimo że zasobem jest urządzenie: dane wpływają ścieżką ingestu, a `core_data` jest modułem bazowym, na którym budują pozostałe — czytanie stanu stamtąd odwróciłoby kierunek zależności ([`01_backend-architecture.md` §2.4](./backend/01_backend-architecture.md)).

Urządzenie, które nigdy nie przysłało stanu, **nie jest błędem** — zwraca pustą listę `sections`, analogicznie do obiektu ze statusem `no_data` zamiast 404.

## 7. Naprawione przy okazji: `last_seen_at` vs `last_diagnostics_at`

Przed tą zmianą `device.last_diagnostics_at` było ustawiane **przy każdym ingeście telemetrii** — pole nazywało się „ostatnia diagnostyka", a znaczyło „ostatni kontakt". `last_seen_at` istniało w modelu, ale nigdy nie było zapisywane. Po wprowadzeniu prawdziwej diagnostyki ta nazwa stałaby się aktywnie myląca.

Teraz:

| Pole | Ustawiane gdy | Znaczy |
|---|---|---|
| `last_seen_at` | **każdy** przyjęty pakiet, łącznie z retransmisją rozpoznaną jako duplikat | urządzenie żyje i się odzywa |
| `last_diagnostics_at` | pakiet zawiera sekcję `device` | urządzenie odpowiedziało na odczyt stanu |

Duplikat też odświeża `last_seen_at`, choć nie niesie nowych danych: urządzenie, które retransmituje po zgubionym ACK, jest jak najbardziej żywe, a pominięcie tego przypadku kazałoby mu wyglądać na milczące dokładnie wtedy, gdy najbardziej się stara.

Dodatkowo sekcja `device` aktualizuje `device.firmware_version` — pole istniało od początku, ale nie miało kto go wypełniać.

## 8. Firmware — kształt implementacji

```
TelemetrySender ── build() ──► TelemetryPayload ──► IStateSectionSource
                                    │                      ▲
                     acknowledge()  │                      │
                                    └──────────────────────┘
                                        onAcknowledged()
```

- [`IStateSectionSource`](../../firmware/lib/DeviceState/src/IStateSectionSource.h) — jedyny punkt styku. `TelemetryPayload` nie wie, **czym** jest stan; udostępnia tablicę `state[]` i znacznik czasu pakietu.
- [`DeviceStateSource`](../../firmware/lib/DeviceState/src/DeviceStateSource.cpp) — odpowiada na odczyt `device`. Identyfikator sekcji i wersję schematu dostaje w konstruktorze (z wygenerowanego `SensorRegistry.h`), więc sama biblioteka nie zależy od pliku generowanego.
- [`device_state::ReportScheduler`](../../firmware/lib/DeviceState/src/DeviceState.h) — decyduje **kiedy**. Pierwszy raport po starcie zawsze, potem raz na interwał. Odejmowanie na `uint32_t` jest odporne na przewinięcie `millis()` po ~49 dniach.

**Potwierdzenie idzie po akceptacji, nie po wysłaniu.** `markReported()` woła się dopiero z `TelemetryPayload::acknowledge()`, czyli po HTTP 200/202. Nieudana wysyłka **nie zjada interwału** — kolejna próba znów dołączy stan. Przy ponownym budowaniu pakietu snapshot jest zbierany od nowa: uptime, RSSI i zapełnienie bufora zdążyły się zmienić, a stare liczby ostemplowane świeżym `captured_at` byłyby kłamstwem.

Cała warstwa decyzyjna (harmonogram, licznik uptime'u odporny na przewinięcie `millis()`, mapowanie przyczyn restartu, przeliczenie CSQ, kształt JSON-a) jest wolna od Arduino i ESP-IDF, więc testuje się na `env:native` bez sprzętu — łącznie ze scenariuszami, których na płytce nie da się wywołać w rozsądnym czasie, jak zachowanie uptime'u po 49 dniach.

### Odwzorowanie przyczyn restartu

`device_state::RestartReason` ma **te same wartości liczbowe** co `esp_reset_reason_t`, a [`main.cpp`](../../firmware/src/main.cpp) pilnuje tego zestawem `static_assert`. Gdyby ESP-IDF kiedyś przenumerowało te stałe, build się wywali — zamiast wypuścić firmware, które błędnie etykietuje każdy restart w terenie.

## 9. Znane ograniczenia i otwarte decyzje

Rzeczy świadomie zostawione poza zakresem — nie przeoczenia, tylko wybory do podjęcia później, z podaną ceną każdego z nich.

**Brak retencji `device_state_reports`.** Sekcja co 15 minut to ~35 tys. wierszy na urządzenie rocznie; dla gminy 15-obiektowej ~0,5 mln. Nic tego nie kasuje. Zapytanie odczytu rankuje po indeksie `(device_id, section, captured_at)` w obrębie jednego urządzenia, a szuflada w UI odpytuje je co 60 s — przy rocznej historii to skanowanie kilkudziesięciu tysięcy wpisów indeksu na odpytanie. Postgres to udźwignie długo, ale nie w nieskończoność. Do rozstrzygnięcia: czy trzymać pełną historię stanu (przydatna do analizy trendu RSSI i degradacji pamięci), czy kasować po N dniach zostawiając tylko najnowszą sekcję. To decyzja produktowa, nie techniczna — historia stanu ma wartość diagnostyczną, której nikt jeszcze nie wycenił.

**Odpytywanie co 60 s przy danych zmieniających się co 15 minut.** Piętnaście razy częściej, niż odpowiedź może się zmienić. Robi to jednak jedną pożyteczną rzecz: utrzymuje etykietę wieku żywą, bo wiek jest liczony po stronie serwera. Alternatywa — liczyć wiek w przeglądarce z `captured_at` i odpytywać rzadziej — jest tańsza, ale przenosi próg `is_stale` na klienta, gdzie może rozjechać się z progiem dashboardu. Zostawione jak jest, świadomie.

**Wyścig na duplikacie nie odświeża `last_seen_at`.** Gdy dwa równoległe żądania niosą to samo `(device_id, seq)`, przegrany wpada w `TelemetryPacketAlreadyExistsError`, którego obsługa wycofuje transakcję. Nie jest to luka: żądanie, które wygrało, zapisało dokładnie ten sam dowód życia mikrosekundy wcześniej.

## 10. Weryfikacja na fizycznej płytce

Testy `native` zastępują atrapą dokładnie tę warstwę, która rozmawia ze sprzętem i siecią, więc poniższe trzeba sprawdzić na urządzeniu:

| Co sprawdzić | Na co patrzeć w logu |
|---|---|
| Pierwszy pakiet po starcie niesie sekcję `device` | `[DATA] Payload:` zawiera `"state":[{"section":"device"` |
| Backend przyjmuje pakiet z sekcją | `[LOOP] Send OK, seq=...`, w bazie wiersz w `device_state_reports` |
| `AT+CSQ` między `ensureConnected()` a `post()` nie psuje sesji modemu | brak `Send failed` po pierwszym raporcie stanu; `rssi_dbm` w payloadzie ma sensowną wartość |
| Kolejne pakiety **nie** niosą sekcji przez 15 minut | `"state"` nieobecne w `[DATA] Payload:` przez ~15 kolejnych wysyłek |
| Po 15 minutach sekcja wraca | jw., `uptime_seconds` wzrosło o ~900 |
| Nieudana wysyłka nie zjada interwału | po `[LOOP] Send failed` kolejny payload nadal zawiera `"state"` |
| `restart_reason` po watchdogu | wymuś restart watchdoga → `"restart_reason":"task_watchdog"` (albo `int_watchdog`), `restart_count` wzrasta |
| Zapełnienie bufora rośnie przy braku sieci | odłącz antenę na >2 min → `buffer_windows_used` rośnie; po >12 min `buffer_windows_dropped` > 0 |
| `Device.firmware_version` uzupełnia się samo | w UI (`DeviceDetailDrawer`) pojawia się `0.4.0` bez ręcznej edycji |
| Retransmisja po zgubionym ACK nadal liczy się jako kontakt | wymuś duplikat `seq` → odpowiedź 200 `duplicate`, a `last_seen_at` w UI się odświeża |

Poza tą listą zostają dwie rzeczy, których na płytce sprawdzić się nie da w rozsądnym czasie i które dlatego są przykryte testami natywnymi: zachowanie `uptime_seconds` po przewinięciu `millis()` (~49 dni) oraz wieloletnia kumulacja przewinięć.

Build firmware wymaga wcześniejszego wygenerowania `SensorRegistry.h` — robi to hook pre-build, ale przy pierwszym uruchomieniu po tej zmianie warto potwierdzić w logu builda linię `9 point_types, 13 error_codes, 1 state_sections`.
