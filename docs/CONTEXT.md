# Platforma Monitoringu Wodociągów — Kontekst Biznesowy

Platforma umożliwia małym gminom i lokalnym zakładom wodociągowym (ZWiK) zbieranie, przechowywanie i analizę danych z rozproszonych obiektów infrastruktury wodociągowej — przepompowni, hydroforni, stacji uzdatniania, punktów pomiarowych sieci — bez konieczności wymiany istniejącej automatyki.

## Słownik — Domeny Biznesowe

### Obiekty Infrastruktury

**Gmina (Klient)**
Jednostka samorządowa (lub niezależny zakład wodociągowy ZWiK), która zarządza infrastrukturą wodociągową i stanowi kontrahenta dla usługi.
_Unikać_: Jednostka administracyjna, samorząd, operator wody

**Obiekt wodociągowy**
Fizyczne miejsce na terenie gminy, gdzie zbieramy dane: przepompownia, hydrofornia, stacja uzdatniania, pomiar na sieci, zbiornik wyrównawczy. Każdy obiekt ma jeden gateway (urządzenie terenowe).
_Unikać_: Lokacja, punkt pomiarowy, urządzenie (urządzenie ≠ obiekt)

**Gmina pilotażowa**
Konkretna gmina, na której testujemy MVP i zbieramy pierwsze dane rzeczywiste. Nazwa i szczegóły anonimowe w dokumentacji.
_Unikać_: Klient pilotażowy, pilot, case study (termin case study używamy tylko po zakończeniu)

### Dane Pomiarowe

**Czujnik**
Urządzenie fizyczne mierzące pojedynczy parametr (temperatura, ciśnienie, chlor, mętność, poziom, praca pompy). Podłączone do gateway'a.
_Unikać_: Sensor, punkt pomiaru, kanał (kanał to reprezentacja danych, nie urządzenie)

**Kanał (pomiarowy)**
Reprezentacja logiczna czujnika w systemie platformy. Każdy kanał ma typ (temperatura, ciśnienie), jednostkę, status jakości, historię. Jeden czujnik = jeden kanał (zwykle), ale jeden czujnik może wyeksportować wiele kanałów (np. przepływomierz: przepływ chwilowy + suma).
_Unikać_: Czujnik (już to słowo), punkt danych, parameter

**Punkt pomiarowy**
W dokumentacji technicznej używane zamiennie z Kanałem — miejsce (fizyczne lub logiczne), w którym wykonywany jest pomiar. Wyjątek: w opisie Zakresu obiektów „punkt pomiarowy na sieci wodociągowej" oznacza samodzielny Obiekt (typu „pomiar na sieci”, bez przepompowni czy hydroforni) — w tym jednym przypadku odnosi się do Obiektu, nie Kanału. Kontekst zdania rozstrzyga, o które znaczenie chodzi.
_Unikać_: traktowania jako trzeciego, odrębnego od Kanału i Obiektu pojęcia

**Pomiar**
Pojedyncza wartość zarejestrowana przez czujnik w danym momencie. Zawiera wartość, czas, jednostkę, status jakości.
_Unikać_: Dane, odczyt, wartość (zbyt ogólne)

**Gateway (urządzenie terenowe)**
Mikrokontroler (ESP32) + modem LTE-M, zainstalowany na obiekcie. Odczytuje czujniki, buforuje dane, transmituje do chmury. Jeden na obiekt.
_Unikać_: RTU, modem, device, urządzenie brzegowe (edge device zbyt abstrakcyjnie)

### Model Produktu

**MVP (Minimum Viable Product)**
Faza 1 produktu: temperatura + ciśnienie, obsługa jednego obiektu, dashboard podstawowy, alarmy progowe, bufor lokalny. Testowana na gminie pilotażowej.
_Unikać_: Phase 1, core, baseline

**Phase 2 (Rozszerzenia)**
Faza 2: dodatkowe kanały (poziom zbiornika, praca pompy, jakość wody — chlor, mętność), profile urządzeń dla różnych czujników, zaawansowane reguły anomalii. Po feedback z MVP.
_Unikać_: Rozwinięcie, następna wersja, V1.1

**Profil urządzenia**
Konfiguracja zawierająca: protokół komunikacji (Modbus, 4-20 mA), mapowanie rejestrów, jednostki, skalowanie. Używana do automatycznego rozpoznania i obsługi danego czujnika/PLC bez zmian firmware'u.
_Unikać_: Szablon, konfiguracja (zbyt ogólnie), driver (implementacyjnie)

### Biznes

**Abonament (subskrypcja)**
Opłata miesięczna za dostęp do platformy (dashboard, alarmy, przechowywanie danych, SIM, serwis). Rozliczana per obiekt.
_Unikać_: Licencja, opłata, czynsz (zbyt technicznie/staroświecko)

**Wdrożenie**
Cykl prac: inwentaryzacja obiektu, montaż gateway'a, konfiguracja czujników, test danych, konfiguracja reguł alarmowych, uruchomienie produkcyjne.
_Unikać_: Instalacja (zbyt wąsko), deployment (informatycznie), implementation (zbyt formalnie)

**Partnerstwo montażowo-integracyjne**
Relacja z lokalnym elektrykiem/AKPiA, który wspomaga montaż gateway'a i czujników na terenie. W fazie MVP: brak formalnego partnerstwa, montaż wykonywany samodzielnie.
_Unikać_: Integrator (zbyt formalnie), installer (informatycznie), partner (zbyt ogólnie)

### Technologia & Infrastruktura

**Łączność (transmisja danych)**
Przesył danych z gateway'a do chmury platformy przez sieć komórkową (LTE-M, NB-IoT). Szyfrowana, asynchroniczna, z buforowaniem lokalnym w przypadku przerwy.
_Unikać_: Komunikacja, transfer, połączenie (zbyt ogólnie)

**Bufor lokalny**
Pamięć gateway'a (flash, SD card) przechowująca dane w przypadku przerwy łączności. Minimalna retencja: 72 godziny.
_Unikać_: Cache, magazyn, backup (backup to kopia bezpieczeństwa, bufor to tymczasowe przechowywanie)

**Reguła alarmowa**
Logika ewaluacji zdefiniowana dla obiektu: np. „jeśli ciśnienie < 2 bar przez 120 sekund, wygeneruj alarm krytyczny". Konfigurowana per gmina.
_Unikać_: Trigger, warunek (zbyt abstrakcyjnie), reguła (OK, ale „reguła alarmowa" bardziej precyzyjnie)

### Regulacyjne & Compliance

**Kontrola wewnętrzna (monitorowanie jakości wody)**
Obowiązek gminy: okresowe badanie jakości wody przeznaczonej do spożycia. Wymaga próbek laboratoryjnych (obowiązkowe); nasze czujniki online to wyłącznie wspierające wczesne ostrzeganie, nie zastępują kontroli.
_Unikać_: Badanie, monitoring, compliance („compliance" to szersze, „kontrola wewnętrzna" to termin z ustawy)

**NIS2 (Dyrektywa Unii Europejskiej 2022/2555)**
Europejskie wymogi cyberbezpieczeństwa dla sektorów krytycznych, w tym wody pitnej i ścieków. Wymaga od gmin: zarządzania ryzykiem, raportowania incydentów, ciągłości działania. Nasz system wspomaga poprzez read-only, szyfrowanie, logi.
_Unikać_: NIST, standard, wymóg (zbyt ogólnie)

---

## Założenia & Ograniczenia (do aktualizacji po MVP)

- **Read-only na MVP**: System nie steruje pompami, zaworami, przepustnicami — obserwuje i alarmuje. Sterowanie w Phase 2 lub później po oddzielnej analizie bezpieczeństwa.
- **Neutralność sprzętowa**: Obsługujemy najpopularniejsze interfejsy (Modbus RTU, 4-20 mA); nowe protokoły dodajemy przez profile, nie recompile.
- **Pragmatyczna integracja**: Nie zakładamy sztywnej listy obsługiwanych urządzeń. Adaptujemy się do tego, co gmina ma — jeśli się podpiąć da łatwo, robimy; jeśli skomplikowane, to odseparowujemy i dokumentujemy.
- **Długoterminowe relacje z klientem**: Nie szukamy szybkiego zysku. Nacisk na satysfakcję gminy, organiczny wzrost, wsparcie długoterminowe.

