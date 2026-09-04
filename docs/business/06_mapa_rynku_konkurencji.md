# Mapa rynku — wszyscy gracze na polskim rynku, bezpośredni vs. pozostali

**Data weryfikacji źródeł: 4 września 2026.** Wszystkie ustalenia w tym dokumencie odnoszą się do tej daty. Rynek zmienia się szybciej niż dokumentacja — przed użyciem tej mapy w rozmowie handlowej sprawdź ponownie podmioty oznaczone jako **bezpośrednie**.

Dokument jest **rozszerzeniem, nie powtórzeniem** [§5.2 planu biznesowego](./01_plan_biznesowy.md#52-analiza-konkurencji). Tam jest głębia (9 pogłębionych profili), tutaj jest **szerokość i jednoznaczny werdykt klasyfikacyjny** dla każdego znalezionego podmiotu — w tym dla tych, które §5.2 już opisuje jakościowo, ale nigdy nie zaklasyfikowała.

> **Stan dokumentu: kompletny w zakresie spisu i klasyfikacji, niekompletny w zakresie cen i zwycięzców postępowań.** Środowisko, w którym powstawał, nie miało dostępu do pobierania stron ani plików PDF. Lista pracy do dokończenia, gotowa do zlecenia, jest w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

---

## 1. Odpowiedź w jednym akapicie

Na polskim rynku zidentyfikowano **52 pozycje** rozłożone na sześć kategorii z [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku). Po zastosowaniu testu opartego na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam) tylko **11 z nich to konkurenci bezpośredni** — reszta albo celuje w innego klienta (33), albo dziś nie konkuruje, lecz ma realną zdolność zejścia w dół rynku (5), albo nie dało się jej rozstrzygnąć z publicznych źródeł (3). Najważniejszy wniosek nie dotyczy jednak liczb: **realna konkurencja o małą gminę nie przychodzi ze strony dużych platform smart water — żadna z ośmiu pozycji w kategorii „kompleksowe smart water" nie przeszła testu na konkurenta bezpośredniego** — tylko z dwóch kierunków, których [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji) nie docenia: od producentów przepompowni i szaf, którzy dorzucają monitoring do sprzedaży sprzętu (4 z 11 bezpośrednich), oraz od małych, mało widocznych firm telemetrycznych sprzedających „monitoring GSM/GPRS z podglądem w przeglądarce" jako gotowy produkt — Inwap, AT Systems, PM Ecology.

> **Hipoteza wymagająca weryfikacji, nie ustalenie.** Nasuwa się wniosek, że to właśnie ta druga grupa wygrywa małe postępowania w gminach — jest tania, gotowa i mieści się w typowym opisie przedmiotu zamówienia. **Nie ma na to dowodu w tym dokumencie**: nie udało się ustalić zwycięzców postępowań (patrz [§6.3](#63-czego-w-przetargach-nie-udało-się-ustalić)). Sprawdzenie tej hipotezy jest zadaniem nr 1 w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia) i najtańszym sposobem, żeby dowiedzieć się, z kim naprawdę przegrywamy albo wygrywamy.

---

## 2. Metoda i jej granice

### 2.1. Jak powstawał spis

1. Punkt wyjścia: 9 podmiotów opisanych w [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji) + taksonomia 6 kategorii z [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku).
2. Przeszukanie sieci pod kątem każdej z 6 kategorii osobno, po polsku, frazami używanymi przez branżę (nie przez marketing): „telemetria przepompowni", „monitoring hydroforni", „system monitoringu i wizualizacji przepompowni ścieków", „inteligentny system zarządzania siecią wodociągową".
3. Przeszukanie **historycznych postępowań publicznych** i BIP-ów małych gmin — patrz [sekcja 6](#6-sygnał-z-przetargów-publicznych).
4. Przeszukanie katalogów branżowych: [katalog wystawców targów WOD-KAN](https://katalog.targi-wod-kan.pl/wystawcy-wg-grup-towarowych), [wod-kan.biz](https://www.wod-kan.biz/telemetria,katalog-firm,g,4,3), [woda-scieki.com](https://www.woda-scieki.com/firmy), [wodkaneko.pl](https://www.wodkaneko.pl/).

**Jak liczone są „52 pozycje".** Jedna pozycja to jeden podmiot albo jedno wyraźnie wyodrębnione rozwiązanie. Wiersz 48 jest **zbiorczy** i obejmuje czterech dostawców AMI (Diehl Metering, Kamstrup, Itron, BMETERS) potraktowanych łącznie, bo mają identyczny werdykt i identyczne uzasadnienie. Liczba firm jest więc o trzy wyższa niż liczba pozycji; wszystkie statystyki w [sekcji 5](#5-podsumowanie-ilościowe) liczą pozycje, nie firmy.

### 2.2. Ograniczenie metody — przeczytaj przed użyciem tabeli

**W środowisku, w którym powstawał ten dokument, dostęp do pobierania stron (WebFetch) i bezpośredni ruch HTTPS były zablokowane przez politykę sieciową.** Cała weryfikacja odbyła się przez wyszukiwarkę: adresy URL są prawdziwe i pochodzą z indeksu wyszukiwarki, a opisy ofert — z treści indeksowanych stron, ale **żadna strona nie została otwarta i przeczytana w całości, a żaden załącznik PDF nie został pobrany**. Praktyczne konsekwencje:

- Kolumna **Pewność** w tabeli mówi dokładnie o tym: `wysoka` = ustalenie wynika wprost z zaindeksowanej treści strony dostawcy; `średnia` = wynika z treści strony trzeciej (portal branżowy, katalog) opisującej dostawcę; `przypuszczenie` = wywnioskowane z pośrednich przesłanek, wymaga potwierdzenia.
- **Żaden segment docelowy oznaczony `przypuszczenie` nie może być użyty jako argument w rozmowie z klientem** bez wcześniejszego sprawdzenia.
- Ceny i zwycięzców postępowań w większości **nie udało się ustalić** — w takich miejscach jest napisane „nieustalone", zgodnie z zasadą: lepiej luka niż zgadywanie.
- **Nie wykonano weryfikacji rejestrowej (KRS/CEIDG)**, której wymaga brief. Dla dużych, rozpoznawalnych podmiotów to nie ma znaczenia; dla kilkunastu małych firm z kategorii K5 i K1 oznacza, że **nie wiadomo, czy nadal prowadzą działalność**. Zadanie B w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

### 2.3. Czego ten dokument świadomie nie robi

- Nie powtarza profili z [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji) — dla podmiotów już tam opisanych jest odesłanie i **sam werdykt**, bo to jest nowa wartość.
- Nie robi analizy technicznej ani UX — to zakres **B-02** i **B-03**. Lista podmiotów wartych tam dołożenia jest w [sekcji 7](#7-podmioty-warte-pogłębionej-analizy-w-b-02b-03).
- Nie wychodzi poza Polskę. Zagraniczne wzorce to celowo zakres **B-02**. Podmioty zagraniczne pojawiają się tu tylko wtedy, gdy mają **potwierdzoną obecność na polskim rynku** (polski oddział, polskojęzyczna oferta, dystrybutor albo udokumentowane wdrożenia w PL). Dwa wyjątki są oznaczone wprost w tabeli: **Lacroix Sofrel** (wiersz 11) i **Kallipr** (wiersz 52) — obecność w PL nieustalona, zostawione w spisie dlatego, że są istotnym punktem odniesienia, ale **nie liczą się jako potwierdzeni gracze rynku krajowego**.

---

## 3. Kryterium klasyfikacji — test, nie wrażenie

Etykietę nadaje **trzypytaniowy test** oparty wprost na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam) (target: gminy 1000–20000 mieszkańców, 5–15 rozproszonych obiektów; nie target: duże miasta, krajowi operatorzy z gotowym SCADA, gminy z <3 obiektami) i na modelu przychodowym z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody) (2,9–8,3 tys. zł jednorazowo na obiekt + 130–170 zł/mies.).

| # | Pytanie testowe |
|---|---|
| **T1 — produkt** | Czy podmiot sprzedaje **gotowe rozwiązanie monitoringu obiektu**, które mała gmina może kupić bez projektu SCADA i bez prac inżynierskich na miarę? |
| **T2 — rząd wielkości ceny** | Czy koszt na obiekt mieści się w **kilku–kilkunastu tysiącach złotych** jednorazowo (a nie w setkach tysięcy za projekt dla całej sieci)? |
| **T3 — dowód obsługi segmentu** | Czy istnieje **publiczny dowód**, że podmiot obsługuje klientów tej wielkości — referencje z małych gmin, materiały kierowane do gmin, rozstrzygnięte postępowania? |

**Reguła nadawania etykiety:**

- **🔴 Bezpośredni konkurent** — T1, T2 i T3 na „tak". Realnie konkuruje o tego samego klienta, o ten sam budżet i w zbliżonym modelu.
- **🟡 Konkurent pośredni / sąsiedni segment** — co najmniej jedno „nie", **bez** widocznej zdolności lub chęci zmiany. Kolumna **Dlaczego** w tabeli wskazuje, **które** pytanie zawodzi — „jest inny" nie jest uzasadnieniem.
- **🔵 Do obserwacji** — dziś zawodzi T1, T2 lub T3, ale podmiot ma **produkt, kanał sprzedaży i markę**, żeby to zmienić niewielkim kosztem. Przy każdym takim wpisie kolumna **Dlaczego** mówi, **co konkretnie musiałoby się stać**, żeby stał się konkurentem bezpośrednim.
- **⚪ Nieustalone** — brak publicznych informacji wystarczających do rozstrzygnięcia. Zgodnie z ograniczeniami briefu: nie zgadujemy.

**Uwaga o T2.** Prawie nikt na tym rynku nie publikuje cen — jedyny jawny punkt odniesienia to deklaracja UniCloud (1–3 tys. zł rocznie za obiekt, start do ~10 tys. zł), i to też jest deklaracja marketingowa, nie oferta. T2 jest więc dziś oceniane **na podstawie modelu sprzedaży i skali referencyjnych wdrożeń**, a nie na podstawie cenników. To najsłabszy element całego testu i pierwsza rzecz, którą naprawi zadanie A z [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

Ważna uwaga do odczytu: **„pośredni" nie znaczy „nieszkodliwy"**. Integrator AKPiA nie konkuruje z nami produktowo, ale gdy gmina zapyta go o monitoring, dostanie ofertę projektową — i to my musimy umieć wytłumaczyć różnicę. Klasyfikacja mówi o **rywalizacji o ten sam typ zakupu**, nie o tym, kogo można zignorować.

---

## 4. Pełny spis — tabela zbiorcza

Kategorie wg [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku): **K1** chmurowa SCADA abonamentowa · **K2** telemetria przemysłowa i RTU · **K3** kompleksowe smart water · **K4** producenci pomp i przepompowni · **K5** integratorzy AKPiA · **K6** wyspecjalizowane urządzenia IoT.

Model biznesowy: **AB** abonament/SaaS · **CAPEX** sprzedaż sprzętu · **PROJ** wdrożenie projektowe · **USL** usługi.

| # | Podmiot | Kat. | Segment docelowy | Model | Klasyfikacja | Dlaczego (który test) | Źródło | Pewność |
|---|---|---|---|---|---|---|---|---|
| 1 | **UniCloud / Unitronics / Elmark Automatyka** — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K1 | małe gminy i obiekty wod-kan, jawnie adresowane | AB + CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — produkt wprost dla małych gmin, jawny model abonamentowy, >50 lokalizacji w PL | [smart.elmark.com.pl](https://smart.elmark.com.pl/uni/umc/branze/wod-kan), [blog: SCADA dla małej gminy](https://www.elmark.com.pl/blog/system-scada-dla-maej-gminy-czy-to-musi-by-drogie-) | wysoka |
| 2 | **Inwap** (monitoring WWW/SMS, chmura PIK-on) | K1 | przepompownie i obiekty rozproszone, małe podmioty | AB + CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — gotowy monitoring GSM/GPRS z podglądem w przeglądarce, sprzedawany na obiekt | [inwap.pl](https://inwap.pl/produkty/monitoring-www-sms-zdalna-zdalne-gsm-gprs.html) | średnia |
| 3 | **AT SYSTEMS** (systemy monitoringu GSM/GPRS) | K1 | przepompownie, zbiorniki, obiekty komunalne | CAPEX + USL | 🔴 bezpośredni | T1✓T2✓T3✓ — zestaw montowany w istniejącej szafie, alarmy SMS/e-mail, dostęp przez przeglądarkę | [atsystems.pl](https://atsystems.pl/systemy-monitoringu-gsm-gprs) | średnia |
| 4 | **Endress+Hauser Polska** (Netilion Water Network Insights) | K1 | przedsiębiorstwa wod-kan średnie i duże | AB + CAPEX | 🔵 do obserwacji | **T2✗** — cena aparatury procesowej jest poza budżetem małej gminy. *Co musiałoby się stać:* pakiet startowy „czujnik + chmura" poniżej ~10 tys. zł na obiekt — mają już chmurę i 12 biur w Polsce | [pl.endress.com](https://www.pl.endress.com/pl/przemysl/rozwiazania-dla-procesow/system-zarzadzania-siecia-wodociagowa) | wysoka |
| 5 | **Vispena** (zdalny monitoring oczyszczalni, brama InHand + chmura) | K1 | oczyszczalnie i instalacje przemysłowe | PROJ + USL | 🟡 pośredni | **T1✗** — wdrożenie projektowe na konkretnej instalacji, nie produkt z półki | [vispena.pl](https://vispena.pl/zdalny-monitoring-oczyszczalni-sciekow/) | średnia |
| 6 | **JUMO** (smartWARE SCADA w chmurze dla wodociągów) | K1 | zakłady wodociągowe, głównie warstwa procesowa | CAPEX + AB | 🟡 pośredni | **T1✗** (przypuszczenie) — sprzedaje aparaturę i oprogramowanie do zbudowania systemu, nie usługę monitoringu obiektu | [jumo.group — blog](https://www.jumo.group/pl/pl/about-us/blog/scada-system-in-water-utilities) | przypuszczenie |
| 7 | **Inventia** (MT-101/MT-102, DataPortal) — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K2 | przepompownie w całej Polsce; >6000 wdrożeń modułów MT-101 | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — moduł zastępuje sterownik w szafie, platforma DataPortal w abonamencie, skala wdrożeń nie do podważenia | [inventia.pl/wod-kan](https://www.inventia.pl/wod-kan/), [automatykab2b — 6000 przepompowni](https://automatykab2b.pl/prezentacje/41761-ponad-6000-przepompowni-wykorzystuje-moduly-telemetryczne-inventia-mt-101) | wysoka |
| 8 | **PM Ecology** (Aqua Logger Compact / RDR / HS / FLOW) | K2 | punkty pomiarowe sieci wod-kan, obiekty bez zasilania | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — gotowy rejestrator bateryjny z GSM sprzedawany na sztuki, integracja ze SCADA i alarmy SMS | [pmecology.com — woda wodociągowa](https://www.pmecology.com/aplikacja/woda-wodociagowa/), [Aqua Logger Compact](https://www.pmecology.com/produkt/rejestrator-danych-aqua-logger-compact/) | wysoka |
| 9 | **PLUM** (MacR6, MacR6 N, MacIQ WM) | K2 | opomiarowanie rozliczeniowe i bilansowanie sieci | CAPEX | 🟡 pośredni | **T1✗** — rozwiązuje odczyt wodomierza i bilans wody, nie stan techniczny obiektu | [plum.pl](https://plum.pl/en/automatingwatermeterreading/), [karta MacR6 N](https://hsb.com.pl/wp-content/uploads/2021/08/Karta-katalogowa-MacR6N_woda_PLUM_11_2019_v2.pdf) | wysoka |
| 10 | **Teletrans** (moduły telemetryczne przewodowe i radiowe, RMZ) | K2 | integratorzy i producenci szaf — sprzedaż komponentu | CAPEX | 🟡 pośredni | **T1✗** — sprzedaje komponent do zabudowy, gmina nie jest jego klientem końcowym | [teletrans.com.pl](https://teletrans.com.pl/index.php?id=Modu%C5%82y+telemetryczne%2C16) | średnia |
| 11 | **Lacroix Sofrel** (S4W, DL4W) — *obecność na rynku PL nieustalona* | K2 | operatorzy sieci wodociągowych, klasa przemysłowa | CAPEX + PROJ | 🟡 pośredni | **T2✗** — RTU klasy przemysłowej dla operatorów sieci, poziom cenowy poza budżetem gminy. **Zastrzeżenie:** nie potwierdzono dystrybutora ani wdrożeń w PL — nie liczyć jako gracza krajowego bez sprawdzenia | [lacroix-environment.com — SOFREL S4W](https://www.lacroix-environment.com/telemetry-solutions/offers/rtus-data-loggers/sofrel-s4w-rtu/) | przypuszczenie (dla obecności w PL) |
| 12 | **Ovarro** (XiLog 4G, Primeweb/Atrium) — w PL przez **RD Tech** | K2 | operatorzy sieci; monitoring strat i ciśnienia | CAPEX + AB | 🟡 pośredni | **T2✗** — rejestrator wielokanałowy z platformą analityczną wyceniany dla operatorów sieci, sprzedaż przez dystrybutora | [rdtech.pl — XiLog 4G](https://www.rdtech.pl/xilog-4g/), [ovarro.com — data loggers](https://ovarro.com/en/global/solutions/monitoring--control-devices/data-loggers--leak-noise-loggers/data-loggers/2/) | wysoka |
| 13 | **Aksel Sp. z o.o.** | K2 | nieustalone (wystawca targów WOD-KAN, profil telemetryczny) | nieustalone | ⚪ nieustalone | brak danych do rozstrzygnięcia któregokolwiek z testów — zadanie D w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia) | [katalog targów WOD-KAN](https://katalog.targi-wod-kan.pl/firma/aksel-sp-z-o-o-41) | przypuszczenie |
| 14 | **SebaKMT / Sewerin** (loggery szumu i ciśnienia, przez dystrybutorów PL) | K2 | służby eksploatacyjne wodociągów — lokalizacja wycieków | CAPEX + USL | 🟡 pośredni | **T1✗** — narzędzie do jednorazowej lokalizacji wycieku, nie stały monitoring obiektu | [sebakmt.com](https://sebakmt.com/en-us/), [przeciek24.com — loggery](https://przeciek24.com/loggery/) | średnia |
| 15 | **AquaRD** (CellBOX, HydraNET, AquaGIS, SCADA) — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K3 | przedsiębiorstwa wodociągowe miast powiatowych i większe | PROJ + CAPEX | 🟡 pośredni | **T2✗ T3✗** — sprzedaje pakiet SCADA + GIS + model hydrauliczny w modelu projektowym (Dębica: docelowo 16 punktów pomiarowych). **Najwyższa wśród pośrednich zdolność zejścia w dół** — ma własne urządzenia CellBOX µH sprzedawane pojedynczo | [aquard.pl](https://aquard.pl/), [wdrożenie w Dębicy](https://www.wodociagi.debickie.pl/2023/02/09/inteligentny-systemu-zarzadzania-siecia-wodociagowa-i-kanalizacyjna-wdrozony/) | wysoka |
| 16 | **AIUT** (WaterPrime — analityka; systemy zdalnego odczytu LoRa) — WaterPrime w [§5.2.4](./01_plan_biznesowy.md#524-konkurenci-w-obszarze-monitoringu-sieci-i-strat-wody) | K3 | duże miasta i operatorzy z modelem hydraulicznym | PROJ + AB | 🟡 pośredni | **T2✗ T3✗** — wymaga opomiarowania, audytu i modelu hydraulicznego; gmina z 10 obiektami nie ma czego analizować | [waterprime.eu](https://waterprime.eu/), [aiut.com — zdalny odczyt wodomierzy](https://aiut.com/rozwiazania/systemy-smart-city-iot/systemy-zdalnego-odczytu-wodomierzy-i-cieplomierzy/system-zdalnego-odczytu-i-monitoringu-pracy-wodomierzy/) | wysoka |
| 17 | **Future Processing** (SmartFlow, z MPWiK Wrocław) | K3 | duże przedsiębiorstwa wodociągowe; analityka strat w strefach DMA | AB + PROJ | 🟡 pośredni | **T3✗** — produkt zbudowany dla i z dużym MPWiK (~100 urządzeń, kilkadziesiąt stref pomiarowych); mała gmina nie ma na czym go uruchomić | [MPWiK Wrocław — SmartFlow](https://www.mpwik.wroc.pl/pracuj-z-nami/projekty/smartflow/), [IGWP o SmartFlow](https://www.igwp.org.pl/smartflow-czyli-nowoczesna-technologia-w-zarzadzaniu-siecia-wodociagowa/) | wysoka |
| 18 | **Orange Polska** (Smart Water) | K3 | **gminy, miasta i ZWiK — jawnie adresowane**; 29 wdrożeń | AB | 🔵 do obserwacji | **T1✗** — sprzedaje opomiarowanie rozliczeniowe i bilans sieci, nie monitoring stanu obiektu. *Co musiałoby się stać:* dołożenie kanałów procesowych (ciśnienie, poziom, praca pompy) do oferty, którą już sprzedaje gminom. **Najwyższy priorytet obserwacji** — ma markę, kanał do samorządu, abonament i własną sieć IoT naraz | [orange.pl — Smart Water](https://www.orange.pl/duze-firmy/smart-water), [poradnik: zarządzanie siecią wodociągową](https://www.orange.pl/poradnik-dla-firm/rozwiazania-smart/inteligentna-woda-zarzadzanie-wodociagami/) | wysoka |
| 19 | **T-Mobile Polska** (IoT / NB-IoT dla wod-kan) | K3 | przedsiębiorstwa wodociągowe; opomiarowanie stacjonarne | AB | 🔵 do obserwacji | **T1✗** — jak wyżej, dodatkowo brak własnej warstwy aplikacyjnej dla wod-kan. *Co musiałoby się stać:* przejęcie lub partnerstwo z dostawcą platformy obiektowej | [T-Mobile — case study PWiK Kutno](https://biznes.t-mobile.pl/pl/case-study/przedsiebiorstwo-wodociagow-i-kanalizacji-w-kutnie), [24 000 nakładek w Katowicach](https://www.telix.pl/operatorzy/t-mobile/2026/06/t-mobile-polska-wdrozy-24-000-nakladek-iot-do-zdalnego-odczytu-wodomierzy-w-katowicach/) | wysoka |
| 20 | **Veolia Woda Polska** | K3 | duzi operatorzy i miasta, w których Veolia zarządza siecią | USL + PROJ | 🟡 pośredni | **T3✗** — model operatorski dla dużych miast; nie sprzedaje produktu małej gminie | [wodatomy.pl — usługi Veolii dla sektora wodnego](https://wodatomy.pl/strefa-wiedzy/veolia-woda-polska-dzialalnosc/nowe-oblicze-uslug-dla-sektora-wodnego/) | średnia |
| 21 | **SUEZ Polska** (urządzenia CellBOX) | K3 | przedsiębiorstwa wodociągowe średnie i duże | PROJ + CAPEX | 🟡 pośredni | **T2✗ T3✗** — sprzedaż w ramach większych kontraktów operatorskich i modernizacyjnych | [suez.com — urządzenia CellBOX](https://www.suez.com/pl-pl/polska/inteligentne-rozwiazania/urzadzenia-cellbox) | średnia |
| 22 | **GlobTree** (GlobeOMS — chmura telemetryczna, nakładki) | K3 | wodociągi i zarządcy mediów; wejście „od jednego urządzenia" | AB + CAPEX | 🔵 do obserwacji | **T1✗** — chmura do opomiarowania mediów, nie do stanu obiektu. *Co musiałoby się stać:* dołożenie wejść procesowych do istniejącej chmury; próg wejścia „od jednej sztuki" już mają | [globtree.pl — firma](https://globtree.pl/firma-globtree/), [globtree.pl — telemetria](https://globtree.pl/telemetria-korzysci-ktorych-szukasz/) | średnia |
| 23 | **Hydro-Vacuum** — profil w [§5.2.3](./01_plan_biznesowy.md#523-konkurenci-związani-z-producentami-pomp-i-szaf) | K4 | gminy kupujące pompy i tłocznie tego producenta | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — monitoring wchodzi razem z pompą, **więc gmina nie podejmuje osobnej decyzji zakupowej i nie ma momentu na porównanie ofert** | [hydro-vacuum.com.pl — monitoring](https://www.hydro-vacuum.com.pl/monitoring.php) | wysoka |
| 24 | **Metalchem-Warszawa** (MRT-GSM, MRM-GPRS) — profil w [§5.2.3](./01_plan_biznesowy.md#523-konkurenci-związani-z-producentami-pomp-i-szaf) | K4 | gminy z przepompowniami i rozdzielnicami tego producenta | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — jak wyżej; wariant SMS obniża próg cenowy poniżej naszego | [metalchemsa.com.pl — monitoring przepompowni](https://www.metalchemsa.com.pl/monitoring-przepompowni/) | wysoka |
| 25 | **Bartosz Sp.j.** (systemy monitorowania GSM/GPRS) | K4 | obiekty wod-kan; **deklarowana zgodność z urządzeniami innych producentów** | CAPEX | 🔴 bezpośredni | T1✓T2✓T3✓ — deklaruje pracę z cudzym sprzętem, więc nie jest ograniczony do własnych obiektów; to atakuje wprost naszą przewagę „neutralności sprzętowej" | [instalacjebudowlane.pl — systemy GSM/GPRS Bartosz](https://www.instalacjebudowlane.pl/9333-26-76-systemy-monitorowania-gsm-gprs--zdalny-nadzor-nad-obiektami-i-instalacjami.html) | średnia |
| 26 | **Wilo Polska** (Wilo-Nexos, Nexos NET Intelligence) | K4 | użytkownicy pompowni i tłoczni Wilo, w tym gminne; kanalizacja ciśnieniowa | CAPEX + AB | 🔴 bezpośredni *(w obrębie własnego sprzętu)* | T1✓T2✓T3✓ — monitoring sprzedawany jako **usługa serwisowa dokupywana do pompowni**, więc trafia w ten sam budżet eksploatacyjny. Ograniczenie: tylko obiekty z pompami Wilo | [wilo.com — monitoring pompowni](https://wilo.com/pl/pl/Serwis/Oferta-serwisowa/Monitoring-pompowni-t%C5%82oczni-%C5%9Bciek%C3%B3w-i-zestaw%C3%B3w-pompowych/), [Nexos NET Intelligence](https://wilo.com/pl/pl/Narz%C4%99dzia/Aplikacje-do-zarz%C4%85dzania-prac%C4%85-pomp/Nexos-NET-Intelligence/) | wysoka |
| 27 | **Hydro-Partner** — profil w [§5.2.3](./01_plan_biznesowy.md#523-konkurenci-związani-z-producentami-pomp-i-szaf) | K4 | obiekty wymagające projektu SCADA i modernizacji | PROJ | 🟡 pośredni | **T1✗** — realizuje projekt SCADA na miarę, wycena per wdrożenie | [hydro-partner.pl — monitoring](https://hydro-partner.pl/automatyka-2/monitoring/) | wysoka |
| 28 | **Ecol-Unicon** (Bumerang SMART) | K4 | zarządcy wód opadowych, retencji i przepompowni — głównie miasta | PROJ + AB | 🟡 pośredni | **T2✗ T3✗** — celuje w retencję i wody opadowe w miastach, skala projektowa; sterowanie, nie tylko obserwacja | [ecol-unicon.com — inteligentne monitorowanie sieci](https://ecol-unicon.com/blog/inteligentne-monitorowanie-sieci-wodno-kanalizacyjnych/) | wysoka |
| 29 | **Xylem Poland** (systemy monitorujące, ekosystem Flygt) | K4 | większe przepompownie i obiekty z pompami Xylem | CAPEX + PROJ | 🟡 pośredni | **T2✗ T3✗** — monitoring przy pompowniach klasy miejskiej; brak oferty skrojonej na obiekt małej gminy (inaczej niż Wilo, wiersz 26) | [xylem.com — systemy monitorujące](https://www.xylem.com/pl-pl/products-services/pumps-packaged-pump-systems/monitoring-control-equipment/monitoring--supervision/monitoring-systems/) | wysoka |
| 30 | **Wobet-Hydret** (przepompownia z modułem GSM) | K4 | obiekty przydomowe i małe przepompownie | CAPEX | 🟡 pośredni | **T3✗** — moduł GSM przy obiektach przydomowych; nie obsługuje sieci obiektów gminnych | [wobet-hydret.pl — przepompownia z modułem GSM](https://www.wobet-hydret.pl/blog/dobre-rozwiazanie-przepompownia-z-modulem-gsm) | średnia |
| 31 | **Grundfos, KSB** (monitoring w ekosystemie własnych pomp) | K4 | nieustalone dla rynku PL | nieustalone | ⚪ nieustalone | brak polskojęzycznego źródła potwierdzającego ofertę monitoringu dla gmin — **luka istotna**, bo dotyczy zagrożenia „monitoring jako dodatek do pompy"; zadanie F w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia) | — | przypuszczenie |
| 32 | **NASUS** — profil w [§5.2.2](./01_plan_biznesowy.md#522-najważniejsi-konkurenci-bezpośredni) | K5 | wodociągi, energetyka, ciepłownictwo — wdrożenia projektowe | PROJ + USL | 🟡 pośredni | **T1✗** — model projektowy, brak produktu z cennikiem | [nasus.pl](http://www.nasus.pl/index.php) | wysoka |
| 33 | **MEDAS** (automatyka i teleinformatyka, >30 lat) | K5 | SUW, oczyszczalnie, przepompownie — projektowo | PROJ | 🟡 pośredni | **T1✗** — jak wyżej | [medas.com.pl](https://medas.com.pl/) | średnia |
| 34 | **Hartimex** | K5 | oczyszczalnie, przepompownie, SUW — PLC/HMI/SCADA, prefabrykacja szaf | PROJ | 🟡 pośredni | **T1✗** — jak wyżej | [hartimex.pl](https://hartimex.pl/) | średnia |
| 35 | **JR Technika s.c.** | K5 | stacje uzdatniania wody — szafy sterownicze, PLC | PROJ | 🟡 pośredni | **T1✗** — jak wyżej | [jrtechnika.pl](https://jrtechnika.pl/pages/automatyzacja.html) | średnia |
| 36 | **Intelcon** (Nowy Sącz) | K5 | AKPiA dla SUW i oczyszczalni — **region małopolski** | PROJ | 🟡 pośredni | **T1✗** — model projektowy. **Ale: działa w województwie pierwszego klienta** — równie prawdopodobny partner montażowy co konkurent (patrz „partnerstwo montażowo-integracyjne" w [CONTEXT.md](./CONTEXT.md)) | [intelcon.pl — AKPiA](https://intelcon.pl/akpia/) | średnia |
| 37 | **PiA-ZAP** | K5 | modernizacje AKPiA SUW, w tym wątek cyberbezpieczeństwa | PROJ | 🟡 pośredni | **T1✗** — model projektowy; wyróżnia się kompetencją cyber, istotną przy NIS2 | [piazap.com.pl — case study SUW Sekuła](https://piazap.com.pl/2025/12/05/modernizacja-akpia-suw-sekula-case-study/) | średnia |
| 38 | **EkoWodrol** (Koszalin) | K5 | obiekty wod-kan — automatyka w ramach większych realizacji | PROJ | 🟡 pośredni | **T1✗** — automatyka jako część większego kontraktu budowlanego | [ekowodrol.pl — automatyka](https://ekowodrol.pl/uslugi/automatyka/) | średnia |
| 39 | **AMEplus** | K5 | obiekty hydrotechniczne i przemysłowe | PROJ | 🟡 pośredni | **T1✗** — model projektowy | [ameplus.pl — obiekty hydrotechniczne](https://www.ameplus.pl/hydrotechnical-objects/) | średnia |
| 40 | **Metria** | K5 | monitoring obiektów wodno-kanalizacyjnych — projekty systemów | PROJ | 🟡 pośredni | **T1✗** — model projektowy | [metria.pl — monitoring](https://metria.pl/automatyka/monitoring/) | średnia |
| 41 | **APS** | K5 | monitoring parametrów technologicznych przepompowni i wodociągów | PROJ | 🟡 pośredni | **T1✗** — realizacje na zamówienie (m.in. dla wodociągów Łodzi) | [AutomatykaOnline — system monitoringu dla przepompowni i wodociągów](https://automatykaonline.pl/Aplikacje/Wod-Kan/System-monitoringu-dla-przepompowni-i-wodociagow) | średnia |
| 42 | **Sauka Baj** | K5 | systemy telemetryczne i dyspozytorskie, studnie głębinowe | PROJ | 🟡 pośredni | **T1✗** — kompleksy dyspozytorskie budowane na zamówienie | [saukabaj.pl](https://saukabaj.pl/systemy-dyspozytorskie-telemetryczne) | średnia |
| 43 | **Tech-Pomp Serwis** | K5 | AKPiA przy obiektach pompowych | PROJ + USL | 🟡 pośredni | **T1✗** — usługa serwisowo-inżynierska | [transferwody.pl — AKPiA](https://transferwody.pl/akpia-aparatura-kontrolno-pomiarowa-i-automatyka) | średnia |
| 44 | **Hawle.live** — profil w [§5.2.4](./01_plan_biznesowy.md#524-konkurenci-w-obszarze-monitoringu-sieci-i-strat-wody) | K6 | wodociągi monitorujące sieć i armaturę; forma produktowa | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — gotowa stacja Hawle.live BOX + aplikacja + mapa; kupowane jako produkt, nie projekt | [hawle.com — Hawle.live](https://www.hawle.com/pl/dla-klienta/serwis-hawle/hawle-live) | wysoka |
| 45 | **Efento** (Kraków — rejestratory NB-IoT ciśnienia i poziomu + Efento Cloud) | K6 | dowolny klient szukający taniego, bateryjnego pomiaru z chmurą | CAPEX + AB | 🔴 bezpośredni | T1✓T2✓T3✓ — rejestrator + chmura dostępne od jednej sztuki, bez bramek i infrastruktury. **Ograniczenie:** brak integracji z istniejącym PLC i szafą, więc konkuruje tylko o obiekty najprostsze | [efento.pl](https://efento.pl/), [rejestrator wysokiego ciśnienia NB-IoT](https://efento.pl/product/bezprzewodowy-rejestrator-wysokiego-cisnienia/) | wysoka |
| 46 | **CTHINGS.CO** | K6 | dziś: Edge AI i ekspansja poza PL; wod-kan był pilotażem w Skandynawii | AB + PROJ | 🔵 do obserwacji | **T3✗** — brak wdrożeń wod-kan na rynku krajowym. *Co musiałoby się stać:* powrót do wod-kan w Polsce; mają kompetencję i finansowanie, ale kierunek rozwoju wskazuje na Amerykę Płn. | [ISBtech — wdrożenia wod-kan w Skandynawii](https://www.isbtech.pl/2021/12/polski-startup-cthings-co-wdraza-nowe-rozwiazania-dla-gospodarki-wodno-kanalizacyjnej-w-skandynawii/), [Platforma Przemysłu Przyszłości](https://przemyslprzyszlosci.gov.pl/iot-w-zarzadzaniu-systemem-wodno-kanalizacyjnym/) | średnia |
| 47 | **Apator Powogaz / Apator Telemetria** | K6 | opomiarowanie rozliczeniowe wodociągów (AMR/AMI) | CAPEX | 🟡 pośredni | **T1✗** — odczyt wodomierza to inne zadanie niż monitoring stanu obiektu | [apator.com — system radiowy AMR](https://www.apator.com/nasze-rozwiazania/woda-i-cieplo/system-zdalnego-odczytu-mediow/system-radiowy/amr), [profil Apator Telemetria](https://www.woda-scieki.com/firmy/2171-apator-telemetria-sp-z-o-o-/produkty) | wysoka |
| 48 | **Dostawcy AMI wodomierzowego: Diehl Metering, Kamstrup, Itron, BMETERS** *(wiersz zbiorczy — 4 firmy)* | K6 | opomiarowanie rozliczeniowe | CAPEX + AB | 🟡 pośredni | **T1✗** — jak wyżej; wspólny werdykt, bo wspólne uzasadnienie | [Polski Instalator — przegląd systemów zdalnego odczytu](https://www.polskiinstalator.com.pl/artykuly/instalacje-sanitarne/2534-systemy-zdalnego-odczytu-wodomierzy) | średnia |
| 49 | **KROHNE Polska** | K6 | pomiar na ujęciach i studniach; rozwiązania bezprzewodowe | CAPEX | 🟡 pośredni | **T1✗** — dostarcza aparaturę, system składa integrator | [pl.krohne.com — zdalny monitoring studni](https://pl.krohne.com/pl/rozwiazania/rozwiazania-pomiarow-bezprzewodowych-zdalnych/pomiar-wody-mozliwoscia-zdalnego-przesylania-danych/zdalny-monitoring-studni-wodnych-zasilania) | wysoka |
| 50 | **METERING (Anna Moder)** | K6 | doradztwo i dobór monitoringu sieci, sprzedaż wodomierzy | USL + CAPEX | 🟡 pośredni | **T1✗** — doradza przy wyborze cudzych rozwiązań, nie ma własnej platformy. Potencjalny kanał dotarcia, nie konkurent | [metering.com.pl — monitoring sieci](https://metering.com.pl/uslugi/monitoring-sieci/) | średnia |
| 51 | **WODOSERWIS** | K6 | diagnostyka sieci i lokalizacja wycieków | USL | 🟡 pośredni | **T1✗** — usługa jednorazowa, nie stały monitoring | [wodoserwis.pl — monitoring](https://www.wodoserwis.pl/monitoring.htm) | średnia |
| 52 | **Kallipr** — wzorzec zagraniczny z [§5.2.5](./01_plan_biznesowy.md#525-zagraniczny-wzorzec-produktowy); *obecność na rynku PL nieustalona* | K6 | rynki AU/NZ i inne | CAPEX + AB | ⚪ nieustalone (poza mapą krajową) | nie da się zastosować testu do rynku, na którym nie potwierdzono obecności; pozostaje wzorcem produktowym dla B-02, nie graczem krajowym | [kallipr.com](https://kallipr.com/solutions/pump-station-monitoring/) | wysoka |

---

## 5. Podsumowanie ilościowe

| Klasyfikacja | Liczba | Udział | Które to są |
|---|---|---|---|
| 🔴 **Bezpośredni konkurent** | **11** | 21% | UniCloud/Elmark, Inwap, AT Systems, Inventia, PM Ecology, Hydro-Vacuum, Metalchem-Warszawa, Bartosz, Wilo Polska, Hawle.live, Efento |
| 🟡 **Pośredni / sąsiedni segment** | **33** | 63% | m.in. AquaRD, AIUT/WaterPrime, Future Processing, Veolia, SUEZ, Hydro-Partner, Ecol-Unicon, Xylem, PLUM, Lacroix Sofrel, Ovarro, cały ogon integratorów AKPiA (12 pozycji), dostawcy AMI |
| 🔵 **Do obserwacji** | **5** | 10% | Orange Polska, T-Mobile Polska, GlobTree, Endress+Hauser Polska, CTHINGS.CO |
| ⚪ **Nieustalone** | **3** | 6% | Aksel, Grundfos/KSB, Kallipr (obecność w PL) |
| **Razem** | **52** | 100% | |

Rozkład po kategoriach z [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku):

| Kategoria | Pozycji | Bezpośrednich | Komentarz |
|---|---|---|---|
| K1 — chmurowa SCADA abonamentowa | 6 | 3 | Najgęstsza konkurencja względem naszego modelu. UniCloud nie jest sam. |
| K2 — telemetria przemysłowa i RTU | 8 | 2 | Dojrzały sprzęt, wysoka poprzeczka jakościowa; większość celuje wyżej niż my. |
| K3 — kompleksowe smart water | 8 | 0 | **Zero bezpośrednich.** Wszyscy celują w miasta i duże ZWiK — za to trzej mają zdolność zejścia w dół. |
| K4 — producenci pomp i przepompowni | 9 | 4 | **Najbardziej niedoszacowane zagrożenie.** Monitoring wchodzi razem z pompą, bez osobnej decyzji zakupowej. |
| K5 — integratorzy AKPiA | 12 | 0 | Długi ogon; konkurują ofertą projektową, nie produktem. Spis reprezentatywny, nie wyczerpujący — patrz niżej. |
| K6 — wyspecjalizowane IoT | 9 | 2 | Efento i Hawle.live pokazują dwa różne sposoby na produktowe podejście do tego samego problemu. |

**Uwaga o kompletności K5.** Kategoria integratorów AKPiA jest z natury **niepoliczalna** — to setki lokalnych firm elektrycznych i automatycznych, z których większość nie prowadzi widocznej działalności marketingowej. Dwanaście pozycji w tabeli to **próbka reprezentatywna dobrana tak, żeby pokryć różne modele działania i różne regiony** (w tym Intelcon z Nowego Sącza jako przykład z województwa pierwszego klienta), a nie spis. Deklarowanie tu „pełnej mapy" byłoby nieuczciwe. Pozostałe pięć kategorii traktujemy jako spis kompletny **w granicach podmiotów widocznych publicznie** — z zastrzeżeniem, że katalogi branżowe (wod-kan.biz, katalog targów WOD-KAN) nie zostały przejrzane pozycja po pozycji, bo były niedostępne; patrz zadanie D w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

---

## 6. Sygnał z przetargów publicznych

To jest źródło, którego [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji) nie użyła: nie to, co firma o sobie mówi, tylko **co gminy faktycznie kupują i za ile**.

### 6.1. Co udało się ustalić

| Zamawiający | Przedmiot | Skala / kwota | Region | Źródło |
|---|---|---|---|---|
| **Gmina Gidle** | „Inteligentne zarządzanie i monitorowanie infrastrukturą wodociągową" — tryb art. 132 PZP (próg unijny) | **1 452 626,11 zł** — *źródło nie rozstrzyga jednoznacznie, czy to wartość projektu czy kwota dofinansowania; do potwierdzenia*. Wadium 22 000 zł; oferty do 12.06.2026 | łódzkie | [BIP Gidle](https://bip.gidle.pl/?bip=2&cid=108&id=1833) |
| **Gmina Zaklików** | Sterowanie, monitoring i wizualizacja **25 przepompowni ścieków** + ujęcie wody Karkówka | kwota nieustalona; dofinansowanie FEPK.02, umowa z 27.06.2024 | **podkarpackie** | [przetargi.egospodarka.pl](https://www.przetargi.egospodarka.pl/20031852601_Wdrozenie-systemu-sterowania-monitoringu-i-wizualizacji-parametrow-pracy-pompowni-sciekow-w-aglomeracji-Zaklikow-oraz-ujecia-wody-pitnej-Karkowka-w-Gminie-Zaklikow_2025_2.html), [UG Zaklików](https://www.zaklikow.pl/asp/podpisanie-umowy-o-dofinansowanie-projektu,2,artykul,1,3079) |
| **MZWiK Myślenice** | „Wdrożenie inteligentnego systemu zarządzania siecią wodociągową" jako element projektu (modernizacja sieci + 2 SUW + PV) | projekt ~**21 mln zł**, dofinansowanie ~12 mln zł; oferty do 24.08.2026 | **małopolskie** | [MZWiK Myślenice](https://www.mzwikmyslenice.com.pl/2026/07/23/przetarg-wdrozenie-inteligentnego-systemu-zarzadzanie-siecia-wodociagowa-dla-miejskiego-zakladu-wodociagow-i-kanalizacji-sp-z-o-o-w-myslenicach/) |
| **PWiK Oświęcim** | „Wdrożenie Inteligentnego Systemu Zarządzania Siecią Wodociągową" — postępowanie **rozstrzygnięte** | kwota i wykonawca nieustalone | **małopolskie** | [PWiK Oświęcim](https://pwik.oswiecim.pl/Wdrozenie-Inteligentnego-Systemu-Zarzadzania-Siecia-Wodociagowa-(rozstrzygniety)-126.html) |
| **Wodociągi Dębickie** | Inteligentny system zarządzania siecią wod-kan: SCADA, AquaGIS, model hydrauliczny; **docelowo 16 punktów pomiarowych** | **wykonawca: AquaRD Sp. z o.o.**, umowa 3.02.2022, zakończenie wdrożenia XII 2022; kwota nieustalona | **podkarpackie** | [Wodociągi Dębickie](https://www.wodociagi.debickie.pl/2023/02/09/inteligentny-systemu-zarzadzania-siecia-wodociagowa-i-kanalizacyjna-wdrozony/), [Inżynieria.com](https://inzynieria.com/wodkan/wiadomosci/64586,debica-zarzadzanie-sieciami-wodno-kanalizacyjnymi-bedzie-cyfrowe) |
| **Gmina Ełk** | Budowa systemu monitoringu przepływu i ciśnienia w wybranych punktach sieci — **oraz osobne postępowanie na 1 (jeden) punkt pomiarowy** | kwoty nieustalone; wybór oferty 26.03.2025 | warmińsko-mazurskie | [BIP Gmina Ełk — system](https://bip.elk.gmina.pl/budowa-systemu-monitoringu-przeplywu-i-cisnienia-w-wybranych-punktach-sieci-wodociagowej-na-terenie-gminy-gmina-elk.html), [BIP — 1 punkt pomiarowy](https://bip.elk.gmina.pl/budowa-1-punktu-pomiarowego-systemu-monitoringu-przeplywu-i-cisnienia-sieci-wodociagowej-na-terenie-gminy-gmina-elk.html) |
| **MZK Stalowa Wola** | Szczegółowy opis systemu monitorowania przepompowni (załącznik SIWZ) | — | **podkarpackie** | [BIP MZK Stalowa Wola (PDF)](https://bip.mzk.stalowa-wola.pl/download/193/33045/Zalaczniknr1-Szczegolowyopis-Monitoringprzepompowni.pdf) |
| **Gminy Jabłoń, Lubiszyn, Pieniężno** | „System monitoringu i wizualizacji przepompowni ścieków w technologii GPRS" — **niemal identyczny opis w trzech niepowiązanych gminach** | — | lubelskie, lubuskie, warmińsko-mazurskie | [UG Jabłoń (PDF)](https://ugjablon.bip.lubelskie.pl/upload/pliki/Zal._Nr_11_do_SIWZ_-_System_monitoringu_i_wizualizacji_przepompowni_sciekow.pdf), [Lubiszyn (PDF)](https://www.lubiszyn.pl/asp/pliki/aktualnosci/opis_monitoringu.pdf), [BIP Pieniężno](https://bip.pieniezno.pl/attachments/download/2294) |

### 6.2. Cztery wnioski, które zmieniają sposób patrzenia na rynek

**1. Gminy kupują monitoring w rozmiarze „jeden punkt", nie tylko „cały system".** Gmina Ełk prowadziła osobne postępowanie na **jeden punkt pomiarowy**. To potwierdza założenie z [ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md) o rozliczeniu per obiekt i pokazuje, że wejście do gminy nie wymaga wygrania dużego przetargu — wystarczy być tańszym i szybszym na jednym obiekcie. To najkorzystniejsza dla nas obserwacja w całym dokumencie.

**2. Krąży ustandaryzowany opis przedmiotu zamówienia.** Trzy niepowiązane gminy (Jabłoń, Lubiszyn, Pieniężno) używają praktycznie tego samego dokumentu „System monitoringu i wizualizacji przepompowni ścieków w technologii GPRS". Ustalenie: **specyfikacje są kopiowane między gminami i opisują technologię** (GPRS, moduł telemetryczny w szafie), a nie efekt. *Wniosek (nie ustalenie): jeśli nasz gateway nie mieści się w takim opisie, wypadamy formalnie mimo lepszego rozwiązania.* Konsekwencja praktyczna jest handlowa, nie produktowa — trzeba umieć zaproponować gminie gotową treść opisu przedmiotu zamówienia, zanim skopiuje cudzą.

**3. Duże pieniądze na monitoring w małych gminach istnieją i pochodzą z dotacji.** Gidle: ~1,45 mln zł na monitoring infrastruktury wodociągowej w gminie wiejskiej, w trybie unijnym. Zaklików: 25 przepompowni ze środków FEPK. Myślenice: 21 mln zł na projekt z komponentem ISZSW. **Cały ten strumień jest dotacyjny** — co bezpośrednio łączy się ze zleceniem **B-14** (dofinansowania) i jest silnym argumentem, żeby je zrealizować przed pierwszą rozmową handlową.

**4. „Inteligentny System Zarządzania Siecią Wodociągową" (ISZSW) to standardowy pakiet dotacyjny.** Powtarza się w Gidlach, Myślenicach, Oświęcimiu, Dębicy, Skierniewicach i Żywcu. W Dębicy wygrał go **AquaRD** — to jedyne twarde powiązanie „kto wygrywa" z całego przeglądu. Zakres pakietu (monitoring + SCADA + GIS + model hydrauliczny) jest **istotnie szerszy niż nasze MVP**: potwierdza klasyfikację AquaRD jako konkurenta pośredniego i jednocześnie ostrzega — gmina finansująca projekt z dotacji kupi szerszy zakres, bo nie płaci za niego sama.

### 6.3. Czego w przetargach nie udało się ustalić

Zwycięzców i cen jednostkowych **poza przypadkiem Dębicy nie ustalono**. Powód jest metodyczny, nie merytoryczny: informacje o wyborze oferty są publikowane jako pliki PDF na BIP-ach poszczególnych gmin, a w tej sesji nie było możliwości pobierania dokumentów (patrz [§2.2](#22-ograniczenie-metody--przeczytaj-przed-użyciem-tabeli)). **To jest najbardziej wartościowy niedokończony wątek tego zlecenia** — rozpisany jako zadanie A w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

---

## 7. Podmioty warte pogłębionej analizy w B-02/B-03

Podmioty spoza listy 9 z [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji), których dołożenie do zakresu **B-02** (warstwa techniczna) lub **B-03** (UX) da najwięcej. Uszeregowane wg wartości informacji:

| Podmiot | Do którego zlecenia | Dlaczego akurat ten |
|---|---|---|
| **PM Ecology** (Aqua Logger) | B-02 | Polski producent bateryjnych rejestratorów ciśnienia i przepływu z transmisją GSM i integracją SCADA — **najbliższy technicznie odpowiednik naszego gatewaya wśród firm, których plan w ogóle nie wymienia**. Wprost odpowiada na pytanie „czy nasz PoC ma sens sprzętowy". |
| **Inwap (PIK-on)** i **AT Systems** | B-02 + B-03 | Dwaj mało widoczni gracze sprzedający dokładnie nasz produkt (monitoring GSM/GPRS + podgląd w przeglądarce + SMS) małym podmiotom. Jeśli ktoś już rozwiązał problem „mała gmina, mały budżet", to oni. Wart sprawdzenia zwłaszcza interfejs — B-03. |
| **Efento** | B-02 | Wzorzec „urządzenie NB-IoT + chmura + zero infrastruktury pośredniej". Ich model provisioningu i cennik chmury to bezpośredni benchmark dla wymiarów 4 i 6 z B-02. |
| **Lacroix Sofrel (S4W)** | B-02 | Klasa przemysłowa z jawnie komunikowanym cyberbezpieczeństwem i wbudowanym serwerem WWW — punkt odniesienia dla wymiaru 11 (bezpieczeństwo) i dla ścieżki NIS2 z [§6.1](./01_plan_biznesowy.md#61-nis2-i-ksc--wpływ-na-projekt). |
| **Ovarro (XiLog 4G + Primeweb/Atrium)** | B-02 | Rejestrator wielokanałowy 4G + platforma analityczna; dojrzały wzorzec dla formatu telemetrii i retencji (wymiary 5 i 8 B-02). |
| **Ecol-Unicon (Bumerang SMART)** | B-03 | Polski system łączący monitoring z prognozą pogody i planowaniem prac — ciekawy wzorzec dla widoku alarmów i triage'u (wymiar 5 B-03). |
| **Wilo Nexos / Nexos NET Intelligence** | B-02 | Pokazuje, jak wygląda monitoring dorzucony do sprzętu przez producenta pomp — czyli zagrożenie nr 1 z [§5.2.8](./01_plan_biznesowy.md#528-największe-zagrożenia-konkurencyjne) w konkretnej, technicznej postaci. |
| **Endress+Hauser Netilion** | B-02 + B-03 | Duża platforma z rozbudowanym onboardingiem urządzeń; dobry wzorzec dla wymiaru 9 B-03 („ile kroków od urządzenia do danych"). |
| **Orange Smart Water** | B-03 | 29 wdrożeń w gminach i miastach — najlepiej sprawdzony w Polsce interfejs adresowany dokładnie do naszego użytkownika. |

**Świadomie nie rekomendujemy** dokładania do B-02/B-03 firm z kategorii K5 (integratorzy) — nie mają produktu do przeanalizowania, tylko realizacje — ani dostawców AMI (Apator, Diehl, Kamstrup, Itron), bo rozwiązują inne zadanie i ich wzorce nie przeniosą się na monitoring obiektu.

---

## 8. Tropy odrzucone — wygląda jak konkurencja, nie jest

Zapisane po to, żeby nikt nie badał ich drugi raz:

| Podmiot / rozwiązanie | Dlaczego odrzucone |
|---|---|
| **Monitoring Ścieki Polskie** (szambo.online, zlewnia.online) | Dotyczy ewidencji nieczystości ciekłych i obowiązków sprawozdawczych gminy wobec szamb i przydomowych oczyszczalni. Zbieżna terminologia („monitoring", „gmina"), całkowicie inny problem i inny użytkownik. [Źródło](https://monitoring.sciekipolskie.org/) |
| **Simex, Lumel, Aplisens** | Producenci aparatury i rejestratorów — dostawcy **komponentów**, potencjalni poddostawcy, nie konkurenci systemowi. [Simex](https://www.simex.pl/) |
| **SmartFlow jako „konkurent dla gminy"** | Rozwiązuje wykrywanie ukrytych wycieków w strefach pomiarowych dużego miasta (Wrocław, ~100 urządzeń, kilkadziesiąt stref). Gmina z 10 obiektami nie ma na czym go uruchomić. Pozostaje w spisie jako pośredni. |
| **Wody Polskie i ich postępowania** | Występują masowo w wynikach wyszukiwania przetargów, ale dotyczą gospodarki wodnej państwa (RZGW), nie sieci wodociągowych gmin. Szum informacyjny przy przeszukiwaniu przetargów — nie mylić. |

---

## 9. Czego nie udało się ustalić

Uczciwa lista luk. Każda jest rozpisana na konkretne działanie w [sekcji 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

1. **Zwycięzcy i ceny jednostkowe postępowań** (zadanie A) — największa luka. Realna wartość: weryfikacja szacunków kosztowych z [§4.2](./01_plan_biznesowy.md#42-szacunek-kosztów-jednostkowych) danymi z rynku, a nie z cenników komponentów.
2. **Weryfikacja rejestrowa KRS/CEIDG** (zadanie B) — wymagana wprost przez brief, niewykonana. Dotyczy kilkunastu małych firm, przy których nie wiadomo, czy nadal działają.
3. **Członkowie wspierający IGWP** (zadanie C) — [Izba Gospodarcza „Wodociągi Polskie"](https://www.igwp.org.pl/) zrzesza ok. 487 członków, w tym ok. 30 wspierających, czyli w większości **dostawców branżowych**. To najbliższy istniejący odpowiednik oficjalnego spisu dostawców branży.
4. **Katalogi branżowe pozycja po pozycji** (zadanie D) — wod-kan.biz i katalog targów WOD-KAN były niedostępne; **Aksel Sp. z o.o.** pozostaje nierozstrzygnięty właśnie z tego powodu.
5. **Cenniki abonamentowe poza UniCloud** (zadanie E) — żaden inny podmiot z K1 nie publikuje cen. To osłabia test T2 dla całej tabeli.
6. **Grundfos i KSB na rynku polskim** (zadanie F) — obie firmy oferują globalnie monitoring w ekosystemie własnych pomp, ale nie znaleziono polskojęzycznego źródła potwierdzającego ofertę dla gmin. Wilo i Xylem zostały potwierdzone, te dwie nie.
7. **Obecność Lacroix Sofrel i Kallipr na rynku polskim** (zadanie G) — do czasu potwierdzenia nie liczą się jako gracze krajowi.

---

## 10. Co z tego wynika dla planu biznesowego

Trzy korekty do rozważenia w [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji) — **propozycje, nie zmiany wprowadzone**:

1. **[§5.2.8](./01_plan_biznesowy.md#528-największe-zagrożenia-konkurencyjne) punkt 1 („monitoring jako dodatek do nowej szafy lub pompy") jest niedoszacowany.** Cztery z jedenastu konkurentów bezpośrednich to producenci sprzętu dorzucający monitoring (Hydro-Vacuum, Metalchem, Bartosz, Wilo). Ich przewaga nie jest technologiczna — polega na tym, że **gmina nie podejmuje wtedy osobnej decyzji zakupowej**, więc nie ma momentu, w którym mogłaby nas porównać.
2. **[§5.2.9](./01_plan_biznesowy.md#529-wnioski-strategiczne) punkt 3 („najbliższym konkurentem biznesowym jest UniCloud") wymaga uzupełnienia, nie zmiany.** UniCloud jest najbliższy pod względem *modelu*, ale jest też najbardziej widoczny — i dlatego przeceniany. Proponowane brzmienie: *„najbliższym konkurentem modelowym jest UniCloud, ale najczęściej spotykanym w praktyce — telemetria GSM/GPRS montowana przez producenta szafy lub lokalnego integratora"*. **Uwaga: to twierdzenie o częstości jest hipotezą do potwierdzenia zadaniem A**, nie ustaleniem — nie wprowadzać do planu przed weryfikacją.
3. **Do [§5.2.1](./01_plan_biznesowy.md#521-ogólny-obraz-rynku) warto dopisać siódmą kategorię: operatorzy telekomunikacyjni.** Orange Smart Water (29 wdrożeń w gminach i miastach) i T-Mobile nie mieszczą się w żadnej z sześciu istniejących kategorii, a mają naraz to, czego nie ma żaden inny gracz: **markę, kanał sprzedaży do samorządu, model abonamentowy i własną sieć IoT**. Dziś sprzedają opomiarowanie rozliczeniowe, nie monitoring obiektu — ale odległość między jednym a drugim jest mała, a my nie mielibyśmy czym odpowiedzieć na argument „bierzemy to od operatora, który i tak dostarcza nam SIM-y".

---

## 11. Definicja ukończenia — sprawdzenie

Pytanie kontrolne z briefu brzmiało: *„czy da się odpowiedzieć jednym zdaniem i bez wahania na pytanie «czy firma X jest naszą konkurencją» dla każdego podmiotu na liście?"*

Tak — kolumna **Dlaczego** w tabeli podaje gotową odpowiedź dla każdego z 52 wpisów, w postaci: **„Firma X jest / nie jest naszym bezpośrednim konkurentem, bo [zawodzi test T1/T2/T3 — konkretnie: …]"**. Trzy przykłady użycia:

- *„Czy AquaRD to nasza konkurencja?"* → Pośrednia. Sprzedaje pakiet SCADA + GIS + model hydrauliczny w modelu projektowym miastom powiatowym (Dębica) — zawodzi T2 i T3. Ale ma własne urządzenia CellBOX i najwyższą wśród graczy pośrednich zdolność zejścia w dół rynku, więc obserwujemy.
- *„Czy Efento to nasza konkurencja?"* → Bezpośrednia. Sprzedaje bateryjny rejestrator ciśnienia NB-IoT z chmurą, dostępny od jednej sztuki — przechodzi T1, T2 i T3. Nie integruje się jednak z istniejącą automatyką ani PLC, więc konkuruje tylko o obiekty najprostsze.
- *„Czy Orange to nasza konkurencja?"* → Dziś nie, jutro możliwe. Sprzedaje gminom opomiarowanie rozliczeniowe i bilansowanie sieci, nie monitoring obiektu — zawodzi T1. Ale ma markę, kanał do samorządu, model abonamentowy i własną sieć IoT, więc rozszerzenie oferty jest dla nich tanie. Kategoria: do obserwacji, priorytet najwyższy.

**Czego ta definicja ukończenia nie obejmuje:** pytania „a ile oni za to biorą". Na to dokument nie odpowiada dla nikogo poza UniCloud — patrz [sekcja 12](#12-instrukcja-dla-kolejnego-agenta--praca-do-dokończenia).

---

## 12. Instrukcja dla kolejnego agenta — praca do dokończenia

### Warunek wstępny — ustawienie środowiska (do zrobienia przez właściciela projektu, nie przez agenta)

Zadania A–G nie zostały wykonane z jednego powodu: środowisko chmurowe tej sesji miało poziom dostępu sieciowego **Trusted**, który przepuszcza tylko rejestry pakietów, GitHub i API Anthropic. Każdy inny host zwracał 403 z proxy — dotyczyło to `ezamowienia.gov.pl`, wszystkich BIP-ów gmin, KRS, CEIDG i stron dostawców. **Agent nie może tego zmienić z wnętrza sesji i nie wolno mu tego obchodzić** — to ustawienie konfiguracyjne, nie przeszkoda techniczna.

**Co trzeba zmienić:** w [claude.ai/code](https://claude.ai/code) kliknąć ikonę chmury z nazwą środowiska (wiersz nad polem wiadomości) → najechać na środowisko → ikona ustawień → pole **Network access**. Dostępne poziomy: `None`, `Trusted` (obecny), `Full` (dowolna domena), `Custom` (własna lista dozwolonych domen). Szczegóły: [dokumentacja środowisk chmurowych](https://code.claude.com/docs/en/cloud-environments#access-levels).

**Rekomendacja: `Full`, w osobnym środowisku roboczym utworzonym na czas tego zadania.** Powód jest merytoryczny, nie wygodowy: zadanie A wymaga wejścia na BIP-y dowolnych gmin w Polsce, a tej listy **nie da się ułożyć z góry** — każda gmina ma własną domenę. `Custom` z ręczną listą będzie się wykrzaczał na co drugim postępowaniu. Po zakończeniu prac środowisko można zarchiwizować.

Jeśli mimo to potrzebna jest lista `Custom`, poniżej minimum pokrywające wszystko poza BIP-ami gmin:

```text
ezamowienia.gov.pl
*.ezamowienia.gov.pl
przetargi.egospodarka.pl
biznes-polska.pl
atlasprzetargow.pl
przetargi.info
portalzp.pl
wyszukiwarka-krs.ms.gov.pl
aplikacja.ceidg.gov.pl
rejestr.io
igwp.org.pl
wod-kan.biz
*.targi-wod-kan.pl
woda-scieki.com
wodkaneko.pl
```

**Uwaga o momencie zmiany:** konfiguracja środowiska jest wczytywana przy starcie sesji, a nie w trakcie — zmiana poziomu dostępu **nie odblokuje sieci w sesji już uruchomionej**. Po zmianie trzeba założyć nową sesję. Zmiana listy dozwolonych hostów powoduje też ponowne uruchomienie skryptu startowego i przebudowę cache środowiska.

**Weryfikacja na starcie nowej sesji — jedna komenda:**

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://ezamowienia.gov.pl/
```

`200` — można zaczynać. `000` z komunikatem `CONNECT tunnel failed, response 403` — polityka nadal blokuje, wróć do ustawień środowiska. **Nie próbuj obchodzić blokady** (własne proxy, `HTTPS_PROXY`, wyłączenie weryfikacji TLS) — to naruszenie polityki organizacji, a nie sprytne obejście.

**Co już jest w środowisku i czego nie trzeba instalować:** Chromium dla Playwrighta (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, zmienna `PLAYWRIGHT_BROWSERS_PATH` ustawiona — **nie uruchamiaj `playwright install`**). Bibliotek do czytania PDF-ów nie ma, ale `pypi.org` jest dostępne niezależnie od polityki sieciowej, więc `pip install pdfplumber` zadziała nawet przy poziomie `Trusted`.

**Alternatywa, jeśli zmiana polityki jest niemożliwa:** wykonać zadania A–G lokalnie w terminalowym Claude Code (tam nie ma tego proxy) albo podpiąć konektor MCP do pobierania stron — ruch konektorów idzie przez serwery Anthropic i **nie podlega liście dozwolonych domen** środowiska.

**Zasady obowiązujące we wszystkich zadaniach:** dokument po polsku · każdy nowy wpis z linkiem do źródła i datą sprawdzenia · „nieustalone" zamiast zgadywania · **gmina pilotażowa pozostaje anonimowa** (pisz „województwo małopolskie/podkarpackie", nigdy nazwy gminy, nawet jeśli natrafisz na nią w dokumentach przetargowych) · nie przepisywać profili z [§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji).

### Zadanie A — ceny i zwycięzcy postępowań *(priorytet 1, największa wartość)*

**Cel:** zamienić hipotezę z [§1](#1-odpowiedź-w-jednym-akapicie) w ustalenie i podeprzeć albo obalić szacunki z [§4.2](./01_plan_biznesowy.md#42-szacunek-kosztów-jednostkowych) cenami z realnego rynku.

**Gdzie:**
1. [e-Zamówienia — tablica ogłoszeń BZP](https://ezamowienia.gov.pl/mo-client-board/bzp/list) — **to aplikacja JS (SPA)**: zwykłe pobranie HTML zwróci pustą powłokę. Użyj Playwrighta, poczekaj na wyrenderowanie tabeli wyników i przeklikaj paginację.
2. BIP-y gmin z tabeli [§6.1](#61-co-udało-się-ustalić) — tam leżą pliki „Informacja o wyborze najkorzystniejszej oferty" (PDF).
3. Agregatory jako uzupełnienie: [Grupa Biznes Polska — branża monitoring kanalizacji i wodociągów](https://www.biznes-polska.pl/branze/455313/), [Atlas Przetargów](https://atlasprzetargow.pl/), [przetargi.egospodarka.pl](https://www.przetargi.egospodarka.pl/).

**Czego szukać — frazy sprawdzone w tym zleceniu (używaj dosłownie):** `monitoring i wizualizacja przepompowni`, `system telemetrii`, `inteligentny system zarządzania siecią wodociągową`, `monitoring przepływu i ciśnienia`, `zdalny nadzór przepompowni`, `monitoring stacji uzdatniania wody`. Dodatkowo przeszukaj po kodach CPV — **najpierw zweryfikuj kody w oficjalnym słowniku CPV, nie przyjmuj ich z pamięci**; interesują nas kody z rodzin „telemetryczne systemy monitorowania", „systemy sterowania i kontroli", „usługi instalowania systemów sterowania".

**Punkty startowe (już zidentyfikowane, zacznij od nich):** Gmina Gidle · Gmina Ełk (dwa osobne postępowania) · Gmina Zaklików · PWiK Oświęcim (**rozstrzygnięty — najszybszy wynik**) · MZWiK Myślenice · MZK Stalowa Wola · Gmina Bobrowo · Świnoujście.

**Co wyciągnąć z każdego postępowania — dokładnie te pola:**

| Pole | Po co |
|---|---|
| zamawiający + liczba mieszkańców gminy | żeby wiedzieć, czy to nasz segment SAM czy nie |
| liczba obiektów objętych zamówieniem | mianownik do przeliczenia na cenę za obiekt |
| kwota, jaką zamawiający zamierza przeznaczyć | górna granica budżetu w tym segmencie |
| **ceny wszystkich złożonych ofert**, nie tylko wygranej | rozrzut cen mówi więcej niż jedna liczba |
| **nazwa zwycięzcy + jego NIP** | to jest odpowiedź na „kto naprawdę wygrywa" |
| źródło finansowania (dotacja? jaki program?) | wejście do B-14 |
| data | bez niej dana jest bezwartościowa |

**Wynik do policzenia:** `cena wygranej oferty ÷ liczba obiektów` = **realna cena rynkowa za obiekt**. Porównaj ją z 2,9–8,3 tys. zł z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody). Jeśli rynek płaci istotnie więcej — mamy większą przestrzeń cenową, niż zakłada plan. Jeśli mniej — trzeba zrewidować model.

**Próg wystarczalności:** minimum **15 rozstrzygniętych postępowań**, w tym **minimum 5 z małopolskiego lub podkarpackiego**. Poniżej tego progu nie wyciągaj wniosków o „typowych cenach" — napisz, ile zebrałeś.

### Zadanie B — weryfikacja rejestrowa KRS/CEIDG *(priorytet 2)*

**Cel:** upewnić się, że wpisy w tabeli to firmy, które **faktycznie istnieją i działają** — brief wymaga tego wprost, a w tej wersji dokumentu tego nie zrobiono.

**Gdzie:** [wyszukiwarka KRS](https://wyszukiwarka-krs.ms.gov.pl/) (spółki) · [CEIDG](https://aplikacja.ceidg.gov.pl/) (jednoosobowe i s.c.) · [rejestr.io](https://rejestr.io/) jako szybsza nakładka na KRS.

**Kogo sprawdzić — dokładnie te pozycje z tabeli** (małe podmioty, przy których ryzyko „firma już nie działa" jest realne): Inwap (2) · AT SYSTEMS (3) · Vispena (5) · PM Ecology (8) · Teletrans (10) · **Aksel (13)** · Bartosz Sp.j. (25) · Wobet-Hydret (30) · MEDAS (33) · Hartimex (34) · JR Technika s.c. (35) · Intelcon (36) · PiA-ZAP (37) · AMEplus (39) · Metria (40) · APS (41) · Sauka Baj (42) · Tech-Pomp Serwis (43) · Efento (45) · METERING Anna Moder (50) · WODOSERWIS (51).

**Co zapisać przy każdej:** NIP/KRS · rok rozpoczęcia działalności · **status (aktywna / zawieszona / wykreślona)** · przeważające PKD · jeśli dostępne w KRS: przychód i zatrudnienie (mówią, czy to firma jednoosobowa czy zespół).

**Co z tym zrobić:** firmę wykreśloną albo zawieszoną **usuń z tabeli i przenieś do [sekcji 8](#8-tropy-odrzucone--wygląda-jak-konkurencja-nie-jest)** z adnotacją; przy pozostałych podnieś Pewność o jeden poziom. **Pamiętaj wtedy przeliczyć wszystkie sumy** — patrz „Kontrola spójności" niżej.

### Zadanie C — członkowie wspierający IGWP *(priorytet 3)*

**Gdzie:** [igwp.org.pl](https://www.igwp.org.pl/) → sekcja członków; szukaj listy **członków wspierających** (ok. 30 podmiotów, w odróżnieniu od ~454 członków zwyczajnych, którzy są odbiorcami, nie dostawcami).
**Cel:** to najbliższy istniejący odpowiednik oficjalnego spisu dostawców branży. Każdą firmę z tej listy, której nie ma w tabeli, dopisz i zaklasyfikuj testem T1–T3.
**Jeśli lista nie jest publiczna:** zanotuj to jako „nieustalone" i nie kombinuj — nie kontaktuj się z Izbą w imieniu projektu bez zgody właściciela produktu.

### Zadanie D — katalogi branżowe pozycja po pozycji *(priorytet 3)*

**Gdzie, dokładne adresy:**
- [wod-kan.biz — Telemetria](https://www.wod-kan.biz/telemetria,katalog-firm,g,4,3)
- [wod-kan.biz — Monitoring i opomiarowanie](https://www.wod-kan.biz/monitoring_automatyka_wod_kan_monitoring_i_opomiarowanie,katalog-firm,g,4,2)
- [wod-kan.biz — Automatyka, systemy sterowania](https://www.wod-kan.biz/pl,monitoring_automatyka_wod_kan_automatyka_systemy_sterowania,katalog-firm-pniewy-556,g,4,1)
- [katalog targów WOD-KAN — wystawcy wg grup towarowych](https://katalog.targi-wod-kan.pl/wystawcy-wg-grup-towarowych) oraz [lista wystawców 2025 (PDF)](https://targi-wod-kan.pl/wp-content/uploads/2025/05/Lista-Wystawcow-9.pdf)
- [woda-scieki.com — katalog firm](https://www.woda-scieki.com/firmy) · [wodkaneko.pl](https://www.wodkaneko.pl/)

**Cel:** domknąć K1, K2 i K6 (K5 pozostanie próbką — patrz uwaga w [sekcji 5](#5-podsumowanie-ilościowe)) i **rozstrzygnąć wiersz 13 (Aksel)**.
**Metoda:** przejdź listę pozycja po pozycji, odrzuć producentów rur, pomp bez telemetrii i firmy budowlane, a każdą pozostałą sprawdź testem T1–T3. Spodziewaj się kilkunastu nowych nazw; **jeśli po przejrzeniu wszystkich katalogów nie przybywa nic nowego w K1/K2/K6 — to jest wynik**: zapisz go, bo oznacza, że mapa jest kompletna.

### Zadanie E — cenniki abonamentowe *(priorytet 4)*

**Cel:** naprawić najsłabszy element testu klasyfikacyjnego (patrz „Uwaga o T2" w [sekcji 3](#3-kryterium-klasyfikacji--test-nie-wrażenie)) — dziś T2 opiera się na modelu sprzedaży, bo cen po prostu nie ma.
**Gdzie szukać:** strony cenowe i „jak kupić" u: Efento (chmura), Inwap, AT Systems, Hawle.live, GlobTree, Endress+Hauser Netilion. Sprawdź też, czy w dokumentacji postępowań z zadania A nie ma **formularzy cenowych z rozbiciem na pozycje** — to najbogatsze źródło cen jednostkowych, jakie w ogóle istnieje publicznie.
**Ograniczenie:** tylko źródła publiczne. **Nie rejestruj się na wersje próbne, nie zamawiaj ofert, nie kontaktuj się z konkurencją podszywając się pod klienta.**

### Zadanie F — Grundfos i KSB na rynku polskim *(priorytet 4)*

**Cel:** domknąć wiersz 31 i zagrożenie „monitoring jako dodatek do pompy" ([§5.2.8](./01_plan_biznesowy.md#528-największe-zagrożenia-konkurencyjne) pkt 1). Wilo i Xylem są potwierdzone, te dwie firmy nie.
**Gdzie:** polskie serwisy obu producentów, w szczególności oferty typu „remote management" i „monitoring pomp"; szukaj polskojęzycznej strony produktowej albo wdrożenia w polskiej gminie.
**Werdykt do nadania:** jeśli mają polskojęzyczną ofertę monitoringu dla obiektów komunalnych → 🔴 bezpośredni w obrębie własnego sprzętu (jak Wilo, wiersz 26). Jeśli tylko oferta globalna bez śladów w PL → 🟡 pośredni z uzasadnieniem T3✗.

### Zadanie G — obecność Lacroix Sofrel i Kallipr w Polsce *(priorytet 5)*

**Cel:** rozstrzygnąć dwa jedyne wyjątki od reguły z [§2.3](#23-czego-ten-dokument-świadomie-nie-robi).
**Co ustalić:** czy istnieje polski dystrybutor lub udokumentowane wdrożenie w polskim przedsiębiorstwie wodociągowym. **Jeśli tak** — zostają w mapie z pełnym werdyktem. **Jeśli nie** — usuń je z tabeli, przenieś do materiału wejściowego dla **B-02** (są tam cenne jako wzorce techniczne) i przelicz sumy.

### Kontrola spójności — wykonaj po każdej zmianie w tabeli

Liczby w [sekcji 5](#5-podsumowanie-ilościowe) muszą się zgadzać z tabelą. Zamiast liczyć ręcznie, uruchom z katalogu głównego repozytorium:

```bash
F=docs/business/06_mapa_rynku_konkurencji.md
awk '/^\| [0-9]+ \|/' $F | wc -l                       # łączna liczba pozycji
for s in 🔴 🟡 🔵 ⚪; do printf "%s " "$s"; awk '/^\| [0-9]+ \|/' $F | grep -c "$s"; done
for k in K1 K2 K3 K4 K5 K6; do printf "%s " "$k"; awk '/^\| [0-9]+ \|/' $F | awk -F'|' -v k=$k '$4 ~ k' | wc -l; done
```

Suma czterech klasyfikacji i suma sześciu kategorii muszą być równe łącznej liczbie pozycji. **Zaktualizuj też datę weryfikacji na górze dokumentu** i dopisz jednym zdaniem, co zostało domknięte — inaczej czytelnik nie odróżni wersji.

---

## Powiązania

- **[§5.1](./01_plan_biznesowy.md#51-rynki-docelowe)** — rynki docelowe i kryteria SAM, na których oparty jest test klasyfikacyjny.
- **[§5.2](./01_plan_biznesowy.md#52-analiza-konkurencji)** — pogłębione profile 9 podmiotów; ten dokument ich nie powtarza, tylko klasyfikuje i rozszerza spis.
- **B-02** (analiza technologiczna konkurencji) i **B-03** (analiza UX) — lista podmiotów do dołożenia w [sekcji 7](#7-podmioty-warte-pogłębionej-analizy-w-b-02b-03).
- **B-14** (dofinansowania dla gmin) — [sekcja 6.2](#62-cztery-wnioski-które-zmieniają-sposób-patrzenia-na-rynek) pokazuje, że budżety na monitoring w małych gminach są w praktyce dotacyjne; to wzmacnia priorytet tamtego zlecenia.
- **[ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md)** — postępowanie Gminy Ełk na jeden punkt pomiarowy potwierdza zasadność rozliczenia per obiekt.
- **[CONTEXT.md](./CONTEXT.md)** — „partnerstwo montażowo-integracyjne"; część podmiotów z K5 to równie prawdopodobni partnerzy co konkurenci.

> **Status dokumentu:** materiał roboczy, oparty na źródłach publicznych zweryfikowanych 4 września 2026 przez wyszukiwarkę (bez otwierania stron — patrz [§2.2](#22-ograniczenie-metody--przeczytaj-przed-użyciem-tabeli)). Klasyfikacje są wnioskami autorskimi na podstawie kryteriów z [§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam), a nie deklaracjami samych podmiotów.
