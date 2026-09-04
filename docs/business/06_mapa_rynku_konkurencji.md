# Mapa rynku — wszyscy gracze na polskim rynku, bezpośredni vs. pozostali

**Data weryfikacji źródeł: 4 września 2026.** Wszystkie ustalenia w tym dokumencie odnoszą się do tej daty. Rynek zmienia się szybciej niż dokumentacja — przed użyciem tej mapy w rozmowie handlowej sprawdź ponownie podmioty oznaczone jako **bezpośrednie**.

Dokument jest **rozszerzeniem, nie powtórzeniem** [§5.2 planu biznesowego](./01_plan_biznesowy.md). Tam jest głębia (9 pogłębionych profili), tutaj jest **szerokość i jednoznaczny werdykt klasyfikacyjny** dla każdego znalezionego podmiotu — w tym dla tych, które §5.2 już opisuje jakościowo, ale nigdy nie zaklasyfikowała.

---

## 1. Odpowiedź w jednym akapicie

Na polskim rynku zidentyfikowano **52 pozycje** (podmioty i wyraźnie wyodrębnione rozwiązania) rozłożone na sześć kategorii z [§5.2.1](./01_plan_biznesowy.md). Po zastosowaniu testu opartego na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md) tylko **11 z nich to konkurenci bezpośredni** — reszta albo celuje w innego klienta (33), albo dziś nie konkuruje, lecz ma realną zdolność zejścia w dół rynku (5), albo nie dało się jej rozstrzygnąć bez źródeł, do których nie ma publicznego dostępu (3). Najważniejszy wniosek nie dotyczy jednak liczb: **realna konkurencja o małą gminę nie przychodzi ze strony dużych platform smart water, tylko z dwóch kierunków, których §5.2 nie docenia** — od producentów przepompowni i szaf, którzy dorzucają monitoring do sprzedaży sprzętu, oraz od małych, mało widocznych firm telemetrycznych sprzedających „monitoring GSM/GPRS z podglądem w przeglądarce" jako gotowy produkt (Inwap, AT Systems, PM Ecology). Te drugie nie pojawiają się w żadnej analizie branżowej, bo nie robią marketingu — ale to one wygrywają małe postępowania.

---

## 2. Metoda i jej granice

### 2.1. Jak powstawał spis

1. Punkt wyjścia: 9 podmiotów opisanych w [§5.2](./01_plan_biznesowy.md) + taksonomia 6 kategorii z [§5.2.1](./01_plan_biznesowy.md).
2. Przeszukanie sieci pod kątem każdej z 6 kategorii osobno, po polsku, frazami używanymi przez branżę (nie przez marketing): „telemetria przepompowni", „monitoring hydroforni", „system monitoringu i wizualizacji przepompowni ścieków", „inteligentny system zarządzania siecią wodociągową".
3. Przeszukanie **historycznych postępowań publicznych** i BIP-ów małych gmin — patrz [sekcja 6](#6-sygnał-z-przetargów-publicznych).
4. Przeszukanie katalogów branżowych: [katalog wystawców targów WOD-KAN](https://katalog.targi-wod-kan.pl/wystawcy-wg-grup-towarowych), [wod-kan.biz](https://www.wod-kan.biz/telemetria,katalog-firm,g,4,3), [woda-scieki.com](https://www.woda-scieki.com/firmy), [wodkaneko.pl](https://www.wodkaneko.pl/).

### 2.2. Ograniczenie metody — przeczytaj przed użyciem tabeli

**W środowisku, w którym powstawał ten dokument, dostęp do bezpośredniego pobierania stron (WebFetch) był zablokowany przez politykę sieciową.** Cała weryfikacja odbyła się przez wyszukiwarkę: adresy URL są prawdziwe i pochodzą z indeksu wyszukiwarki, a opisy ofert — z treści indeksowanych stron, ale **żadna strona nie została otwarta i przeczytana w całości**. Praktyczne konsekwencje:

- Kolumna **Pewność** w tabeli mówi dokładnie o tym: `wysoka` = ustalenie wynika wprost z cytowanej treści strony dostawcy; `średnia` = wynika z treści strony trzeciej (portal branżowy, katalog) opisującej dostawcę; `przypuszczenie` = wywnioskowane z pośrednich przesłanek, wymaga potwierdzenia.
- **Żaden segment docelowy oznaczony `przypuszczenie` nie może być użyty jako argument w rozmowie z klientem** bez wcześniejszego sprawdzenia.
- Ceny i zwycięzców postępowań w większości **nie udało się ustalić** — w takich miejscach jest napisane „nieustalone", zgodnie z zasadą: lepiej luka niż zgadywanie.

### 2.3. Czego ten dokument świadomie nie robi

- Nie powtarza profili z [§5.2](./01_plan_biznesowy.md) — dla podmiotów już tam opisanych jest odesłanie i **sam werdykt**, bo to jest nowa wartość.
- Nie robi analizy technicznej ani UX — to zakres **B-02** i **B-03**. Lista podmiotów wartych tam dołożenia jest w [sekcji 7](#7-podmioty-warte-pogłębionej-analizy-w-b-02b-03).
- Nie wychodzi poza Polskę. Zagraniczne wzorce to celowo zakres **B-02**. Podmioty zagraniczne pojawiają się tu **tylko wtedy, gdy realnie działają na polskim rynku** (mają polski oddział, dystrybutora albo udokumentowane wdrożenia w PL).

---

## 3. Kryterium klasyfikacji — test, nie wrażenie

Etykietę nadaje **trzypytaniowy test** oparty wprost na kryteriach SAM z [§5.1.2](./01_plan_biznesowy.md) (target: gminy 1000–20000 mieszkańców, 5–15 rozproszonych obiektów; nie target: duże miasta, krajowi operatorzy z gotowym SCADA, gminy z <3 obiektami) i na modelu przychodowym z [§4.1](./01_plan_biznesowy.md) (2,9–8,3 tys. zł jednorazowo na obiekt + 130–170 zł/mies.).

| # | Pytanie testowe |
|---|---|
| **T1 — produkt** | Czy podmiot sprzedaje **gotowe rozwiązanie monitoringu obiektu**, które mała gmina może kupić bez projektu SCADA i bez prac inżynierskich na miarę? |
| **T2 — rząd wielkości ceny** | Czy koszt na obiekt mieści się w **kilku–kilkunastu tysiącach złotych** jednorazowo (a nie w setkach tysięcy za projekt dla całej sieci)? |
| **T3 — dowód obsługi segmentu** | Czy istnieje **publiczny dowód**, że podmiot obsługuje klientów tej wielkości — referencje z małych gmin, materiały kierowane do gmin, rozstrzygnięte postępowania? |

**Reguła nadawania etykiety:**

- **🔴 Bezpośredni konkurent** — T1, T2 i T3 na „tak". Realnie konkuruje o tego samego klienta, o ten sam budżet i w zbliżonym modelu.
- **🟡 Konkurent pośredni / sąsiedni segment** — co najmniej jedno „nie", **bez** widocznej zdolności lub chęci zmiany. Uzasadnienie musi wskazać **które** pytanie zawodzi — „jest inny" nie jest uzasadnieniem.
- **🔵 Do obserwacji** — dziś zawodzi T1, T2 lub T3, ale podmiot ma **produkt, kanał sprzedaży i markę**, żeby to zmienić niewielkim kosztem. To ryzyko realne, nie teoretyczne — dlatego przy każdym takim wpisie jest napisane, **co konkretnie musiałoby się stać**.
- **⚪ Nieustalone** — brak publicznych informacji wystarczających do rozstrzygnięcia. Zgodnie z ograniczeniami briefu: nie zgadujemy.

Ważna uwaga do odczytu: **„pośredni" nie znaczy „nieszkodliwy"**. Integrator AKPiA nie konkuruje z nami produktowo, ale gdy gmina zapyta go o monitoring, dostanie ofertę projektową — i to my musimy umieć wytłumaczyć różnicę. Klasyfikacja mówi o **rywalizacji o ten sam typ zakupu**, nie o tym, kogo można zignorować.

---

## 4. Pełny spis — tabela zbiorcza

Kategorie wg [§5.2.1](./01_plan_biznesowy.md): **K1** chmurowa SCADA abonamentowa · **K2** telemetria przemysłowa i RTU · **K3** kompleksowe smart water · **K4** producenci pomp i przepompowni · **K5** integratorzy AKPiA · **K6** wyspecjalizowane urządzenia IoT.

Model biznesowy: **AB** abonament/SaaS · **CAPEX** sprzedaż sprzętu · **PROJ** wdrożenie projektowe · **USL** usługi.

| # | Podmiot | Kat. | Segment docelowy | Model | Klasyfikacja | Źródło | Pewność |
|---|---|---|---|---|---|---|---|
| 1 | **UniCloud / Unitronics / Elmark Automatyka** — opisany w [§5.2.2](./01_plan_biznesowy.md) | K1 | małe gminy i obiekty wod-kan, jawnie adresowane | AB + CAPEX | 🔴 bezpośredni | [smart.elmark.com.pl](https://smart.elmark.com.pl/uni/umc/branze/wod-kan), [blog: SCADA dla małej gminy](https://www.elmark.com.pl/blog/system-scada-dla-maej-gminy-czy-to-musi-by-drogie-) | wysoka |
| 2 | **Inwap** (system monitoringu WWW/SMS, chmura PIK-on) | K1 | przepompownie i obiekty rozproszone, małe podmioty | AB + CAPEX | 🔴 bezpośredni | [inwap.pl](https://inwap.pl/produkty/monitoring-www-sms-zdalna-zdalne-gsm-gprs.html) | średnia |
| 3 | **AT SYSTEMS** (systemy monitoringu GSM/GPRS) | K1 | przepompownie, zbiorniki, obiekty komunalne | CAPEX + USL | 🔴 bezpośredni | [atsystems.pl](https://atsystems.pl/systemy-monitoringu-gsm-gprs) | średnia |
| 4 | **Endress+Hauser Polska** (Netilion Water Network Insights) | K1 | przedsiębiorstwa wod-kan średnie i duże | AB + CAPEX | 🔵 do obserwacji | [pl.endress.com](https://www.pl.endress.com/pl/przemysl/rozwiazania-dla-procesow/system-zarzadzania-siecia-wodociagowa) | wysoka |
| 5 | **Vispena** (zdalny monitoring oczyszczalni, brama InHand + chmura) | K1 | oczyszczalnie i instalacje przemysłowe | PROJ + USL | 🟡 pośredni | [vispena.pl](https://vispena.pl/zdalny-monitoring-oczyszczalni-sciekow/) | średnia |
| 6 | **JUMO** (smartWARE SCADA w chmurze dla wodociągów) | K1 | zakłady wodociągowe, głównie procesowe | CAPEX + AB | 🟡 pośredni | [jumo.group — blog](https://www.jumo.group/pl/pl/about-us/blog/scada-system-in-water-utilities) | przypuszczenie |
| 7 | **Inventia** (MT-101/MT-102, DataPortal) — opisany w [§5.2.2](./01_plan_biznesowy.md) | K2 | przepompownie w całej Polsce, >6000 wdrożeń modułów MT-101 | CAPEX + AB | 🔴 bezpośredni | [inventia.pl/wod-kan](https://www.inventia.pl/wod-kan/), [automatykab2b — 6000 przepompowni](https://automatykab2b.pl/prezentacje/41761-ponad-6000-przepompowni-wykorzystuje-moduly-telemetryczne-inventia-mt-101) | wysoka |
| 8 | **PM Ecology** (Aqua Logger Compact / RDR / HS / FLOW) | K2 | punkty pomiarowe sieci wod-kan, obiekty bez zasilania | CAPEX + AB | 🔴 bezpośredni | [pmecology.com — woda wodociągowa](https://www.pmecology.com/aplikacja/woda-wodociagowa/), [Aqua Logger Compact](https://www.pmecology.com/produkt/rejestrator-danych-aqua-logger-compact/) | wysoka |
| 9 | **PLUM** (MacR6, MacR6 N, MacIQ WM) | K2 | opomiarowanie rozliczeniowe i bilansowanie sieci | CAPEX | 🟡 pośredni | [plum.pl](https://plum.pl/en/automatingwatermeterreading/), [karta MacR6 N](https://hsb.com.pl/wp-content/uploads/2021/08/Karta-katalogowa-MacR6N_woda_PLUM_11_2019_v2.pdf) | wysoka |
| 10 | **Teletrans** (moduły telemetryczne przewodowe i radiowe, RMZ) | K2 | integratorzy i producenci szaf (sprzedaż komponentu) | CAPEX | 🟡 pośredni | [teletrans.com.pl](https://teletrans.com.pl/index.php?id=Modu%C5%82y+telemetryczne%2C16) | średnia |
| 11 | **Lacroix Sofrel** (S4W, DL4W) | K2 | operatorzy sieci wodociągowych, klasa przemysłowa | CAPEX + PROJ | 🟡 pośredni | [lacroix-environment.com — SOFREL S4W](https://www.lacroix-environment.com/telemetry-solutions/offers/rtus-data-loggers/sofrel-s4w-rtu/) | wysoka |
| 12 | **Ovarro** (XiLog 4G, Primeweb/Atrium) — w PL przez **RD Tech** | K2 | operatorzy sieci, monitoring strat i ciśnienia | CAPEX + AB | 🟡 pośredni | [rdtech.pl — XiLog 4G](https://www.rdtech.pl/xilog-4g/), [ovarro.com — data loggers](https://ovarro.com/en/global/solutions/monitoring--control-devices/data-loggers--leak-noise-loggers/data-loggers/2/) | wysoka |
| 13 | **Aksel Sp. z o.o.** | K2 | nieustalone (wystawca targów WOD-KAN, profil telemetryczny) | nieustalone | ⚪ nieustalone | [katalog targów WOD-KAN](https://katalog.targi-wod-kan.pl/firma/aksel-sp-z-o-o-41) | przypuszczenie |
| 14 | **SebaKMT / Sewerin** (loggery szumu i ciśnienia, przez dystrybutorów PL) | K2 | służby eksploatacyjne wodociągów — lokalizacja wycieków | CAPEX + USL | 🟡 pośredni | [sebakmt.com](https://sebakmt.com/en-us/), [przeciek24.com — loggery](https://przeciek24.com/loggery/) | średnia |
| 15 | **AquaRD** (CellBOX, HydraNET, AquaGIS, SCADA) — opisany w [§5.2.2](./01_plan_biznesowy.md) | K3 | przedsiębiorstwa wodociągowe miast powiatowych i większe | PROJ + CAPEX | 🟡 pośredni | [aquard.pl](https://aquard.pl/), [wdrożenie w Dębicy](https://www.wodociagi.debickie.pl/2023/02/09/inteligentny-systemu-zarzadzania-siecia-wodociagowa-i-kanalizacyjna-wdrozony/) | wysoka |
| 16 | **AIUT** (WaterPrime — analityka; systemy zdalnego odczytu LoRa) — WaterPrime w [§5.2.4](./01_plan_biznesowy.md) | K3 | duże miasta i operatorzy z modelem hydraulicznym | PROJ + AB | 🟡 pośredni | [waterprime.eu](https://waterprime.eu/), [aiut.com — zdalny odczyt wodomierzy](https://aiut.com/rozwiazania/systemy-smart-city-iot/systemy-zdalnego-odczytu-wodomierzy-i-cieplomierzy/system-zdalnego-odczytu-i-monitoringu-pracy-wodomierzy/) | wysoka |
| 17 | **Future Processing** (SmartFlow, z MPWiK Wrocław) | K3 | duże przedsiębiorstwa wodociągowe, analityka strat w strefach DMA | AB + PROJ | 🟡 pośredni | [MPWiK Wrocław — SmartFlow](https://www.mpwik.wroc.pl/pracuj-z-nami/projekty/smartflow/), [IGWP o SmartFlow](https://www.igwp.org.pl/smartflow-czyli-nowoczesna-technologia-w-zarzadzaniu-siecia-wodociagowa/) | wysoka |
| 18 | **Orange Polska** (Smart Water) | K3 | **gminy, miasta i ZWiK — jawnie adresowane**; 29 wdrożeń | AB | 🔵 do obserwacji | [orange.pl — Smart Water](https://www.orange.pl/duze-firmy/smart-water), [poradnik: zarządzanie siecią wodociągową](https://www.orange.pl/poradnik-dla-firm/rozwiazania-smart/inteligentna-woda-zarzadzanie-wodociagami/) | wysoka |
| 19 | **T-Mobile Polska** (IoT / NB-IoT dla wod-kan) | K3 | przedsiębiorstwa wodociągowe, opomiarowanie stacjonarne | AB | 🔵 do obserwacji | [T-Mobile — case study PWiK Kutno](https://biznes.t-mobile.pl/pl/case-study/przedsiebiorstwo-wodociagow-i-kanalizacji-w-kutnie), [24 000 nakładek w Katowicach](https://www.telix.pl/operatorzy/t-mobile/2026/06/t-mobile-polska-wdrozy-24-000-nakladek-iot-do-zdalnego-odczytu-wodomierzy-w-katowicach/) | wysoka |
| 20 | **Veolia Woda Polska** | K3 | duzi operatorzy i miasta, w których Veolia zarządza siecią | USL + PROJ | 🟡 pośredni | [wodatomy.pl — usługi Veolii dla sektora wodnego](https://wodatomy.pl/strefa-wiedzy/veolia-woda-polska-dzialalnosc/nowe-oblicze-uslug-dla-sektora-wodnego/) | średnia |
| 21 | **SUEZ Polska** (urządzenia CellBOX) | K3 | przedsiębiorstwa wodociągowe średnie i duże | PROJ + CAPEX | 🟡 pośredni | [suez.com — urządzenia CellBOX](https://www.suez.com/pl-pl/polska/inteligentne-rozwiazania/urzadzenia-cellbox) | średnia |
| 22 | **GlobTree** (GlobeOMS — chmura telemetryczna, nakładki) | K3 | wodociągi i zarządcy mediów, wejście „od jednego urządzenia" | AB + CAPEX | 🔵 do obserwacji | [globtree.pl — firma](https://globtree.pl/firma-globtree/), [globtree.pl — telemetria](https://globtree.pl/telemetria-korzysci-ktorych-szukasz/) | średnia |
| 23 | **Hydro-Vacuum** — opisany w [§5.2.3](./01_plan_biznesowy.md) | K4 | gminy kupujące pompy i tłocznie tego producenta | CAPEX | 🔴 bezpośredni | [hydro-vacuum.com.pl — monitoring](https://www.hydro-vacuum.com.pl/monitoring.php) | wysoka |
| 24 | **Metalchem-Warszawa** (MRT-GSM, MRM-GPRS) — opisany w [§5.2.3](./01_plan_biznesowy.md) | K4 | gminy z przepompowniami i rozdzielnicami tego producenta | CAPEX | 🔴 bezpośredni | [metalchemsa.com.pl — monitoring przepompowni](https://www.metalchemsa.com.pl/monitoring-przepompowni/) | wysoka |
| 25 | **Bartosz Sp.j.** (systemy monitorowania GSM/GPRS) | K4 | obiekty wod-kan, **deklarowana zgodność z urządzeniami innych producentów** | CAPEX | 🔴 bezpośredni | [instalacjebudowlane.pl — systemy GSM/GPRS Bartosz](https://www.instalacjebudowlane.pl/9333-26-76-systemy-monitorowania-gsm-gprs--zdalny-nadzor-nad-obiektami-i-instalacjami.html) | średnia |
| 26 | **Wilo Polska** (Wilo-Nexos, Nexos NET Intelligence) | K4 | użytkownicy pompowni i tłoczni Wilo, w tym gminne | CAPEX + AB | 🔴 bezpośredni (ograniczony do własnego sprzętu) | [wilo.com — monitoring pompowni](https://wilo.com/pl/pl/Serwis/Oferta-serwisowa/Monitoring-pompowni-t%C5%82oczni-%C5%9Bciek%C3%B3w-i-zestaw%C3%B3w-pompowych/), [Nexos NET Intelligence](https://wilo.com/pl/pl/Narz%C4%99dzia/Aplikacje-do-zarz%C4%85dzania-prac%C4%85-pomp/Nexos-NET-Intelligence/) | wysoka |
| 27 | **Hydro-Partner** — opisany w [§5.2.3](./01_plan_biznesowy.md) | K4 | obiekty wymagające projektu SCADA i modernizacji | PROJ | 🟡 pośredni | [hydro-partner.pl — monitoring](https://hydro-partner.pl/automatyka-2/monitoring/) | wysoka |
| 28 | **Ecol-Unicon** (Bumerang SMART) | K4 | zarządcy wód opadowych, retencji i przepompowni — głównie miasta | PROJ + AB | 🟡 pośredni | [ecol-unicon.com — inteligentne monitorowanie sieci](https://ecol-unicon.com/blog/inteligentne-monitorowanie-sieci-wodno-kanalizacyjnych/) | wysoka |
| 29 | **Xylem Poland** (systemy monitorujące, ekosystem Flygt) | K4 | większe przepompownie i obiekty z pompami Xylem | CAPEX + PROJ | 🟡 pośredni | [xylem.com — systemy monitorujące](https://www.xylem.com/pl-pl/products-services/pumps-packaged-pump-systems/monitoring-control-equipment/monitoring--supervision/monitoring-systems/) | wysoka |
| 30 | **Wobet-Hydret** (przepompownia z modułem GSM) | K4 | obiekty przydomowe i małe przepompownie | CAPEX | 🟡 pośredni | [wobet-hydret.pl — przepompownia z modułem GSM](https://www.wobet-hydret.pl/blog/dobre-rozwiazanie-przepompownia-z-modulem-gsm) | średnia |
| 31 | **Grundfos, KSB** (monitoring w ekosystemie własnych pomp) | K4 | nieustalone dla rynku PL | nieustalone | ⚪ nieustalone | brak potwierdzonego źródła dla oferty PL — patrz [sekcja 9](#9-czego-nie-udało-się-ustalić) | przypuszczenie |
| 32 | **NASUS** — opisany w [§5.2.2](./01_plan_biznesowy.md) | K5 | wodociągi, energetyka, ciepłownictwo — wdrożenia projektowe | PROJ + USL | 🟡 pośredni | [nasus.pl](http://www.nasus.pl/index.php) | wysoka |
| 33 | **MEDAS** (automatyka i teleinformatyka, >30 lat) | K5 | SUW, oczyszczalnie, przepompownie — projektowo | PROJ | 🟡 pośredni | [medas.com.pl](https://medas.com.pl/) | średnia |
| 34 | **Hartimex** | K5 | oczyszczalnie, przepompownie, SUW — PLC/HMI/SCADA, prefabrykacja szaf | PROJ | 🟡 pośredni | [hartimex.pl](https://hartimex.pl/) | średnia |
| 35 | **JR Technika s.c.** | K5 | stacje uzdatniania wody — szafy sterownicze, PLC | PROJ | 🟡 pośredni | [jrtechnika.pl](https://jrtechnika.pl/pages/automatyzacja.html) | średnia |
| 36 | **Intelcon** (Nowy Sącz) | K5 | AKPiA dla SUW i oczyszczalni — **region małopolski** | PROJ | 🟡 pośredni | [intelcon.pl — AKPiA](https://intelcon.pl/akpia/) | średnia |
| 37 | **PiA-ZAP** | K5 | modernizacje AKPiA SUW, w tym wątek cyberbezpieczeństwa | PROJ | 🟡 pośredni | [piazap.com.pl — case study SUW Sekuła](https://piazap.com.pl/2025/12/05/modernizacja-akpia-suw-sekula-case-study/) | średnia |
| 38 | **EkoWodrol** (Koszalin) | K5 | obiekty wod-kan — automatyka w ramach większych realizacji | PROJ | 🟡 pośredni | [ekowodrol.pl — automatyka](https://ekowodrol.pl/uslugi/automatyka/) | średnia |
| 39 | **AMEplus** | K5 | obiekty hydrotechniczne i przemysłowe | PROJ | 🟡 pośredni | [ameplus.pl — obiekty hydrotechniczne](https://www.ameplus.pl/hydrotechnical-objects/) | średnia |
| 40 | **Metria** | K5 | monitoring obiektów wodno-kanalizacyjnych — projekty systemów | PROJ | 🟡 pośredni | [metria.pl — monitoring](https://metria.pl/automatyka/monitoring/) | średnia |
| 41 | **APS** | K5 | monitoring parametrów technologicznych przepompowni i wodociągów | PROJ | 🟡 pośredni | [AutomatykaOnline — system monitoringu dla przepompowni i wodociągów](https://automatykaonline.pl/Aplikacje/Wod-Kan/System-monitoringu-dla-przepompowni-i-wodociagow) | średnia |
| 42 | **Sauka Baj** | K5 | systemy telemetryczne i dyspozytorskie, studnie głębinowe | PROJ | 🟡 pośredni | [saukabaj.pl](https://saukabaj.pl/systemy-dyspozytorskie-telemetryczne) | średnia |
| 43 | **Tech-Pomp Serwis** | K5 | AKPiA przy obiektach pompowych | PROJ + USL | 🟡 pośredni | [transferwody.pl — AKPiA](https://transferwody.pl/akpia-aparatura-kontrolno-pomiarowa-i-automatyka) | średnia |
| 44 | **Hawle.live** — opisany w [§5.2.4](./01_plan_biznesowy.md) | K6 | wodociągi monitorujące sieć i armaturę, forma produktowa | CAPEX + AB | 🔴 bezpośredni | [hawle.com — Hawle.live](https://www.hawle.com/pl/dla-klienta/serwis-hawle/hawle-live) | wysoka |
| 45 | **Efento** (Kraków — rejestratory NB-IoT ciśnienia i poziomu + Efento Cloud) | K6 | dowolny klient szukający taniego, bateryjnego pomiaru z chmurą | CAPEX + AB | 🔴 bezpośredni | [efento.pl](https://efento.pl/), [rejestrator wysokiego ciśnienia NB-IoT](https://efento.pl/product/bezprzewodowy-rejestrator-wysokiego-cisnienia/) | wysoka |
| 46 | **CTHINGS.CO** | K6 | dziś: Edge AI i ekspansja poza PL; wod-kan był pilotażem w Skandynawii | AB + PROJ | 🔵 do obserwacji | [ISBtech — wdrożenia wod-kan w Skandynawii](https://www.isbtech.pl/2021/12/polski-startup-cthings-co-wdraza-nowe-rozwiazania-dla-gospodarki-wodno-kanalizacyjnej-w-skandynawii/), [Platforma Przemysłu Przyszłości](https://przemyslprzyszlosci.gov.pl/iot-w-zarzadzaniu-systemem-wodno-kanalizacyjnym/) | średnia |
| 47 | **Apator Powogaz / Apator Telemetria** | K6 | opomiarowanie rozliczeniowe wodociągów (AMR/AMI) | CAPEX | 🟡 pośredni | [apator.com — system radiowy AMR](https://www.apator.com/nasze-rozwiazania/woda-i-cieplo/system-zdalnego-odczytu-mediow/system-radiowy/amr), [profil Apator Telemetria](https://www.woda-scieki.com/firmy/2171-apator-telemetria-sp-z-o-o-/produkty) | wysoka |
| 48 | **Dostawcy AMI wodomierzowego: Diehl Metering, Kamstrup, Itron, BMETERS** | K6 | opomiarowanie rozliczeniowe — inne zadanie niż monitoring obiektu | CAPEX + AB | 🟡 pośredni | [Polski Instalator — przegląd systemów zdalnego odczytu](https://www.polskiinstalator.com.pl/artykuly/instalacje-sanitarne/2534-systemy-zdalnego-odczytu-wodomierzy) | średnia |
| 49 | **KROHNE Polska** | K6 | pomiar na ujęciach i studniach, rozwiązania bezprzewodowe | CAPEX | 🟡 pośredni | [pl.krohne.com — zdalny monitoring studni](https://pl.krohne.com/pl/rozwiazania/rozwiazania-pomiarow-bezprzewodowych-zdalnych/pomiar-wody-mozliwoscia-zdalnego-przesylania-danych/zdalny-monitoring-studni-wodnych-zasilania) | wysoka |
| 50 | **METERING (Anna Moder)** | K6 | doradztwo i dobór monitoringu sieci, sprzedaż wodomierzy | USL + CAPEX | 🟡 pośredni | [metering.com.pl — monitoring sieci](https://metering.com.pl/uslugi/monitoring-sieci/) | średnia |
| 51 | **WODOSERWIS** | K6 | diagnostyka sieci i lokalizacja wycieków — usługa, nie platforma | USL | 🟡 pośredni | [wodoserwis.pl — monitoring](https://www.wodoserwis.pl/monitoring.htm) | średnia |
| 52 | **Kallipr** — wzorzec zagraniczny z [§5.2.5](./01_plan_biznesowy.md) | K6 | rynki AU/NZ i inne — obecność na rynku PL nieustalona | CAPEX + AB | ⚪ nieustalone (poza mapą krajową) | [kallipr.com](https://kallipr.com/solutions/pump-station-monitoring/) | wysoka |

---

## 5. Podsumowanie ilościowe

| Klasyfikacja | Liczba | Udział | Które to są |
|---|---|---|---|
| 🔴 **Bezpośredni konkurent** | **11** | 21% | UniCloud/Elmark, Inwap, AT Systems, Inventia, PM Ecology, Hydro-Vacuum, Metalchem-Warszawa, Bartosz, Wilo Polska, Hawle.live, Efento |
| 🟡 **Pośredni / sąsiedni segment** | **33** | 63% | m.in. AquaRD, AIUT/WaterPrime, Future Processing, Veolia, SUEZ, Hydro-Partner, Ecol-Unicon, Xylem, PLUM, Lacroix Sofrel, Ovarro, cały ogon integratorów AKPiA (12 pozycji), dostawcy AMI |
| 🔵 **Do obserwacji** | **5** | 10% | Orange Polska, T-Mobile Polska, GlobTree, Endress+Hauser Polska, CTHINGS.CO |
| ⚪ **Nieustalone** | **3** | 6% | Aksel, Grundfos/KSB, Kallipr (obecność w PL) |
| **Razem** | **52** | 100% | |

Rozkład po kategoriach z [§5.2.1](./01_plan_biznesowy.md):

| Kategoria | Pozycji | Bezpośrednich | Komentarz |
|---|---|---|---|
| K1 — chmurowa SCADA abonamentowa | 6 | 3 | Najgęstsza konkurencja względem naszego modelu. UniCloud nie jest sam. |
| K2 — telemetria przemysłowa i RTU | 8 | 2 | Dojrzały sprzęt, wysoka poprzeczka jakościowa; większość celuje wyżej niż my. |
| K3 — kompleksowe smart water | 8 | 0 | **Zero bezpośrednich.** Wszyscy celują w miasta i duże ZWiK — za to trzej mają zdolność zejścia w dół. |
| K4 — producenci pomp i przepompowni | 9 | 4 | **Najbardziej niedoszacowane zagrożenie.** Monitoring wchodzi razem z pompą, bez osobnej decyzji zakupowej. |
| K5 — integratorzy AKPiA | 12 | 0 | Długi ogon; konkurują ofertą projektową, nie produktem. Spis jest reprezentatywny, nie wyczerpujący — patrz niżej. |
| K6 — wyspecjalizowane IoT | 9 | 2 | Efento i Hawle.live pokazują dwa różne sposoby na produktowe podejście do tego samego problemu. |

**Uwaga o kompletności K5.** Kategoria integratorów AKPiA jest z natury **niepoliczalna** — to setki lokalnych firm elektrycznych i automatycznych, z których większość nie prowadzi widocznej działalności marketingowej. Dwanaście pozycji w tabeli to **próbka reprezentatywna dobrana tak, żeby pokryć różne modele działania i różne regiony** (w tym Intelcon z Nowego Sącza jako przykład z województwa pierwszego klienta), a nie spis. Deklarowanie tu „pełnej mapy" byłoby nieuczciwe. Pozostałe pięć kategorii traktujemy jako spis kompletny w granicach publicznie widocznych podmiotów.

---

## 6. Sygnał z przetargów publicznych

To jest źródło, którego [§5.2](./01_plan_biznesowy.md) nie użyła: nie to, co firma o sobie mówi, tylko **co gminy faktycznie kupują i za ile**.

### 6.1. Co udało się ustalić

| Zamawiający | Przedmiot | Skala / kwota | Region | Źródło |
|---|---|---|---|---|
| **Gmina Gidle** | „Inteligentne zarządzanie i monitorowanie infrastrukturą wodociągową" — tryb art. 132 PZP (próg unijny) | **1 452 626,11 zł**, wadium 22 000 zł; oferty do 12.06.2026 | łódzkie | [BIP Gidle](https://bip.gidle.pl/?bip=2&cid=108&id=1833) |
| **Gmina Zaklików** | Sterowanie, monitoring i wizualizacja **25 przepompowni ścieków** + ujęcie wody Karkówka | kwota nieustalona; dofinansowanie FEPK.02, umowa z 27.06.2024 | **podkarpackie** | [przetargi.egospodarka.pl](https://www.przetargi.egospodarka.pl/20031852601_Wdrozenie-systemu-sterowania-monitoringu-i-wizualizacji-parametrow-pracy-pompowni-sciekow-w-aglomeracji-Zaklikow-oraz-ujecia-wody-pitnej-Karkowka-w-Gminie-Zaklikow_2025_2.html), [UG Zaklików](https://www.zaklikow.pl/asp/podpisanie-umowy-o-dofinansowanie-projektu,2,artykul,1,3079) |
| **MZWiK Myślenice** | „Wdrożenie inteligentnego systemu zarządzania siecią wodociągową" jako element projektu (modernizacja sieci + 2 SUW + PV) | projekt ~**21 mln zł**, dofinansowanie ~12 mln zł; oferty do 24.08.2026 | **małopolskie** | [MZWiK Myślenice](https://www.mzwikmyslenice.com.pl/2026/07/23/przetarg-wdrozenie-inteligentnego-systemu-zarzadzanie-siecia-wodociagowa-dla-miejskiego-zakladu-wodociagow-i-kanalizacji-sp-z-o-o-w-myslenicach/) |
| **PWiK Oświęcim** | „Wdrożenie Inteligentnego Systemu Zarządzania Siecią Wodociągową" — postępowanie rozstrzygnięte | kwota i wykonawca nieustalone | **małopolskie** | [PWiK Oświęcim](https://pwik.oswiecim.pl/Wdrozenie-Inteligentnego-Systemu-Zarzadzania-Siecia-Wodociagowa-(rozstrzygniety)-126.html) |
| **Wodociągi Dębickie** | Inteligentny system zarządzania siecią wod-kan: **16 punktów pomiarowych**, SCADA, AquaGIS, model hydrauliczny | **wykonawca: AquaRD Sp. z o.o.**, umowa 3.02.2022, zakończenie XII 2022; kwota nieustalona | **podkarpackie** | [Wodociągi Dębickie](https://www.wodociagi.debickie.pl/2023/02/09/inteligentny-systemu-zarzadzania-siecia-wodociagowa-i-kanalizacyjna-wdrozony/), [Inżynieria.com](https://inzynieria.com/wodkan/wiadomosci/64586,debica-zarzadzanie-sieciami-wodno-kanalizacyjnymi-bedzie-cyfrowe) |
| **Gmina Ełk** | Budowa systemu monitoringu przepływu i ciśnienia w wybranych punktach sieci — **oraz osobne postępowanie na 1 (jeden) punkt pomiarowy** | kwoty nieustalone; wybór oferty 26.03.2025 | warmińsko-mazurskie | [BIP Gmina Ełk — system](https://bip.elk.gmina.pl/budowa-systemu-monitoringu-przeplywu-i-cisnienia-w-wybranych-punktach-sieci-wodociagowej-na-terenie-gminy-gmina-elk.html), [BIP — 1 punkt pomiarowy](https://bip.elk.gmina.pl/budowa-1-punktu-pomiarowego-systemu-monitoringu-przeplywu-i-cisnienia-sieci-wodociagowej-na-terenie-gminy-gmina-elk.html) |
| **MZK Stalowa Wola** | Szczegółowy opis systemu monitorowania przepompowni (dokument SIWZ) | — | **podkarpackie** | [BIP MZK Stalowa Wola (PDF)](https://bip.mzk.stalowa-wola.pl/download/193/33045/Zalaczniknr1-Szczegolowyopis-Monitoringprzepompowni.pdf) |
| **Gminy Jabłoń, Lubiszyn, Pieniężno** | „System monitoringu i wizualizacji przepompowni ścieków w technologii GPRS" — **niemal identyczny opis w trzech różnych gminach** | — | lubelskie, lubuskie, warmińsko-mazurskie | [UG Jabłoń (PDF)](https://ugjablon.bip.lubelskie.pl/upload/pliki/Zal._Nr_11_do_SIWZ_-_System_monitoringu_i_wizualizacji_przepompowni_sciekow.pdf), [Lubiszyn (PDF)](https://www.lubiszyn.pl/asp/pliki/aktualnosci/opis_monitoringu.pdf), [BIP Pieniężno](https://bip.pieniezno.pl/attachments/download/2294) |

### 6.2. Cztery wnioski, które zmieniają sposób patrzenia na rynek

**1. Gminy kupują monitoring w rozmiarze „jeden punkt", nie tylko „cały system".** Gmina Ełk prowadziła osobne postępowanie na **jeden punkt pomiarowy**. To potwierdza założenie z [ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md) o rozliczeniu per obiekt i pokazuje, że wejście do gminy nie wymaga wygrania dużego przetargu — wystarczy być tańszym i szybszym na jednym obiekcie. To najkorzystniejsza dla nas obserwacja w całym dokumencie.

**2. Krąży ustandaryzowany opis przedmiotu zamówienia.** Trzy niepowiązane gminy używają praktycznie tego samego dokumentu „System monitoringu i wizualizacji przepompowni ścieków w technologii GPRS". Oznacza to, że **specyfikacje są kopiowane między gminami** i opisują technologię (GPRS, moduł telemetryczny w szafie), a nie efekt. Konsekwencja praktyczna: jeśli nasz gateway nie mieści się w takim opisie, wypadamy formalnie, nawet będąc lepszym rozwiązaniem. To zadanie dla materiału handlowego, nie dla produktu — trzeba umieć zaproponować gminie treść opisu przedmiotu zamówienia.

**3. Duże pieniądze na monitoring w małych gminach istnieją i pochodzą z dotacji.** Gidle: 1,45 mln zł na monitoring infrastruktury wodociągowej w gminie wiejskiej, w trybie unijnym. Zaklików: 25 przepompowni ze środków FEPK. Myślenice: 21 mln zł na projekt z komponentem ISZSW. **Cały ten strumień jest dotacyjny** — co bezpośrednio łączy się ze zleceniem **B-14** (dofinansowania) i jest silnym argumentem, żeby je zrealizować przed pierwszą rozmową handlową.

**4. Nazwa „Inteligentny System Zarządzania Siecią Wodociągową" (ISZSW) to standardowy pakiet dotacyjny.** Powtarza się w Gidlach, Myślenicach, Oświęcimiu, Dębicy, Skierniewicach i Żywcu. W Dębicy wygrał go **AquaRD**, i to jest jedyne twarde powiązanie „kto wygrywa" z całego przeglądu. Zakres pakietu (monitoring + SCADA + GIS + model hydrauliczny) jest **istotnie szerszy niż nasze MVP** — to potwierdza klasyfikację AquaRD jako konkurenta pośredniego i jednocześnie ostrzega: jeśli gmina finansuje projekt z dotacji, będzie skłonna kupić szerszy zakres, bo nie płaci za niego sama.

### 6.3. Czego w przetargach nie udało się ustalić

Nazwisk zwycięzców i cen jednostkowych **poza przypadkiem Dębicy nie ustalono**. Powód jest metodyczny, nie merytoryczny: informacje o wyborze oferty są publikowane jako pliki PDF na BIP-ach poszczególnych gmin, a w tej sesji nie było możliwości pobierania dokumentów (patrz [§2.2](#22-ograniczenie-metody--przeczytaj-przed-użyciem-tabeli)). **To jest najbardziej wartościowy niedokończony wątek tego zlecenia** — patrz [sekcja 9](#9-czego-nie-udało-się-ustalić).

---

## 7. Podmioty warte pogłębionej analizy w B-02/B-03

Podmioty spoza listy 9 z [§5.2](./01_plan_biznesowy.md), których dołożenie do zakresu **B-02** (warstwa techniczna) lub **B-03** (UX) da najwięcej. Uszeregowane wg wartości informacji:

| Podmiot | Do którego zlecenia | Dlaczego akurat ten |
|---|---|---|
| **PM Ecology** (Aqua Logger) | B-02 | Polski producent bateryjnych rejestratorów ciśnienia i przepływu z transmisją GSM i integracją SCADA — **najbliższy technicznie odpowiednik naszego gatewaya wśród firm, których plan w ogóle nie wymienia**. Wprost odpowiada na pytanie „czy nasz PoC ma sens sprzętowy". |
| **Inwap (PIK-on)** i **AT Systems** | B-02 + B-03 | Dwaj mało widoczni gracze sprzedający dokładnie nasz produkt (monitoring GSM/GPRS + podgląd w przeglądarce + SMS) małym podmiotom. Jeśli ktoś już rozwiązał problem „mała gmina, mały budżet", to oni. Wart sprawdzenia zwłaszcza interfejs — B-03. |
| **Efento** | B-02 | Wzorzec „urządzenie NB-IoT + chmura + zero infrastruktury pośredniej". Ich model provisioningu i cennik chmury to bezpośredni benchmark dla wymiarów 4 i 6 z B-02. |
| **Lacroix Sofrel (S4W)** | B-02 | Klasa przemysłowa z jawnie komunikowanym cyberbezpieczeństwem i wbudowanym serwerem WWW — punkt odniesienia dla wymiaru 11 (bezpieczeństwo) i dla ścieżki NIS2 z [§6.1](./01_plan_biznesowy.md). |
| **Ovarro (XiLog 4G + Primeweb/Atrium)** | B-02 | Rejestrator wielokanałowy 4G + platforma analityczna; dojrzały wzorzec dla formatu telemetrii i retencji (wymiary 5 i 8 B-02). |
| **Ecol-Unicon (Bumerang SMART)** | B-03 | Polski system łączący monitoring z prognozą pogody i planowaniem prac — ciekawy wzorzec dla widoku alarmów i triage'u (wymiar 5 B-03). |
| **Wilo Nexos / Nexos NET Intelligence** | B-02 | Pokazuje, jak wygląda monitoring dorzucony do sprzętu przez producenta pomp — czyli zagrożenie nr 1 z [§5.2.8](./01_plan_biznesowy.md) w konkretnej, technicznej postaci. |
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
| **SmartFlow jako „konkurent dla gminy"** | Produkt rozwiązuje wykrywanie ukrytych wycieków w strefach pomiarowych dużego miasta (Wrocław, ~100 urządzeń, kilkadziesiąt stref). Gmina z 10 obiektami nie ma na czym go uruchomić. Pozostaje jako pośredni. |
| **Wody Polskie i ich postępowania** | Występują masowo w wynikach wyszukiwania przetargów, ale dotyczą gospodarki wodnej państwa (RZGW), nie sieci wodociągowych gmin. Szum informacyjny przy przeszukiwaniu przetargów — nie mylić. |

---

## 9. Czego nie udało się ustalić

Uczciwa lista luk, z których każda jest gotowym zadaniem do zlecenia:

1. **Zwycięzcy i ceny jednostkowe postępowań.** Największa luka. Wymaga otwarcia PDF-ów „informacja o wyborze najkorzystniejszej oferty" na BIP-ach gmin oraz przeszukania [platformy e-Zamówienia](https://ezamowienia.gov.pl/mo-client-board/bzp/list) i agregatorów ([Grupa Biznes Polska — branża monitoring kanalizacji i wodociągów](https://www.biznes-polska.pl/branze/455313/), [Atlas Przetargów](https://atlasprzetargow.pl/)). Realna wartość: **weryfikacja szacunków kosztowych z [§4.2](./01_plan_biznesowy.md) danymi z rynku, a nie z cenników komponentów.** Rekomendacja: osobne zlecenie, wykonywane w środowisku bez blokady pobierania stron.
2. **Aksel Sp. z o.o.** — wystawca targów WOD-KAN o profilu telemetrycznym, brak wystarczających danych do klasyfikacji.
3. **Grundfos i KSB na rynku polskim** — obie firmy oferują globalnie monitoring w ekosystemie własnych pomp (Grundfos Remote Management, KSB Guard), ale **nie znaleziono polskojęzycznego źródła potwierdzającego ofertę dla gmin**. Wobec zagrożenia „monitoring jako dodatek do pompy" ([§5.2.8](./01_plan_biznesowy.md), punkt 1) warto to domknąć — Wilo i Xylem zostały potwierdzone, te dwie nie.
4. **Obecność Kallipr na rynku polskim** — nieustalona; do czasu potwierdzenia traktujemy wyłącznie jako wzorzec produktowy, zgodnie z [§5.2.5](./01_plan_biznesowy.md), a nie jako gracza na mapie krajowej.
5. **Członkowie wspierający IGWP.** [Izba Gospodarcza „Wodociągi Polskie"](https://www.igwp.org.pl/) zrzesza ok. 487 członków, z czego ok. 30 to członkowie wspierający — czyli w większości **dostawcy branżowi**. Lista tych 30 podmiotów byłaby najbliższym istniejącym odpowiednikiem oficjalnego spisu dostawców branży; nie udało się jej pobrać. Zdobycie jej to najtańszy sposób na domknięcie kategorii K5.
6. **Cenniki abonamentowe poza UniCloud.** Żaden inny podmiot z kategorii K1 nie publikuje cen. Deklarowany przedział UniCloud (1–3 tys. zł rocznie za obiekt, start do ~10 tys. zł) pozostaje jedynym punktem odniesienia — i wciąż jest to deklaracja marketingowa, nie oferta.

---

## 10. Co z tego wynika dla planu biznesowego

Trzy korekty do rozważenia w [§5.2](./01_plan_biznesowy.md) — **propozycje, nie zmiany wprowadzone**:

1. **§5.2.8 punkt 1 („monitoring jako dodatek do nowej szafy lub pompy") jest niedoszacowany i zasługuje na awans na pozycję pierwszą pod względem prawdopodobieństwa, nie tylko kolejności.** Cztery z jedenastu konkurentów bezpośrednich to producenci sprzętu dorzucający monitoring (Hydro-Vacuum, Metalchem, Bartosz, Wilo). Ich przewaga nie jest technologiczna — polega na tym, że **gmina nie podejmuje wtedy osobnej decyzji zakupowej**, więc nie ma momentu, w którym mogłaby nas porównać.
2. **§5.2.9 punkt 3 („najbliższym konkurentem biznesowym jest UniCloud") wymaga uzupełnienia, nie zmiany.** UniCloud jest najbliższy pod względem *modelu*, ale jest też najbardziej widoczny — i dlatego przeceniany. W realnym postępowaniu w małej gminie prędzej spotkamy Inventię (>6000 przepompowni z modułami MT-101) albo lokalnego integratora z modułem GSM w szafie. Proponowane brzmienie: *„najbliższym konkurentem modelowym jest UniCloud, ale najczęściej spotykanym w praktyce — telemetria GSM/GPRS montowana przez producenta szafy lub lokalnego integratora"*.
3. **Do §5.2.1 warto dopisać siódmą kategorię: operatorzy telekomunikacyjni.** Orange Smart Water (29 wdrożeń w gminach i miastach) i T-Mobile nie mieszczą się w żadnej z sześciu istniejących kategorii, a mają to, czego nie ma żaden inny gracz jednocześnie: **markę, kanał sprzedaży do samorządu, model abonamentowy i własną sieć IoT**. Dziś sprzedają opomiarowanie rozliczeniowe, nie monitoring obiektu — ale odległość między jednym a drugim jest mała, a my nie mielibyśmy czym odpowiedzieć na argument „bierzemy to od operatora, który i tak dostarcza nam SIM-y".

---

## 11. Definicja ukończenia — sprawdzenie

Pytanie kontrolne z briefu brzmiało: *„czy da się odpowiedzieć jednym zdaniem i bez wahania na pytanie «czy firma X jest naszą konkurencją» dla każdego podmiotu na liście?"*

Tak, w postaci: **„Firma X jest / nie jest naszym bezpośrednim konkurentem, bo [zawodzi test T1/T2/T3 — konkretnie: …]"**. Trzy przykłady użycia:

- *„Czy AquaRD to nasza konkurencja?"* → Pośrednia. Sprzedaje pakiet SCADA + GIS + model hydrauliczny w modelu projektowym miastom powiatowym (Dębica, 16 punktów pomiarowych) — zawodzi T2 i T3. Ale ma własne urządzenia CellBOX i najwyższą wśród graczy pośrednich zdolność zejścia w dół rynku, więc obserwujemy.
- *„Czy Efento to nasza konkurencja?"* → Bezpośrednia. Sprzedaje bateryjny rejestrator ciśnienia NB-IoT z chmurą w abonamencie, dostępny od jednej sztuki — przechodzi T1, T2 i T3. Nie integruje się jednak z istniejącą automatyką ani PLC, więc konkuruje tylko o obiekty najprostsze.
- *„Czy Orange to nasza konkurencja?"* → Dziś nie, jutro możliwe. Sprzedaje gminom opomiarowanie rozliczeniowe i bilansowanie sieci, nie monitoring obiektu — zawodzi T1. Ale ma markę, kanał do samorządu, model abonamentowy i własną sieć IoT, więc rozszerzenie oferty o monitoring obiektu jest dla nich tanie. Kategoria: do obserwacji, priorytet najwyższy.

---

## Powiązania

- **[§5.1](./01_plan_biznesowy.md)** — rynki docelowe i kryteria SAM, na których oparty jest test klasyfikacyjny.
- **[§5.2](./01_plan_biznesowy.md)** — pogłębione profile 9 podmiotów; ten dokument ich nie powtarza, tylko klasyfikuje i rozszerza spis.
- **B-02** (analiza technologiczna konkurencji) i **B-03** (analiza UX) — lista podmiotów do dołożenia w [sekcji 7](#7-podmioty-warte-pogłębionej-analizy-w-b-02b-03).
- **B-14** (dofinansowania dla gmin) — [sekcja 6.2](#62-cztery-wnioski-które-zmieniają-sposób-patrzenia-na-rynek) pokazuje, że budżety na monitoring w małych gminach są w praktyce dotacyjne; to wzmacnia priorytet tamtego zlecenia.
- **[ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md)** — postępowanie Gminy Ełk na jeden punkt pomiarowy potwierdza zasadność rozliczenia per obiekt.

> **Status dokumentu:** materiał roboczy, oparty na źródłach publicznych zweryfikowanych 4 września 2026 przez wyszukiwarkę (bez otwierania stron — patrz [§2.2](#22-ograniczenie-metody--przeczytaj-przed-użyciem-tabeli)). Klasyfikacje są wnioskami autorskimi na podstawie kryteriów z [§5.1.2](./01_plan_biznesowy.md), a nie deklaracjami samych podmiotów.
