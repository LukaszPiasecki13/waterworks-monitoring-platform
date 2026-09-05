# Mapa rynku — wszyscy gracze na polskim rynku, bezpośredni vs. pozostali

**Data weryfikacji źródeł: 5 września 2026.**

Dokument jest **rozszerzeniem, nie powtórzeniem** [§5.2 planu biznesowego](./01_plan_biznesowy.md#52-analiza-konkurencji). Tam jest głębia (9 pogłębionych profili), tutaj **szerokość, jednoznaczny werdykt klasyfikacyjny i dowód rynkowy** — kto faktycznie wygrywa postępowania w małych gminach i za ile.

---

## 1. Odpowiedź w jednym akapicie

Na polskim rynku zidentyfikowano **57 pozycji** w sześciu kategoriach z [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku). Po zastosowaniu testu opartego na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam) **15 z nich to konkurenci bezpośredni**, 36 to konkurenci pośredni, 5 wymaga obserwacji, 1 pozostaje nierozstrzygnięty. Najważniejsze ustalenie nie jest jednak liczbą — jest nim odpowiedź na pytanie, **kto naprawdę wygrywa w małych gminach**. Przegląd 72 postępowań publicznych z lat 2021–2026 (51 zakończonych umową) pokazał trzy rzeczy:

1. **Hydro-Partner Sp. z o.o. z Leszna jest konkurentem bezpośrednim o najbliższym nam modelu na całym rynku.** Ma hostowaną platformę webową (HydroNET Web 6, osobna subdomena na gminę), własne call center 7:00–22:00 przez 365 dni w roku z **dodatkowo płatnym monitorowaniem newralgicznych obiektów**, i wygrywa małe postępowania gminne — w tym jedno za **55 680 zł** (Siechnice, 2025: retrofit monitoringu do *istniejących* szaf sterowniczych, bez ich wymiany). To jest nasz produkt, nasz model i nasz przedział cenowy.
2. **W przetargu gmina płaci za obiekt z szafą sterowniczą i wizualizacją 90–400 tys. zł, a za sam retrofit monitoringu 55–110 tys. zł** — podczas gdy [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody) zakłada 2,9–8,3 tys. zł na obiekt. To nie znaczy, że plan jest błędny; to znaczy, że **nie startujemy w tym samym zakupie** — patrz [§5.4](#54-ile-gmina-naprawdę-płaci) i wniosek o progu 130 000 zł w [§5.6](#56-najważniejsza-konsekwencja-handlowa--próg-130-000-zł).
3. **To, co gmina nazywa „systemem monitoringu sieci wodociągowej", bardzo często okazuje się wymianą wodomierzy z nakładkami radiowymi (AMI), a nie monitoringiem obiektu** — 12 z 51 rozstrzygniętych postępowań, czyli prawie co czwarte. Wygrywają je Orange Polska, Metering Anna Moder, Diehl Metering, FILA i Sensus — podmioty pośrednie produktowo, ale **zajmujące pozycję „monitoring" w budżecie gminy**.

Realna konkurencja o małą gminę nie przychodzi od dużych platform smart water — **żadna z ośmiu pozycji w kategorii K3 nie przeszła testu na konkurenta bezpośredniego**. Przychodzi od **producentów sprzętu i szaf, którzy dorzucają do niego monitoring**, a w przetargach dodatkowo od **dostawców AMI i długiego ogona lokalnych firm elektrycznych**.

---

## 2. Metoda i kryterium klasyfikacji

### 2.1. Źródła

| Źródło | Co z niego pochodzi |
|---|---|
| **Biuletyn Zamówień Publicznych** (publiczne API portalu e-Zamówienia) | 72 postępowania monitoringowo-telemetryczne wod-kan 2021–2026: liczba i ceny wszystkich ofert, nazwa i NIP wykonawcy, data umowy, współfinansowanie UE, kod CPV. Wyszukiwanie po frazach w przedmiocie zamówienia (`telemetr`, `monitoring`, `monitorowania`, `wizualizac`, `SCADA`, `przepompown`, `hydrofor`, `uzdatnian`) i po kodach CPV rodziny telemetrycznej (32441000-6, 32441100-7, 32441200-8, 32441300-9), z osobnym przebiegiem dla małopolskiego i podkarpackiego. Zbiór danych: [`assets/06_przetargi_bzp_2021_2026.csv`](./assets/06_przetargi_bzp_2021_2026.csv) |
| **Wykaz podatników VAT Ministerstwa Finansów** | Weryfikacja rejestrowa podmiotów z tabeli — NIP, KRS, REGON, status, adres ([§6](#6-weryfikacja-rejestrowa)) |
| **Wykaz członków IGWP** ([igwp.org.pl](https://www.igwp.org.pl/o-nas/czlonkostwo/wykaz-czlonkow/), stan 23.07.2026) | 471 członków zwyczajnych i 63 wspierających — najbliższy istniejący spis dostawców branży ([§7](#7-członkowie-wspierający-igwp)) |
| **Katalog wystawców targów WOD-KAN** | 22 wystawców w grupie „Urządzenia pomiarowe stacji, technika pomiarów, regulacji i analiz" |
| **Strony producentów** | Zakres oferty, ceny publiczne, potwierdzenie obecności na rynku polskim |

Nie kontaktowano się z żadnym podmiotem: bez zapytań ofertowych, bez rejestracji na wersje próbne, bez pozyskiwania cenników pod pozorem zainteresowania zakupem.

Kolumna **Pewność** w tabeli: `wysoka` = ustalenie wynika wprost z treści strony dostawcy albo z dokumentu postępowania; `średnia` = ze źródła trzeciego (portal branżowy, katalog); `przypuszczenie` = wywnioskowane pośrednio. **Segment docelowy oznaczony `przypuszczenie` nie nadaje się jako argument w rozmowie z klientem bez wcześniejszego sprawdzenia.**

### 2.2. Zasada wpisu do mapy

Do tabeli w [§3](#3-pełny-spis--tabela-zbiorcza) trafia podmiot, który ma **powtarzalną, publicznie opisaną ofertę** dotyczącą monitoringu, telemetrii lub automatyki wod-kan. Jednorazowi wykonawcy wyłonieni w przetargach, bez publicznie opisanej oferty produktowej, są w tabeli w [§5.2](#52-rozstrzygnięte-postępowania) — mapa pozostaje mapą dostawców, a nie listą wszystkich firm elektrycznych w Polsce.

Kategoria **K5 (integratorzy AKPiA) jest z natury próbką, nie spisem** — to setki lokalnych firm bez widocznej działalności marketingowej. Trzynaście pozycji dobrano tak, żeby pokryć różne modele działania i regiony, w tym Intelcon z Nowego Sącza jako przykład z województwa pierwszego klienta.

### 2.3. Test klasyfikacyjny — kryterium, nie wrażenie

Etykietę nadaje **trzypytaniowy test** oparty wprost na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam) (target: gminy 1000–20000 mieszkańców, 5–15 rozproszonych obiektów; nie target: duże miasta, krajowi operatorzy z gotowym SCADA, gminy z <3 obiektami) i na modelu przychodowym z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody).

| # | Pytanie testowe |
|---|---|
| **T1 — produkt** | Czy podmiot sprzedaje **gotowe rozwiązanie monitoringu obiektu**, które mała gmina może kupić bez projektu SCADA i bez prac inżynierskich na miarę? |
| **T2 — rząd wielkości ceny** | Czy koszt na obiekt mieści się w **kilku–kilkunastu tysiącach złotych** jednorazowo (a nie w setkach tysięcy za projekt dla całej sieci)? |
| **T3 — dowód obsługi segmentu** | Czy istnieje **publiczny dowód**, że podmiot obsługuje klientów tej wielkości — referencje z małych gmin, materiały kierowane do gmin, rozstrzygnięte postępowania? |

- **🔴 Bezpośredni konkurent** — T1, T2 i T3 na „tak".
- **🟡 Konkurent pośredni / sąsiedni segment** — co najmniej jedno „nie", **bez** widocznej zdolności lub chęci zmiany. Kolumna **Dlaczego** wskazuje, **które** pytanie zawodzi.
- **🔵 Do obserwacji** — dziś zawodzi T1, T2 lub T3, ale podmiot ma produkt, kanał sprzedaży i markę, żeby to zmienić niewielkim kosztem. Kolumna **Dlaczego** mówi, **co konkretnie musiałoby się stać**.
- **⚪ Nieustalone** — publiczne informacje nie wystarczają do rozstrzygnięcia; nie zgadujemy.

Tam, gdzie podmiot wystąpił w przetargu, T2 ocenia się po **realnej cenie kontraktowej** ([§5.4](#54-ile-gmina-naprawdę-płaci)), a nie po modelu sprzedaży.

Ważna uwaga do odczytu: **„pośredni" nie znaczy „nieszkodliwy"**. Integrator AKPiA nie konkuruje z nami produktowo, ale gdy gmina zapyta go o monitoring, dostanie ofertę projektową — i to my musimy umieć wytłumaczyć różnicę. Klasyfikacja mówi o **rywalizacji o ten sam typ zakupu**, nie o tym, kogo można zignorować.

---

## 3. Pełny spis — tabela zbiorcza

Kategorie wg [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku): **K1** chmurowa SCADA abonamentowa · **K2** telemetria przemysłowa i RTU · **K3** kompleksowe smart water · **K4** producenci pomp i przepompowni · **K5** integratorzy AKPiA · **K6** wyspecjalizowane urządzenia IoT.
Model biznesowy: **AB** abonament/SaaS · **CAPEX** sprzedaż sprzętu · **PROJ** wdrożenie projektowe · **USL** usługi.
Kolumna **Rejestr**: dane z Wykazu podatników VAT MF na 5.09.2026; „—" oznacza, że podmiotu nie weryfikowano rejestrowo.

| # | Podmiot | Kat. | Segment docelowy | Model | Klasyfikacja | Dlaczego (który test) | Rejestr | Źródło | Pewność |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **UniCloud / Unitronics / Elmark Automatyka** — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K1 | małe gminy i obiekty wod-kan, jawnie adresowane | AB + CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — produkt wprost dla małych gmin, **jawna cena 1–3 tys. zł/rok za obiekt**, >50 lokalizacji w PL | — | [smart.elmark.com.pl](https://smart.elmark.com.pl/uni/umc/branze/wod-kan), [blog: monitoring SUW i przepompowni](https://www.elmark.com.pl/blog/monitoring-stacji-uzdatniania-wody-i-przepompowni-dlaczego-to-dzis-koniecznosc) | wysoka |
| 2 | **Inwap Sp. z o.o.** (monitoring WWW/SMS, chmura PIK-on) | K1 | przepompownie i obiekty rozproszone, małe podmioty | AB + CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — gotowy monitoring GSM/GPRS z podglądem w przeglądarce, sprzedawany na obiekt | czynny, NIP 7470006021, KRS 0000135661 | [inwap.pl](https://inwap.pl/produkty/monitoring-www-sms-zdalna-zdalne-gsm-gprs.html) | średnia |
| 3 | **AT SYSTEMS Sp. z o.o.** (systemy monitoringu GSM/GPRS) | K1 | przepompownie, zbiorniki, obiekty komunalne | CAPEX + USL | 🔴 bezpośredni | T1✓T2✓T3✓ — zestaw montowany w istniejącej szafie, alarmy SMS/e-mail, dostęp przez przeglądarkę | czynny, NIP 6040155396, KRS 0000401698, Gdańsk | [atsystems.pl](https://atsystems.pl/systemy-monitoringu-gsm-gprs) | średnia |
| 4 | **Endress+Hauser Polska** (Netilion Water Network Insights) | K1 | przedsiębiorstwa wod-kan średnie i duże | AB + CAPEX | 🔵 do obserwacji | **T2✗** — cena aparatury procesowej poza budżetem małej gminy. *Co musiałoby się stać:* pakiet startowy „czujnik + chmura" poniżej ~10 tys. zł na obiekt — mają już chmurę, 12 biur w Polsce i status członka wspierającego IGWP | — | [pl.endress.com](https://www.pl.endress.com/pl/przemysl/rozwiazania-dla-procesow/system-zarzadzania-siecia-wodociagowa) | wysoka |
| 5 | **Vispena** (zdalny monitoring oczyszczalni, brama InHand + chmura) | K1 | oczyszczalnie i instalacje przemysłowe | PROJ + USL | 🟡 pośredni | **T1✗** — wdrożenie projektowe na konkretnej instalacji, nie produkt z półki. Vispena jest marką, nie odrębnym podmiotem | czynny jako STOVARIS Sp. z o.o., NIP 5242877169 | [vispena.pl](https://vispena.pl/zdalny-monitoring-oczyszczalni-sciekow/) | średnia |
| 6 | **JUMO** (smartWARE SCADA w chmurze dla wodociągów) | K1 | zakłady wodociągowe, głównie warstwa procesowa | CAPEX + AB | 🟡 pośredni | **T1✗** (przypuszczenie) — sprzedaje aparaturę i oprogramowanie do zbudowania systemu, nie usługę monitoringu obiektu | — | [jumo.group — blog](https://www.jumo.group/pl/pl/about-us/blog/scada-system-in-water-utilities) | przypuszczenie |
| 7 | **Inventia** (MT-101/MT-102, DataPortal) — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K2 | przepompownie w całej Polsce; >6000 wdrożeń modułów MT-101 | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — moduł zastępuje sterownik w szafie, platforma DataPortal w abonamencie, skala wdrożeń nie do podważenia | czynny, NIP 9512017534 | [inventia.pl/wod-kan](https://www.inventia.pl/wod-kan/), [automatykab2b — 6000 przepompowni](https://automatykab2b.pl/prezentacje/41761-ponad-6000-przepompowni-wykorzystuje-moduly-telemetryczne-inventia-mt-101) | wysoka |
| 8 | **PM Ecology Sp. z o.o.** (Aqua Logger Compact / RDR / HS / FLOW) | K2 | punkty pomiarowe sieci wod-kan, obiekty bez zasilania | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — gotowy rejestrator bateryjny z GSM sprzedawany na sztuki, integracja ze SCADA i alarmy SMS | czynny, NIP 5862278374, KRS 0000427907, Gdańsk | [pmecology.com](https://www.pmecology.com/aplikacja/woda-wodociagowa/) | wysoka |
| 9 | **PLUM Sp. z o.o.** (MacR6, MacR6 N, MacIQ WM) | K2 | opomiarowanie rozliczeniowe i bilansowanie sieci | CAPEX | 🟡 pośredni | **T1✗** — rozwiązuje odczyt wodomierza i bilans wody, nie stan techniczny obiektu | czynny, NIP 9661427390 | [plum.pl](https://plum.pl/en/automatingwatermeterreading/) | wysoka |
| 10 | **Teletrans** (moduły telemetryczne przewodowe i radiowe, RMZ) | K2 | integratorzy i producenci szaf — sprzedaż komponentu | CAPEX | 🟡 pośredni | **T1✗** — sprzedaje komponent do zabudowy, gmina nie jest jego klientem końcowym | — | [teletrans.com.pl](https://teletrans.com.pl/index.php?id=Modu%C5%82y+telemetryczne%2C16) | średnia |
| 11 | **Ovarro** (XiLog 4G, Primeweb/Atrium) — w PL przez **RD Tech** | K2 | operatorzy sieci; monitoring strat i ciśnienia | CAPEX + AB | 🟡 pośredni | **T2✗** — rejestrator wielokanałowy z platformą analityczną wyceniany dla operatorów sieci, sprzedaż przez dystrybutora | — | [rdtech.pl — XiLog 4G](https://www.rdtech.pl/xilog-4g/) | wysoka |
| 12 | **Aksel Sp. z o.o.** (Rybnik) | K2 | wodociągi — łączność radiowa Motorola DMR/TETRA + rejestrator ciśnienia RESUD-30 | CAPEX + USL | 🟡 pośredni | **T1✗** — podstawą oferty jest profesjonalna łączność radiowa i oprogramowanie dyspozytorskie; dla wodociągów oferuje **jeden** produkt pomiarowy (rejestrator ciśnienia), nie system monitoringu obiektu | czynny, NIP 6422635416, KRS 0000107942; członek wspierający IGWP | [aksel.com.pl — rozwiązania dla wodociągów](https://aksel.com.pl/pl/produkty/rozwiazania-dla-wodociagow) | wysoka |
| 13 | **SebaKMT / Sewerin** (loggery szumu i ciśnienia, przez dystrybutorów PL) | K2 | służby eksploatacyjne wodociągów — lokalizacja wycieków | CAPEX + USL | 🟡 pośredni | **T1✗** — narzędzie do jednorazowej lokalizacji wycieku, nie stały monitoring obiektu | — | [sebakmt.com](https://sebakmt.com/en-us/), [przeciek24.com](https://przeciek24.com/loggery/) | średnia |
| 14 | **Złote Runo Sp. z o.o.** (Warszawa) | K2 | wodociągi miejskie i gminne — dostawa i wymiana modułów telemetrycznych | CAPEX + PROJ | 🟡 pośredni | **T1✗** — realizuje dostawę i konfigurację modułów telemetrycznych w istniejącej infrastrukturze zamawiającego, nie sprzedaje własnej platformy. **Ale ma dowód segmentu:** wygrał Radom (589 502 zł, 2025) i Płużnicę (2022, w konsorcjum z Metrologiem) | czynny, NIP 7010220422, KRS 0000348491; członek wspierający IGWP | [2025/BZP 00611968/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2025%2FBZP%2000611968%2F01) | wysoka |
| 15 | **AquaRD Sp. z o.o.** (CellBOX, HydraNET, AquaGIS, SCADA) — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K3 | przedsiębiorstwa wodociągowe miast powiatowych i większe | PROJ + CAPEX | 🟡 pośredni | **T2✗ T3✗** — pakiet SCADA + GIS + model hydrauliczny w modelu projektowym (Dębica: docelowo 16 punktów pomiarowych). **Najwyższa wśród pośrednich zdolność zejścia w dół** — ma własne urządzenia CellBOX µH sprzedawane pojedynczo | czynny, NIP 5252262044, KRS 0000159597; członek wspierający IGWP | [aquard.pl](https://aquard.pl/), [wdrożenie w Dębicy](https://www.wodociagi.debickie.pl/2023/02/09/inteligentny-systemu-zarzadzania-siecia-wodociagowa-i-kanalizacyjna-wdrozony/) | wysoka |
| 16 | **AIUT** (WaterPrime; systemy zdalnego odczytu LoRa) — WaterPrime w [§5.2.4](./01_plan_biznesowy.md#524-konkurenci-w-obszarze-monitoringu-sieci-i-strat-wody) | K3 | duże miasta i operatorzy z modelem hydraulicznym | PROJ + AB | 🟡 pośredni | **T2✗ T3✗** — wymaga opomiarowania, audytu i modelu hydraulicznego; gmina z 10 obiektami nie ma czego analizować | — (członek wspierający IGWP) | [waterprime.eu](https://waterprime.eu/) | wysoka |
| 17 | **Future Processing** (SmartFlow, z MPWiK Wrocław) | K3 | duże przedsiębiorstwa wodociągowe; analityka strat w strefach DMA | AB + PROJ | 🟡 pośredni | **T3✗** — produkt zbudowany dla i z dużym MPWiK (~100 urządzeń, kilkadziesiąt stref); mała gmina nie ma na czym go uruchomić | — (członek wspierający IGWP) | [MPWiK Wrocław — SmartFlow](https://www.mpwik.wroc.pl/pracuj-z-nami/projekty/smartflow/) | wysoka |
| 18 | **Orange Polska** (Smart Water) | K3 | **gminy, miasta i ZWiK — jawnie adresowane**; >40 tys. urządzeń w >30 miejscowościach | AB + PROJ | 🔵 do obserwacji | **T1✗, ale T3 udowodnione twardo** — wygrał dwa postępowania gminne: Maszewo 759 866 zł (2024) i Jordanów 323 955 zł (2025, małopolskie), oba na **zdalny odczyt wodomierzy**, nie monitoring obiektu. *Co musiałoby się stać:* dołożenie kanałów procesowych (ciśnienie, poziom, praca pompy) do oferty, którą już sprzedaje gminom. **Najwyższy priorytet obserwacji** | — | [orange.pl — Smart Water](https://www.orange.pl/duze-firmy/smart-water); [2025/BZP 00148146/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2025%2FBZP%2000148146%2F01) | wysoka |
| 19 | **T-Mobile Polska** (IoT / NB-IoT dla wod-kan) | K3 | przedsiębiorstwa wodociągowe; opomiarowanie stacjonarne | AB | 🔵 do obserwacji | **T1✗** — jak wyżej, dodatkowo bez własnej warstwy aplikacyjnej dla wod-kan. *Co musiałoby się stać:* przejęcie lub partnerstwo z dostawcą platformy obiektowej | — | [T-Mobile — case study PWiK Kutno](https://biznes.t-mobile.pl/pl/case-study/przedsiebiorstwo-wodociagow-i-kanalizacji-w-kutnie) | wysoka |
| 20 | **Veolia Woda Polska** | K3 | duzi operatorzy i miasta, w których Veolia zarządza siecią | USL + PROJ | 🟡 pośredni | **T3✗** — model operatorski dla dużych miast; nie sprzedaje produktu małej gminie | — (Veolia Energia Polska: członek wspierający IGWP) | [wodatomy.pl](https://wodatomy.pl/strefa-wiedzy/veolia-woda-polska-dzialalnosc/nowe-oblicze-uslug-dla-sektora-wodnego/) | średnia |
| 21 | **SUEZ Polska** (urządzenia CellBOX) | K3 | przedsiębiorstwa wodociągowe średnie i duże | PROJ + CAPEX | 🟡 pośredni | **T2✗ T3✗** — sprzedaż w ramach większych kontraktów operatorskich i modernizacyjnych | — | [suez.com — CellBOX](https://www.suez.com/pl-pl/polska/inteligentne-rozwiazania/urzadzenia-cellbox) | średnia |
| 22 | **GlobTree** (GlobeOMS — chmura telemetryczna, nakładki) | K3 | wodociągi i zarządcy mediów; wejście „od jednego urządzenia" | AB + CAPEX | 🔵 do obserwacji | **T1✗** — chmura do opomiarowania mediów, nie do stanu obiektu. *Co musiałoby się stać:* dołożenie wejść procesowych do istniejącej chmury; próg wejścia „od jednej sztuki" już mają | czynny, NIP 7393679238 | [globtree.pl](https://globtree.pl/telemetria-korzysci-ktorych-szukasz/) | średnia |
| 23 | **Hydro-Vacuum S.A.** — profil w [§5.2.3](./01_plan_biznesowy.md#523-konkurenci-związani-z-producentami-pomp-i-szaf) | K4 | gminy kupujące pompy i tłocznie tego producenta | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — monitoring wchodzi razem z pompą, **więc gmina nie podejmuje osobnej decyzji zakupowej i nie ma momentu na porównanie ofert** | — (członek wspierający IGWP) | [hydro-vacuum.com.pl — monitoring](https://www.hydro-vacuum.com.pl/monitoring.php) | wysoka |
| 24 | **Metalchem-Warszawa** (MRT-GSM, MRM-GPRS) — profil w [§5.2.3](./01_plan_biznesowy.md#523-konkurenci-związani-z-producentami-pomp-i-szaf) | K4 | gminy z przepompowniami i rozdzielnicami tego producenta | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — jak wyżej; wariant SMS obniża próg cenowy poniżej naszego | — | [metalchemsa.com.pl](https://www.metalchemsa.com.pl/monitoring-przepompowni/) | wysoka |
| 25 | **Firma „Bartosz" Sp.j. Bujwicki, Sobiech** (Białystok) | K4 | obiekty wod-kan; **deklarowana zgodność z urządzeniami innych producentów** | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — deklaruje pracę z cudzym sprzętem, więc nie jest ograniczony do własnych obiektów; to atakuje wprost naszą przewagę „neutralności sprzętowej" | czynny, NIP 5420203646, KRS 0000015893 | [instalacjebudowlane.pl — systemy GSM/GPRS Bartosz](https://www.instalacjebudowlane.pl/9333-26-76-systemy-monitorowania-gsm-gprs--zdalny-nadzor-nad-obiektami-i-instalacjami.html) | średnia |
| 26 | **Wilo Polska** (Wilo-Nexos, Nexos NET Intelligence) | K4 | użytkownicy pompowni i tłoczni Wilo, w tym gminne | CAPEX + AB | 🔴 bezpośredni *(w obrębie własnego sprzętu)* | T1✓T2✓T3✓ — monitoring sprzedawany jako **usługa serwisowa dokupywana do pompowni**, więc trafia w ten sam budżet eksploatacyjny. Ograniczenie: tylko obiekty z pompami Wilo | — (członek wspierający IGWP) | [wilo.com — monitoring pompowni](https://wilo.com/pl/pl/Serwis/Oferta-serwisowa/Monitoring-pompowni-t%C5%82oczni-%C5%9Bciek%C3%B3w-i-zestaw%C3%B3w-pompowych/) | wysoka |
| 27 | **Grundfos Pompy Sp. z o.o.** (Grundfos Remote Management) | K4 | użytkownicy pomp Grundfos, w tym gminne pompownie i SUW | CAPEX + AB | 🔴 bezpośredni *(w obrębie własnego sprzętu)* | T1✓T2✓T3✓ — polskojęzyczna oferta GRM opisana wprost jako **„alternatywa dla systemów SCADA"** dla użytkowników niepotrzebujących automatyzacji procesu, ze **stałą niską opłatą roczną** obejmującą hosting i wsparcie; zarządzanie przez przeglądarkę, alarmy na telefon | — (Grundfos Pompy Sp. z o.o.: członek wspierający IGWP) | [product-selection.grundfos.com/pl — Zdalne zarządzanie](https://product-selection.grundfos.com/pl/products/grundfos-remote-management) | wysoka |
| 28 | **KSB Pompy i Armatura** (KSB Guard) | K4 | użytkownicy pomp KSB; nadzór stanu agregatu | CAPEX + AB | 🟡 pośredni | **T1✗** — KSB Guard mierzy **drgania i temperaturę pompy** (czujnik → moduł nadawczy → bramka → chmura KSB, aktualizacja cogodzinna). To diagnostyka stanu maszyny, nie monitoring stanu obiektu (poziom, ciśnienie, zalanie, otwarcie włazu) | — | [ksb.com/pl-pl — KSB Guard](https://www.ksb.com/pl-pl/uslugi-serwis/obsluga/kontrola-agregatow-pompowych) | wysoka |
| 29 | **Hydro-Partner Sp. z o.o.** (Leszno) | K4 | gminy i ZWiK — szafy sterownicze, monitoring i wizualizacja obiektów wod-kan | CAPEX + AB + USL | 🔴 **bezpośredni** | T1✓T2✓T3✓ — **hostowana platforma HydroNET Web 6** z osobną instancją na gminę (np. `elk.hydronetweb.pl`), **call center 7:00–22:00 przez 365 dni w roku** z dopłatą za „monitorowanie newralgicznych obiektów", cztery wygrane postępowania gminne w 2025 r., w tym trzy monitoringowo-automatykowe (55,7 / 227,4 / 398,4 tys. zł). Najbliższy nam model biznesowy na całym rynku | czynny, NIP 6972067331, KRS 0000026745, Leszno | [hydro-partner.pl — monitoring](https://hydro-partner.pl/automatyka-2/monitoring/), [call center](https://hydro-partner.pl/uslugi-2/call-center/), [HydroNET Web 6](https://elk.hydronetweb.pl/auth/contact) | wysoka |
| 30 | **Ecol-Unicon** (Bumerang SMART) | K4 | zarządcy wód opadowych, retencji i przepompowni — głównie miasta | PROJ + AB | 🟡 pośredni | **T2✗ T3✗** — celuje w retencję i wody opadowe w miastach, skala projektowa; sterowanie, nie tylko obserwacja | — (członek wspierający IGWP) | [ecol-unicon.com](https://ecol-unicon.com/blog/inteligentne-monitorowanie-sieci-wodno-kanalizacyjnych/) | wysoka |
| 31 | **Xylem Poland** (systemy monitorujące, ekosystem Flygt) | K4 | większe przepompownie i obiekty z pompami Xylem | CAPEX + PROJ | 🟡 pośredni | **T2✗ T3✗** — monitoring przy pompowniach klasy miejskiej; brak oferty skrojonej na obiekt małej gminy (inaczej niż Wilo i Grundfos). Spółka grupy, SENSUS Polska, wygrała gminne postępowanie w Tomicach (295 242 zł) — ale na **odczyt urządzeń pomiarowych**, nie monitoring obiektu | — | [xylem.com — systemy monitorujące](https://www.xylem.com/pl-pl/products-services/pumps-packaged-pump-systems/monitoring-control-equipment/monitoring--supervision/monitoring-systems/) | wysoka |
| 32 | **Wobet-Hydret Sp.j. Cichecki** (przepompownia z modułem GSM) | K4 | obiekty przydomowe i małe przepompownie | CAPEX | 🟡 pośredni | **T3✗** — moduł GSM przy obiektach przydomowych; nie obsługuje sieci obiektów gminnych | czynny, NIP 7322066451, KRS 0000301666 | [wobet-hydret.pl](https://www.wobet-hydret.pl/blog/dobre-rozwiazanie-przepompownia-z-modulem-gsm) | średnia |
| 33 | **METROLOG Sp. z o.o.** (Czarnków) | K4 | gminy modernizujące SUW — technologia + automatyka + monitoring | PROJ + CAPEX | 🟡 pośredni | **T1✗ T2✗** — wygrywa **modernizacje całych SUW** z monitoringiem jako elementem: Kobylec 3 687 540 zł i Potulice 3 608 820 zł (2023), Łekno 4 548 540 zł (2024), Płużnica 316 083 zł (2023) i 228 631 zł (2022, w konsorcjum ze Złotym Runem). Pięć wygranych, łącznie ~12,4 mln zł — rząd wielkości o dwie klasy wyżej niż nasz | czynny, NIP 7631861838, KRS 0000071593 | [2024/BZP 00428976/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2024%2FBZP%2000428976%2F01) | wysoka |
| 34 | **NASUS** — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K5 | wodociągi, energetyka, ciepłownictwo — wdrożenia projektowe | PROJ + USL | 🟡 pośredni | **T1✗** — model projektowy, brak produktu z cennikiem | — | [nasus.pl](http://www.nasus.pl/index.php) | wysoka |
| 35 | **MEDAS Sp. z o.o.** (Mikołów) | K5 | SUW, oczyszczalnie, przepompownie — projektowo | PROJ | 🟡 pośredni | **T1✗ T2✗** — potwierdzone przetargiem: wizualizacja i zdalne sterowanie **jednego** ujęcia wody w Nowym Targu za **242 015 zł** (2023, małopolskie). To cena projektu na jeden obiekt, nie produktu | czynny, NIP 6340135162, KRS 0000124736 | [medas.com.pl](https://medas.com.pl/), [2023/BZP 00050009/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2023%2FBZP%2000050009%2F01) | wysoka |
| 36 | **Hartimex Sp. z o.o.** | K5 | oczyszczalnie, przepompownie, SUW — PLC/HMI/SCADA, prefabrykacja szaf | PROJ | 🟡 pośredni | **T1✗** — model projektowy | czynny, NIP 5371345003, KRS 0000427301 | [hartimex.pl](https://hartimex.pl/) | średnia |
| 37 | **JR Technika s.c.** | K5 | stacje uzdatniania wody — szafy sterownicze, PLC | PROJ | 🟡 pośredni | **T1✗** — model projektowy | czynny, NIP 1182090882 (spółka cywilna) | [jrtechnika.pl](https://jrtechnika.pl/pages/automatyzacja.html) | średnia |
| 38 | **Intelcon** (Nowy Sącz) | K5 | AKPiA dla SUW i oczyszczalni — **region małopolski** | PROJ | 🟡 pośredni | **T1✗** — model projektowy. **Ale: działa w województwie pierwszego klienta** — równie prawdopodobny partner montażowy co konkurent (patrz „partnerstwo montażowo-integracyjne" w [CONTEXT.md](./CONTEXT.md)) | — | [intelcon.pl — AKPiA](https://intelcon.pl/akpia/) | średnia |
| 39 | **PiA-ZAP Sp. z o.o.** | K5 | modernizacje AKPiA SUW, w tym wątek cyberbezpieczeństwa | PROJ | 🟡 pośredni | **T1✗** — model projektowy; wyróżnia się kompetencją cyber, istotną przy NIS2 | czynny, NIP 7160017869, KRS 0000006759 | [piazap.com.pl — case study SUW Sekuła](https://piazap.com.pl/2025/12/05/modernizacja-akpia-suw-sekula-case-study/) | średnia |
| 40 | **EkoWodrol Sp. z o.o.** (Koszalin) | K5 | obiekty wod-kan — automatyka w ramach większych realizacji | PROJ | 🟡 pośredni | **T1✗** — automatyka jako część większego kontraktu budowlanego | czynny, NIP 6690500171, KRS 0000097981 | [ekowodrol.pl](https://ekowodrol.pl/uslugi/automatyka/) | średnia |
| 41 | **AMEplus Sp. z o.o.** | K5 | obiekty hydrotechniczne i przemysłowe | PROJ | 🟡 pośredni | **T1✗** — model projektowy | czynny, NIP 6312309466 | [ameplus.pl](https://www.ameplus.pl/hydrotechnical-objects/) | średnia |
| 42 | **Metria** (działalność jednoosobowa) | K5 | monitoring obiektów wodno-kanalizacyjnych — projekty systemów | PROJ | 🟡 pośredni | **T1✗** — model projektowy, realizowany przez jednoosobową działalność; istotne przy ocenie zdolności do obsługi floty obiektów | czynny, NIP 7010384804 (osoba fizyczna) | [metria.pl — monitoring](https://metria.pl/automatyka/monitoring/) | średnia |
| 43 | **APS** | K5 | monitoring parametrów technologicznych przepompowni i wodociągów | PROJ | 🟡 pośredni | **T1✗** — realizacje na zamówienie (m.in. dla wodociągów Łodzi) | — | [AutomatykaOnline](https://automatykaonline.pl/Aplikacje/Wod-Kan/System-monitoringu-dla-przepompowni-i-wodociagow) | średnia |
| 44 | **Sauka Baj** | K5 | systemy telemetryczne i dyspozytorskie, studnie głębinowe | PROJ | 🟡 pośredni | **T1✗** — kompleksy dyspozytorskie budowane na zamówienie | — | [saukabaj.pl](https://saukabaj.pl/systemy-dyspozytorskie-telemetryczne) | średnia |
| 45 | **Tech-Pomp Serwis Sp. z o.o.** | K5 | AKPiA przy obiektach pompowych | PROJ + USL | 🟡 pośredni | **T1✗** — usługa serwisowo-inżynierska | czynny, NIP 9522127603, KRS 0000490913 | [transferwody.pl — AKPiA](https://transferwody.pl/akpia-aparatura-kontrolno-pomiarowa-i-automatyka) | średnia |
| 46 | **SYNCHRONEO Sp. z o.o.** (Niemcz) | K5 | gminy i spółki komunalne — remonty i modernizacje sterowania oraz monitoringu SUW/oczyszczalni | PROJ | 🟡 pośredni | **T1✗** — wykonawstwo na zamówienie, ale z **powtarzalnością**: Kruszwica 269 370 zł (3 SUW, 2025) i Wodzisław 407 499 zł (2 oczyszczalnie, 2026). Rząd wielkości ~90–200 tys. zł na obiekt | czynny, NIP 5542996903, KRS 0000920634 | [2026/BZP 00184764/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2026%2FBZP%2000184764%2F01) | wysoka |
| 47 | **Hawle.live** (Fabryka Armatury Hawle) — profil w [§5.2.4](./01_plan_biznesowy.md#524-konkurenci-w-obszarze-monitoringu-sieci-i-strat-wody) | K6 | wodociągi monitorujące sieć i armaturę; forma produktowa | CAPEX + AB | 🔴 bezpośredni *(punkty sieciowe, nie obiekty)* | T1✓T2✓T3✓ — gotowa stacja Hawle.live BOX + aplikacja + mapa; kupowane jako produkt, nie projekt. **Ograniczenie:** monitoruje elementy sieci (hydranty, zasuwy, jakość), nie obiekt z szafą sterowniczą — konkuruje o tę samą pozycję budżetową, o inny punkt pomiarowy | — (Fabryka Armatury Hawle: członek wspierający IGWP) | [hawle.com — Hawle.live](https://www.hawle.com/pl/dla-klienta/serwis-hawle/hawle-live) | wysoka |
| 48 | **AVK Smart Water** (AVK Armatura, Pniewy) | K6 | przedsiębiorstwa wodociągowe monitorujące sieć — czujniki VIDI + platforma VIDI Cloud | CAPEX + AB | 🔴 bezpośredni *(punkty sieciowe, nie obiekty)* | T1✓T2✓ — produktowy zestaw sześciu czujników (VIDI Ciśnienie, Przepływ, Temperatura, Poziom, Pozycjoner, Pokrywa nasad) z własną chmurą i API. **T3 przypuszczenie** — publicznych wdrożeń w PL nie opisano. Ten sam wzorzec zagrożenia co Hawle.live: producent armatury dokłada monitoring | — (AVK Armatura: członek wspierający IGWP) | [avk.com.pl — AVK Smart Water](https://www.avk.com.pl/pl-pl/avk-w-polsce/avk-smart-water/avk-smart-water-monitoring-sieci) | średnia |
| 49 | **Efento Sp. z o.o.** (Kraków) | K6 | dowolny klient szukający taniego, bateryjnego pomiaru z chmurą | CAPEX + AB | 🔴 bezpośredni | T1✓**T2✓ (jawne ceny)**T3✓ — rejestratory NB-IoT z cenami na stronie: 4-20 mA i 0-10 V po **790 zł**, poziom wody **1 232 zł**, I/O **750 zł**; rejestrator ciśnienia BLE 860–1 060 zł. Wariant BLE wymaga bramki lub smartfona, a dostęp do Efento Cloud jest licencjonowany osobno na rejestrator | czynny, NIP 6762499917, KRS 0000941769 | [efento.pl — rejestratory NB-IoT](https://efento.pl/kategoria-produktu/sesnory-nb-iot/) | wysoka |
| 50 | **CTHINGS.CO Sp. z o.o.** | K6 | dziś: Edge AI i ekspansja poza PL; wod-kan był pilotażem w Skandynawii | AB + PROJ | 🔵 do obserwacji | **T3✗** — wdrożeń wod-kan na rynku krajowym nie opisano. *Co musiałoby się stać:* powrót do wod-kan w Polsce | czynny, NIP 8212656459, KRS 0000718829, Warszawa | [ISBtech — wdrożenia w Skandynawii](https://www.isbtech.pl/2021/12/polski-startup-cthings-co-wdraza-nowe-rozwiazania-dla-gospodarki-wodno-kanalizacyjnej-w-skandynawii/) | średnia |
| 51 | **METERING Anna Moder Sp. z o.o.** (Buczek) | K6 | małe gminy — monitoring sieci wodociągowej i zdalny odczyt, „pod klucz" | PROJ + CAPEX | 🔴 **bezpośredni** | T1✓T2✓T3✓ — **cztery wygrane postępowania gminne**: Chotcza 377 044 zł (2023), **Mniów 338 127 zł (2023 — SCADA + punkty monitoringu sieci w technologii LoRaWAN)**, Łopiennik Górny 763 963 zł (2025), Osieck 803 498 zł (2026) | czynny, NIP 8311646702, KRS 0001123209 (działalność przeniesiona z JDG Anna Moder do spółki); członek wspierający IGWP | [metering.com.pl — monitoring sieci](https://metering.com.pl/uslugi/monitoring-sieci/), [2023/BZP 00572909/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2023%2FBZP%2000572909%2F01) | wysoka |
| 52 | **Apator Powogaz / Apator Telemetria** | K6 | opomiarowanie rozliczeniowe wodociągów (AMR/AMI) | CAPEX | 🟡 pośredni | **T1✗** — odczyt wodomierza to inne zadanie niż monitoring stanu obiektu | — (członek wspierający IGWP) | [apator.com — system radiowy AMR](https://www.apator.com/nasze-rozwiazania/woda-i-cieplo/system-zdalnego-odczytu-mediow/system-radiowy/amr) | wysoka |
| 53 | **Dostawcy AMI wodomierzowego: Diehl Metering, Kamstrup, Itron, BMETERS** *(wiersz zbiorczy — 4 firmy)* | K6 | opomiarowanie rozliczeniowe | CAPEX + AB | 🟡 pośredni | **T1✗** — jak wyżej. Diehl Metering wygrał bezpośrednio postępowanie gminne w podkarpackiem (158 842 zł, 2026) — sprzedają gminom bez pośrednika | — | [2026/BZP 00291115/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2026%2FBZP%2000291115%2F01) | wysoka |
| 54 | **Pronal SmartMetering24 Sp. z o.o. Sp.k.** | K6 | wodociągi, gminy, spółdzielnie — AMI wodomierzowe NB-IoT, kanał sprzedaży **Plus (Polkomtel)** | CAPEX + AB | 🟡 pośredni | **T1✗** — adaptery IoT na wodomierzu, monitoring przepływu i wykrywanie wycieków; nie monitoruje obiektu. **Istotne dla obrazu rynku:** to **trzeci operator telekomunikacyjny** z kanałem do samorządu, obok Orange i T-Mobile | — (KRS 0000808399) | [biznes.plus.pl — SmartMetering24](https://biznes.plus.pl/nasi-partnerzy/smartmetering24), [smartmetering24.eu](https://smartmetering24.eu/) | średnia |
| 55 | **KROHNE Polska** | K6 | pomiar na ujęciach i studniach; rozwiązania bezprzewodowe | CAPEX | 🟡 pośredni | **T1✗** — dostarcza aparaturę, system składa integrator | — | [pl.krohne.com — zdalny monitoring studni](https://pl.krohne.com/pl/rozwiazania/rozwiazania-pomiarow-bezprzewodowych-zdalnych/pomiar-wody-mozliwoscia-zdalnego-przesylania-danych/zdalny-monitoring-studni-wodnych-zasilania) | wysoka |
| 56 | **S WATER Sp. z o.o.** (Tychy) | K6 | gminy — urządzenia pomiarowe z oprogramowaniem do odczytów i wizualizacji | CAPEX | ⚪ nieustalone | Wygrał postępowanie w Gminie Ćmielów (221 339 zł, 2023, projekt „e-Woda"), ale publicznie opisanej oferty produktowej nie ma — test T1/T2 nie ma na czym się oprzeć | — | [2023/BZP 00205793/01](https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/2023%2FBZP%2000205793%2F01) | przypuszczenie |
| 57 | **WODOSERWIS** | K6 | diagnostyka sieci i lokalizacja wycieków | USL | 🟡 pośredni | **T1✗** — usługa jednorazowa, nie stały monitoring | — | [wodoserwis.pl — monitoring](https://www.wodoserwis.pl/monitoring.htm) | średnia |

---

## 4. Podsumowanie ilościowe

| Klasyfikacja | Liczba | Udział | Które to są |
|---|---|---|---|
| 🔴 **Bezpośredni konkurent** | **15** | 26% | UniCloud/Elmark, Inwap, AT Systems, Inventia, PM Ecology, Hydro-Vacuum, Metalchem-Warszawa, Bartosz, Wilo Polska, Grundfos, Hydro-Partner, Hawle.live, AVK Smart Water, Efento, Metering |
| 🟡 **Pośredni / sąsiedni segment** | **36** | 63% | m.in. AquaRD, AIUT/WaterPrime, Future Processing, Veolia, SUEZ, Ecol-Unicon, Xylem, KSB, PLUM, Ovarro, Aksel, Metrolog, Złote Runo, Synchroneo, cały ogon integratorów AKPiA (13 pozycji), dostawcy AMI |
| 🔵 **Do obserwacji** | **5** | 9% | Orange Polska, T-Mobile Polska, GlobTree, Endress+Hauser Polska, CTHINGS.CO |
| ⚪ **Nieustalone** | **1** | 2% | S WATER |
| **Razem** | **57** | 100% | |

| Kategoria | Pozycji | Bezpośrednich | Komentarz |
|---|---|---|---|
| K1 — chmurowa SCADA abonamentowa | 6 | 3 | Najgęstsza konkurencja względem naszego modelu. UniCloud nie jest sam. |
| K2 — telemetria przemysłowa i RTU | 8 | 2 | Dojrzały sprzęt, wysoka poprzeczka jakościowa; większość celuje wyżej niż my. |
| K3 — kompleksowe smart water | 8 | 0 | **Zero bezpośrednich.** Wszyscy celują w miasta i duże ZWiK; trzej mają zdolność zejścia w dół. |
| K4 — producenci pomp i przepompowni | 11 | 6 | **Najbardziej niedoszacowane zagrożenie.** Monitoring wchodzi razem ze sprzętem, bez osobnej decyzji zakupowej. |
| K5 — integratorzy AKPiA | 13 | 0 | Długi ogon; konkurują ofertą projektową, nie produktem. |
| K6 — wyspecjalizowane IoT | 11 | 4 | Najbardziej produktowa kategoria: Hawle.live, AVK Smart Water, Efento, Metering. |

**Jak liczone są pozycje.** Jedna pozycja = jeden podmiot albo jedno wyodrębnione rozwiązanie. Wiersz 53 jest zbiorczy i obejmuje czterech dostawców AMI o wspólnym werdykcie i wspólnym uzasadnieniu, więc **liczba firm jest o trzy wyższa niż liczba pozycji**; wszystkie statystyki liczą pozycje.

---

## 5. Dowód z przetargów publicznych

Nie to, co firma o sobie mówi, tylko **co gminy faktycznie kupują, od kogo i za ile**.

### 5.1. Zakres zbioru

**72 postępowania dotyczące monitoringu, telemetrii i automatyki wod-kan z lat 2021–2026**, w tym **51 zakończonych zawarciem umowy** i 21 unieważnionych. Z województw małopolskiego i podkarpackiego pochodzi 18 postępowań, w tym 13 zakończonych umową (Nowy Targ, Tomice, Jordanów, Piwniczna-Zdrój, Wieprz ×2, Pleśna, Politechnika Krakowska — małopolskie; Jasienica Rosielna, Jeżowe, Zaklików ×2, Żyraków — podkarpackie).

Pełny zbiór z cenami wszystkich ofert, nazwami i NIP-ami wykonawców: [`assets/06_przetargi_bzp_2021_2026.csv`](./assets/06_przetargi_bzp_2021_2026.csv) (separator `;`, kodowanie UTF-8, 72 wiersze × 16 kolumn) — każdą liczbę w tej sekcji da się sprawdzić bez odtwarzania zapytań do API.

Dwie rzeczy trzeba wiedzieć przy odczycie tych danych, bo zmieniają wnioski:

- **Zamówienia poniżej 130 000 zł netto nie podlegają ustawie PZP i nie trafiają do BZP.** To jest dokładnie przedział, w którym mieści się nasz produkt — patrz [§5.6](#56-najważniejsza-konsekwencja-handlowa--próg-130-000-zł).
- **Tytuł zamówienia nie mówi, co zostało kupione.** Zamówienie parasolowe bywa dzielone na części o tym samym tytule (np. w Zaklikowie ten sam tytuł objął część fotowoltaiczną, pompową i monitoringową), a „system monitoringu sieci wodociągowej" to najczęściej wymiana wodomierzy — patrz [§5.7](#57-pułapka-nazewnicza-monitoring-sieci-wodociągowej-najczęściej-znaczy-ami). Wnioski w tej sekcji opierają się na opisie przedmiotu zamówienia, nie na tytule.

### 5.2. Rozstrzygnięte postępowania

Wybór 28 postępowań najbliższych naszemu produktowi. Kwoty brutto, w złotych.

| Data | Zamawiający | Woj. | Przedmiot (skrót) | Ofert | Cena wybrana | Wykonawca | UE |
|---|---|---|---|---|---|---|---|
| 2021-08-23 | PGM Sp. z o.o. (Polkowice) | dolnośl. | system nadzoru i zdalnego sterowania siecią wod-kan | 2 | **824 100** | Technika Pomiarowa i Automatyka Cieplna B. Dziadosz | nie |
| 2021-12-13 | Gmina Daleszyce | świętokrz. | monitoring ujęcia i sieci Marzysz — **7 punktów pomiarowych + 3 zasuwy** | 1 | **199 500** | ZUK w Daleszycach Sp. z o.o. | nie |
| 2022-09-16 | Gmina Płużnica | kuj.-pom. | rozbudowa SUW + system zarządzania siecią | 1 | **228 631** | Złote Runo + Metrolog (konsorcjum) | nie |
| 2023-01-23 | MZWiK Nowy Targ | **małopol.** | wizualizacja i zdalne sterowanie ujęciem „Podhale" (1 obiekt) | 1 | **242 015** | MEDAS Sp. z o.o. | nie |
| 2023-04-05 | Gmina Chotcza | mazow. | monitoring sieci + radiowy odczyt **740 wodomierzy** | 1 | **377 044** | METERING Anna Moder | nie |
| 2023-04-26 | GZGKiM Wągrowiec | wielkop. | modernizacja SUW Kobylec z monitoringiem | 1 | **3 687 540** | METROLOG Sp. z o.o. | nie |
| 2023-04-26 | GZGKiM Wągrowiec | wielkop. | modernizacja SUW Potulice z monitoringiem | 1 | **3 608 820** | METROLOG Sp. z o.o. | nie |
| 2023-05-08 | Gmina Ćmielów | świętokrz. | urządzenia pomiarowe + oprogramowanie („e-Woda") | 1 | **221 339** | S WATER Sp. z o.o. | nie |
| 2023-09-18 | Gmina Płużnica | kuj.-pom. | rozbudowa SUW + system zarządzania siecią | 2 | **316 083** | METROLOG Sp. z o.o. | nie |
| 2023-12-07 | Gmina Niechanowo | wielkop. | zdalny odczyt i monitoring zużycia wody | 3 | **203 180** | PHU „WODEX" L. Domagalski | nie |
| 2023-12-27 | Gmina Mniów | świętokrz. | **SCADA + punkty monitoringu sieci w LoRaWAN** | 1 | **338 127** | METERING Anna Moder | **tak** |
| 2024-03-20 | Gmina Bierzwnik | zach.-pom. | szafy sterownicze SUW z monitoringiem | 2 | **514 891** | Elektrotechnika i Automatyka Przem. M. Gorkowski | **tak** |
| 2024-04-05 | Gmina Maszewo | lubuskie | system monitorowania sieci + zdalny odczyt wodomierzy | 1 | **759 866** | **Orange Polska S.A.** | nie |
| 2024-06-05 | Gmina Tomice | **małopol.** | monitoring sieci ze zdalnym odczytem (3 miejscowości) | 1 | **295 242** | SENSUS Polska Sp. z o.o. | nie |
| 2024-07-09 | Gmina Mirów | mazow. | punkty pomiarowe + system GIS zarządzania siecią | 3 | **608 493** | Biuro Inżynierskie Wodnik K. Świętochowski | **tak** |
| 2024-07-24 | Gmina Wągrowiec | wielkop. | przebudowa SUW Łekno z monitoringiem | 3 | **4 548 540** | METROLOG Sp. z o.o. | **tak** |
| 2025-03-17 | Gmina Jordanów | **małopol.** | zdalny odczyt wodomierzy | 2 | **323 955** | **Orange Polska S.A.** | nie |
| 2025-06-27 | Gmina Kraśniczyn | lubelskie | modernizacja + monitoring **5 pompowni strefowych** | 2 | **731 813** | LPRINŻ INVEST Sp. z o.o. | **tak** |
| 2025-07-07 | Gmina Wierzbinek | wielkop. | zdalny monitoring i obsługa pracy SUW (1 obiekt) | 6 | **311 400** | Inż. Środowiska ELGAJ L. Kondratowicz | **tak** |
| 2025-08-13 | Gmina Siechnice | dolnośl. | **monitoring przepompowni wód opadowych — retrofit do istniejących szaf** | 2 | **55 680** | **HYDRO-PARTNER Sp. z o.o.** | nie |
| 2025-08-29 | Gmina Kłecko | wielkop. | szafy sterownicze SUW + wpięcie do wizualizacji SCADA | 4 | **227 402** | **HYDRO-PARTNER Sp. z o.o.** | nie |
| 2025-09-02 | PK Ogrodzieniec | śląskie | monitoring sieci: przepływ i ciśnienie + 15 studni | 2 | **576 533** | Aquadrill Przewierty Sterowane Sp. z o.o. | **tak** |
| 2025-09-10 | Gmina Łopiennik Górny | lubelskie | wodomierze ze zdalnym odczytem + monitoring sieci | 2 | **763 963** | METERING Anna Moder Sp. z o.o. | **tak** |
| 2025-11-20 | Gmina Zagrodno | dolnośl. | szafy sterownicze SUW + **wpięcie do systemu HydroNET** | 2 | **398 354** | **HYDRO-PARTNER Sp. z o.o.** | nie |
| 2025-12-19 | Wodociągi Miejskie w Radomiu | mazow. | kompleksowa wymiana modułów telemetrycznych | 2 | **589 502** | Złote Runo Sp. z o.o. | nie |
| 2025-12-29 | PK Kruszwica | kuj.-pom. | remont sterowania i monitoringu **3 SUW** | 2 | **269 370** | SYNCHRONEO Sp. z o.o. | nie |
| 2026-02-17 | Gmina Wieprz | **małopol.** | rozbudowa monitoringu **SUW + przepompownia** (2 obiekty) | 3 | **799 500** | Delta Rafał Stępiński | **tak** |
| 2026-04-03 | Gmina Wodzisław | świętokrz. | monitoring pracy **2 oczyszczalni** + rozbudowa SCADA | 2 | **407 499** | SYNCHRONEO Sp. z o.o. | **tak** |

### 5.3. Kto naprawdę wygrywa

| Wykonawca | Wygranych | Łącznie | Charakter |
|---|---|---|---|
| **METROLOG Sp. z o.o.** | 5 (jedna w konsorcjum ze Złotym Runem) | ~12,4 mln zł | modernizacje SUW z monitoringiem — inny rząd wielkości niż nasz |
| **HYDRO-PARTNER Sp. z o.o.** | 4 | ~791 tys. zł | **monitoring i szafy dla małych gmin — nasz segment** |
| **METERING Anna Moder** | 4 | ~2,28 mln zł | monitoring sieci + AMI dla małych gmin |
| **Orange Polska S.A.** | 2 | ~1,08 mln zł | AMI wodomierzowe w gminach |
| **SYNCHRONEO Sp. z o.o.** | 2 | ~677 tys. zł | remonty sterowania i monitoringu SUW/oczyszczalni |
| **Złote Runo Sp. z o.o.** | 2 (jedna w konsorcjum z Metrologiem) | ~818 tys. zł | moduły telemetryczne |

Reszta rozstrzygnięć rozkłada się na **jednorazowych wykonawców lokalnych** — firmy elektryczne i inżynierskie bez opisanej oferty produktowej, każda z jedną wygraną.

**Wniosek, którego nie widać z materiałów marketingowych:** mali dostawcy telemetrii GSM/GPRS, którzy produktowo są nam najbliżsi (Inwap, AT Systems, PM Ecology), **nie wystąpili ani razu w 51 rozstrzygnięciach**. Oznacza to, że sprzedają poniżej progu ustawy albo przez pośredników — a nie że ich nie ma. Ten sam kanał jest dostępny dla nas ([§5.6](#56-najważniejsza-konsekwencja-handlowa--próg-130-000-zł)).

### 5.4. Ile gmina naprawdę płaci

| Typ zakupu | Przykład | Cena | Na obiekt |
|---|---|---|---|
| **Retrofit monitoringu do istniejących szaf** | Siechnice 2025 (przepompownie wód opadowych) | 55 680 zł | **najtańsze zamówienie monitoringowe w całym zbiorze** |
| **Punkty pomiarowe na sieci** | Daleszyce 2021 — 7 punktów + 3 zasuwy | 199 500 zł | **~28,5 tys. zł/punkt** (z zasuwami) |
| **Sterowanie + monitoring SUW (1 obiekt)** | Kłecko 227 402 zł · Wierzbinek 311 400 zł · Zagrodno 398 354 zł · Złotniki Kuj. 167 280 zł | 167–398 tys. zł | **~170–400 tys. zł/obiekt** |
| **Sterowanie + monitoring SUW (wiele obiektów)** | Kruszwica 2025 — 3 SUW | 269 370 zł | **~90 tys. zł/obiekt** |
| **Rozbudowa monitoringu 2 obiektów** | Wieprz 2026 — SUW + przepompownia | 799 500 zł | **~400 tys. zł/obiekt** |
| **Monitoring pompowni strefowych** | Kraśniczyn 2025 — 5 pompowni (z pracami budowlanymi) | 731 813 zł | **~146 tys. zł/obiekt** |
| **AMI wodomierzowe** | Chotcza — 740 wodomierzy · Brochów — 749 wodomierzy | 377 044 / 373 367 zł | **~500 zł/wodomierz** |

**Porównanie z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody).** Plan zakłada 2,9–8,3 tys. zł jednorazowo na obiekt; rynek przetargowy płaci 20–100× więcej. Właściwy odczyt tej różnicy jest jeden z trzech możliwych:

1. *„Rynek płaci więcej, więc możemy podnieść ceny"* — **błędny**. Te kwoty obejmują szafę sterowniczą, sterownik PLC, przetwornice, prace elektryczne i uruchomienie. My sprzedajemy warstwę pomiarowo-komunikacyjną, a nie rozdzielnicę.
2. *„Nasz model jest nierealny"* — **też błędny**. Siechnice pokazują, że gmina potrafi kupić **sam monitoring bez wymiany szaf**, i że taki zakup kosztuje rząd wielkości 50–100 tys. zł na całe zadanie.
3. **Właściwy:** jesteśmy w **innej pozycji budżetowej niż większość tych postępowań** — konkurujemy nie z modernizacją SUW za 300 tys. zł, tylko z zakupem, którego w BZP w ogóle nie widać.

### 5.5. Budżety gmin — sygnał z postępowań unieważnionych

21 postępowań unieważniono, w większości dlatego, że oferty przekroczyły kwotę, którą gmina zamierzała przeznaczyć. To najlepsze dostępne źródło informacji o realnych budżetach:

| Zamawiający | Przedmiot | Sygnał budżetowy |
|---|---|---|
| Gmina Kłecko (2025) | szafy sterownicze SUW + wizualizacja | jedyna oferta **215 250 zł** przekroczyła budżet; rok później to samo kupione za 227 402 zł |
| Gmina Tomice (2024) | monitoring sieci ze zdalnym odczytem | oferty 118 704–295 200 zł, wszystkie ponad budżet |
| Gmina Płużnica (2022) | rozbudowa SUW + system zarządzania siecią | gmina miała **4 750 000 zł**, najniższa oferta **14 697 270 zł** — rozjazd 3× |
| Gmina Łopiennik Górny (2025, dwukrotnie) | wodomierze + monitoring sieci | dwa unieważnienia z powodu ceny, dopiero trzecie podejście rozstrzygnięte |
| Miasto Słupsk (2025) | monitoring centralnej SUW | unieważnione, bo **środki z programu nie zostały przyznane** |
| Miasto Suwałki (2025) | monitoring 2 studni awaryjnych | unieważnione — zadanie nie weszło do umowy z wojewodą |

Dwa wnioski, oba handlowe: **(1)** w małej gminie budżet na monitoring jest ciasny i stale przekraczany przez oferty rynkowe — czyli oferta wyraźnie tańsza ma przewagę nie „cenową", ale **wykonalnościową**: pozwala zadanie w ogóle zrealizować; **(2)** znacząca część tych zadań **żyje i umiera z dotacją**, co domyka argument o priorytecie zlecenia B-13.

### 5.6. Najważniejsza konsekwencja handlowa — próg 130 000 zł

Ustawa Prawo zamówień publicznych stosuje się do zamówień o wartości **od 130 000 zł netto** (art. 2 ust. 1 pkt 1). Poniżej tej kwoty gmina kupuje według własnego regulaminu — bez ogłoszenia w BZP, bez SWZ, często z jednym albo trzema zapytaniami ofertowymi.

Przy naszym modelu z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody) (2,9–8,3 tys. zł na obiekt) gmina z 10 obiektami wydaje **29–83 tys. zł** — **poniżej progu**. Trzy skutki:

1. **Nie musimy wygrywać przetargu, żeby wejść do gminy.** Wystarczy być zamówieniem regulaminowym. To tłumaczy też nieobecność Inwapu i AT Systems w BZP.
2. **Cykl sprzedaży jest krótszy i nie zależy od kalendarza naboru dotacyjnego.** Postępowania z §5.2 trwają miesiącami i bywają unieważniane po drodze.
3. **Ale: nie jesteśmy widoczni tam, gdzie gmina szuka.** Gmina z dotacją ogłosi przetarg na „inteligentny system zarządzania siecią" i kupi pakiet za 300 tys. zł. Naszą drogą jest gmina **bez** dotacji, która chce rozwiązać problem tanio i szybko — a tam nikt nie ogłasza niczego publicznie, więc trzeba do niej dotrzeć samemu.

**Twierdzenie o progu wymaga potwierdzenia u prawnika lub w regulaminie konkretnej gminy** — próg wynika z ustawy, ale gminy mają własne regulaminy wewnętrzne z niższymi progami zapytania ofertowego.

### 5.7. Pułapka nazewnicza: „monitoring sieci wodociągowej" najczęściej znaczy AMI

**12 z 51 rozstrzygniętych postępowań** dotyczy wymiany wodomierzy z nakładkami radiowymi, mimo że w tytule mają „system monitoringu sieci wodociągowej", „system monitorowania sieci" albo „monitoring zużycia wody": Chotcza (740 wodomierzy), Niechanowo, Maszewo, Łopiennik Górny, Brochów (744 wodomierze indywidualne + 5 sieciowych), Stara Kornica, Stara Błotnica, Osieck, Jordanów, Wieprz, Pleśna, Żyraków.

1. **Przy analizie rynku i przy szukaniu klienta nie wolno ufać tytułowi zamówienia** — trzeba czytać opis przedmiotu.
2. **Dostawcy AMI zajmują pozycję budżetową „monitoring" w budżecie gminy**, nawet jeśli produktowo rozwiązują inne zadanie. W rozmowie handlowej trzeba umieć powiedzieć, czym nasz monitoring różni się od „monitoringu", który gmina właśnie kupiła — inaczej usłyszymy „my już to mamy".

---

## 6. Weryfikacja rejestrowa

Sprawdzono w Wykazie podatników VAT Ministerstwa Finansów (stan 5 września 2026) podmioty, przy których forma prawna albo ciągłość działalności mają znaczenie dla oceny. **Wszystkie zweryfikowane podmioty mają status czynny** — numery w kolumnie **Rejestr** tabeli w [§3](#3-pełny-spis--tabela-zbiorcza).

Trzy ustalenia zmieniające obraz podmiotu:

| Podmiot | Ustalenie |
|---|---|
| **METERING Anna Moder** | Działalność przeniesiona z jednoosobowej firmy do **METERING ANNA MODER Sp. z o.o.** (NIP 8311646702, KRS 0001123209). Widać to w przetargach: do 2023 r. wygrywa JDG, od 2025 r. — spółka. |
| **Vispena** | To marka **STOVARIS Sp. z o.o.** (NIP 5242877169), nie odrębny podmiot. |
| **Metria** | Jednoosobowa działalność gospodarcza (NIP 7010384804), nie spółka — istotne przy ocenie zdolności do obsługi floty obiektów. |

---

## 7. Członkowie wspierający IGWP

[Izba Gospodarcza „Wodociągi Polskie"](https://www.igwp.org.pl/o-nas/czlonkostwo/wykaz-czlonkow/) zrzesza **471 członków zwyczajnych** (przedsiębiorstwa wod-kan — czyli potencjalni klienci) i **63 członków wspierających** (dostawcy branżowi).

**Z 63 członków wspierających w mapie jest 15:** AIUT, Aksel, Apator Powogaz, AquaRD, AVK Armatura, Ecol-Unicon, Endress+Hauser Polska, Fabryka Armatury Hawle, Future Processing, Grundfos Pompy, Hydro-Vacuum, Metering Anna Moder, Veolia Energia Polska, Wilo Polska, Złote Runo. Pozostałe 48 to producenci rur, armatury, chemii, usług laboratoryjnych i firmy budowlane — poza zakresem konkurencyjnym.

Dwie pozycje warte odnotowania mimo braku konkurencyjności: **ICsec S.A.** (cyberbezpieczeństwo OT — punkt odniesienia i potencjalny partner przy wymaganiach NIS2) oraz **Unisoft Sp. z o.o.** (systemy billingowe dla przedsiębiorstw wod-kan — potencjalny kanał integracji).

Lista IGWP pokrywa się z mapą bez reszty: **branżowy „mainstream" dostawców jest w niej w całości.**

---

## 8. Ceny publiczne

| Podmiot | Co jest jawne | Kwota |
|---|---|---|
| **UniCloud (Elmark)** | abonament za obiekt wod-kan | **od ~1 000 zł/rok**, typowo **1–3 tys. zł/rok**; start do ~10 tys. zł |
| **Efento** | ceny katalogowe rejestratorów NB-IoT (brutto) | rejestrator sygnału **4-20 mA — 790 zł**, **0-10 V — 790 zł**, **I/O — 750 zł**, **poziomu wody — 1 232 zł**, ciśnienia różnicowego 1 310 zł; rejestrator ciśnienia BLE **860–1 060 zł** |
| **Efento Cloud** | model licencjonowania | **opłata licencyjna za każdy podłączony rejestrator** |
| **Grundfos Remote Management** | model rozliczenia | **stała, niska opłata roczna** obejmująca hosting, bezpieczeństwo i wsparcie (ceny katalogowe Grundfos są hurtowe, w euro, dostępne przez dystrybutora) |

Pozostali dostawcy — Hawle.live, AVK VIDI, Inwap, AT Systems, GlobTree, Endress+Hauser Netilion, KSB — cen nie publikują i kierują do kontaktu handlowego. Rolę cennika przejmują dla nich ceny kontraktowe z [§5.4](#54-ile-gmina-naprawdę-płaci).

**Trzy wnioski cenowe:**

1. **Efento wyznacza dolną granicę rynku sprzętowego: ~790 zł za kanał pomiarowy 4-20 mA.** To bezpośredni punkt odniesienia dla naszego BOM z [§4.2](./01_plan_biznesowy.md#42-szacunek-kosztów-jednostkowych) — musimy być tańsi na kanał, żeby argument kosztowy w ogóle istniał.
2. **Efento nie jest tak „bezinfrastrukturowe", jak wygląda w materiałach.** Wariant BLE wymaga bramki albo smartfona (zasięg ~100 m), a dostęp do chmury jest licencjonowany osobno na rejestrator. Bez bramki działają tylko warianty NB-IoT.
3. **UniCloud jest jedynym jawnym punktem odniesienia dla abonamentu — i nie jesteśmy od niego tańsi.** Nasze 130–170 zł/mies. (1 560–2 040 zł/rok) mieści się **wewnątrz** przedziału 1–3 tys. zł/rok. Przewaga musi leżeć gdzie indziej: koszt wejścia, neutralność sprzętowa, prostota.

---

## 9. Monitoring w ekosystemie producenta pomp

Trzech producentów pomp ma potwierdzoną polskojęzyczną ofertę zdalnego monitoringu, ale rozwiązują różne zadania — i stąd różne werdykty:

- **Wilo Polska** (wiersz 26) — monitoring pompowni i tłoczni jako **usługa serwisowa dokupywana do sprzętu**, trafia w budżet eksploatacyjny gminy. 🔴 bezpośredni w obrębie własnego sprzętu.
- **Grundfos** (wiersz 27) — **Grundfos Remote Management**, opisany na polskiej stronie produktowej wprost jako alternatywa dla systemów SCADA dla użytkowników niepotrzebujących automatyzacji procesu: dostęp przez przeglądarkę, alarmy na telefon, stała niska opłata roczna obejmująca hosting i wsparcie. To nasz model biznesowy wykonany przez producenta pomp, z dostępem do gminy przez własną sieć serwisową. 🔴 bezpośredni w obrębie własnego sprzętu.
- **KSB** (wiersz 28) — **KSB Guard** monitoruje drgania i temperaturę pompy (czujnik → moduł nadawczy → bramka → chmura KSB, aktualizacja cogodzinna). Odpowiada na pytanie „czy pompa się zużywa", nie „co się dzieje na obiekcie". 🟡 pośredni.

**Konsekwencja dla [§5.2.8](./01_plan_biznesowy.md#528-największe-zagrożenia-konkurencyjne):** zagrożenie „monitoring jako dodatek do pompy" obejmuje **trzech** producentów z potwierdzoną polską ofertą (Wilo, Grundfos, Hydro-Vacuum). To nie jest ryzyko punktowe, tylko **wzorzec rynkowy**.

---

## 10. Podmioty warte pogłębionej analizy w B-02/B-03

| Podmiot | Do którego zlecenia | Dlaczego akurat ten |
|---|---|---|
| **Hydro-Partner (HydroNET Web 6)** | **B-02 + B-03, priorytet 1** | Najbliższy nam model na rynku: hostowana platforma z instancją na gminę, call center z płatnym monitorowaniem obiektów, wygrane postępowania w naszym przedziale cenowym. B-03 — ich interfejs (publiczna strona logowania `hydronetweb.pl`); B-02 — sposób integracji z szafą i kanał komunikacji. |
| **PM Ecology** (Aqua Logger) | B-02 | Polski producent bateryjnych rejestratorów z GSM i integracją SCADA — najbliższy technicznie odpowiednik naszego gatewaya. Odpowiada na pytanie „czy nasz PoC ma sens sprzętowy". |
| **Efento** | B-02 | Jedyny konkurent z **jawnym cennikiem**. Benchmark kosztu na kanał pomiarowy i modelu licencjonowania chmury. |
| **Inwap (PIK-on)** i **AT Systems** | B-02 + B-03 | Sprzedają dokładnie nasz produkt małym podmiotom, a przy tym nie startują w przetargach — warto zbadać, jak docierają do klienta. |
| **Grundfos Remote Management** | B-02 | Wzorzec „producent sprzętu z chmurą w abonamencie" wykonany przez globalną firmę; punkt odniesienia dla onboardingu urządzenia. |
| **AVK Smart Water (VIDI Cloud)** | B-02 + B-03 | Produktowy zestaw czujnik + chmura + API od producenta armatury; bezpośrednia analogia do Hawle.live, pokazuje kierunek kategorii. |
| **Ovarro (XiLog 4G + Primeweb)** | B-02 | Dojrzały wzorzec formatu telemetrii i retencji (wymiary 5 i 8 B-02). |
| **Ecol-Unicon (Bumerang SMART)** | B-03 | Monitoring połączony z prognozą pogody i planowaniem prac — wzorzec dla widoku alarmów. |
| **Endress+Hauser Netilion** | B-02 + B-03 | Rozbudowany onboarding urządzeń; wzorzec dla wymiaru 9 B-03. |
| **Orange Smart Water** | B-03 | >40 tys. urządzeń w >30 miejscowościach — najlepiej sprawdzony w Polsce interfejs adresowany do naszego użytkownika. |
| **Lacroix Sofrel (S4W)**, **Kallipr (Captis)** | B-02 | Wzorce techniczne spoza rynku PL: bezpieczeństwo i zgodność z NIS2 (Sofrel), pobór mocy i model urządzenie↔chmura (Kallipr). |

**Świadomie nie rekomendujemy** dokładania do B-02/B-03 firm z kategorii K5 (integratorzy — nie mają produktu do przeanalizowania, tylko realizacje) ani dostawców AMI, bo rozwiązują inne zadanie i ich wzorce nie przeniosą się na monitoring obiektu.

---

## 11. Tropy odrzucone

Zapisane po to, żeby nikt nie badał ich drugi raz.

| Podmiot / rozwiązanie | Dlaczego odrzucone |
|---|---|
| **Lacroix Sofrel**, **Kallipr** | **Nie działają na rynku polskim** — bez polskiego dystrybutora, polskojęzycznych materiałów i udokumentowanych wdrożeń. Pozostają wzorcami technicznymi dla B-02, nie graczami krajowymi. |
| **Monitoring Ścieki Polskie** (szambo.online, zlewnia.online) | Ewidencja nieczystości ciekłych i sprawozdawczość gminy wobec szamb. Zbieżna terminologia, inny problem i inny użytkownik. [Źródło](https://monitoring.sciekipolskie.org/) |
| **Simex, Lumel, Aplisens, BD Sensors, Introl, Dacpol, OMC Envag, G.Drexl, KanRo, Eurodis, Aqua Seen, Alter** | Producenci i dystrybutorzy aparatury pomiarowej — dostawcy **komponentów**, potencjalni poddostawcy, nie konkurenci systemowi (wystawcy grupy pomiarowej targów WOD-KAN). KROHNE Polska został w mapie (wiersz 55), bo ma polskojęzyczną ofertę zdalnego monitoringu studni. |
| **SmartFlow jako „konkurent dla gminy"** | Rozwiązuje wykrywanie ukrytych wycieków w strefach dużego miasta. Pozostaje w spisie jako pośredni. |
| **Wody Polskie i ich postępowania** | Dotyczą gospodarki wodnej państwa (RZGW), nie sieci wodociągowych gmin. Szum przy przeszukiwaniu przetargów. |
| **Lokalni wykonawcy z przetargów bez oferty produktowej** (Biuro Inżynierskie Wodnik, ELGAJ, X-Comfort, Rosmomis-Wawrzyniak, PHU PAGOS, LPRINŻ, Aquadrill, Delta, WES, Mikroserw i in.) | Wygrali pojedyncze zamówienia, ale nie mają publicznie opisanej, powtarzalnej oferty monitoringu — zgodnie z zasadą z [§2.2](#22-zasada-wpisu-do-mapy) należą do tabeli [rozstrzygniętych postępowań](#52-rozstrzygnięte-postępowania), nie do mapy. Jeśli któryś zacznie wygrywać seryjnie, trafi do mapy przy aktualizacji. |
| **ICsec, Unisoft, LogicSynergy, Eskom IT** (członkowie wspierający IGWP) | Cyberbezpieczeństwo OT, billing, IT — sąsiadują tematycznie, ale nie sprzedają monitoringu obiektu. Potencjalni partnerzy, nie konkurenci. |
| **Katalogi branżowe wod-kan.biz i wodkaneko.pl jako źródło mapy** | Kategorie „Telemetria" i „Monitoring" w wod-kan.biz **nie zawierają wpisów firm**; w wodkaneko.pl filtr marki „Telemetria" zwraca zero wyników, a kategoria monitoringowa (599 firm) jest zdominowana przez dystrybutorów komponentów. Przetargi publiczne dały w jednym przebiegu więcej zweryfikowanych nazw niż wszystkie katalogi razem. |

---

## 12. Co z tego wynika dla planu biznesowego

Pięć propozycji korekt — **propozycje, nie zmiany wprowadzone**.

1. **[§5.2.8](./01_plan_biznesowy.md#528-największe-zagrożenia-konkurencyjne) punkt 1 („monitoring jako dodatek do nowej szafy lub pompy") jest niedoszacowany.** Pięć z piętnastu konkurentów bezpośrednich to producenci sprzętu dorzucający monitoring (Hydro-Vacuum, Metalchem, Bartosz, Wilo, Grundfos), a szósty — Hydro-Partner — to producent szaf, który zbudował do tego własną platformę webową i call center. Ich przewaga nie jest technologiczna: polega na tym, że **gmina nie podejmuje wtedy osobnej decyzji zakupowej**.
2. **[§5.2.9](./01_plan_biznesowy.md#529-wnioski-strategiczne) punkt 3 („najbliższym konkurentem biznesowym jest UniCloud") wymaga korekty.** Proponowane brzmienie: *„najbliższym konkurentem modelowym jest UniCloud, ale najbliższym konkurentem operacyjnym — Hydro-Partner, który ma hostowaną platformę, płatny nadzór w call center i udokumentowane wygrane w małych gminach w przedziale 55–400 tys. zł"*. Podstawa: cztery rozstrzygnięte postępowania.
3. **Do [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku) warto dopisać siódmą kategorię: operatorzy telekomunikacyjni.** Orange (>40 tys. urządzeń, >30 miejscowości, dwie wygrane w gminach), T-Mobile i Plus (przez Pronal SmartMetering24) nie mieszczą się w żadnej z sześciu kategorii, a mają naraz markę, kanał sprzedaży do samorządu, model abonamentowy i własną sieć IoT.
4. **[§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody) powinien jawnie powiedzieć, że sprzedajemy poniżej progu PZP.** To oś strategii wejścia: 10 obiektów × 2,9–8,3 tys. zł = 29–83 tys. zł, czyli poniżej 130 000 zł netto. Nie musimy wygrywać przetargów, cykl sprzedaży jest krótszy — ale nie jesteśmy widoczni tam, gdzie gmina z dotacją szuka dostawcy. Plan powinien wyciągnąć z tego konsekwencje w opisie kanału sprzedaży.
5. **Materiały handlowe muszą rozbroić pułapkę nazewniczą „monitoringu".** Gmina, która wymieniła wodomierze na radiowe, jest przekonana, że ma monitoring. Potrzebne jest jedno zdanie różnicujące, gotowe do użycia w rozmowie: *„zdalny odczyt mówi, ile wody zużył mieszkaniec; nasz monitoring mówi, że hydrofornia stanęła o 3:40 w nocy"*.

---

## Powiązania

- **[§5.1](./01_plan_biznesowy.md#51-rynki-docelowe)** — rynki docelowe i kryteria SAM, na których oparty jest test klasyfikacyjny.
- **[§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji)** — pogłębione profile 9 podmiotów; ten dokument ich nie powtarza, tylko klasyfikuje i rozszerza spis. Propozycje korekt w [§12](#12-co-z-tego-wynika-dla-planu-biznesowego).
- **[§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody) i [§4.2](./01_plan_biznesowy.md#42-szacunek-kosztów-jednostkowych)** — model przychodowy i koszty jednostkowe skonfrontowane z cenami rynkowymi w [§5.4](#54-ile-gmina-naprawdę-płaci) i [§8](#8-ceny-publiczne).
- **B-02** (analiza technologiczna konkurencji) i **B-03** (analiza UX) — lista podmiotów do dołożenia w [§10](#10-podmioty-warte-pogłębionej-analizy-w-b-02b-03).
- **B-13** (dofinansowania dla gmin) — [§5.5](#55-budżety-gmin--sygnał-z-postępowań-unieważnionych) pokazuje postępowania unieważniane z powodu nieprzyznanych środków dotacyjnych.
- **[ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md)** — rozliczenie per obiekt; [§5.6](#56-najważniejsza-konsekwencja-handlowa--próg-130-000-zł) dokłada argument o progu PZP.
- **[CONTEXT.md](./CONTEXT.md)** — „partnerstwo montażowo-integracyjne"; część podmiotów z K5 to równie prawdopodobni partnerzy co konkurenci (w szczególności Intelcon z województwa pierwszego klienta).

> **Źródła i status.** Ustalenia o podmiotach opierają się na źródłach publicznych zweryfikowanych 5 września 2026. Dane o postępowaniach pochodzą z ogłoszeń o wyniku postępowania w Biuletynie Zamówień Publicznych, dane rejestrowe z Wykazu podatników VAT Ministerstwa Finansów. Klasyfikacje są wnioskami autorskimi na podstawie kryteriów z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam), a nie deklaracjami samych podmiotów. Twierdzenie o progu 130 000 zł wymaga potwierdzenia przez prawnika.
