# B-03 — instrukcja dla kolejnego agenta: uzupełnienie tego, czego nie dało się zrobić

> **Do kogo:** agent (albo człowiek) pracujący w środowisku **z normalnym dostępem do sieci** i z przeglądarką.
> **Po czym:** [`01_analiza_ux_konkurencji.md`](01_analiza_ux_konkurencji.md) — analiza jest kompletna poza tym, co niżej. **Przeczytaj ją najpierw w całości**, a szczególnie §0.1 (ograniczenia), §2.0 (macierz porównawcza) i §3 (katalog wzorców) — numery `W-xx` używane w tym dokumencie pochodzą stamtąd.
> **Gałąź:** kontynuuj na `claude/analiza-ux-ui-konkurencji-vharpb` albo odgałęź od niej. Nie merguj do `main` bez zgody.

## Dlaczego to zadanie w ogóle istnieje

Sesja, w której powstała analiza, miała politykę egress dopuszczającą wyłącznie hosty GitHuba. Potwierdzone odmowy bramy (`403` na `CONNECT`) dla `grafana.com`, `kallipr.com`, `zabbix.com`, `en.wikipedia.org`, `developer.mozilla.org`. Wyszukiwarka działała i zwracała streszczenia, ale **żadnej strony nie dało się otworzyć** — ani przez pobranie treści, ani przeglądarką, bo obie idą przez ten sam proxy.

Skutek: wszystkie ustalenia o konkurencji opisują **to, co producent deklaruje w dokumentacji**, a nie to, co widać na ekranie. Twoim zadaniem jest zamienić deklaracje na obserwacje — i przy okazji sprawdzić, czy któraś z nich się nie rozsypie w zderzeniu z rzeczywistym interfejsem.

**Zanim zaczniesz — sprawdź, czy masz dostęp.** Jeśli poniższe zwróci `403` albo `000`, jesteś w tym samym środowisku co ja i tego zadania nie da się wykonać; zgłoś to zamiast obchodzić proxy:

```bash
for h in grafana.com thingsboard.io zabbix.com kallipr.com; do
  echo "$h -> $(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 https://$h/ 2>/dev/null || echo BLOCKED)"
done
```

---

## Zadanie 1 — biblioteka zrzutów ekranu (główne, blokujące „definicję ukończenia” briefu)

Brief B-03 wymaga „orientacyjnie 30–60 zrzutów łącznie” w `docs/analysis/assets/`, jako **zasób do przeglądania, nie tylko materiał dowodowy**.

**Co jest przygotowane:** [`assets/README.md`](assets/README.md) zawiera listę **48 konkretnych ujęć** — numer, nazwa pliku, adres, co ma być na ekranie, typ źródła (`[dok]`/`[mkt]`/`[std]`/`[art]`) i wzorzec `W-xx`, którego dotyczy. [`assets/capture_screenshots.mjs`](assets/capture_screenshots.mjs) zbiera je automatycznie.

**Kroki:**

```bash
cd docs/analysis/assets
npm install playwright sharp
npx playwright install chromium
node capture_screenshots.mjs
```

Skrypt jest wznawialny (pomija istniejące pliki), kompresuje do WebP 1600 px / jakość 82, ostrzega o plikach powyżej 300 KB i zapisuje `capture_log.json` z datami pobrania. Nieudane pozycje wypisuje na końcu — te zrób ręcznie wg instrukcji w README.

**Po zebraniu:**

1. Wpisz daty pobrania do kolumny „pobrano” w [`assets/README.md`](assets/README.md) (masz je w `capture_log.json`). Brief wymaga daty przy każdym zrzucie — interfejsy zmieniają się między wersjami i analiza bez daty starzeje się niezauważalnie.
2. Sprawdź rozmiar: `du -sh .` — przy 48 plikach powinno wyjść poniżej ~12 MB.
3. **Obejrzyj to, co zebrałeś.** To jest właściwa część zadania, nie pobieranie. Przy każdym ujęciu oznaczonym **★** sprawdź, czy zrzut faktycznie pokazuje wzorzec opisany w analizie. Jeśli nie pokazuje — dopisz to. Rozbieżność między dokumentacją a ekranem jest cenniejszym ustaleniem niż potwierdzenie.
4. Osadź zrzuty w [`01_analiza_ux_konkurencji.md`](01_analiza_ux_konkurencji.md) tam, gdzie **dokładają coś do tekstu** — nie wszystkie 48. Reszta zostaje w katalogu jako zasób do przeglądania, zgodnie z intencją briefu.

**Czego nie robić:** nie rejestruj się na wersje próbne i nie sięgaj po płatne raporty — brief tego zabrania, a lista 48 adresów prowadzi wyłącznie do materiałów publicznych.

---

## Zadanie 2 — uzupełnić macierz porównawczą (§2.0 analizy)

Macierz produkt × wymiar w [§2.0](01_analiza_ux_konkurencji.md#20-macierz-porównawcza--produkt--wymiar) ma **dużo komórek `○` — „brak informacji publicznej”**. To nie znaczy, że produkt czegoś nie ma; znaczy, że nie dało się tego ustalić bez otwarcia ekranu.

**Priorytet — te komórki zmieniają wnioski, jeśli okażą się inne:**

| Produkt | Wymiar do ustalenia | Gdzie szukać | Dlaczego to ważne |
|---|---|---|---|
| Wszystkie sześć wod-kan | **3 — pomiar razem z czasem i jakością** | ekrany podglądu wartości bieżących | Cała kolumna jest pusta. Analiza twierdzi na tej podstawie, że nasz niezmiennik z §2.4.3 jest **ponad** poziomem rynku wod-kan. Jeśli którykolwiek z nich to jednak pokazuje, teza wymaga korekty |
| Inventia, AquaRD | 5 — alarmy i triage | folder produktowy, materiały z targów, webinary | Konkurenci bezpośredni; nasz projekt widoku alarmów powstał bez ich udziału |
| HWM DataGate | 1, 2, 5 | [instrukcja użytkownika DataGate2 (PDF)](https://www.hwmglobal.com/uploads/manuals/DataGate2/MAN-130-0015-A%20DataGate2%20Introduction%20for%20Users%20and%20Administrators.pdf) — **jedyny publiczny pełny manual w kategorii wod-kan** | Najbliższy funkcjonalnie temu, co budujemy, a jego manuala nie dało się otworzyć. Zacznij od tego pliku |
| Zabbix | 1 — ekran po zalogowaniu | instancja demo albo instalacja lokalna | Analiza świadomie **nie** twierdzi, że Zabbix startuje na `Problems`, bo nie dało się tego potwierdzić. Rozstrzygnij i popraw §2.1 |
| Ayyeka | 3, 5 | [baza wiedzy Ayyeki](https://www.ayyeka.com/en/knowledge/dashboard-widgets) | Jedyny w kategorii z publiczną bazą wiedzy — prawdopodobnie da się uzupełnić kilka komórek naraz |

Aktualizując macierz, **zmień też legendę stanu**: komórka podniesiona z `○` na `●` na podstawie obejrzanego ekranu zasługuje na przypis mówiący, że pochodzi z obserwacji, a nie z dokumentacji.

---

## Zadanie 3 — zweryfikować dwie tezy, które opierają się na braku danych

Obie są w analizie postawione wprost i obie są **falsyfikowalne**. Jeśli któraś padnie, trzeba poprawić dokument, a nie ukryć wynik.

1. **„Polscy konkurenci nie publikują dokumentacji interfejsu”** ([§1.1](01_analiza_ux_konkurencji.md#11-kategoria-a--wod-kan-i-smart-water)). Analiza wyciąga z tego wniosek biznesowy: czytelna dokumentacja użytkownika jest w polskim wod-kanie tanią różnicą konkurencyjną. Sprawdź strony Inventii, AquaRD i Hawle pod kątem instrukcji, bazy wiedzy albo publicznego dema. Jeśli takie materiały istnieją, wniosek trzeba złagodzić.
2. **„Wymiar 5 to jedyny, w którym mam materiał od czterech niezależnych produktów”** ([§2.0](01_analiza_ux_konkurencji.md#20-macierz-porównawcza--produkt--wymiar)). To uzasadnia, dlaczego projekt widoku alarmów jest najbardziej szczegółową częścią dokumentu. Po uzupełnieniu macierzy sprawdź, czy nadal jest prawdziwe.

---

## Zadanie 4 — podmienić schematy w Artifaccie na rzeczywiste zrzuty

**Artifact:** https://claude.ai/code/artifact/666711ee-d6ae-4ca1-89db-8d9d0e4149c3
**Plik źródłowy:** nie jest w repozytorium (powstał w katalogu roboczym sesji). Żeby go zaktualizować, odczytaj opublikowaną wersję narzędziem Artifact z tym adresem jako `url`, zapisz do pliku, edytuj i opublikuj **z tym samym `url`** — inaczej powstanie osobny Artifact zamiast aktualizacji tego.

Dziś przy każdej z dziesięciu rekomendacji stoi para paneli „dziś / propozycja” rysowana w SVG. Panele „dziś” są oparte na naszym kodzie i **zostają** — są prawdziwe i nic ich nie zastąpi. Do podmiany kwalifikują się miejsca, gdzie zrzut konkurenta pokazałby wzorzec lepiej niż schemat:

| Rekomendacja w Artifaccie | Zrzut do wstawienia |
|---|---|
| 02 — ekran startowy pokazuje wyjątki | `32_zabbix_problems_list.webp` |
| 03 — jakość wraca na wartość | `13_ignition_quality_overlays.webp` |
| 04 — „brak komunikacji” przestaje być szary | `44_isa101_going_gray.webp` |
| 06 — przerwa w łączności na wykresie | `26_grafana_nodata_error_states.webp` |
| 07 — awaria obiektu ≠ awaria telemetrii | `12_ayyeka_dashboard_widgets.webp` |
| 08 — tabela zamienia się w karty | `41_pagerduty_mobile_incident.webp` |
| 09 — wiersz alarmu z akcjami | `21_thingsboard_alarms_table.webp` |
| 10 — potwierdzenie z komentarzem | `33_zabbix_update_problem.webp` |

**Ograniczenia techniczne Artifactów, o które trzeba zadbać:**

- obrazy **muszą** być osadzone jako `data:` URI — odwołania do zewnętrznych hostów są blokowane przez CSP i znikają bez komunikatu o błędzie;
- limit całej strony to 16 MB, więc do osadzenia przygotuj **osobne, mniejsze warianty** (szerokość ok. 900 px, jakość ~75), a nie pliki 1600 px z katalogu `assets/`;
- zrzut podpisz jako zrzut, z nazwą produktu i datą pobrania — dziś panele są jawnie oznaczone jako schematy i ta uczciwość ma zostać po podmianie;
- nie zmieniaj `favicon` ani `<title>` przy ponownej publikacji — Artifact zachowuje tożsamość.

---

## Zadanie 5 — czego **nie** trzeba robić

Żeby nie marnować czasu na rzeczy już zamknięte:

- **Nie przeprowadzaj analizy kodu od nowa.** [§4](01_analiza_ux_konkurencji.md#4-konfrontacja-z-naszym-interfejsem) powstała z bezpośredniej lektury plików, wszystkie odwołania (plik + zakres linii) zostały zweryfikowane wobec stanu gałęzi z 2026-09-02. Jeśli kod się w międzyczasie zmienił — sprawdź, ale nie zaczynaj od zera.
- **Nie przeprojektowuj widoku alarmów.** [§6](01_analiza_ux_konkurencji.md#6-projekt-widoku-alarmów) jest kompletna: model danych, układ ekranu, przepływy akcji, uprawnienia, stany brzegowe, wariant mobilny, punkty styku. Zrzuty z zadania 1 mogą ją uszczegółowić, ale nie podważą.
- **Nie zaczynaj od implementacji.** To zlecenie jest analityczne; backlog w [§7](01_analiza_ux_konkurencji.md#7-backlog-zmian-we-froncie) jest wejściem do osobnej pracy, a widok alarmów dodatkowo czeka na moduł backendu i na cztery kody uprawnień z [§6.7](01_analiza_ux_konkurencji.md#67-uprawnienia--brakujące-kody-bez-których-ekranu-nie-da-się-zbudować).
- **Nie usuwaj sekcji o ograniczeniach z §0.1** po uzupełnieniu zrzutów — przepisz ją tak, żeby mówiła, co i kiedy zostało uzupełnione. Historia tego, na jakim materiale powstały wnioski, jest częścią ich wiarygodności.

## Definicja ukończenia tego zadania

1. `docs/analysis/assets/` zawiera kilkadziesiąt zrzutów z datami pobrania wpisanymi do README.
2. Macierz w §2.0 ma uzupełnione komórki priorytetowe z zadania 2, z rozróżnieniem „z dokumentacji” / „z obserwacji”.
3. Obie tezy z zadania 3 są potwierdzone albo skorygowane w tekście.
4. Artifact pod tym samym adresem pokazuje rzeczywiste zrzuty przy rekomendacjach z tabeli w zadaniu 4.
5. §0.1 opisuje stan faktyczny po uzupełnieniu, a nie stan z 2026-09-02.
