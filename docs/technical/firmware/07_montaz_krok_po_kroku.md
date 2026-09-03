# Montaż gatewaya krok po kroku

Instrukcja dla osoby, która ma części na stole i ma to fizycznie złożyć. Kolejność kroków nie jest
przypadkowa: **każdy etap kończy się testem**, żeby nie szukać potem błędu w całości naraz.

Schemat, do którego warto zerkać przez cały czas:
[`00_przeglad.md §4`](./00_przeglad.md#4-schemat-połączeń). Numery pinów: wyłącznie
[`01_hardware.md`](./01_hardware.md) i [`Config.h`](../../../firmware/include/Config.h).

**Status: draft.** Ta instrukcja została napisana na podstawie kodu i dokumentacji producenta modułu,
**nie na podstawie przejścia przez montaż z płytką w ręku**. Kroki testowe są prawdziwe (opisują
zachowanie, które da się wyprowadzić z kodu), ale sam przebieg montażu wymaga jednorazowego
potwierdzenia w praktyce.

---

## 0. Czego potrzebujesz

| Element | Uwagi |
|---|---|
| ESP32-S3-DevKitC-1 | zapisz sobie wariant modułu z nadruku (N8R2 / N8R8 / N16R8) — będzie potrzebny przy rozbudowie |
| KAmod LTE CAT1-GNSS z A7670E-FASE | HAT na złącze 40-pin Raspberry Pi |
| Antena LTE ze złączem U.FL | **osobna od anteny GNSS** |
| Karta micro SIM (M2M) | 1,8 V lub 3,0 V, **bez PIN-u** albo z PIN-em wpisanym do `Config.h` |
| Zasilacz 5 V / min. 2 A | osobny od USB, do zasilenia modułu HAT |
| Moduł MAX31865 | sprawdź, czy ma zworkę „2/3W" |
| Czujnik PT100 3-przewodowy | |
| Przewody połączeniowe, multimetr | multimetr jest **obowiązkowy** — bez niego nie rozpoznasz par przewodów PT100 |
| Kabel USB-C do dev-kitu | do programowania i logów |

Oprogramowanie: PlatformIO (`pio`), Python 3 z pakietem `PyYAML` (potrzebny hookowi generującemu
`SensorRegistry.h` przed budowaniem).

---

## 1. Uwagi krytyczne — przeczytaj przed pierwszym podłączeniem

Pięć rzeczy, które najczęściej kończą się „nie działa i nie wiadomo dlaczego":

1. **Nie zasilaj modułu HAT z USB dev-kitu.** Modem przy nadawaniu LTE ciągnie szczytowo ok. 2 A.
   Port USB tego nie utrzyma — objawia się to resetami modemu, które wyglądają jak błąd firmware.
   Zasilanie 5 V idzie z osobnego zasilacza na piny **2 i 4** złącza 40-pin.
2. **Masa musi być wspólna.** Zasilacz 5 V, ESP32-S3 i moduł HAT muszą mieć połączone GND. Bez tego
   UART nie zadziała, nawet przy poprawnie założonych zworkach.
3. **Zworki J2 muszą być założone** — osobno dla TXD, RXD, PWK i RST. Bez zworki sygnał nie dociera
   do złącza 40-pin, mimo że GPIO po stronie ESP32 jest podłączone prawidłowo.
4. **Sprawdź zworkę J_APWK na spodzie płytki.** Steruje automatycznym włączeniem modemu przy podaniu
   zasilania. Firmware sam generuje impuls na PWRKEY — jeśli J_APWK nie jest przecięta, oba impulsy
   mogą się nałożyć.
5. **RESET jest aktywny stanem wysokim.** Na tej płytce HIGH na linii RST **trzyma modem w resecie**.
   Jeśli po złożeniu modem milczy, to pierwsza rzecz do zmierzenia na GPIO5.

---

## 2. Krok 1 — przygotowanie płytki KAmod

1. **Włóż kartę SIM** do gniazda micro SIM. Zwróć uwagę na orientację (ścięty róg wg nadruku).
2. **Podłącz antenę LTE** do złącza U.FL opisanego jako LTE. Płytka ma **dwa** złącza U.FL — drugie
   to GNSS, nieużywane przez obecne firmware. Podłączenie anteny do niewłaściwego gniazda daje
   „brak zasięgu" przy sprawnym module.
3. **Załóż zworki J2** dla wszystkich czterech sygnałów: TXD, RXD, PWK, RST.
4. **Obejrzyj J_APWK na spodzie płytki** i zanotuj stan (przecięta / nieprzecięta). Jeżeli po
   uruchomieniu modem będzie się zachowywał nieprzewidywalnie — to jest pierwszy podejrzany.

**Test:** podaj samo zasilanie 5 V (jeszcze bez ESP32) i sprawdź diodę **PWR (D5)** — powinna
świecić. Jeśli J_APWK nie jest przecięta, po chwili powinna zapalić się też **STA (D3)**, a **NET
(D4)** zacząć migać w poszukiwaniu sieci.

---

## 3. Krok 2 — masa i zasilanie

Kolejność ma znaczenie: **najpierw masa, potem zasilanie.**

1. Połącz **GND zasilacza 5 V** z dowolnym pinem GND złącza 40-pin (6, 9, 14, 20, 25, 30, 34 lub 39).
2. Połącz **GND ESP32-S3** z tą samą masą.
3. Dopiero teraz podłącz **+5 V** zasilacza do pinów **2 i 4** złącza 40-pin.

**Test:** zmierz multimetrem napięcie między pinem 2 a GND — powinno być 5 V ±5%. Zmierz napięcie
między masą ESP32 a masą HAT-a — powinno być 0 V. Wszystko inne niż 0 V oznacza, że mas nie połączono.

---

## 4. Krok 3 — UART i linie sterujące

Cztery przewody, wg [`01_hardware.md §7`](./01_hardware.md#7-a7670e-fase--moduł-kamod-lte-cat1-gnss-hat):

| ESP32-S3 | → | Pin złącza 40-pin | Sygnał |
|---|---|---|---|
| GPIO17 | → | 8 | TX ESP32 do RXD modemu |
| GPIO18 | ← | 10 | RX ESP32 od TXD modemu |
| GPIO5 | → | 12 | RESET (active-high) |
| GPIO4 | → | 7 | PWRKEY (active-high) |

**Najczęstszy błąd: zamienione TX i RX.** Jeśli po wgraniu firmware modem nie odpowiada na komendy
AT, a zasilanie jest w porządku — zamień GPIO17 i GPIO18 miejscami i spróbuj ponownie.

**Test:** wgraj firmware i obejrzyj log.

```bash
cd firmware
pio run --target upload
pio device monitor -b 115200
```

Spodziewany przebieg:

```
[INFO][BOOT] ESP32-S3 + A7670E telemetry sender
[INFO][BOOT] Powering on modem...
[INFO][MODEM] Starting UART...
[INFO][MODEM] Auto-bauding...
[INFO][MODEM] Init OK
[INFO][NET] Network connected
[INFO][NET] Signal quality: 18
[INFO][DATA] GPRS/LTE connected
[INFO][DATA] Local IP: 10.x.x.x
```

Jeśli zatrzyma się na którymkolwiek z tych kroków — tabela objawów i przyczyn jest w
[`02_modem_a7670e_communication.md §6.2`](./02_modem_a7670e_communication.md#62-scenariusze-błędów).

> **Uwaga o pierwszym uruchomieniu.** Fabrycznie nowe urządzenie **nie włączy modemu w ogóle** —
> czeka na kod aktywacyjny, którego obecne firmware nie potrafi przyjąć (usterka U-1). Zobaczysz wtedy
> tylko `Provisioning not completed — waiting for ACTIVATE <code>` i nic więcej. To nie jest błąd
> montażu. Szczegóły: [krok 7 — aktywacja urządzenia](#8-krok-7--aktywacja-urządzenia).

---

## 5. Krok 4 — MAX31865

Sześć przewodów między dev-kitem a modułem konwertera:

| ESP32-S3 | MAX31865 |
|---|---|
| GPIO11 | SDI (MOSI) |
| GPIO13 | SDO (MISO) |
| GPIO12 | CLK (SCK) |
| GPIO14 | CS |
| 3V3 | VIN |
| GND | GND |

**MAX31865 zasilaj z 3,3 V, nie z 5 V.**

Jeżeli moduł ma zworkę **„2/3W"** obok zacisków RTD — dla czujnika 3-przewodowego musi być zwarta.

---

## 6. Krok 5 — czujnik PT100

Czujnik 3-przewodowy ma dwa przewody zwarte wewnętrznie i jeden osobny. **Nie zgaduj po kolorach —
zmierz.**

1. Multimetrem w trybie pomiaru rezystancji znajdź parę przewodów o rezystancji **~0–2 Ω** — to para
   sparowana.
2. Trzeci przewód będzie miał względem każdego z tej pary ok. **100 Ω** (przy temperaturze pokojowej).

| Przewód | Zacisk MAX31865 |
|---|---|
| Sparowany #1 | F+ |
| Sparowany #2 | RTD+ |
| Pojedynczy | RTD- |

**Test:** po ponownym wgraniu firmware w logu powinno się pojawić:

```
[INFO][PT100] Initialized
[INFO][PT100] Temperature: 22.45°C
```

Odczyt powinien odpowiadać temperaturze otoczenia. Chwyć czujnik w dłoń — wartość powinna rosnąć w
ciągu kilkunastu sekund (kolejne próbki są co 15 s).

| Co widzisz | Co to znaczy |
|---|---|
| `Initialization failed!` | Brak komunikacji SPI — sprawdź cztery przewody SPI i zasilanie 3,3 V |
| `Fault 0x08` + `RTDIN- < 0.85 x Bias` | Przerwa w obwodzie RTD — najczęściej źle dobrane przewody czujnika |
| Temperatura ok. -242 °C | Jak wyżej, ale bez zgłoszonego błędu — sprawdź RTD+/RTD-/F+ |
| Stały offset kilku stopni | Rezystor odniesienia na module to 400 Ω, nie 430 Ω — zmierz go |

Pełna tabela kodów błędów: [`05_pt100_temperature_sensor.md §8`](./05_pt100_temperature_sensor.md#8-troubleshooting).

---

## 7. Krok 6 — kanał ciśnienia

**Ten krok nie istnieje.** Kanał pomiaru ciśnienia (PT-506 → pętla 4-20 mA → rezystor 136 Ω →
ADS1015) jest zaplanowany, ale **nie ma go w firmware**: nie ma klasy czujnika, sterownika ani
przypisanych pinów I²C. Podłączenie ADS1015 na tym etapie nic nie da — urządzenie go nie odczyta.

Co trzeba rozstrzygnąć, zanim ten krok da się w ogóle napisać:
[`01_hardware.md §3`](./01_hardware.md#3-ścieżka-ciśnienia--draft).

---

## 8. Krok 7 — aktywacja urządzenia

Docelowy przebieg: po pierwszym uruchomieniu urządzenie generuje numer seryjny z adresu MAC (postać
`WW-3CDC756F6DC0`), czeka na kod aktywacyjny podany przez port szeregowy, po jego przyjęciu włącza
modem, wymienia kod na tożsamość w backendzie, a następnie cyklicznie odnawia token sesji.

```
> ACTIVATE YU4N-6HGS-Y3
< ACTIVATION_CODE_ACCEPTED
```

> ⚠️ **W obecnym firmware ten krok nie zadziała.** Odczyt z portu szeregowego jest wyłączony
> (`readSerial()` jest pustą zaślepką), a metoda przyjmująca kod nie jest wołana z żadnego miejsca.
> Urządzenie zostanie na komunikacie `waiting for ACTIVATE <code>` i nigdy nie włączy modemu.
> Usterka U-1 — [`00_przeglad.md §10`](./00_przeglad.md#10-usterki-w-kodzie-znalezione-przy-uzgadnianiu-dokumentacji),
> opis protokołu do odtworzenia: [`04_device_provisioning_flow.md §3.2`](./04_device_provisioning_flow.md#32-protokół-serial).

Numer seryjny urządzenia odczytasz z logu startowego albo wyliczysz z adresu MAC modułu: prefiks
`WW-` plus 12 znaków hex adresu MAC interfejsu WiFi STA, wielkimi literami.

**Test końcowy** (dla urządzenia już zaprovisionowanego): w logu, co ok. 60 s, powinien się pojawiać
komplet:

```
[INFO][PT100] Temperature: 22.45°C     ← cztery razy, co 15 s
[INFO][DATA] Payload: {"v":2,"device_id":"WW-...",...}
[INFO][LOOP] Send OK, seq=1787497190
```

oraz **jedno mignięcie zielonej diody na GPIO48** po każdej udanej wysyłce (trzy mignięcia = błąd).

---

## 9. Krok 8 — montaż docelowy w szafie

Status: **draft** — poniższe pochodzi z planu, nie z wykonanej instalacji. Zanim to złożysz w
hydroforni, przejdź przez listę „do rozstrzygnięcia" z
[`00_przeglad.md §5`](./00_przeglad.md#5-drzewo-zasilania).

Zamiast dwóch osobnych zasilaczy (USB + 5 V) łańcuch docelowy wygląda tak:

```
230 V AC → zasilacz DIN 24 V DC → przetwornica XL4015 (24 → 5 V / 2 A) → ESP32-S3 i HAT
                                → pętla prądowa 4-20 mA czujnika ciśnienia
```

Czego ten dokument **nie rozstrzyga**, a co trzeba rozstrzygnąć przed instalacją u klienta: obudowa i
stopień ochrony IP, ochrona przepięciowa na linii zasilania i sygnałowej, separacja galwaniczna
wejść, zapas prądowy przetwornicy w szczycie nadawania, wyprowadzenie anteny poza metalową szafę.
Formalna strona (CE, deklaracja zgodności, atesty dla elementów mających kontakt z wodą pitną) to
osobny temat — zob. plan biznesowy.

---

## 10. Lista kontrolna

Do odhaczenia po złożeniu, zanim urządzenie pojedzie w teren:

- [ ] Karta SIM włożona, bez PIN-u (albo PIN wpisany do `Config.h`)
- [ ] Antena LTE w gnieździe **LTE**, nie GNSS
- [ ] Wszystkie cztery zworki J2 założone
- [ ] Stan zworki J_APWK zanotowany
- [ ] Wspólna masa: zasilacz ↔ HAT ↔ ESP32-S3, zmierzona 0 V między masami
- [ ] Zasilanie 5 V / ≥ 2 A z osobnego zasilacza na piny 2 i 4
- [ ] MAX31865 zasilany z 3,3 V, nie z 5 V
- [ ] Zworka „2/3W" na module MAX31865 zwarta
- [ ] Rezystor odniesienia MAX31865 zmierzony i zgodny z `REF_RESISTOR_OHMS` (430 Ω)
- [ ] Para przewodów PT100 wyznaczona multimetrem, nie po kolorach
- [ ] Log startowy dochodzi do `[DATA] Local IP: ...`
- [ ] Log pokazuje `[PT100] Temperature: ...` co 15 s
- [ ] Log pokazuje `[LOOP] Send OK` co ok. 60 s
- [ ] Zielona dioda miga raz po udanej wysyłce

---

## 11. Gdy nie działa

| Warstwa | Gdzie szukać |
|---|---|
| Modem, sieć, brak IP | [`02_modem_a7670e_communication.md §6`](./02_modem_a7670e_communication.md#6-diagnostyka-i-troubleshooting) |
| Restarty, zawieszenia, watchdog | [`03_esp32_reset_and_recovery.md §7`](./03_esp32_reset_and_recovery.md#7-troubleshooting) |
| Aktywacja, token, 401/409 | [`04_device_provisioning_flow.md §6`](./04_device_provisioning_flow.md#6-znane-problemy-i-obejścia) |
| Temperatura, kody błędów MAX31865 | [`05_pt100_temperature_sensor.md §8`](./05_pt100_temperature_sensor.md#8-troubleshooting) |
| Dane docierają nieregularnie albo z lukami | [`00_przeglad.md §8.1`](./00_przeglad.md#81-gdzie-dane-mogą-zginąć) |
| Objaw wygląda na błąd firmware, nie montażu | [`00_przeglad.md §10`](./00_przeglad.md#10-usterki-w-kodzie-znalezione-przy-uzgadnianiu-dokumentacji) |
