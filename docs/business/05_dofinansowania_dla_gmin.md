# Dofinansowania dla gmin i polityki wsparcia

**Status dokumentu:** materiał roboczy zespołu sprzedaży i zarządu. **To nie jest doradztwo dotacyjne.** Każde ustalenie wymaga potwierdzenia u operatora programu przed powołaniem się na nie w rozmowie z gminą.

**Data weryfikacji źródeł: 5 września 2026.** Programy dotacyjne zmieniają się co kwartał — informacja bez daty jest bezwartościowa, dlatego każda pozycja w tabelach ma własną datę sprawdzenia i link. Po 3 miesiącach od tej daty dokument należy uznać za wymagający przeglądu (patrz [rozdział 10](#10-kalendarz-monitorowania-i-pytania-do-operatorów-programów)).

**Zakres geograficzny:** cała Polska w ujęciu przeglądowym, **pogłębiony przegląd dla województw małopolskiego i podkarpackiego** — tam będzie pierwszy klient. Zgodnie z [`CONTEXT.md`](./CONTEXT.md) gmina pilotażowa pozostaje anonimowa; dokument nie wskazuje jej nazwy ani lokalizacji dokładniejszej niż województwo.

**Powiązania:** [`01_plan_biznesowy.md` §4.1–4.2](./01_plan_biznesowy.md#41-model-biznesowy--przychody) (model przychodów i koszty), [§5.1](./01_plan_biznesowy.md#51-rynki-docelowe) (segment klienta), [ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md) (model hardware + abonament), [brief B-13](../plan/01_briefy_dla_agentow.md).

---

## Streszczenie — odpowiedź na pytanie „a czy da się to z czegoś sfinansować"

**Tak, ale prawie nigdy jako samodzielny projekt.** Nasza instalacja u typowej gminy to 29–83 tys. zł jednorazowo ([§4.1.1](./01_plan_biznesowy.md#411-wdrożenie-one-time): 2,9–8,3 tys. zł × 10 obiektów). Każdy program, który w ogóle ustala próg minimalny, ustawia go **wyżej niż cała nasza dostawa**:

| Program | Próg minimalny | Nasza dostawa mieści się? |
|---|---|---|
| WFOŚiGW Katowice — „Bezpieczeństwo dostaw wody pitnej" | 200 tys. zł łącznego dofinansowania | nie |
| NFOŚiGW — gospodarka wodno-ściekowa poza aglomeracjami | 300 tys. zł wartości przedsięwzięcia | nie |
| KPO B3.1.1 (zakończony) | 1 mln zł wsparcia | nie |
| PS WPR I.10.10.B „Inteligentna wieś" | 1,5 mln zł kosztów kwalifikowalnych | nie |

Dwa najważniejsze dla nas nabory regionalne (FEM 13.1, FEP 12.1) **nie mają jawnego progu minimalnego**, ale ich konstrukcja — projekt infrastrukturalny, wskaźniki liczone w kilometrach sieci i obiektach, koszty pośrednie liczone od kosztów bezpośrednich — sprawia, że samodzielny wniosek na kilkadziesiąt tysięcy złotych byłby w ocenie punktowej niekonkurencyjny **(przypuszczenie — do zweryfikowania w kryteriach wyboru projektów)**.

**Wniosek strategiczny: nie sprzedajemy „projektu dotacyjnego", tylko wchodzimy jako komponent cudzej inwestycji wodociągowej.** Gmina i tak modernizuje SUW, buduje zbiornik albo wymienia sieć — nasz monitoring to pozycja w tym samym wniosku, warta kilka procent budżetu projektu i podnosząca jego punktację (bezpieczeństwo dostaw, ograniczenie strat wody, ciągłość działania). To zmienia moment sprzedaży: **trzeba być w rozmowie zanim gmina złoży wniosek**, a nie po.

**Trzy konkretne okna, o których można rozmawiać już dziś:**

1. **Małopolska — FEM 13.1 „Wzmacnianie bezpieczeństwa wodnego", nabór 14.10–4.12.2026, dotacja do 75%**, max 3 mln zł dofinansowania UE na projekt, **jeden wniosek na gminę**. Obligatoryjnym elementem każdego projektu są działania zapewniające „ciągłość działania systemów wodno-kanalizacyjnych" — to dokładnie opis naszego produktu. ([szczegóły](#31-małopolska--fem-131-wzmacnianie-bezpieczeństwa-wodnego))
2. **Podkarpacie — FEP 12.1 „Bezpieczeństwo dostaw wody", nabór zapowiedziany na I kw. 2027, 113,9 mln zł.** Opis typu projektu wprost mówi o „doposażaniu [infrastruktury] w rozwiązania zwiększające bezpieczeństwo, **monitoring** i niezawodność" oraz o „inwestycjach w ograniczenie strat wody". ([szczegóły](#32-podkarpacie--fep-121-bezpieczeństwo-dostaw-wody))
3. **WFOŚiGW — pożyczka z umorzeniem, nabór ciągły przez cały rok.** W Krakowie umorzenie do 30% pożyczki dla zadań z zakresu ochrony wód, w Rzeszowie pożyczka do 100% kosztów kwalifikowanych (nabór 9.02–27.11.2026). Ścieżka wolniejsza i mniej atrakcyjna niż dotacja, ale dostępna poza terminami naborów unijnych. ([szczegóły](#4-wfośigw--kraków-i-rzeszów-szczegółowo))

**Dwie rzeczy, które trzeba powiedzieć gminie uczciwie:**

- **Sprzęt i wdrożenie kwalifikują się bez problemu. Abonament — warunkowo i tylko na czas trwania projektu.** Koszty operacyjne w projektach EFRR są niekwalifikowalne, *chyba że* zostaną zatwierdzone we wniosku i poniesione w okresie kwalifikowalności ([szczegóły i cytat](#5-kwalifikowalność-sprzęt-vs-abonament)). Po zakończeniu projektu abonament płaci gmina z budżetu bieżącego — zawsze.
- **Dotacja wiąże gminę na 5 lat** (trwałość projektu) i wymusza wybór dostawcy w procedurze konkurencyjnej, w której nie wolno wskazać naszej nazwy. Dofinansowanie nie skraca ścieżki sprzedaży — ono ją wydłuża i sformalizuje ([rozdział 6](#6-pułapki--trwałość-własność-i-ciągłość-usługi) i [7](#7-pzp-i-zasada-konkurencyjności--co-to-zmienia-w-ścieżce-sprzedaży)).

---

## Jak czytać ten dokument

**Statusy naborów** (stan na 5.09.2026):

| Oznaczenie | Znaczenie |
|---|---|
| 🟢 **otwarty** | wnioski można składać dziś |
| 🟡 **zapowiedziany** | termin jest w oficjalnym harmonogramie, ogłoszenie/regulamin jeszcze nieopublikowane |
| 🔴 **zakończony** | nabór się odbył i został zamknięty; program może wrócić w kolejnej edycji |
| ⚪ **archiwalny** | program wygasł, brak zapowiedzi kontynuacji |

**Wiarygodność ustaleń:** twierdzenia bez adnotacji mają link do źródła pierwotnego (dokument programowy, ogłoszenie instytucji, akt prawny). Twierdzenia oznaczone **(przypuszczenie)** opierają się na źródle wtórnym albo na wnioskowaniu — nie należy ich powtarzać gminie jako pewnik. Oznaczenie **(nieustalone)** oznacza, że próba weryfikacji się nie powiodła i podano powód.

---

## 1. Inwentaryzacja programów — tabela zbiorcza

Kolumna „nasz sprzęt" odpowiada na pytanie, czy gateway + czujniki + wdrożenie mieszczą się w katalogu kosztów kwalifikowalnych. Kolumna „abonament" — czy da się w tym programie sfinansować opłatę za platformę (szerzej: [rozdział 5](#5-kwalifikowalność-sprzęt-vs-abonament)).

| # | Program / działanie | Instytucja | Beneficjent | Status naboru (5.09.2026) | Termin | Poziom i forma | Nasz sprzęt | Abonament |
|---|---|---|---|---|---|---|---|---|
| 1 | **FEM 13.1** Wzmacnianie bezpieczeństwa wodnego, typ A | UMWM (Departament Funduszy Europejskich) | JST, przedsiębiorstwa wod-kan, spółki wodne | 🟡 zapowiedziany | 14.10–4.12.2026 (konkurencyjny) | dotacja, **do 75%**, max 3 mln zł UE/projekt | **tak** | warunkowo |
| 2 | **FEP 12.1** Bezpieczeństwo dostaw wody | UMWP (Departament Wdrażania Projektów Infrastrukturalnych RPO) | JST, podmioty świadczące usługi publiczne | 🟡 zapowiedziany | I–II 2027 (konkurencyjny) | dotacja, % nieustalony (w FEP 2.6 było do 85%) | **tak** | warunkowo |
| 3 | **WFOŚiGW Kraków** — pożyczka + umorzenie (ochrona wód) | WFOŚiGW w Krakowie | JST, spółki komunalne, przedsiębiorcy | 🟢 otwarty (tryb ciągły) | cały 2026 r. | pożyczka (opr. od 2,00–3,50%), **umorzenie do 30%** | **tak** | nie |
| 4 | **WFOŚiGW Rzeszów** — pożyczka na zadania z ochrony środowiska i gospodarki wodnej | WFOŚiGW w Rzeszowie | podmioty korzystające ze środowiska (w tym JST) | 🟢 otwarty (tryb ciągły) | 9.02–27.11.2026 | pożyczka lub pożyczka + dotacja, **do 100%** kosztów kwalifikowanych | **tak** | nie |
| 5 | **WFOŚiGW Katowice** — „Bezpieczeństwo dostaw wody pitnej" | WFOŚiGW w Katowicach | JST, spółki komunalne (>50% udziałów JST) | 🟢 otwarty | 6.02.2026–29.10.2027 | dotacja do 30% (JST) + obowiązkowa pożyczka; max dotacja 500 tys. zł, **min. 200 tys. zł łącznie** | **tak** (monitoring wprost w zakresie) | nie |
| 6 | **NFOŚiGW** — Gospodarka wodno-ściekowa poza granicami aglomeracji | NFOŚiGW | JST i związki, podmioty realizujące zadania własne gmin | 🟢 otwarty | 31.07.2025–30.06.2029 | pożyczka do 100%, WIBOR 3M (min. 2%), **min. 300 tys. zł** | tylko przy zadaniach **ściekowych** | nie |
| 7 | **NFOŚiGW** — Gospodarka wodno-ściekowa w aglomeracjach | NFOŚiGW | JST, przedsiębiorstwa wod-kan | 🟢 otwarty | do 29.10.2027 | dotacja i pożyczka inwestycyjna | tylko w aglomeracjach KPOŚK | nie |
| 8 | **NFOŚiGW** — Adaptacja do zmian klimatu | NFOŚiGW | JST i związki, spółki, wspólnoty | 🟢 otwarty / 🟡 II nabór | do 30.09.2026; II nabór 1.10.2026–30.06.2034 | pożyczka do 100%, dotacja do 70% (retencja) | słabe dopasowanie (zieleń, wody opadowe) | nie |
| 9 | **FEnIKS 2.5** Woda do spożycia | NFOŚiGW | JST, przedsiębiorstwa wod-kan | 🔴 zakończony | ostatni nabór do 3.06.2024 | dotacja do 70% | tak, ale **próg 15 tys. mieszkańców** | nie |
| 10 | **FEnIKS 1.3** Gospodarka wodno-ściekowa | NFOŚiGW | JST, przedsiębiorstwa wod-kan, spółki wodne | 🔴 zakończony | 1.12.2025–31.03.2026 | dotacja | tylko aglomeracje KPOŚK | nie |
| 11 | **KPO B3.1.1** Gospodarka wodno-ściekowa na terenach wiejskich | samorządy województw / MRiRW | gminy wiejskie i miejsko-wiejskie, spółki 100% JST, związki | ⚪ archiwalny | nabory XII 2024–VII 2025; realizacja do 30.06.2026 | 1–5 mln zł na gminę | **tak** (rozwiązania cyfrowe wprost w zakresie) | nie |
| 12 | **PS WPR I.10.10.B** Inteligentna wieś | samorządy województw / ARiMR | gmina, związek międzygminny | 🟡 terminy naborów ustalają samorządy województw — **nie zweryfikowano** dla małopolskiego i podkarpackiego | wniosek o płatność do 30.06.2029 | 30–75%, max 10 mln zł, **min. 1,5 mln zł kosztów kwalifikowalnych** | tak, jako element koncepcji smart village | (przypuszczenie) nie |
| 13 | **PS WPR I.10.10.A** Indywidualne oczyszczanie ścieków | samorządy województw / ARiMR | gmina, związek międzygminny | 🔴 zakończony (Podkarpacie 1–31.12.2025) | — | do 75% | nie (przydomowe oczyszczalnie) | nie |
| 14 | **FERC 4.1** Lokalne Centra Cyberbezpieczeństwa | CPPC | JST (partnerstwa) | 🟢 otwarty | 31.07–30.10.2026 | ok. 269,6 mln zł; 100% kosztów kwalifikowalnych (przypuszczenie — do potwierdzenia w regulaminie) | nie wprost (sprzęt i oprogramowanie ochrony sieci) | nie |
| 15 | **FERC 2.2** Cyberbezpieczny Samorząd | CPPC | wszystkie JST | ⚪ archiwalny | nabór 19.07–14.12.2023 | granty 200–850 tys. zł | nie wprost | nie |
| 16 | **Rządowy Fundusz Polski Ład: PIS** | BGK / KPRM | JST i ich związki | ⚪ brak potwierdzonego naboru | ostatnie edycje 2023 r. | do 95% bezzwrotnie | tak, gdyby wrócił | nie |
| 17 | **Program Ochrony Ludności i Obrony Cywilnej 2025–2026** | MSWiA / wojewodowie | JST | 🟡 nabory prowadzą wojewodowie | środki na 2026 r. przekazywane do 31.03.2026 | do 100% | słabe dopasowanie (mobilne SUW, zbiorniki, cysterny) | nie |

**Czego w tej tabeli nie ma i dlaczego:** „Cyfrowa Gmina" (POPC/REACT-EU) wygasła wraz z perspektywą 2014–2020 i nie ma bezpośredniego następcy dla infrastruktury komunalnej — jej rolę przejęły FERC (cyberbezpieczeństwo) i programy regionalne. Programy PROW 2014–2020 zakończyły okres kwalifikowalności; ich funkcję przejął PS WPR 2023–2027 (poz. 12–13).

---

## 2. Programy krajowe — co żyje, a co już nie

### 2.1. KPO — okno się zamknęło, ale zostawiło precedens

KPO było **najlepiej dopasowanym programem w historii tego rynku** i już go nie ma. Inwestycja **B3.1.1 „Inwestycje w zrównoważoną gospodarkę wodno-ściekową na terenach wiejskich"** wprost wymieniała jako wspierany typ przedsięwzięcia „infrastrukturę wykorzystującą rozwiązania cyfrowe" — inteligentne wodomierze ze zdalnym odczytem i systemy teleinformatyczne do zarządzania gospodarką wodno-kanalizacyjną — obok budowy i modernizacji sieci ([ogłoszenie o naborze, woj. śląskie, publ. 20.11.2024](https://prow.slaskie.pl/pl/aktualnosci/ogloszenie-o-naborze-wnioskow-w-ramach-inwestycji-b311-inwestycje-w-zrownowazona-gospodarke-wodno-sciekowa-na-terenach-wiejskich-kpo.html)).

- **Beneficjenci:** gminy wiejskie i miejsko-wiejskie (z wyłączeniem miast powyżej 5 tys. mieszkańców), spółki ze 100% udziałem JST, związki międzygminne.
- **Wsparcie:** od 1 mln zł do 5 mln zł, przy czym limit 5 mln zł liczony jest **na obszar gminy** ([nabór woj. małopolskie, publ. 23.12.2024](https://www.funduszeunijne.gov.pl/nabory/woj-malopolskie-nabor-wnioskow-w-inwestycji-b311-inwestycje-w-zrownowazona-gospodarke-wodno-sciekowa-na-terenach-wiejskich/); alokacja małopolska: 61 325 189 zł).
- **Status:** 🔴 nabory zamknięte (Małopolska — 15.01.2025; druga tura w części województw do lipca 2025). Termin **zakończenia realizacji inwestycji wod-kan na obszarach wiejskich przedłużono do 30.06.2026** ([kpo.gov.pl, 16.06.2026](https://www.kpo.gov.pl/strony/aktualnosci/wiecej-czasu-na-inwestycje-z-kpo-rolnicy-przedsiebiorcy-i-samorzady-zyskaja-dodatkowe-miesiace/)), a całe KPO jest w fazie rozliczania. **Nowych naborów nie będzie.**

**Co z tego zostaje:** twardy dowód, że administracja publiczna uznaje cyfryzację gospodarki wodnej za koszt kwalifikowalny, oraz świadomość, że część gmin w Małopolsce i na Podkarpaciu **właśnie skończyła** taką inwestycję i przez 5 lat trwałości nie będzie robić kolejnej. Przed rozmową warto sprawdzić, czy gmina realizowała B3.1.1 — jeśli tak, jej pieniądze i uwaga są już zaangażowane.

### 2.2. FEnIKS — dla nas praktycznie zamknięty

W **aktualnym harmonogramie naborów FEnIKS (wersja obowiązująca od 19.12.2025, sprawdzono 5.09.2026)** nie ma żadnego zaplanowanego naboru w działaniu **2.5 „Woda do spożycia"**. Jedyny nabór wod-kan z tego harmonogramu — **FENX.01.03**, kompleksowe projekty w aglomeracjach ujętych w KPOŚK, 720 mln zł — trwał od 1.12.2025 do 31.03.2026 i jest zamknięty. ([harmonogram FEnIKS](https://feniks.gov.pl/harmonogram-naborow-feniks/), [plik XLSX](https://feniks.gov.pl/wp-content/uploads/2026/01/Harmonogram_naborow_FEnIKS_19_12_2025.xlsx))

Nawet gdyby 2.5 wróciło, **próg wielkości wyklucza nasz segment**: nabory z 2023 i 2024 r. dotyczyły zaopatrzenia w wodę gmin liczących **co najmniej 15 tys. mieszkańców**, a dla mniejszych gmin dopuszczano wyłącznie sieci magistralne. Maksymalne dofinansowanie: 70% wydatków kwalifikowalnych ([karta naboru 2.5, zakończony 3.06.2024](https://funduszeunijne.gov.pl/nabory/25-woda-do-spozycia-niekonkurencyjny/)). Nasz SAM to gminy 1000–20000 mieszkańców ([§5.1.2](./01_plan_biznesowy.md#512-kryteria-dobrego-klienta-sam)) — większość odpada z definicji.

**Wniosek: FEnIKS wykreślamy z materiałów sprzedażowych.** Wymienianie go w rozmowie z małą gminą to strata wiarygodności.

### 2.3. NFOŚiGW — pożyczki, nie dotacje, i głównie ścieki

Program **„Gospodarka wodno-ściekowa poza granicami aglomeracji ujętych w KPOŚK"** (nabór 🟢 31.07.2025–30.06.2029, budżet do 100 mln zł) jest najbliższy naszemu segmentowi geograficznie, ale nie tematycznie:

- forma wsparcia to **pożyczka preferencyjna** (oprocentowanie WIBOR 3M, nie mniej niż 2%), do 100% kosztów kwalifikowanych, **minimalna wartość przedsięwzięcia 300 tys. zł**;
- w katalogu przedsięwzięć są „systemy cyfrowe do ewidencji zbiorników, oczyszczalni, monitoringu i sprawozdawczości", ale **kwalifikowalne wyłącznie łącznie z zadaniami ściekowymi** (oczyszczalnie, sieci kanalizacyjne, przyłącza, punkty zlewne, pojazdy asenizacyjne). To ewidencja zbiorników bezodpływowych, nie monitoring sieci wodociągowej. ([gov.pl/nfosigw](https://www.gov.pl/web/nfosigw/gospodarka-wodno-sciekowa-poza-granicami-aglomeracji))

Pozostałe programy NFOŚiGW z aktualnego harmonogramu (aktualizacja strony 3.09.2026, [harmonogram naborów NFOŚiGW](https://www.gov.pl/web/nfosigw/harmonogram-naborow)) też nie trafiają w nasz zakres: „Gospodarka wodno-ściekowa w aglomeracjach" dotyczy KPOŚK, „Mikroretencja" i „Adaptacja do zmian klimatu" — retencji i zielono-niebieskiej infrastruktury, FENX.10.01 „Odbudowa infrastruktury do zaopatrzenia w wodę po powodzi" (1.07–30.09.2026) — wyłącznie gmin z rządowego wykazu powodziowego.

### 2.4. PS WPR — jedyna żywa ścieżka „wiejska", ale duża

Po wygaśnięciu PROW rolę wsparcia obszarów wiejskich przejął **Plan Strategiczny dla WPR 2023–2027**, interwencja **I.10.10**, wdrażana przez samorządy województw:

- **obszar A** — inwestycje w systemy indywidualnego oczyszczania ścieków (przydomowe oczyszczalnie). Podkarpacie: nabór 1–31.12.2025, alokacja 61 973 478,95 zł ([ogłoszenie UMWP, publ. 5.11.2025](https://prow.podkarpackie.pl/index.php/test-1/430-nabor-wnioskow-o-przyznanie-pomocy-dla-interwencji-i-10-10-infrastruktura-na-obszarach-wiejskich-oraz-wdrozenie-koncepcji-inteligentnych-wsi-obszar-a-inwestycje-w-zakresie-systemow-indywidualnego-oczyszczania-sciekow)). **Nie nasz zakres.**
- **obszar B — „Inteligentna wieś"**: beneficjentem jest gmina lub związek międzygminny, intensywność pomocy **30–75%** kosztów kwalifikowalnych, pomoc **do 10 mln zł**, przy czym operacja musi mieć **koszty kwalifikowalne powyżej 1,5 mln zł**; wniosek o płatność do 30.06.2029 (podstawa: komunikat MRiRW z 9.07.2025, M.P. 2025 poz. 643; [karta interwencji, DPROW UMWW](https://dprow.umww.pl/interwencje/i-10-10-b-wdrozenie-koncepcji-inteligentnych-wsi/)). Kryteria oceny premiują m.in. **komponent cyfrowy** i innowacyjność ([MRiRW](https://www.gov.pl/web/rolnictwo/i1010-infrastruktura-na-obszarach-wiejskich-oraz-wdrozenie-koncepcji-inteligentnych-wsi)).

**Jak to wykorzystać:** monitoring wodociągów jako element „inteligentnej wsi" jest sensownym uzasadnieniem merytorycznym, ale wymaga, żeby gmina budowała projekt o wartości ≥1,5 mln zł i miała opracowaną koncepcję smart village. To ścieżka dla gminy ambitnej i przygotowanej — nie dla pierwszego kontaktu.

### 2.5. Polski Ład — nieaktywny, warto obserwować

Rządowy Fundusz Polski Ład: Program Inwestycji Strategicznych oferował do **95% bezzwrotnego dofinansowania** dla dowolnych inwestycji JST i był kiedyś najprostszą drogą do sfinansowania czegokolwiek. Ostatnie potwierdzone nabory to edycja ósma (20.07–16.08.2023) i dziewiąta („Rozświetlamy Polskę"). **Na dzień 5.09.2026 nie znaleziono ogłoszenia o nowym naborze.** Serwis BGK blokuje zautomatyzowany dostęp (HTTP 403 / weryfikacja przeglądarki), więc status należy **potwierdzić ręcznie** na [bgk.pl/polski-lad](https://www.bgk.pl/polski-lad/) — **(nieustalone)**.

Gdyby program wrócił, byłby dla nas najlepszą opcją: brak ograniczeń tematycznych, wysoki poziom dofinansowania, wniosek składany przez gminę bez skomplikowanej dokumentacji projektowej.

### 2.6. Program Ochrony Ludności i Obrony Cywilnej 2025–2026 — dopasowanie pozorne

Program (M.P. 2025 poz. 541) obejmuje m.in. „zapewnienie ciągłości dostaw wody", dotacje rozdzielają wojewodowie, poziom dofinansowania sięga 100%, a środki na 2026 r. miały być przekazane do 31.03.2026. Problem w tym, że **katalog wspieranego wyposażenia to sprzęt kryzysowy** — mobilne stacje uzdatniania, zbiorniki elastyczne, cysterny, środki do dezynfekcji ujęć — a **monitoring, telemetria ani systemy pomiarowe nie są w nim wymienione** ([przegląd zadań wodnych programu, 19.03.2026](https://euroclean.pl/artykuly-o-wodzie/zachowanie-ciaglosci-dostaw-wody-w-ramach-programu-ochrony-ludnosci-i-obrony-cywilnej-na-lata-2025-2026/)). Traktujemy jako **słabe dopasowanie**; nie budujemy na tym argumentacji.

---

## 3. Programy regionalne — Małopolska i Podkarpacie

W obu województwach w 2026 r. wydarzyła się ta sama rzecz: **w wyniku przeglądu śródokresowego programów regionalnych powstały nowe priorytety poświęcone bezpieczeństwu dostaw wody.** To nie jest kosmetyka — to nowa pula pieniędzy z opisem interwencji, który wymienia monitoring i ciągłość działania jako cel sam w sobie, a nie jako dodatek do rury. Dla nas jest to najważniejsze ustalenie całego dokumentu.

### 3.1. Małopolska — FEM 13.1 „Wzmacnianie bezpieczeństwa wodnego"

**Źródło:** [Szczegółowy Opis Priorytetów FEM 2021–2027, wersja SZOP.FEMP.030, obowiązuje od 18.08.2026](https://fundusze.malopolska.pl/sites/default/files/2026/08/3342/1_zalacznik%20nr%201%20do%20uchwaly_SZOP.FEMP_.030.pdf) (str. 726–731) oraz [harmonogram naborów FEM, wersja z 2.09.2026](https://fundusze.malopolska.pl/harmonogram). Sprawdzono 5.09.2026.

| Parametr | Wartość |
|---|---|
| Alokacja działania | 47 368 421 EUR ogółem (45 mln EUR ze środków UE) |
| Nabór konkurencyjny | 🟡 **14.10.2026 – 4.12.2026**, alokacja **161 317 409,49 zł** |
| Nabór niekonkurencyjny | 🟡 X–XII 2026, 30 288 090,51 zł — beneficjentem jest wskazana z nazwy gmina wraz z partnerami |
| Forma wsparcia | dotacja |
| Maksymalny poziom dofinansowania | **75%** wydatków kwalifikowalnych; minimalny wkład własny **25%** |
| Maksymalne dofinansowanie UE na projekt | **3 mln zł** (tryb konkurencyjny) |
| Limit wniosków | **jeden wniosek na obszar danej gminy**, niezależnie od wnioskodawcy |
| Beneficjenci | JST i ich związki, jednostki organizacyjne działające w ich imieniu, przedsiębiorstwa wodociągowo-kanalizacyjne, spółki wodne, podmioty świadczące usługi publiczne w ramach zadań własnych gminy |
| Koszty pośrednie | 3% bezpośrednich kosztów kwalifikowalnych |
| Cross-financing | 0% |

**Dlaczego to jest nasz nabór.** Typ projektu A dzieli się na dwa obszary, a **obszar I jest obligatoryjny w każdym projekcie**: „Obligatoryjnym elementem projektu będą adekwatne i uzasadnione działania wskazane w obszarze I. Bezpieczeństwo działania systemów wodno-kanalizacyjnych". W katalogu obszaru I znajduje się m.in. punkt 6: **„zapewnienie ciągłości działania systemów wodno-kanalizacyjnych"**. Nasz system — wczesne ostrzeganie o spadku ciśnienia, wykrycie utraty łączności z obiektem, alarm o awarii pompy — jest wprost realizacją tego punktu.

Potwierdza to lista wskaźników produktu działania, w której figuruje **WLWK-PLRO176 „Liczba nowych/zmodernizowanych stanowisk pomiarowych na potrzeby monitoringu stanu środowiska"**. Wskaźnik jest gotowym miejscem, w którym nasze punkty pomiarowe wpisują się do wniosku i do sprawozdawczości.

**Warunek zgodności, który gra na naszą korzyść.** Warunek nr 5 działania wymaga, żeby projekt wykazał zgodność z obszarami działań wskazanymi w **„Programie inwestycyjnym w zakresie poprawy jakości i ograniczenia strat wody przeznaczonej do spożycia przez ludzi"** (Ministerstwo Infrastruktury, czerwiec 2021; 14 obszarów działań, podrozdział 4.1.1). W tym dokumencie:

- **obszar 5 „SIEĆ DYSTRYBUCJI"** obejmuje wprost „monitorowanie (monitoring hydrauliczny i jakościowy) i modelowanie procesów" i jest sklasyfikowany jako **priorytetowy**;
- **obszar 6 „INFRASTRUKTURA IT"** oraz **obszar 7 „OCHRONA FIZYCZNA I CYBERBEZPIECZEŃSTWO"** — kategoria „zalecany";
- obszar 3 „UZDATNIANIE WODY" wymienia „monitorowanie operacyjne".

([Program inwestycyjny…, PDF, tabela 10, str. 42–45](https://www.gov.pl/attachment/edd4fc6f-0e68-4fc4-b60f-3eb5b1e016fb))

To jest gotowe uzasadnienie merytoryczne do wniosku: nasza pozycja w projekcie realizuje **priorytetowy** obszar krajowego programu inwestycyjnego dla wodociągów.

**Ograniczenia, o których trzeba wiedzieć:**

- inwestycje w gospodarkę **ściekową** są kwalifikowalne wyłącznie jako element projektu i nie mogą przekroczyć **50%** kosztów kwalifikowalnych;
- inwestycje **w zakresie gospodarki ściekowej** realizowane w aglomeracjach **od 15 tys. RLM są niekwalifikowalne**; obowiązuje priorytetyzacja: 1) aglomeracje 10–15 tys. RLM, 2) aglomeracje 2–10 tys. RLM, 3) inwestycje poza aglomeracjami — program celuje więc w mniejsze ośrodki, czyli w nasz segment;
- **warunek zgodności z dyrektywą ściekową 91/271/EWG nie dotyczy samodzielnych projektów obejmujących działania z Obszaru I** — czyli projekt złożony wyłącznie z działań „bezpieczeństwo działania systemów wod-kan" jest w SZOP przewidziany. To najważniejsza furtka dla nas i pierwsze pytanie do IZ (patrz [rozdział 10.2](#102-pytania-do-zadania-operatorom-programów));
- przydomowe oczyszczalnie oraz **przyłącza wodociągowe i kanalizacyjne** i urządzenia indywidualnych użytkowników (gdy właścicielem nie jest beneficjent) są niekwalifikowalne;
- 29.05.2026 IZ zapowiedziała **zmiany warunków wsparcia w SzOP dla działania 13.1**, będące odpowiedzią na postulaty gmin ([komunikat](https://fundusze.malopolska.pl/aktualnosc/14117-planowane-zmiany-szop-w-zakresie-dzialania-131-wzmacnianie-bezpieczenstwa-wodnego)). **Parametry z tabeli powyżej mogą się jeszcze zmienić** — przed rozmową z gminą sprawdź aktualną wersję SZOP i regulamin naboru;
- na 5.09.2026 **nie znaleziono opublikowanego ogłoszenia ani regulaminu wyboru projektów** dla tego naboru — jest on wyłącznie w harmonogramie. Regulamin doprecyzuje szczegółowe warunki wsparcia.

### 3.2. Podkarpacie — FEP 12.1 „Bezpieczeństwo dostaw wody"

**Źródło:** [harmonogram naborów FEP 2021–2027, wersja zatwierdzona 30.06.2026](https://funduszeue.podkarpackie.pl/harmonogram) ([plik XLSM](https://funduszeue.podkarpackie.pl/images/Dokumenty_2026/Pliki/Harmonogram%20naborow%20wnioskow%20o%20dofinansowanie%20dla%20programu%20regionalnego%20Fundusze%20Europejskie%20dla%20Podkarpacia%202021-2027%20z%2030.06.2.xlsm)). Sprawdzono 5.09.2026.

Priorytet 12 to jeden z pięciu nowych priorytetów FEP, zatwierdzonych **decyzją wykonawczą Komisji Europejskiej z 22.04.2026** ([komunikat UMWP, 24.04.2026](https://podkarpackie.pl/index.php/fundusze-eu/aktualnosci/od-strategicznego-bezpieczenstwa-po-lokalne-potrzeby-program-fep-w-dzialaniu)).

| Parametr | Wartość |
|---|---|
| Nabór | 🟡 zapowiedziany: **I 2027 – II 2027**, tryb konkurencyjny |
| Kwota dofinansowania w naborze | **113 881 150 zł** |
| Beneficjenci | JST oraz podmioty świadczące usługi publiczne w ramach realizacji zadań własnych JST |
| Instytucja | IZ — Departament Wdrażania Projektów Infrastrukturalnych RPO, UMWP |
| Cel szczegółowy | EFRR/FS.CP2.V — bezpieczny dostęp do wody, zintegrowane zarządzanie wodą, odporność wodna |
| Poziom dofinansowania | **(nieustalone)** — SZOP dla nowego priorytetu nie był dostępny w dniu weryfikacji; w poprzednim działaniu 2.6 maksymalny poziom dofinansowania UE wynosił **85%** |

**Opis typu projektu — cytat z harmonogramu (kolumna „Typy projektów"):**

> • Roboty budowlane, instalacyjne lub zakup wyposażenia w zakresie infrastruktury niezbędnej do ujęcia, uzdatniania, magazynowania i dystrybucji wody do spożycia oraz **doposażanie jej w rozwiązania zwiększające bezpieczeństwo, monitoring i niezawodność zwłaszcza w sytuacjach kryzysowych**
> • **Inwestycje w ograniczenie strat wody**

To najbardziej dosłowny opis naszego produktu, jaki znaleziono w jakimkolwiek polskim dokumencie programowym. Dwa zdania, dwa nasze argumenty sprzedażowe.

**Kalendarz przygotowań:** kryteria wyboru projektów dla większości nowych priorytetów FEP miały zostać zatwierdzone 11.06.2026, pozostałe we wrześniu 2026; pierwsze nabory z nowych priorytetów zapowiedziano na drugą połowę 2026 r. Nabór 12.1 jest w harmonogramie na I kw. 2027 — **to daje ok. pół roku na przygotowanie gminy**, co jest realistycznym horyzontem dla pierwszego wdrożenia komercyjnego.

**Historia dla kontekstu:** wcześniejsze działanie **FEPK.02.06 „Zrównoważona gospodarka wodno-ściekowa"** (nabór FEPK.02.06-IZ.00-003/23, 10.05–24.08.2023, 🔴 zakończony) obejmowało „roboty budowlane, instalacyjne lub zakup wyposażenia w zakresie infrastruktury niezbędnej do ujęcia, uzdatniania, magazynowania i dystrybucji wody" wraz z działaniami na rzecz **ograniczania strat wody**; maksymalne dofinansowanie **85%**, beneficjenci: JST i podmioty świadczące usługi publiczne w ich imieniu ([karta naboru](https://funduszeue.podkarpackie.pl/nabory-wnioskow/2-6-zrownowazona-gospodarka-wodno-sciekowa-nr-naboru-fepk-02-06-iz-00-003-23)). Warto to znać: gminy, które wtedy zrealizowały projekt, są w okresie trwałości i mogą mieć ograniczone pole manewru.

---

## 4. WFOŚiGW — Kraków i Rzeszów szczegółowo

Wojewódzkie fundusze to **jedyny kanał dostępny w trybie ciągłym przez cały rok**. Nie dają dotacji „z automatu" — podstawowym instrumentem jest pożyczka, a dotacja pojawia się albo jako umorzenie części pożyczki, albo w ramach osobno ogłaszanych programów.

**Podstawa prawna wspólna dla wszystkich 16 funduszy** to katalog zadań z art. 400a ust. 1 ustawy — Prawo ochrony środowiska. W katalogu tym są dwie pozycje, na których opieramy argumentację:

- „wspomaganie realizacji zadań modernizacyjnych i inwestycyjnych służących ochronie środowiska i gospodarce wodnej, w tym dotyczących (…) **zaopatrzenia ludności w wodę**";
- „wspomaganie realizacji zadań państwowego monitoringu środowiska, **innych systemów kontrolnych i pomiarowych** oraz badań stanu środowiska, a także **systemów pomiarowych zużycia wody** i ciepła".

(cyt. za: [Zasady finansowania zadań ze środków WFOŚiGW w Krakowie na rok 2026](https://www.wfos.krakow.pl/wp-content/uploads/2026/01/Zasady-finansowania-zadan-ze-srodkow-WFOSIGW-w-Krakowie-na-rok-2026.pdf), Wstęp, str. 3–4 — fundusz odwzorowuje tam katalog ustawowy)

### 4.1. WFOŚiGW w Krakowie (małopolskie)

**Obowiązujący dokument:** „Zasady finansowania zadań ze środków WFOŚiGW w Krakowie", uchwała Rady Nadzorczej nr 128/2025 z **19.12.2025**, obowiązuje od **1.01.2026** ([strona](https://www.wfos.krakow.pl/oferta/warunki-wsparcia-finansowego/zasady_finansowania_zadan_wfosigw_w_krakowie/), [PDF](https://www.wfos.krakow.pl/wp-content/uploads/2026/01/Zasady-finansowania-zadan-ze-srodkow-WFOSIGW-w-Krakowie-na-rok-2026.pdf)). Sprawdzono 5.09.2026.

| Parametr | Wartość |
|---|---|
| Formy pomocy | pożyczki, dotacje, nagrody za działalność ekologiczną, poręczenia, dofinansowanie państwowych jednostek budżetowych |
| Dotacje | **wyłącznie w ramach osobno ogłaszanych programów** i na warunkach w nich określonych (§21) — nie ma „dotacji na wniosek" |
| Umorzenie pożyczki | **do 30%** wykorzystanej kwoty dla zadań **związanych z ochroną wód** (z wyjątkiem przydomowych oczyszczalni); wniosek można złożyć po spłacie minimum 50% kapitału (§18) |
| Oprocentowanie pożyczek | min. **3,50%** do 5 mln zł, **2,60%** dla 5–10 mln zł, **2,00%** powyżej 10 mln zł (niższe stawki dla gmin o słabszej kondycji finansowej) |
| VAT | koszt kwalifikowany **tylko wtedy**, gdy beneficjent nie ma prawnej możliwości odliczenia (§22) |
| Ograniczenie zbycia majątku | sprzedaż, wydzierżawienie lub likwidacja majątku trwałego sfinansowanego ze środków Funduszu **w ciągu 5 lat od zakończenia zadania** jest podstawą do wypowiedzenia umowy pożyczki (§17 ust. 1 pkt 2 lit. g) |

**Precedens, który warto znać.** „Lista przedsięwzięć priorytetowych WFOŚiGW w Krakowie na 2026 rok" (uchwała nr 58/2025, [PDF](https://www.wfos.krakow.pl/wp-content/uploads/2025/06/Zalacznik-do-Uchwaly-nr-58-2025-.pdf)) zawiera zgłoszone przez gminy zadania wodociągowe, a w opisie jednego z nich — obok budowy sieci, SUW i remontu ujęcia — figuruje **„montaż słupków telemetrycznych na sieciach wodociągowych"**. To dowód, że telemetria na sieci jest w tym funduszu traktowana jako normalny element zadania wodociągowego, a nie egzotyka wymagająca tłumaczenia.

**Jak z tego korzystać:** lista przedsięwzięć priorytetowych powstaje z wniosków zgłaszanych przez potencjalnych beneficjentów. Jeśli gmina planuje zadanie wodociągowe na kolejny rok, **nasza pozycja powinna trafić do opisu zadania na etapie zgłoszenia do listy**, a nie dopiero do wniosku o pożyczkę.

### 4.2. WFOŚiGW w Rzeszowie (podkarpackie)

**Nabór 🟢 otwarty:** „Pożyczka na realizację zadań z dziedziny ochrony środowiska i gospodarki wodnej", tryb ciągły **9.02.2026 – 27.11.2026** ([ogłoszenie, publ. 9.02.2026](https://bip.wfosigw.rzeszow.pl/nabory-wnioskow/pozyczki/254-nabor-pozyczek-2026/1561-pozyczka-na-realizacje-zadan-z-dziedziny-ochrony-srodowiska-i-gospodarki-wodnej)). Równolegle prowadzony jest nabór na **pożyczki pomostowe** dla projektów współfinansowanych ze środków UE (ten sam okres) — instrument istotny, bo dotacje unijne działają w trybie refundacji.

| Parametr | Wartość |
|---|---|
| Intensywność | **do 100%** kosztów kwalifikowanych dla podmiotów spoza sfery komercyjnej (JST); do 80% dla przedsiębiorców |
| Koszty kwalifikowane (inwestycyjne) | roboty budowlane, **dostawy i usługi**, **zakup materiałów i urządzeń**, nadzór inwestorski i obsługa geodezyjna, rozruch mechaniczny i technologiczny, prace wstępne/przygotowawcze i promocja — łącznie **do 10%** kosztów inwestycyjnych |
| Wykluczenie | Fundusz **nie finansuje zadań zakończonych** ani elementów, na które faktury wystawiono przed złożeniem wniosku |
| Trwałość | **5 lat** od zakończenia zadania: obowiązek utrzymania przedsięwzięcia i niepoddawania go modyfikacjom mogącym negatywnie wpłynąć na efekt ekologiczny |
| Kryteria merytoryczne | m.in. wiarygodność danych będących podstawą wyliczenia **efektu ekologicznego**, posiadanie wymaganych decyzji administracyjnych oraz **„informacje o terminie i sposobie wyboru Wykonawcy"** ([Regulamin naboru, §3](https://bip.wfosigw.rzeszow.pl/images/pozyczka_dlugoterm_2026/regulamin_naboru_wnioskow_pozyczki.pdf)) |
| Zasady ogólne | „Zasady udzielania dofinansowania przez WFOŚiGW w Rzeszowie" obowiązujące od 22.04.2025 — **(nieustalone)**: serwis `wfosigw-rzeszow.bip.gov.pl` odrzucał połączenia (HTTP 503 / reset), treści nie udało się zweryfikować. Karencja, oprocentowanie i warunki umorzenia są uregulowane właśnie tam i **wymagają sprawdzenia przed rozmową** |
| Lista przedsięwzięć priorytetowych na 2026 | **(nieustalone)** — na BIP Funduszu najnowsza dostępna lista dotyczy 2024 r.; ogłoszenie o naborze odsyła do listy na 2026 r. w serwisie, który był niedostępny |

**Konsekwencja praktyczna „efektu ekologicznego":** wniosek do funduszu wojewódzkiego wymaga **wyliczonego, mierzalnego efektu**. Dla nas naturalną miarą jest **ograniczenie strat wody** (m³/rok) wynikające ze skrócenia czasu wykrycia awarii — a nie „lepszy wgląd w dane". To wymaga od nas przygotowania metodyki liczenia tego efektu na podstawie danych gminy (patrz [rozdział 9](#9-materiał-operacyjny--jak-o-tym-rozmawiać-z-gminą), sekcja „w czym pomagamy").

### 4.3. Pozostałe 14 funduszy — czy materiał się przeniesie

Sprawdzono wyrywkowo cztery fundusze poza Krakowem i Rzeszowem. **Wniosek: model jest wszędzie ten sam — pożyczka z możliwością częściowego umorzenia jako instrument bazowy, dotacja tylko w ramach dedykowanych programów.** Różnią się progi, poziomy umorzeń i to, czy fundusz ma akurat program wodociągowy.

| Fundusz | Instrument bazowy | Program dedykowany wodzie | Data weryfikacji |
|---|---|---|---|
| **Kraków** (małopolskie) | pożyczka, umorzenie do 30% (ochrona wód) | brak osobnego programu; zadania wodociągowe przez listę przedsięwzięć priorytetowych | 5.09.2026 |
| **Rzeszów** (podkarpackie) | pożyczka do 100% kosztów kwalifikowanych | brak osobnego programu; nabór ciągły na zadania z gospodarki wodnej | 5.09.2026 |
| **Katowice** (śląskie) | pożyczka; dotacja tylko łącznie z pożyczką | 🟢 **„Bezpieczeństwo dostaw wody pitnej"**, 6.02.2026–29.10.2027 — zakres wprost obejmuje **monitoring wody i cyberbezpieczeństwo**; dotacja do 30% dla JST, max 500 tys. zł, min. 200 tys. zł łącznego dofinansowania, razem do 100% kosztów ([program](https://wfosigw.katowice.pl/nabory/bezpieczenstwo-dostaw-wody/)) | 5.09.2026 |
| **Poznań** (wielkopolskie) | pożyczka „Ekologiczna Wielkopolska 2026", umorzenia do 40% w wybranych kategoriach (limit 2 mln zł) | „Chroń wodę" — dotacja do 70%, max 300 tys. zł, gminy do 30 tys. mieszkańców, nabór 11.05–10.07.2026, ale zakres to **wody opadowe i roztopowe**, nie wodociągi | 5.09.2026 |
| **Wrocław** (dolnośląskie) | pożyczka do 85% kosztów kwalifikowanych + umorzenia | nie stwierdzono | 5.09.2026 |
| **Warszawa** (mazowieckie) | **(nieustalone)** — serwis `wfosigw.pl` zwracał błąd weryfikacji certyfikatu TLS; wymaga sprawdzenia ręcznego | — | 5.09.2026 |
| pozostałe 10 funduszy | **nie weryfikowano indywidualnie**; ta sama podstawa ustawowa (art. 400a POŚ) i ta sama konstrukcja instrumentów | — | — |

**Co z tego wynika dla skalowania:** materiał przeniesie się na inne województwa **co do mechanizmu**, ale nie co do liczb. Przy kolejnym kliencie trzeba sprawdzić trzy rzeczy w lokalnym funduszu: (1) czy jest program dedykowany bezpieczeństwu dostaw wody, (2) jaki jest procent umorzenia dla zadań z ochrony wód, (3) jaka jest minimalna kwota dofinansowania. Przykład Katowic pokazuje, że **programy typu „bezpieczeństwo dostaw wody" pojawiają się w funduszach wojewódzkich od początku 2026 r.** — to trend, który warto obserwować także w Krakowie i Rzeszowie.

---

## 5. Kwalifikowalność: sprzęt vs. abonament

To jest pytanie, od którego zależy, czy dofinansowanie zmienia nasz model przychodów, czy tylko pokrywa jego jednorazową część.

### 5.1. Sprzęt i wdrożenie — kwalifikują się

W obu badanych ścieżkach katalog kosztów obejmuje dostawę urządzeń i usługi instalacyjne:

- **Fundusze UE (EFRR):** koszty inwestycyjne w infrastrukturę są istotą interwencji; FEM 13.1 dopuszcza „zakup urządzeń" wprost, a wskaźnik produktu PLRO176 zlicza stanowiska pomiarowe.
- **WFOŚiGW Rzeszów:** „roboty budowlane oraz dostawy i usługi", „zakup materiałów i urządzeń", nadzór, rozruch — nasz gateway, czujniki, okablowanie, montaż i uruchomienie mieszczą się w katalogu bez naciągania.
- **WFOŚiGW Katowice:** przedsięwzięcia obejmują infrastrukturę do „poboru, wykorzystania, uzdatniania, magazynowania, dystrybucji i **monitoringu** wody".

**Ryzyko interpretacyjne, które trzeba adresować w opisie:** urządzenie o wartości poniżej progu środka trwałego i o krótkim cyklu życia bywa kwestionowane jako „produkt podlegający szybkiemu zużyciu". Nasz gateway opisujemy jako **element infrastruktury obiektu**, trwale zamontowany w szafie sterowniczej, z określoną żywotnością — nie jako „urządzenie elektroniczne".

### 5.2. Abonament — warunkowo, i tylko w okresie realizacji projektu

**Regulacja jest jednoznaczna i cytujemy ją dosłownie.** „Wytyczne dotyczące kwalifikowalności wydatków na lata 2021–2027" (MFiPR, obowiązujące od **25.03.2025**), podrozdział 2.3 pkt 1 lit. p, w katalogu wydatków **niekwalifikowalnych**:

> p) **koszty operacyjne projektu EFRR/FS/FST**, czyli wydatki ponoszone w fazie eksploatacji inwestycji (m.in. wydatki poniesione na wynagrodzenia pracowników zatrudnionych w eksploatacyjnej fazie inwestycji, wydatki na produkty podlegające szybkiemu zużyciu, wydatki na części zamienne, energię oraz środki chemiczne do wykorzystania podczas fazy eksploatacyjnej inwestycji) **chyba, że zostały zatwierdzone we wniosku o dofinansowanie projektu w związku z przedmiotem i specyfiką projektu oraz poniesione w okresie kwalifikowalności wydatków określonym w umowie o dofinansowanie projektu.**

([PDF Wytycznych](https://www.funduszeunijne.gov.pl/media/148730/Wytyczne_dotyczace_kwalifikowalnosci_wydatkow_na_lata_2021_2027_14_03_2025.pdf), [strona MFiPR](https://www.funduszeunijne.gov.pl/strony/o-funduszach/dokumenty/wytyczne-dotyczace-kwalifikowalnosci-2021-2027/))

Z tego wynikają trzy konkretne rzeczy:

1. **Domyślnie abonament jest niekwalifikowalny.** Nie wolno obiecywać gminie, że „platformę też sfinansuje dotacja".
2. **Wyjątek jest realny, ale ma dwa warunki łącznie:** koszt musi być (a) **zatwierdzony we wniosku** — czyli wpisany do budżetu projektu z uzasadnieniem wynikającym z przedmiotu i specyfiki projektu, oraz (b) **poniesiony w okresie kwalifikowalności** wskazanym w umowie o dofinansowanie. Praktyczna konsekwencja: da się sfinansować abonament **za okres realizacji projektu** (typowo 12–24 miesiące), opłacony z góry i wpisany do wniosku jako koszt niezbędny do uruchomienia i weryfikacji efektu. Nie da się sfinansować abonamentu na 5 lat do przodu.
3. **Po zakończeniu projektu abonament zawsze płaci gmina z budżetu bieżącego.** To trzeba powiedzieć wprost na pierwszym spotkaniu — inaczej w roku 2. pojawi się konflikt oczekiwań, a nas czeka rozmowa o wypowiedzeniu umowy.

W **WFOŚiGW jest gorzej**: katalog kosztów kwalifikowanych jest wprost „o charakterze inwestycyjnym" (Rzeszów) albo obejmuje roboty, urządzenia i dokumentację (Kraków). **Abonament w ścieżce funduszowej nie przejdzie** — to koszt eksploatacyjny.

**Rekomendacja dla oferty:** rozdzielić cennik na trzy pozycje, żeby dały się osobno wpisać do budżetu projektu:

| Pozycja | Kwalifikowalna? | Uwaga do wniosku |
|---|---|---|
| Sprzęt (gateway, czujniki, okablowanie, obudowa) | tak | pozycja inwestycyjna, środek trwały gminy |
| Wdrożenie (inwentaryzacja, montaż, konfiguracja, testy, szkolenie) | tak | usługa towarzysząca dostawie |
| Abonament za platformę i transmisję | warunkowo | tylko za okres realizacji projektu, wpisany do wniosku z uzasadnieniem |

To wymaga korekty sposobu prezentacji cennika z [§4.1](./01_plan_biznesowy.md#41-model-biznesowy--przychody), gdzie abonament jest jedną kwotą „platforma + SIM + serwis". Do wniosku o dofinansowanie trzeba umieć podać **rozbicie abonamentu** i wskazać, która część jest niezbędna w fazie realizacji (uruchomienie, kalibracja, weryfikacja efektu), a która jest kosztem eksploatacji.

### 5.3. VAT

- W projektach o łącznym koszcie **poniżej 5 mln EUR** VAT **może** być kwalifikowalny (podrozdz. 3.5 pkt 1 Wytycznych) — ale **instytucja zarządzająca ma prawo wyłączyć kwalifikowalność VAT** w SZOP, regulaminie naboru lub umowie (pkt 8). Trzeba sprawdzić w regulaminie konkretnego naboru.
- W projektach **od 5 mln EUR** VAT jest kwalifikowalny tylko wtedy, gdy nie ma prawnej możliwości jego odzyskania.
- **W WFOŚiGW w Krakowie zasada jest twardsza:** VAT jest kosztem kwalifikowanym wyłącznie wtedy, gdy beneficjent nie ma prawnej możliwości odliczenia — sama rezygnacja z odliczenia nie wystarczy (§22 Zasad).
- **Praktyczna konsekwencja dla gmin prowadzących sprzedaż wody:** gmina lub spółka komunalna rozliczająca VAT od sprzedaży wody zwykle **odlicza VAT naliczony**, więc VAT od naszej dostawy nie będzie kwalifikowalny. Kalkulację dla gminy zawsze podajemy w **kwotach netto** i osobno zaznaczamy VAT jako pozycję po stronie gminy. **(przypuszczenie co do konkretnej gminy — status VAT zależy od jej organizacji gospodarki wodnej i wymaga potwierdzenia u jej skarbnika.)**

---

## 6. Pułapki — trwałość, własność i ciągłość usługi

### 6.1. Okres trwałości: 5 lat, liczony od płatności końcowej

Podstawa: **art. 65 rozporządzenia (UE) 2021/1060** oraz podrozdział 2.6 Wytycznych kwalifikowalności. Trwałość projektu musi być zachowana przez **5 lat od daty płatności końcowej** na rzecz beneficjenta (3 lata dla MŚP, gdy projekt wiąże się z wymogiem utrzymania inwestycji lub miejsc pracy).

Naruszeniem trwałości jest wystąpienie co najmniej jednej z przesłanek:

1. zaprzestanie lub przeniesienie działalności produkcyjnej poza region NUTS 2;
2. **zmiana własności elementu infrastruktury, która daje przedsiębiorstwu lub podmiotowi publicznemu nienależną korzyść**;
3. **istotna zmiana wpływająca na charakter projektu, jego cele lub warunki realizacji, która mogłaby doprowadzić do naruszenia jego pierwotnych celów**.

Skutek naruszenia: **zwrot dofinansowania proporcjonalnie do okresu, w którym trwałość nie została zachowana**, w trybie art. 207 ustawy o finansach publicznych — czyli z odsetkami jak od zaległości podatkowych.

W ścieżce funduszowej obowiązuje analogiczny rygor: WFOŚiGW w Rzeszowie wymaga „utrzymania [przedsięwzięcia] oraz niepoddawania modyfikacji mogącej wpłynąć negatywnie na efekt ekologiczny w okresie 5 lat od daty zakończenia zadania"; WFOŚiGW w Krakowie może wypowiedzieć pożyczkę w razie zbycia lub wydzierżawienia dofinansowanego majątku w ciągu 5 lat.

### 6.2. Trzy konsekwencje, które dotyczą bezpośrednio naszego modelu

**(a) Model użyczenia sprzętu koliduje z dotacją.** [ADR-0003](./adr/0003-revenue-model-hardware-plus-subscription.md) ustala, że gmina kupuje sprzęt i jest jego właścicielem — i **to jest właściwa decyzja z punktu widzenia dofinansowania**. Beneficjent musi ponieść wydatek i utrzymać składnik majątku przez 5 lat; sprzęt pozostający naszą własnością nie jest wydatkiem gminy i nie może być rozliczony w projekcie. To jest istotne, bo brief B-01 rozważa model użyczenia jako sposób na uproszczenie formalności certyfikacyjnych. **Te dwie ścieżki się wykluczają:** użyczenie upraszcza CE, ale zamyka drogę do dotacji. Decyzja powinna zapaść świadomie i jest materiałem na aktualizację ADR-0003 — nie rozstrzygamy jej w tym dokumencie.

**(b) Nasza ciągłość działania staje się ryzykiem gminy.** Jeśli w okresie trwałości przestaniemy świadczyć usługę platformy, sprzęt gminy staje się bezużyteczny, a projekt przestaje realizować swój cel — czyli spełnia przesłankę „istotnej zmiany wpływającej na cele projektu". Gmina, która to zrozumie, zapyta o zabezpieczenie. **Musimy mieć na to odpowiedź zanim padnie pytanie.** Minimum:

- umowne zobowiązanie do świadczenia usługi przez okres trwałości (5 lat), z karami umownymi;
- procedura wyjścia: eksport pełnych danych historycznych w otwartym formacie, dokumentacja protokołu telemetrycznego i formatu wiadomości ([§3.4 planu](./01_plan_biznesowy.md#34-format-wiadomości-telemetrycznej)), umożliwiająca podpięcie gatewayów do innej platformy;
- rozważyć depozyt (escrow) firmware'u i specyfikacji API u strony trzeciej.

To nie jest wyłącznie temat prawny — to **wymaganie produktowe**: neutralność danych i możliwość migracji muszą być realne, nie deklaratywne.

**(c) Zakaz zmiany dostawcy w okresie trwałości — mit i fakt.** Same przepisy o trwałości **nie zakazują gminie zmiany dostawcy usługi**. Zakazują zaprzestania działalności, zbycia infrastruktury z nienależną korzyścią i istotnej zmiany celów. W praktyce jednak gmina, która przez 5 lat musi utrzymać efekt projektu, **będzie unikać zmiany dostawcy** — bo każda zmiana to ryzyko przerwy w realizacji wskaźnika i pytań od instytucji kontrolującej. To działa na naszą korzyść po podpisaniu umowy i przeciw nam, gdy gmina jest już związana z kimś innym. **Wniosek sprzedażowy:** gmina po świeżo zakończonym projekcie wod-kan (np. KPO B3.1.1 rozliczonym w 2026 r.) to zły prospekt na najbliższe lata — chyba że wchodzimy jako rozszerzenie, które nie narusza pierwotnego zakresu.

### 6.3. Refundacja, nie zaliczka

Dotacje unijne działają w trybie **refundacji poniesionych wydatków**. Gmina najpierw płaci nam, potem odzyskuje 75–85%. Oznacza to, że:

- w budżecie gminy musi być zabezpieczona **pełna kwota**, a nie wkład własny;
- nasz harmonogram płatności powinien być dopasowany do harmonogramu składania wniosków o płatność — inaczej gmina będzie zwlekać z zapłatą do czasu refundacji;
- istnieje instrument, który to rozwiązuje: **pożyczka pomostowa WFOŚiGW** (w Rzeszowie 🟢 nabór 9.02–27.11.2026, przeznaczona na zachowanie płynności finansowej przedsięwzięć współfinansowanych ze środków UE). Warto o niej wiedzieć i wspomnieć — to konkret, który buduje wiarygodność w rozmowie ze skarbnikiem.

### 6.4. Jeden wniosek na gminę

W naborze FEM 13.1 (tryb konkurencyjny) **może zostać złożony nie więcej niż jeden wniosek na obszar danej gminy, niezależnie od podmiotu ubiegającego się o dofinansowanie**. To oznacza, że jeśli gmina lub jej spółka wodociągowa już przygotowuje wniosek na inny zakres, nasza pozycja albo wejdzie do tego wniosku, albo nie wejdzie wcale. **Nie ma drugiej szansy w tym samym naborze** — dlatego moment rozmowy (przed złożeniem, nie po) decyduje o wszystkim.

---

## 7. PZP i zasada konkurencyjności — co to zmienia w ścieżce sprzedaży

### 7.1. Dwa progi, o których trzeba pamiętać

| Reżim | Próg | Co obowiązuje poniżej | Co obowiązuje powyżej |
|---|---|---|---|
| **Prawo zamówień publicznych** (gmina jest zamawiającym publicznym zawsze, niezależnie od dotacji) | **170 000 zł netto** — próg podniesiony ze 130 000 zł **od 1.01.2026** (ustawa z 25.07.2025 o zmianie ustawy — Pzp, podpisana 21.08.2025) | wewnętrzny regulamin zamawiającego | pełna procedura Pzp |
| **Zasada konkurencyjności** (dodatkowo, w projektach z dofinansowaniem UE) | **80 000 zł netto** (Wytyczne kwalifikowalności, sekcja 3.2.1 pkt 1 lit. a) | procedury beneficjenta | upublicznienie zapytania w Bazie Konkurencyjności, **min. 7 dni** na złożenie ofert (dostawy i usługi), obiektywne kryteria oceny |

Źródło progu Pzp: [omówienie zmiany, publ. 2.09.2025](https://sowislo.com.pl/zmiana-progu-stosowania-ustawy-prawo-zamowien-publicznych-z-130-000-zl-netto-na-170-000-zl-netto/). Postępowania wszczęte przed 1.01.2026 prowadzone są według starego progu.

**Gdzie w tych progach leży nasza oferta.** Instalacja u typowej gminy (10 obiektów) to 29–83 tys. zł netto — czyli:

- w projekcie **bez** dofinansowania UE: zwykle poniżej progu Pzp → zamówienie według regulaminu wewnętrznego gminy, prosta ścieżka;
- w projekcie **z** dofinansowaniem UE: przy większych wdrożeniach przekraczamy 80 tys. zł netto → **zasada konkurencyjności**, ogłoszenie w Bazie Konkurencyjności, minimum 7 dni na oferty;
- jeśli nasza pozycja jest częścią większego zamówienia (np. „modernizacja SUW wraz z systemem monitoringu"), liczy się **wartość całego zamówienia**, a nie naszej części — czyli praktycznie zawsze pełne Pzp.

### 7.2. Konsekwencja, której nie da się obejść: nie wolno wskazać nas z nazwy

Art. 99 ust. 4 Pzp zakazuje opisywania przedmiotu zamówienia w sposób mogący utrudniać uczciwą konkurencję, **w szczególności przez wskazanie znaków towarowych, patentów lub pochodzenia**, jeżeli mogłoby to faworyzować lub eliminować wykonawców. Wyjątek z ust. 5 (gdy nie da się opisać przedmiotu wystarczająco precyzyjnie) wymaga dopisania **„lub równoważny"**, a ust. 6 nakazuje **wskazać kryteria oceny równoważności** — przy czym niedopuszczalne jest formułowanie ich tak, by odtwarzały wszystkie cechy konkretnego produktu ([e-komentarz UZP do art. 99](https://ekomentarzpzp.uzp.gov.pl/prawo-zamowien-publicznych/art-99), [interpretacja UZP](https://www.uzp.gov.pl/nowe-pzp/interpretacje/pytania-instytucji-kontrolujacych/art.-99-ust.-4-pzp-stanowi,-ze-przedmiotu-zamowienia-nie-mozna-opisywac-w-sposob,-ktory-moglby-utrudniac-uczciwa-konkurencje,-w-szczegolnosci-przez-wskazanie-znakow-towarowych,-patentow-lub-pochodzenia,-zrodla-lub-szczegolnego-procesu,-ktory-charakte)).

**Co to znaczy w praktyce:**

- Rozmowa przedsprzedażowa z gminą **nie kończy się zamówieniem**, tylko postępowaniem, które musimy wygrać.
- Możemy (i powinniśmy) pomóc gminie zrozumieć, **jakie parametry funkcjonalne** ma sens opisać: częstotliwość próbkowania i transmisji, bufor lokalny przy utracie łączności, otwarty format eksportu danych, brak sterowania procesem, niezależność od jednego producenta czujników, zgodność z wymogami KSC. To są nasze przewagi wyrażone jako **wymagania funkcjonalne**, a nie jako marka.
- Nie możemy pisać OPZ za gminę ani sugerować opisu, który eliminuje konkurencję — poza ryzykiem prawnym dla gminy, w projekcie dotowanym skutkuje to **korektą finansową**, czyli obcięciem dofinansowania po fakcie. To jest ryzyko, które gmina zapamięta jako „przez tego dostawcę straciliśmy pieniądze".

### 7.3. Trzeci reżim: wybór wykonawcy w projekcie WFOŚiGW

W pożyczce z WFOŚiGW w Rzeszowie jednym z elementów oceny merytorycznej są „informacje o terminie i sposobie wyboru Wykonawcy", a do dokumentacji dołącza się **oświadczenie o wyborze wykonawcy**. Nawet poza reżimem unijnym trzeba więc udokumentować, że wybór był konkurencyjny.

---

## 8. NIS2/KSC — nowy motor zakupowy, ale nie źródło pieniędzy na monitoring

**Nowelizacja ustawy o krajowym systemie cyberbezpieczeństwa, wdrażająca dyrektywę NIS2, obowiązuje od 3.04.2026.** Kluczowe terminy dla samorządów ([prawo.pl, 23.04.2026](https://www.prawo.pl/samorzad/nowelizacja-ksc-i-nis-2-wojt-odpowie-finansowo-za-cyberbezpieczenstwo-urzedu,1543342.html)):

| Data | Obowiązek |
|---|---|
| 3.04.2026 | wejście w życie nowelizacji |
| **3.10.2026** | koniec terminu rejestracji podmiotów |
| 3.04.2027 | wdrożenie Systemu Zarządzania Bezpieczeństwem Informacji (SZBI) |
| 3.04.2028 | pierwsze kary pieniężne i audyty podmiotów kluczowych |

Wójt, burmistrz lub prezydent zatwierdza analizę ryzyka i środki bezpieczeństwa, zapewnia środki na wdrożenie SZBI i **odpowiada osobiście, finansowo** — kara może sięgnąć 100% wynagrodzenia. Woda pitna jest sektorem objętym NIS2 (por. [`CONTEXT.md`](./CONTEXT.md), hasło „NIS2"), więc gminny zakład wodociągowy wchodzi w reżim niezależnie od wielkości urzędu — **to ustalenie wymaga potwierdzenia dla konkretnej gminy** na podstawie załączników do ustawy **(przypuszczenie)**.

**Czego to nie zmienia:** żaden z programów cyberbezpieczeństwa nie sfinansuje monitoringu wodociągów. „Cyberbezpieczny Samorząd" (FERC 2.2, granty 200–850 tys. zł) jest ⚪ archiwalny — nabór trwał 19.07–14.12.2023 ([CPPC](https://www.gov.pl/web/cppc/cyberbezpieczny-samorzad)). Trwający 🟢 nabór **FERC.04.01-IP.01-003/26 na Lokalne Centra Cyberbezpieczeństwa** (31.07–30.10.2026, ok. **269,6 mln zł**) finansuje sprzęt i oprogramowanie ochrony sieci, licencje, szkolenia i audyty dla partnerstw JST ([telko.in, 3.08.2026](https://www.telko.in/270-mln-zl-dla-samorzadow-na-tworzenie-lokalnych-centrow-cyberbezpieczenstwa)) — nie infrastrukturę pomiarową.

**Czego to jednak dostarcza:** argumentu zakupowego i wymagań produktowych. Gmina, która musi udokumentować zarządzanie ryzykiem i zgłaszanie incydentów w systemie wodociągowym, potrzebuje **dowodów** — logów, rejestru zdarzeń, wykrywalności anomalii. Nasz system jest read-only, szyfruje transmisję i prowadzi audyt zdarzeń (por. [`05_audit_module.md`](../technical/backend/05_audit_module.md)), co daje konkretny wkład w SZBI. To argument „dlaczego teraz", a nie „skąd pieniądze".

---

## 9. Materiał operacyjny — jak o tym rozmawiać z gminą

> **Jedna strona do wydruku przed spotkaniem. Stan na 5.09.2026 — sprawdź datę, zanim użyjesz.**

### Zdanie otwierające

„Sam monitoring rzadko jest osobnym projektem dotacyjnym — jest za mały. Ale jeśli planujecie jakąkolwiek inwestycję wodociągową, monitoring wchodzi do tego samego wniosku i podnosi jego ocenę, bo programy z 2026 roku premiują właśnie bezpieczeństwo dostaw i ograniczanie strat wody."

### Które pytanie zadać jako pierwsze

**„Czy macie zaplanowaną albo złożoną inwestycję wodociągową na najbliższe dwa lata — i z czego chcecie ją sfinansować?"**

Odpowiedź od razu klasyfikuje rozmówcę:

| Odpowiedź gminy | Ścieżka | Co powiedzieć |
|---|---|---|
| „Tak, planujemy, jeszcze nie składaliśmy wniosku" — **Małopolska** | **FEM 13.1**, nabór 14.10–4.12.2026 | To jest okno, które zamyka się w grudniu. Dotacja do 75%, jeden wniosek na gminę, obligatoryjny element „ciągłość działania systemów wod-kan" — monitoring wpisuje się tam wprost. |
| „Tak, planujemy" — **Podkarpacie** | **FEP 12.1**, nabór zapowiedziany na I kw. 2027 | Jest pół roku na przygotowanie. Opis typu projektu wprost wymienia „rozwiązania zwiększające bezpieczeństwo, monitoring i niezawodność" oraz „inwestycje w ograniczenie strat wody". |
| „Tak, ale to poza terminami naborów" | **WFOŚiGW** (Kraków / Rzeszów) — nabór ciągły | Pożyczka preferencyjna, w Krakowie z umorzeniem do 30% dla zadań z ochrony wód, w Rzeszowie do 100% kosztów kwalifikowanych. Wolniej, ale bez czekania na konkurs. |
| „Nie, nic nie planujemy" | żadna | Uczciwie: dziś nie ma programu, który sfinansuje sam monitoring w skali kilkudziesięciu tysięcy złotych. Rozmawiamy o wdrożeniu z budżetu bieżącego albo wracamy, gdy pojawi się inwestycja. |
| „Właśnie skończyliśmy projekt (KPO / FEnIKS / FEP 2.6)" | **uwaga: okres trwałości** | Przez 5 lat od płatności końcowej gmina nie może istotnie zmienić charakteru projektu. Sprawdzić, czy nasze wdrożenie da się potraktować jako rozszerzenie, a nie zmianę zakresu. |
| „Mamy problem z KSC/NIS2" | argument, nie finansowanie | Rejestracja do 3.10.2026, SZBI do 3.04.2027, odpowiedzialność osobista wójta. Nasz system dostarcza logów i rejestru zdarzeń do SZBI, ale programy cyber (FERC) nie sfinansują monitoringu wodociągów. |

### Co gmina musi zrobić sama

1. **Zdecydować i zgłosić zakres** — nasza pozycja musi trafić do wniosku (a w WFOŚiGW w Krakowie: już do zgłoszenia na listę przedsięwzięć priorytetowych na dany rok).
2. **Zabezpieczyć pełną kwotę w budżecie** — dotacja to refundacja, nie zaliczka. Wkład własny to minimum 25% (FEM 13.1), ale przejściowo gmina finansuje 100%.
3. **Przeprowadzić postępowanie o udzielenie zamówienia** — bez wskazania marki (art. 99 ust. 4–6 Pzp), z zachowaniem zasady konkurencyjności powyżej 80 tys. zł netto w projektach unijnych.
4. **Utrzymać projekt przez 5 lat** i sprawozdawać wskaźniki.
5. **Rozliczyć abonament po zakończeniu projektu z budżetu bieżącego.**

### W czym pomagamy

- **Opis techniczny i parametry funkcjonalne** do części opisowej wniosku i do OPZ — sformułowane jako wymagania, nie jako marka.
- **Kosztorys w rozbiciu na pozycje kwalifikowalne** (sprzęt / wdrożenie / abonament w okresie realizacji) — gotowy do wklejenia w budżet projektu.
- **Wyliczenie efektu ekologicznego i wskaźników** — przede wszystkim ograniczenie strat wody (m³/rok) wynikające ze skrócenia czasu wykrycia awarii, oraz liczba stanowisk pomiarowych (wskaźnik WLWK-PLRO176 w FEM 13.1).
- **Uzasadnienie zgodności** z „Programem inwestycyjnym w zakresie poprawy jakości i ograniczenia strat wody" Ministerstwa Infrastruktury — obszar 5 „Sieć dystrybucji" (monitoring hydrauliczny i jakościowy) ma w tym programie status **priorytetowego**; to wymóg formalny w FEM 13.1.
- **Zobowiązanie do ciągłości usługi** na okres trwałości i procedura wyjścia z danymi — odpowiedź na pytanie „a co, jeśli was zabraknie".

### W czym nie pomagamy — i mówimy to wprost

- **Nie jesteśmy doradcą dotacyjnym.** Nie piszemy wniosku, nie prowadzimy rozliczenia, nie bierzemy odpowiedzialności za wynik oceny.
- **Nie gwarantujemy kwalifikowalności** żadnego kosztu — decyduje instytucja i regulamin konkretnego naboru.
- **Nie piszemy OPZ za gminę** i nie sugerujemy opisu eliminującego konkurencję — dla gminy to ryzyko korekty finansowej.
- **Nie obiecujemy dofinansowania abonamentu** poza okresem realizacji projektu.

### Czego nie mówić

- „Dotacja pokryje wszystko" — nie pokryje abonamentu po zakończeniu projektu ani (zwykle) VAT-u u gminy odliczającej podatek.
- „Załatwimy dofinansowanie" — nie załatwiamy; gmina jest wnioskodawcą i beneficjentem.
- „Jest program FEnIKS dla małych gmin" — nie ma; próg 15 tys. mieszkańców wyklucza nasz segment.

---

## 10. Kalendarz monitorowania i pytania do operatorów programów

### 10.1. Co i kiedy sprawdzić

| Termin | Co zweryfikować | Gdzie |
|---|---|---|
| **przed 14.10.2026** | ogłoszenie i regulamin naboru FEM 13.1 — zwłaszcza zapowiedziane zmiany SzOP; katalog kosztów kwalifikowalnych, kwalifikowalność VAT | [fundusze.malopolska.pl](https://fundusze.malopolska.pl/) |
| **do 30.10.2026** | FERC 4.1 Lokalne Centra Cyberbezpieczeństwa — czy w partnerstwie gminy jest miejsce na komponent monitoringu infrastruktury krytycznej | [CPPC](https://www.gov.pl/web/cppc/cyberbezpieczny-samorzad) |
| **IV kw. 2026** | kryteria wyboru projektów dla priorytetu 12 FEP i termin ogłoszenia naboru | [funduszeue.podkarpackie.pl](https://funduszeue.podkarpackie.pl/harmonogram) |
| **IV kw. 2026** | lista przedsięwzięć priorytetowych WFOŚiGW w Krakowie na 2027 — moment na zgłoszenie zadania gminy | [wfos.krakow.pl](https://www.wfos.krakow.pl/oferta/warunki-wsparcia-finansowego/lista-przedsiewziec%E2%80%8B-%E2%80%8Bpriorytetowych/) |
| **kwartalnie** | aktualizacje harmonogramów FEM, FEP i FEnIKS (aktualizowane raz na kwartał) | portale programów |
| **kwartalnie** | czy WFOŚiGW w Krakowie lub Rzeszowie uruchomił program typu „bezpieczeństwo dostaw wody" (wzorem Katowic) | BIP funduszy |
| **na bieżąco** | czy wraca Rządowy Fundusz Polski Ład: PIS | [bgk.pl/polski-lad](https://www.bgk.pl/polski-lad/) |

### 10.2. Pytania do zadania operatorom programów

Zadać **przed** pierwszą poważną rozmową z gminą — odpowiedzi zmieniają treść oferty:

**Do IZ FEM (UMWM, Departament Funduszy Europejskich) — działanie 13.1:**
1. Czy system monitoringu parametrów sieci (ciśnienie, temperatura, przepływ) bez funkcji sterowania kwalifikuje się jako działanie z obszaru I pkt 6 „zapewnienie ciągłości działania systemów wodno-kanalizacyjnych"?
2. Czy opłata abonamentowa za platformę SaaS, poniesiona w okresie realizacji projektu i wskazana w budżecie wniosku, będzie uznana za kwalifikowalną w rozumieniu podrozdz. 2.3 pkt 1 lit. p Wytycznych?
3. Czy regulamin naboru wyłącza kwalifikowalność VAT?
4. Czy projekt złożony wyłącznie z działań obszaru I (bez robót sieciowych) jest dopuszczalny, i jaka jest wtedy minimalna wartość projektu?
5. Jak dokumentuje się wskaźnik WLWK-PLRO176 dla stanowisk pomiarowych na sieci wodociągowej?

**Do IZ FEP (UMWP, Departament Wdrażania Projektów Infrastrukturalnych RPO) — działanie 12.1:**
6. Jaki będzie maksymalny poziom dofinansowania i czy przewidziano limit kwotowy na projekt?
7. Czy „doposażanie w rozwiązania zwiększające monitoring" obejmuje zakup gatewayów i czujników montowanych na istniejącej infrastrukturze, bez robót budowlanych?

**Do WFOŚiGW w Krakowie i w Rzeszowie:**
8. Czy zadanie polegające wyłącznie na montażu systemu monitoringu sieci mieści się w dziedzinie „ochrona wód" (Kraków — istotne dla umorzenia do 30%)?
9. Jaka jest minimalna kwota pożyczki i czy fundusz akceptuje efekt ekologiczny wyrażony jako ograniczenie strat wody wyliczone metodą bilansową?
10. Czy abonament za pierwsze 12 miesięcy, ujęty w harmonogramie rzeczowo-finansowym jako element rozruchu, może być kosztem kwalifikowanym?

---

## 11. Źródła

Wszystkie linki sprawdzone **5 września 2026 r.** Data przy pozycji oznacza datę publikacji lub obowiązywania dokumentu.

**Akty prawne i dokumenty horyzontalne**
- Rozporządzenie (UE) 2021/1060, art. 65 — trwałość operacji.
- [Wytyczne dotyczące kwalifikowalności wydatków na lata 2021–2027](https://www.funduszeunijne.gov.pl/strony/o-funduszach/dokumenty/wytyczne-dotyczace-kwalifikowalnosci-2021-2027/), obowiązujące od 25.03.2025 ([PDF](https://www.funduszeunijne.gov.pl/media/148730/Wytyczne_dotyczace_kwalifikowalnosci_wydatkow_na_lata_2021_2027_14_03_2025.pdf)) — podrozdz. 2.3 (wydatki niekwalifikowalne), 2.6 (trwałość), 3.2.1 (zasada konkurencyjności), 3.5 (VAT).
- Ustawa z 11.09.2019 — Prawo zamówień publicznych, art. 99 ust. 4–6 ([e-komentarz UZP](https://ekomentarzpzp.uzp.gov.pl/prawo-zamowien-publicznych/art-99)); zmiana progu na 170 000 zł netto od 1.01.2026 ([omówienie, 2.09.2025](https://sowislo.com.pl/zmiana-progu-stosowania-ustawy-prawo-zamowien-publicznych-z-130-000-zl-netto-na-170-000-zl-netto/)).
- Ustawa — Prawo ochrony środowiska, art. 400a ust. 1 (katalog zadań finansowanych przez fundusze ochrony środowiska).
- Nowelizacja ustawy o KSC (wdrożenie NIS2), obowiązuje od 3.04.2026 ([prawo.pl, 23.04.2026](https://www.prawo.pl/samorzad/nowelizacja-ksc-i-nis-2-wojt-odpowie-finansowo-za-cyberbezpieczenstwo-urzedu,1543342.html)).
- [Program inwestycyjny w zakresie poprawy jakości i ograniczenia strat wody przeznaczonej do spożycia przez ludzi](https://www.gov.pl/attachment/edd4fc6f-0e68-4fc4-b60f-3eb5b1e016fb), Ministerstwo Infrastruktury, czerwiec 2021 — 14 obszarów działań, podrozdz. 4.1.1 i tabela 10.

**Małopolska**
- [SZOP FEM 2021–2027, wersja 030, obowiązuje od 18.08.2026](https://fundusze.malopolska.pl/sites/default/files/2026/08/3342/1_zalacznik%20nr%201%20do%20uchwaly_SZOP.FEMP_.030.pdf) — działanie FEMP.13.01, str. 726–731.
- [Harmonogram naborów FEM, wersja z 2.09.2026](https://fundusze.malopolska.pl/harmonogram) ([PDF](https://www.fundusze.malopolska.pl/sites/default/files/2026/09/1862/zal.%20do%20uchwaly%20%20nr%201975_26%20z%20dnia%202%20wrzesnia%202026.pdf)).
- [Planowane zmiany SzOP w zakresie działania 13.1, 29.05.2026](https://fundusze.malopolska.pl/aktualnosc/14117-planowane-zmiany-szop-w-zakresie-dzialania-131-wzmacnianie-bezpieczenstwa-wodnego).
- [Zasady finansowania zadań ze środków WFOŚiGW w Krakowie](https://www.wfos.krakow.pl/oferta/warunki-wsparcia-finansowego/zasady_finansowania_zadan_wfosigw_w_krakowie/), uchwała RN nr 128/2025 z 19.12.2025, obowiązują od 1.01.2026 ([PDF](https://www.wfos.krakow.pl/wp-content/uploads/2026/01/Zasady-finansowania-zadan-ze-srodkow-WFOSIGW-w-Krakowie-na-rok-2026.pdf)).
- [Lista przedsięwzięć priorytetowych WFOŚiGW w Krakowie na 2026 r.](https://www.wfos.krakow.pl/wp-content/uploads/2025/06/Zalacznik-do-Uchwaly-nr-58-2025-.pdf), uchwała nr 58/2025.

**Podkarpacie**
- [Harmonogram naborów FEP 2021–2027, wersja z 30.06.2026](https://funduszeue.podkarpackie.pl/harmonogram) ([XLSM](https://funduszeue.podkarpackie.pl/images/Dokumenty_2026/Pliki/Harmonogram%20naborow%20wnioskow%20o%20dofinansowanie%20dla%20programu%20regionalnego%20Fundusze%20Europejskie%20dla%20Podkarpacia%202021-2027%20z%2030.06.2.xlsm)) — działanie FEPK.12.01.
- [Nowe priorytety FEP zatwierdzone decyzją KE z 22.04.2026](https://podkarpackie.pl/index.php/fundusze-eu/aktualnosci/od-strategicznego-bezpieczenstwa-po-lokalne-potrzeby-program-fep-w-dzialaniu) (komunikat UMWP z 24.04.2026).
- [Nabór FEPK.02.06-IZ.00-003/23 „Zrównoważona gospodarka wodno-ściekowa" — zaopatrzenie w wodę](https://funduszeue.podkarpackie.pl/nabory-wnioskow/2-6-zrownowazona-gospodarka-wodno-sciekowa-nr-naboru-fepk-02-06-iz-00-003-23), ogłoszenie z 10.05.2023.
- [Nabór pożyczek WFOŚiGW w Rzeszowie na 2026 r.](https://bip.wfosigw.rzeszow.pl/nabory-wnioskow/pozyczki/254-nabor-pozyczek-2026/1561-pozyczka-na-realizacje-zadan-z-dziedziny-ochrony-srodowiska-i-gospodarki-wodnej), ogłoszenie z 9.02.2026 ([regulamin naboru, PDF](https://bip.wfosigw.rzeszow.pl/images/pozyczka_dlugoterm_2026/regulamin_naboru_wnioskow_pozyczki.pdf)).
- [Pożyczka pomostowa WFOŚiGW w Rzeszowie, nabór 2026](https://bip.wfosigw.rzeszow.pl/nabory-wnioskow/pozyczki/254-nabor-pozyczek-2026/1559-pozyczka-pomostowa-na-realizacje-zadan-z-dziedziny-ochrony-srodowiska-i-gospodarki-wodnej).
- [Nabór I.10.10 obszar A, woj. podkarpackie](https://prow.podkarpackie.pl/index.php/test-1/430-nabor-wnioskow-o-przyznanie-pomocy-dla-interwencji-i-10-10-infrastruktura-na-obszarach-wiejskich-oraz-wdrozenie-koncepcji-inteligentnych-wsi-obszar-a-inwestycje-w-zakresie-systemow-indywidualnego-oczyszczania-sciekow), ogłoszenie z 5.11.2025.

**Programy krajowe**
- [Harmonogram naborów FEnIKS](https://feniks.gov.pl/harmonogram-naborow-feniks/), wersja obowiązująca od 19.12.2025 ([XLSX](https://feniks.gov.pl/wp-content/uploads/2026/01/Harmonogram_naborow_FEnIKS_19_12_2025.xlsx)).
- [FEnIKS 2.5 „Woda do spożycia" — karta naboru zakończonego 3.06.2024](https://funduszeunijne.gov.pl/nabory/25-woda-do-spozycia-niekonkurencyjny/) oraz [naboru zakończonego 31.01.2024](https://www.funduszeunijne.gov.pl/nabory/25-woda-do-spozycia/).
- [NFOŚiGW — Gospodarka wodno-ściekowa poza granicami aglomeracji](https://www.gov.pl/web/nfosigw/gospodarka-wodno-sciekowa-poza-granicami-aglomeracji).
- [NFOŚiGW — harmonogram naborów](https://www.gov.pl/web/nfosigw/harmonogram-naborow), aktualizacja 3.09.2026.
- [KPO — wydłużenie terminów realizacji inwestycji, 16.06.2026](https://www.kpo.gov.pl/strony/aktualnosci/wiecej-czasu-na-inwestycje-z-kpo-rolnicy-przedsiebiorcy-i-samorzady-zyskaja-dodatkowe-miesiace/).
- [KPO B3.1.1 — nabór woj. małopolskie, publ. 23.12.2024](https://www.funduszeunijne.gov.pl/nabory/woj-malopolskie-nabor-wnioskow-w-inwestycji-b311-inwestycje-w-zrownowazona-gospodarke-wodno-sciekowa-na-terenach-wiejskich/); [ogłoszenie woj. śląskie, publ. 20.11.2024](https://prow.slaskie.pl/pl/aktualnosci/ogloszenie-o-naborze-wnioskow-w-ramach-inwestycji-b311-inwestycje-w-zrownowazona-gospodarke-wodno-sciekowa-na-terenach-wiejskich-kpo.html); [zwiększenie środków, MRiRW, 24.06.2025](https://www.gov.pl/web/rolnictwo/wiecej-srodkow-z-kpo-na-inwestycje-wodno-kanalizacyjne-na-obszarach-wiejskich).
- [PS WPR — interwencja I.10.10 (MRiRW)](https://www.gov.pl/web/rolnictwo/i1010-infrastruktura-na-obszarach-wiejskich-oraz-wdrozenie-koncepcji-inteligentnych-wsi); [karta I.10.10.B, DPROW UMWW](https://dprow.umww.pl/interwencje/i-10-10-b-wdrozenie-koncepcji-inteligentnych-wsi/).
- [Cyberbezpieczny Samorząd (FERC 2.2), CPPC](https://www.gov.pl/web/cppc/cyberbezpieczny-samorzad); [nabór na Lokalne Centra Cyberbezpieczeństwa, 3.08.2026](https://www.telko.in/270-mln-zl-dla-samorzadow-na-tworzenie-lokalnych-centrow-cyberbezpieczenstwa).
- [Rządowy Fundusz Polski Ład: Program Inwestycji Strategicznych](https://www.bgk.pl/polski-lad/) — status naboru **nieustalony** (serwis blokuje dostęp automatyczny).
- [Program Ochrony Ludności i Obrony Cywilnej 2025–2026 — zadania wodne, 19.03.2026](https://euroclean.pl/artykuly-o-wodzie/zachowanie-ciaglosci-dostaw-wody-w-ramach-programu-ochrony-ludnosci-i-obrony-cywilnej-na-lata-2025-2026/).

**Pozostałe WFOŚiGW (przegląd skrótowy)**
- [WFOŚiGW w Katowicach — „Bezpieczeństwo dostaw wody pitnej na obszarze województwa śląskiego"](https://wfosigw.katowice.pl/nabory/bezpieczenstwo-dostaw-wody/), nabór 6.02.2026–29.10.2027.
- [WFOŚiGW w Poznaniu — „Ekologiczna Wielkopolska 2026"](https://www.wfosgw.poznan.pl/programy/ekologiczna-wielkopolska-2026-nabor-wnioskow-pozyczkowych-na-przedsiewziecia-z-zakresu-ochrony-srodowiska-i-gospodarki-wodnej/).
- [WFOŚiGW we Wrocławiu — ochrona wód](https://wfosigw.wroclaw.pl/zloz-wniosek/ow-ochrona-wod/w_69,informacje).

---

**Ostrzeżenie końcowe.** Ten dokument opisuje stan na 5.09.2026 i będzie się dezaktualizował szybciej niż reszta dokumentacji projektu. Nabór FEM 13.1 zamyka się 4.12.2026, a zapowiedziane zmiany SzOP mogą zmienić jego parametry jeszcze przed startem. **Przed każdą rozmową z gminą sprawdź co najmniej: aktualny regulamin naboru, aktualną wersję SZOP i harmonogram naborów.** Powoływanie się na nieaktualne warunki jest gorsze niż niepowoływanie się na żadne.
