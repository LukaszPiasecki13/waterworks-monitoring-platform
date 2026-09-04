# Analiza UX/UI konkurencji i wzorce dla interfejsu

> **Zlecenie:** B-03 z [`docs/plan/01_briefy_dla_agentow.md`](../plan/01_briefy_dla_agentow.md)
> **Data badania:** 2026-09-04 (wszystkie zrzuty i odczyty ze źródeł wykonane tego dnia)
> **Zakres:** wyłącznie warstwa „jak to wygląda i jak się tego używa”. Warstwa techniczna (firmware, sprzęt, backend) to osobne zlecenie B-02.
> **Artifact z rekomendacjami:** [„Dwanaście zmian we froncie”](https://claude.ai/code/artifact/0f8179dd-6126-45cb-bc04-21db6e92ef5c) — wizualny towarzysz tego dokumentu: 12 rekomendacji o najwyższym stosunku wartości do kosztu, każda z przykładem interfejsu i wskazaniem pliku w naszym kodzie. Źródło i skrypt budujący: [`artifact/`](./artifact/).

---

## 0. Jak czytać ten dokument

| Rozdział | Do czego służy |
|---|---|
| [1. Metoda i dobór produktów](#1-metoda-i-dobór-produktów) | Dlaczego akurat te produkty, jak oznaczana jest wiarygodność ustaleń |
| [2. Profile produktów](#2-profile-badanych-produktów) | Skrótowy opis każdego badanego produktu + tabela porównawcza 9 wymiarów |
| [3. Katalog wzorców](#3-katalog-wzorców-z-werdyktem) | **Sedno merytoryczne** — 27 wzorców z werdyktem BIERZ / NIE BIERZ / ROZWAŻ |
| [4. Konfrontacja z naszym interfejsem](#4-konfrontacja-z-naszym-interfejsem) | **Sedno wdrożeniowe** — co mamy dziś, co zmienić, w którym pliku |
| [5. Architektura informacji](#5-rekomendacja-architektury-informacji) | Mapa nawigacji dopasowana do trzech ról z §2.7.2 planu biznesowego |
| [6. Projekt widoku alarmów](#6-projekt-widoku-alarmów) | Opis ekranu, którego jeszcze nie ma — gotowy jako wejście do implementacji |
| [7. Backlog](#7-backlog-zmian-we-froncie) | Kolejność prac wg stosunku wartości do kosztu |
| [8. Praca na telefonie](#8-wymiar-8--praca-na-telefonie) | Wymiar 8 briefu, zrealizowany samodzielnie (dokument B-12 nie istnieje) |
| [9. Ograniczenia](#9-ograniczenia-analizy) | Czego nie udało się ustalić i dlaczego |
| [Załącznik A](#załącznik-a--biblioteka-zrzutów) | Pełna biblioteka 50 zrzutów ze źródłami i datami |

**Terminologia** zgodna z [`CONTEXT.md`](../business/CONTEXT.md): *obiekt wodociągowy*, *punkt pomiarowy* (= *kanał*), *gateway*, *gmina*, *reguła alarmowa*. Nazwy własne i terminy techniczne produktów obcych zostawione w oryginale.

---

## 1. Metoda i dobór produktów

### 1.1. Kryterium doboru

Brief pozostawia dobór produktów agentowi, z kryterium **porównywalności problemu, nie popularności marki**. Problem, który rozwiązujemy, rozkłada się na trzy pytania, i każde z nich ma na rynku inne, dojrzalsze rozwiązanie:

| Nasze pytanie | Gdzie jest najlepiej rozwiązane | Kategoria |
|---|---|---|
| „Który obiekt wymaga uwagi i dlaczego?” (§2.8.1) | Monitoring infrastruktury IT — dziesiątki lat pracy nad triażem setek obiektów | Obserwowalność |
| „Jak pokazać pomiar, żeby nikt nie wziął starej wartości za bieżącą?” (§2.4.3) | Zabbix i platformy IoT — czas pomiaru jest tam polem pierwszej klasy | Obserwowalność / IoT |
| „Jak wygląda pełny cykl życia alarmu z reakcją człowieka?” (§2.8.3) | Zarządzanie incydentami i alarmy przemysłowe | On-call / SCADA |
| „Jak to wygląda u konkurentów, do których pójdzie ta sama gmina?” | Polskie i europejskie platformy wod-kan | Wod-kan |

Stąd trzy kategorie i **12 produktów**, z czego **5 przeanalizowanych szczegółowo** (pełne ekrany, nie materiały marketingowe).

### 1.2. Badane produkty

| # | Produkt | Kategoria | Głębokość | Podstawa |
|---|---|---|---|---|
| 1 | **Grafana / Grafana Alerting** | obserwowalność | **szczegółowa** | publiczna instancja [play.grafana.org](https://play.grafana.org/) — klikana ręcznie + dokumentacja producenta |
| 2 | **Zabbix** | obserwowalność | **szczegółowa** | pełna, ilustrowana dokumentacja producenta |
| 3 | **ThingsBoard** | IoT / device management | **szczegółowa** | dokumentacja producenta ze zrzutami |
| 4 | **Ignition Perspective** (Inductive Automation) | SCADA w chmurze | **szczegółowa** | dokumentacja producenta; publiczne demo niedostępne (patrz §9) |
| 5 | **Inventia DataPortal** | wod-kan (PL) | **szczegółowa** | materiały producenta zawierające realne ekrany aplikacji |
| 6 | **PagerDuty** | zarządzanie incydentami | przeglądowa | dokumentacja producenta ze zrzutami |
| 7 | **Hawle.live** | wod-kan (PL/AT) | przeglądowa | aplikacja dostępna wyłącznie po zalogowaniu |
| 8 | **AquaRD** (SCADA / HydraNET / AquaGIS) | wod-kan (PL) | przeglądowa | strona produktowa, bez ekranów aplikacji |
| 9 | **Metasphere** | wod-kan (UK) | przeglądowa | strona produktowa, bez ekranów aplikacji |
| 10 | **HWM Global** | wod-kan (UK) | przeglądowa | strona produktowa, bez ekranów aplikacji |
| 11 | **TaKaDu** | wod-kan / CEM (IL) | przeglądowa | wyłącznie materiały marketingowe (patrz §9) |
| 12 | **Prometheus Alertmanager** | obserwowalność | przeglądowa (koncepcyjna) | dokumentacja — wzorzec grupowania/wyciszania bez własnego UI |

**Odrzucone z uzasadnieniem:** Uptime Kuma (publiczne demo okazało się kreatorem instalacji świeżej instancji, nie działającą aplikacją — brak materiału), Xylem / Ovarro / Ayyeka (strony produktowe nie zawierają ekranów aplikacji w publicznym dostępie), UniCloud WOD-KAN (serwis niedostępny w dniu badania).

### 1.3. Poziomy wiarygodności

Każde ustalenie w tym dokumencie ma jedną z etykiet:

| Etykieta | Znaczenie |
|---|---|
| **[demo]** | Zaobserwowane bezpośrednio w działającej, publicznej instancji produktu |
| **[dok]** | Zrzut lub opis z dokumentacji producenta |
| **[mkt]** | Materiał marketingowy producenta — wyidealizowany, traktowany jako najsłabsze źródło |
| **[nieujawnione]** | Informacja niedostępna publicznie; **nie zgadujemy** |

Zrzuty ekranu przechowywane są w [`docs/analysis/assets/`](./assets/) wraz z [`index.json`](./assets/index.json), który dla każdego pliku zawiera adres źródła i datę pobrania. Pełna tabela w [Załączniku A](#załącznik-a--biblioteka-zrzutów).

**Zastrzeżenie:** interfejsy zmieniają się między wersjami. Każde ustalenie tutaj opisuje stan na **2026-09-04**.

---

## 2. Profile badanych produktów

### 2.1. Grafana / Grafana Alerting — [demo]

Platforma wizualizacji szeregów czasowych z rozbudowanym, osobnym modułem alarmowania. Zbadana na publicznej instancji `play.grafana.org`, gdzie widoczne są rzeczywiste dane i rzeczywista konfiguracja.

Co robi najlepiej z naszej perspektywy:

- **Lista reguł alarmowych** ma boczny panel filtrów ze stanami `Firing / Normal / Pending / Recovering`, przełącznik widoku „Grouped / List” i zapisywane wyszukiwania ([`grafana-lista-regul-alarmowych.jpg`](./assets/grafana-lista-regul-alarmowych.jpg)). Stan `Pending` to okres, w którym warunek jest spełniony, ale nie upłynął jeszcze czas utrzymania — dokładny odpowiednik naszego „czasu utrzymania warunku” z §2.6.4.
- **Historia alarmów** to histogram liczby zdarzeń w czasie nad tabelą przejść stanów (`✓ → ⊗`), z filtrem po stanie początkowym i końcowym ([`grafana-historia-alarmow.jpg`](./assets/grafana-historia-alarmow.jpg)). Histogram odpowiada na pytanie „czy mamy zalew alarmów?” bez czytania listy.
- **Polityki powiadomień** są drzewem dopasowań, a parametry grupowania opisane są zdaniem po ludzku: _„Wait 30s to group instances · Wait 5m before sending updates · Repeated every 4h”_ ([`grafana-polityki-powiadomien.jpg`](./assets/grafana-polityki-powiadomien.jpg)).
- **Adnotacje** nanoszą zdarzenia na wykres jako pionowe znaczniki i jednocześnie listują je pod spodem z czasem i tagiem ([`grafana-adnotacje-na-wykresie.jpg`](./assets/grafana-adnotacje-na-wykresie.jpg)).
- **Panel „Alerts linked to this dashboard”** pokazuje przy wykresie, które reguły go pilnują i w jakim są stanie ([`grafana-dashboard-z-regulami.jpg`](./assets/grafana-dashboard-z-regulami.jpg)).

Czego nie robi dobrze dla nas: reguła alarmowa jest definiowana zapytaniem w języku źródła danych — dla pracownika gminy to bariera nie do przejścia. Nie ma też pojęcia „właściciela alarmu” ani słownika przyczyn zamknięcia; alarm w Grafanie jest sygnałem, nie zadaniem.

### 2.2. Zabbix — [dok]

Klasyczny monitoring infrastruktury z bardzo dojrzałym modelem zdarzenia. Dokumentacja producenta jest w całości ilustrowana rzeczywistymi ekranami.

- **Dialog „Update problem”** ([`zabbix-aktualizacja-problemu.jpg`](./assets/zabbix-aktualizacja-problemu.jpg)) mieści w jednym oknie: komentarz, historię reakcji (czas / użytkownik / akcja / treść), zakres operacji (tylko to zdarzenie albo wszystkie z powiązanych reguł), zmianę priorytetu, wyciszenie („Indefinitely” albo „Until” z konkretnym czasem), potwierdzenie, „Convert to cause” i zamknięcie. Na dole warunek: _„At least one update operation or message must exist”_ — nie da się kliknąć „załatwione” bez śladu.
- **Szczegóły zdarzenia** ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg)) zawierają log powiadomień z **kolumną Status** (widoczny wpis `Failed`) oraz „Event list [previous 20]” — dwadzieścia poprzednich wystąpień tej samej reguły z czasem trwania każdego.
- **Filtr widoku Problems** ([`zabbix-filtr-problemow.jpg`](./assets/zabbix-filtr-problemow.jpg)): severity jako sześć niezależnych checkboxów, „Age less than N days”, „Show suppressed problems”, „Acknowledgement status: All / Unacknowledged / Acknowledged / By me”, tagi z operatorem And/Or, „Save as” zapisujący filtr jako zakładkę.
- **Latest data** ([`zabbix-latest-data.jpg`](./assets/zabbix-latest-data.jpg)) pokazuje w jednym wierszu: obiekt, nazwę pozycji, `Last check` (wiek odczytu, np. „7s”), `Last value` i `Change` względem poprzedniego odczytu. Wartość bez wieku po prostu nie występuje.
- **Konfiguracja widgetu Item value** ([`zabbix-konfiguracja-widgetu-wartosci.jpg`](./assets/zabbix-konfiguracja-widgetu-wartosci.jpg)) ma osobne przełączniki `Description / Value / Time / Change indicator / Sparkline` — czas jest równorzędnym elementem kafla, nie dopiskiem.
- **Dashboard** ([`zabbix-dashboard.jpg`](./assets/zabbix-dashboard.jpg)) prowadzi od kafli zbiorczych („Problems by severity”, „Host availability”) do tabeli bieżących problemów.
- **Widget Top hosts** ([`zabbix-widget-top-hosts.jpg`](./assets/zabbix-widget-top-hosts.jpg)) — tabela z paskiem wartości i sparkline’em w komórce, kolumny definiowane przez użytkownika.
- **Okna serwisowe** ([`zabbix-okno-serwisowe.jpg`](./assets/zabbix-okno-serwisowe.jpg)) tłumią alarmy w zaplanowanym czasie, z kreatorem harmonogramu bez pisania wyrażeń.

Model stanu Zabbiksa rozróżnia trzy niezależne osie: **stan warunku** (PROBLEM / RESOLVED), **potwierdzenie** (Acknowledged / nie) i **tłumienie** (suppressed / nie). To rozróżnienie jest kluczowe i wraca w §3 i §6.

### 2.3. ThingsBoard — [dok]

Platforma IoT ogólnego przeznaczenia, najbliższa naszemu modelowi danych (urządzenie → telemetria → alarm).

- **Szczegóły alarmu** ([`thingsboard-szczegoly-alarmu.jpg`](./assets/thingsboard-szczegoly-alarmu.jpg)) — dokumentacja opisuje pola wprost: „An entity that causes the alarm”, „Alarm creation time”, „Duration of alarm”, „Alarm type”, „Alarm severity”, „Current alarm status” (`Active Unacknowledged`), **„Alarm assignment field to user”** oraz sekcja Activity z komentarzami systemowymi i użytkownika. Przyciski: `Acknowledge`, `Clear`.
- **Kreator filtrów** ([`thingsboard-filtry-3.jpg`](./assets/thingsboard-filtry-3.jpg), [`thingsboard-filtry-4.jpg`](./assets/thingsboard-filtry-4.jpg)) buduje warunek z trzech pól: klucz, operator, wartość — bez składni. Gotowy warunek pokazywany jest jako czytelne zdanie: `model equal 'DHT22' and batteryLevel less than 20` ([`thingsboard-filtry-podglad.jpg`](./assets/thingsboard-filtry-podglad.jpg)).

To jest bezpośredni wzorzec dla naszego §2.8.4 („progi alarmowe dla niezaawansowanego użytkownika”).

### 2.4. Ignition Perspective — [dok]

SCADA klasy przemysłowej z klientem webowym.

- **Alarm Status Table** ([`ignition-tabela-alarmow.jpg`](./assets/ignition-tabela-alarmow.jpg)): kolumny `Active Time / Display Path / Priority / Current State`, zakładki `Details` i `Notes`, przyciski `Acknowledge` i `Shelve`.
- **Wartość poznawcza — kolumna `Current State`.** Zawiera wartości złożone: `Active, Unacknowledged`, `Cleared, Unacknowledged`. To jawne rozdzielenie **stanu warunku** od **stanu obsługi**. Alarm, który sam ustąpił, ale nikt go nie widział, jest innym obiektem niż alarm ustąpiony i potwierdzony — i oba muszą być widoczne.
- **Wartość ostrzegawcza — kolorystyka.** Całe wiersze wypełnione nasyconą czerwienią i turkusem. Przy pięciu alarmach ekran jest ścianą koloru; nie da się z niego odczytać priorytetu, bo kolor niesie stan, a nie ważność.

### 2.5. Inventia DataPortal — [mkt]/[dok]

Najbliższy odpowiednik polskiego konkurenta, do którego pójdzie ta sama gmina. Materiały producenta zawierają realne ekrany.

- **Ekran główny to synoptyka** ([`inventia-synoptyka.jpg`](./assets/inventia-synoptyka.jpg)) — narysowany schemat instalacji z animowanymi elementami. Wartości: `FAN SPEED [RPM] 378`, `LIQUID LEVEL 56.74`. **Nigdzie nie ma czasu pomiaru ani statusu jakości danych.** Napis `NORMAL` jest zielony i statyczny.
- **„Zestawienie alarmów” to mapa** ([`inventia-zestawienie-alarmow.jpg`](./assets/inventia-zestawienie-alarmow.jpg)) z pinami; przy każdym pinie etykieta typu `Status: AWARIA_P3` albo `Status: POSTÓJ`. Kody są surowe — pochodzą wprost z rejestrów sterownika. Brak listy, brak sortowania po ważności, brak czasu wystąpienia. Skupiska pinów zwijają się w liczniki (2, 5), co przy zoomie ukrywa alarmy.
- **Edytor ekranów** ([`dataportal-edytor.jpg`](./assets/dataportal-edytor.jpg)) — produkt zakłada, że ktoś (integrator) narysuje synoptykę per obiekt.

**Wniosek konkurencyjny:** różnicą, którą możemy postawić naprzeciw temu produktowi, nie jest ładniejszy wykres — jest nią **odpowiedź na pytanie „czy tej wartości można dziś ufać”**, której konkurent nie daje wcale.

### 2.6. PagerDuty — [dok]

- **Oś czasu incydentu** ([`pagerduty-os-czasu-incydentu.jpg`](./assets/pagerduty-os-czasu-incydentu.jpg)) jako narracja: „Assigned to Casey Bennett and reopened”, „Resolved by Mark Phillips through the website”, „Custom field updated by Mark Phillips: `resolution_category` to »1«”. Zakładki: `Alerts`, `Status Updates`, `Timeline`, `Automation Actions Log`, **`Past Incidents`**, `Related Incidents`.
- **Pole własne przy zamknięciu** (`resolution_category`) to dokładnie mechanizm, którego potrzebujemy do rozróżnienia „potwierdzona awaria” / „błąd czujnika” / „fałszywy alarm”.

### 2.7. Produkty wod-kan bez publicznego interfejsu

| Produkt | Co udało się ustalić | Etykieta |
|---|---|---|
| **Hawle.live** | Adres `hawle.live` przekierowuje wprost na `app.hawle.live/login`. Aplikacja za logowaniem, bez publicznej dokumentacji ani demo ([`hawle-live-logowanie.jpg`](./assets/hawle-live-logowanie.jpg)) | [nieujawnione] |
| **AquaRD** | Trzy produkty: SCADA („zbieranie danych, wizualizacja, sterowanie i alarmowanie”), HydraNET (bilansowanie, odczyty, „monitorowanie ciśnienia i przepływu w sieci”), AquaGIS. Brak ekranów aplikacji w materiałach publicznych | [mkt] |
| **Metasphere**, **HWM Global** | Strony produktowe zawierają wyłącznie fotografie sprzętu i materiały wizerunkowe; ekranów oprogramowania nie publikują | [nieujawnione] |
| **TaKaDu** | Deklaruje zarządzanie pełnym cyklem życia zdarzenia: „from event detection, through classification, prioritisation, resource allocation, until event closure”. **Żadnych publicznych zrzutów interfejsu.** Serwis blokował też automatyczne pobranie strony | [mkt] |

To samo w sobie jest ustaleniem: **w segmencie wod-kan nikt nie pokazuje swojego interfejsu**. Konsekwencje dla nas w §9.3.

### 2.8. Tabela porównawcza — produkt × 9 wymiarów briefu

Legenda: ●●● mocne i udokumentowane · ●●○ obecne, ograniczone · ●○○ szczątkowe · ✕ brak · ? nieujawnione

| Wymiar | Grafana | Zabbix | ThingsBoard | Ignition | Inventia DataPortal | PagerDuty | Wod-kan PL/UK (pozostali) |
|---|---|---|---|---|---|---|---|
| **1. Ekran startowy — „co wymaga uwagi”** | ●●○ dashboard konfigurowalny, priorytet zależy od autora | ●●● kafle severity + dostępność nad listą problemów | ●●○ dashboard budowany od zera | ●●○ tabela alarmów, priorytet czytelny, kolor przytłacza | ●○○ synoptyka; alarmy jako mapa | ●●● lista incydentów wg pilności | ? |
| **2. Hierarchia nawigacji** | ●●○ foldery + tagi, płasko | ●●● grupy → obiekty → pozycje → wykresy | ●●● klient → urządzenie → telemetria | ●●○ ścieżka wyświetlania jako tekst | ●○○ per ekran narysowany ręcznie | ●●○ usługa → incydent | ? |
| **3. Prezentacja pomiaru (wartość + czas + jakość)** | ●●○ czas na osi, jakość brak | ●●● `Last check` + `Change` w każdym wierszu; czas jako osobny przełącznik widgetu | ●●● czas i czas trwania jako pola alarmu | ●●○ `Active Time` w tabeli | ✕ **wartość bez czasu i bez jakości** | n/d | ? |
| **4. Statusy i kolor** | ●●● kolor + ikona + tekst stanu | ●●● severity nazwana słownie, kolor wspiera | ●●● severity słowna | ●○○ **nasycony kolor całego wiersza** | ●○○ surowe kody (`AWARIA_P3`) | ●●● tekst + kolor | ? |
| **5. Widok alarmów i triage** | ●●● filtry stanu, wyciszenia, grupowanie, historia | ●●● najbogatszy: potwierdzanie, tłumienie czasowe, zmiana priorytetu, historia reakcji, poprzednie wystąpienia | ●●● przypisanie do osoby, komentarze, Ack/Clear | ●●○ Ack + Shelve, notatki | ●○○ mapa pinów | ●●● przypisanie, eskalacja, oś czasu, pola własne | ? / [mkt] deklaracje TaKaDu |
| **6. Wykresy i analiza historii** | ●●● adnotacje, progi, state timeline, zakresy | ●●● legenda z last/min/avg/max | ●●○ widgety wykresów | ●●○ trendy | ●○○ | n/d | ? |
| **7. Konfiguracja progów bez wyrażeń** | ●○○ **wymaga zapytania w języku źródła** | ●○○ wyrażenie wyzwalacza | ●●● **kreator klucz/operator/wartość + podgląd zdaniem** | ●●○ konfiguracja per tag | ? | n/d | ? |
| **8. Praca na telefonie** | ●●○ układ responsywny, panele w kolumnie | ●●○ | ●●○ | ●●○ | ? | ●●● aplikacja natywna | ? |
| **9. Onboarding i dodanie obiektu** | ●○○ zakłada gotowe źródło danych | ●●○ szablony obiektów | ●●● profile urządzeń | ●○○ wymaga projektu | ●○○ wymaga narysowania ekranu | n/d | ? |

---

## 3. Katalog wzorców z werdyktem

27 wzorców. Każdy: co to jest, gdzie zaobserwowane (z dowodem), werdykt, uzasadnienie odniesione do naszych przypadków użycia UC-01…UC-05 i ról z §2.7.2.

Legenda kosztu: **S** ≤ 1 dzień · **M** 2–4 dni · **L** ≥ 1 tydzień · **XL** wymaga też pracy w backendzie.

### 3.1. BIERZ

#### W-01. Wartość pomiaru zawsze z czasem i statusem jakości — **BIERZ**, koszt S

**Gdzie:** Zabbix Latest data ([`zabbix-latest-data.jpg`](./assets/zabbix-latest-data.jpg)) — kolumna `Last check` z wiekiem odczytu przy każdej wartości; konfiguracja widgetu Item value ([`zabbix-konfiguracja-widgetu-wartosci.jpg`](./assets/zabbix-konfiguracja-widgetu-wartosci.jpg)) traktuje `Time` jako osobny, równorzędny element kafla. **Antywzorzec:** Inventia DataPortal ([`inventia-synoptyka.jpg`](./assets/inventia-synoptyka.jpg)) — `LIQUID LEVEL 56.74` bez jakiejkolwiek informacji o wieku pomiaru.

**Dlaczego bierzemy:** §2.4.3 planu biznesowego stawia to jako twardy niezmiennik: _„Ostatnia poprawna wartość nie może być prezentowana jako bieżąca bez informacji o czasie pomiaru i jakości.”_ To jedyny wymiar, w którym mamy udokumentowaną przewagę nad polskim konkurentem — i dziś **łamiemy go we własnym kodzie** (patrz [Z-01](#z-01-wartość-bez-czasu-i-jakości-w-liście-i-na-kafelku)).

#### W-02. Rozdzielenie stanu warunku od stanu obsługi — **BIERZ**, koszt XL

**Gdzie:** Ignition, kolumna `Current State` z wartościami `Active, Unacknowledged` i `Cleared, Unacknowledged` ([`ignition-tabela-alarmow.jpg`](./assets/ignition-tabela-alarmow.jpg)). Zabbix: `PROBLEM`/`RESOLVED` niezależnie od `Acknowledged: No` ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg)). ThingsBoard: `Active Unacknowledged` / `Cleared Acknowledged` ([`thingsboard-szczegoly-alarmu.jpg`](./assets/thingsboard-szczegoly-alarmu.jpg)).

**Dlaczego bierzemy:** nasz automat stanów z §2.5 (`Nowy → Aktywny → Potwierdzony → Zamknięty`) jest **liniowy** i przez to gubi najważniejszy operacyjnie przypadek: warunek ustąpił sam, ale nikt tego nie zauważył. Trzy niezależne produkty modelują to tak samo dwuosiowo — to nie jest przypadek. Rekomendacja szczegółowa w [§6.2](#62-model-stanu-alarmu).

#### W-03. Jeden dialog aktualizacji alarmu z obowiązkowym śladem — **BIERZ**, koszt L

**Gdzie:** Zabbix „Update problem” ([`zabbix-aktualizacja-problemu.jpg`](./assets/zabbix-aktualizacja-problemu.jpg)). Wszystkie operacje na zdarzeniu w jednym oknie, z warunkiem na dole: _„At least one update operation or message must exist”_.

**Dlaczego bierzemy:** §2.8.3 wymienia pięć osobnych czynności (potwierdzenie, komentarz, zamknięcie, oznaczenie fałszywym, przejście do wykresu). Pięć osobnych przycisków to pięć osobnych ścieżek do przetestowania i pięć miejsc, w których operator może zamknąć alarm bez śladu. Jedno okno z wymuszonym śladem jest tańsze i pewniejsze.

#### W-04. Wyciszenie czasowe zamiast trwałego — **BIERZ**, koszt M

**Gdzie:** Zabbix `Suppress: Indefinitely | Until [now+1h]` ([`zabbix-aktualizacja-problemu.jpg`](./assets/zabbix-aktualizacja-problemu.jpg)) oraz filtr z przełącznikiem „Show suppressed problems” ([`zabbix-filtr-problemow.jpg`](./assets/zabbix-filtr-problemow.jpg)). Grafana: osobny ekran Silences ([`grafana-wyciszenia.jpg`](./assets/grafana-wyciszenia.jpg)).

**Dlaczego bierzemy:** pracownik terenowy, który jedzie na obiekt, chce wyciszyć alarm na czas dojazdu i naprawy — nie na zawsze. Wyciszenie bez terminu to najprostsza droga do tego, żeby po pół roku nikt nie wiedział, czemu obiekt „nigdy nie alarmuje”. Domyślne „Until” z sugerowanym czasem jest bezpieczniejsze niż domyślne „Indefinitely”.

#### W-05. Log powiadomień ze statusem dostarczenia — **BIERZ**, koszt M (backend: XL)

**Gdzie:** Zabbix, sekcja `Actions` w szczegółach zdarzenia — kolumna `Status` z widocznym wpisem `Failed` ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg)). Grafana: punkty kontaktowe z historią i informacją o ostatnim dostarczeniu ([`grafana-punkty-kontaktowe.jpg`](./assets/grafana-punkty-kontaktowe.jpg)).

**Dlaczego bierzemy:** §2.8.3 wymaga wprost „wyświetlenia historii wysłanych powiadomień”. Kluczowe jest to, że Zabbix pokazuje nie tylko *że* wysłano, ale *czy doszło*. W gminie, gdzie kanałem będzie SMS albo e-mail na skrzynkę, którą ktoś zmienił, to jest różnica między „system nie zadziałał” a „system zadziałał, ale wiadomość nie doszła”.

#### W-06. „Poprzednie wystąpienia tej samej reguły” przy zdarzeniu — **BIERZ**, koszt M

**Gdzie:** Zabbix „Event list [previous 20]” w szczegółach zdarzenia — tabela z czasem wystąpienia, czasem powrotu do normy, statusem, wiekiem i czasem trwania ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg)). PagerDuty: zakładka `Past Incidents` ([`pagerduty-os-czasu-incydentu.jpg`](./assets/pagerduty-os-czasu-incydentu.jpg)).

**Dlaczego bierzemy:** to jest narzędzie do strojenia progów. Dyspozytor patrzący na alarm „niskie ciśnienie” i widzący, że ta sama reguła odpaliła 14 razy w tym miesiącu, zawsze o 6:00 rano, wie, że problemem jest próg, a nie sieć. Bez tego widoku fałszywe alarmy strojone są ze słuchu.

#### W-07. Czas trwania stanu jako pole pierwszej klasy — **BIERZ**, koszt S

**Gdzie:** Grafana, panel Alert list: `Firing for 8d 9h 53m 21s` ([`grafana-panel-listy-alarmow.jpg`](./assets/grafana-panel-listy-alarmow.jpg)). Zabbix: kolumny `Age` i `Duration` ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg)). ThingsBoard: pole `Duration` w szczegółach alarmu.

**Dlaczego bierzemy:** „Alarm od 4 minut” i „alarm od 8 dni” to dwa różne zadania. Pierwsze wymaga wyjazdu, drugie wymaga rozmowy o tym, czemu nikt go nie zamknął. Dziś nie pokazujemy tego nigdzie.

#### W-08. Grupowanie i opóźnianie powiadomień, opisane po ludzku — **BIERZ**, koszt M (backend: XL)

**Gdzie:** Grafana, polityki powiadomień: _„Wait 30s to group instances · Wait 5m before sending updates · Repeated every 4h”_ ([`grafana-polityki-powiadomien.jpg`](./assets/grafana-polityki-powiadomien.jpg)); schemat routingu instancji do punktów kontaktowych ([`grafana-schemat-routingu.jpg`](./assets/grafana-schemat-routingu.jpg)). Koncepcyjnie ten sam mechanizm co Prometheus Alertmanager (`group_wait`, `group_interval`, `repeat_interval`).

**Dlaczego bierzemy:** §2.6.4 przewiduje „minimalny czas między zdarzeniami” — to deduplikacja pojedynczej reguły. Nie mamy natomiast **grupowania między regułami**, a to jest realny scenariusz: zanik zasilania na obiekcie generuje jednocześnie brak komunikacji, spadek ciśnienia i błąd czujnika. Trzy SMS-y zamiast jednego. Wartość dla nas jest w **sposobie opisania** tych parametrów: zdanie po polsku, nie trzy pola liczbowe.

#### W-09. Adnotacje zdarzeń na wykresie + lista adnotacji — **BIERZ**, koszt M

**Gdzie:** Grafana ([`grafana-adnotacje-na-wykresie.jpg`](./assets/grafana-adnotacje-na-wykresie.jpg)) — pionowe znaczniki na wykresie i pod spodem lista z czasem i tagiem, klikalna do nawigacji.

**Dlaczego bierzemy:** §2.8.3 wymaga „przejścia do wykresu obejmującego okres przed i po zdarzeniu”. Sam skok do zakresu czasu to za mało — bez znacznika na osi operator nie wie, w którym miejscu wykresu patrzeć. Lista pod wykresem daje też odpowiedź na „co się jeszcze wtedy działo”.

#### W-10. Progi naniesione na wykres jako obszary — **BIERZ**, koszt S

**Gdzie:** Grafana, progi jako kolorowe obszary tła wizualizacji ([`grafana-progi-na-wykresie.jpg`](./assets/grafana-progi-na-wykresie.jpg)).

**Dlaczego bierzemy:** UC-02 („analiza historii”) bez progu na wykresie zmusza do trzymania wartości progowej w głowie. Nasz `ObjectMeasurementsChart` nie rysuje dziś żadnej linii odniesienia.

#### W-11. Pasmo stanu w czasie (state timeline) dla łączności — **BIERZ**, koszt M

**Gdzie:** Grafana, wizualizacja State timeline ([`grafana-state-timeline.jpg`](./assets/grafana-state-timeline.jpg)) — poziome pasma stanu z czasem trwania w tooltipie.

**Dlaczego bierzemy:** UC-04 to „utrata komunikacji”. Wykres liniowy jest do tego złym narzędziem — przerwa w danych rysuje się jako prosta łącząca dwa punkty, czyli **jako zmyślony pomiar**. Pasmo stanu pokazuje przerwę jako przerwę. To także jedyny czytelny sposób pokazania historii jakości danych (`good` / `stale` / `sensor_error`) obok szeregu wartości.

#### W-12. Sparkline i mikropaski w wierszu tabeli — **BIERZ**, koszt M

**Gdzie:** Zabbix Top hosts ([`zabbix-widget-top-hosts.jpg`](./assets/zabbix-widget-top-hosts.jpg)) — w jednej komórce pasek proporcji, w innej sparkline trendu.

**Dlaczego bierzemy:** UC-01 to przegląd listy obiektów. Sama liczba „3,4 bar” nie mówi, czy ciśnienie rośnie, spada, czy stoi. Sparkline w kolumnie odpowiada na to bez wchodzenia w obiekt — czyli oszczędza dokładnie te kliknięcia, które kosztują dyspozytora najwięcej.

#### W-13. Kafle zbiorcze nad listą — **BIERZ**, koszt S

**Gdzie:** Zabbix dashboard: rząd „Problems by severity” i rząd „Host availability” nad tabelą bieżących problemów ([`zabbix-dashboard.jpg`](./assets/zabbix-dashboard.jpg)); widget „Problem hosts” jako macierz grupa × severity ([`zabbix-widget-problem-hosts.jpg`](./assets/zabbix-widget-problem-hosts.jpg)).

**Dlaczego bierzemy:** §2.8.1 stawia dashboardowi jedno zadanie: „który obiekt wymaga uwagi i dlaczego”. Kafel z liczbą jest jednocześnie odpowiedzią zbiorczą i filtrem — kliknięcie „3 alarmy” ma zawężać listę pod spodem. To zamienia dwa ekrany w jeden.

#### W-14. Filtr alarmów: severity + wiek + status potwierdzenia + zapisane filtry — **BIERZ**, koszt M

**Gdzie:** Zabbix, filtr widoku Problems ([`zabbix-filtr-problemow.jpg`](./assets/zabbix-filtr-problemow.jpg)); wart uwagi jest przełącznik `Acknowledgement status: All / Unacknowledged / Acknowledged / By me` oraz przycisk `Save as` tworzący z filtru zakładkę.

**Dlaczego bierzemy:** trzy role z §2.7.2 to w praktyce trzy zapisane filtry: pracownik terenowy → „niepotwierdzone, krytyczne, moje”; dyspozytor → „wszystkie aktywne”; zarząd → „zamknięte w tym miesiącu”. Zamiast trzech ekranów wystarczy jeden z trzema presetami.

#### W-15. Kreator warunku bez składni, z podglądem w formie zdania — **BIERZ**, koszt L

**Gdzie:** ThingsBoard ([`thingsboard-filtry-3.jpg`](./assets/thingsboard-filtry-3.jpg), [`thingsboard-filtry-4.jpg`](./assets/thingsboard-filtry-4.jpg)) — trzy pola: klucz, operator, wartość; podgląd `model equal 'DHT22' and batteryLevel less than 20` ([`thingsboard-filtry-podglad.jpg`](./assets/thingsboard-filtry-podglad.jpg)). **Antywzorzec:** Grafana, gdzie reguła to zapytanie w języku źródła danych.

**Dlaczego bierzemy:** §2.8.4 wymaga, żeby próg ustawiał „niezaawansowany użytkownik”. Podgląd zdaniem jest tu ważniejszy niż sam kreator — pozwala operatorowi sprawdzić, czy system zrozumiał go tak, jak chciał, zanim zapisze.

#### W-16. Przypisanie alarmu do osoby — **BIERZ**, koszt M (backend: L)

**Gdzie:** ThingsBoard, pole `Assignee: Unassigned` w szczegółach alarmu ([`thingsboard-szczegoly-alarmu.jpg`](./assets/thingsboard-szczegoly-alarmu.jpg)); PagerDuty, „Assigned to Casey Bennett” w osi czasu ([`pagerduty-os-czasu-incydentu.jpg`](./assets/pagerduty-os-czasu-incydentu.jpg)).

**Dlaczego bierzemy:** w gminie z trzema osobami w brygadzie „kto to bierze” jest rozstrzygane telefonicznie. To działa do momentu, w którym dwie osoby jadą na ten sam obiekt albo żadna. Pole „przypisany” jest tanie, a zamienia listę alarmów w listę zadań. §2.7.3 ma już rolę „Użytkownik operacyjny”, więc model uprawnień tego nie blokuje.

#### W-17. Słownik przyczyn zamknięcia — **BIERZ**, koszt S (backend: M)

**Gdzie:** PagerDuty, pole własne `resolution_category` ustawiane przy zamknięciu ([`pagerduty-os-czasu-incydentu.jpg`](./assets/pagerduty-os-czasu-incydentu.jpg)).

**Dlaczego bierzemy:** §2.5 przewiduje już stan „odrzucony jako fałszywy” — to jest pierwsza pozycja takiego słownika. Reszta (`potwierdzona awaria`, `błąd czujnika`, `problem łączności`, `prace planowe`) kosztuje tyle co pole `select`, a po kwartale daje odpowiedź na pytanie, które progi trzeba przestroić. Bez słownika ta wiedza zostaje w komentarzach i nikt jej nie policzy.

#### W-18. Powiązanie wykresu z regułami, które go pilnują — **BIERZ**, koszt M

**Gdzie:** Grafana, panel „Alerts linked to this dashboard” z listą reguł, ich stanem i liczbą instancji ([`grafana-dashboard-z-regulami.jpg`](./assets/grafana-dashboard-z-regulami.jpg)); ikona stanu przy tytule każdego panelu.

**Dlaczego bierzemy:** w widoku obiektu operator musi móc odpowiedzieć na „czy ten pomiar jest w ogóle pilnowany”. Punkt pomiarowy bez żadnej reguły alarmowej to cichy fałsz bezpieczeństwa — wygląda tak samo jak pilnowany.

#### W-19. Stan pośredni „warunek spełniony, czas jeszcze nie” — **BIERZ**, koszt S

**Gdzie:** Grafana, stan `Pending` w filtrze listy reguł, obok `Firing`, `Normal`, `Recovering` ([`grafana-lista-regul-alarmowych.jpg`](./assets/grafana-lista-regul-alarmowych.jpg)).

**Dlaczego bierzemy:** §2.6.4 przewiduje „czas utrzymania warunku”. Jeśli ten czas wynosi 120 sekund, to przez dwie minuty system wie coś, czego nie pokazuje. Dla dyspozytora, który akurat patrzy na ekran, to jest cenna informacja („zaczyna się”), a nie szum.

#### W-20. Histogram zdarzeń nad listą historii — **BIERZ**, koszt S

**Gdzie:** Grafana, ekran History ([`grafana-historia-alarmow.jpg`](./assets/grafana-historia-alarmow.jpg)) — słupki liczby zdarzeń w czasie nad tabelą przejść stanów.

**Dlaczego bierzemy:** to jedyny widziany sposób, żeby „zalew alarmów” zobaczyć jako kształt, a nie jako przewijanie listy. Dla zarządu (§2.7.2, „liczby i rodzaju wykrytych nieprawidłowości”) to gotowy materiał raportowy.

### 3.2. NIE BIERZ

#### W-21. Synoptyka jako główny widok obiektu — **NIE BIERZ**

**Gdzie:** Inventia DataPortal ([`inventia-synoptyka.jpg`](./assets/inventia-synoptyka.jpg), [`dataportal-synoptyka-laptop.jpg`](./assets/dataportal-synoptyka-laptop.jpg)) i towarzyszący jej edytor ekranów ([`dataportal-edytor.jpg`](./assets/dataportal-edytor.jpg)).

**Dlaczego nie:** trzy niezależne powody. (1) Wartości na synoptyce są podawane bez czasu i jakości — wzorzec strukturalnie zachęca do łamania naszego niezmiennika §2.4.3. (2) Każdy obiekt wymaga osobnego rysunku, czyli pracy integratora przy każdym wdrożeniu; §4.2 planu zakłada wdrożenie tanie i powtarzalne. (3) Rysunek nie skaluje się na telefon, a pracownik terenowy jest naszą pierwszą rolą (§2.7.2). To nie jest kwestia gustu — synoptyka jest droga w wytworzeniu i słabsza w odpowiedzi na „czy jechać”.

#### W-22. Alarmy prezentowane wyłącznie jako mapa z pinami — **NIE BIERZ**

**Gdzie:** Inventia, ekran „ZESTAWIENIE ALARMÓW” ([`inventia-zestawienie-alarmow.jpg`](./assets/inventia-zestawienie-alarmow.jpg)).

**Dlaczego nie:** mapa nie ma porządku. Nie da się jej posortować po ważności ani po czasie, a przy zoomie skupiska zwijają się w liczniki, które ukrywają alarmy. §2.8.1 rozstrzyga to zresztą wprost: _„Mapa obiektów może być funkcją dodatkową, ale nie powinna zastępować czytelnej listy operacyjnej.”_ Mapa jako widok pomocniczy — patrz [W-25](#w-25-mapa-jako-widok-pomocniczy--rozważ).

#### W-23. Surowe kody statusu z automatyki w interfejsie użytkownika — **NIE BIERZ**

**Gdzie:** Inventia, etykiety pinów: `Status: AWARIA_P3`, `Status: POSTÓJ` ([`inventia-zestawienie-alarmow.jpg`](./assets/inventia-zestawienie-alarmow.jpg)).

**Dlaczego nie:** `AWARIA_P3` znaczy coś dla osoby, która programowała sterownik. Dla pracownika gminy jest to napis do zapamiętania. Nasz `statusConfig.ts` robi to dziś dobrze — trzyma osobną mapę etykiet po polsku — i tego nie wolno rozmontować przy dodawaniu nowych typów zdarzeń.

#### W-24. Pełne wypełnienie wiersza nasyconym kolorem — **NIE BIERZ**

**Gdzie:** Ignition Alarm Status Table ([`ignition-tabela-alarmow.jpg`](./assets/ignition-tabela-alarmow.jpg)) — wiersze w całości czerwone i turkusowe.

**Dlaczego nie:** przy pięciu alarmach ekran staje się ścianą koloru, w której nie da się odczytać hierarchii ważności, bo kolor niesie stan (aktywny/ustąpił), a nie priorytet. Dodatkowo tekst na nasyconym tle rzadko utrzymuje kontrast wymagany przez WCAG. Przy naszej skali (kilkanaście obiektów na gminę) kolor powinien być akcentem na krawędzi wiersza albo na znaczniku, nie tłem.

### 3.3. ROZWAŻ

#### W-25. Mapa jako widok pomocniczy — **ROZWAŻ**

**Warunek:** gdy gmina ma > 15 obiektów rozrzuconych na tyle, że dojazd staje się elementem decyzji, i gdy istnieje już działająca lista. Mapa ma wtedy odpowiadać na „w jakiej kolejności je objechać”, a nie na „co się dzieje”. Do MVP nie wchodzi.

#### W-26. Okna serwisowe / planowane tłumienie alarmów — **ROZWAŻ**

**Gdzie:** Zabbix Maintenance ([`zabbix-okno-serwisowe.jpg`](./assets/zabbix-okno-serwisowe.jpg), [`zabbix-harmonogram-serwisowy.jpg`](./assets/zabbix-harmonogram-serwisowy.jpg)).
**Warunek:** gdy pojawi się drugi lub trzeci klient i płukanie sieci zacznie regularnie generować alarmy „nagły wzrost przepływu”. Do tego czasu wystarcza wyciszenie doraźne z [W-04](#w-04-wyciszenie-czasowe-zamiast-trwałego--bierz-koszt-m).

#### W-27. Korelacja przyczyna/objaw — **ROZWAŻ**

**Gdzie:** Zabbix — pole `Rank: Cause` w szczegółach zdarzenia i operacja `Convert to cause` w dialogu aktualizacji ([`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg), [`zabbix-aktualizacja-problemu.jpg`](./assets/zabbix-aktualizacja-problemu.jpg)).
**Warunek:** gdy zdarzy się pierwszy realny „zalew” — pojedyncza awaria generująca cztery alarmy naraz. Wtedy ręczne wskazanie „to jest objaw tamtego” jest tańsze niż automatyczna korelacja i wystarczy. Automatyzacji na tym etapie nie planujemy.

---

## 4. Konfrontacja z naszym interfejsem

Dla każdego wzorca „BIERZ” — co mamy dziś, co trzeba zmienić i w którym pliku. To jest sedno zlecenia: wzorzec bez wskazania miejsca w kodzie jest niedokończoną robotą.

### Z-01. Wartość bez czasu i jakości w liście i na kafelku

**Wzorzec:** [W-01](#w-01-wartość-pomiaru-zawsze-z-czasem-i-statusem-jakości--bierz-koszt-s)
**Stan dzisiejszy — łamiemy własny niezmiennik w dwóch z trzech miejsc:**

| Miejsce | Co pokazuje | Czy zgodne z §2.4.3 |
|---|---|---|
| [`ObjectsTable.tsx:82-102`](../../frontend/src/components/objects/ObjectsTable.tsx#L82-L102) | `${pressure.value} ${pressure.unit}` — sama liczba | ❌ brak czasu, brak jakości |
| [`ObjectCard.tsx:122-129`](../../frontend/src/components/objects/ObjectCard.tsx#L122-L129) | `{point.value} {point.unit}` dla dwóch pierwszych punktów | ❌ brak czasu, brak jakości |
| [`CurrentValueCard.tsx:45-59`](../../frontend/src/components/objects/CurrentValueCard.tsx#L45-L59) | wartość + `StatusPill kind="quality"` + „Zmierzono X temu” | ✅ jedyne zgodne miejsce |

Kolumna „Świeżość” w tabeli dotyczy **ostatniego kontaktu z gatewayem**, nie czasu konkretnego pomiaru — to nie to samo. Gateway może się odzywać co minutę, a jeden z czujników być w stanie `sensor_error` od godziny.

**Zmiana:** w `ObjectsTable.tsx` i `ObjectCard.tsx` renderować wartość przez wspólny komponent `MeasurementValue`, który przyjmuje `{ value, unit, measuredAt, quality }` i nigdy nie renderuje samej liczby. Wydzielić go z `CurrentValueCard.tsx` do `components/ui/MeasurementValue.tsx` — dziś ta logika istnieje tylko tam i jest wpleciona w układ kafla. Przy jakości innej niż `good` wartość powinna być wizualnie osłabiona (kolor drugorzędny) — nie ukryta, ale wyraźnie oznaczona.

**Uwaga uboczna:** `CurrentValueCard.tsx` renderuje tekst „Zmierzono {czas}” dwukrotnie — raz w popoverze ([:38-40](../../frontend/src/components/objects/CurrentValueCard.tsx#L38-L40)), raz pod spodem ([:57-59](../../frontend/src/components/objects/CurrentValueCard.tsx#L57-L59)). Przy okazji refaktoru zostawić jedno.

### Z-02. Trzy różne, niezgodne pojęcia „świeżości” w jednym froncie

**Wzorzec:** [W-01](#w-01-wartość-pomiaru-zawsze-z-czasem-i-statusem-jakości--bierz-koszt-s)
**Stan dzisiejszy:**

| Plik | Definicja świeżości | Progi |
|---|---|---|
| [`FreshnessBar.tsx:26`](../../frontend/src/components/ui/FreshnessBar.tsx#L26) | pasek postępu do `expectedIntervalSeconds` | domyślnie **300 s** |
| [`FreshnessBar.tsx:45-49`](../../frontend/src/components/ui/FreshnessBar.tsx#L45-L49) | kolor paska | < 50 % zielony, < 80 % żółty, ≥ 80 % czerwony |
| [`deviceFreshness.ts:10-15`](../../frontend/src/lib/deviceFreshness.ts#L10-L15) | `getFreshness()` | `fresh` < **1 h**, `warn` < **3 dni**, dalej `stale` |
| [`statusConfig.ts:31-39`](../../frontend/src/lib/statusConfig.ts#L31-L39) | `DATA_QUALITY_COLOR_MAP` ze statusem `stale` z backendu | próg po stronie serwera |

**Problem główny — domyślne 300 s jest pięciokrotnie za duże.** Gateway wysyła paczkę co ~60 s: [`TelemetryPayload.h:34-37`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h#L34-L37) ustala `WINDOWS_PER_BATCH = 4` przy `WINDOW_SECONDS = 15`. Przy domyślnym `expectedIntervalSeconds = 300` pasek po **czterech nieudanych transmisjach** stoi wciąż na ~80 % w kolorze żółtym. Żadne z wywołań `FreshnessBar` nie podaje własnej wartości ([`ObjectCard.tsx:137`](../../frontend/src/components/objects/ObjectCard.tsx#L137), [`ObjectsTable.tsx:109`](../../frontend/src/components/objects/ObjectsTable.tsx#L109)) — wszystkie używają domyślnej.

**Zmiana:**
1. Domyślną wartość ustawić na 60 s i — docelowo — pobierać ją z konfiguracji urządzenia, a nie zaszywać w komponencie. Do czasu, aż backend to wystawi, przekazywać stałą z jednego miejsca.
2. Zdecydować, które pojęcie jest kanoniczne. Rekomendacja: `deviceFreshness.ts` opisuje **urządzenie** (kiedy ostatnio się odezwało), `FreshnessBar` opisuje **oczekiwanie na następną paczkę**. To dwie różne rzeczy i powinny mieć dwie różne nazwy — dziś obie nazywają się „freshness” i to jest źródło pomyłek.
3. Kolory paska pobierać z tokenów (`--color-status-*`), nie z `bg-green-500` / `bg-yellow-500` / `bg-red-500` wpisanych na sztywno ([`FreshnessBar.tsx:46-48`](../../frontend/src/components/ui/FreshnessBar.tsx#L46-L48)) — dziś pasek nie zmieni się razem z paletą.

**Uwaga uboczna:** [`freshnessUtils.ts:2`](../../frontend/src/components/ui/freshnessUtils.ts#L2) generuje napis `„12 sec temu”` — kalka z angielskiego w polskim interfejsie. Powinno być „12 s temu” albo „przed chwilą”.

### Z-03. Dashboard istnieje w kodzie, ale jest nieosiągalny

**Wzorzec:** [W-13](#w-13-kafle-zbiorcze-nad-listą--bierz-koszt-s)
**Stan dzisiejszy:** [`App.tsx:58-59`](../../frontend/src/App.tsx#L58-L59) przekierowuje `/` i `/dashboard` na `/objects`. [`DashboardPage.tsx`](../../frontend/src/pages/DashboardPage.tsx) nie jest importowany nigdzie poza własnym testem, a jedyny jego komponent, [`ObjectsStatusTable.tsx`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx) (216 linii, własna paginacja, własny filtr statusu), nie jest używany przez nic innego. To martwy kod, który udaje działającą funkcję.

**Zmiana:** rozstrzygnąć jedną z dwóch dróg i zrobić ją do końca.
- **Droga A (rekomendowana):** `/objects` zostaje jedynym ekranem przeglądu i dostaje rząd kafli zbiorczych na górze (W-13). `DashboardPage.tsx` i `ObjectsStatusTable.tsx` zostają usunięte. Uzasadnienie: przy kilkunastu obiektach na gminę osobny dashboard i lista pokazują to samo dwa razy.
- **Droga B:** `/dashboard` wraca jako trasa i staje się ekranem startowym z kaflami; `/objects` zostaje zarządzaniem. Wymaga wtedy rozbudowy `ObjectsStatusTable` o świeżość i wartości, których dziś nie pokazuje.

Zostawienie stanu obecnego jest najgorszą opcją — utrzymujemy dwa niezależne widoki listy obiektów, z których jeden nikomu się nie wyświetla.

### Z-04. Brak widoku alarmów — i brak miejsca, w które miałby wejść

**Wzorzec:** [W-03](#w-03-jeden-dialog-aktualizacji-alarmu-z-obowiązkowym-śladem--bierz-koszt-l), [W-14](#w-14-filtr-alarmów-severity--wiek--status-potwierdzenia--zapisane-filtry--bierz-koszt-m)
**Stan dzisiejszy:** [`OrgSidebar.tsx:29-43`](../../frontend/src/components/layout/OrgSidebar.tsx#L29-L43) ma dwie pozycje: „Obiekty” (sekcja *Monitorowanie*) i „Urządzenia” (sekcja *Konfiguracja*). Sekcja „Administracja” istnieje w kodzie ([:70](../../frontend/src/components/layout/OrgSidebar.tsx#L70)), ale jest pusta i przez [:83](../../frontend/src/components/layout/OrgSidebar.tsx#L83) nigdy się nie renderuje. Alarmów nie ma ani w nawigacji, ani w trasach, ani w widoku obiektu.

**Zmiana:** pełny projekt ekranu w [§6](#6-projekt-widoku-alarmów). Nawigacja: [§5](#5-rekomendacja-architektury-informacji).

### Z-05. Wykres nie odróżnia braku danych od danych

**Wzorzec:** [W-11](#w-11-pasmo-stanu-w-czasie-state-timeline-dla-łączności--bierz-koszt-m), [W-10](#w-10-progi-naniesione-na-wykres-jako-obszary--bierz-koszt-s), [W-09](#w-09-adnotacje-zdarzeń-na-wykresie--lista-adnotacji--bierz-koszt-m)
**Stan dzisiejszy:** [`ObjectMeasurementsChart.tsx:174-188`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L174-L188) rysuje `<Line type="monotone" ... dot={false}>`. Przy przerwie w transmisji recharts połączy dwa punkty odległe o godziny **gładką krzywą** — czyli narysuje pomiar, którego nie było. To ten sam błąd co u konkurenta z W-21, tylko subtelniejszy.

**Zmiana:**
1. Przerwać serię tam, gdzie odstęp między próbkami przekracza wielokrotność oczekiwanego interwału (wstawić `null` w danych — recharts przerywa wtedy linię).
2. Dodać pod wykresem pasmo stanu łączności/jakości (W-11).
3. Dodać linie progów jako `ReferenceLine`/`ReferenceArea` (W-10), gdy reguły alarmowe będą już istnieć.
4. Dodać `ReferenceLine` dla zdarzeń alarmowych w wyświetlanym zakresie (W-09) — to zamyka wymaganie §2.8.3 o wykresie „przed i po zdarzeniu”.

**Uwaga uboczna:** kolory osi i siatki są wpisane na sztywno jako `#e5e7eb` / `#9ca3af` ([:148-159](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L148-L159)), podczas gdy serie używają już zmiennych `var(--color-chart-N)`. Niespójne, i blokuje ewentualny motyw ciemny.

### Z-06. `StatusPill` koduje status kolorem i tekstem, ale nie kształtem

**Wzorzec:** [W-24](#w-24-pełne-wypełnienie-wiersza-nasyconym-kolorem--nie-bierz) (od strony pozytywnej)
**Stan dzisiejszy:** [`StatusPill.tsx:43`](../../frontend/src/components/ui/StatusPill.tsx#L43) renderuje `<span>●</span>` w kolorze wynikającym ze statusu, obok etykiety tekstowej. Kropka jest **zawsze tym samym znakiem** — niesie wyłącznie kolor. Nośnikami znaczenia są więc kolor i tekst; kształt nie niesie nic.

Dodatkowo w [`statusConfig.ts:15-21`](../../frontend/src/lib/statusConfig.ts#L15-L21) `no_comm` mapuje się na `danger`, a `danger` w [`:54`](../../frontend/src/lib/statusConfig.ts#L54) to paleta `status-no-comm-*`, która w [`tokens.css:57-60`](../../frontend/src/styles/tokens.css#L57-L60) jest **szara**. Czyli semantyczna nazwa „danger” daje kolor szary. To działa, ale nazwa kłamie i przy następnej zmianie palety ktoś to zepsuje.

**Zmiana:** rozróżniać kształt znacznika per status (np. `●` ok, `▲` ostrzeżenie, `■` alarm, `○` brak danych, `⊘` brak komunikacji) albo użyć ikon `lucide-react`, które już są w zależnościach. Tekst zostaje. Przemianować `danger` → `muted-alert` albo wprost `no-comm`, żeby nazwa semantyczna odpowiadała kolorowi.

**To nie jest kosmetyka:** w liście obiektów status jest jedyną informacją, która ma być odczytana „rzutem oka”, a wydruk czarno-biały i częsty w populacji daltonizm sprowadzają wtedy odczyt do samego tekstu.

### Z-07. `tokens.css` deklaruje kolor alarmu jako nieużywany, choć jest używany

**Stan dzisiejszy:** [`tokens.css:50`](../../frontend/src/styles/tokens.css#L50) — komentarz `/* Alarm — czerwony (Etap 5, teraz nieużywany ale zarezerwowany) */`. Tymczasem `statusConfig.ts` mapuje `alarm → danger-strong → bg-status-alarm-50 …` ([:18](../../frontend/src/lib/statusConfig.ts#L18), [:55](../../frontend/src/lib/statusConfig.ts#L55)) i `StatusPill` renderuje to dla każdego obiektu w stanie `alarm`.

**Zmiana:** poprawić komentarz. Drobiazg, ale komentarz, który kłamie o stanie systemu, jest gorszy niż brak komentarza — a ten akurat dotyczy koloru alarmu.

### Z-08. `DataTable` ma sortowanie, którego nikt nie włącza, i nie mówi o nim czytnikom ekranu

**Wzorzec:** [W-12](#w-12-sparkline-i-mikropaski-w-wierszu-tabeli--bierz-koszt-m), [W-14](#w-14-filtr-alarmów-severity--wiek--status-potwierdzenia--zapisane-filtry--bierz-koszt-m)
**Stan dzisiejszy:** [`DataTable.tsx:31-33`](../../frontend/src/components/ui/DataTable.tsx#L31-L33) przyjmuje `sortBy`/`sortDir`/`onSort`, a [`:129-142`](../../frontend/src/components/ui/DataTable.tsx#L129-L142) obsługuje kliknięcie nagłówka. Żadna z tabel obiektów nie przekazuje tych propsów ani nie ustawia `sortable: true` — sortowania w praktyce nie ma. Nagłówek jest klikalnym `<th>` bez `<button>`, bez `aria-sort` i bez obsługi klawiatury. Tabela nie ma też kontenera `overflow-x-auto` ([:120-121](../../frontend/src/components/ui/DataTable.tsx#L120-L121)) — na wąskim ekranie rozpycha stronę w poziomie.

**Zmiana:** włączyć sortowanie w `ObjectsTable` (po statusie, po świeżości, po nazwie), owinąć treść nagłówka w `<button>` z `aria-sort` na `<th>`, dodać `overflow-x-auto` na kontenerze tabeli.

### Z-09. Zakresy czasu wykresu bez zakresu własnego i bez pamięci wyboru

**Wzorzec:** [W-09](#w-09-adnotacje-zdarzeń-na-wykresie--lista-adnotacji--bierz-koszt-m)
**Stan dzisiejszy:** [`ObjectDetailPage.tsx:136-141`](../../frontend/src/pages/ObjectDetailPage.tsx#L136-L141) — cztery przyciski `2h / 24h / 7d / 30d`, stan trzymany lokalnie w `useState`, nieobecny w URL. Nie da się podać komuś linku do wykresu z konkretnego okna czasowego, a przejście „do wykresu obejmującego okres przed i po zdarzeniu” (§2.8.3) wymaga dokładnie tego.

**Zmiana:** przenieść zakres czasu do parametrów URL (`?from=&to=`), dodać zakres własny. Grafana robi to tak samo — zakres w adresie ([`grafana-adnotacje-na-wykresie.jpg`](./assets/grafana-adnotacje-na-wykresie.jpg), adres `?from=now-24h&to=now`), co czyni każdy wykres linkowalnym.

### Z-10. Widok obiektu nie pokazuje, czy pomiar jest w ogóle pilnowany

**Wzorzec:** [W-18](#w-18-powiązanie-wykresu-z-regułami-które-go-pilnują--bierz-koszt-m)
**Stan dzisiejszy:** [`ObjectDetailPage.tsx:104-108`](../../frontend/src/pages/ObjectDetailPage.tsx#L104-L108) ma dwie zakładki: „Aktualne wartości” i „Wykresy pomiarów”. Nie ma alarmów, nie ma diagnostyki gatewaya, nie ma informacji o regułach.

**Zmiana:** rozszerzyć do czterech zakładek — „Przegląd”, „Wykresy”, „Alarmy” (zdarzenia tego obiektu), „Diagnostyka” (stan gatewaya, wersja konfiguracji, historia komunikacji — §2.8.2 wymienia to wprost). Na kafelku punktu pomiarowego (`CurrentValueCard`) dodać wskaźnik „pilnowany przez N reguł” albo ostrzeżenie „brak reguły alarmowej”.

### Z-11. Kafle nagłówka widoku obiektu marnują najlepsze miejsce na ekranie

**Stan dzisiejszy:** [`ObjectDetailPage.tsx:68-100`](../../frontend/src/pages/ObjectDetailPage.tsx#L68-L100) — cztery kafle: Organizacja, Ostatni kontakt, **Sekwencja**, Pomiary (liczba). „Sekwencja” (`last_seq`) to numer sekwencyjny paczki telemetrycznej — informacja diagnostyczna dla nas, nie dla operatora gminy. „Organizacja” jest zawsze ta sama w kontekście zalogowanego użytkownika.

**Zmiana:** zastąpić kafle „Organizacja” i „Sekwencja” przez „Aktywne alarmy” i „Typ obiektu / lokalizacja”. `last_seq` przenieść do zakładki „Diagnostyka”.

### Z-12. Brak jakiejkolwiek ścieżki eksportu

**Stan dzisiejszy:** §2.8.2 („możliwość eksportu danych”) i UC-05 („Raport i eksport”) nie mają odpowiednika w kodzie — `grep` po froncie nie znajduje żadnej akcji eksportu.

**Zmiana:** przycisk „Pobierz CSV” przy wykresie, eksportujący dokładnie ten zakres i te punkty pomiarowe, które są aktualnie wybrane. To najtańsza możliwa realizacja UC-05 i realnie zdejmuje z nas dużą część pytań o raporty.

---

## 5. Rekomendacja architektury informacji

### 5.1. Punkt wyjścia — trzy role, trzy pytania

| Rola (§2.7.2) | Pytanie, na które musi odpowiedzieć w 5 sekund | Urządzenie | Ekran domyślny |
|---|---|---|---|
| **Pracownik terenowy** | „Czy jechać, i na który obiekt?” | telefon | Alarmy, preset „niepotwierdzone” |
| **Kierownik / dyspozytor** | „Co się dzieje w całej gminie?” | desktop | Obiekty z kaflami zbiorczymi |
| **Zarząd / urząd** | „Ile było zdarzeń i jak szybko je obsłużono?” | desktop, rzadko | Raporty (Faza 2) |

### 5.2. Proponowana nawigacja

```
Monitorowanie
├─ Obiekty          ← domyślny ekran dyspozytora; kafle zbiorcze + lista
└─ Alarmy           ← NOWE; domyślny ekran pracownika terenowego
Konfiguracja
├─ Urządzenia       ← jest dziś
├─ Punkty pomiarowe ← jest dziś, ale schowane pod urządzeniem
└─ Reguły alarmowe  ← NOWE (Faza 2)
Administracja
└─ (pozostaje pod menu użytkownika)
```

Zmiany względem [`OrgSidebar.tsx:29-43`](../../frontend/src/components/layout/OrgSidebar.tsx#L29-L43):

1. **Dodać „Alarmy”** w sekcji *Monitorowanie*, z licznikiem niepotwierdzonych alarmów przy etykiecie. Licznik w nawigacji to jedyny element interfejsu, który jest widoczny na każdym ekranie — i dlatego jedyne miejsce, w którym „coś się dzieje” dociera do użytkownika, który akurat patrzy gdzie indziej.
2. **Nie dodawać osobnego „Dashboardu”.** Przy kilkunastu obiektach na gminę lista z kaflami zbiorczymi jest dashboardem. Konsekwencja: droga A z [Z-03](#z-03-dashboard-istnieje-w-kodzie-ale-jest-nieosiągalny).
3. **Ekran domyślny zależny od roli.** Użytkownik z uprawnieniem operacyjnym po zalogowaniu trafia na „Alarmy”; pozostali na „Obiekty”. Mechanizm istnieje — `useActivePermissions()` jest już jedynym źródłem prawdy o uprawnieniach ([`frontend-architecture.md` §5](../technical/frontend/frontend-architecture.md)).
4. **Usunąć martwą sekcję „Administracja”** z `OrgSidebar` albo ją wypełnić — dziś jest zadeklarowana i nigdy nie renderowana.

### 5.3. Ścieżka od alarmu do decyzji

Docelowa ścieżka pracownika terenowego, maksymalnie trzy kliknięcia od powiadomienia do decyzji „jadę / nie jadę”:

```
Powiadomienie (SMS/e-mail)
   │ link
   ▼
Alarmy → wiersz alarmu                  [1 kliknięcie: rozwinięcie panelu bocznego]
   ├─ wartość, która wyzwoliła regułę + czas + jakość
   ├─ wykres 2 h przed i 30 min po, ze znacznikiem zdarzenia
   ├─ stan gatewaya (zasilanie, sygnał, ostatni kontakt)
   └─ „Poprzednie wystąpienia (12)”
   ▼
[Potwierdź i przypisz do mnie]          [2 kliknięcie]
   ▼
[Wycisz na 2 h — jadę]                  [3 kliknięcie]
```

Wszystko bez opuszczania listy alarmów — panel boczny (`Drawer`, który już mamy w [`components/ui/Drawer.tsx`](../../frontend/src/components/ui/Drawer.tsx)), nie osobna strona. Powód: po obsłużeniu jednego alarmu operator ma zwykle przed sobą kolejny, a powrót do listy przez „wstecz” gubi filtr i pozycję przewinięcia.

---

## 6. Projekt widoku alarmów

Ekran nie istnieje ani we froncie, ani w backendzie. Poniższy opis jest na tyle szczegółowy, żeby dało się z niego zaimplementować bez zgadywania — łącznie z tym, co musi wystawić backend.

### 6.1. Układ

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Alarmy                                       [Niepotwierdzone ▾] [Zapisz]  │  ← presety filtrów
├────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ Krytyczne│ │Ostrzeżeń │ │  Nowe    │ │ Wyciszone│ │Bez łączn.│          │  ← kafle-filtry (W-13)
│ │    2     │ │    5     │ │    3     │ │    1     │ │    1     │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├────────────────────────────────────────────────────────────────────────────┤
│ Filtry: [Ważność ▾] [Stan ▾] [Obiekt ▾] [Okres ▾] [☐ tylko moje]  Wyczyść │
├────────────────────────────────────────────────────────────────────────────┤
│ ▲ │ Obiekt          │ Zdarzenie          │ Wartość      │ Od      │ Kto   │
│ ■ │ SUW Kolonia     │ Bardzo niskie ciśn.│ 1,62 bar     │ 23 min  │ —     │
│   │                 │ próg < 2,0 bar     │ ✓ 12:41      │         │       │
│ ▲ │ Przepomp. Dolna │ Brak komunikacji   │ —            │ 1 h 12  │ J.K.  │
│ ● │ Komora Polna    │ Ciśnienie wysokie  │ 4,71 bar     │ 3 h     │ —     │
│   │                 │ ↳ wyciszone do 15:00                                │
└────────────────────────────────────────────────────────────────────────────┘
```

**Kolumny — uzasadnienie każdej:**

| Kolumna | Skąd wzorzec | Po co |
|---|---|---|
| Znacznik ważności (kształt + kolor) | W-24 od strony pozytywnej, Z-06 | odczyt rzutem oka, także na wydruku |
| Obiekt wodociągowy | §2.8.3 „filtrowanie po obiekcie” | pierwsza rzecz, której szuka operator |
| Zdarzenie + próg reguły | §2.8.3 „wartości, które uruchomiły regułę” | bez progu wartość nic nie mówi |
| Wartość + czas + jakość | W-01 | niezmiennik §2.4.3 obowiązuje też tutaj |
| „Od” (czas trwania) | W-07 | „23 min” i „8 dni” to dwa różne zadania |
| Przypisany | W-16 | żeby dwie osoby nie jechały na ten sam obiekt |

Wyciszenie pokazywane jest jako **wiersz podrzędny z terminem**, nie przez ukrycie wiersza — to bezpośredni wniosek z Zabbiksa („Show suppressed problems” jako świadomy przełącznik, a nie domyślne ukrycie).

### 6.2. Model stanu alarmu

Rekomendowana zmiana wobec §2.5 planu biznesowego: **dwie niezależne osie zamiast jednego łańcucha** (W-02).

```
Oś 1 — stan warunku (ustala system)
   AKTYWNY  ←→  USTĄPIŁ

Oś 2 — stan obsługi (ustala człowiek)
   NOWY → POTWIERDZONY → ZAMKNIĘTY
                       ↘ ODRZUCONY (fałszywy)

Oś 3 — tłumienie (niezależne, z terminem)
   widoczny  ←→  wyciszony do <czas>
```

Cztery kombinacje z osi 1 × 2, które muszą być rozróżnialne w interfejsie:

| Warunek | Obsługa | Co to znaczy operacyjnie | Jak pokazać |
|---|---|---|---|
| aktywny | nowy | **wymaga reakcji teraz** | góra listy, pełna ważność |
| aktywny | potwierdzony | ktoś się tym zajmuje | ważność wyszarzona, widoczny „kto” |
| ustąpił | nowy | **problem minął sam, nikt tego nie widział** | osobna sekcja „do przejrzenia” |
| ustąpił | potwierdzony/zamknięty | historia | poza listą domyślną |

Trzeci wiersz jest tym, co dziś gubimy — i jest to najczęstszy przypadek przy monitoringu ciśnienia, gdzie krótkie zapady zdarzają się w nocy.

**Konsekwencja dla backendu:** rekord alarmu potrzebuje osobno `condition_state` i `handling_state`, a nie jednego pola `status`. Zmiana po fakcie kosztuje migrację danych.

### 6.3. Panel szczegółów (Drawer)

Otwierany kliknięciem wiersza, bez zmiany trasy — z parametrem w URL, żeby dało się podać link.

```
Bardzo niskie ciśnienie — SUW Kolonia                              [✕]
────────────────────────────────────────────────────────────────────
Reguła:    ciśnienie < 2,0 bar utrzymane przez 120 s
Wartość:   1,62 bar   ✓ dobra jakość   pomiar 12:41:03
Trwa:      23 min                    Przypisany: —   [Przypisz do mnie]
────────────────────────────────────────────────────────────────────
[ wykres: 2 h przed → 30 min po, ze znacznikiem zdarzenia          ]
[ pasmo łączności pod wykresem                                     ]
[ linia progu 2,0 bar                                              ]
────────────────────────────────────────────────────────────────────
Stan gatewaya w chwili zdarzenia
  Ostatni kontakt 12:41 · Sygnał −79 dBm · Zasilanie OK
────────────────────────────────────────────────────────────────────
Poprzednie wystąpienia tej reguły (12)                    [rozwiń ▾]
  04.09 12:41 — trwa
  03.09 05:12 — 18 min — zamknięty: potwierdzona awaria
  01.09 05:09 — 22 min — zamknięty: fałszywy alarm
────────────────────────────────────────────────────────────────────
Historia reakcji
  12:44  Jan K.  potwierdził  „jadę na obiekt”
────────────────────────────────────────────────────────────────────
Wysłane powiadomienia
  12:42  SMS → +48 …  dostarczony
  12:42  e-mail → dyspozytor@…  BŁĄD: nieznany adres
────────────────────────────────────────────────────────────────────
[ Aktualizuj alarm ]                              [ Pokaż w obiekcie ]
```

Sekcje „Poprzednie wystąpienia” (W-06) i „Wysłane powiadomienia” ze statusem dostarczenia (W-05) są tym, co odróżnia ten ekran od zwykłej listy powiadomień. Sekcja „Stan gatewaya w chwili zdarzenia” odpowiada wprost na pytanie pracownika terenowego z §2.7.2: _„czy działa zasilanie i komunikacja”_.

### 6.4. Dialog „Aktualizuj alarm”

Jedno okno, wzorowane na Zabbiksie (W-03), zamiast pięciu osobnych przycisków:

```
Aktualizuj alarm — Bardzo niskie ciśnienie, SUW Kolonia
────────────────────────────────────────────────────────────────
Komentarz  [_____________________________________________]

☐ Potwierdź
☐ Przypisz do:            [ Jan Kowalski ▾ ]
☐ Wycisz:    ( ) bezterminowo   (•) do [ 15:00 ▾ ]
☐ Zamknij, przyczyna:     [ potwierdzona awaria ▾ ]
                            · potwierdzona awaria
                            · błąd czujnika
                            · problem łączności
                            · prace planowe
                            · fałszywy alarm — do przestrojenia progu
☐ Zmień ważność:          [ krytyczny ▾ ]

Wymagany jest komentarz albo co najmniej jedna operacja.
                                            [ Anuluj ]  [ Zapisz ]
```

Trzy decyzje projektowe, każda przeniesiona z konkretnej obserwacji:

1. **Wymuszony ślad** — nie da się zapisać pustej aktualizacji (Zabbix: _„At least one update operation or message must exist”_). Bez tego historia reakcji będzie pełna wpisów „potwierdzono” bez kontekstu.
2. **Wyciszenie domyślnie terminowe** (W-04) — opcja bezterminowa istnieje, ale nie jest domyślna.
3. **Słownik przyczyn zamknięcia** (W-17) — pozycja „fałszywy alarm — do przestrojenia progu” jest sformułowana tak, żeby jej wybór był jednocześnie zgłoszeniem do strojenia. Po kwartale zapytanie „ile alarmów zamknięto tą przyczyną, wg reguły” jest gotową listą progów do poprawy.

### 6.5. Stany brzegowe

| Sytuacja | Co pokazać |
|---|---|
| Brak alarmów | Znacznik ✓ i tekst „Brak aktywnych zdarzeń · ostatnie sprawdzenie HH:MM”. Pusty ekran bez czasu ostatniego sprawdzenia jest niejednoznaczny — nie wiadomo, czy nic się nie dzieje, czy system nie działa |
| Brak alarmów, bo wszystkie wyciszone | „Brak aktywnych zdarzeń · 3 wyciszone” z linkiem do wyciszonych. Nie wolno pokazać czystego ✓ |
| Backend niedostępny | Komunikat błędu z przyciskiem ponowienia — nigdy pusta lista, która wygląda jak „wszystko OK” |
| Alarm na obiekcie bez łączności | Znacznik „dane sprzed X” przy wartości; wartość, która wyzwoliła regułę, jest historyczna |

Ostatni wiersz w tabeli powyżej to najpoważniejsza pułapka tego ekranu: pusta lista alarmów i awaria backendu wyglądają identycznie, a znaczą coś przeciwnego.

### 6.6. Czego backend musi dostarczyć

Ekran nie da się zbudować bez tych pól — warto je ustalić przed implementacją modułu alarmów:

| Pole | Uzasadnienie |
|---|---|
| `condition_state`, `handling_state` osobno | §6.2, W-02 |
| `triggered_value`, `triggered_at`, `triggered_quality` | §2.8.3 „wartości, które uruchomiły regułę”; W-01 |
| `rule_snapshot` (próg i czas utrzymania **w chwili zdarzenia**) | reguła mogła zostać później zmieniona; bez migawki historia kłamie |
| `assigned_to` | W-16 |
| `suppressed_until` | W-04 |
| `close_reason` ze słownika | W-17 |
| lista wpisów historii reakcji (czas, użytkownik, akcja, komentarz) | W-03 |
| lista wysłanych powiadomień ze **statusem dostarczenia** | W-05, §2.8.3 |
| licznik i lista poprzednich wystąpień tej samej reguły | W-06 |
| migawka stanu gatewaya z chwili zdarzenia | §2.7.2, §2.8.2 |

---

## 7. Backlog zmian we froncie

Uszeregowany wg stosunku wartości do kosztu. „Wartość” oceniana względem przypadków użycia UC-01…UC-05 i niezmienników z §2.4.3.

### Poziom 1 — tanie i naprawiające rzeczy zepsute

| # | Zmiana | Pliki | Koszt | Uzasadnienie |
|---|---|---|---|---|
| 1 | Domyślny interwał `FreshnessBar` 300 s → 60 s + kolory z tokenów | [`FreshnessBar.tsx`](../../frontend/src/components/ui/FreshnessBar.tsx) | S | [Z-02](#z-02-trzy-różne-niezgodne-pojęcia-świeżości-w-jednym-froncie) — dziś pasek nie zauważa czterech utraconych transmisji |
| 2 | `MeasurementValue` — wartość zawsze z czasem i jakością | [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx), [`ObjectCard.tsx`](../../frontend/src/components/objects/ObjectCard.tsx), nowy `components/ui/` | S | [Z-01](#z-01-wartość-bez-czasu-i-jakości-w-liście-i-na-kafelku) — łamiemy własny niezmiennik §2.4.3 |
| 3 | Przerwanie linii wykresu przy luce w danych | [`ObjectMeasurementsChart.tsx`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx) | S | [Z-05](#z-05-wykres-nie-odróżnia-braku-danych-od-danych) — dziś rysujemy pomiary, których nie było |
| 4 | Rozstrzygnięcie losu `DashboardPage` (droga A) | [`App.tsx`](../../frontend/src/App.tsx), usunięcie 2 plików | S | [Z-03](#z-03-dashboard-istnieje-w-kodzie-ale-jest-nieosiągalny) — martwy kod udający funkcję |
| 5 | Kształt znacznika per status w `StatusPill` | [`StatusPill.tsx`](../../frontend/src/components/ui/StatusPill.tsx), [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) | S | [Z-06](#z-06-statuspill-koduje-status-kolorem-i-tekstem-ale-nie-kształtem) |
| 6 | Zakres czasu wykresu w URL + zakres własny | [`ObjectDetailPage.tsx`](../../frontend/src/pages/ObjectDetailPage.tsx) | S | [Z-09](#z-09-zakresy-czasu-wykresu-bez-zakresu-własnego-i-bez-pamięci-wyboru) — warunek konieczny dla §2.8.3 |
| 7 | Poprawki uboczne: „sec temu”, podwójne „Zmierzono”, komentarz w `tokens.css`, kolory osi wykresu | 4 pliki | S | [Z-02](#z-02-trzy-różne-niezgodne-pojęcia-świeżości-w-jednym-froncie), [Z-01](#z-01-wartość-bez-czasu-i-jakości-w-liście-i-na-kafelku), [Z-07](#z-07-tokenscss-deklaruje-kolor-alarmu-jako-nieużywany-choć-jest-używany), [Z-05](#z-05-wykres-nie-odróżnia-braku-danych-od-danych) |

### Poziom 2 — widok alarmów (największa pojedyncza wartość)

| # | Zmiana | Koszt | Zależność |
|---|---|---|---|
| 8 | Trasa `/alarms` + pozycja w `OrgSidebar` z licznikiem | S | — |
| 9 | Lista alarmów z kaflami-filtrami i filtrem (§6.1) | M | backend: lista alarmów |
| 10 | Panel szczegółów alarmu (§6.3) | L | backend: §6.6 |
| 11 | Dialog „Aktualizuj alarm” (§6.4) | M | backend: historia reakcji, słownik przyczyn |
| 12 | Zakładka „Alarmy” w widoku obiektu | S | 9 |

### Poziom 3 — jakość odczytu i analiza

| # | Zmiana | Koszt | Wzorzec |
|---|---|---|---|
| 13 | Kafle zbiorcze nad listą obiektów | S | [W-13](#w-13-kafle-zbiorcze-nad-listą--bierz-koszt-s) |
| 14 | Sortowanie i dostępność w `DataTable` + `overflow-x-auto` | S | [Z-08](#z-08-datatable-ma-sortowanie-którego-nikt-nie-włącza-i-nie-mówi-o-nim-czytnikom-ekranu) |
| 15 | Sparkline w wierszu tabeli obiektów | M | [W-12](#w-12-sparkline-i-mikropaski-w-wierszu-tabeli--bierz-koszt-m) |
| 16 | Pasmo stanu łączności/jakości pod wykresem | M | [W-11](#w-11-pasmo-stanu-w-czasie-state-timeline-dla-łączności--bierz-koszt-m) |
| 17 | Progi i adnotacje zdarzeń na wykresie | M | [W-10](#w-10-progi-naniesione-na-wykres-jako-obszary--bierz-koszt-s), [W-09](#w-09-adnotacje-zdarzeń-na-wykresie--lista-adnotacji--bierz-koszt-m) |
| 18 | Eksport CSV bieżącego zakresu | S | [Z-12](#z-12-brak-jakiejkolwiek-ścieżki-eksportu) |
| 19 | Cztery zakładki w widoku obiektu + przebudowa kafli nagłówka | M | [Z-10](#z-10-widok-obiektu-nie-pokazuje-czy-pomiar-jest-w-ogóle-pilnowany), [Z-11](#z-11-kafle-nagłówka-widoku-obiektu-marnują-najlepsze-miejsce-na-ekranie) |

### Poziom 4 — Faza 2

| # | Zmiana | Koszt | Wzorzec |
|---|---|---|---|
| 20 | Kreator reguł alarmowych bez składni, z podglądem zdaniem | L | [W-15](#w-15-kreator-warunku-bez-składni-z-podglądem-w-formie-zdania--bierz-koszt-l) |
| 21 | Zapisane filtry jako presety per rola | M | [W-14](#w-14-filtr-alarmów-severity--wiek--status-potwierdzenia--zapisane-filtry--bierz-koszt-m) |
| 22 | Histogram zdarzeń nad historią alarmów | S | [W-20](#w-20-histogram-zdarzeń-nad-listą-historii--bierz-koszt-s) |
| 23 | Okna serwisowe | M | [W-26](#w-26-okna-serwisowe--planowane-tłumienie-alarmów--rozważ) |
| 24 | Ręczne oznaczanie „to jest objaw tamtego” | M | [W-27](#w-27-korelacja-przyczynaobjaw--rozważ) |

---

## 8. Wymiar 8 — praca na telefonie

Dokument z zlecenia B-12 nie istniał w chwili realizacji tego briefu, więc wymiar 8 opisany jest tu samodzielnie, w zakresie potrzebnym do rekomendacji UX. Pełny audyt responsywności zostaje w zakresie B-12.

### 8.1. Co robi rynek

Zbadane na tym samym ekranie renderowanym w 390 px (iPhone 14):

- **Grafana, dashboard** ([`grafana-dashboard-mobile.jpg`](./assets/grafana-dashboard-mobile.jpg), [`grafana-adnotacje-mobile.jpg`](./assets/grafana-adnotacje-mobile.jpg)) — panele układają się w jedną kolumnę, wykres zachowuje czytelność, pasek narzędzi zwija się do ikon, boczna nawigacja chowa się pod hamburgerem. Nic nie znika — zmienia się układ, nie zawartość.
- **Grafana, lista reguł alarmowych** ([`grafana-lista-regul-alarmowych-mobile.jpg`](./assets/grafana-lista-regul-alarmowych-mobile.jpg)) — panel filtrów, który na desktopie jest kolumną po lewej, na telefonie ląduje **nad listą** i zajmuje cały pierwszy ekran. To jest antywzorzec: żeby zobaczyć pierwszy alarm, trzeba przewinąć przez kilkanaście kontrolek filtrowania.
- **PagerDuty** — jedyny z badanych z aplikacją natywną; poza zakresem naszego MVP.

### 8.2. Wnioski dla nas

1. **Filtry na telefonie muszą być zwinięte do jednego przycisku** otwierającego arkusz od dołu — nie rozwinięte nad listą. Nasz `Popover` w [`ObjectsStatusTable.tsx:136-179`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L136-L179) robi to już dobrze i ten wzorzec należy powtórzyć w widoku alarmów.
2. **Tabela z sześcioma kolumnami nie zmieści się na 390 px.** Poniżej `md:` lista alarmów powinna przechodzić na układ kartowy: ważność + obiekt + zdarzenie w pierwszej linii, wartość + czas trwania w drugiej. Nie poziome przewijanie.
3. **`DataTable` nie ma dziś `overflow-x-auto`** ([Z-08](#z-08-datatable-ma-sortowanie-którego-nikt-nie-włącza-i-nie-mówi-o-nim-czytnikom-ekranu)) — do czasu wprowadzenia układu kartowego rozpycha stronę w poziomie, co łamie regułę z [`frontend-architecture.md` §10](../technical/frontend/frontend-architecture.md).
4. **Akcje z §6.4 muszą działać kciukiem** — „Potwierdź” i „Wycisz na 2 h” jako duże przyciski na dole arkusza, nie pozycje w menu kontekstowym.
5. **Wykres na telefonie zostaje.** Grafana pokazuje, że wykres 390 px jest czytelny, jeśli zredukować liczbę serii i etykiet osi. Nasz `ObjectMeasurementsChart` ogranicza już serie do trzech ([`:94`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L94)) — to dobra decyzja, warto ją utrzymać.

---

## 9. Ograniczenia analizy

### 9.1. Czego nie udało się zobaczyć

| Produkt | Powód | Wpływ na wnioski |
|---|---|---|
| **TaKaDu** | brak publicznych zrzutów; serwis blokował automatyczne pobranie strony | Wszystkie stwierdzenia o TaKaDu są **[mkt]** — deklaracjami producenta. Nie opieram na nich żadnej rekomendacji |
| **Ignition Perspective (demo)** | publiczne demo używa WebSocketów, których nie przepuszcza sieć wykorzystana do badania — klient zatrzymuje się na „Connecting” | Ignition oceniony wyłącznie z dokumentacji **[dok]**. Wnioski dotyczą tabeli alarmów, której zrzut jest jednoznaczny; nie oceniam nawigacji ani pracy na telefonie |
| **Hawle.live, HWM, Metasphere, Xylem, Ovarro, Ayyeka** | interfejs wyłącznie za logowaniem, brak publicznych zrzutów | Kolumny „?” w tabeli §2.8. Zgodnie z briefem nie zgaduję |
| **UniCloud WOD-KAN** | serwis niedostępny w dniu badania | Pominięty |
| **Uptime Kuma** | publiczne „demo” to kreator instalacji świeżej instancji | Odrzucony jako źródło |

### 9.2. Ograniczenia metody

- **Nie rejestrowałem się na wersje próbne ani nie zamawiałem dem** — brief tego zabrania. Oznacza to, że produkty, które chronią interfejs logowaniem, są w tej analizie reprezentowane słabiej niż te, które publikują dokumentację. To przesuwa ciężar wniosków w stronę Grafany, Zabbiksa i ThingsBoard — ale akurat te trzy mają najbogatsze wzorce alarmowe, więc przesunięcie działa na korzyść treści.
- **Nie oceniałem estetyki.** Kryterium było skuteczność w realizacji UC-01…UC-05.
- **Zrzuty z dokumentacji pokazują wersje demonstracyjne**, nie wdrożenia produkcyjne. Widoczne w nich dane są przykładowe.

### 9.3. Wniosek uboczny, nie-UX-owy

Z dwunastu badanych produktów **żaden z segmentu wod-kan nie publikuje zrzutów swojego interfejsu**. Ani Hawle.live, ani HWM, ani Metasphere, ani TaKaDu. Robią to natomiast wszystkie badane produkty spoza tego segmentu. Wygląda to na normę branżową, a nie na przypadek.

Dla nas to jest okazja, nie przeszkoda: **publiczne zrzuty interfejsu w materiałach sprzedażowych są w tym segmencie wyróżnikiem**, a nie standardem. Gmina, która porównuje trzy oferty i tylko w jednej widzi, jak wygląda ekran, dostaje argument, którego pozostali jej nie dają. To wykracza poza zakres tego briefu — odnotowuję jako obserwację do rozważenia przy materiałach sprzedażowych, nie jako rekomendację produktową.

### 9.4. Pytania otwarte

Rzeczy, których ta analiza nie rozstrzyga, bo wymagają decyzji produktowej albo danych z pilotażu:

1. **Czy ekran domyślny ma zależeć od roli** (§5.2 pkt 3), czy wszyscy mają startować z tego samego miejsca? Rekomendacja: zależny od roli, ale to zmienia model routingu.
2. **Czy „wyciszenie” w gminie z trzema osobami ma w ogóle sens**, czy wystarczy „potwierdzenie”? Rekomendacja: wyciszenie tak, ale dopiero po pierwszym miesiącu pilotażu, kiedy będzie wiadomo, ile alarmów naprawdę powtarza się w trakcie dojazdu.
3. **Ile poprzednich wystąpień pokazywać** w panelu szczegółów — Zabbix pokazuje 20. Do rozstrzygnięcia na danych z pilotażu.

---

## Załącznik A — biblioteka zrzutów

50 plików w [`docs/analysis/assets/`](./assets/), łącznie ~3,5 MB, każdy ≤ 200 KB, szerokość ≤ 1600 px, format JPEG. Maszynowo czytelny spis ze źródłami: [`assets/index.json`](./assets/index.json).

Wszystkie zrzuty pobrane **2026-09-04**. Kolumna „Cyt.” oznacza, czy zrzut jest cytowany w treści analizy — pozostałe są materiałem do przeglądania, zgodnie z punktem 7 zakresu briefu.

| Plik | Produkt | Co pokazuje | Źródło | Cyt. |
|---|---|---|---|---|
| [`grafana-adnotacje-mobile.jpg`](./assets/grafana-adnotacje-mobile.jpg) | Grafana | Ten sam dashboard na ekranie 390 px | [play.grafana.org/d/000000010/annotations](https://play.grafana.org/d/000000010/annotations?from=now-24h&to=now&timezone=browser) | ✓ |
| [`grafana-adnotacje-na-wykresie.jpg`](./assets/grafana-adnotacje-na-wykresie.jpg) | Grafana | Adnotacje zdarzeń jako pionowe znaczniki na wykresie + lista adnotacji pod spodem | [play.grafana.org/d/000000010/annotations](https://play.grafana.org/d/000000010/annotations?from=now-24h&to=now&timezone=browser) | ✓ |
| [`grafana-akcje-grupy-regul.jpg`](./assets/grafana-akcje-grupy-regul.jpg) | Grafana | Menu akcji grupy reguł: Pause evaluation, Silence notifications | [grafana.com/docs/grafana/latest/alerting/monitor-status…](https://grafana.com/media/docs/alerting/view-alert-rule-list-with-actions2.png?w=750) | — |
| [`grafana-dashboard-mobile.jpg`](./assets/grafana-dashboard-mobile.jpg) | Grafana | Dashboard Grafana Play na ekranie 390 px | [play.grafana.org/d/to6j8mh/grafana-play-home](https://play.grafana.org/d/to6j8mh/grafana-play-home?from=now-6h&to=now&timezone=utc) | ✓ |
| [`grafana-dashboard-z-regulami.jpg`](./assets/grafana-dashboard-z-regulami.jpg) | Grafana | Dashboard z panelem „Alerts linked to this dashboard” — powiązanie wykresu z regułami | [play.grafana.org/d/000000074/alerting](https://play.grafana.org/d/000000074/alerting?from=now-3h&to=now&timezone=browser) | ✓ |
| [`grafana-explore.jpg`](./assets/grafana-explore.jpg) | Grafana | Explore — ad-hoc analiza szeregu czasowego poza dashboardem | [play.grafana.org/explore](https://play.grafana.org/explore?schemaVersion=1&panes=%7B%22l4h%22%3A%7B%22datasource%22%3A%22grafana%22%2C%22queries%22%3A%5B%7B%22queryType%22%3A%22randomWalk%22%2C%22refId%22%3A%22A%22%2C%22datasource%22%3A%7B%22type%22%3A%22datasource%22%2C%22uid%22%3A%22grafana%22%7D%7D%5D%2C%22range%22%3A%7B%22from%22%3A%22now-1h%22%2C%22to%22%3A%22now%22%7D%2C%22compact%22%3Afalse%7D%7D) | — |
| [`grafana-historia-alarmow.jpg`](./assets/grafana-historia-alarmow.jpg) | Grafana | Historia alarmów: histogram zdarzeń w czasie + tabela z przejściami stanów | [play.grafana.org/alerting/history](https://play.grafana.org/alerting/history) | ✓ |
| [`grafana-katalog-dashboardow.jpg`](./assets/grafana-katalog-dashboardow.jpg) | Grafana | Katalog dashboardów: foldery, tagi, filtr po właścicielu | [play.grafana.org/dashboards](https://play.grafana.org/dashboards) | — |
| [`grafana-lista-regul-alarmowych.jpg`](./assets/grafana-lista-regul-alarmowych.jpg) | Grafana | Lista reguł alarmowych: filtr stanu (Firing/Normal/Pending/Recovering), grupowanie po folderach, zapisane wyszukiwania | [play.grafana.org/alerting/list](https://play.grafana.org/alerting/list) | ✓ |
| [`grafana-lista-regul-alarmowych-mobile.jpg`](./assets/grafana-lista-regul-alarmowych-mobile.jpg) | Grafana | Ta sama lista reguł na ekranie 390 px | [play.grafana.org/alerting/list](https://play.grafana.org/alerting/list) | ✓ |
| [`grafana-panel-listy-alarmow.jpg`](./assets/grafana-panel-listy-alarmow.jpg) | Grafana | Panel „Alert list” — czas trwania stanu Firing jako pole pierwszej klasy | [play.grafana.org/d/bdodlcyou483ke/alert-list](https://play.grafana.org/d/bdodlcyou483ke/alert-list?from=now-6h&to=now&timezone=browser) | ✓ |
| [`grafana-polityki-powiadomien.jpg`](./assets/grafana-polityki-powiadomien.jpg) | Grafana | Drzewo polityk powiadomień z czytelnym opisem grupowania i powtarzania | [play.grafana.org/alerting/routes](https://play.grafana.org/alerting/routes) | ✓ |
| [`grafana-progi-na-wykresie.jpg`](./assets/grafana-progi-na-wykresie.jpg) | Grafana | Progi naniesione na wizualizację jako obszary tła | [grafana.com/docs/grafana/latest/panels-visualizations/c…](https://grafana.com/media/docs/grafana/panels-visualizations/screenshot-thresholds-state-timeline-v10.4.png) | ✓ |
| [`grafana-punkty-kontaktowe.jpg`](./assets/grafana-punkty-kontaktowe.jpg) | Grafana | Punkty kontaktowe z historią i statusem dostarczenia powiadomień | [play.grafana.org/alerting/notifications](https://play.grafana.org/alerting/notifications?search=) | ✓ |
| [`grafana-schemat-routingu.jpg`](./assets/grafana-schemat-routingu.jpg) | Grafana | Schemat routingu: instancje alarmu → polityki → punkty kontaktowe | [grafana.com/docs/grafana/latest/alerting/configure-noti…](https://grafana.com/media/docs/alerting/get-started-notification-policy-tree-combo.png?w=750) | ✓ |
| [`grafana-state-timeline.jpg`](./assets/grafana-state-timeline.jpg) | Grafana | State timeline — pasma stanu w czasie z czasem trwania w tooltipie | [grafana.com/docs/grafana/latest/panels-visualizations/v…](https://grafana.com/media/docs/grafana/panels-visualizations/screenshot-state-timeline-v11.4.png) | ✓ |
| [`grafana-wyciszenia.jpg`](./assets/grafana-wyciszenia.jpg) | Grafana | Ekran wyciszeń (Silences) z pustym stanem i CTA „Create silence” | [play.grafana.org/alerting/silences](https://play.grafana.org/alerting/silences) | ✓ |
| [`hawle-live-logowanie.jpg`](./assets/hawle-live-logowanie.jpg) | Hawle.live | Aplikacja dostępna wyłącznie po zalogowaniu — brak publicznego demo | [app.hawle.live/login](https://app.hawle.live/login) | ✓ |
| [`ignition-tabela-alarmow.jpg`](./assets/ignition-tabela-alarmow.jpg) | Ignition Perspective | Alarm Status Table: pełne wypełnienie wiersza kolorem, kolumna Current State łącząca stan warunku i potwierdzenia, przyciski Acknowledge / Shelve | [docs.inductiveautomation.com/docs/8.1/platform/alarming](https://docs.inductiveautomation.com/assets/images/img2-4365a609946ac4dd24be2c18bafae754.png) | ✓ |
| [`dataportal-edytor.jpg`](./assets/dataportal-edytor.jpg) | Inventia DataPortal | Edytor ekranów DataPortal — drzewo projektu i paleta elementów | [dataportal.pl/en/data-visualization-at-your-fingertips/](https://dataportal.pl/wp-content/uploads/elementor/thumbs/dataportal-computer-designer-ptyszcr0l73oz2t91zr7hhghldzx80nsh29hlbrl5m.png) | ✓ |
| [`dataportal-lista-projektow.jpg`](./assets/dataportal-lista-projektow.jpg) | Inventia DataPortal | Tabela projektów/kont w panelu administracyjnym | [dataportal.pl/en/data-visualization-at-your-fingertips/](https://dataportal.pl/wp-content/uploads/elementor/thumbs/dataportal-computer-manage-projects-ptyszbt6ed2engum7hckwzp1004k0bk24xm041szbu.png) | — |
| [`dataportal-synoptyka-laptop.jpg`](./assets/dataportal-synoptyka-laptop.jpg) | Inventia DataPortal | Ten sam ekran synoptyczny w materiale produktowym | [dataportal.pl/en/data-visualization-at-your-fingertips/](https://dataportal.pl/wp-content/uploads/2022/08/dataportal-computer-run.png) | ✓ |
| [`inventia-synoptyka.jpg`](./assets/inventia-synoptyka.jpg) | Inventia DataPortal | Ekran synoptyczny „Sample system” — wartości bez czasu pomiaru i bez statusu jakości | [www.inventia.pl/dataportal-jak-wizualizacja-danych-moze…](https://www.inventia.pl/wp-content/uploads/2025/03/Demo-zrzut-w%C4%99%C5%BCszy.png) | ✓ |
| [`inventia-zestawienie-alarmow.jpg`](./assets/inventia-zestawienie-alarmow.jpg) | Inventia DataPortal | „Zestawienie alarmów” jako mapa z pinami; status w postaci surowego kodu (AWARIA_P3, POSTÓJ) | [www.inventia.pl/dataportal-jak-wizualizacja-danych-moze…](https://www.inventia.pl/wp-content/uploads/2025/03/mapa-zestawienie-alarm%C3%B3w-2000x1126.png) | ✓ |
| [`pagerduty-filtr-osi-czasu.jpg`](./assets/pagerduty-filtr-osi-czasu.jpg) | PagerDuty | Filtr osi czasu po typie aktywności | [support.pagerduty.com/main/docs/incidents](https://files.readme.io/cee3ee8c91a7d6d40d4851ce6dd547a3d61f67233f443c05af1539db2b392042-filter_timeline.webp) | — |
| [`pagerduty-os-czasu-incydentu.jpg`](./assets/pagerduty-os-czasu-incydentu.jpg) | PagerDuty | Oś czasu incydentu: przypisania, ponowne otwarcie, pola własne (resolution_category) | [support.pagerduty.com/main/docs/incidents](https://files.readme.io/b6c3efde615e6dd6b40025115381c18338abe7a20e1790d8a2ffdc83e3455223-timeline.webp) | ✓ |
| [`thingsboard-dashboard-narzedzia.jpg`](./assets/thingsboard-dashboard-narzedzia.jpg) | ThingsBoard | Opisany pasek narzędzi dashboardu (stany, układy, filtry, wersjonowanie) | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-toolbar-edit-mode-ce.DFvzxTiz_nkHWc.webp) | — |
| [`thingsboard-dashboard-pusty.jpg`](./assets/thingsboard-dashboard-pusty.jpg) | ThingsBoard | Pusty dashboard i pasek narzędzi edycji | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-toolbar-view-mode-ce.CiNEFCy0_1PYOO7.webp) | — |
| [`thingsboard-filtry-1.jpg`](./assets/thingsboard-filtry-1.jpg) | ThingsBoard | Wejście do konfiguracji filtrów dashboardu | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-1-ce.DDgFb7jn_Z1sIx0m.webp) | — |
| [`thingsboard-filtry-2.jpg`](./assets/thingsboard-filtry-2.jpg) | ThingsBoard | Definicja filtru — nazwa i przełącznik edytowalności przez klienta | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-2-ce.BGQ9aFnd_2oEudc.webp) | — |
| [`thingsboard-filtry-3.jpg`](./assets/thingsboard-filtry-3.jpg) | ThingsBoard | Kreator warunku filtru: klucz, typ, operator, wartość — bez pisania wyrażeń | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-3-ce.B_kc_NLd_19XQ01.webp) | ✓ |
| [`thingsboard-filtry-4.jpg`](./assets/thingsboard-filtry-4.jpg) | ThingsBoard | Warunek na danych szeregu czasowego („batteryLevel less than 20”) | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-5-ce.CUdLky8U_1W7NrX.webp) | ✓ |
| [`thingsboard-filtry-lista.jpg`](./assets/thingsboard-filtry-lista.jpg) | ThingsBoard | Lista zapisanych filtrów dashboardu | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-7-ce.CiUbV6AX_1cm58o.webp) | — |
| [`thingsboard-filtry-podglad.jpg`](./assets/thingsboard-filtry-podglad.jpg) | ThingsBoard | Podgląd złożonego filtru w formie czytelnego zdania | [thingsboard.io/docs/user-guide/ui/dashboards/](https://thingsboard.io/_astro/dashboard-filters-6-ce.CAcV6YGs_Z2vdJCa.webp) | ✓ |
| [`thingsboard-szczegoly-alarmu.jpg`](./assets/thingsboard-szczegoly-alarmu.jpg) | ThingsBoard | Szczegóły alarmu z opisem pól: severity, czas trwania, status, przypisanie do osoby, komentarze | [thingsboard.io/docs/user-guide/alarms/](https://thingsboard.io/_astro/find-alarms-2-ce.BO6r2p5W_Z2cDqfU.webp) | ✓ |
| [`zabbix-aktualizacja-problemu.jpg`](./assets/zabbix-aktualizacja-problemu.jpg) | Zabbix | Dialog „Update problem”: komentarz, historia reakcji, zmiana priorytetu, wyciszenie do czasu, potwierdzenie, zamknięcie | [www.zabbix.com/documentation/current/en/manual/acknowle…](https://www.zabbix.com/documentation/current/assets/en/manual/acknowledges/update_problem.png) | ✓ |
| [`zabbix-dashboard.jpg`](./assets/zabbix-dashboard.jpg) | Zabbix | Dashboard: kafle „Problems by severity” i „Host availability” nad tabelą bieżących problemów | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/dashboards/dashboard.png) | ✓ |
| [`zabbix-filtr-problemow.jpg`](./assets/zabbix-filtr-problemow.jpg) | Zabbix | Filtr widoku Problems: severity, wiek, status potwierdzenia, wyciszone, tagi, zapisane filtry | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/problem_filter.png) | ✓ |
| [`zabbix-harmonogram-serwisowy.jpg`](./assets/zabbix-harmonogram-serwisowy.jpg) | Zabbix | Harmonogram okna serwisowego — kreator bez pisania wyrażeń | [www.zabbix.com/documentation/current/en/manual/maintenance](https://www.zabbix.com/documentation/current/assets/en/manual/maintenance/maintenance_period.png) | ✓ |
| [`zabbix-konfiguracja-problem-hosts.jpg`](./assets/zabbix-konfiguracja-problem-hosts.jpg) | Zabbix | Konfiguracja widgetu Problem hosts: „Hide groups without problems”, „Unacknowledged only” | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/problem_hosts.png) | — |
| [`zabbix-konfiguracja-top-hosts.jpg`](./assets/zabbix-konfiguracja-top-hosts.jpg) | Zabbix | Konfiguracja widgetu Top hosts — kolumny definiowane przez użytkownika | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/top_hosts.1.png) | — |
| [`zabbix-konfiguracja-widgetu-wartosci.jpg`](./assets/zabbix-konfiguracja-widgetu-wartosci.jpg) | Zabbix | Konfiguracja widgetu Item value — czas i wskaźnik zmiany jako osobne przełączniki | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/dashboards/widget_edit.png) | ✓ |
| [`zabbix-latest-data.jpg`](./assets/zabbix-latest-data.jpg) | Zabbix | Latest data: wartość zawsze obok „Last check” i zmiany względem poprzedniego odczytu | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/latest_data.png) | ✓ |
| [`zabbix-latest-data-subfiltr.jpg`](./assets/zabbix-latest-data-subfiltr.jpg) | Zabbix | Podfiltr Latest data: przełącznik „With data / Without data” i stan pozycji | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/latest_data_subfilter.png) | — |
| [`zabbix-okno-serwisowe.jpg`](./assets/zabbix-okno-serwisowe.jpg) | Zabbix | Okno serwisowe: zakres obiektów, harmonogram, opis — planowane tłumienie alarmów | [www.zabbix.com/documentation/current/en/manual/maintenance](https://www.zabbix.com/documentation/current/assets/en/manual/maintenance/maintenance.png) | ✓ |
| [`zabbix-szczegoly-zdarzenia.jpg`](./assets/zabbix-szczegoly-zdarzenia.jpg) | Zabbix | Szczegóły zdarzenia: warunek, dane operacyjne, log powiadomień ze statusem, lista 20 poprzednich wystąpień | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/event_details.png) | ✓ |
| [`zabbix-wartosci-tekstowe.jpg`](./assets/zabbix-wartosci-tekstowe.jpg) | Zabbix | Widok wartości jako czysty tekst — timestamp + wartość, bez wykresu | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/latest_values.png) | — |
| [`zabbix-widget-problem-hosts.jpg`](./assets/zabbix-widget-problem-hosts.jpg) | Zabbix | Widget „Problem hosts” — macierz grup obiektów × severity | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/problem_hosts_overview_hover.png) | ✓ |
| [`zabbix-widget-top-hosts.jpg`](./assets/zabbix-widget-top-hosts.jpg) | Zabbix | Widget „Top hosts” — tabela z paskami i sparkline’ami w komórkach | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/frontend_sections/monitoring/top_hosts.png) | ✓ |
| [`zabbix-wykresy.jpg`](./assets/zabbix-wykresy.jpg) | Zabbix | Wykresy z legendą zawierającą last/min/avg/max dla każdej serii | [www.zabbix.com/documentation/current/en/manual/web_inte…](https://www.zabbix.com/documentation/current/assets/en/manual/web_interface/graphs.png) | — |

**Cytowane w treści: 35 z 50.** Pozostałe 15 to materiał do przeglądania — ekrany, które nie trafiają w żaden konkretny wzorzec z katalogu, ale pokazują ciekawe rozwiązania (konfiguracja widgetów, kreatory filtrów, warianty układu).


---

## Historia dokumentu

| Data | Zmiana |
|---|---|
| 2026-09-04 | Wersja 1. Zastępuje usunięty wcześniej dokument o tej samej nazwie (commit `676c7a9`), który opierał się na czterech produktach bez linków do źródeł i dat, i którego biblioteka zrzutów została skasowana jako nieaktualna. |
