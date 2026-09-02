# Analiza UX/UI konkurencji i wzorce dla interfejsu (B-03)

> **Artifact z rekomendacjami:** [Benchmark UX wodociągów — dziesięć zmian, które rynek już rozstrzygnął](https://claude.ai/code/artifact/666711ee-d6ae-4ca1-89db-8d9d0e4149c3)
> Wizualny, samodzielny skrót do przejrzenia w pięć minut: dziesięć rekomendacji o najwyższym stosunku wartości do kosztu, każda ze schematem „dziś / propozycja” i odwołaniem do pliku. Nie powtarza tego dokumentu — jest jego towarzyszem.
>
> **Data wykonania analizy:** 2026-09-02. Wszystkie odwołania do interfejsów konkurencji odnoszą się do stanu dokumentacji publicznej z tego dnia.
> **Zakres:** wyłącznie warstwa *jak to wygląda i jak się tego używa*. Warstwa techniczna (firmware, sprzęt, backend) to osobne zlecenie B-02.

---

## Spis treści

- [0. Jak czytać ten dokument](#0-jak-czytać-ten-dokument)
  - [0.1. Metoda i jej twarde ograniczenia](#01-metoda-i-jej-twarde-ograniczenia)
  - [0.2. Status deliverables](#02-status-deliverables)
  - [0.3. Streszczenie — 10 rzeczy do zrobienia](#03-streszczenie--10-rzeczy-do-zrobienia)
- [1. Kogo badano i dlaczego](#1-kogo-badano-i-dlaczego)
- [2. Analiza według dziewięciu wymiarów](#2-analiza-według-dziewięciu-wymiarów)
- [3. Katalog wzorców z werdyktem](#3-katalog-wzorców-z-werdyktem)
- [4. Konfrontacja z naszym interfejsem](#4-konfrontacja-z-naszym-interfejsem)
- [5. Rekomendacja architektury informacji](#5-rekomendacja-architektury-informacji)
- [6. Projekt widoku alarmów](#6-projekt-widoku-alarmów)
- [7. Backlog zmian we froncie](#7-backlog-zmian-we-froncie)
- [8. Korekty do istniejących dokumentów](#8-korekty-do-istniejących-dokumentów)
- [9. Źródła](#9-źródła)

---

## 0. Jak czytać ten dokument

### 0.1. Metoda i jej twarde ograniczenia

**Co udało się zrobić:** przegląd dokumentacji produktowej, instrukcji użytkownika i materiałów producentów czternastu platform z trzech kategorii, zestawiony z lekturą całego kodu frontendu w `frontend/src/` i wymagań produktowych z [`01_plan_biznesowy.md`](../business/01_plan_biznesowy.md) §2.3, §2.4.3, §2.7, §2.8.

**Czego nie udało się zrobić i dlaczego — przeczytaj przed oceną kompletności:**

Sesja, w której powstała ta analiza, ma politykę egress ograniczoną do hostów GitHuba. Każde bezpośrednie pobranie strony konkurenta kończy się odmową bramy (`403 CONNECT`), zweryfikowane na `grafana.com`, `kallipr.com`, `en.wikipedia.org`, `zabbix.com`, `developer.mozilla.org`. Wynikają z tego trzy konsekwencje, których nie da się obejść bez zmiany środowiska:

| Element briefu | Status | Powód |
|---|---|---|
| Katalog wzorców, konfrontacja z kodem, architektura informacji, projekt widoku alarmów, backlog | **Wykonane w całości** | Oparte na dokumentacji produktowej dostępnej przez wyszukiwarkę + na kodzie repozytorium |
| Biblioteka 30–60 zrzutów ekranu w `assets/` | **Niewykonane** | Przeglądarka w tej sesji nie ma dostępu do sieci poza GitHubem; nie da się wejść na żaden ekran konkurenta |
| Zrzuty konkurencji osadzone w Artifaccie | **Zastąpione** | W miejsce zrzutów Artifact zawiera **schematy wzorców** rysowane w SVG, jawnie oznaczone jako rekonstrukcje, nie fotografie ekranów |

Zamiast pustego katalogu `assets/` zostawiam w nim **wykonawczy plan uzupełnienia**: [`assets/README.md`](assets/README.md) z listą 48 konkretnych zrzutów do zrobienia (adres + co ma być na ekranie + do którego wzorca się odnosi) oraz skrypt [`assets/capture_screenshots.mjs`](assets/capture_screenshots.mjs), który na maszynie z normalnym dostępem do sieci robi i kompresuje komplet w jednym uruchomieniu. To jest praca na kilkanaście minut po stronie z dostępem do internetu — ale nie da się jej wykonać stąd, więc nie udaję, że została wykonana.

**Wiarygodność ustaleń.** Każde twierdzenie o cudzym interfejsie ma w [§9](#9-źródła) odnośnik do źródła i etykietę:

- `[dok]` — dokumentacja produktu lub instrukcja użytkownika (najwyższa wiarygodność),
- `[std]` — norma lub wytyczna branżowa (ISA, EEMUA, WCAG),
- `[art]` — opracowanie trzeciej strony,
- `[mkt]` — materiał marketingowy producenta (najniższa wiarygodność; traktuj jako deklarację, nie jako opis działania).

**Dodatkowe zastrzeżenie, którego brief nie przewidywał, a które jest istotne:** ponieważ nie mogłem otworzyć żadnego ekranu, wszystkie ustalenia o konkurencji opisują **to, co producent deklaruje w dokumentacji**, a nie to, co widać po zalogowaniu. Rozróżnienie „materiał marketingowy vs. realne demo”, którego wymaga brief, jest więc zrealizowane tylko połowicznie: umiem odróżnić dokumentację od marketingu, ale żadnego ustalenia nie potwierdziłem realnym demo. Wszystkie wnioski dla naszego kodu w [§4](#4-konfrontacja-z-naszym-interfejsem) opierają się natomiast na **bezpośredniej lekturze naszych plików** i są w pełni weryfikowalne.

### 0.2. Status deliverables

| Deliverable z briefu | Gdzie |
|---|---|
| 1. Katalog wzorców z werdyktem bierz/nie bierz/rozważ | [§3](#3-katalog-wzorców-z-werdyktem) |
| 2. Konfrontacja z obecnym interfejsem (plik po pliku) | [§4](#4-konfrontacja-z-naszym-interfejsem) |
| 3. Rekomendacja architektury informacji dla trzech ról | [§5](#5-rekomendacja-architektury-informacji) |
| 4. Projekt widoku alarmów | [§6](#6-projekt-widoku-alarmów) |
| 5. Backlog zmian wg wartości do kosztu | [§7](#7-backlog-zmian-we-froncie) |
| 6. Artifact z rekomendacjami | link na górze dokumentu |
| 7. Biblioteka zrzutów | **zablokowana** — plan wykonania w [`assets/README.md`](assets/README.md) |

Wszystko, czego nie dało się zrobić z tej sesji, jest rozpisane na konkretne kroki w [`02_handoff_b03_uzupelnienie.md`](02_handoff_b03_uzupelnienie.md) — łącznie z tym, które tezy tej analizy są falsyfikowalne i co je obali.

### 0.3. Streszczenie — 10 rzeczy do zrobienia

Kolejność według stosunku wartości do kosztu, pełne uzasadnienie w [§7](#7-backlog-zmian-we-froncie).

| # | Zmiana | Plik | Koszt |
|---|---|---|---|
| 1 | Lista obiektów przestaje być martwa — dodać `refetchInterval` jak w widoku szczegółu | [`useTelemetryApi.ts:6`](../../frontend/src/hooks/useTelemetryApi.ts#L6) | XS |
| 2 | Sortowanie domyślne „najpierw to, co wymaga uwagi” zamiast alfabetycznego | [`ObjectsGrid.tsx`](../../frontend/src/components/objects/ObjectsGrid.tsx), [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx) | S |
| 3 | Wartości na liście obiektów bez jakości i czasu pomiaru — naruszenie niezmiennika §2.4.3 | [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx), [`ObjectCard.tsx`](../../frontend/src/components/objects/ObjectCard.tsx) | S |
| 4 | Nakładka jakości na wartości — wzorzec „quality overlay” z Ignition | [`CurrentValueCard.tsx`](../../frontend/src/components/objects/CurrentValueCard.tsx) | S |
| 5 | Kolor przestaje być jedynym nośnikiem statusu — ikona kształtu w `StatusPill` | [`StatusPill.tsx`](../../frontend/src/components/ui/StatusPill.tsx) | S |
| 6 | Naprawić semantykę koloru: „brak komunikacji” jest dziś szary, nie czerwony | [`tokens.css`](../../frontend/src/styles/tokens.css), [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) | S |
| 7 | Wykres pokazuje przerwę w komunikacji jako przerwę, nie jako linię prostą | [`ObjectMeasurementsChart.tsx`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx) | M |
| 8 | Widok alarmów — nowy ekran wg projektu z §6 | nowy `pages/AlarmsPage.tsx` | L |
| 9 | Czas bezwzględny obok względnego wszędzie tam, gdzie dziś jest tylko „2 h temu” | [`freshnessUtils.ts`](../../frontend/src/components/ui/freshnessUtils.ts) i konsumenci | XS |
| 10 | Tabela dostępna z klawiatury i przewijalna w poziomie na telefonie | [`DataTable.tsx`](../../frontend/src/components/ui/DataTable.tsx) | S |

---

## 1. Kogo badano i dlaczego

Brief wymaga minimum ośmiu produktów z trzech kategorii, z czego co najmniej cztery pogłębione. Zbadano czternaście — sześć w kategorii wod-kan, trzy w przemysłowym monitoringu aktywów, pięć w obserwowalności IT; pięć z nich pogłębionych. Kryterium doboru było **podobieństwo problemu**, nie wielkość marki — dla każdego wpisu poniżej podane jest, jaki nasz problem ten produkt rozwiązał wcześniej.

### 1.1. Kategoria A — wod-kan i smart water

| Produkt | Kraj | Dlaczego w zestawie | Głębokość |
|---|---|---|---|
| **Inventia DataPortal / MTPortal** | PL | Konkurent bezpośredni z [§5.2.2 planu](../business/01_plan_biznesowy.md); ten sam klient (gmina), ta sama skala (kilkanaście przepompowni) | przeglądowa |
| **AquaRD (CellBOX + HydraNet Expert)** | PL | Konkurent bezpośredni; jedyny w zestawie z jawnym rozdziałem „SCADA” od „platformy analitycznej” — to samo rozdzielenie rozważamy | przeglądowa |
| **Hawle.live (APP / BOX / CAP)** | AT/PL | Reprezentuje wzorzec „mapa jest interfejsem podstawowym”, czyli dokładnie tę decyzję, którą [§2.8.1](../business/01_plan_biznesowy.md) u nas odrzuca | przeglądowa |
| **Kallipr Kloud (+ Kloud Fleet)** | AU | Wzorzec produktowy wskazany w [§5.2.5 planu](../business/01_plan_biznesowy.md); rozdziela widok danych od widoku floty urządzeń — mamy dokładnie ten sam podział na płaszczyznę gminy i platformy | **pogłębiona** |
| **HWM DataGate / HWM Online** | UK | Dojrzały portal rejestratorów sieciowych z publicznymi instrukcjami użytkownika; najbliższy funkcjonalnie temu, co budujemy | przeglądowa |
| **Ayyeka Field Asset Intelligence** | IL/US | Jedyny w kategorii z publiczną bazą wiedzy opisującą **widżety dashboardu** i **kondycję urządzeń** jako osobny obiekt zainteresowania | **pogłębiona** |

**Obserwacja o samej kategorii, istotna dla naszego pozycjonowania:** polscy konkurenci nie publikują dokumentacji interfejsu. Nie ma instrukcji użytkownika online, nie ma opisu ekranów, nie ma publicznego dema — jest materiał sprzedażowy z pojedynczymi zrzutami. Kontrast z HWM i Ayyeką, które publikują pełne manuale i bazy wiedzy, jest jaskrawy. To znaczy, że **dostępna, czytelna dokumentacja użytkownika jest w polskim wod-kanie realną, tanią różnicą konkurencyjną** — nie funkcją do odłożenia na później.

### 1.2. Kategoria B — przemysłowy monitoring aktywów i SCADA w chmurze

| Produkt | Dlaczego w zestawie | Głębokość |
|---|---|---|
| **Ignition Perspective** (Inductive Automation) | Rozwiązał problem „setki punktów, który wymaga uwagi” w wersji mobile-first; do tego ma **jawny model jakości danych z nakładkami graficznymi** — bezpośredni odpowiednik naszego niezmiennika z §2.4.3 | **pogłębiona** |
| **AVEVA Insight** | Chmurowy monitoring aktywów z aplikacją mobilną i alertami — ten sam kształt produktu, inna skala klienta | przeglądowa |
| **ThingsBoard (CE/PE)** | Otwarta platforma IoT z najlepiej udokumentowanym publicznie **widżetem tabeli alarmów** i przepływem potwierdzania; nasz widok alarmów nie istnieje, więc to jest wzorzec referencyjny | **pogłębiona** |

### 1.3. Kategoria C — monitoring i obserwowalność IT

Brief słusznie zauważa, że ta kategoria jest zwykle pomijana, a ma najwięcej do zaoferowania w warstwie alarmowej. Potwierdzam — **większość rekomendacji dla widoku alarmów w [§6](#6-projekt-widoku-alarmów) pochodzi właśnie stąd.**

| Produkt | Dlaczego w zestawie | Głębokość |
|---|---|---|
| **Grafana Alerting** | Najlepiej opisany publicznie model „alarm → dlaczego się odpalił → co z tym zrobić”, plus jawna obsługa stanów `No Data` i `Error` jako osobnych bytów — u nas to jest `no_data` i `communication_error` | **pogłębiona** |
| **Zabbix (Monitoring → Problems)** | Klasyczna lista problemów operatorskich: masowa aktualizacja, komentarze, zmiana priorytetu, wygaszanie. Bliski mentalnie służbom technicznym, nie devopsom | **pogłębiona** |
| **Prometheus Alertmanager** | Czysty model grupowania, wyciszania i **inhibicji** (tłumienia skutków przez przyczynę) — dokładnie to, czego potrzebujemy przy zaniku zasilania na obiekcie | przeglądowa |
| **Datadog Monitors** | Wzorzec „wycisz konkretny zakres, nie cały alarm” oraz ostrzeżenie o skutkach ubocznych wyciszania | przeglądowa |
| **PagerDuty** | Wzorzec mobilny: co zostaje na ekranie telefonu, gdy ktoś ma zdecydować „jadę / nie jadę” | przeglądowa |

Odrzucone świadomie: narzędzia BI (Power BI, Tableau) — inny problem, prezentacja analityczna zamiast operacyjnej; oraz platformy device-managementowe bez warstwy prezentacji danych końcowemu użytkownikowi (Balena, Golioth) — należą do zakresu B-02, nie tutaj.

---

## 2. Analiza według dziewięciu wymiarów

### 2.0. Macierz porównawcza — produkt × wymiar

Brief wymaga tych samych wymiarów dla każdego produktu, „żeby dało się porównać”. Macierz mówi, **na jakim materiale opiera się każda komórka** — a nie jak dobrze produkt sobie radzi, bo oceny jakości bez dostępu do ekranu nie da się postawić uczciwie.

- ● — opisane w dokumentacji produktu lub instrukcji użytkownika
- ◐ — deklarowane w materiale producenta (marketing), bez opisu działania
- ○ — brak informacji publicznej
- — — wymiar nie dotyczy tego produktu

| Produkt | 1 ekran startowy | 2 nawigacja | 3 pomiar+jakość | 4 status/kolor | 5 alarmy/triage | 6 wykresy | 7 progi | 8 telefon | 9 onboarding |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Inventia DataPortal | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ | ○ |
| AquaRD / HydraNet | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ | ○ |
| Hawle.live | ◐ | ○ | ○ | ◐ | ◐ | ○ | ○ | ◐ | ○ |
| Kallipr Kloud | ◐ | ◐ | ◐ | ○ | ◐ | ◐ | ◐ | ○ | ◐ |
| HWM DataGate | ◐ | ○ | ○ | ○ | ◐ | ◐ | ◐ | ◐ | ○ |
| Ayyeka FAI | ● | ◐ | ○ | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| Ignition Perspective | ○ | ● | ● | ● | ○ | ○ | ○ | ● | — |
| AVEVA Insight | ◐ | ◐ | ○ | ○ | ◐ | ◐ | ○ | ◐ | ○ |
| ThingsBoard | ◐ | ● | ○ | ○ | ● | ○ | ● | ◐ | ● |
| Grafana Alerting | ○ | ● | ● | ○ | ● | ● | ● | ○ | — |
| Zabbix | ● | ○ | ○ | ● | ● | ○ | ○ | ○ | — |
| Alertmanager | — | — | — | — | ● | — | ◐ | — | — |
| Datadog Monitors | ○ | ● | ○ | ○ | ● | ○ | ○ | ○ | — |
| PagerDuty | ● | ○ | — | ○ | ● | — | — | ● | — |

**Trzy rzeczy widać dopiero w tej postaci, a nie w prozie poniżej:**

1. **Kolumna 3 (pomiar razem z czasem i jakością) jest niemal pusta w całej kategorii wod-kan.** Ani jeden z sześciu badanych produktów wodociągowych nie opisuje publicznie, jak pokazuje jakość danych przy wartości. Jedyne udokumentowane rozwiązania tego problemu pochodzą z automatyki przemysłowej (Ignition) i z obserwowalności IT (Grafana). Nasz niezmiennik z §2.4.3 jest więc wymaganiem **ponad** poziomem rynku wod-kan — a nie doganianiem go.
2. **Wiersze wod-kan są zdominowane przez ◐ i ○, wiersze IT przez ●.** To nie jest przypadek doboru źródeł, tylko różnica kultury: platformy IT publikują instrukcje, polskie platformy wod-kan publikują foldery sprzedażowe. Wniosek dla nas jest w [§1.1](#11-kategoria-a--wod-kan-i-smart-water): czytelna dokumentacja użytkownika jest w tym segmencie tanią różnicą konkurencyjną.
3. **Wymiar 5 jest jedynym, w którym mam materiał ● od czterech niezależnych produktów.** To jest dokładnie ten wymiar, w którym my nie mamy nic — i to uzasadnia, dlaczego projekt widoku alarmów w [§6](#6-projekt-widoku-alarmów) jest najbardziej szczegółową częścią tego dokumentu.

> **Jak czytać ○.** Znak „brak informacji publicznej” nie znaczy „produkt tego nie ma”. Znaczy, że nie dało się tego ustalić bez dostępu do ekranu — a dostępu, z przyczyn opisanych w [§0.1](#01-metoda-i-jej-twarde-ograniczenia), nie było. Uzupełnienie tych komórek jest pierwszym zadaniem opisanym w [`02_handoff_b03_uzupelnienie.md`](02_handoff_b03_uzupelnienie.md).

### 2.1. Wymiar 1 — ekran startowy

**Co robi rynek.** Rysują się trzy szkoły:

1. **Lista/tabela priorytetowa.** Zabbix ma osobny widok operacyjny `Monitoring → Problems`, który wylicza wyłącznie wyzwalacze będące w stanie problemowym, a nie wszystko, co jest monitorowane `[dok]`; ten sam wykaz jest dostępny jako widżet dashboardu `[dok]`. To jest wybór „pokaż wyjątki, nie inwentarz”. *(Czego nie ustaliłem: który ekran Zabbix pokazuje bezpośrednio po zalogowaniu — bez dostępu do instancji nie da się tego potwierdzić, a dokumentacja tego nie rozstrzyga. Wzorzec dotyczy istnienia widoku wyjątków, nie tego, czy jest ekranem domyślnym.)*
2. **Mapa jako ekran główny.** Hawle.live buduje interfejs wokół interaktywnej mapy z lokalizacją i statusem hydrantów, zasuw i innych elementów sieci `[mkt]`. HWM DataGate również stawia mapę sieci obok dashboardów i alarmów `[mkt]`.
3. **Konfigurowalne kafelki.** Ayyeka pozwala kolorować całe regiony mapy według **średniej kondycji urządzeń** albo dowolnego strumienia danych, z rozwinięciem do wykazu per urządzenie `[dok]`. AVEVA Insight opiera się na samoobsługowych dashboardach `[mkt]`.

**Co z tego wynika dla nas.** Plan ([§2.8.1](../business/01_plan_biznesowy.md)) już rozstrzygnął, że mapa jest dodatkiem, a nie zamiennikiem czytelnej listy operacyjnej — i rynek tego nie podważa: nawet produkty mapocentryczne trzymają obok listę i dashboard. Rozstrzygnięta jest natomiast inna rzecz, której plan nie dopowiada: **ekran startowy ma pokazywać wyjątki, nie inwentarz.** Zabbix trzyma wykaz problemów jako osobny, pierwszorzędny widok, oddzielony od inwentarza hostów. My otwieramy się na liście wszystkich obiektów wodociągowych, posortowanej alfabetycznie ([`ObjectsPage.tsx:153`](../../frontend/src/pages/ObjectsPage.tsx#L153) → [`ObjectsGrid`](../../frontend/src/components/objects/ObjectsGrid.tsx)), co przy piętnastu obiektach jeszcze działa, ale nie odpowiada na pytanie „który wymaga uwagi”, tylko „jakie mam obiekty”.

Ważny szczegół z Ayyeki: **kondycja urządzenia jest osobnym, pierwszorzędnym strumieniem danych**, po którym można pokolorować widok, a nie przypisem przy pomiarze `[dok]`. To dokładnie pokrywa nasz `UC-04` (utrata komunikacji) i uzasadnia rozdzielenie „awarii obiektu” od „awarii telemetrii” w warstwie wizualnej.

### 2.2. Wymiar 2 — hierarchia nawigacji

**Co robi rynek.** Grafana przeniosła przestrzeń nazw i grupę reguły do **okruszków nawigacyjnych (breadcrumb)** i uczyniła je klikalnym filtrem — z okruszka wchodzi się w listę przefiltrowaną do tego poziomu `[art]`. ThingsBoard trzyma płaską hierarchię encji (klient → urządzenie → alarm), a zagnieżdżenie odwzorowuje relacjami i widżetami na dashboardzie `[dok]`. Ignition Perspective zaleca budowę widoków przez wiązania pośrednie i szablony wielokrotnego użytku, czyli jeden widok obiektu parametryzowany identyfikatorem, a nie ekran per obiekt `[art]`.

**Co z tego wynika dla nas.** Nasza hierarchia z [`CONTEXT.md`](../business/CONTEXT.md) to organizacja → obiekt wodociągowy → gateway → punkt pomiarowy. Dziś użytkownik gminy widzi w nawigacji dwie pozycje: „Obiekty” i „Urządzenia” ([`OrgSidebar.tsx:29-44`](../../frontend/src/components/layout/OrgSidebar.tsx#L29-L44)), a ścieżka do wartości pomiaru to: lista obiektów → karta obiektu → zakładka „Aktualne wartości”. To **dwa kliknięcia do wartości** — dobry wynik, lepszy niż w Zabbixie. Natomiast **droga powrotna jest zepsuta**: [`ObjectDetailPage.tsx:54`](../../frontend/src/pages/ObjectDetailPage.tsx#L54) ma przycisk „Wróć do dashboardu” prowadzący na `/dashboard`, a `/dashboard` jest w [`App.tsx:59`](../../frontend/src/App.tsx#L59) przekierowaniem na `/objects`. Użytkownik klika „wróć do dashboardu” i ląduje na liście obiektów — nazwa celu nie zgadza się z celem. Brakuje też okruszków: będąc na obiekcie nie widać, w której gminie się jest.

### 2.3. Wymiar 3 — prezentacja pomiaru: wartość, czas, jakość

To jest wymiar, w którym mamy najbardziej konkretny niezmiennik produktowy ([§2.4.3](../business/01_plan_biznesowy.md): *ostatnia poprawna wartość nie może być prezentowana jako bieżąca bez informacji o czasie pomiaru i jakości*) — i, jak się okazuje, najlepiej opracowany wzorzec przemysłowy.

**Co robi rynek.** Świat automatyki rozwiązał to trzydzieści lat temu w modelu jakości OPC: każda wartość niesie status z trzech klas — `Good`, `Uncertain`, `Bad` — gdzie `Uncertain` oznacza wprost „wartość była dobra, ale system nie dostał nowej w rozsądnym czasie” `[dok]`. Ignition renderuje to **nakładką graficzną bezpośrednio na komponencie pokazującym wartość**: nakładka „Unknown” dla każdego podkodu `Uncertain`, nakładka „Error” dla każdej jakości `Bad` `[dok]`. Wartość nie znika — zostaje na ekranie, ale jest wizualnie zdyskwalifikowana.

Krytyczna obserwacja z tej samej dokumentacji: Ignition **nie generuje własnego kodu jakości dla „znacznik czasu zbyt stary”**, więc operator musi sam patrzeć na czas, żeby wykryć dane nieaktualne mimo jakości `Good` `[dok]`. To jest znana pułapka całej branży — i to jest dokładnie ta pułapka, którą nasz `FreshnessBar` zamyka.

Grafana rozdziela dwa różne zjawiska, które łatwo pomylić: **brak danych** (zapytanie nie zwróciło serii — metryka nie istnieje albo nic nie zbiera) od **wartości pustych** (seria istnieje, ale brak punktu w danym czasie) `[dok]`. Do tego oznacza serie jako nieaktualne po dwóch interwałach ewaluacji `[dok]`. Nasze statusy `no_data` i `stale` odpowiadają dokładnie temu rozróżnieniu — czyli mamy właściwy model, tylko go nie pokazujemy konsekwentnie.

**Co z tego wynika dla nas.** Nasze podejście **ma odpowiednik na rynku i jest miejscami lepsze**: `FreshnessBar` ([`FreshnessBar.tsx`](../../frontend/src/components/ui/FreshnessBar.tsx)) realizuje dokładnie ten mechanizm, którego brak Ignition sam u siebie odnotowuje — ciągłą, wizualną informację o wieku danych, nie tylko znacznik czasu do samodzielnej oceny. To warto zachować i rozszerzyć, nie zastępować.

Trzy luki, wszystkie do naprawienia tanio:

1. **Wartość i jakość są rozklejone.** W [`CurrentValueCard.tsx:45-49`](../../frontend/src/components/objects/CurrentValueCard.tsx#L45-L49) liczba jest wyświetlana dużym, czarnym `text-2xl font-bold` niezależnie od jakości; jakość ląduje w osobnym wierszu na dole karty, za poziomą kreską. Wartość `sensor_error` wygląda dokładnie tak samo autorytatywnie jak wartość `good`. Wzorzec nakładki z Ignition mówi wprost: znacznik jakości ma być **na** wartości, nie obok niej.
2. **Wiek danych jest w widoku obiektu tylko tekstem względnym** („2 godziny temu”, [`CurrentValueCard.tsx:14-17`](../../frontend/src/components/objects/CurrentValueCard.tsx#L14-L17)), bez `FreshnessBar`, który mamy i który jest tam potrzebny bardziej niż na kafelku listy.
3. **Nigdzie nie ma czasu bezwzględnego.** [`freshnessUtils.ts`](../../frontend/src/components/ui/freshnessUtils.ts) i `formatDistanceToNow` dają wyłącznie formę względną. Przy zgłoszeniu awarii, wpisie do dziennika czy rozmowie telefonicznej „14 h temu” jest bezużyteczne — potrzebna jest data i godzina. Wzorzec: czas względny jako etykieta główna, bezwzględny w `title`/tooltipie albo drobnym drukiem obok.

### 2.4. Wymiar 4 — statusy i kolor

**Co robi rynek.** Norma ISA-101 („high performance HMI”) formułuje regułę odwrotną do intuicji projektanta: **ekran w stanie normalnym jest szary i niskokontrastowy, a kolor jest zarezerwowany dla stanów nienormalnych** `[std]`. Około 90% powierzchni ekranu ma pozostać neutralne; kolor znaczy „patrz tutaj teraz” `[art]`. Czerwień jest rezerwowana wyłącznie dla awarii i alarmu, żeby nie zużyć jej uwagowo na dekorację `[art]`. Ta sama filozofia stoi za rekomendacją Ignition Perspective dla ekranów operatorskich `[art]`.

Od strony dostępności WCAG 2.2 SC 1.4.1 wymaga, żeby kolor nie był jedynym wizualnym nośnikiem informacji — wskaźniki statusu mają mieć etykietę tekstową, ikonę albo kształt `[std]`. Około 8% mężczyzn ma zaburzenie widzenia barw `[std]`, co przy typowej brygadzie wodociągowej oznacza realnie jedną osobę na kilkanaście.

**Co z tego wynika dla nas.** Nasz [`StatusPill`](../../frontend/src/components/ui/StatusPill.tsx) **spełnia WCAG 1.4.1**, bo zawsze renderuje etykietę tekstową obok kropki (`OBJECT_STATUS_LABEL_MAP`, [`statusConfig.ts:23-29`](../../frontend/src/lib/statusConfig.ts#L23-L29)). To jest dobra decyzja i nie ma powodu jej zmieniać. Ale sama kropka `●` niesie znaczenie wyłącznie kolorem — a etykieta ratuje sytuację tylko dopóki pill jest wyświetlany w całości. Wzorzec z rynku: kropka zastąpiona ikoną o różnym **kształcie** per status (koło / trójkąt / oktagon / przekreślone koło), czyli redundancja kształtu obok redundancji tekstu.

Znacznie poważniejszy problem to **semantyka palety**, i jest to problem faktyczny, nie estetyczny. W [`statusConfig.ts:15-22`](../../frontend/src/lib/statusConfig.ts#L15-L22) status `no_comm` mapuje się na semantykę `danger`, ale `danger` w [`SEMANTIC_STATUS_TO_TAILWIND`](../../frontend/src/lib/statusConfig.ts#L51-L58) wskazuje na tokeny `status-no-comm-*`, które w [`tokens.css`](../../frontend/src/styles/tokens.css) są zdefiniowane jako **odcienie szarości** (`#6b7280`, `#374151`). Efekt: „brak komunikacji” — czyli stan, w którym nie wiemy nic o obiekcie i który plan klasyfikuje jako **alarm krytyczny** ([§2.6.1](../business/01_plan_biznesowy.md): *brak komunikacji z obiektem krytycznym*) — renderuje się jako szara plakietka, wizualnie prawie nieodróżnialna od `no_data` (też szara, `#9ca3af`). Nazwa semantyczna mówi „danger”, piksele mówią „nic się nie dzieje”. Do tego komentarz w tokenach przy palecie alarmu głosi „Etap 5, teraz nieużywany ale zarezerwowany”, a typ `ObjectSummary.status` w [`types/telemetry.ts:20`](../../frontend/src/types/telemetry.ts#L20) w ogóle nie dopuszcza wartości `'alarm'` — mimo że `statusConfig.ts` ją definiuje. Warstwa typów i warstwa prezentacji rozjechały się.

Jednocześnie ISA-101 podpowiada, czego **nie** robić: nie kolorować na zielono wszystkiego, co działa. Nasz `ok` renderuje pełną zieloną plakietkę na każdym poprawnym obiekcie ([`statusConfig.ts:16`](../../frontend/src/lib/statusConfig.ts#L16)), więc przy piętnastu zdrowych obiektach ekran jest zielony — i jeden żółty obiekt musi się przebić przez czternaście konkurujących z nim plam koloru.

### 2.5. Wymiar 5 — widok alarmów i triage

**Najważniejszy wymiar tego zlecenia** — u nas ten ekran nie istnieje w ogóle, więc wszystko poniżej jest materiałem wejściowym do projektu w [§6](#6-projekt-widoku-alarmów).

**Struktura listy.** ThingsBoard pokazuje alarmy w tabeli, gdzie wiersz niesie: źródło (originator), typ, priorytet, status i osobę przypisaną; filtrować można po statusie, priorytecie, typie i przypisaniu, a filtry się łączą `[dok]`. Akcje potwierdzenia, wyczyszczenia i przypisania są **bezpośrednio w wierszu**, po najechaniu, bez wchodzenia w szczegół `[dok]`. Zabbix idzie dalej: pozwala zaznaczyć wiele problemów i wykonać **masową aktualizację** przyciskiem pod listą `[dok]`.

**Cykl życia i ślad.** W Zabbixie potwierdzenie alarmu jest zawsze połączone z komentarzem — użytkownik pisze, co robi — a lista wcześniejszych działań i komentarzy, wraz z czasem i osobą, jest widoczna w szczegółach zdarzenia `[dok]`. Ten sam ekran aktualizacji obsługuje komentowanie, zmianę priorytetu, potwierdzenie i wygaszenie `[dok]`. To jest kompletna realizacja naszego wymagania z [§2.8.3](../business/01_plan_biznesowy.md) („potwierdzenie, komentarz, historia reakcji”) i warto ją skopiować niemal wprost.

**Kontekst „dlaczego to się odpaliło”.** Grafana przebudowała widok szczegółów alarmu właśnie po to, żeby wyciągnąć na wierzch informacje wcześniej zakopane — przede wszystkim **zapytanie, które wygenerowało alarm** — tak, żeby dało się je ogarnąć wzrokiem od razu po otwarciu `[art]`. Do tego standaryzuje trzy adnotacje przy każdej regule: `summary`, `description` i `runbook_url` — link do instrukcji postępowania — wyświetlane w szczegółach alarmu `[dok]`. Szczegóły alarmu zawierają też gotowy odnośnik do utworzenia wyciszenia `[dok]`.

**Redukcja szumu — trzy różne mechanizmy, których nie wolno mylić.** Alertmanager rozdziela je czysto `[art]`:

- **grupowanie** — alarmy o tych samych etykietach lądują w jednym powiadomieniu zamiast w piętnastu,
- **wyciszanie (silence)** — czasowe wyłączenie powiadomień dla dopasowanych alarmów, na okno serwisowe albo znany problem,
- **inhibicja** — alarm o wysokim priorytecie **tłumi swoje własne skutki**: gdy padnie serwer bazy, nie chcemy osobnego alarmu z każdej usługi, która od niego zależy, tylko jednego wskazującego przyczynę `[art]`.

Datadog dokłada do tego ostrzeżenie z praktyki: wyciszanie ma skutki uboczne, o których trzeba użytkownika informować w interfejsie — wyciszenie monitora przez UI kasuje wszystkie zaplanowane dla niego przerwy serwisowe `[dok]`. Pozwala też wyciszyć **wybrany zakres**, a nie cały alarm `[dok]`.

**Ile alarmów to za dużo.** EEMUA 191 i ISA 18.2 podają twarde liczby: w normalnej pracy nie więcej niż **5 alarmów na operatora na godzinę**, a szczytowo nie więcej niż **10 alarmów na 10 minut** `[std]`. ISA 18.2 formułuje przy tym regułę projektową, która powinna być u nas zapisana wprost: **alarm, który nie wymaga żadnej reakcji operatora, ma zostać zamieniony na zdarzenie informacyjne** `[std]`. Zaleca też martwą strefę (histerezę) na poziomie 2–5% zakresu wielkości, żeby nie generować alarmów-drgań `[art]`.

**Co z tego wynika dla nas.** Nasz [`§2.6.4 planu`](../business/01_plan_biznesowy.md) ma już histerezę, czas utrzymania i minimalny czas między zdarzeniami — czyli model reguły jest zgodny z normą. Czego w planie nie ma, a co rynek uznaje za konieczne: **grupowania, inhibicji i wyciszania**. Przy zaniku zasilania na hydroforni nasza obecna specyfikacja wygeneruje jednocześnie: brak komunikacji, brak odczytu z czujnika temperatury, brak odczytu z czujnika ciśnienia i zanik zasilania — cztery alarmy z jednej przyczyny, do jednego wyjazdu. To już jest przekroczenie progu EEMUA przy jednym zdarzeniu na jednym obiekcie.

### 2.6. Wymiar 6 — wykresy i analiza historii

**Co robi rynek.** HWM oferuje krzywe trendów z przewijaniem i przybliżaniem `[mkt]`; AVEVA Insight buduje widok wokół wykresów czasowych, grafik procesowych i geolokalizacji `[mkt]`. Kluczowe ustalenie dotyczy jednak nie funkcji, tylko **prawdziwości wykresu**: Grafana traktuje sposób rysowania braków jako świadomą decyzję projektową — wartości puste mogą zostać pokazane jako przerwa, mogą zostać połączone linią „w sposób mylący” albo potraktowane jako zero, w zależności od ustawień panelu `[dok]`. Ustawienie „null jako zero” jest przy tym opisane jako osobna, jawna opcja `[art]` — czyli świat obserwowalności uznaje domyślne dorysowywanie linii przez lukę za pułapkę, przed którą trzeba użytkownika ostrzec.

**Co z tego wynika dla nas.** Nasz wykres ([`ObjectMeasurementsChart.tsx`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx)) używa `<Line type="monotone" dot={false}>` na danych scalonych po znaczniku czasu. Recharts przy braku wiersza dla danego czasu **narysuje prostą między sąsiednimi punktami** — czyli dwunastogodzinna przerwa w łączności wygląda na wykresie jak spokojny, liniowy przebieg ciśnienia. To bezpośrednio łamie [`UC-02`](../business/01_plan_biznesowy.md), który wymaga, żeby system pokazywał przerwy w komunikacji, i podważa cały niezmiennik z §2.4.3 w warstwie historycznej: pilnujemy jakości przy wartości bieżącej, a na wykresie ją tracimy.

Dwie mniejsze luki: **limit trzech serii** ([`ObjectMeasurementsChart.tsx:94`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L94) — `.slice(-3)`) jest arbitralny i cicho odrzuca czwarty wybór bez komunikatu; oraz **brak drugiej osi Y** — ciśnienie w barach (0–6) i temperatura w °C (0–20) na wspólnej osi sprawiają, że jedna z serii jest wizualnie płaska. Brakuje też eksportu, wymaganego przez [`UC-05`](../business/01_plan_biznesowy.md) i [§2.8.2](../business/01_plan_biznesowy.md), oraz zakresu niestandardowego („od–do”) — dziś są cztery sztywne przyciski 2h/24h/7d/30d ([`ObjectDetailPage.tsx:136-141`](../../frontend/src/pages/ObjectDetailPage.tsx#L136-L141)), więc nie da się obejrzeć zeszłotygodniowej awarii.

### 2.7. Wymiar 7 — konfiguracja progów i reguł

**Co robi rynek.** Rozstrzygnięcie jest jednoznaczne: dla użytkownika nietechnicznego **formularz, nie wyrażenie**. Azure IoT Central konfiguruje reguły w całości przez portal, bez kodu dla scenariuszy podstawowych `[art]`. Datacake reklamuje wprost „bez skryptów, bez YAML — skonfiguruj i aktywuj” w edytorze wizualnym `[mkt]`. ThingsBoard trzyma reguły alarmowe jako konfigurację obiektu (warunek, logika priorytetu, reguły czyszczenia i automatycznego zamykania), a nie jako kod `[dok]`.

Dwa niuanse warte przeniesienia: ThingsBoard rozdziela **warunek utworzenia** od **warunku wyczyszczenia** alarmu jako dwie osobne konfiguracje `[dok]` — to jest dokładnie nasza para „próg aktywacji / warunek zakończenia” z §2.6.4, i warto, żeby w UI też były dwoma osobnymi blokami, a nie jednym polem z histerezą do wyliczenia w głowie. Drugi: martwa strefa 2–5% zakresu jako **wartość domyślna podpowiadana przez system** `[art]`, a nie puste pole, które użytkownik wypełni zerem i dostanie alarm-drgania.

**Co z tego wynika dla nas.** U nas nie ma dziś żadnego ekranu konfiguracji reguł alarmowych — [§2.8.4 planu](../business/01_plan_biznesowy.md) przewiduje go docelowo, backend modułu alarmów też jeszcze nie istnieje. Rekomendacja projektowa: kreator w formie zdania z uzupełnianymi lukami („Jeśli **ciśnienie** na **[punkt pomiarowy]** spadnie poniżej **[2,0] bar** i utrzyma się tak przez **[120] s**, zgłoś alarm **[krytyczny]**”), z domyślną histerezą wyliczoną z zakresu czujnika i z podglądem „ta reguła odpaliłaby się N razy w ostatnich 30 dniach” — bo ten podgląd zamienia zgadywanie progu w decyzję opartą na danych, które i tak mamy w bazie.

### 2.8. Wymiar 8 — praca na telefonie

> Dokument z zakresu B-12 (widok mobilny) **nie istnieje** w repozytorium w chwili pisania (`docs/` nie zawiera żadnego pliku o tym zakresie), więc wymiar opisany samodzielnie, w zakresie tego briefu. Gdy B-12 powstanie, jego audyt responsywności jest nadrzędny wobec tej sekcji.

**Co robi rynek.** Ignition Perspective jest projektowany mobile-first, z kontenerami punktów granicznych i układami elastycznymi, a dla dotyku zaleca **cele dotykowe co najmniej 44 px** i tekst czytelny z odległości ramienia `[art]`. AVEVA Insight ma osobną aplikację mobilną do podglądu danych i odbioru alertów `[mkt]`. Najciekawszy jest jednak PagerDuty, bo rozwiązuje dokładnie nasz problem „czy jechać”: ekran szczegółu incydentu na telefonie sprowadza się do **informacji, osi czasu i sekcji statusu**, akcje potwierdzenia i zamknięcia są dostępne **gestem przesunięcia** wprost z listy, a osobna zakładka „Triage” skupia działania: dodanie notatki, zmianę priorytetu, dołączenie osób `[dok]`.

**Co z tego wynika dla nas.** Nasz frontend jest responsywny na poziomie szkieletu — [`OrgShell.tsx:36-50`](../../frontend/src/components/layout/OrgShell.tsx#L36-L50) ma sidebar wysuwany z nakładką na `lg:`, siatka kart schodzi do jednej kolumny. Ale warstwa danych się nie skaluje:

- [`DataTable.tsx`](../../frontend/src/components/ui/DataTable.tsx) renderuje `<table class="w-full">` w kontenerze z `overflow-hidden` — na telefonie kolumny się zgniatają i **nie da się przewinąć w poziomie**, treść jest po prostu przycięta. Tabela obiektów ma sześć kolumn.
- Wiersz jest klikalny przez `onClick` na `<tr>` ([`DataTable.tsx:149-157`](../../frontend/src/components/ui/DataTable.tsx#L149-L157)) — bez `role`, bez `tabIndex`, bez obsługi klawiatury. Nagłówek sortowania to `<th onClick>`, też nie przycisk. Nie działa z klawiatury ani z czytnikiem ekranu.
- Sterowanie wykresem to przyciski `px-3 py-1.5` — poniżej progu 44 px.
- Ikona gwiazdki przypinania ma `p-1` wokół ikony 16 px, czyli cel dotykowy ~24 px ([`ObjectsTable.tsx:54`](../../frontend/src/components/objects/ObjectsTable.tsx#L54)).

Wzorzec do przeniesienia z PagerDuty: na wąskim ekranie tabela **zamienia się w listę kart**, gdzie każda karta niesie tylko to, co potrzebne do decyzji „jadę / nie jadę” — nazwa obiektu, status, wartość, która wywołała problem, wiek danych — a reszta jest schowana.

### 2.9. Wymiar 9 — onboarding i dodanie obiektu

**Co robi rynek.** ThingsBoard ma dopracowany, publicznie opisany model **przejęcia urządzenia (claiming)**: producent wysyła urządzenia wstępnie zarejestrowane na koncie dostawcy, a klient przejmuje swoją sztukę kluczem tajnym; po przejęciu tylko jego użytkownicy widzą urządzenie i jego dane `[dok]`. Klucz może być zakodowany w **kodzie QR** zawierającym nazwę urządzenia i sekret, skanowanym aplikacją `[dok]`. Dokumentacja rozdziela przy tym dwa scenariusze: urządzenie z wyświetlaczem, które samo pokazuje kod przy pierwszym uruchomieniu, oraz urządzenie bez żadnego interfejsu (NB-IoT, LoRaWAN), gdzie sekret trafia do klienta w opakowaniu albo w mailu powitalnym `[dok]`. Kallipr reklamuje „szablony konfiguracji gotowe do użycia, przyspieszające wdrożenie i redukujące błędy” oraz konfigurację urządzeń z wbudowaną diagnostyką gotową do pracy w terenie `[mkt]`.

**Co z tego wynika dla nas.** Nasz gateway to ESP32 bez wyświetlacza — czyli jesteśmy w drugim scenariuszu ThingsBoard. Mamy już [`PlatformActivationCodesPage`](../../frontend/src/pages/PlatformActivationCodesPage.tsx) i [`useActivationCodes`](../../frontend/src/hooks/useActivationCodes.ts), czyli mechanizm kodów aktywacyjnych istnieje — ale żyje **wyłącznie na płaszczyźnie platformy**, niedostępnej dla administratora gminy. Sekwencja „mam urządzenie w ręku → widzę dane” wymaga dziś: utworzenia obiektu wodociągowego (dialog w [`WaterObjectFormDialog`](../../frontend/src/components/dialogs/WaterObjectFormDialog.tsx)), utworzenia urządzenia ([`DeviceFormDialog`](../../frontend/src/components/dialogs/DeviceFormDialog.tsx)), wejścia na osobną stronę punktów pomiarowych ([`DeviceMeasurementPointsPage`](../../frontend/src/pages/DeviceMeasurementPointsPage.tsx)) i dodania kanałów po jednym — czyli **trzech niezależnych formularzy w trzech miejscach nawigacji, bez żadnej nici prowadzącej**. Wzorzec do wzięcia: jeden kreator „Dodaj obiekt” w krokach, kończący się ekranem oczekiwania na pierwszy pomiar z tego gatewaya.

---

## 3. Katalog wzorców z werdyktem

Werdykt: **BIERZ** — pasuje do naszych przypadków użycia; **NIE BIERZ** — antywzorzec dla małej gminy; **ROZWAŻ** — z warunkiem, przy którym zaczyna mieć sens.

| # | Wzorzec | Źródło wzorca | Werdykt | Uzasadnienie |
|---|---|---|---|---|
| W-01 | Ekran startowy pokazuje wyjątki, nie inwentarz | Zabbix `Monitoring → Problems` | **BIERZ** | Wprost realizuje pytanie „który obiekt wymaga uwagi” z §2.8.1; przy 15 obiektach wystarczy sortowanie priorytetowe, nie trzeba osobnego ekranu |
| W-02 | Kondycja urządzenia jako osobny strumień, nie przypis przy pomiarze | Ayyeka FAI | **BIERZ** | Pokrywa `UC-04` i pozwala odróżnić „awarię obiektu” od „awarii telemetrii”, czego dziś nie robimy |
| W-03 | Nakładka jakości renderowana na wartości | Ignition (quality overlays) / model OPC | **BIERZ** | Jedyny wzorzec, który realizuje niezmiennik §2.4.3 w sposób nie do przeoczenia |
| W-04 | Ciągły wskaźnik wieku danych, nie tylko znacznik czasu | *nasz własny* `FreshnessBar` | **BIERZ (utrzymać)** | Ignition sam dokumentuje brak kodu jakości dla „zbyt stary znacznik czasu”; mamy przewagę, trzeba ją rozciągnąć na widok obiektu |
| W-05 | Czas względny + bezwzględny obok siebie | praktyka Zabbix/Grafana (szczegóły zdarzenia) | **BIERZ** | „14 h temu” jest bezużyteczne w zgłoszeniu awarii i w dzienniku pracy |
| W-06 | Kolor zarezerwowany dla stanu nienormalnego, tło neutralne | ISA-101 / high-performance HMI | **BIERZ** | Nasz ekran przy 15 zdrowych obiektach jest zielony; jeden żółty musi konkurować z 14 plamami koloru |
| W-07 | Redundancja kształtu obok koloru i tekstu | WCAG 2.2 SC 1.4.1 | **BIERZ** | Tanie (ikona zamiast `●`), a `StatusPill` jest używany wszędzie |
| W-08 | Przerwa w danych rysowana jako przerwa na wykresie | Grafana (null vs. no data) | **BIERZ** | Dziś linia przez lukę kłamie o przebiegu; łamie `UC-02` |
| W-09 | Akcje alarmu bezpośrednio w wierszu listy | ThingsBoard (tabela alarmów) | **BIERZ** | Dyspozytor obsługuje serię alarmów bez wchodzenia w każdy z osobna |
| W-10 | Potwierdzenie zawsze z komentarzem, historia reakcji przy zdarzeniu | Zabbix (acknowledgment) | **BIERZ** | Realizuje wprost §2.8.3 i „historię reakcji na zdarzenia” z §2.7.2 |
| W-11 | Alarm niesie kontekst „dlaczego się odpalił” + instrukcję postępowania | Grafana (`summary`, `description`, `runbook_url`) | **BIERZ** | Pracownik terenowy potrzebuje odpowiedzi „czy jechać”, a nie samego faktu przekroczenia progu |
| W-12 | Grupowanie alarmów z jednej przyczyny | Alertmanager (grouping) | **BIERZ** | Zanik zasilania generuje u nas dziś 4 alarmy wg §2.6; EEMUA dopuszcza 5/h łącznie |
| W-13 | Wyciszenie na okno czasowe (prace serwisowe) | Alertmanager silences / Datadog downtime | **BIERZ** | Bez tego każde planowe płukanie sieci to fala fałszywych alarmów |
| W-14 | Formularz zamiast wyrażenia przy konfiguracji progu | Azure IoT Central / Datacake / ThingsBoard | **BIERZ** | Użytkownik to konserwator sieci, nie inżynier danych |
| W-15 | Rozdzielony warunek powstania i warunek zamknięcia alarmu | ThingsBoard (create/clear rule) | **BIERZ** | Odpowiada parze „próg aktywacji / warunek zakończenia” z §2.6.4; w UI mają być dwa bloki, nie jedno pole |
| W-16 | Tabela zamienia się w listę kart na wąskim ekranie | PagerDuty mobile | **BIERZ** | Nasza `DataTable` jest dziś na telefonie przycięta bez możliwości przewinięcia |
| W-17 | Kreator dodania obiektu zamiast trzech formularzy w trzech miejscach | ThingsBoard claiming / Kallipr templates | **BIERZ** | Wdrożenie u gminy robi jedna osoba, raz, w terenie |
| W-18 | Kod QR na gatewayu przyspieszający parowanie w terenie | ThingsBoard (claiming via QR) | **ROZWAŻ** | Ma sens dopiero gdy powstanie widok mobilny (B-12) i gdy liczba wdrożeń przekroczy kilka; przy trzech prototypach kod z opakowania wystarczy |
| W-19 | Mapa jako główny ekran operacyjny | Hawle.live, HWM DataGate | **ROZWAŻ** | §2.8.1 świadomie stawia listę; mapa ma sens przy obiektach rozrzuconych na kilkadziesiąt km — czyli gdy pojawi się drugi klient z rozproszoną siecią, i tylko jako zakładka obok listy |
| W-20 | Inhibicja — przyczyna tłumi swoje skutki | Alertmanager (inhibition) | **ROZWAŻ** | Wymaga modelu zależności między regułami; sensowne dopiero gdy alarmów będzie na tyle dużo, że grupowanie (W-12) przestanie wystarczać |
| W-21 | Widżet „średnia kondycja regionu” z rozwinięciem | Ayyeka (area averages) | **ROZWAŻ** | Ma sens dla zarządu przy wielu gminach; przy jednej gminie z 15 obiektami agregat regionu nie niesie informacji |
| W-22 | Masowa aktualizacja wielu alarmów naraz | Zabbix (mass update) | **ROZWAŻ** | Wchodzi w grę dopiero gdy pojedyncza fala przekracza kilkanaście alarmów; przy naszej skali grupowanie (W-12) załatwia problem taniej |
| W-23 | Konfigurowalny dashboard budowany przez użytkownika z widżetów | AVEVA Insight, ThingsBoard, Ayyeka | **NIE BIERZ** | Antywzorzec dla małej gminy: przerzuca projektowanie interfejsu na użytkownika, który robi to raz i nigdy nie poprawia. §2.8.1 wymaga jednej, przemyślanej odpowiedzi na jedno pytanie, nie płótna do rysowania |
| W-24 | Grafika procesowa / mnemoschemat obiektu (rysunek hydroforni z animacjami) | AVEVA, klasyczna SCADA | **NIE BIERZ** | Wymaga rysowania schematu per obiekt, czyli pracy projektowej przy każdym wdrożeniu — zabija model „montaż w jeden dzień” z §4.2.3. Dodatkowo sugeruje sterowanie, a system jest read-only |
| W-25 | Sterowanie z poziomu interfejsu (start/stop pompy) | Inventia DataPortal, klasyczna SCADA | **NIE BIERZ** | Sprzeczne z założeniem read-only z [`CONTEXT.md`](../business/CONTEXT.md); zmienia klasę ryzyka i wymagania NIS2 |
| W-26 | Wyciszenie kasujące ciche efekty uboczne bez ostrzeżenia | Datadog (mute usuwa zaplanowane downtime'y) | **NIE BIERZ** | Datadog to dokumentuje jako pułapkę; jeśli wprowadzimy wyciszanie (W-13), interfejs ma **jawnie** mówić, co zostanie wyłączone i do kiedy |
| W-27 | Alarm bez wymaganej reakcji operatora | — (antywzorzec z ISA 18.2) | **NIE BIERZ** | ISA 18.2 wprost: co nie wymaga reakcji, ma być zdarzeniem informacyjnym. Nasz katalog §2.6.3 już to rozdziela — pilnować, żeby UI nie zrównał tych dwóch rzeczy w jednej liście |

---

## 4. Konfrontacja z naszym interfejsem

Sedno zlecenia. Dla każdego wzorca **BIERZ**: co jest dziś w kodzie, co zmienić, w którym pliku.

### 4.1. W-01 — ekran startowy pokazuje wyjątki

**Co mamy.** Trasa `/` i `/dashboard` przekierowują na `/objects` ([`App.tsx:58-59`](../../frontend/src/App.tsx#L58-L59)). `ObjectsPage` renderuje wszystkie obiekty gminy w siatce kart albo w tabeli, bez sortowania po statusie — kolejność wynika z odpowiedzi API i z przypiętych ręcznie ulubionych ([`ObjectsPage.tsx:109-118`](../../frontend/src/pages/ObjectsPage.tsx#L109-L118)). Nagłówek brzmi „Obiekty wodne”, a podtytuł „Pulpit zarządzania obiektami i monitorowaniem w czasie rzeczywistym” ([`ObjectsPage.tsx:130-133`](../../frontend/src/pages/ObjectsPage.tsx#L130-L133)).

Istnieje też druga, **nieosiągalna** implementacja tego samego: [`DashboardPage.tsx`](../../frontend/src/pages/DashboardPage.tsx) wraz z [`ObjectsStatusTable.tsx`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx) — kompletny komponent z filtrem statusu i paginacją, do którego nie prowadzi żadna trasa, bo `/dashboard` jest przekierowaniem. Ma własny, zduplikowany słownik etykiet statusów ([`ObjectsStatusTable.tsx:73-79`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L73-L79)), rozjeżdżający się z [`OBJECT_STATUS_LABEL_MAP`](../../frontend/src/lib/statusConfig.ts#L23-L29) (`'OK'` vs `'OK — Aktywne'`).

**I rzecz, która czyni to gorszym niż zwykły martwy kod:** jedynym miejscem w całym repozytorium, które importuje `DashboardPage`, jest [`DashboardPage.test.tsx`](../../frontend/src/pages/DashboardPage.test.tsx) (zweryfikowane przeszukaniem `frontend/src` — poza własnym plikiem i własnym testem nie ma ani jednego odwołania). Ekran jest więc pokryty zielonymi testami i **nie da się do niego wejść w aplikacji**. Zestaw testów daje fałszywe poczucie, że dashboard działa, podczas gdy użytkownik nigdy go nie zobaczy. To jest argument za rozstrzygnięciem sprawy teraz, a nie za odłożeniem jej jako kosmetyki.

**Co zmienić.**

1. Sortowanie domyślne w [`ObjectsGrid.tsx`](../../frontend/src/components/objects/ObjectsGrid.tsx) i [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx): przypięte → `alarm` → `no_comm` → `warning` → `no_data` → `ok`, a w obrębie grupy po czasie ostatniego kontaktu rosnąco. Przypięte zostają na górze, bo to świadomy wybór użytkownika.
2. Pasek podsumowania nad listą: „2 wymagają uwagi · 1 bez łączności · 12 OK”, każdy człon filtrujący listę po kliknięciu. Filtr statusu istnieje już gotowy w [`ObjectsStatusTable.tsx:136-172`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L136-L172) — przenieść, zamiast pisać od nowa.
3. Rozstrzygnąć los `DashboardPage`/`ObjectsStatusTable`: albo usunąć jako martwy kod, albo przywrócić trasę. Utrzymywanie dwóch rozjeżdżających się list obiektów jest źródłem błędów, a duplikat słownika statusów już się rozjechał.
4. Nazwa strony na „Obiekty wodociągowe” — [`CONTEXT.md`](../business/CONTEXT.md) definiuje ten termin i zaleca unikać synonimów; „obiekt wodny” nie jest terminem ze słownika.

### 4.2. W-02 — kondycja gatewaya jako osobny strumień

**Co mamy.** Status obiektu miesza dwie różne rzeczy w jednym polu: `no_comm` (gateway milczy — problem telemetrii) stoi w tym samym wyliczeniu co `warning` i `alarm` (parametr wody poza zakresem — problem procesu), [`statusConfig.ts:5`](../../frontend/src/lib/statusConfig.ts#L5). Skutek: obiekt z pękniętą rurą **i** martwym modemem może pokazać tylko jeden z tych faktów.

**Co zmienić.** Rozdzielić na dwa niezależne wskaźniki w wierszu i na karcie: **stan procesu** (`ok`/`warning`/`alarm`) i **stan łączności** (`online`/`opóźniony`/`brak łączności`). Dane są już dostępne — [`ObjectSummary`](../../frontend/src/types/telemetry.ts#L13-L24) niesie `last_contact_at` obok `last_measurement_at`, a więc rozróżnienie „gateway się odzywa, ale czujnik milczy” jest wyliczalne po stronie frontu bez zmian w API. Zmiana dotyka [`ObjectCard.tsx:107-117`](../../frontend/src/components/objects/ObjectCard.tsx#L107-L117) i kolumny statusu w [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx).

### 4.3. W-03 — nakładka jakości na wartości

**Co mamy.** [`CurrentValueCard.tsx:45-49`](../../frontend/src/components/objects/CurrentValueCard.tsx#L45-L49) renderuje wartość jako `text-2xl font-bold text-neutral-900` niezależnie od jakości; `StatusPill kind="quality"` ląduje w stopce karty, po kresce ([`CurrentValueCard.tsx:52-55`](../../frontend/src/components/objects/CurrentValueCard.tsx#L52-L55)). Wartość z `sensor_error` wygląda równie autorytatywnie jak poprawna. Do tego czas pomiaru jest w karcie **dwa razy** — w popoverze i w stopce ([`CurrentValueCard.tsx:38-40`](../../frontend/src/components/objects/CurrentValueCard.tsx#L38-L40) i [`:67-69`](../../frontend/src/components/objects/CurrentValueCard.tsx#L57-L59)).

**Ta sama luka jest na liście obiektów — i tam jest poważniejsza, bo to najczęściej oglądany ekran aplikacji.** Oba warianty listy pokazują wartości pomiarowe, ale gołe:

- [`ObjectCard.tsx:119-131`](../../frontend/src/components/objects/ObjectCard.tsx#L119-L131) renderuje pierwsze dwa punkty pomiarowe jako `{point.value} {point.unit}` — bez jakości, bez czasu pomiaru.
- [`ObjectsTable.tsx:81-101`](../../frontend/src/components/objects/ObjectsTable.tsx#L81-L101) ma dedykowane kolumny „Ciśnienie” i „Temperatura”, renderowane tak samo goło: `` `${pressure.value} ${pressure.unit}` ``.

W obu przypadkach wartość `sensor_error` sprzed sześciu godzin wygląda identycznie jak świeży, poprawny pomiar. To naruszenie niezmiennika §2.4.3 wprost. `FreshnessBar` w sąsiedniej kolumnie mówi tylko o wieku **kontaktu z gatewayem**, nie o jakości konkretnego kanału — gateway może się odzywać regularnie, meldując `sensor_error`.

**Drugie ustalenie o tabeli, niezwiązane z jakością:** kolumny są zaszyte na sztywno pod dwa typy kanałów — `p.type === 'pressure'` i `p.type === 'temperature'`. **Przepływ, którego wymaga [§2.8.1](../business/01_plan_biznesowy.md), nie ma kolumny**, podobnie jak każdy inny kanał z Phase 2 (poziom zbiornika, praca pompy, chlor, mętność). Obiekt z przepływomierzem pokaże w tabeli dwie kreski i nic więcej. Kafelek jest pod tym względem lepszy — bierze dwa pierwsze punkty niezależnie od typu — ale za to arbitralnie ucina resztę bez informacji, że coś uciął.

**Co zmienić.**

1. Wydzielić komponent `MeasurementValue` (nowy plik w `components/ui/`) przyjmujący `{ value, unit, quality, measuredAt }` i renderujący wartość razem z jej jakością: dla `good` — czysta wartość; dla `stale`/`delayed` — wartość przygaszona (`text-neutral-500`) z ikoną zegara; dla `sensor_error`/`communication_error`/`out_of_range` — wartość przekreślona lub w nawiasach, z ikoną ostrzeżenia i etykietą; dla `unknown` — `—` zamiast liczby. Czas pomiaru zawsze w `title`. To jest przeniesienie wzorca nakładek Ignition do naszej warstwy komponentów.
2. Użyć go we wszystkich trzech miejscach: [`CurrentValueCard.tsx`](../../frontend/src/components/objects/CurrentValueCard.tsx), [`ObjectCard.tsx`](../../frontend/src/components/objects/ObjectCard.tsx) i w kolumnach wartości w [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx).
3. Zamienić dwie zaszyte kolumny tabeli na kolumny generowane z rzeczywistych typów kanałów występujących w danych — inaczej każdy nowy typ czujnika wymaga zmiany w kodzie tabeli.
4. Usunąć zdublowany czas pomiaru z `CurrentValueCard`.

### 4.4. W-04 — wskaźnik wieku danych

**Co mamy.** [`FreshnessBar`](../../frontend/src/components/ui/FreshnessBar.tsx) używany jest na kafelku ([`ObjectCard.tsx:134-138`](../../frontend/src/components/objects/ObjectCard.tsx#L134-L138)) i w tabeli obiektów — ale **nie w widoku obiektu**, gdzie użytkownik podejmuje decyzję. Domyślny `expectedIntervalSeconds` wynosi 300 s ([`FreshnessBar.tsx:26`](../../frontend/src/components/ui/FreshnessBar.tsx#L26)), podczas gdy [`ustalenia wspólne briefów`](../plan/01_briefy_dla_agentow.md) i §3.5 planu mówią o transmisji co ~60 s. Pasek jest więc skalibrowany na pięciokrotność rzeczywistego interwału i zapala się na czerwono dopiero po czterech minutach ciszy (80% z 300 s), gdy realnie brakuje już czterech transmisji.

Osobno: komponent przelicza świeżość `setInterval` co 1 s ([`FreshnessBar.tsx:38-46`](../../frontend/src/components/ui/FreshnessBar.tsx#L38-L46)) i wywołuje `setState` przy każdym tyknięciu. Przy piętnastu kafelkach to piętnaście przerysowań na sekundę dla informacji zmieniającej się co minutę.

**Co zmienić.** Przekazywać rzeczywisty interwał transmisji obiektu zamiast domyślnej wartości; obniżyć domyślną do 60 s. Wstawić `FreshnessBar` do nagłówka [`ObjectDetailPage`](../../frontend/src/pages/ObjectDetailPage.tsx) obok statusu. Zmniejszyć częstość przeliczania do 10 s albo uzależnić ją od skali (`elapsed < 60 s` → 1 s, dalej rzadziej).

### 4.5. W-05 — czas względny i bezwzględny razem

**Co mamy.** Wyłącznie forma względna, w dwóch niezależnych implementacjach: własna [`formatTimeAgo`](../../frontend/src/components/ui/freshnessUtils.ts) („5 min temu”) oraz `formatDistanceToNow` z `date-fns` z lokalizacją `pl` w [`ObjectsStatusTable.tsx:107-110`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L107-L110), [`CurrentValueCard.tsx:14-17`](../../frontend/src/components/objects/CurrentValueCard.tsx#L14-L17) i [`ObjectDetailPage.tsx:79-84`](../../frontend/src/pages/ObjectDetailPage.tsx#L79-L84). Dwa formaty tej samej informacji w jednym interfejsie („5 min temu” vs „około 5 minut temu”).

**Co zmienić.** Jedna funkcja w [`freshnessUtils.ts`](../../frontend/src/components/ui/freshnessUtils.ts) zwracająca parę `{ relative, absolute }`, gdzie `absolute` to `dd.MM.yyyy HH:mm` w strefie lokalnej. Wszędzie renderować względny jako tekst i bezwzględny w atrybucie `title` (a w widoku obiektu i w widoku alarmu — jawnie, drobnym drukiem). Wycofać bezpośrednie wywołania `formatDistanceToNow` z komponentów na rzecz tej jednej funkcji.

### 4.6. W-06 — kolor tylko dla stanu nienormalnego

**Co mamy.** Problem opisany w [§2.4](#24-wymiar-4--statusy-i-kolor): `no_comm` → semantyka `danger` → tokeny **szare**; `alarm` zdefiniowany w `statusConfig.ts`, ale nieobecny w typie [`ObjectSummary['status']`](../../frontend/src/types/telemetry.ts#L20); `ok` renderowany jako pełna zielona plakietka na każdym zdrowym obiekcie.

**Co zmienić.**

1. W [`tokens.css`](../../frontend/src/styles/tokens.css): przemapować `--color-status-no-comm-*` na paletę czerwoną/pomarańczową (brak łączności z obiektem to alarm wg §2.6.1), a `no_data` zostawić szare — wtedy dwa różne stany przestają wyglądać identycznie. Usunąć nieaktualny komentarz „Etap 5, teraz nieużywany” przy palecie alarmu.
2. W [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts): dodać wariant wyciszony dla `ok` — kropka i tekst w neutralnej szarości zamiast zielonego tła. Realizuje regułę ISA-101 „90% ekranu neutralne”; jeden żółty obiekt wśród czternastu szarych widać natychmiast, wśród czternastu zielonych — nie.
3. Doprowadzić `'alarm'` do typu `ObjectSummary['status']` w [`types/telemetry.ts:20`](../../frontend/src/types/telemetry.ts#L20), żeby warstwa typów zgadzała się z warstwą prezentacji (do uzgodnienia z kontraktem backendu — **wymaga sprawdzenia po stronie API przed zmianą**).

### 4.7. W-07 — kształt obok koloru

**Co mamy.** [`StatusPill.tsx:43-44`](../../frontend/src/components/ui/StatusPill.tsx#L43-L44) renderuje `●` w kolorze semantycznym plus etykietę tekstową. Etykieta ratuje zgodność z WCAG 1.4.1, ale sam znacznik graficzny jest identyczny dla wszystkich statusów.

**Co zmienić.** Zastąpić `●` mapą ikon `lucide-react` (biblioteka już jest w zależnościach) o **różnych kształtach**: `CheckCircle` dla `ok`, `AlertTriangle` dla `warning`, `AlertOctagon` dla `alarm`, `WifiOff` dla `no_comm`, `CircleDashed` dla `no_data`. Jedna mapa w [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) obok istniejących map koloru i etykiety. Zmiana punktowa w jednym komponencie, propaguje się na cały interfejs.

### 4.8. W-08 — przerwa w danych na wykresie

**Co mamy.** [`ObjectMeasurementsChart.tsx:67-79`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L67-L79) scala pomiary w mapę po znaczniku czasu i renderuje `<Line type="monotone">`. Brak wiersza dla danego czasu = prosta przez lukę.

**Co zmienić.**

1. Po posortowaniu `chartData` wstawić **jawne punkty `null`** tam, gdzie odstęp między kolejnymi znacznikami przekracza dwukrotność oczekiwanego interwału. Recharts przerywa linię na wartości `null`, więc przerwa staje się widoczna jako przerwa. To jest bezpośrednie przeniesienie rozróżnienia Grafany „null ≠ no data ≠ zero”.
2. Zaznaczyć okres bez łączności `<ReferenceArea>` w tle, z podpisem „brak łączności”.
3. Punkty o jakości innej niż `good` rysować innym znacznikiem (`dot` z obrysem) zamiast chować je w ciągłej linii — `MeasurementSeriesItem` niesie `quality` ([`types/telemetry.ts:41`](../../frontend/src/types/telemetry.ts#L41)), więc dane są dostępne, tylko nieużywane.
4. Druga oś Y dla serii o różnych jednostkach oraz komunikat przy próbie wyboru czwartej serii zamiast cichego odrzucenia ([`ObjectMeasurementsChart.tsx:94`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx#L94)).

### 4.9. W-09, W-10, W-11, W-12, W-13, W-15 — widok alarmów

**Co mamy.** Nic. Nie ma trasy, strony, komponentu ani typu. `AlarmsPage` nie istnieje, `types/` nie zawiera modelu alarmu, `OrgSidebar` nie ma pozycji „Alarmy”, `statusConfig.ts` nie definiuje priorytetów alarmu. Backendowy moduł alarmów również nie istnieje — [`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md) wymienia `core_data`, `security`, `telemetry`, `audit`, `device_identity`.

**Co zmienić.** Pełny projekt w [§6](#6-projekt-widoku-alarmów), gotowy do implementacji.

### 4.10. W-14 — konfiguracja progów formularzem

**Co mamy.** Nic w interfejsie gminy. Istniejące dialogi CRUD ([`DeviceMeasurementPointFormDialog`](../../frontend/src/components/dialogs/DeviceMeasurementPointFormDialog.tsx) i pokrewne) konfigurują kanały, nie reguły alarmowe.

**Co zmienić.** Kreator opisany w [§2.7](#27-wymiar-7--konfiguracja-progów-i-reguł), oparty na istniejącym [`useCrudPageState`](../../frontend/src/hooks/useCrudPageState.ts) i wzorcu dialogów z `components/dialogs/`. Zależy od backendu — do zaplanowania razem z modułem alarmów, nie przed nim.

### 4.11. W-16 — tabela na wąskim ekranie

**Co mamy.** [`DataTable.tsx:120-121`](../../frontend/src/components/ui/DataTable.tsx#L120-L121): `<div class="rounded-lg border overflow-hidden"><table class="w-full">`. Brak przewijania poziomego, brak wariantu mobilnego, wiersz klikalny bez obsługi klawiatury ([`:152-159`](../../frontend/src/components/ui/DataTable.tsx#L149-L157)), nagłówek sortowania jako `<th onClick>` ([`:126-138`](../../frontend/src/components/ui/DataTable.tsx#L125-L140)), klucz wiersza z indeksu tablicy ([`:154`](../../frontend/src/components/ui/DataTable.tsx#L151)).

**Co zmienić.**

1. Owinąć tabelę w `<div class="overflow-x-auto">` — jedna klasa, natychmiastowa poprawa na telefonie.
2. Nagłówek sortowalny jako `<button>` wewnątrz `<th>`; wiersz klikalny dostający `tabIndex={0}`, `role="button"` i obsługę `Enter`/`Space`, albo — lepiej — pierwsza komórka jako link, a `onClick` na wierszu jako skrót dla myszy.
3. Opcjonalna właściwość `getRowKey` zamiast klucza z indeksu.
4. Wariant `mobileCard`: poniżej `md:` renderować listę kart zamiast tabeli, z kolumnami oznaczonymi jako priorytetowe. Wzorzec z PagerDuty (W-16).

### 4.12. W-17 — kreator dodania obiektu

**Co mamy.** Trzy niezależne formularze w trzech miejscach nawigacji, opisane w [§2.9](#29-wymiar-9--onboarding-i-dodanie-obiektu). Bez nici prowadzącej i bez potwierdzenia „dane dochodzą”.

**Co zmienić.** `AddObjectWizard` w `components/dialogs/`, trzy kroki (obiekt → gateway z kodem aktywacyjnym → punkty pomiarowe), z ekranem końcowym odpytującym telemetrię o pierwszy pomiar z tego urządzenia i komunikatem „czekam na pierwsze dane…”. Wykorzystuje istniejące mutacje z [`useWaterObjects`](../../frontend/src/hooks/useWaterObjects.ts), [`useDevices`](../../frontend/src/hooks/useDevices.ts) i [`useMeasurementPoints`](../../frontend/src/hooks/useMeasurementPoints.ts) — nie wymaga zmian w API.

### 4.13. Ustalenia poza katalogiem wzorców

Znalezione przy lekturze kodu, warte naprawy, choć nie wynikają wprost z benchmarku:

| Ustalenie | Plik | Waga |
|---|---|---|
| Lista obiektów nie odświeża się sama — [`useTelemetryObjects`](../../frontend/src/hooks/useTelemetryApi.ts#L6-L20) nie ma `refetchInterval`, podczas gdy [`useTelemetryObjectDetail`](../../frontend/src/hooks/useTelemetryApi.ts#L22-L36) i [`useTelemetryMeasurements`](../../frontend/src/hooks/useTelemetryApi.ts#L38-L64) mają 15 s. Ekran, który ma odpowiadać „który obiekt wymaga uwagi”, pokazuje stan z chwili wejścia na stronę | [`useTelemetryApi.ts:6`](../../frontend/src/hooks/useTelemetryApi.ts#L6) | **wysoka** |
| „Wróć do dashboardu” prowadzi na listę obiektów, bo `/dashboard` jest przekierowaniem | [`ObjectDetailPage.tsx:54`](../../frontend/src/pages/ObjectDetailPage.tsx#L54), [`App.tsx:59`](../../frontend/src/App.tsx#L59) | średnia |
| `ObjectsStatusTable` pobiera 50 obiektów i paginuje po stronie klienta po 20; przy wzroście liczby obiektów po cichu gubi resztę | [`ObjectsStatusTable.tsx:17`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L17) | średnia |
| Zduplikowany słownik etykiet statusu, już rozjechany z `statusConfig.ts` | [`ObjectsStatusTable.tsx:73-79`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L73-L79) | średnia |
| Kafelki KPI w widoku obiektu pokazują „Sekwencja” (`last_seq`) jako jedną z czterech głównych informacji — to numer diagnostyczny firmware'u, nieprzydatny operacyjnie; przydałaby się tam jakość łączności albo liczba aktywnych alarmów | [`ObjectDetailPage.tsx:88-94`](../../frontend/src/pages/ObjectDetailPage.tsx#L88-L94) | niska |
| Brak eksportu danych mimo wymagania `UC-05` i §2.8.2 | [`ObjectDetailPage.tsx`](../../frontend/src/pages/ObjectDetailPage.tsx) | średnia |
| Terminologia rozjeżdża się ze słownikiem: „Obiekty wodne”, „Pomiary” jako nagłówek kolumny liczby kanałów | [`ObjectsPage.tsx:130`](../../frontend/src/pages/ObjectsPage.tsx#L130), [`ObjectsStatusTable.tsx:118`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L118) | niska |

---

## 5. Rekomendacja architektury informacji

Trzy role z [§2.7.2 planu](../business/01_plan_biznesowy.md) mają różne pytania, a dziś dostają jedną nawigację o dwóch pozycjach.

### 5.1. Stan obecny

```text
Monitorowanie
└── Obiekty            → lista wszystkich obiektów (siatka / tabela)
    └── /objects/:id   → zakładki: Aktualne wartości | Wykresy pomiarów
Konfiguracja
└── Urządzenia         → CRUD gatewayów (wymaga CAN_VIEW_ASSETS)
    └── /:deviceId     → punkty pomiarowe
[Ustawienia — dialog]  → konto, członkowie, grupy
```

Źródło: [`OrgSidebar.tsx:29-44`](../../frontend/src/components/layout/OrgSidebar.tsx#L29-L44) i [`App.tsx:56-84`](../../frontend/src/App.tsx#L56-L84).

### 5.2. Stan docelowy

```text
Monitorowanie
├── Przegląd            → lista obiektów posortowana wg pilności + pasek podsumowania
│   └── /objects/:id    → zakładki: Przegląd | Pomiary | Wykresy | Alarmy | Gateway
├── Alarmy              → NOWE: lista alarmów z triage (§6)
└── Raporty             → NOWE: eksport i zestawienia okresowe (UC-05, rola zarządu)
Konfiguracja
├── Obiekty i gateweye  → CRUD + kreator dodania obiektu (W-17)
└── Reguły alarmowe     → NOWE: kreator progów (W-14)
[Ustawienia — dialog]   → bez zmian
```

**Uzasadnienie odstępstw od stanu dzisiejszego:**

1. **„Alarmy” jako pozycja pierwszego poziomu, nie zakładka w obiekcie.** Pytanie dyspozytora brzmi „co się dzieje w gminie”, a nie „co się dzieje na hydroforni Zachód”. Alarmy zagnieżdżone w obiekcie wymagają, żeby najpierw wiedzieć, którego obiektu dotyczy problem — czyli odwracają kierunek pracy. Zabbix, Grafana i ThingsBoard wszystkie trzymają alarmy jako widok globalny.
2. **Rozdzielenie zakładek „Pomiary” i „Wykresy”.** Dziś obie zakładki żyją na tej samej stronie ([`ObjectDetailPage.tsx:105-108`](../../frontend/src/pages/ObjectDetailPage.tsx#L105-L108)), ale brakuje trzeciej — „Gateway” — na to, czego wymaga [§2.8.2](../business/01_plan_biznesowy.md): stan gatewaya i modemu, wersja konfiguracji urządzenia, historia komunikacji. Ta informacja dziś nie ma miejsca w interfejsie gminy, a jest dokładnie tym, czego potrzebuje pracownik terenowy przed wyjazdem.
3. **„Raporty” jako osobna pozycja.** Rola zarządu z §2.7.2 (liczba nieprawidłowości, dostępność obiektów, czas obsługi zdarzeń) nie ma dziś w interfejsie żadnego miejsca. Nie potrzebuje osobnej roli w systemie ani osobnego pulpitu — potrzebuje jednej strony z zestawieniem okresowym i eksportem. Świadomie **nie** rekomenduję osobnego „dashboardu zarządu”: przy jednej gminie z piętnastoma obiektami to byłby ekran oglądany raz na kwartał, a koszt utrzymania stały.
4. **Brak przełącznika ról.** Rozważone i odrzucone: trzy role z §2.7.2 różnią się głównie tym, jak *głęboko* schodzą, a nie tym, co widzą. Jedna nawigacja z sensownym sortowaniem obsługuje wszystkie trzy; przełącznik trybu dodałby stan do zapamiętania i kolejny wymiar do testowania. Różnicowanie zostaje tam, gdzie już jest — w uprawnieniach ([`useActivePermissions`](../../frontend/src/hooks/useActivePermissions.ts) i [`RequirePermission`](../../frontend/src/components/RequirePermission.tsx)).

### 5.3. Ścieżki trzech ról w układzie docelowym

| Rola | Pytanie | Ścieżka | Liczba kliknięć |
|---|---|---|---|
| Pracownik terenowy | „czy jechać na obiekt?” | Alarmy → alarm → sekcja „co to znaczy” + wykres okołozdarzeniowy | 2 |
| Dyspozytor | „co się dzieje w gminie?” | Przegląd (pasek podsumowania) → obiekt → Pomiary | 2 |
| Zarząd | „czy system działa i co dał?” | Raporty | 1 |

---

## 6. Projekt widoku alarmów

Ekran nie istnieje ani we froncie, ani w backendzie. Poniższy opis ma być na tyle szczegółowy, żeby dało się z niego zaimplementować bez zgadywania — zgodnie z definicją ukończenia briefu.

### 6.1. Model danych, którego wymaga ten ekran

Wynika z [§2.5](../business/01_plan_biznesowy.md), [§2.6.4](../business/01_plan_biznesowy.md) i z wzorców W-09…W-15. Do dopisania w `frontend/src/types/alarms.ts`:

```ts
export type AlarmState = 'new' | 'active' | 'acknowledged' | 'closed' | 'false_positive'
export type AlarmPriority = 'critical' | 'warning' | 'info'

export interface AlarmTrigger {
  point_id: string
  point_name: string
  parameter_type: string
  unit: string
  value: number              // wartość, która uruchomiła regułę
  threshold: number          // próg z reguły
  quality: DataQuality       // jakość pomiaru w chwili wyzwolenia
  measured_at: string
}

export interface AlarmActivity {
  at: string
  user_id: string | null     // null = akcja systemu
  user_name: string | null
  action: 'created' | 'escalated' | 'acknowledged' | 'commented'
    | 'closed' | 'marked_false' | 'silenced' | 'notification_sent'
  comment: string | null
  channel: string | null     // dla notification_sent: 'email' | 'sms' | ...
}

export interface Alarm {
  alarm_id: string
  org_id: string
  object_id: string
  object_name: string
  device_id: string
  rule_id: string
  rule_name: string
  priority: AlarmPriority
  state: AlarmState
  started_at: string
  ended_at: string | null      // kiedy warunek ustąpił (niezależne od zamknięcia)
  acknowledged_at: string | null
  acknowledged_by: string | null
  assigned_to: string | null
  trigger: AlarmTrigger
  group_id: string | null      // W-12: wspólna przyczyna
  group_size: number           // ile alarmów w grupie
  summary: string              // krótko, co się stało
  guidance: string | null      // W-11: co z tym zrobić — odpowiednik runbook_url
  activity: AlarmActivity[]
  silenced_until: string | null
}
```

Trzy decyzje projektowe w tym modelu, z uzasadnieniem:

- **`ended_at` jest niezależne od `state`.** Alarm może przestać być aktywny (ciśnienie wróciło), a nadal wymagać zamknięcia przez człowieka. Diagram stanów z §2.5 dopuszcza `Nowy → Zamknięty` samoczynnie, ale ścieżka `Potwierdzony → Zamknięty` wymaga decyzji operatora. Bez rozdzielenia tych dwóch osi nie da się pokazać „warunek ustąpił, czeka na zamknięcie”.
- **`quality` w `AlarmTrigger`.** §2.6.3 wymaga, żeby reguła nie odpalała się na danych o niedopuszczonej jakości. Zapisanie jakości w chwili wyzwolenia pozwala to zweryfikować po fakcie i jest jedynym sposobem, żeby wyjaśnić fałszywy alarm.
- **`guidance` zamiast `runbook_url`.** Grafana linkuje do zewnętrznej instrukcji `[dok]`. Mała gmina nie ma bazy instrukcji, więc pole trzyma treść wprost — jedno-, dwuzdaniową podpowiedź wpisywaną przy definicji reguły alarmowej.

### 6.2. Układ ekranu `/alarms`

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Alarmy                                             [Historia] [⚙]    │
│ 2 krytyczne · 3 ostrzeżenia · 1 wyciszony            ← pasek stanu    │
├──────────────────────────────────────────────────────────────────────┤
│ [Stan ▾] [Priorytet ▾] [Obiekt ▾] [Okres ▾]   [Tylko moje] [Wyczyść] │
├──────────────────────────────────────────────────────────────────────┤
│ ▲ KRYT.  Hydrofornia Zachód — ciśnienie 1,2 bar (próg 2,0)          │
│          od 14:32 · 47 min · wywołał: Ciśnienie sieciowe P1          │
│          ┃ +3 powiązane z tej samej przyczyny            [rozwiń ▾]  │
│          [Potwierdź] [Komentarz] [Wykres] [Zamknij] [Fałszywy]      │
├──────────────────────────────────────────────────────────────────────┤
│ ⛔ KRYT.  Przepompownia Nowa — brak komunikacji                       │
│          od 09:04 · 5 h 15 min · ostatni kontakt 09:03               │
│          ✓ potwierdzony przez J. Kowalski 09:20 — „jadę na miejsce”  │
│          [Komentarz] [Wykres] [Zamknij] [Fałszywy]                  │
├──────────────────────────────────────────────────────────────────────┤
│ ⚠ OSTRZ. SUW Południe — temperatura 2,1 °C (próg 3,0)                │
│          od 03:12 · warunek ustąpił 06:40 · czeka na zamknięcie      │
│          [Potwierdź] [Komentarz] [Wykres] [Zamknij]                 │
└──────────────────────────────────────────────────────────────────────┘
```

**Zasady układu i skąd pochodzą:**

1. **Wiersz mówi całą historię bez klikania** — obiekt, parametr, wartość która wywołała regułę, próg, czas trwania. Wymaganie §2.8.3 („wyświetlenie wartości, które uruchomiły regułę”) plus wzorzec Grafany „wyciągnij na wierzch to, co zakopane” (W-11).
2. **Akcje w wierszu, nie w szczegółach** — ThingsBoard (W-09). Dyspozytor obsługuje serię alarmów bez wchodzenia w każdy.
3. **Grupowanie widoczne jako zwinięty wiersz z licznikiem** — Alertmanager (W-12). Zanik zasilania to jeden wiersz z „+3 powiązane”, nie cztery wiersze. Rozwinięcie pokazuje składowe.
4. **Domyślny filtr: stany `new` + `active` + `acknowledged`.** Zamknięte i fałszywe są pod przyciskiem „Historia”. Widok `Problems` w Zabbixie z definicji wylicza problemy bieżące — archiwum zdarzeń jest osobnym ekranem `[dok]`.
5. **Sortowanie: priorytet malejąco, w obrębie priorytetu czas rozpoczęcia rosnąco** (najstarszy nieobsłużony na górze — to on grozi eskalacją).
6. **Ikona kształtu przy priorytecie** (`⛔`/`▲`/`⚠` → w implementacji `AlertOctagon`/`AlertTriangle`/`Info`) — W-07, WCAG 1.4.1.
7. **Czas trwania jest wyliczany i pokazywany wprost.** „47 min” niesie więcej informacji operacyjnej niż sam czas rozpoczęcia; czas bezwzględny obok (W-05).

### 6.3. Szczegół alarmu (panel boczny, nie osobna strona)

Wykorzystuje istniejący [`Drawer`](../../frontend/src/components/ui/Drawer.tsx) — ten sam wzorzec co [`DeviceDetailDrawer`](../../frontend/src/components/devices/DeviceDetailDrawer.tsx), więc lista nie traci kontekstu przy przeglądaniu kolejnych alarmów.

Sekcje, w kolejności od góry:

1. **Nagłówek** — priorytet (ikona + kolor + tekst), nazwa obiektu, stan, czas trwania.
2. **„Co się stało”** — `summary` plus tabelka wyzwolenia: parametr, wartość, próg, jakość danych w chwili wyzwolenia, czas pomiaru. Realizuje §2.8.3 i model OPC-owy z W-03: jeśli alarm odpalił się na danych o jakości innej niż `good`, ma to być widoczne od razu, bo to pierwsza hipoteza fałszywego alarmu.
3. **„Co z tym zrobić”** — treść pola `guidance` z reguły alarmowej. Sekcja ukryta, gdy puste (W-11).
4. **Wykres okołozdarzeniowy** — wykres punktu pomiarowego z zakresem domyślnie od `started_at − 2 h` do `min(now, ended_at + 2 h)`, z pionową linią `<ReferenceLine>` w momencie wyzwolenia i poziomą na wysokości progu. Wprost realizuje wymaganie §2.8.3 („przejście do wykresu obejmującego okres przed i po zdarzeniu”). Ponownie używa [`ObjectMeasurementsChart`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx) rozszerzonego o zakres bezwzględny — to samo rozszerzenie, którego wymaga W-08 i punkt 6 backlogu.
5. **Oś czasu reakcji** — lista `activity` chronologicznie: kto, kiedy, co zrobił, z jakim komentarzem; wpisy systemowe (utworzenie, wysłane powiadomienie) wizualnie odróżnione od ludzkich. Realizuje „historię reakcji na zdarzenia” z §2.7.2 i „historię wysłanych powiadomień” z §2.8.3 w jednej osi, zamiast w dwóch listach — bo operator i tak czyta je razem (wzorzec Zabbixa, W-10).
6. **Pasek akcji przyklejony do dołu panelu** — Potwierdź / Komentarz / Zamknij / Oznacz jako fałszywy / Wycisz.

### 6.4. Przepływy akcji

| Akcja | Zachowanie | Źródło wzorca |
|---|---|---|
| **Potwierdź** | Dialog z **wymaganym** polem komentarza (min. 3 znaki). Bez komentarza nie da się potwierdzić — potwierdzenie bez informacji „kto i co robi” nie niesie wartości operacyjnej | Zabbix: potwierdzenie połączone z komentarzem (W-10) |
| **Komentarz** | Dodaje wpis do osi czasu bez zmiany stanu | Zabbix |
| **Zamknij** | Dialog z opcjonalnym komentarzem. Blokowany, gdy `ended_at === null` — nie da się zamknąć trwającego alarmu bez świadomego potwierdzenia („warunek nadal trwa, zamknąć mimo to?”) | diagram stanów §2.5 |
| **Fałszywy** | Dialog z **wymaganym** powodem. Powód jest jedynym materiałem do korekty progu — bez niego reguła zostanie z tym samym progiem na zawsze | §2.8.3 + ISA 18.2 (racjonalizacja alarmów) |
| **Wycisz** | Wybór okna czasowego (1 h / 8 h / 24 h / do daty) + powód. Interfejs **jawnie wypisuje**, co zostanie wyciszone i do kiedy, oraz co dalej będzie działać (rejestracja zdarzeń tak, powiadomienia nie) | Alertmanager silences (W-13) + antywzorzec Datadog (W-26) |

Wszystkie dialogi budowane na istniejącym [`Dialog`](../../frontend/src/components/ui/Dialog.tsx) i [`ConfirmDialog`](../../frontend/src/components/ui/ConfirmDialog.tsx), stan formularzy na [`useCrudPageState`](../../frontend/src/hooks/useCrudPageState.ts) albo na jego wzorcu.

### 6.5. Wariant mobilny

Lista alarmów jest **jedynym ekranem, który pracownik terenowy naprawdę otwiera na telefonie** — to on odpowiada na pytanie „czy jechać”. Wariant wąski (W-16, wzorzec PagerDuty):

- lista kart zamiast tabeli, jedna karta = jeden alarm,
- na karcie tylko: ikona priorytetu, obiekt, jedno zdanie `summary`, czas trwania, stan potwierdzenia,
- akcje pierwotne jako pełnej szerokości przyciski na karcie: **Potwierdź** i **Szczegóły**; reszta w szczegółach,
- cele dotykowe minimum 44 px (Ignition Perspective, [§2.8](#28-wymiar-8--praca-na-telefonie)),
- sekcja „co z tym zrobić” (`guidance`) rozwinięta domyślnie na wąskim ekranie — na telefonie to najważniejsza treść, bo decyzja o wyjeździe zapada właśnie tam.

### 6.6. Punkty styku z resztą aplikacji

| Miejsce | Zmiana |
|---|---|
| [`OrgSidebar.tsx`](../../frontend/src/components/layout/OrgSidebar.tsx) | Pozycja „Alarmy” w sekcji `monitoring`, z licznikiem alarmów nieobsłużonych |
| [`App.tsx`](../../frontend/src/App.tsx) | Trasy `/alarms` i `/alarms/:alarmId` (druga otwiera listę z rozwiniętym panelem — żeby dało się wysłać link do konkretnego alarmu) |
| [`ObjectDetailPage.tsx`](../../frontend/src/pages/ObjectDetailPage.tsx) | Zakładka „Alarmy” z listą przefiltrowaną do tego obiektu — ten sam komponent listy, inny filtr |
| [`ObjectCard.tsx`](../../frontend/src/components/objects/ObjectCard.tsx), [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx) | Licznik aktywnych alarmów na kafelku/wierszu, klikalny do listy przefiltrowanej |
| [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) | Mapy koloru, etykiety i ikony dla `AlarmPriority` i `AlarmState` — obok istniejących map statusu obiektu i jakości danych |
| [`queryKeys.ts`](../../frontend/src/hooks/queryKeys.ts) | Gałąź `alarms` (lista z filtrami, szczegół, licznik) |

### 6.7. Uprawnienia — brakujące kody, bez których ekranu nie da się zbudować

Sprawdziłem katalog uprawnień: [`types/permissions.ts`](../../frontend/src/types/permissions.ts) (lustro `backend/app/modules/security/permission_catalog.py`) zawiera siedemnaście kodów i **żaden z nich nie dotyczy alarmów**. Najbliższe, `CAN_VIEW_ASSETS` i `CAN_MANAGE_ASSETS`, opisują rejestr obiektów, urządzeń i punktów pomiarowych — nie obsługę zdarzeń. Bez nowych kodów każdy, kto widzi obiekty, mógłby zamykać cudze alarmy.

Propozycja do dodania **najpierw w backendowym katalogu**, potem w lustrze frontowym (kolejność ma znaczenie — komentarz w pliku mówi wprost, że lustro utrzymuje się ręcznie):

| Kod | Nazwa w katalogu | Co odblokowuje |
|---|---|---|
| `CAN_VIEW_ALARMS` | Podgląd alarmów | Wejście na `/alarms`, zakładka „Alarmy” w obiekcie, licznik w sidebarze |
| `CAN_ACK_ALARMS` | Obsługa alarmów | Potwierdź, Komentarz, Zamknij, Oznacz jako fałszywy |
| `CAN_SILENCE_ALARMS` | Wyciszanie alarmów | Wycisz — celowo osobno od obsługi, bo wyciszenie ukrywa problem przed całą organizacją |
| `CAN_MANAGE_ALARM_RULES` | Zarządzanie regułami alarmowymi | Kreator progów (W-14) |

Mapowanie na role z [§2.7.3 planu](../business/01_plan_biznesowy.md): użytkownik operacyjny dostaje pierwsze dwa (plan mówi wprost, że „potwierdza alarmy i dodaje informacje dotyczące obsługi zdarzenia”), administrator klienta wszystkie cztery, użytkownik tylko do odczytu wyłącznie `CAN_VIEW_ALARMS`.

Egzekwowanie w kodzie: trasa przez [`RequirePermission`](../../frontend/src/components/RequirePermission.tsx) jak pozostałe chronione ekrany w [`App.tsx`](../../frontend/src/App.tsx), przyciski akcji przez `hasPermission()` z [`useActivePermissions`](../../frontend/src/hooks/useActivePermissions.ts). Zasada fail-closed tego hooka (brak kontekstu = pusta lista uprawnień) obowiązuje bez zmian.

### 6.8. Stany brzegowe i zachowania, które inaczej trzeba by zgadywać

| Sytuacja | Zachowanie |
|---|---|
| **Brak alarmów** | Nie pusta tabela, tylko komunikat potwierdzający: „Żaden obiekt nie zgłasza problemów”, z czasem ostatniego odświeżenia i odnośnikiem „Pokaż historię”. Cisza w systemie monitoringu jest informacją, a nie brakiem informacji — pusty ekran bez daty jest nieodróżnialny od zepsutego zapytania |
| **Ładowanie** | Szkielet wierszy zamiast spinnera na całą stronę — lista alarmów jest odświeżana cyklicznie i pełnoekranowy spinner co 15 s czyniłby ekran nieczytelnym |
| **Błąd pobrania** | Komunikat z przyciskiem ponowienia, ale **ostatnie znane alarmy zostają na ekranie**, wyszarzone, z etykietą „dane sprzed HH:MM”. Znikająca lista alarmów przy chwilowym błędzie sieci to gorszy stan niż lista nieaktualna i oznaczona |
| **Odświeżanie** | `refetchInterval` 15 s, spójnie z [`useTelemetryObjectDetail`](../../frontend/src/hooks/useTelemetryApi.ts#L22) — i z poz. 1 backlogu, która wyrównuje do tego resztę |
| **Akcja na zgrupowanym wierszu** | Potwierdzenie grupy potwierdza **wszystkie** alarmy w grupie jednym komentarzem; dialog mówi to wprost („Potwierdzisz 4 alarmy z tej samej przyczyny”). Zamknięcie grupy zamyka tylko te składowe, których warunek już ustąpił, a pozostałe zostawia — i informuje o tym po wykonaniu |
| **Alarm wyciszony** | Zostaje na liście, wyszarzony, z ikoną i czasem do końca wyciszenia. Nie znika — wyciszenie wycisza powiadomienia, nie problem. Filtr „Tylko aktywne” może go schować, ale nie jest to stan domyślny |
| **Alarm z jakością danych ≠ `good` w chwili wyzwolenia** | Wiersz dostaje dodatkowy znacznik „do weryfikacji”, bo to pierwszy kandydat na fałszywy alarm ([§2.6.3 planu](../business/01_plan_biznesowy.md) zabrania ewaluacji na niedopuszczonej jakości — jeśli taki alarm powstał, reguła jest źle skonfigurowana) |
| **Paginacja** | Serwerowa, 50 pozycji na stronę, z sortowaniem po stronie API. Świadomie **nie** powtarzamy wzorca z [`ObjectsStatusTable.tsx:17`](../../frontend/src/components/dashboard/ObjectsStatusTable.tsx#L17), gdzie pobierane jest 50 rekordów i paginowane po 20 po stronie klienta — przy alarmach ta konstrukcja po cichu ukryłaby najstarsze zdarzenia |
| **Głębokie linkowanie** | `/alarms/:alarmId` otwiera listę z rozwiniętym panelem, filtry w query stringu — żeby dyspozytor mógł wysłać pracownikowi terenowemu link do konkretnego alarmu |

---

## 7. Backlog zmian we froncie

Uszeregowany według stosunku wartości do kosztu. Koszt w skali XS (< 1 h) / S (kilka h) / M (1–2 dni) / L (powyżej).

### Poziom 1 — wysoka wartość, niski koszt

| # | Zmiana | Wzorzec | Plik | Koszt |
|---|---|---|---|---|
| 1 | `refetchInterval: 15000` w `useTelemetryObjects` — lista przestaje pokazywać stan sprzed wejścia na stronę | — | [`useTelemetryApi.ts:6`](../../frontend/src/hooks/useTelemetryApi.ts#L6) | XS |
| 2 | `overflow-x-auto` wokół tabeli | W-16 | [`DataTable.tsx:120`](../../frontend/src/components/ui/DataTable.tsx#L120) | XS |
| 3 | Czas bezwzględny w `title` wszędzie, gdzie jest względny | W-05 | [`freshnessUtils.ts`](../../frontend/src/components/ui/freshnessUtils.ts) + konsumenci | XS |
| 4 | Ikony o różnych kształtach w `StatusPill` | W-07 | [`StatusPill.tsx:43`](../../frontend/src/components/ui/StatusPill.tsx#L43), [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) | S |
| 5 | Przemapowanie tokenów `no_comm` na czerwień; wyciszony wariant `ok` | W-06 | [`tokens.css`](../../frontend/src/styles/tokens.css), [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) | S |
| 6 | Sortowanie priorytetowe + pasek podsumowania nad listą | W-01 | [`ObjectsGrid.tsx`](../../frontend/src/components/objects/ObjectsGrid.tsx), [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx) | S |
| 7 | `expectedIntervalSeconds` z rzeczywistej konfiguracji obiektu, domyślnie 60 s | W-04 | [`FreshnessBar.tsx:26`](../../frontend/src/components/ui/FreshnessBar.tsx#L26) | XS |
| 8 | Poprawka „Wróć do dashboardu” → „Wróć do listy obiektów” | — | [`ObjectDetailPage.tsx:54`](../../frontend/src/pages/ObjectDetailPage.tsx#L54) | XS |
| 9 | Terminologia wg `CONTEXT.md` („obiekt wodociągowy”, „punkty pomiarowe”) | — | [`ObjectsPage.tsx:130`](../../frontend/src/pages/ObjectsPage.tsx#L130) i in. | XS |

### Poziom 2 — wysoka wartość, średni koszt

| # | Zmiana | Wzorzec | Plik | Koszt |
|---|---|---|---|---|
| 10 | Komponent `MeasurementValue` z nakładką jakości, wdrożony w trzech miejscach | W-03 | nowy `components/ui/MeasurementValue.tsx` | S |
| 11 | Kolumny wartości generowane z typów kanałów zamiast zaszytych `pressure`/`temperature` — dziś przepływ z §2.8.1 nie ma gdzie się pokazać | W-03 | [`ObjectsTable.tsx:81-101`](../../frontend/src/components/objects/ObjectsTable.tsx#L81-L101) | S |
| 12 | Rozdzielenie stanu procesu od stanu łączności | W-02 | [`ObjectCard.tsx`](../../frontend/src/components/objects/ObjectCard.tsx), [`ObjectsTable.tsx`](../../frontend/src/components/objects/ObjectsTable.tsx) | M |
| 13 | Przerwy i jakość na wykresie + druga oś Y + zakres „od–do” | W-08 | [`ObjectMeasurementsChart.tsx`](../../frontend/src/components/objects/ObjectMeasurementsChart.tsx) | M |
| 14 | Dostępność `DataTable`: nagłówek jako przycisk, wiersz z klawiatury, `getRowKey` | W-16 | [`DataTable.tsx`](../../frontend/src/components/ui/DataTable.tsx) | S |
| 15 | Zakładka „Gateway” w widoku obiektu (stan modemu, wersja konfiguracji, historia łączności — §2.8.2) | — | [`ObjectDetailPage.tsx`](../../frontend/src/pages/ObjectDetailPage.tsx) | M |
| 16 | Eksport danych z widoku obiektu (`UC-05`) | — | [`ObjectDetailPage.tsx`](../../frontend/src/pages/ObjectDetailPage.tsx) | M |
| 17 | Rozstrzygnięcie losu `DashboardPage`/`ObjectsStatusTable` (usunąć albo przywrócić trasę) | — | [`DashboardPage.tsx`](../../frontend/src/pages/DashboardPage.tsx) | S |

### Poziom 3 — wysoka wartość, wysoki koszt (wymaga backendu)

| # | Zmiana | Wzorzec | Zależność | Koszt |
|---|---|---|---|---|
| 18a | Cztery kody uprawnień do alarmów w katalogu backendu + lustro we froncie ([§6.7](#67-uprawnienia--brakujące-kody-bez-których-ekranu-nie-da-się-zbudować)) | — | poprzedza poz. 18 | S |
| 18 | Widok alarmów wg [§6](#6-projekt-widoku-alarmów) | W-09…W-13, W-15 | moduł alarmów w backendzie + poz. 18a | L |
| 19 | Wariant mobilny listy alarmów | W-16 | poz. 18 | M |
| 20 | Kreator reguł alarmowych | W-14, W-15 | moduł alarmów w backendzie | M |
| 21 | Kreator dodania obiektu w krokach | W-17 | brak (API istnieje) | M |
| 22 | Strona „Raporty” dla roli zarządu | — | agregaty po stronie API | M |

### Poziom 4 — odłożone świadomie

| Zmiana | Warunek, przy którym wraca |
|---|---|
| Mapa obiektów (W-19) | drugi klient z siecią rozproszoną na kilkadziesiąt km |
| Kod QR przy parowaniu gatewaya (W-18) | powstanie widoku mobilnego (B-12) i przekroczenie ~10 wdrożeń |
| Inhibicja alarmów (W-20) | gdy grupowanie z W-12 przestanie wystarczać |
| Masowa aktualizacja alarmów (W-22) | pojedyncze fale powyżej kilkunastu alarmów |
| Widżet agregatu regionalnego (W-21) | obsługa wielu gmin z poziomu jednego konta |

---

## 8. Korekty do istniejących dokumentów

Rzeczy znalezione przy tej analizie, które korygują albo uzupełniają dokumentację — do rozstrzygnięcia przez właściciela produktu, nie zmienione przeze mnie samodzielnie:

1. **[§2.8.1](../business/01_plan_biznesowy.md) wymaga na dashboardzie „aktualnej temperatury, ciśnienia i przepływu”, a przepływ nie ma gdzie się pojawić.** [`ObjectsTable`](../../frontend/src/components/objects/ObjectsTable.tsx#L81-L101) ma kolumny zaszyte pod dwa typy kanałów (`pressure`, `temperature`); [`ObjectCard`](../../frontend/src/components/objects/ObjectCard.tsx#L119-L131) pokazuje pierwsze dwa punkty pomiarowe niezależnie od typu, ale bez jakości i czasu pomiaru. Wymaganie i implementacja rozjeżdżają się w dwóch miejscach naraz: brakuje przepływu i brakuje metadanych wymaganych przez §2.4.3 (poz. 10–11 backlogu).
2. **[§2.5](../business/01_plan_biznesowy.md) nie przewiduje grupowania, wyciszania ani inhibicji.** Katalog z §2.6 przy jednym zaniku zasilania generuje cztery alarmy, co przekracza próg EEMUA 191 (5 alarmów na operatora na godzinę) przy jednym zdarzeniu na jednym obiekcie. Rekomendacja: dopisać do §2.5 grupowanie po wspólnej przyczynie i wyciszanie na okno serwisowe jako wymagania MVP, a nie Phase 2.
3. **ISA 18.2 formułuje regułę, której warto użyć wprost w §2.6:** alarm niewymagający reakcji operatora ma być zdarzeniem informacyjnym. Nasz katalog już rozdziela §2.6.1–2 od §2.6.3, ale nie mówi, że to rozdzielenie ma być egzekwowane przy dodawaniu każdej nowej reguły.
4. **[`frontend-architecture.md` §10](../technical/frontend/frontend-architecture.md)** („Responsywność i dostępność”) stwierdza, że konwencje żyją w komponentach `components/ui/`. Audyt z [§2.8](#28-wymiar-8--praca-na-telefonie) pokazuje, że w `DataTable` tych konwencji nie ma (brak obsługi klawiatury, brak przewijania poziomego). Sekcja wymaga uzupełnienia o minimalne wymagania: cel dotykowy 44 px, tabela przewijalna, element interaktywny osiągalny z klawiatury.
5. **Typ [`ObjectSummary['status']`](../../frontend/src/types/telemetry.ts#L20) nie zawiera `'alarm'`, choć [`statusConfig.ts`](../../frontend/src/lib/statusConfig.ts) tę wartość definiuje i obsługuje.** Do uzgodnienia z kontraktem API — jeśli backend zwraca `alarm`, typ jest błędny; jeśli nie zwraca, `statusConfig` obsługuje stan nieosiągalny. Nie zmieniałem, bo rozstrzygnięcie należy do warstwy kontraktu.
6. **Katalog uprawnień nie przewiduje alarmów.** [§2.7.3 planu](../business/01_plan_biznesowy.md) definiuje rolę „użytkownik operacyjny”, która „potwierdza alarmy i dodaje informacje dotyczące obsługi zdarzenia”, ale w `permission_catalog.py` i jego froncie ([`types/permissions.ts`](../../frontend/src/types/permissions.ts)) nie ma ani jednego kodu, który by to wyrażał. Cztery brakujące kody wraz z mapowaniem na role: [§6.7](#67-uprawnienia--brakujące-kody-bez-których-ekranu-nie-da-się-zbudować). Do dodania w backendzie **przed** implementacją ekranu.
7. **`DashboardPage` jest pokryty testami, ale nieosiągalny w aplikacji** ([§4.1](#41-w-01--ekran-startowy-pokazuje-wyjątki)). Zestaw testów raportuje sprawność ekranu, do którego nie prowadzi żadna trasa. Niezależnie od tego, czy strona wróci czy zniknie, ten stan powinien zostać rozstrzygnięty, bo fałszuje obraz pokrycia testami.

---

## 9. Źródła

Wszystkie dostępy: **2026-09-02**. Etykiety: `[dok]` dokumentacja produktu, `[std]` norma/wytyczna, `[art]` opracowanie trzeciej strony, `[mkt]` materiał marketingowy producenta.

> **Zastrzeżenie metodyczne:** ze względu na ograniczenie egress opisane w [§0.1](#01-metoda-i-jej-twarde-ograniczenia) treść tych stron była dostępna wyłącznie przez streszczenia wyszukiwarki, a nie przez bezpośrednie otwarcie strony ani przez zalogowanie się do produktu. Adresy są podane po to, żeby dało się je zweryfikować przy uzupełnianiu biblioteki zrzutów.

### Wod-kan i smart water

| # | Źródło | Typ |
|---|---|---|
| Ź-01 | Inventia, *DataPortal — Jak wizualizacja danych może ułatwić Twoją pracę?* — https://www.inventia.pl/dataportal-jak-wizualizacja-danych-moze-ulatwic-twoja-prace/ | `[mkt]` |
| Ź-02 | Dataportal, *Applications* — https://dataportal.pl/en/applications/ | `[mkt]` |
| Ź-03 | AquaRD, *SCADA — system wizualizacji procesów* — https://aquard.pl/scada/ | `[mkt]` |
| Ź-04 | AquaRD, *HydraNet Expert* — https://aquard.pl/hydranet-expert/ | `[mkt]` |
| Ź-05 | Hawle, *Hawle.live CAP — monitorowanie hydrantów podziemnych* — https://www.hawle.com/pl/hawle-knowledge/systemy-i-rozwiazania/hawle-live-cap-rewolucja-w-monitorowaniu-hydrantow-podziemnych-na-przykladzie-hydrantu-uno | `[mkt]` |
| Ź-06 | Hawle, *Monitoring sieci wodociągowej* — https://www.hawle.com/Monitoring_sieci_wodocigowej | `[mkt]` |
| Ź-07 | Kallipr, *Kallipr Kloud Fleet — IoT Device Management* — https://kallipr.com/product/kallipr-kloud-fleet/ | `[mkt]` |
| Ź-08 | Kallipr, *Water Utilities* — https://kallipr.com/industries/water-utilities/ | `[mkt]` |
| Ź-09 | HWM Global, *DataGate* — https://www.hwmglobal.com/datagate/ | `[mkt]` |
| Ź-10 | HWM Global, *DataGate2 — Introduction for Users and Administrators* (MAN-130-0015-A, PDF) — https://www.hwmglobal.com/uploads/manuals/DataGate2/MAN-130-0015-A%20DataGate2%20Introduction%20for%20Users%20and%20Administrators.pdf | `[dok]` |
| Ź-11 | Ayyeka, *Dashboard Widgets* (baza wiedzy) — https://www.ayyeka.com/en/knowledge/dashboard-widgets | `[dok]` |
| Ź-12 | Ayyeka, *FAI Software Versions* — https://www.ayyeka.com/en/knowledge/fai-software-versions | `[dok]` |

### Przemysłowy monitoring aktywów i SCADA w chmurze

| # | Źródło | Typ |
|---|---|---|
| Ź-13 | Inductive Automation, *Quality Codes and Overlays* (Ignition User Manual) — https://www.docs.inductiveautomation.com/docs/8.1/platform/tags/quality-codes-and-overlays | `[dok]` |
| Ź-14 | Inductive Automation, *Perspective* (Ignition User Manual) — https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/perspective | `[dok]` |
| Ź-15 | Corso Systems, *5 Advanced Responsive Design Tips For Perspective* — https://corsosystems.com/posts/5-responsive-design-tips-for-perspective | `[art]` |
| Ź-16 | NFM Consulting, *HMI Design Best Practices for Industrial Operators* — https://nfmconsulting.com/knowledge/hmi-design-best-practices/ | `[art]` |
| Ź-17 | AVEVA, *Insight — Industrial Cloud Platform for Operations* — https://www.aveva.com/en/products/insight/ | `[mkt]` |
| Ź-18 | AVEVA, *Insight* (broszura PDF) — https://www.aveva.com/content/dam/aveva/documents/brochures/Brochure_AVEVA_Insight_23-07.pdf | `[mkt]` |
| Ź-19 | ThingsBoard, *Alarms Table* (widget reference) — https://thingsboard.io/docs/pe/reference/widgets/alarm-widgets/alarms-table/ | `[dok]` |
| Ź-20 | ThingsBoard, *Working with alarms* — https://thingsboard.io/docs/user-guide/alarms/ | `[dok]` |
| Ź-21 | ThingsBoard, *Alarm rules* — https://thingsboard.io/docs/user-guide/alarm-rules/ | `[dok]` |
| Ź-22 | ThingsBoard, *Claiming devices* — https://thingsboard.io/docs/user-guide/claiming-devices/ | `[dok]` |
| Ź-23 | ThingsBoard, *Lesson 4. Alarm management* — https://thingsboard.io/docs/pe/user-guide/advanced-guides-for-working-with-dashboard/advanced-dashboard-guide-lesson-4/ | `[dok]` |

### Monitoring i obserwowalność IT

| # | Źródło | Typ |
|---|---|---|
| Ź-24 | Grafana Labs, *No Data and Error states* — https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rule-evaluation/nodata-and-error-states/ | `[dok]` |
| Ź-25 | Grafana Labs, *Handle missing data in Grafana Alerting* — https://grafana.com/docs/grafana/latest/alerting/guides/missing-data/ | `[dok]` |
| Ź-26 | Grafana Labs, *Labels and annotations* — https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rules/annotation-label/ | `[dok]` |
| Ź-27 | Grafana Labs, *Configure silences* — https://grafana.com/docs/grafana/latest/alerting/configure-notifications/create-silence/ | `[dok]` |
| Ź-28 | Grafana Labs, *New tools to resolve incidents faster and avoid alert fatigue* (blog) — https://grafana.com/blog/2024/05/14/grafana-alerting-new-tools-to-resolve-incidents-faster-and-avoid-alert-fatigue/ | `[art]` |
| Ź-29 | Zabbix, *Monitoring → Problems* — https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/monitoring/problems | `[dok]` |
| Ź-30 | Zabbix, *Problem acknowledgment* — https://www.zabbix.com/documentation/current/en/manual/acknowledgment | `[dok]` |
| Ź-31 | Zabbix, *Problem suppression* — https://www.zabbix.com/documentation/current/en/manual/acknowledgment/suppression | `[dok]` |
| Ź-32 | Prometheus, *Alertmanager* — https://prometheus.io/docs/alerting/latest/alertmanager/ | `[dok]` |
| Ź-33 | OneUptime, *How to Use Alertmanager Inhibition Rules* — https://oneuptime.com/blog/post/2026-01-27-alertmanager-inhibition-rules/view | `[art]` |
| Ź-34 | Datadog, *Monitor Status Page* — https://docs.datadoghq.com/monitors/status/status_page/ | `[dok]` |
| Ź-35 | Datadog, *Downtimes* — https://docs.datadoghq.com/monitors/downtimes/ | `[dok]` |
| Ź-36 | PagerDuty, *Mobile App* — https://support.pagerduty.com/main/docs/mobile-app | `[dok]` |
| Ź-37 | PagerDuty, *Navigate the Incidents Page* — https://support.pagerduty.com/main/docs/navigate-the-incidents-page | `[dok]` |

### Normy, wytyczne i wzorce ogólne

| # | Źródło | Typ |
|---|---|---|
| Ź-38 | EEMUA, *Publication 191 — Alarm systems: a guide to design, management and procurement* — https://www.eemua.org/products/publications/digital/eemua-publication-191 | `[std]` |
| Ź-39 | ISA, *Alarm management questions that everyone asks* (InTech) — https://www.isa.org/intech-home/2020/march-april/features/alarm-management-questions-that-everyone-asks | `[std]` |
| Ź-40 | Industrial Monitor Direct, *Industrial Alarm System Standards: IEC 62682, ISA 18.2 and EEMUA 191* — https://industrialmonitordirect.com/blogs/knowledgebase/industrial-alarm-system-standards-iec-62682-isa-182-and-eemua-191 | `[art]` |
| Ź-41 | Control.com, *Going Gray: A New HMI Standard* — https://control.com/technical-articles/going-gray/ | `[art]` |
| Ź-42 | HMI Library, *ISA-101 HMI Design Standard: A Guide* — https://hmilibrary.com/standards/isa-101 | `[art]` |
| Ź-43 | OPC Foundation, *UA Part 8: DataAccess — Data and error mapping* — https://reference.opcfoundation.org/v104/Core/docs/Part8/A.4.3/ | `[std]` |
| Ź-44 | Software Toolbox, *OPC DA Quality Codes* — https://help.softwaretoolbox.com/faq/414 | `[dok]` |
| Ź-45 | W3C/WCAG 2.2, *SC 1.4.1 Use of Color* (omówienie) — https://www.thewcag.com/criteria/1.4.1 | `[std]` |
| Ź-46 | Azure IoT Central — *Configure rules and email alerts based on device telemetry* (omówienie) — https://oneuptime.com/blog/post/2026-02-16-how-to-configure-rules-and-email-alerts-in-azure-iot-central-based-on-device-telemetry/view | `[art]` |
| Ź-47 | Datacake, *IoT Rule Engine* — https://datacake.co/iot-rule-engine-lorawan-mqtt-sms-email-alerting | `[mkt]` |
| Ź-48 | eLynx, *Water Utility SCADA* — https://water.elynxtech.com/solutions/water-utility-scada | `[mkt]` |

### Źródła wewnętrzne

- [`docs/business/01_plan_biznesowy.md`](../business/01_plan_biznesowy.md) §2.3, §2.4.3, §2.5, §2.6, §2.7, §2.8, §5.2
- [`docs/business/CONTEXT.md`](../business/CONTEXT.md) — słownik pojęć
- [`docs/technical/frontend/frontend-architecture.md`](../technical/frontend/frontend-architecture.md)
- Kod: `frontend/src/` — stan gałęzi `claude/analiza-ux-ui-konkurencji-vharpb` z 2026-09-02
