# Briefy dla agentów — gotowe instrukcje do zlecenia


Każdy brief jest samodzielny — można go skopiować w całości jako prompt dla agenta. Sekcja **„Decyzje już podjęte"** istnieje po to, żeby agent nie zawracał głowy pytaniami, na które odpowiedź już padła.

**Każdy brief jest w pełni autonomiczny: agent nie zadaje pytań w trakcie realizacji.** Tam, gdzie mogła się pojawić potrzeba zapytania (niejednoznaczny wybór projektowy, brak informacji), brief albo podaje jawną decyzję/domyślne zachowanie, albo instruuje agenta, żeby wybrał sam i **udokumentował uzasadnienie w deliverable/PR** — nie żeby czekał na odpowiedź. Jedyny dopuszczalny „przystanek" to koniec zadania: gotowy dokument, gotowy branch z kodem, gotowe szkice do przeglądu. Żaden brief nie zakłada dialogu w trakcie pracy.



### Ustalenia wspólne dla wszystkich briefów

Padły w rundzie pytań i są już wbudowane w poszczególne briefy — tu zebrane, bo dotyczą więcej niż jednego zlecenia:

| Ustalenie | Dotyczy |
|---|---|
| **Skala: kilka prototypów**, brak planów skalowania na teraz — nie licz opłacalności na zmyślonym wolumenie, licz **próg** | B-01, B-10 |
| **Czujniki wkręcane w rurociąg wody pitnej** → ścieżka atestów PZH jest w zakresie | B-01, B-05 |
| **Pierwszy klient w małopolskim lub podkarpackim**, gmina pozostaje anonimowa | B-13 |
| **Refaktor działającego firmware pod testowalność dozwolony bez ograniczeń**, weryfikacja na płytce raz na końcu | B-06 |
| **Rynek: Polska.** Brak analiz eksportowych poza UE | B-01, B-13 |
| **Dokumenty po polsku**, jak reszta `docs/` | wszystkie |
| **Transmisja co ~60 s** (`WINDOWS_PER_BATCH=4` × `WINDOW_SECONDS=15`), bufor RAM ≈ 12 minut, brak deep sleep | B-08, B-11 |
| **Migracje danych zawsze projektowane jako zero-downtime** (addytywna migracja schematu → backfill w tle, batchami, wznawialny → dopiero potem przełączenie odczytów) — niezależnie od tego, czy środowisko produkcyjne akurat coś przyjmuje. To domyślna dyscyplina inżynierska, nie decyzja do konsultacji za każdym razem | B-09 |
| **`prepare-work` (z fazą `grill-me` i wbudowanymi przystankami na przegląd) nie jest używany w żadnym briefie** — wszystkie wieloetapowe zlecenia idą jako ciągły przebieg: agent projektuje → dokumentuje wybór → implementuje → sam sobie robi code review (`code-reviewer`) w tej samej sesji, bez czekania na akceptację między etapami | B-08, B-09 |

---

## B-01 🟡 Certyfikacja i wymagania przed sprzedażą gminie

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b01-certyfikacja` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `explorer` (WebSearch + WebFetch) → `documentation-writer`
**Czas:** duży research, 1 sesja
**Przeczytaj najpierw:** [`01_plan_biznesowy.md` §4.2.2](../business/01_plan_biznesowy.md) (BOM i warianty sprzętowe), [§6.1](../business/01_plan_biznesowy.md) (NIS2/KSC), [§6.2.1](../business/01_plan_biznesowy.md) (ryzyko „urządzenie prototypowe"), [`01_hardware.md`](../technical/firmware/01_hardware.md)

### Kontekst

Produkt ma trafić do gminy — podmiotu publicznego, potencjalnie objętego NIS2/KSC jako operator infrastruktury krytycznej (woda pitna). Dziś gateway to **zestaw deweloperski ESP32-S3-DevKitC-1 + moduł HAT KAmod z A7670E**, zasilany z zewnętrznego 5 V, bez obudowy, bez ochrony przepięciowej. Plan biznesowy sam nazywa to ryzykiem („zestaw deweloperski może nie spełniać wymagań środowiskowych i niezawodnościowych w terenie"). Nie ma żadnego dokumentu opisującego, co formalnie trzeba spełnić, zanim urządzenie zawiśnie w szafie w hydroforni.

### Zakres

Analiza ma objąć **trzy warianty sprzętowe** i dla każdego rozstrzygnąć te same pytania:

| Wariant | Opis |
|---|---|
| **W1 — obecny PoC** | ESP32-S3-DevKitC-1 + KAmod A7670E HAT + MAX31865 + ADS1015, montaż własny |
| **W2 — gotowy modem RS485** | USR-DR154-E (modem 4G LTE RS485, montaż DIN, ~78 zł) jako gotowy moduł z własnym CE + czujniki Modbus/4-20 mA |
| **W3 — przemysłowy ESP32** | Gotowa płytka przemysłowa na ESP32 w obudowie DIN (agent ma znaleźć 2–3 konkretne modele dostępne w PL/UE, z cenami) |

Dla każdego wariantu ustal:

1. **Które dyrektywy UE mają zastosowanie** — EMC (2014/30/UE), LVD (2014/35/UE), RED (2014/53/UE dla części radiowej), RoHS, WEEE. Wskaż, które są aktywowane przez *co* w zestawie.
2. **Czy zestawienie modułów z własnym CE tworzy nowy wyrób** wymagający własnej deklaracji zgodności — i **gdzie dokładnie przebiega granica** między „montażem instalacji u klienta" (nie tworzy wyrobu) a „wprowadzeniem wyrobu do obrotu" (tworzy). To jest kluczowe pytanie całej analizy.
3. **Co konkretnie trzeba wytworzyć** w każdym scenariuszu: deklaracja zgodności UE, dokumentacja techniczna, analiza ryzyka, instrukcja użytkownika w języku polskim, oznakowanie.
4. **Koszt i czas badań laboratoryjnych** (EMC, ewentualnie bezpieczeństwo) — realne stawki polskich/europejskich laboratoriów notyfikowanych, rzędy wielkości wystarczą, ale podaj źródła.
5. **Wymagania sektorowe poza CE**: NIS2/KSC w roli **dostawcy** podmiotu kluczowego (co gmina będzie musiała od Ciebie wymagać kontraktowo) oraz **atesty higieniczne PZH** — patrz osobna sekcja niżej.
6. **Ubezpieczenie OC** za produkt/działalność — czy i w jakim zakresie potrzebne przy sprzedaży do JST.

### Pytanie nadrzędne — instalacja pilotażowa, nie produkcja seryjna

**To jest najważniejsze pytanie tej analizy i ma trafić na początek dokumentu.** Skala na najbliższy okres to **kilka prototypów u pierwszego klienta**, bez planów seryjnej produkcji. Zanim więc policzysz cokolwiek o CE dla wyrobu, rozstrzygnij:

- Czy pojedyncza instalacja pilotażowa/testowa u klienta w ogóle stanowi **„wprowadzenie do obrotu"** w rozumieniu przepisów, czy mieści się w innej kategorii (urządzenie prototypowe, instalacja badawcza, sprzęt na potrzeby własne dostawcy usługi)?
- **Czy zmienia to cokolwiek, że gmina płaci fakturę?** Sprawdź, czy odpłatność przesądza o wprowadzeniu do obrotu, i czy alternatywne modele (użyczenie sprzętu na czas pilotażu, sprzedaż samej usługi monitoringu z urządzeniem pozostającym Twoją własnością) zmieniają obowiązki. **Uwaga:** [ADR-0003](../business/adr/0003-revenue-model-hardware-plus-subscription.md) zakłada dziś, że sprzęt kupuje gmina i jest jego właścicielem — jeśli model użyczenia istotnie upraszcza formalności na etapie pilotażu, zgłoś to jako rekomendację zmiany ADR, nie zakładaj jej samodzielnie.
- Jaki jest **realny próg**, po przekroczeniu którego trzeba przejść na pełną ścieżkę wyrobu — liczony w sztukach, w klientach, albo w charakterze działalności.

Dopiero po tym rozstrzygnięciu przechodź do porównania ścieżek dla większej skali.

### Atesty PZH — w zakresie, potwierdzone

Czujniki są **wkręcane bezpośrednio w rurociąg wody pitnej** (PT-506 ma gwint 1/4" G). To aktywuje osobną ścieżkę: wymagania dla wyrobów kontaktujących się z wodą przeznaczoną do spożycia. Ustal:

- Które elementy faktycznie stykają się z medium (czujnik, króciec, uszczelnienie, ewentualna tuleja osłonowa dla PT100).
- Czy atest higieniczny PZH (lub odpowiednik) jest wymagany prawnie, czy tylko oczekiwany kontraktowo przez ZWiK.
- **Kto jest odpowiedzialny** — producent czujnika czy Ty jako integrator instalacji. Sprawdź, czy kupowane czujniki mają już atest, i co się dzieje, gdy nie mają.
- Czy da się tego uniknąć montażem nieinwazyjnym (czujnik temperatury na powierzchni rury, ciśnienie z istniejącego króćca manometrycznego) — i ile to kosztuje w dokładności pomiaru. To może być tańsza droga niż zdobywanie atestów.

### Decyzje już podjęte

- **Skala: kilka prototypów, brak planów skalowania na teraz.** Nie licz opłacalności certyfikacji „na sztukę" przy założonym wolumenie — zamiast tego policz **próg**: przy ilu urządzeniach/klientach która ścieżka zaczyna się opłacać. Priorytet dokumentu to odpowiedź na „co muszę zrobić, żeby legalnie postawić pierwsze kilka sztuk u klienta".
- **Czujniki mają kontakt z wodą pitną** — PZH jest w zakresie, nie pomijaj tego wątku.
- **Rynek: Polska.** Nie analizuj wymagań eksportowych poza UE.
- **Rola prawna nie jest przesądzona** — analiza ma ją zarekomendować, ale z uwzględnieniem realnej skali (patrz wyżej).
- System jest read-only, nie steruje procesem — wykorzystaj to, bo obniża klasę ryzyka.

### Ograniczenia

- **To nie jest porada prawna.** Wszystkie ustalenia oznacz jako wymagające potwierdzenia przez prawnika/jednostkę notyfikowaną, i zbierz na końcu listę pytań do zadania specjaliście.
- Każde twierdzenie o wymogu prawnym musi mieć **link do źródła** (tekst dyrektywy, strona UOKiK/PIH, wytyczne Komisji Europejskiej). Bez źródła → oznacz jako **przypuszczenie**.

### Deliverable

`docs/business/04_certyfikacja_i_zgodnosc.md` zawierający: **na początku** rozstrzygnięcie kwestii instalacji pilotażowej, dalej tabelę wariant × dyrektywa × obowiązek, ścieżkę PZH, próg skali przełączający ścieżki, szacunek kosztów wejścia dla każdego wariantu, checklistę „co musi istnieć zanim pierwsze urządzenie trafi do gminy", listę pytań do prawnika.

### Definicja ukończenia

Da się odpowiedzieć na pytanie **„czy mogę dziś legalnie zamontować W1 u pierwszego klienta i wystawić fakturę"** — a jeśli nie, wiadomo dokładnie czego brakuje, ile to kosztuje i czy zmiana modelu (użyczenie zamiast sprzedaży) omija problem.

---

## B-02 🟢 Analiza technologiczna i sprzętowa konkurencji — cały system (nie UX)

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b02-analiza-technologiczna-konkurencji` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `explorer` (WebSearch + WebFetch, dużo) → `documentation-writer`
**Przeczytaj najpierw:** [`01_plan_biznesowy.md` §5.2](../business/01_plan_biznesowy.md) (pełna analiza konkurencji — **już istnieje**, nie powtarzaj jej), [`CONTEXT.md`](../business/CONTEXT.md), [`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md), [`01_hardware.md`](../technical/firmware/01_hardware.md)
**Rozgraniczenie:** warstwa UX/UI/grafika to osobne zlecenie — **B-03**. Jeśli oba są realizowane, uzgodnij z nim granicę: B-02 bada *jak to jest zbudowane pod spodem — firmware, sprzęt, backend, cały system*, B-03 bada *jak to wygląda i jak się tego używa*.

### Kontekst

To jest zlecenie „przeczytaj moje dokumenty biznesowe, zrób dokładną analizę technologii i systemu, jak coś takiego robi konkurencja w Polsce i na świecie, zbierz najlepsze rozwiązania" — rozpisane na konkretny zakres. Analiza **biznesowa** konkurencji już istnieje (§5.2 planu — pozycjonowanie, ceny, mocne i słabe strony). To zlecenie dokłada warstwę techniczną obejmującą **cały system, nie tylko backend**: architekturę firmware, dobór i integrację sprzętu, oraz architekturę chmury/backendu konkurentów — i co z tego warto przenieść do własnego produktu. Warstwa UX/UI/grafika to osobne zlecenie (B-03) — nie wchodź w nią tutaj.

### Zakres

Dla każdego z badanych podmiotów ustal, **jak to jest zrobione pod spodem** — nie co obiecuje marketing:

**Konkurenci polscy (z §5.2, nie szukaj nowych):** Inventia (+ DataPortal), AquaRD (CellBOX), UniCloud/Unitronics, Hawle.live, AIUT WaterPrime.
**Wzorce światowe (tu szukaj szeroko, to jest cel zlecenia):** Kallipr Kloud, oraz min. 5 innych zagranicznych platform smart-water / industrial IoT o modelu zbliżonym do naszego (kandydaci do sprawdzenia: Ayyeka, Metasphere, HWM Water, Xylem/Sensus, Itron, Ovarro/Servelec, Nivus, Telit, Golioth, Blues Wireless, Balena — agent ma zweryfikować, które są faktycznie porównywalne, i odrzucić resztę z uzasadnieniem).

Wymiary analizy — te same dla wszystkich, żeby dało się porównać:

1. **Architektura sprzętowa gatewaya** — własny moduł czy złożenie z gotowych komponentów (jak nasz PoC), przemysłowy czy deweloperski poziom wykonania, obudowa i stopień IP, zasilanie (sieciowe/bateryjne/solarne), zakres temperatur pracy, ochrona przepięciowa. To wymiar, którego typowa analiza „tylko software" pomija — a bezpośrednio zasila naszą własną ocenę wariantów sprzętowych (patrz B-01, B-10, B-11).
2. **Obsługiwane interfejsy pomiarowe** — Modbus RTU/TCP, 4-20 mA, 0-10 V, wejścia cyfrowe/impulsowe — i jak szeroki jest realny katalog, nie deklaracja marketingowa.
3. **Protokół transmisji urządzenie ↔ chmura** — HTTP/MQTT/CoAP/LwM2M/Sparkplug B; czy publikują specyfikację.
4. **Model tożsamości i provisioningu urządzenia** — klucz współdzielony, certyfikat X.509, TPM/secure element, kod aktywacyjny, QR. Jak wygląda pierwsze uruchomienie w terenie (ile kroków, czy potrzebny laptop).
5. **Format telemetrii** — surowe próbki vs. okna agregowane, obsługa jakości danych, znaczniki czasu, idempotencja/deduplikacja.
6. **Konfiguracja bez rekompilacji** — czy mają „profile urządzeń" (obietnica z [ADR-0002](../business/adr/0002-pragmatic-integration-strategy.md)), jak wygląda mapowanie rejestrów Modbus, czy da się to zrobić z przeglądarki.
7. **OTA i zarządzanie flotą** — mechanizm aktualizacji, kanały wydawnicze, rollback, zarządzanie SIM.
8. **Model danych i retencja** — czy używają TSDB (InfluxDB/Timescale) czy zwykłego SQL, jak długo trzymają dane, czy robią downsampling.
9. **Model alarmów** — gdzie ewaluowane (gateway vs. chmura), jakie typy reguł, jak radzą sobie z zalewem alarmów.
10. **API i integracje** — czy jest publiczne API, REST/GraphQL, webhooki, integracja z SCADA/GIS.
11. **Bezpieczeństwo** — co publicznie deklarują (certyfikaty ISO, pen-testy, zarządzanie podatnościami, disclosure policy).

### Metoda

Źródła w kolejności wiarygodności: dokumentacja techniczna i developerska producenta → karty katalogowe i instrukcje PDF → whitepapery → materiały marketingowe (najsłabsze). **Każde ustalenie z etykietą źródła i poziomem pewności.** Tam, gdzie informacji nie ma publicznie, napisz wprost „nieujawnione" — nie zgaduj.

### Decyzje już podjęte

- Nie powtarzaj analizy UX ani analizy biznesowej — te istnieją (a UX ma swoje osobne zlecenie, B-03). Jeśli natrafisz na coś, co je koryguje, dopisz osobną sekcję „korekty do istniejących analiz", nie przepisuj ich.
- Zakres światowy jest **celem, nie dodatkiem** — połowa wartości tego zlecenia leży w podmiotach spoza Polski.
- **Dokument po polsku**, jak reszta dokumentacji. Terminy techniczne i nazwy własne zostawiaj w oryginale.
- **Tylko źródła publicznie dostępne.** Żadnych płatnych raportów branżowych, żadnych rejestracji na demo w celu zdobycia materiałów.
- Platformy ogólnego przeznaczenia (device management typu Golioth, Blues, Balena, Telit) potraktuj jako **osobną sekcję**, nie mieszaj ich do tabeli z konkurentami wod-kan. One nie są konkurencją — są potencjalnym wzorcem inżynierskim albo wręcz komponentem do kupienia zamiast budowania. Odpowiedz przy okazji na pytanie: czy któryś z tych gotowych mechanizmów (provisioning, OTA, zarządzanie flotą) opłaca się wziąć z półki zamiast pisać samodzielnie.

### Deliverable

`docs/analysis/02_analiza_technologiczna_konkurencji.md`: tabela porównawcza (podmiot × 11 wymiarów), sekcja „co warto skopiować" z uzasadnieniem i szacunkiem kosztu wdrożenia u nas, sekcja „czego świadomie nie kopiujemy i dlaczego", oraz **lista konkretnych zmian do rozważenia w naszej architekturze** (firmware, hardware i backend) z odniesieniem do istniejących plików.

### Definicja ukończenia

Dla każdego z 11 wymiarów da się powiedzieć, gdzie nasz system stoi względem rynku: z tyłu, na poziomie, czy z przodu — i co konkretnie by to zmieniło.

---

## B-03 🟡 Analiza UX/UI konkurencji i wzorce dla interfejsu

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b03-analiza-ux-konkurencji` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `explorer` (WebSearch + WebFetch, plus przeglądarka do zrzutów) → `documentation-writer`
**Przeczytaj najpierw:** [`01_plan_biznesowy.md` §2.3](../business/01_plan_biznesowy.md) (przypadki użycia UC-01…UC-05), [§2.7](../business/01_plan_biznesowy.md) (użytkownicy operacyjni i role), [§2.8](../business/01_plan_biznesowy.md) (zakres aplikacji — dashboard, widok obiektu, widok alarmów, konfiguracja), [`CONTEXT.md`](../business/CONTEXT.md) (słownik — używaj tych terminów), [`frontend-architecture.md`](../technical/frontend/frontend-architecture.md), oraz istniejący kod w [`frontend/src/pages/`](../../frontend/src/pages/) i [`frontend/src/components/`](../../frontend/src/components/)
**Rozgraniczenie:** warstwa techniczna (firmware, sprzęt, backend) to osobne zlecenie — **B-02**. Ten brief bada wyłącznie *jak to wygląda i jak się tego używa*.

### Kontekst

Frontend jest już zbudowany — 20 stron, własna biblioteka komponentów (`DataTable`, `StatusPill`, `FreshnessBar`, `Drawer`, `Dialog`), React 19 + Tailwind. Powstał jednak **bez systematycznego benchmarku** tego, jak podobne systemy rozwiązują te same problemy. Jednocześnie plan biznesowy stawia interfejsowi bardzo konkretne wymagania, których dziś nikt nie zweryfikował względem rynku:

- dashboard ma odpowiadać na jedno pytanie: **„który obiekt wymaga uwagi i dlaczego?"** (§2.8.1),
- wartość pomiaru **nigdy nie może być pokazana bez czasu i statusu jakości** (§2.4.3) — to twardy niezmiennik produktowy, nie preferencja estetyczna,
- widok alarmów ma obsłużyć pełny cykl: potwierdzenie, komentarz, zamknięcie, oznaczenie jako fałszywy, przejście do wykresu z okresem przed i po zdarzeniu (§2.8.3),
- trzy różne role o różnych potrzebach: pracownik terenowy (telefon, pytanie „czy jechać"), dyspozytor (pełny obraz), zarząd (agregaty).

To zlecenie ma zebrać wzorce z rynku i przełożyć je na **konkretne decyzje dla naszego interfejsu** — nie na ogólny przegląd ładnych ekranów.

### Zakres — kogo badać

**Nie ograniczaj się do wod-kan.** Najlepsze wzorce dla tego typu produktu pochodzą z trzech sąsiadujących kategorii i warto wziąć po kilka z każdej:

1. **Wod-kan i smart water** — polskie i zagraniczne platformy monitoringu sieci wodociągowej.
2. **Przemysłowy monitoring aktywów i SCADA w chmurze** — bo tam rozwiązano problem „setki punktów, który wymaga uwagi".
3. **Ogólny monitoring i obserwowalność** (narzędzia do monitoringu infrastruktury IT) — bo tam najlepiej dopracowano listy alarmów, triage, wyciszanie i eskalację. Ta kategoria jest często pomijana, a ma najwięcej do zaoferowania w warstwie alarmowej.

Agent sam dobiera konkretne produkty i **uzasadnia wybór** — kryterium jest porównywalność problemu, nie popularność marki. Minimum 8 produktów, z czego co najmniej 4 przeanalizowane szczegółowo (pełne ekrany, nie same zrzuty marketingowe).

### Zakres — co badać

Dla każdego produktu, te same wymiary, żeby dało się porównać:

1. **Ekran startowy** — co widać w pierwszej sekundzie, jak zakomunikowany jest priorytet, czy dominuje lista, mapa, czy kafelki. Czy da się odpowiedzieć „co wymaga uwagi" bez klikania.
2. **Hierarchia nawigacji** — jak reprezentowane jest zagnieżdżenie „organizacja → obiekt → urządzenie → punkt pomiarowy" (u nas dokładnie taka struktura, patrz `CONTEXT.md`). Ile kliknięć do wartości pomiaru.
3. **Prezentacja pomiaru** — jak pokazują wartość razem z czasem i jakością danych, jak sygnalizują dane nieaktualne, jak pokazują przerwę w komunikacji na wykresie (u nas jest już `FreshnessBar` i `freshnessUtils` — sprawdź, czy nasze podejście ma odpowiednik na rynku).
4. **Statusy i kolor** — jaka paleta statusów, czy kolor jest jedynym nośnikiem znaczenia (nasz `statusConfig.ts` — sprawdź pod kątem dostępności), jak odróżniają „awaria obiektu" od „awaria telemetrii".
5. **Widok alarmów i triage** — filtry, przypisanie właściciela, potwierdzanie, komentarze, historia reakcji, wyciszanie, grupowanie powiązanych alarmów. **To najważniejszy wymiar tego zlecenia**, bo u nas widoku alarmów nie ma jeszcze wcale, więc wnioski trafią wprost do projektu.
6. **Wykresy i analiza historii** — zakresy czasu, porównywanie wielu punktów, zaznaczanie zdarzeń na osi, eksport.
7. **Konfiguracja progów i reguł** — jak niezaawansowany użytkownik ustawia próg alarmowy bez pisania wyrażeń.
8. **Praca na telefonie** — czy w ogóle, i co wtedy zostaje na ekranie (bezpośrednio zasila B-12).
9. **Onboarding i dodanie obiektu** — ile kroków od „mam urządzenie w ręku" do „widzę dane".

### Zakres — produkt końcowy

Materiał ma być praktyczny do dwóch różnych zastosowań naraz: głęboka analiza do pracy nad kodem (markdown) **i** szybki przegląd rekomendacji z przykładami do przeglądania bez czytania całego dokumentu (Artifact). Oba są obowiązkową częścią tego zlecenia, nie opcją.

1. **Katalog wzorców z werdyktem** — dla każdego zaobserwowanego wzorca jedna z trzech etykiet: **bierz** (i dlaczego pasuje do naszych przypadków użycia), **nie bierz** (i dlaczego to antywzorzec dla małej gminy), **rozważ** (z warunkiem, przy którym zaczyna mieć sens).
2. **Konfrontacja z naszym obecnym interfejsem** — dla każdego wzorca „bierz": co mamy dziś, co trzeba zmienić, w którym pliku. To jest sedno zlecenia. Wzorzec bez wskazania miejsca w kodzie jest niedokończoną robotą.
3. **Rekomendacja architektury informacji** — mapa nawigacji dopasowana do trzech ról z §2.7.2, z uzasadnieniem odstępstw od tego, co jest dziś.
4. **Projekt widoku alarmów** — opis ekranu, którego jeszcze nie ma, gotowy do przekazania jako wejście do implementacji (powiązanie: moduł alarmów w backendzie też jeszcze nie istnieje).
5. **Backlog zmian we froncie**, uszeregowany wg stosunku wartości do kosztu.
6. **Artifact z głównymi rekomendacjami** (HTML, publikowany narzędziem Artifact) — wizualny, samodzielny towarzysz markdownu, nie jego powtórzenie. Zanim zaczniesz go pisać, wczytaj skill `artifact-design`. Zawartość: 8–12 najważniejszych rekomendacji z punktu 2 (nie wszystkie z katalogu — tylko te o najwyższej wartości), każda z: krótkim opisem „co zmienić", **przykładem interfejsu** (zrzut ekranu konkurenta pokazujący wzorzec, osadzony jako `data:` URI zgodnie z zasadami Artifactów — bez linków do zewnętrznych hostów), i jednym zdaniem „co to znaczy dla naszego kodu" z odniesieniem do pliku. Format jak prezentacja rekomendacji do przeglądania w 5 minut, nie jak drugi raport.
7. **Szeroka biblioteka zrzutów jako osobna wartość, nie tylko dowód na tezę.** Oprócz zrzutów bezpośrednio cytowanych w katalogu wzorców, zbierz i zachowaj dodatkowe, ciekawe ekrany z badanych platform — rzeczy, które nie trafiają w żaden konkretny wzorzec z listy „co badać" wyżej, ale są interesującym pomysłem do przejrzenia. Celuj w realną liczbę, nie symboliczną: **orientacyjnie 30–60 zrzutów łącznie** ze wszystkich badanych produktów (nie tylko z 4 pogłębionych), nie tylko z tych bezpośrednio cytowanych w tekście. To ma być zasób do przeglądania, nie tylko materiał dowodowy.

### Decyzje już podjęte

- **Nie przeprojektowujemy aplikacji od zera.** Frontend działa; to jest analiza wskazująca ulepszenia, nie mandat na przepisanie. Rekomendacje mają się mieścić w istniejącym stosie (React + Tailwind + własne komponenty) i w istniejącej strukturze stron.
- **Dokument po polsku**, terminologia zgodna z [`CONTEXT.md`](../business/CONTEXT.md) — „obiekt wodociągowy", „punkt pomiarowy", „gateway", nie dowolne synonimy.
- **Tylko źródła publicznie dostępne** — dokumentacja produktów, publiczne dema, materiały producenta. Bez rejestrowania się na wersje próbne i bez płatnych raportów.
- **Zrzuty ekranu zapisuj do `docs/analysis/assets/`, szeroko, nie tylko te cytowane wprost** (patrz punkt 7 „Zakres — produkt końcowy") — ale **pilnuj rozmiaru repo**: kompresuj każdy zrzut do rozsądnego rozmiaru (orientacyjnie < 300 KB/plik, szerokość ok. 1600 px wystarcza do czytelności), format JPEG/WebP zamiast nieskompresowanego PNG tam, gdzie jakość na tym nie ucierpi.

### Ograniczenia

- **Każdy zrzut i każde twierdzenie z linkiem do źródła i datą.** Interfejsy zmieniają się między wersjami — analiza bez daty zestarzeje się niezauważalnie.
- Odróżniaj **materiał marketingowy** (wyidealizowany, często nieprawdziwy) od **dokumentacji produktu** i **realnego demo**. Oznacz, z czego pochodzi każdy wniosek.
- Nie oceniaj estetyki. Kryterium to skuteczność w realizacji naszych przypadków użycia, nie to, co ładniej wygląda.
- **Artifact musi być samodzielny** — obrazy osadzone jako `data:` URI, żadnych odwołań do zewnętrznych hostów (poza Google Fonts, jeśli w ogóle potrzebne). Zrzuty, które mają trafić do Artifactu, przygotuj w rozmiarze sensownym do osadzenia (nie oryginalne wielomegapikselowe pliki).

### Deliverable

`docs/analysis/01_analiza_ux_konkurencji.md` (pełna analiza) + zrzuty w `docs/analysis/assets/` (szeroka biblioteka, nie tylko cytowane) + Artifact z rekomendacjami (opublikowany narzędziem Artifact, link do niego dopisany na górze markdownu).

### Definicja ukończenia

Da się wskazać co najmniej pięć konkretnych, uzasadnionych zmian w naszym froncie (z nazwami plików) oraz mieć gotowy opis widoku alarmów na tyle szczegółowy, żeby dało się z niego zaimplementować ekran bez zgadywania. Artifact z rekomendacjami jest opublikowany i zawiera przykłady interfejsów przy każdej rekomendacji. Biblioteka zrzutów w `docs/analysis/assets/` ma realną objętość (rząd wielkości dziesiątek, nie pojedynczych plików).

### Zlecenia pokrewne (niezależne, nie sekwencyjne)

- **B-12** (widok mobilny) bada tę samą aplikację od strony responsywności. Wymiar 8 tego briefu („praca na telefonie") pokrywa się częściowo z zakresem B-12 — jeśli dokument z B-12 już istnieje w chwili realizacji tego zlecenia, wykorzystaj jego ustalenia zamiast powtarzać audyt od zera; jeśli nie istnieje, opisz wymiar 8 samodzielnie, w zakresie tego briefu.
- **B-02** (analiza technologiczna) bada te same produkty na innej warstwie — B-03 to *jak wygląda i jak się używa*, B-02 to *jak zbudowane pod spodem*. Oba stoją samodzielnie; nie zakładaj, że drugi już powstał.

---

## B-04 🟢 Niezapisane paradygmaty backendu — analiza autonomiczna → ADR

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b04-paradygmaty-adr` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody. (Odwołania do `ai-tools/...` w tym briefie dotyczą sąsiedniego repozytorium, tylko do odczytu — nie są objęte tą gałęzią.)
**Agent:** `explorer` (inwentaryzacja i dowody) → `general-purpose` (pisanie ADR-ów)
**Przeczytaj najpierw:** [`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md), `ai-tools/.claude/rules/python-coding-standards.md`, `ai-tools/.claude/rules/error-handling-patterns.md`, `ai-tools/.claude/rules/security-checklist.md` (inne repozytorium — ścieżki podane względem jego katalogu głównego), wszystkie moduły w `backend/app/modules/` (kod, nie tylko przykłady), [`sensor_registry.yaml`](../../sensor_registry.yaml), schematy w `backend/app/modules/*/schemas/`

### Kontekst

Zamiast rozmowy interview'owej (`grill-me`), to zlecenie ma być **w pełni autonomiczne**: agent samodzielnie znajduje w kodzie powtarzające się wzorce, których architektura ([`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md)) nie opisuje wprost, ocenia czy są zamierzone, i zapisuje potwierdzone jako ADR-y. Bez interakcji w trakcie — pytania zbierane są na końcu, do jednej rundy odpowiedzi, nie do dialogu.

### Zakres — dwie warstwy, reszta poza zakresem

1. **Backend (Python/FastAPI)** — cały `backend/app/`, wszystkie moduły (`core_data`, `security`, `telemetry`, `audit`, `device_identity`), nie tylko przykłady cytowane niżej.
2. **Warstwa styku (kontrakty)** — [`sensor_registry.yaml`](../../sensor_registry.yaml) jako współdzielone źródło prawdy między backendem a firmware, schematy payloadów telemetrycznych, kontrakt API konsumowany przez frontend.

**Firmware i frontend są świadomie poza zakresem tego zlecenia** — mają inny zestaw konwencji i inną pracochłonność, zasługują na osobne przejście. Wyjątek: jeśli coś w warstwie styku dotyka firmware (np. `sensor_registry.yaml` → `SensorRegistry.h`), opisz kontrakt, ale nie oceniaj stylu kodu C++ po drugiej stronie.

### Metoda — jak rozstrzygać bez pytania w trakcie

Dla każdego znalezionego wzorca:

1. **Zbierz wszystkie wystąpienia**, nie jedno. Wzorzec widziany raz to obserwacja, nie ustalenie — przeszukaj wszystkie moduły, policz zgodne i niezgodne przypadki.
2. **Klasyfikuj** na tej podstawie:
   - **reguła** — wzorzec występuje konsekwentnie (blisko 100%) w wielu modułach, bez kontrprzykładów, LUB jest już opisany (nawet pośrednio) w [`01_backend-architecture.md`](../technical/backend/01_backend-architecture.md) czy w istniejących regułach `.claude/rules/` → kandydat na ADR.
   - **wyjątek** — wzorzec łamany raz lub kilka razy, ale z dostrzegalnym uzasadnieniem w kodzie/kontekście (np. `skip_audit=True` przy ingeście telemetrii — dane z urządzenia IoT, nie akcja użytkownika) → kandydat na ADR opisujący regułę *i* jej granicę.
   - **dług** — wzorzec sprzeczny z tym, co dokumentacja już deklaruje, bez uzasadnienia, LUB nazewnictwo/zachowanie wprowadzające w błąd → **nie** ADR, tylko wpis na liście długu technicznego.
3. **Nie zostawiaj klasyfikacji otwartej.** Jeśli jest niejednoznaczna (mogłoby być regułą, mogłoby być wyjątkiem), wybierz interpretację lepiej popartą dowodami z kodu, zapisz ją w ADR-ie ze statusem `Proposed` (status z natury dopuszcza korektę przy przeglądzie) i w jednym zdaniu odnotuj odrzuconą alternatywę oraz dlaczego. Sekcja pytań na końcu raportu jest na rzeczy faktycznie nierozstrzygalne z samego kodu — nie na spory, które dają się rozstrzygnąć przewagą dowodów.

### Materiał wejściowy — hipotezy z audytu (punkt startowy, nie granica zakresu)

Potwierdź, obal albo doprecyzuj każdą metodą z sekcji wyżej. Szukaj też wzorców spoza tej listy — to jest jej właściwe zadanie.

1. **`get_` vs `find_`** — udokumentowane w architekturze, ale sprawdź czy trzymane wszędzie. Czy `get_or_create_internal` w [`ingest.py:190`](../../backend/app/modules/telemetry/services/ingest.py#L190) (auto-provisioning punktów pomiarowych z pakietu) łamie tę konwencję świadomie, czy jest przeoczeniem?
2. **Moduł bez `api/`** — `audit` nie ma warstwy API, wystawia się przez port w `core/`. Znajdź, czy to jedyny taki przypadek, i wydestyluj regułę „kiedy moduł powinien być bezportowy".
3. **`AuditAwareSession` blokujący commit bez wpisu audytowego** — mocny niezmiennik. Znajdź wszystkie miejsca z `skip_audit=True` i sprawdź, czy mają wspólną cechę (np. „zapis inicjowany przez urządzenie, nie przez użytkownika") — jeśli tak, to jest reguła do zapisania, nie tylko wyjątek.
4. **Funkcje modułowe zamiast metod serwisu** — `ingest.py` ma `_authorize`, `_build_error`, `_iter_points` jako funkcje modułowe. Sprawdź inne serwisy: czy to lokalny styl jednego pliku, czy powtarzający się wzorzec z rozpoznawalnym kryterium (np. „funkcja bez potrzeby stanu `self` zostaje funkcją").
5. **Frozen dataclass jako kontekst przewlekany przez helpery** (`_IngestContext`) — sprawdź, czy podobny wzorzec występuje gdzie indziej.
6. **`sensor_registry.yaml` jako jedyne źródło prawdy** — dziś obejmuje typy punktów i kody błędów, ale nie cały kontrakt payloadu, a prebuild hook, który miał to pilnować, jest wyłączony ([`platformio.ini`](../../firmware/platformio.ini)). Opisz zakres obecnej reguły „jedno źródło prawdy" i miejsce, gdzie się kończy.
7. **Nazewnictwo niezgodne z zachowaniem** — `device.last_diagnostics_at` ustawiane przy każdym ingeście telemetrii ([`ingest.py:154`](../../backend/app/modules/telemetry/services/ingest.py#L154)), czyli faktycznie znaczy „last_seen". Przeszukaj backend pod kątem innych pól/funkcji, których nazwa nie odpowiada temu, co robią — to zawsze ląduje w kategorii „dług", nigdy w ADR.
8. **Wzorzec `transaction()` context managera** ([`01_backend-architecture.md` §4.2](../technical/backend/01_backend-architecture.md)) — sprawdź, czy każdy serwis go faktycznie używa, czy są miejsca z ręcznym `commit`/`rollback` obok.
9. **Walidacja przy granicy modułu** — jak konsekwentnie schematy Pydantic z `extra="forbid"` ([`measurement_packet.py:63`](../../backend/app/modules/telemetry/schemas/measurement_packet.py#L63)) są stosowane w innych modułach; czy to reguła czy przypadek.

### Audyt zgodności z istniejącymi regułami

Sprawdź kod backendu i warstwy styku pod kątem trzech reguł, które go faktycznie dotyczą — `python-coding-standards`, `error-handling-patterns`, `security-checklist` (wszystkie w `ai-tools/.claude/rules/`). Reguły frontendowe, C++ i PowerShell **pomiń** — nie dotyczą zakresu tego zlecenia.

Dla każdej z trzech reguł: czy kod ją konsekwentnie przestrzega, czy są systematyczne odstępstwa. Jeśli kod **konsekwentnie i z dobrym powodem** robi inaczej niż mówi reguła — to reguła jest nieaktualna, nie kod jest zepsuty. Zaproponuj konkretną korektę tekstu reguły (jako diff/cytat, nie ogólnik). Jeśli odstępstwo jest przypadkowe (część kodu tak, część inaczej, bez powodu) — to jest dług, nie korekta reguły.

### Deliverable

**Raport analityczny** (główny wynik, do przeczytania w całości):
`docs/technical/backend/07_analiza_paradygmatow.md` — dla każdego znalezionego wzorca: nazwa, wszystkie miejsca wystąpienia z linkami, klasyfikacja (reguła/wyjątek/dług) z uzasadnieniem, i — dla klasyfikacji „reguła"/„wyjątek" — odniesienie do numeru ADR, który z tego powstał. Na końcu: sekcja „pytania do rozstrzygnięcia", jeśli coś zostało niejednoznaczne mimo metody wyżej, oraz sekcja „proponowane korekty istniejących reguł" z audytu zgodności.

**Szkice ADR** (do przeglądu jako diff, nie do commitowania automatycznie):
Jeden plik na potwierdzony wzorzec w `docs/technical/adr/NNNN-slug.md`, numeracja sekwencyjna od `0001` (nowy katalog — analogiczny do istniejącego `docs/business/adr/`, ale dla decyzji technicznych, które dziś nigdzie nie są zapisane). Format: krótki tytuł, `Status: Proposed`, 1–3 zdania kontekstu i decyzji — **zwięźle, konkretnie, bez wypełniania sekcji na siłę**. Rozbudowane sekcje (Rozpatrywane alternatywy, Konsekwencje) tylko tam, gdzie faktycznie coś wnoszą, na wzór istniejących [`docs/business/adr/`](../business/adr/). Status zostaje `Proposed`, dopóki go nie zaakceptujesz — agent nie przełącza sam na `Accepted`.

### Ograniczenia

- Żaden ADR nie powstaje z pojedynczej obserwacji — wymagane min. 2–3 zgodne wystąpienia w kodzie albo wyraźne pokrycie w istniejącej dokumentacji architektury.
- Nie twórz ADR-a dla czegoś, co jest oczywistym, jedynym rozsądnym wyborem bez realnej alternatywy — `ai-tools/.claude/skills/domain-modeling/ADR-FORMAT.md` opisuje kryteria „kiedy w ogóle pisać ADR" (musi być trudne do odwrócenia, zaskakujące bez kontekstu, i wynikiem realnego kompromisu); trzymaj się ich.
- Kategoria „dług" nigdy nie staje się ADR-em — trafia do listy na końcu raportu, jako osobne zadania do zlecenia później.

### Definicja ukończenia

Każdy wzorzec z listy hipotez ma jednoznaczną klasyfikację z dowodami; katalog `docs/technical/adr/` zawiera szkice gotowe do przeglądu jednym `git diff`; lista długu technicznego jest gotowa do przepisania na osobne zadania.

---

## B-05 🟢 Dokumentacja firmware + hardware ze schematami

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b05-dokumentacja-firmware-hardware` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `documentation-writer` (+ `explorer` do inwentaryzacji kodu)
**Przeczytaj najpierw:** wszystkie 7 plików w [`docs/technical/firmware/`](../technical/firmware/), [`Config.h`](../../firmware/include/Config.h), [`main.cpp`](../../firmware/src/main.cpp), wszystkie biblioteki w `firmware/lib/` **poza** `Adafruit_MAX31865` (zewnętrzna)

### Kontekst

Dokumentacja firmware **istnieje i jest niezła** (7 dokumentów, w tym bardzo dobry [`01_hardware.md`](../technical/firmware/01_hardware.md) z mapą pinów i uwagami o module KAmod). To nie jest zlecenie „napisz od zera" — to **scalenie, korekta i uzupełnienie o grafiki**.

### Znane niespójności do naprawienia (znalezione w audycie)

- [`01_hardware.md` §5](../technical/firmware/01_hardware.md) twierdzi „PT-506 — draft. Brak biblioteki odczytu ADC; telemetria wysyła dane syntetyczne (sinus)", ale §1 tego samego dokumentu mówi „kod gotowy" i wskazuje istniejący [`PressureSensor.cpp`](../../firmware/lib/Sensor/src/PressureSensor.cpp). Ustal stan faktyczny z kodu i popraw.
- §6 mówi o rezystorze **250 Ω**, §3 i `Config.h` o **136 Ω** (2× 68 Ω). §6 jest pozostałością po porzuconym planie — popraw.
- §6 nazywa SPI/PT100 „draft", podczas gdy §1 i §2 oznaczają go jako zweryfikowany.

### Zakres

1. **Uzgodnij dokumentację ze stanem kodu** — każdy element oznaczony statusem: `zweryfikowane w kodzie` / `zweryfikowane na sprzęcie` / `draft`. Te trzy statusy to nie to samo i dziś są mieszane.
2. **Schemat połączeń** — kompletny, jako **Mermaid + inline SVG** (bez zewnętrznych zasobów, ma się renderować na GitHubie i w Artifactach). Minimum: ESP32-S3 ↔ KAmod HAT (z zaznaczeniem zworek J2 i J_APWK), ESP32-S3 ↔ MAX31865 ↔ PT100 (3-przewodowy), ESP32-S3 ↔ ADS1015 ↔ pętla 4-20 mA PT-506 z rezystorem 136 Ω, drzewo zasilania (230 V → 24 V → 5 V XL4015 → 3,3 V).
3. **Diagram architektury firmware** — jak 13 bibliotek w `lib/` składa się w całość: co od czego zależy, co jest wołane z `loop()`, gdzie leży stan.
4. **Diagram stanów urządzenia** — od pierwszego uruchomienia (brak provisioningu → oczekiwanie na `ACTIVATE <kod>`) przez enrollment, auth challenge/response, aż po normalną pracę i ścieżki recovery. Materiał jest rozproszony po [`04_device_provisioning_flow.md`](../technical/firmware/04_device_provisioning_flow.md) i [`03_esp32_reset_and_recovery.md`](../technical/firmware/03_esp32_reset_and_recovery.md).
5. **Diagram sekwencji transmisji** — próbkowanie → okno → batch → HTTP POST → odpowiedź → czyszczenie bufora, z zaznaczeniem gdzie dane mogą zginąć (patrz B-09 kontekst: bufor jest tylko w RAM).
6. **Instrukcja montażu krok po kroku** — dla osoby, która ma to złożyć fizycznie, z uwagami krytycznymi (zasilanie 5 V/2 A osobne od USB, wspólna masa, zworki, dwie anteny U.FL).

### Ograniczenia

- **Nie zgaduj pinów.** Jedyne źródło prawdy to `Config.h`. Jeśli coś jest niejasne — oznacz jako pytanie, nie wymyślaj.
- Grafiki muszą działać w **obu motywach** (jasnym i ciemnym) — nie używaj czarnych linii na przezroczystym tle.
- **Zachowaj istniejącą numerację `01`–`07` i nazwy plików.** Dokładasz `00_przeglad.md` jako punkt wejścia i ewentualnie nowe pliki z kolejnymi numerami — nie reorganizujesz tego, co jest. Powód: te ścieżki są linkowane z `ai-tools/CLAUDE.md` i z innych dokumentów.
- **Nie weryfikujesz niczego na fizycznym sprzęcie.** Jeśli kod i dokumentacja się nie zgadzają, a rozstrzygnięcie wymaga płytki (np. czy zworka J_APWK jest przecięta), zostaw status `draft` i dopisz do listy „do sprawdzenia na sprzęcie" na końcu dokumentu. Nie awansuj niczego na `zweryfikowane na sprzęcie` na podstawie samego kodu.

### Deliverable

Zaktualizowany `docs/technical/firmware/` + nowy `00_przeglad.md` jako punkt wejścia ze schematem połączeń i diagramem architektury. Opcjonalnie: publikacja jako Artifact do wygodnego oglądania grafik.

---

## B-06 🔴 Testy firmware — analiza pokrycia i uzupełnienie

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b06-testy-firmware` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `test-writer` + `esp32-firmware-engineer`
**Przeczytaj najpierw:** [`firmware/test/`](../../firmware/test/) (5 istniejących testów), [`platformio.ini`](../../firmware/platformio.ini) (`env:native`, googletest), wszystkie biblioteki w `firmware/lib/`

### Kontekst

Infrastruktura testowa **już działa**: środowisko `native` + googletest, 5 plików testowych (`test_isensor_pt100`, `test_logger`, `test_telemetry_pt100`, `test_timestamp_regression`, `test_timesync`). Pokryte są rzeczy najłatwiejsze do przetestowania. **Bez pokrycia jest cała warstwa komunikacyjna** — czyli dokładnie to, co najczęściej zawodzi w terenie.

### Zakres — projekt warstwy testowalnej

Wykonaj w ramach jednego ciągłego przebiegu, bez przystanku na akceptację — decyzje z tej sekcji udokumentuj krótkim „dlaczego" w opisie PR-a (a jeśli branch nie jest jeszcze wypchnięty do zdalnego — w treści ostatniego commita), potem od razu przechodź do pisania testów:

1. Zinwentaryzuj wszystkie 13 własnych bibliotek: co robi, jakie ma zależności sprzętowe, czy da się ją testować na `native` bez przeróbek.
2. Wskaż, **które biblioteki wymagają wprowadzenia interfejsu/atrapy**, żeby dały się testować — w szczególności `ModemLink` (dziś wprost trzyma `TinyGSM`), `TelemetryHttpClient` (trzyma `HttpClient`), `DeviceIdentity` (trzyma `Preferences`/NVS).
3. Zaprojektuj warstwę testowalną tak, jak uznasz za właściwe — **refaktor działającego kodu jest dozwolony bez ograniczeń** (patrz „Decyzje już podjęte"). Nadal jednak uzasadnij każdy wprowadzony szew: interfejs, który nie służy żadnemu testowi, jest kosztem bez zwrotu.
4. Ustal ryzyko każdego modułu (co się stanie w terenie, jeśli to zawiedzie) i posortuj kolejność pisania testów wg ryzyka, nie wg łatwości.
5. **Wypisz listę zmian wymagających weryfikacji na sprzęcie** — będzie podstawą jednorazowego testu na płytce na końcu prac.

### Zakres — testy

Priorytet wg ryzyka, propozycja wyjściowa:

| Priorytet | Moduł | Scenariusze krytyczne |
|---|---|---|
| 1 | `TelemetryPayload` | przepełnienie bufora (`RETAIN_WINDOWS_MAX`), poprawne czyszczenie po wysyłce, `WINDOW_DROPPED_BUFFER_FULL`, kolejność okien, limit `MAX_ERRORS` |
| 2 | `TelemetrySender` | retry po błędzie, zachowanie przy 401/403/500/timeout, brak podwójnej wysyłki tego samego okna, inkrementacja `seq` |
| 3 | `DeviceAuthClient` | wygaśnięcie tokenu, odświeżenie z marginesem `TOKEN_REFRESH_MARGIN_SECONDS`, odrzucony podpis, parsowanie ISO8601 |
| 4 | `EnrollmentClient` | poprawny/niepoprawny kod aktywacji, backoff, przejście do fazy telemetrii |
| 5 | `Watchdog` | wykrycie zawieszenia po `WATCHDOG_STUCK_MS`, limit `MAX_RESTART_ATTEMPTS`, reset licznika po sukcesie |
| 6 | `ModemLink` | sekwencja inicjalizacji, obsługa braku sieci, timeout AT |

Dodatkowo: **test kontraktowy payloadu** — wygenerowany przez firmware JSON musi przejść walidację schematem [`MeasurementPacketRequest`](../../backend/app/modules/telemetry/schemas/measurement_packet.py) (v=2, `extra="forbid"`). Dziś rozjazd wykryłby dopiero backend na produkcji.

### Decyzje już podjęte

- Zostajemy przy `env:native` + googletest — nie wprowadzaj nowego frameworka.
- **Refaktor działającego firmware pod testowalność jest dozwolony bez ograniczeń.** Nie musisz pytać o zgodę na wprowadzenie interfejsu w `ModemLink`, `TelemetryHttpClient` czy `DeviceIdentity`. Weryfikacja na fizycznej płytce odbywa się **raz, na końcu** — nie po każdej zmianie.
- **Konsekwencja, o której musisz pamiętać:** ryzyko regresji w warstwie komunikacyjnej jest realne i nie zostanie wychwycone przez testy `native` (bo one właśnie tę warstwę zastępują atrapą). Dlatego prowadź jawną listę zmian dotykających kodu, który rozmawia ze sprzętem lub siecią, i oznacz w niej, co dokładnie trzeba sprawdzić na płytce: rejestracja w sieci LTE, wysłanie pakietu, challenge/response, restart po watchdogu.
- Testy na sprzęcie (`pio test -e esp32-s3`) są poza zakresem — weryfikacja końcowa to normalne uruchomienie i odczyt logów, nie framework testowy na urządzeniu.
- Naprawa wyłączonego prebuild hooka (`scripts/prebuild.py`) wchodzi w zakres, bo dotyczy tej samej pętli walidacji.

### Definicja ukończenia

`pio test -e native` przechodzi, pokrywa min. 6 bibliotek, test kontraktowy payloadu wyłapuje celowo wprowadzony rozjazd ze schematem backendu, a lista zmian do weryfikacji sprzętowej jest gotowa do przejścia na płytce.

---

## B-08 🟡 Jeden interfejs odczytu stanu z firmware

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b08-interfejs-stanu-urzadzenia` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agenci:** `Plan` (projekt) → `esp32-firmware-engineer` + backend (implementacja) → `code-reviewer` (samoprzegląd) — jeden ciągły przebieg, bez przystanku między etapami; **nie używaj skilla `prepare-work`** (jego pełny wariant ma wbudowaną fazę `grill-me` i przystanki na przegląd — to zlecenie ma przejść od projektu do gotowego kodu bez pytań).
**Przeczytaj najpierw:** [`TelemetryHttpClient.h`](../../firmware/lib/TelemetryHttpClient/src/TelemetryHttpClient.h), [`DeviceAuthClient.h`](../../firmware/lib/DeviceAuthClient/src/DeviceAuthClient.h), [`main.cpp`](../../firmware/src/main.cpp), [`ingest.py`](../../backend/app/modules/telemetry/services/ingest.py), [`06_device_identity_module.md`](../technical/backend/06_device_identity_module.md), [`01_plan_biznesowy.md` §3.7](../business/01_plan_biznesowy.md) (format wiadomości diagnostycznej)

### Kontekst i ograniczenie architektoniczne

Dziś komunikacja jest **wyłącznie jednokierunkowa**: urządzenie wysyła, backend odpowiada statusem. [`TelemetryHttpClient`](../../firmware/lib/TelemetryHttpClient/src/TelemetryHttpClient.h) ma **tylko metodę `post()`** — nie ma `get()`. Urządzenie siedzi za NAT-em operatora komórkowego, więc backend **nie może** go zaczepić z własnej inicjatywy. Każdy odczyt z urządzenia musi więc być realizowany jako *odpowiedź urządzenia przy jego następnym kontakcie*.

To zlecenie ma zaprojektować i wdrożyć **dokładnie jeden**, kanoniczny mechanizm takiego odczytu — tak, żeby każdy kolejny odczyt (konfiguracja, wersja, cokolwiek) szedł tą samą ścieżką, a nie dorabiał sobie własnej.

### Decyzje już podjęte

- **Pierwszy odczyt to stan i tożsamość urządzenia**: wersja firmware, uptime, licznik restartów (`rtcRestartCounter` już istnieje w RTC), przyczyna ostatniego restartu, RSSI, wolna pamięć, numer seryjny, wersja schematu rejestru czujników. Konfiguracja urządzenia to **kolejny** odczyt, już tym samym kanałem — zaprojektuj mechanizm tak, żeby ją obsłużył bez zmian w kontrakcie.
- Model **pull, nie push** — wymuszony przez NAT, nie podlega dyskusji.
- Nie budujemy pełnej kolejki komend ad-hoc na tym etapie. Ma powstać *jeden* mechanizm, nie framework.

### Rytm komunikacji — liczby z kodu, nie z założeń

Zanim policzysz koszt transferu, weź faktyczne wartości z [`TelemetryPayload.h`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.h) i [`Config.h`](../../firmware/include/Config.h):

| Parametr | Wartość w kodzie | Znaczenie |
|---|---|---|
| `SAMPLE_INTERVAL_MS` | 15 000 | próbkowanie co 15 s |
| `WINDOW_SECONDS` | 15 | jedno okno = 15 s |
| `WINDOWS_PER_BATCH` | 4 | **transmisja mniej więcej co 60 s** |
| `RETAIN_WINDOWS_MAX` | 48 (`4 × 12`) | **bufor RAM mieści tylko ~12 minut danych** |

Dwie rzeczy z tego wynikają i obie są dla tego zlecenia istotne:

1. **Obecny interwał transmisji to ~60 s, a plan biznesowy zakłada docelowo 1–5 min.** Policz koszt wariantu B (osobny endpoint) dla obu rytmów, nie tylko dla obecnego — inaczej rekomendacja zestarzeje się przy pierwszej zmianie interwału.
2. **Bufor lokalny to ~12 minut w RAM**, podczas gdy [`CONTEXT.md`](../business/CONTEXT.md) obiecuje klientowi 72 h retencji offline. To jest osobne zadanie (trwały bufor), ale **diagnostyka musi to raportować** — stan zapełnienia bufora i liczba porzuconych okien (`WINDOW_DROPPED_BUFFER_FULL`) należą do zestawu odczytywanych pól, bo bez nich nie da się zauważyć, że urządzenie po cichu gubi dane.

### Zakres — projekt

Rozstrzygnij, udokumentuj wybór krótkim „dlaczego" w opisie PR-a (a jeśli branch nie jest jeszcze wypchnięty do zdalnego — w treści ostatniego commita) i przejdź od razu do implementacji, bez przystanku na akceptację:

1. **Doczepienie do istniejącego POST-a czy osobny endpoint?** Wariant A: urządzenie dokłada blok stanu do pakietu telemetrycznego (zero nowych rund komunikacji, ale miesza dwa różne rodzaje danych i zwiększa payload w każdym cyklu). Wariant B: osobny `POST /telemetry/diagnostics` z własnym interwałem (czysty rozdział, ale dodatkowa transmisja = koszt transferu SIM). Wariant C: backend zwraca w odpowiedzi na ingest flagę „prześlij stan przy następnym kontakcie", urządzenie reaguje. **Rekomendacja z uzasadnieniem kosztu transferu** — plan zakłada 50–200 MB/miesiąc na SIM.
2. **Kontrakt danych** — schemat wiadomości diagnostycznej. Punkt wyjścia jest gotowy w [§3.7 planu biznesowego](../business/01_plan_biznesowy.md), a plan wdrożenia backendu ma już rozpisany model `DeviceDiagnostic` (Etap 2.2). Użyj ich, nie wymyślaj od nowa.
3. **Gdzie leży źródło prawdy o schemacie** — [`sensor_registry.yaml`](../../sensor_registry.yaml) jest już wspólny dla typów punktów i kodów błędów. Rozstrzygnij, czy schemat diagnostyki dołącza do tego samego mechanizmu.
4. **Świeżość odczytu** — jak backend ma pokazać, że dane pochodzą sprzed 20 minut, a nie z teraz. Nawiązuje do zasady z planu: nigdy nie pokazuj wartości bez czasu i jakości.

### Zakres — implementacja

Backend: model + migracja Alembic (`alembic revision --autogenerate`, nigdy ręcznie) + endpoint + serwis + testy.
Firmware: zebranie danych stanu + wysyłka wg wybranego wariantu + testy na `native`.
Frontend: pokazanie stanu w widoku urządzenia (`DeviceDetailDrawer` już istnieje).
Dokumentacja: nowy plik w `docs/technical/` — to jest nowy moduł/kanał, więc dokumentacja jest obowiązkowa w tym samym zadaniu.

### Uwaga do naprawienia przy okazji

`device.last_diagnostics_at` jest dziś ustawiane **przy każdym ingeście telemetrii** ([`ingest.py:154`](../../backend/app/modules/telemetry/services/ingest.py#L154)), czyli pole nazywa się „ostatnia diagnostyka", a znaczy „ostatni kontakt". Po wprowadzeniu prawdziwej diagnostyki ta nazwa stanie się aktywnie myląca — rozdziel `last_seen_at` od `last_diagnostics_at`.

---

## B-09 🟡 Normalizacja telemetrii — tabela `measurements`

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b09-normalizacja-telemetrii` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agenci:** `Plan` (projekt) → implementacja → `code-reviewer` (samoprzegląd) — jeden ciągły przebieg, bez przystanku między etapami; **nie używaj skilla `prepare-work`** (jego pełny wariant ma wbudowaną fazę `grill-me` i przystanki na przegląd — to zlecenie ma przejść od projektu do gotowego kodu bez pytań).
**Przeczytaj najpierw:** [`ingest.py`](../../backend/app/modules/telemetry/services/ingest.py), [`measurement_packet.py`](../../backend/app/modules/telemetry/schemas/measurement_packet.py), [`queries.py`](../../backend/app/modules/telemetry/repositories/queries.py), [`03_plan_wdrozenia_backend_mvp.md` Etap 2.1 i 4](../business/03_plan_wdrozenia_backend_mvp.md), [`04_telemetry_module.md`](../technical/backend/04_telemetry_module.md)

### Kontekst

Pomiary trafiają dziś **wyłącznie do blobu JSON** w tabeli `telemetry_packets` — [`telemetry/models/`](../../backend/app/modules/telemetry/models/) zawiera tylko `measurement_packet.py` i `telemetry_error.py`. Zapytania dashboardu przekopują się przez te bloby ([`queries.py`](../../backend/app/modules/telemetry/repositories/queries.py) robi `row_number()` po pakietach, żeby znaleźć najnowszy per obiekt).

Konsekwencje, wszystkie naraz:
- **alarmy** nie mają czego obserwować (reguła progowa potrzebuje strumienia pomiarów, nie blobów),
- **historia i wykresy** nie mają wydajnego zapytania po zakresie czasu,
- **eksport CSV** nie ma z czego eksportować bez parsowania JSON-a w locie,
- **wydajność** — [plan wdrożenia §4.3](../business/03_plan_wdrozenia_backend_mvp.md) szacuje ~1,6 mln rekordów/rok na obiekt i ~23 mln dla gminy 15-obiektowej.

To jest **pojedyncza zmiana odblokowująca trzy funkcje MVP naraz** — najwyższy priorytet w warstwie backendu.

### Zakres

1. **Model `Measurement`** — punkt wyjścia gotowy w [Etapie 2.1 planu](../business/03_plan_wdrozenia_backend_mvp.md): `measurement_point_id` (FK), `window_start`, `window_seconds`, `avg`/`min`/`max`/`value`, `quality`, `received_at`, `source_packet_id` (traceability do blobu). `UniqueConstraint(measurement_point_id, window_start)` daje idempotencję per punkt per okno — **niezależną** od istniejącej idempotencji `(device_id, seq)`.
   Zwróć uwagę na typ `value`: schemat dopuszcza `float | int | bool | None` ([`measurement_packet.py:21`](../../backend/app/modules/telemetry/schemas/measurement_packet.py#L21)) — rozstrzygnij, jak przechowywać `bool` (`digital_input`, `power_status`) obok `float`.
2. **Zapis przy ingest** — rozszerz [`_process_measurement_windows`](../../backend/app/modules/telemetry/services/ingest.py#L180), który już rozwiązuje `point_id → MeasurementPoint`. Zachowaj zapis blobu (audyt/replay). Zachowaj `skip_audit=True` (dane z urządzenia, nie akcja użytkownika).
3. **Backfill** — skrypt migrujący istniejące bloby do znormalizowanej tabeli, idempotentny, wznawialny, z raportem ile rekordów przeniesiono i ile odrzucono.
4. **Indeksy** — minimum `(measurement_point_id, window_start)`. Zweryfikuj planem zapytania, nie założeniem.
5. **Przepisanie zapytań** — [`queries.py`](../../backend/app/modules/telemetry/repositories/queries.py) przechodzi na nową tabelę. Porównaj czasy przed/po na danych syntetycznych.
6. **Endpoint historii** — `GET .../points/{point_id}/measurements?from=&to=&limit=` (Etap 4 planu). Odpowiedź **zawsze** z `quality` i `window_start`.

### Decyzje już podjęte

- Blob `telemetry_packets` **zostaje** — to ścieżka audytu i replay. Retencja blobów to osobne zadanie.
- Migracja **wyłącznie** przez `alembic revision --autogenerate -m "..."` + ręczny review diffu. Nigdy pisana z palca.
- Model musi być zarejestrowany w [`models_registry.py`](../../backend/app/infrastructure/sql/models_registry.py) — bez tego autogenerate go nie zobaczy.
- Bez nowych zależności (żadnego TimescaleDB/InfluxDB na tym etapie) bez osobnej zgody.

### Backfill i migracja — zawsze zero-downtime, niezależnie od wolumenu

Nie ma tu decyzji do konsultacji — buduj to tak, żeby zadziałało bez względu na to, ile danych faktycznie jest, i bez okna serwisowego:

1. **Migracja schematu jest czysto addytywna** (nowa tabela `measurements`, nic nie blokuje ani nie zmienia istniejących tabel) — bezpieczna do uruchomienia w dowolnym momencie, produkcja czy nie.
2. **Backfill zawsze jako osobny skrypt, batchami, wznawialny**, niezależnie od tego, ile wierszy faktycznie jest w `telemetry_packets` — nie warunkuj implementacji od zmierzonego wolumenu, tylko zawsze buduj wersję odporną na duży wolumen. Policz faktyczną liczbę wierszy i zakres dat na środowisku, na którym pracujesz, i **zapisz to w opisie PR-a (lub w commit message, jeśli branch nie jest jeszcze wypchnięty)** jako kontekst (np. „X pakietów, backfill zajął Y sekund") — to informacja do raportu, nie pytanie do zadania.
3. **Cutover na czytanie z nowej tabeli następuje dopiero po zakończeniu backfillu** — do tego momentu `queries.py` może nadal czytać ze starej ścieżki. Żaden krok nie wymaga zatrzymania przyjmowania telemetrii.
4. Sprawdź, czy `waterworks-monitoring-platform.onrender.com` (patrz `Config.h`) aktualnie odpowiada — jeśli tak, potraktuj to jako potwierdzenie, że powyższa dyscyplina (addytywność, brak okna serwisowego) jest tu obowiązkowa, nie opcjonalna. Zapisz w PR-ze (lub w commit message, jeśli branch jest jeszcze lokalny), czy środowisko żyło w chwili pracy — to też tylko informacja do raportu.

### Partycjonowanie — decyzja, nie pytanie

Wprowadź partycjonowanie czasowe **od razu**, wzorem partycjonowanego modułu `audit` — zmiana schematu na docelowej skali (~23 mln rekordów/rok dla gminy 15-obiektowej, patrz Kontekst) boli dużo bardziej niż na pustej/małej tabeli, a koszt zrobienia tego teraz jest niski. Udokumentuj wybrany schemat partycjonowania w opisie PR-a (lub w commit message, jeśli branch jest jeszcze lokalny).

### Definicja ukończenia

Pakiet telemetryczny tworzy wiersze w `measurements`; zapytanie o wykres 30-dniowy nie dotyka blobów; backfill przeniósł dane historyczne; testy pokrywają idempotencję (ten sam pakiet dwa razy → brak duplikatów), nieznany punkt, oraz `bool` w `value`.

---

## B-10 🟡 Analiza portu ESP32-S3 → ESP-WROOM-32

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b10-analiza-port-wroom32` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `esp32-firmware-engineer` (analiza)
**Przeczytaj najpierw:** [`Config.h`](../../firmware/include/Config.h), [`main.cpp`](../../firmware/src/main.cpp), [`platformio.ini`](../../firmware/platformio.ini), [`StatusLed`](../../firmware/lib/StatusLed/src/StatusLed.cpp), [`DeviceIdentity`](../../firmware/lib/DeviceIdentity/src/DeviceIdentity.cpp), [`01_hardware.md`](../technical/firmware/01_hardware.md)

### Kontekst i motyw

Motywem jest **cena i dostępność modułów** — ESP-WROOM-32 (klasyczny ESP32) jest tańszy i szerzej dostępny niż ESP32-S3. Analiza ma odpowiedzieć, czy oszczędność jest realna po uwzględnieniu kosztu pracy i utraconych funkcji.

### Zakres — analiza wykonalności

Przejdź przez cały firmware i wypisz **każde** miejsce zależne od S3. Znane punkty zaczepienia (lista wyjściowa, nie wyczerpująca):

1. **Piny.** `Config.h` używa GPIO 4, 5, 8, 9, 11, 12, 13, 14, 17, 18, 48. Na klasycznym ESP32: **GPIO 48 nie istnieje** (zakres 0–39), **GPIO 6–11 są zajęte przez flash SPI** i nie wolno ich używać, **GPIO 34–39 są tylko wejściowe**. To wymusza przemapowanie I2C (dziś 8/9) i części SPI (dziś 11/12/13/14). Zaproponuj konkretną nową mapę pinów z uzasadnieniem każdego wyboru.
2. **LED statusu.** [`StatusLed`](../../firmware/lib/StatusLed/src/StatusLed.cpp) steruje adresowalnym WS2812 (Adafruit_NeoPixel) na GPIO48 — na klasycznych płytkach DevKit **nie ma diody RGB**, jest zwykła LED (często GPIO 2). Rozstrzygnij: zewnętrzny WS2812 czy degradacja do zwykłej diody (i co to robi z sygnalizacją kolorami opisaną w [`01_hardware.md` §4](../technical/firmware/01_hardware.md)).
3. **Kryptografia.** `DeviceIdentity` generuje parę EC P-256 i podpisuje challenge. **To jest punkt krytyczny analizy** — sprawdź w kodzie, czy używane jest przyspieszenie sprzętowe dostępne tylko na S3, ile zajmuje generowanie klucza i podpis na klasycznym ESP32, i czy mieści się w budżecie czasowym (watchdog `esp_task_wdt` z timeoutem 15 s wg `platformio.ini`).
4. **Pamięć.** Sprawdź zużycie RAM/flash w obecnym buildzie (`pio run -e esp32-s3` podaje statystyki) i porównaj z możliwościami WROOM-32 (520 KB SRAM, zwykle 4 MB flash, brak PSRAM w podstawowych wariantach). Zwróć uwagę na bufor okien w [`TelemetryPayload`](../../firmware/lib/TelemetryPayload/src/TelemetryPayload.cpp) i na `TINY_GSM_RX_BUFFER=1024`.
5. **USB/Serial.** S3 ma natywne USB CDC, klasyczny ESP32 wymaga konwertera UART — wpływ na logi i na proces flashowania w terenie.
6. **`RTC_DATA_ATTR`** — używane dla `rtcRestartCounter` i stanu czasu; sprawdź zgodność.
7. **`platformio.ini`** — nowe środowisko `env:esp32-wroom` obok istniejących, **bez usuwania** `env:esp32-s3`.

### Zakres — wnioski, których oczekuję

1. **Werdykt:** port opłacalny / opłacalny warunkowo / nieopłacalny — z liczbami.
2. **Próg opłacalności zamiast rachunku na zadanym wolumenie.** Skala nie jest znana — na teraz to **kilka prototypów, bez planów skalowania**. Nie zgaduj więc liczby urządzeń. Zamiast tego policz **przy ilu sztukach port zaczyna się zwracać**: (koszt pracy nad portem + roczny koszt utrzymywania dwóch wariantów) ÷ oszczędność na module = próg w sztukach. Ceny modułów sprawdź aktualne, nie z pamięci.
3. **Co się traci** — konkretnie, funkcja po funkcji.
4. **Ryzyko utrzymania dwóch wariantów** — każdy przyszły czujnik trzeba będzie testować na obu. Przy kilku prototypach ten koszt stały jest prawdopodobnie większy niż cała oszczędność — sprawdź, czy tak jest, i powiedz to wprost.
5. **Alternatywa do rozważenia:** czy przemysłowe płytki DIN na klasycznym ESP32 nie rozwiązują sprawy lepiej niż gołe moduły WROOM (patrz B-01, wariant W3) — czyli czy port i tak nie będzie potrzebny z innego powodu. **To może się okazać ważniejsze niż sam rachunek cenowy:** jeśli droga do wersji przemysłowej i tak prowadzi przez klasyczny ESP32, port przestaje być kwestią oszczędności, a staje się warunkiem wejścia.

### Ograniczenia

- **To zlecenie kończy się na dokumencie — implementacja portu jest poza jego zakresem, niezależnie od werdyktu.** Nawet gdy analiza wyjdzie jednoznacznie pozytywna, nie zaczynaj przepinać GPIO ani zmieniać `platformio.ini` w ramach tej pracy — port to osobne, przyszłe zlecenie, dla którego ten dokument jest wejściem. Zadanie jest ukończone, gdy dokument jest gotowy, nie gdy ktoś go zaakceptuje.
- Nie zakładaj, że coś działa — sprawdź w kodzie i w dokumentacji Espressif.
- **Nie licz oszczędności na wyimaginowanym wolumenie.** Jeśli wniosek brzmi „przy obecnej skali to się nie opłaca", napisz to wprost — to jest wartościowa odpowiedź, nie porażka analizy.

### Deliverable

`docs/technical/firmware/08_analiza_portu_esp32_wroom.md`. Plan wdrożenia portu (jeśli werdykt jest pozytywny) zostaje osobnym, przyszłym zleceniem — nie pisz go w ramach tego zadania, wystarczy żeby dokument dawał wystarczająco dużo, żeby taki plan dało się zlecić od razu.

---

## B-11 🔴 Budżet energetyczny i tryby zasilania

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b11-budzet-energetyczny` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `esp32-firmware-engineer` + `documentation-writer`
**Przeczytaj najpierw:** [`main.cpp`](../../firmware/src/main.cpp), [`Config.h`](../../firmware/include/Config.h), [`ModemPower`](../../firmware/lib/ModemPower/src/ModemPower.cpp), [`01_hardware.md` §7](../technical/firmware/01_hardware.md), [`sensor_registry.yaml`](../../sensor_registry.yaml) (kod `POWER_LOW`)

### Kontekst — stan faktyczny

Nie istnieje żaden dokument o poborze mocy. Co widać w kodzie:

- **Nigdzie nie ma trybu uśpienia.** `loop()` kręci się z `delay(10)`, modem po `powerOn()` zostaje włączony na stałe, `SAMPLE_INTERVAL_MS` to 15 s. Urządzenie pracuje w trybie ciągłym.
- **Dokumentacja modułu KAmod** ostrzega o zapotrzebowaniu **5 V / min. 2 A** przy szczytach transmisji LTE i wprost mówi, że USB dev-kitu tego nie zapewni.
- **Kod błędu `POWER_LOW`** istnieje w [`sensor_registry.yaml`](../../sensor_registry.yaml) („Device battery voltage below safe threshold"), ale **nic go nigdy nie ustawia** — nie ma pomiaru napięcia zasilania.
- Katalog alarmów w planie biznesowym wymienia „zanik zasilania urządzenia lub obiektu" jako alarm krytyczny i „powrót zasilania" jako zdarzenie informacyjne — obu dziś nie da się wykryć.

### Zakres

1. **Bilans prądowy** — oszacuj pobór w każdej fazie: bezczynność, próbkowanie PT100 przez MAX31865, próbkowanie ADS1015, rejestracja w sieci LTE, transmisja HTTPS, szczyt nadawania. Osobno ESP32-S3 i modem — modem dominuje. **Podstawą są karty katalogowe** (ESP32-S3, A7670E, MAX31865, ADS1015), nie pomiar — nie zakładaj dostępu do przyrządów. Jeśli jakaś wartość wymaga zmierzenia, żeby wniosek był wiarygodny, wypisz ją na osobnej liście „do zmierzenia na stanowisku" z opisem jak zmierzyć.
2. **Dobór zasilania** — czy obecny łańcuch (zasilacz 24 V 1 A → XL4015 24→5 V 2 A) wystarcza w szczycie. Uwzględnij sprawność przetwornicy i tętnienia. Zweryfikuj to obliczeniowo, nie na oko.
3. **Podtrzymanie przy zaniku 230 V** — ile czasu potrzeba, żeby urządzenie zdążyło wysłać alarm „zanik zasilania" i bezpiecznie zapisać stan. Zaproponuj rozwiązanie (kondensator o dużej pojemności / superkondensator / mały akumulator / UPS DIN) z ceną i miejscem w BOM.
4. **Detekcja zaniku zasilania i pomiar napięcia** — jak to zmierzyć. ADS1015 ma **trzy wolne kanały** (AIN1–3 wg [`01_hardware.md` §3](../technical/firmware/01_hardware.md)) — najprostsza droga to dzielnik napięcia na wolnym kanale. Zaprojektuj: dzielnik, progi, histereza, ustawianie `POWER_LOW`, wysłanie zdarzenia przed utratą zasilania.
5. **Czy warto wprowadzać tryby uśpienia** — przy zasilaniu sieciowym (założenie: „w głównych obiektach dostępne jest zasilanie elektryczne") deep sleep może być niepotrzebną komplikacją. Ale próbkowanie co 15 s, **transmisja co ~60 s** (`WINDOWS_PER_BATCH = 4` × `WINDOW_SECONDS = 15`) i modem stale włączony podbijają zużycie transferu SIM i temperaturę w szafie. Rozstrzygnij z liczbami, nie z przeczucia. Uwaga: uśpienie z modemem wyłączanym cyklicznie oznacza kilkudziesięciosekundową rejestrację w sieci przy każdym wybudzeniu — przy interwale 60 s to się prawdopodobnie nie spina, przy 5 min już może.
6. **Punkty pomiarowe bez zasilania sieciowego.** Plan zakłada prąd „w głównych obiektach", ale zakres produktu obejmuje też *punkty pomiarowe na sieci* i *komory pomiarowe*, gdzie 230 V bywa niedostępne. Oszacuj, czy obecna architektura (modem stale włączony, brak deep sleep) ma jakąkolwiek szansę na zasilaniu bateryjnym lub solarnym, i jaki byłby konieczny rytm pracy. To nie musi być projekt — wystarczy werdykt „da się / nie da się bez przebudowy" z liczbami.
7. **Temperatura pracy** — szafa metalowa w hydroforni latem. Sprawdź zakresy pracy komponentów z BOM.

### Uwaga o niezależności od innych zleceń

Punkt 4 (detekcja zaniku zasilania) zakłada wysłanie zdarzenia z urządzenia do backendu. Sprawdź w repo, czy taki kanał już istnieje (`TelemetryHttpClient`, `DeviceAuthClient`, endpointy w `backend/app/modules/telemetry/`). Jeśli tak — użyj go. Jeśli nie — zaprojektuj dla tego jednego zdarzenia najmniejszy możliwy sposób transmisji (np. dodatkowe pole w istniejącym payloadzie telemetrycznym) w ramach tego zlecenia, zamiast czekać na osobny, ogólny interfejs diagnostyczny; opisz go tak, żeby dało się go później łatwo przenieść do takiego interfejsu, gdyby powstał.

Wynik tego zlecenia (bilans mocy, BOM podtrzymania) naturalnie uzupełnia dokumentację sprzętową i zestawienie wariantów gatewaya. Jeśli te dokumenty już istnieją w chwili realizacji — dopisz do nich. Jeśli nie — zostaw wynik jako samodzielny plik; ktoś inny scali go później.

### Deliverable

`docs/technical/firmware/09_budzet_energetyczny.md`: tabela poboru per faza, bilans dla zasilacza, rekomendacja podtrzymania z BOM, projekt detekcji zaniku zasilania, werdykt w sprawie trybów uśpienia.

---

## B-12 🟢 Widok mobilny — audyt i dostosowanie

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b12-widok-mobilny` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `general-purpose` (frontend) · **Weryfikacja:** skill `ui-verify`
**Przeczytaj najpierw:** [`frontend-architecture.md`](../technical/frontend/frontend-architecture.md), [`01_plan_biznesowy.md` §2.8](../business/01_plan_biznesowy.md) (zakres aplikacji użytkownika — dashboard, widok obiektu), [`src/components/layout/`](../../frontend/src/components/layout/), [`src/pages/`](../../frontend/src/pages/)

### Kontekst — stan faktyczny z audytu

Frontend jest zbudowany **wyłącznie pod desktop**. Konkretnie:

- W całym `src/` jest **33 wystąpienia prefiksów responsywnych** Tailwinda (22× `lg:`, 7× `sm:`, 4× `md:`).
- **18 z 20 stron ma zero** prefiksów responsywnych — w tym `DashboardPage`, `ObjectsPage`, `DevicesPage`, `MembersPage` i wszystkie strony platformowe. Wyjątki to `LoginPage` (1) i `ObjectDetailPage` (2).
- Shell'e z sidebarem (`OrgShell`, `PlatformShell`) mają po **1** prefiksie — czyli sidebar prawdopodobnie nie chowa się na wąskim ekranie.
- `<meta name="viewport">` **jest** poprawny — czyli strona nie jest skalowana, tylko po prostu się nie mieści.

Tymczasem plan biznesowy opisuje pracownika terenowego, który „szybko sprawdza, czy wyjazd na obiekt jest uzasadniony" — to jest scenariusz telefonowy, nie biurkowy.

### Zakres

1. **Audyt** — przejdź przez wszystkie 20 stron w szerokościach 375 px, 768 px i 1280 px. Dla każdej: co się łamie, co wystaje poza ekran, czego nie da się kliknąć. Udokumentuj zrzutami przed zmianą.
2. **Ustal priorytet stron.** Nie wszystko musi działać na telefonie. Propozycja: **krytyczne** — `LoginPage`, `DashboardPage`, `ObjectsPage`, `ObjectDetailPage` (to jest ścieżka pracownika w terenie); **ważne** — `DevicesPage`; **pomijalne na tym etapie** — strony platformowe i konfiguracyjne (admin siedzi przy biurku). Zweryfikuj ten podział i uzasadnij zmiany.
3. **Nawigacja** — sidebar musi się chować na wąskim ekranie (drawer/hamburger). To dotyka `OrgShell`, `PlatformShell`, `OrgSidebar`, `PlatformSidebar`, `Topbar`.
4. **Tabele** — [`DataTable`](../../frontend/src/components/ui/DataTable.tsx) jest używana wszędzie i na telefonie nie zadziała w formie tabeli. Rozstrzygnij wzorzec: przewijanie poziome w kontenerze vs. przełączanie na listę kart poniżej progu. Wybierz **jeden** i zastosuj konsekwentnie.
5. **Wykresy** — `ObjectMeasurementsChart` (recharts) wymaga sprawdzenia na wąskim ekranie: czytelność osi, dotyk zamiast hovera dla tooltipa.
6. **Dialogi i drawery** — `Dialog`, `Drawer`, `SettingsDialog` (z `SettingsRail`) to komponenty typowo desktopowe.
7. **Cele dotykowe** — minimum 44×44 px dla elementów klikalnych. Sprawdź `Button`, `StatusPill`, ikony akcji w tabelach.

### Decyzje już podjęte

- Zostajemy przy Tailwindzie i podejściu utility-first — nie wprowadzaj biblioteki komponentów ani osobnego CSS-a.
- Nie budujemy osobnej aplikacji mobilnej ani PWA — to responsywność istniejącej aplikacji.
- Testy istniejące (12 plików) muszą dalej przechodzić.

### Jak uruchomić aplikację lokalnie

W repo nie ma instrukcji uruchomieniowej (`frontend/README.md` to niezmieniony szablon Vite), więc dla porządku:

- **Backend:** konfiguracja `FastAPI (backend)` w [`.vscode/launch.json`](../../.vscode/launch.json) — `uvicorn app.main:app --reload --port 8000`, interpreter z `.venv` w katalogu głównym repo. Wymaga działającego PostgreSQL i `.env`.
- **Dane testowe:** [`backend/scripts/seed_database.py`](../../backend/scripts/seed_database.py).
- **Frontend:** `npm --prefix frontend run dev` (Vite, domyślnie `:5173`).

Jeśli któregoś kroku nie da się wykonać, zatrzymaj się i zgłoś — nie audytuj responsywności na zrzutach z pustej aplikacji bez danych, bo tabele bez wierszy nie pokażą problemów z układem.

### Weryfikacja

Po implementacji uruchom skill `ui-verify` — przeklikanie ścieżki pracownika terenowego w realnej przeglądarce w szerokości 375 px: logowanie → wybór organizacji → lista obiektów → obiekt z alarmem → wykres → powrót.

### Deliverable

Zmiany w kodzie + krótki `docs/technical/frontend/breakpoints.md` z ustalonymi progami i wzorcami (jeden wzorzec na problem, nie trzy).

---

## B-13 🟡 Dofinansowania dla gmin i polityki wsparcia

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b13-dofinansowania` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `explorer` (WebSearch + WebFetch) → `documentation-writer`
**Przeczytaj najpierw:** [`01_plan_biznesowy.md` §4.1–4.2](../business/01_plan_biznesowy.md) (model przychodów i koszty), [§5.1](../business/01_plan_biznesowy.md) (segment klienta), [ADR-0003](../business/adr/0003-revenue-model-hardware-plus-subscription.md)

### Kontekst — dlaczego to jest ważniejsze, niż wygląda

Cały model finansowy zakłada, że gmina płaci **z własnego budżetu**: 2,9–8,3 tys. zł jednorazowo za obiekt plus 130–170 zł miesięcznie. Dla gminy 1000–20000 mieszkańców z 10 obiektami to jest wydatek rzędu 30–80 tys. zł na starcie — kwota, która w budżecie takiej gminy wymaga uzasadnienia i często odłożenia na kolejny rok.

Jeśli koszt jednorazowy da się sfinansować z dotacji, **argument sprzedażowy zmienia się jakościowo**: z „to kosztuje 50 tys. zł" na „to kosztuje gminę tylko abonament, resztę pokrywa program X, a my pomożemy w papierach". Plan biznesowy nie porusza tego tematu ani razu.

### Zakres

1. **Inwentaryzacja programów** aktualnych w 2026 r., dostępnych dla polskich gmin i ZWiK na cyfryzację/monitoring infrastruktury wodociągowej. Kierunki do sprawdzenia (agent ma zweryfikować, które faktycznie żyją i czy nabory są otwarte): KPO, FEnIKS, programy NFOŚiGW i **wojewódzkich** WFOŚiGW, PROW / Plan Strategiczny WPR dla obszarów wiejskich, Polski Ład / Rządowy Fundusz Inwestycji Lokalnych, „Cyfrowa Gmina" i jej następcy, programy regionalne w ramach RPO (FEM dla małopolskiego, FEP dla podkarpackiego), oraz finansowanie związane z wdrażaniem NIS2/KSC.

   **Priorytet regionalny:** pierwszy klient będzie w **małopolskim albo podkarpackim**. Zrób pełny, szczegółowy przegląd dla **WFOŚiGW w Krakowie** i **WFOŚiGW w Rzeszowie** oraz programów regionalnych tych dwóch województw. Pozostałe 14 funduszy wojewódzkich potraktuj skrótowo — wystarczy tabela zbiorcza pokazująca, czy warunki są zbliżone, żeby wiadomo było, na ile materiał przeniesie się na inne regiony przy kolejnym kliencie.
2. **Dla każdego żywego programu:** beneficjent (gmina czy spółka komunalna — to istotna różnica, bo ZWiK bywa spółką), zakres kosztów kwalifikowalnych, **czy sprzęt IoT się kwalifikuje**, **czy abonament SaaS się kwalifikuje** (zwykle trudniejsze niż sprzęt — sprawdź to szczególnie), poziom dofinansowania, wkład własny, progi kwotowe, harmonogram naborów, wymagana dokumentacja.
3. **Ograniczenia i pułapki** — okresy trwałości projektu (czy gmina musi utrzymać system przez N lat), zakaz zmiany dostawcy w okresie trwałości, wymogi przetargowe przy projektach dotowanych, konsekwencje dla struktury umowy.
4. **Powiązanie z PZP** — zamówienia finansowane z dotacji mają często zaostrzone wymogi proceduralne. Zasygnalizuj, jak to wpływa na ścieżkę sprzedaży.
5. **Materiał operacyjny** — jednostronicowy materiał „jak o tym rozmawiać z gminą": które programy pasują do jakiego profilu gminy, co gmina musi zrobić, w czym możesz pomóc (a w czym nie — nie jesteś doradcą dotacyjnym i nie bierzesz za to odpowiedzialności).

### Ograniczenia

- **Wszystko z datą i linkiem do źródła.** Programy dotacyjne zmieniają się co kwartał — informacja bez daty jest bezwartościowa. Oznacz wprost, kiedy dane sprawdzano.
- Rozróżniaj **nabór otwarty** / **zapowiedziany** / **zakończony** / **archiwalny**.
- To nie jest doradztwo dotacyjne — oznacz jako materiał roboczy wymagający potwierdzenia u operatora programu.
- **Gmina pilotażowa pozostaje anonimowa.** Dokumentacja projektu celowo nie ujawnia jej nazwy ([`CONTEXT.md`](../business/CONTEXT.md)) i ten dokument też nie ma jej ujawniać. Pisz o „województwie małopolskim/podkarpackim", nigdy o konkretnej gminie — nawet jeśli natrafisz na jej nazwę w innych materiałach.

### Deliverable

`docs/business/05_dofinansowania_dla_gmin.md`: tabela programów z datą weryfikacji, sekcja o kwalifikowalności sprzętu vs. abonamentu, pułapki okresu trwałości, jednostronicowy materiał do rozmowy z gminą.

### Definicja ukończenia

Da się odpowiedzieć gminie na pytanie „a czy da się to z czegoś sfinansować" konkretną nazwą programu, terminem naboru i poziomem dofinansowania — zamiast „chyba coś było".

---

## B-15 🟢 Mapa rynku — wszyscy gracze na polskim rynku, bezpośredni vs. pozostali

**Start:** repozytorium `waterworks-monitoring-platform` (katalog główny: `d:\dev\WebApps\waterworks-monitoring-platform`). Przed rozpoczęciem: `git checkout main`, sprawdź że jest czysto (`git status`) — **jeśli nie jest, zatrzymaj się i zgłoś stan zamiast kontynuować**: nie mieszaj cudzych niezacommitowanych zmian ze swoją pracą na nowej gałęzi. Jeśli jest czysto, `git checkout -b brief/b15-mapa-rynku` (z aktualnego `main`; jeśli branch już istnieje, kontynuuj na nim). Cała praca tego zlecenia zostaje na tej gałęzi — nie merguj do `main` bez wyraźnej zgody.
**Agent:** `explorer` (WebSearch + WebFetch, dużo) → `documentation-writer`
**Przeczytaj najpierw:** [`01_plan_biznesowy.md` §5.1](../business/01_plan_biznesowy.md) (rynki docelowe, kryteria SAM), [§5.2](../business/01_plan_biznesowy.md) (analiza konkurencji — **już istnieje, 9 podmiotów z pogłębioną analizą, nie powtarzaj tych opisów**), [§5.2.1](../business/01_plan_biznesowy.md) (6 kategorii rynkowych — użyj tej samej taksonomii)
**Rozgraniczenie:** to zlecenie idzie w **szerz**, nie w głąb — pełny spis graczy z jasną klasyfikacją, nie kolejny pogłębiony profil. Głębokie profile techniczne i UX konkretnych podmiotów to B-02 i B-03; ten brief może wskazać, które dodatkowe podmioty warto tam włączyć, ale sam ich nie analizuje w tym stopniu szczegółowości.

### Kontekst

§5.2 planu biznesowego ma już pogłębioną analizę 9 konkretnych podmiotów (Inventia, AquaRD, UniCloud, NASUS, Hydro-Vacuum, Metalchem, Hydro-Partner, Hawle.live, WaterPrime) plus Kallipr jako wzorzec zagraniczny. To dobra głębia, ale ograniczona szerokość — nie wiadomo, **ilu jeszcze graczy działa na polskim rynku** i, co ważniejsze, nie ma jednoznacznej reguły odróżniającej **bezpośredniego konkurenta** od podmiotu, który tylko wygląda na konkurenta (np. dostawca SCADA dla dużych miast — inny budżet, inny proces zakupowy, inny produkt, mimo że słowo „monitoring wodociągów" pasuje do obu).

### Zakres

1. **Zbuduj pełny spis**, nie tylko pogłębiaj istniejące 9. Szukaj w każdej z 6 kategorii z [§5.2.1](../business/01_plan_biznesowy.md): chmurowa SCADA abonamentowa, telemetria przemysłowa/RTU, kompleksowe smart water, producenci pomp/przepompowni, integratorzy AKPiA, wyspecjalizowane IoT. Nie ograniczaj się do firm już wymienionych w planie.
2. **Źródło o wysokiej wiarygodności, którego plan jeszcze nie użył:** przeszukaj **historyczne postępowania o udzielenie zamówienia publicznego** (portal e-Zamówienia, archiwalny BZP, ewentualnie ogłoszenia na stronach BIP małych gmin) pod kątem „monitoring/telemetria wodociągów", „system SCADA wod-kan", „zdalny odczyt/nadzór przepompowni". To pokazuje, **kto faktycznie wygrywa kontrakty w segmencie małych gmin** — twardszy sygnał niż strona marketingowa firmy. Zanotuj, jeśli natrafisz na rząd wielkości cen z realnych postępowań — to cenna weryfikacja szacunków z [§4.2](../business/01_plan_biznesowy.md).
3. **Dodatkowe źródła:** Izba Gospodarcza „Wodociągi Polskie" (IGWP) — członkowie/partnerzy branżowi, targi branżowe (np. targi WOD-KAN), wyszukiwarki firm (KRS/CEIDG dla weryfikacji, że firma faktycznie istnieje i działa).
4. **Dla każdego znalezionego podmiotu** (nowego i już opisanego w §5.2 — dla tych drugich wystarczy odesłanie, nie przepisuj): nazwa, kategoria (z taksonomii §5.2.1), segment docelowy (na podstawie publicznych informacji — wielkość miast/gmin, sektor), model biznesowy (abonament/CAPEX/projektowy), i **werdykt klasyfikacji** (patrz niżej).

### Klasyfikacja — kryterium, nie wrażenie

Dla każdego podmiotu jedna z trzech etykiet, uzasadniona przez **kryteria SAM z [§5.1.2](../business/01_plan_biznesowy.md)** (target: małe gminy 1000–20000 mieszkańców, 5–15 rozproszonych obiektów; **nie target**: duże miasta, krajowi operatorzy z gotowym SCADA, gminy z <3 obiektami):

- **Bezpośredni konkurent** — realnie konkuruje o tego samego klienta (mała gmina/ZWiK, budżet rzędu kilku–kilkunastu tys. zł na obiekt, model abonamentowy lub zbliżony).
- **Konkurent pośredni / sąsiedni segment** — działa w pokrewnej kategorii, ale celuje w innego klienta (np. SCADA dla dużych miast, projekt na miarę zamiast produktu, budżet o rząd wielkości większy) — **wyjaśnij konkretnie, dlaczego** nie trafia w nasz segment, nie tylko że „jest inny".
- **Do obserwacji** — dziś nie konkuruje bezpośrednio, ale ma zdolność zejścia w dół rynku (np. istniejący dostawca dla dużych miast z tanim wariantem w planach) — realne ryzyko na przyszłość, nie tylko teoretyczne.

### Decyzje już podjęte

- **Zakres: polski rynek.** To odróżnia ten brief od B-02, który celowo szuka szeroko za granicą — tu chodzi o kompletność mapy krajowej, nie o wzorce światowe.
- Nie przepisuj profili już opisanych w §5.2 — dla nich sam **werdykt klasyfikacji** jest nową wartością tego zlecenia, bo dziś plan opisuje ich jakościowo, ale nie ma jednej czytelnej tabeli bezpośredni/pośredni/do obserwacji.
- **Dokument po polsku**, jak reszta dokumentacji.

### Ograniczenia

- **Każdy podmiot z linkiem do źródła.** Jeśli klasyfikacja opiera się na przypuszczeniu (np. brak jawnych informacji o segmencie klienta), oznacz to wprost jako **przypuszczenie**, nie pewnik.
- Nie każdy trop z przetargów da się jednoznacznie przypisać do dostawcy (ogłoszenia bywają ogólne) — gdzie się nie da, napisz „nieustalone", nie zgaduj.
- To nie jest kolejna wersja §5.2 — nie przepisuj istniejącej analizy, rozszerzaj ją.

### Deliverable

`docs/business/06_mapa_rynku_konkurencji.md`: tabela pełnego spisu (podmiot × kategoria × segment × model biznesowy × klasyfikacja × źródło), osobna sekcja podsumowująca liczbę graczy w każdej z trzech klasyfikacji, oraz krótka lista „podmioty warte pogłębionej analizy w B-02/B-03, których tam jeszcze nie ma".

### Definicja ukończenia

Da się odpowiedzieć jednym zdaniem i bez wahania na pytanie „czy firma X jest naszą konkurencją" dla każdego podmiotu na liście — z uzasadnieniem opartym na kryteriach SAM, nie na wrażeniu.

