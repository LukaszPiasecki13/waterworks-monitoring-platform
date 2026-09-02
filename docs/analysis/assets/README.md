# Biblioteka zrzutów ekranu — plan wykonania

> **Status: do wykonania.** Katalog jest celowo pusty poza tym plikiem i skryptem zbierającym.

## Dlaczego katalog jest pusty

Analiza [`../01_analiza_ux_konkurencji.md`](../01_analiza_ux_konkurencji.md) powstała w sesji, której polityka egress dopuszcza wyłącznie hosty GitHuba. Każda próba połączenia z domeną konkurenta kończy się odmową bramy (`403` na `CONNECT`) — zweryfikowane na `grafana.com`, `kallipr.com`, `zabbix.com`, `en.wikipedia.org`, `developer.mozilla.org`. Dotyczy to zarówno pobierania stron, jak i przeglądarki sterowanej Playwrightem, bo obie chodzą przez ten sam proxy.

Nie dało się więc otworzyć ani jednego ekranu konkurencji. Zamiast wstawiać zrzuty z innego źródła albo udawać, że deliverable powstał, zostawiam **wykonawczy plan uzupełnienia**: listę konkretnych ujęć poniżej i skrypt, który je zbierze na maszynie z normalnym dostępem do sieci.

## Jak uzupełnić — wariant automatyczny

```bash
cd docs/analysis/assets
npm install playwright sharp        # jednorazowo
npx playwright install chromium     # jednorazowo
node capture_screenshots.mjs
```

Skrypt otwiera każdy adres z listy, robi zrzut pełnej strony w szerokości 1600 px, kompresuje do WebP z jakością 82 i zapisuje pod nazwą `NN_produkt_temat.webp`. Typowy plik wychodzi w okolicach 150–250 KB, czyli poniżej limitu 300 KB/plik z briefu B-03. Skrypt wypisuje na koniec podsumowanie: co się udało, co zwróciło błąd i jaki jest łączny rozmiar katalogu.

Adresy prowadzą wyłącznie do publicznej dokumentacji i stron produktowych — **nie ma wśród nich niczego za logowaniem ani za rejestracją na wersję próbną**, zgodnie z ograniczeniem „tylko źródła publicznie dostępne” z briefu.

## Jak uzupełnić — wariant ręczny

Jeżeli któryś adres przestanie działać (interfejsy i dokumentacje zmieniają się między wersjami), zrób zrzut ręcznie i zapisz pod tą samą nazwą. Wymagania: szerokość ok. 1600 px, format WebP lub JPEG, poniżej 300 KB. Do przeliczenia pojedynczego pliku:

```bash
npx sharp-cli --input zrzut.png --output 12_zabbix_problems_list.webp resize 1600 -- webp --quality 82
```

## Zasady, których trzeba pilnować przy uzupełnianiu

1. **Data przy każdym zrzucie.** Dopisz ją do tabeli poniżej w kolumnie „pobrano”. Analiza bez daty starzeje się niezauważalnie — interfejs, który dziś ilustruje wzorzec, za pół roku może już go nie mieć.
2. **Odróżniaj materiał marketingowy od dokumentacji.** Kolumna „typ” w tabeli mówi, czego się spodziewać: `[dok]` to instrukcja użytkownika lub referencja produktu, `[mkt]` to strona sprzedażowa z wyidealizowanym ekranem. Zrzut z materiału marketingowego jest dowodem na to, co producent *deklaruje*, a nie na to, jak produkt *działa*.
3. **Nie kadruj tak, żeby wzorzec wyglądał lepiej, niż jest.** Jeśli lista alarmów u konkurenta ma trzy pozycje na demo, a nie sto, zapisz to w opisie.

## Lista ujęć — 48 pozycji

Kolumna „wzorzec” odsyła do [katalogu wzorców](../01_analiza_ux_konkurencji.md#3-katalog-wzorców-z-werdyktem). Pozycje oznaczone **★** są cytowane wprost w analizie albo w Artifaccie i mają pierwszeństwo, gdyby czasu starczyło tylko na część.

### Wod-kan i smart water (12)

| # | Plik | Co ma być na ekranie | Adres | Typ | Wzorzec | Pobrano |
|---|---|---|---|---|---|---|
| 01 | `01_inventia_dataportal_wizualizacja.webp` | Ekran wizualizacji przepompowni | https://www.inventia.pl/dataportal-jak-wizualizacja-danych-moze-ulatwic-twoja-prace/ | `[mkt]` | W-24, W-25 | |
| 02 | `02_inventia_dataportal_scada.webp` | Prezentacja modułu SCADA | https://www.inventia.pl/przetestuj-funkcjonalnosc-dataportal-scada-bez-ponoszenia-kosztow-nowoczesna-wizualizacja-i-monitoring-danych-w-zasiegu-reki/ | `[mkt]` | W-25 | |
| 03 | `03_dataportal_applications.webp` | Katalog zastosowań i ekranów | https://dataportal.pl/en/applications/ | `[mkt]` | W-01 | |
| 04 | `04_aquard_scada.webp` | Ekran wizualizacji procesów | https://aquard.pl/scada/ | `[mkt]` | W-24 | |
| 05 | `05_aquard_hydranet_expert.webp` | Prezentacja tabelaryczna i przestrzenna | https://aquard.pl/hydranet-expert/ | `[mkt]` | W-19 | |
| 06 | `06_aquard_monitoring_sieci.webp` | Widok monitoringu sieci | https://aquard.pl/monitoring-sieci-wodociagowej/ | `[mkt]` | W-19 | |
| 07 ★ | `07_hawle_live_cap_mapa.webp` | Mapa hydrantów jako interfejs główny | https://www.hawle.com/pl/hawle-knowledge/systemy-i-rozwiazania/hawle-live-cap-rewolucja-w-monitorowaniu-hydrantow-podziemnych-na-przykladzie-hydrantu-uno | `[mkt]` | **W-19** | |
| 08 | `08_hawle_monitoring_sieci.webp` | Przegląd rozwiązania | https://www.hawle.com/Monitoring_sieci_wodocigowej | `[mkt]` | W-19 | |
| 09 ★ | `09_kallipr_kloud_fleet.webp` | Pulpit zarządzania flotą urządzeń | https://kallipr.com/product/kallipr-kloud-fleet/ | `[mkt]` | **W-02**, W-17 | |
| 10 | `10_kallipr_water_utilities.webp` | Widok dla zakładu wodociągowego | https://kallipr.com/industries/water-utilities/ | `[mkt]` | W-01 | |
| 11 ★ | `11_hwm_datagate.webp` | Portal DataGate — mapa, dashboard, alarmy | https://www.hwmglobal.com/datagate/ | `[mkt]` | W-19 | |
| 12 ★ | `12_ayyeka_dashboard_widgets.webp` | Widżety dashboardu, w tym średnie regionalne | https://www.ayyeka.com/en/knowledge/dashboard-widgets | `[dok]` | **W-02**, W-21 | |

### Przemysłowy monitoring aktywów i SCADA w chmurze (13)

| # | Plik | Co ma być na ekranie | Adres | Typ | Wzorzec | Pobrano |
|---|---|---|---|---|---|---|
| 13 ★ | `13_ignition_quality_overlays.webp` | Nakładki jakości renderowane na wartości | https://www.docs.inductiveautomation.com/docs/8.1/platform/tags/quality-codes-and-overlays | `[dok]` | **W-03** | |
| 14 ★ | `14_ignition_quality_codes_table.webp` | Tabela kodów jakości Good/Uncertain/Bad | https://www.docs.inductiveautomation.com/docs/8.1/platform/tags/quality-codes-and-overlays | `[dok]` | **W-03** | |
| 15 | `15_ignition_perspective_overview.webp` | Przegląd modułu Perspective | https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/perspective | `[dok]` | W-16 | |
| 16 ★ | `16_ignition_perspective_mobile.webp` | Ten sam ekran na telefonie i na desktopie | https://inductiveautomation.com/ignition/modules/perspective | `[mkt]` | **W-16** | |
| 17 | `17_ignition_responsive_tips.webp` | Kontenery punktów granicznych | https://corsosystems.com/posts/5-responsive-design-tips-for-perspective | `[art]` | W-16 | |
| 18 | `18_hmi_best_practices.webp` | Zestawienie zasad projektowych HMI | https://nfmconsulting.com/knowledge/hmi-design-best-practices/ | `[art]` | W-06 | |
| 19 | `19_aveva_insight_dashboard.webp` | Dashboard chmurowy | https://www.aveva.com/en/products/insight/ | `[mkt]` | W-23 | |
| 20 | `20_aveva_insight_mobile.webp` | Aplikacja mobilna | https://apps.apple.com/us/app/aveva-insight/id1428614248 | `[mkt]` | W-16 | |
| 21 ★ | `21_thingsboard_alarms_table.webp` | Tabela alarmów z akcjami w wierszu | https://thingsboard.io/docs/pe/reference/widgets/alarm-widgets/alarms-table/ | `[dok]` | **W-09** | |
| 22 ★ | `22_thingsboard_alarms_filters.webp` | Filtry stanu, priorytetu, typu, przypisania | https://thingsboard.io/docs/pe/reference/widgets/alarm-widgets/alarms-table/ | `[dok]` | **W-09** | |
| 23 ★ | `23_thingsboard_alarm_rules.webp` | Konfiguracja reguły: warunek utworzenia i wyczyszczenia | https://thingsboard.io/docs/user-guide/alarm-rules/ | `[dok]` | **W-14**, **W-15** | |
| 24 | `24_thingsboard_working_with_alarms.webp` | Cykl życia alarmu | https://thingsboard.io/docs/user-guide/alarms/ | `[dok]` | W-10 | |
| 25 ★ | `25_thingsboard_claiming.webp` | Przejęcie urządzenia przez klienta | https://thingsboard.io/docs/user-guide/claiming-devices/ | `[dok]` | **W-17**, W-18 | |

### Monitoring i obserwowalność IT (15)

| # | Plik | Co ma być na ekranie | Adres | Typ | Wzorzec | Pobrano |
|---|---|---|---|---|---|---|
| 26 ★ | `26_grafana_nodata_error_states.webp` | Rozdzielenie „brak danych” od „błąd” | https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rule-evaluation/nodata-and-error-states/ | `[dok]` | **W-08** | |
| 27 ★ | `27_grafana_missing_data.webp` | Obsługa luk w danych i serie nieaktualne | https://grafana.com/docs/grafana/latest/alerting/guides/missing-data/ | `[dok]` | **W-08** | |
| 28 ★ | `28_grafana_annotations.webp` | `summary`, `description`, `runbook_url` przy regule | https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rules/annotation-label/ | `[dok]` | **W-11** | |
| 29 ★ | `29_grafana_silences.webp` | Tworzenie wyciszenia | https://grafana.com/docs/grafana/latest/alerting/configure-notifications/create-silence/ | `[dok]` | **W-13** | |
| 30 ★ | `30_grafana_alert_detail_redesign.webp` | Przebudowany widok szczegółów alarmu | https://grafana.com/blog/2024/05/14/grafana-alerting-new-tools-to-resolve-incidents-faster-and-avoid-alert-fatigue/ | `[art]` | **W-11** | |
| 31 | `31_grafana_active_notifications.webp` | Widok aktywnych powiadomień, pogrupowanych | https://grafana.com/docs/grafana/latest/alerting/monitor-status/view-active-notifications/ | `[dok]` | W-12 | |
| 32 ★ | `32_zabbix_problems_list.webp` | Lista problemów jako ekran startowy | https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/monitoring/problems | `[dok]` | **W-01** | |
| 33 ★ | `33_zabbix_update_problem.webp` | Okno aktualizacji: komentarz, priorytet, potwierdzenie | https://www.zabbix.com/documentation/current/en/manual/acknowledgment | `[dok]` | **W-10** | |
| 34 ★ | `34_zabbix_event_details.webp` | Historia działań i komentarzy przy zdarzeniu | https://www.zabbix.com/documentation/current/en/manual/acknowledgment | `[dok]` | **W-10** | |
| 35 | `35_zabbix_suppression.webp` | Wygaszanie problemu | https://www.zabbix.com/documentation/current/en/manual/acknowledgment/suppression | `[dok]` | W-13 | |
| 36 | `36_zabbix_severity.webp` | Skala priorytetów i jej kolory | https://www.zabbix.com/documentation/current/en/manual/config/triggers/severity | `[dok]` | W-06, W-07 | |
| 37 ★ | `37_alertmanager_overview.webp` | Grupowanie, wyciszanie, inhibicja | https://prometheus.io/docs/alerting/latest/alertmanager/ | `[dok]` | **W-12**, W-20 | |
| 38 | `38_alertmanager_inhibition.webp` | Reguły inhibicji na przykładzie | https://oneuptime.com/blog/post/2026-01-27-alertmanager-inhibition-rules/view | `[art]` | W-20 | |
| 39 | `39_datadog_monitor_status.webp` | Strona statusu monitora z akcjami | https://docs.datadoghq.com/monitors/status/status_page/ | `[dok]` | W-13 | |
| 40 ★ | `40_datadog_downtimes.webp` | Przerwy serwisowe i ostrzeżenie o skutkach ubocznych | https://docs.datadoghq.com/monitors/downtimes/ | `[dok]` | **W-26** | |

### Wzorce mobilne, normy i wzorce ogólne (8)

| # | Plik | Co ma być na ekranie | Adres | Typ | Wzorzec | Pobrano |
|---|---|---|---|---|---|---|
| 41 ★ | `41_pagerduty_mobile_incident.webp` | Szczegół incydentu na telefonie: oś czasu, akcje | https://support.pagerduty.com/main/docs/mobile-app | `[dok]` | **W-16** | |
| 42 ★ | `42_pagerduty_incidents_page.webp` | Lista incydentów i triage | https://support.pagerduty.com/main/docs/navigate-the-incidents-page | `[dok]` | **W-09** | |
| 43 | `43_pagerduty_mobile_marketing.webp` | Ekran mobilny w materiale producenta | https://www.pagerduty.com/platform/incident-management/on-call-management/mobile/ | `[mkt]` | W-16 | |
| 44 ★ | `44_isa101_going_gray.webp` | Porównanie ekranu kolorowego i szarego | https://control.com/technical-articles/going-gray/ | `[art]` | **W-06** | |
| 45 | `45_isa101_guide.webp` | Zasady ISA-101 w zestawieniu | https://hmilibrary.com/standards/isa-101 | `[art]` | W-06 | |
| 46 | `46_opc_quality_codes.webp` | Mapowanie kodów jakości OPC UA | https://reference.opcfoundation.org/v104/Core/docs/Part8/A.4.3/ | `[std]` | W-03 | |
| 47 ★ | `47_wcag_141_examples.webp` | Przykłady zgodne i niezgodne z SC 1.4.1 | https://www.thewcag.com/criteria/1.4.1 | `[std]` | **W-07** | |
| 48 ★ | `48_datacake_rule_engine.webp` | Wizualny kreator reguły bez kodu | https://datacake.co/iot-rule-engine-lorawan-mqtt-sms-email-alerting | `[mkt]` | **W-14** | |

## Po uzupełnieniu

1. Wpisz daty pobrania do kolumny „pobrano”.
2. Sprawdź łączny rozmiar katalogu: `du -sh .` — powinien zmieścić się poniżej ~12 MB przy 48 plikach.
3. W [`../01_analiza_ux_konkurencji.md`](../01_analiza_ux_konkurencji.md) podmień odwołania do wzorców na osadzone obrazy tam, gdzie zrzut faktycznie coś dokłada do tekstu.
4. W Artifaccie z rekomendacjami podmień schematy SVG na rzeczywiste zrzuty osadzone jako `data:` URI — pamiętając o limicie 16 MB na całą stronę, więc do Artifactu przygotuj osobne, mniejsze warianty (szerokość ok. 900 px wystarczy).
