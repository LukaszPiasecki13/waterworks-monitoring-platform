# Analiza UX/UI Konkurencji — Platformy Monitoringu Infrastruktury Wodno-Kanalizacyjnej

**Wersja:** 1.0  
**Data:** 2026-08-19  
**Autor:** Łukasz Piasecki  
**Kontekst:** Opracowanie map nawigacji, wzorowników UI i backlogu frontendu dla MVP platformy monitoringu wodociągów.

---

## Spis treści

1. [Metodologia](#część-1-metodologia)
2. [Analiza Produktów](#część-2-analiza-produktów)
3. [Standardy i Praktyki](#część-3-standardy-i-praktyki)
4. [Katalog Wzorców UI](#część-4-katalog-wzorców-ui--bierz--nie-bierz)
5. [Rekomendacje Architektury Informacji](#część-5-rekomendacje-architektury-informacji)
6. [Kluczowe Decyzje](#część-6-kluczowe-decyzje)
7. [Backlog Frontendu](#część-7-backlog-frontendu)

---

## Część 1: Metodologia

### Zakres Badania

- **Platforma:** wod-kan (polska + światowa), SCADA przemysłowy, asset monitoring (ABB, Siemens, Schneider)
- **Artefakty:** Screeny UI z dokumentacji produktów, artykułów case studies, live demos
- **Okres:** 2022–2026
- **Liczba produktów:** 20+ (zidentyfikowano, 4 zanalizowane szczegółowo)

### Kryterium Wyboru Produktów do Głębokie Analizy

1. **Inventia DataPortal** — polski wod-kan, dostępne pełne ekrany obiektowe
2. **ABB Ability Digital Powertrain** — industrial asset monitoring, przejrzysta architektura hierarchii
3. **TaKaDu CEM** — zaawansowana obsługa alarków (triage, właściciel, przyczyna)
4. **Inductive Automation Ignition Perspective** — SCADA klasyczne (antywzorzec do ominięcia)

### Technika Zbierania Danych

**Zautomatyzowany harvester (Playwright + Edge)** — collect screeny z 20+ stron produktowych, filtruj osadzone obrazki UI (rozdzielczość ≥700px, aspect ratio 1.05–3.2), wyodrębnij metadane.

**Rezultat:** 50+ screenshotów, 13 najlepszych wybranych do analizy.

---

## Część 2: Analiza Produktów

### 2.1 Inventia DataPortal (Polska, wod-kan)

**Pozycja:** Diagnostyka i wizualizacja pomiarów dla operatorów gminnych.

#### Kluczowe Obserwacje

**2.1.1 Pasek Świeżości (freshness bar) — WZORZEC KLUCZOWY**

```
⚪ ← ostatni pomiar (13:04)
━━━━━━▋     ← pasek: osi czasu interwału transmisji (5 min)
   4 min temu  Prognoza: 1 min do ostrzeżenia o braku komunikacji
```

Skalowanko liniowe do oczekiwanego interwału pomiarów. Operator widzi bez tabeli konfiguracji czy są problemy z łącznością. To pierwszy przypadek, gdzie freshness jest **first-class UI pattern** — nigdy nie widziałem tego w innych narzędziach.

**2.1.2 Hierarchia Ekranów**
- Widok gminny (list PZK'ów)
- Widok stacji (lista pomiarów + alarmów)
- Widok pomiaru (10-dniowy chart, min/max/avg, zakres dobowy)

**2.1.3 Tabela Diagnostyczna**
- Checklist zasilania, modeemu, czujnika w jednym panelu
- Status: ✓ OK | ⚠ WARN | ✗ BŁĄD — nie przez kolor, ale glyf + tekst
- Sekcja "Detale techniczne" schowata za expand (operator nie widzi, serwisant może)

#### Wady

- Ekrany obiektu są przeładowane (40 bitów rejestru Modbus wprost dla operatora)
- Brak triage'u alarmów (wszystkie alarmy równo)
- Właściciel alarmu nie jest widoczny — brak możliwości delegacji

#### Rating: ★★★★☆ (4/5)

---

### 2.2 ABB Ability Digital Powertrain (Industrial Asset Monitoring)

**Pozycja:** Hierarchiczny przegląd zdrowia zasobów (Powertrains → Asset Groups → Assets).

#### Kluczowe Obserwacje

**2.2.1 Hierarchia i Filtrowanie**

Trzy poziomy agregacji:
- KPI donuts: # Powertrains, # Asset Groups, # Assets, Connectivity
- Tabela: Powertrain name | Condition Index | Critical Issues | Last Update
- Filtry: Status chips (Healthy | Warning | Critical), Org filter

Operator może patrzeć zarówno na podsumowanie ("Ile powertrain'ów ma warning?"), jak i drążyć szczegóły jednego zasobu.

**2.2.2 Triple Encoding Status**

```
🔴 CRITICAL | pressure > 6.5 bar
```

- Kolor (dla CVD-sensitive): czerwony
- Glyf (dla słabego widzenia): ●
- Tekst (dla jasności): "CRITICAL"

Zgodnie z ISA-18.2 — nigdy nie polegaj na samym kolorze.

**2.2.3 Condition Overview (Master-Detail)**

- Lewy panel (300px): Hierarchia assetów, mini status (zielony pasek % health)
- Prawy panel: Status tabela z kolumnami (Asset | Condition | Power | Vibration | Temperature | Humidity)
- Inline charts sparkline w każdej kolumnie

#### Rating: ★★★★★ (5/5 — best-in-class architecture)

---

### 2.3 TaKaDu CEM (Alarm Management & Event Processing)

**Pozycja:** Centrale zarządzania zdarzeniami dla sieciach wodociągowych (leak detection, pressure management).

#### Kluczowe Obserwacje

**2.3.1 Triage zamiast Priorytetów**

```
Wymaga działania (2)          ← Actionable: leaks, breaks, extreme deviations
  └─ Pressure burst (Gmina Wierchowo, SUW Kolonia): 1.62 bar
     Reguła: pressure-low-critical · Przypisane: Grzegorz S.
     Czas odkrycia: 15:08 | Czas do potwierdzenia: 23 min
     
Do obserwacji (3)             ← Candidate: watch for trend, not critical
  └─ Pressure warning (Komora Polna): 4.71 bar
     Reguła: pressure-high-warning
     
Informacyjne (5)              ← Informational: routine, no action needed
  └─ Daily report generated
  
Wyciszone (1)                 ← Suppressed/Muted: acknowledged but not closed
  └─ Temperature (Zbiornik Górny)
```

To ortogonalne do "severity" — event może być niski severity ale wymaga działania (sensor error), lub wysoki severity ale informacyjny (planowana konserwacja).

**2.3.2 Alarm jako Task**

Każde event ma:
- **Właściciel** (assigned to person)
- **Przyczyna zamknięcia** (słownik: `Closed/Leak`, `Closed/Sensor Error`, `Closed/Communication`, `Closed/Maintenance`, `False Alarm — need tuning`, `Confirmed Fault`)
- **Komentarze** (operator notes & attachments)
- **Timeline** (created → confirmed → closed)

Po 3 miesiącach query "false alarms grouped by rule" mówi Ci które progi trzeba dostroić.

**2.3.3 Event Detail — Sparkline + Baseline**

```
Chart 24-godzinny:
  Measured (blue)     ← rzeczywista linia
  Baseline (gray)     ← średnia z ostatnich 14 dni
  Threshold (red)     ← próg alarmowy
  [band] ← okres zdarzenia zaznaczony
```

Operator widzi czy to blip czy trend, czy event wpadł w anomalię rzeczywistą czy systemową.

#### Rating: ★★★★★ (5/5 — best-in-class alarm workflows)

---

### 2.4 Inductive Automation Ignition Perspective (Antipattern — Co Unikać)

**Pozycja:** Classical HMI z animacją 3D (zbiorniki, pompy, przepływy).

#### Kluczowe Obserwacje — Dlaczego to Nie Działa

**2.4.1 Tanki Kolorowe**

```
Zielony zbiornik = pełny = OK
Brązowy zbiornik = niski = ???
Pomarańczowy zbiornik = zagrażający = ???
Czerwony zbiornik = AWARIA
```

Operator widzi 5 zbiorników, 2 zielone, 1 pomarańczowy, 2 czerwone. Które wymagają działania? **Sekund stracone.**

**2.4.2 Mapa Synoptyczna (Synoptic Panel)**

- Wygląda jak "to faktycznie funkcjonuje" (są pompy, przepływy, cisnienie narysowane)
- Ale dla operatora bez 5 lat doświadczenia? — Czarna magia
- Skalowanie na mobilu — niemożliwe
- Accessibility — niedostępne dla slepo/słabowzroku

**2.4.3 Brak Triage'u Alarmów**

Alarm table:
```
|State        |Priority|Message           |Time    |
|NORMAL       |LOW     |Pump 1 idle       |13:04   |
|UNACK        |MEDIUM  |Tank low (80%)    |13:07   |
|UNACK        |HIGH    |Pressure out range|13:08   |
|ACK          |CRITICAL|Leak detected     |13:10   |
```

— Co ja robię jako operator? Wszystko jednakowo. ISA-101 mówi: **nigdy nie polegaj na ikonice koloru samego.**

#### Rating: ★☆☆☆☆ (1/5 — Avoid this approach)

---

## Część 3: Standardy i Praktyki

### 3.1 ISA-101 High Performance HMI

**Zasada główna:** Operator nie może błędu z wizualizacją w sytuacji awaryjnej.

#### Reguła 1: Kolor Wyłącznie dla Odchyleń

```
Stan normalny (95% ekranu)     → Neutralny (szary)
Ostrzeżenie (4% ekranu)         → Warmth (pomarańczowy)
Alarm krytyczny (1% ekranu)     → Red-like (czerwony)
```

**Konsekwencja:** W Twoim `tokens.css`, `--status-ok: green` jest błędem. Zmień na `--st-normal: gray` i zarezerwuj kolor wyłącznie dla stanu `warn` i `alarm`.

#### Reguła 2: Potrójne Kodowanie Statusu (Triple Encoding)

```
Status CRITICAL = Kolor (red) + Glyf (●) + Tekst ("CRITICAL")
```

Dla CVD-friendly: 15% populacji ma daltonizm. Sami glyfy nie wystarczą (osób niewidowych), same teksty (czytanie szybko) — bierz **wszystkie trzy**.

#### Reguła 3: Nigdy Animacja dla Alertu

Migający element = denerwujący dla operatora. **Static color only** + audio pulse (jeśli jest dźwięk).

---

### 3.2 ISA-18.2 Alarm Lifecycle

Alarm przechodzi przez stany:

```
Unacknowledged (NEW)
    ↓ [operator clicks ACK button]
Acknowledged (ACK)
    ↓ [operator clicks MUTE or system times out]
Shelved (MUTE)         [explicitly silenced by operator]
Suppressed (AUTO)      [silenced by system config]
Out-of-Service (DISABLE) [maintenance mode]
```

**Każdy stan musi być widoczny w UI — bez polegania na kolorze.** TaKaDu pokazuje: `NEW · ACK · MUTE` — tekstowe znaczniki.

---

### 3.3 Master-Detail Layout

```
┌─────────────────────────────────────────────┐
│  [Gmina Wierchowo]  [SUW Kolonia] [...]     │ ← nawigacja
├─────────────────────────────────────────────┤
│ Obiekty (lewy panel)      │  Szczegóły (prawy) │
│ ────────────────────────  │  ────────────────  │
│ • Przepompownia Dolna     │ Przepompownia      │
│ ★ SUW Kolonia            │ Dolna              │
│ • Komora Polna            │ [map + chart]      │
│ • Hidrofornia Zachód      │ [4 tiles]          │
│ • Zbiornik Górny          │                    │
│ • Studnia Głęboka 2       │                    │
│                           │ [active alarms]    │
│ 15 objects · 6 selected   │                    │
└─────────────────────────────────────────────┘
```

**Zasada:** Utrzymuj kontekst listy widoczny podczas drążenia szczegółów. Unika powrotu do listy cyklicznie.

**Responsive:** <1024px → przełącz na full-screen detail, ukryj listę (wróć via back button).

---

## Część 4: Katalog Wzorców UI — BIERZ / NIE BIERZ / ROZWAŻ

| # | Wzorzec | Opis | BIERZ | Etap | Koszt | Źródło |
|---|---------|------|-------|------|-------|--------|
| **1** | **Pasek Świeżości (Freshness Bar)** | Pasek na skali 0→interwał pomiarów, podpowiadający czas do progu braku komunikacji | ✅ | MVP | M | Inventia |
| **2** | **Status Badge (Triple Coding)** | Kolor + Glyf + Tekst dla każdego stanu | ✅ | MVP | M | ABB, TaKaDu |
| **3** | **Master-Detail (Split View)** | Lista po lewej, szczegóły po prawej, kolista nawigacja | ✅ | MVP | M | ABB, TaKaDu |
| **4** | **Value Tile (4-column grid)** | Kafelki: wartość | zakres | min/avg/max | ✅ | MVP | M | ABB |
| **5** | **Sparkline w Tabeli** | Mini chart w kolumnie (2-series: measured vs baseline) | ✅ | MVP | M | TaKaDu, Inventia |
| **6** | **Triage zamiast Priorytetów** | Grupowanie: Wymaga działania / Do obserwacji / Informacyjne / Wyciszone | ✅ | MVP | L | TaKaDu |
| **7** | **Alarm Ownership** | Każde zdarzenie przypisane do pracownika | ✅ | MVP | M | TaKaDu |
| **8** | **Słownik Przyczyn Zamknięcia** | Operator wybiera przyczynę z listy (Confirmed Fault / Sensor Error / Communication / Maintenance / False Alarm) | ✅ | MVP | M | TaKaDu |
| **9** | **State Timeline (banda za banda)** | Wizualizacja binarna: connectivity, power, sensor status jako paskami w czasie | ✅ | Phase 2 | M | Inventia Diagnostyka |
| **10** | **Chart z Pasem Ereignisu** | Wykres z zaznaczonym okresem alarmu (background fill) | ✅ | MVP | S | TaKaDu, Inventia |
| **11** | **Reference Line (Próg)** | Linia progu alarmowego na wykresie, dash'em nie solidem | ✅ | MVP | S | TaKaDu |
| **12** | **Baseline Overlay** | Druga seria: średnia z 14 dni dla porównania z trendem | ✅ | Phase 2 | M | TaKaDu |
| **13** | **Filtry jako Chips** | Status chips: [All] [Alarm] [Warning] [NoComm] — klikalne, bez multiselect | ✅ | MVP | S | ABB, TaKaDu |
| **14** | **Hierarchia Assetów** | Gmin → PZK → Stacja → Pomiary; toggle do/od agregacji | ✅ | MVP | L | ABB, Inventia |
| **15** | **Nested Tabs** | W widoku obiektu: Przegląd / Pomiary / Alarmy / Diagnostyka | ✅ | MVP | M | Inventia, ABB |
| **16** | **"Wyciszone zawsze widoczne"** | Osobna sekcja dla muted alarmów (operator musi móc je wznowić) | ✅ | MVP | S | TaKaDu |
| **17** | **Organization Switcher** | Prawy górny róg: [Gmina Wierchowo ▾] [Operator ▾] [Notifications] [Avatar] | ✅ | MVP | M | Inventia, ABB |
| **18** | **Data Freshness Indicator** | Timestamp + relative time ("2 min temu", "wczoraj o 13:00") | ✅ | MVP | S | Inventia |
| **19** | **Empty State Positive** | Brak alarmów → icon ✓ + tekst "Brak aktywnych zdarzeń" (nie puste pole) | ✅ | MVP | S | TaKaDu |
| **20** | **Responsive Grid (4→2→1 col)** | Tiles zmieniają layout na wąskich ekranach | ✅ | MVP | M | Standards |
| **21** | **Kommentarz w Zdarzeniu** | Text field + attachment button dla notatek operatora | ✅ | Phase 2 | M | TaKaDu |
| **22** | **Event-Count Icons** | 5-ikono array: [💬 3] [📎 1] [🔔 2] — liczby komunikacji/attachmentów/notyfikacji | ✅ | Phase 2 | M | TaKaDu |
| **23** | **Checklist Diagnostyczny** | Polski: zasilanie / modem / czujnik / sygnał / temperatura / bufor / watchdog | ✅ | Phase 2 | M | Inventia |
| **24** | **Sekcja "Detale Techniczne" (expand)** | Rejestr Modbus, firmware version — schowane za expand | ✅ | Phase 2 | S | Inventia |
| **25** | **Theme Toggle (Light/Dark)** | Explicit toggle w UI + system `prefers-color-scheme` | ✅ | MVP | S | Standards |
| **26** | **Toolbar Search** | Szukanie obiektu po nazwie, ID, lokalizacji | ✅ | Phase 2 | M | Standards |
| **27** | **Sort Control** | "Sortuj: [Po ostatnim pomiaru ▾]" | ✅ | MVP | S | ABB, TaKaDu |
| **28** | **Breadcrumb Navigation** | "Gmina > PZK > Stacja > Pomiar" — łatwo wrócić | ✅ | MVP | S | ABB |
| **29** | **CSV Export** | Button w toolbar: Export filtered data as CSV | ✅ | Phase 2 | M | Standards |
| **30** | **Alert Audio Pulse** | Dźwięk (nie miganie!) dla nowych krytycznych zdarzeń | ❌ | Phase 3+ | L | Audioble |
| **31** | **Map/Synoptic View** | Mapa geograficzna lub schemat sieci z assetami | ❌ | Phase 3+ | XL | Wyd. |
| **32** | **Custom Dashboards** | Operator tworzy własne dashboardy (drag-and-drop tiles) | ❌ | Phase 3+ | XL | Wyd. |
| **33** | **Muting Rules** | System auto-mutes alarmów wg konfiguracji (np. mute pressure w nocy) | ❌ | Phase 3+ | L | Inv. Config |
| **34** | **SLA Metrics** | Dashboard: MTTR, % uptime, # alarmów per PZK | ❌ | Phase 3+ | M | Biz. Analytics |
| **35** | **Role-Based Dialogs** | Operatorzy widzą [Close], Technicy widzą [Troubleshoot], Admini widzą [Suppress] | ❌ | Phase 2 | M | Sec. Model |
| **36** | **Geofencing Alerts** | (Na urządzeniach mobilnych) Alert gdy pracownik wchodzi w zasięg PZK | ❌ | Phase 3+ | M | Mobile App |

**Legenda:**
- **BIERZ (✅)** — Weź do MVP lub zaplanowanego fazy
- **NIE BIERZ (❌)** — Omijaj (high cost, low value lub antiwzorzec)
- **Etap:** MVP / Phase 2 / Phase 3+
- **Koszt:** S (Small) / M (Medium) / L (Large) / XL (Extra Large)

---

## Część 5: Rekomendacje Architektury Informacji

### 5.1 Struktura Nawigacji — Flattened (4 pozycje)

**Obecna (błędna):**
```
Monitoring
├─ Obiekty
├─ Pomiary
├─ Alarmy
├─ Raporty
Admin
├─ Konfiguracja
├─ Użytkownicy
├─ Organizacje
├─ Uprawnienia
```

**Rekomendowana:**
```
🏠 Monitoring  ← Default (Dashboard / Quick View)
🎯 Obiekty     ← Lista do drążenia (master-detail)
⚠️  Alarmy      ← Triage list + active event detail
📊 Raporty     ← (Phase 2+)
───────────────────
⚙️  Admin       ← Ukryte pod user menu
```

**Uzasadnienie:**
- Operator spędza 80% czasu na 2 ekranach: lista + alarm detail
- Admin czyta config 2× miesiącu — nie potrzebuje highlight
- 4 pozycje pasują w navbar desktop i mobile

### 5.2 Master-Detail Widoku Obiektu

```
URL: /monitoring/objects/gw-2026-0002

Obiekty (lewy panel)
━━━━━━━━━━━━━━━━━━
Przepompownia Dolna
SUW Kolonia ★
  Ciśnienie wlot
  Temperatura
  Sygnał
Komora Polna
Hydrofornia Zachód

[6 objects] · [1 expanded]
```

**Taby w panelu szczegółów:**
- **Przegląd** (default) — 4 tiles + chart + active alarm
- **Pomiary** (Phase 2) — historia wszystkich pomiarów, CSV export
- **Alarmy** — timeline zdarzeń dla tego obiektu (oddzielone od globalnego alarmu view)
- **Diagnostyka** (Phase 2) — checklist + state timeline

### 5.3 Triage Alarmu — Sekcje

```
Wymaga działania (2)          ← Actionable
├─ Pressure burst
└─ No communication for 15 min

Do obserwacji (3)             ← Candidate
├─ High pressure trend
├─ Temperature rising
└─ Battery low (warn)

Informacyjne (5)              ← Informational
├─ Daily report
├─ Scheduled maintenance
└─ [...]

Wyciszone (1)                 ← Muted (persistent)
├─ Temperature (Zbiornik) — wznów
```

**Logika:**
- Każda sekcja collapsible, domyślnie "Wymaga działania" expanded
- Wyciszone zawsze widoczne (operator musi znać co się wyciszyło)

---

## Część 6: Kluczowe Decyzje

### Decyzja 1: Kolor Neutralny dla Stanu Normalnego

**Decyzja:** ✅ **Adopt ISA-101.** Zmień `--status-ok: green` na `--st-normal: #8a969c` (szary).

**Konsekwencja:**
- Wszystkie nowe komponenty muszą używać szarego dla "OK"
- Zielony zarezerwowany dla "Return to Normal" (ewent event po alarmie)
- Audyt: przejdź po frontend/ i zmień 20–30 classnames

**Timing:** Do Next Sprint — to jest łatwa zmiana, ale fundamentalna.

---

### Decyzja 2: Świeżość Danych as First-Class UI Element

**Decyzja:** ✅ **Adopt Freshness Bar.** Każdy pomiar ma pasek świeżości pod timestamp'em.

**Komponenta:**
```tsx
<DataFreshness 
  lastMeasureTime={time}
  expectedIntervalSeconds={300}  // 5 min
  thresholdSeconds={900}          // 15 min → no-comms
/>
// Renders: ⚫ ━━━━▋ (4 min temu)
```

**Timing:** MVP Phase 1 — to jest signature feature, różni Cię od Inventia.

---

### Decyzja 3: Alarm jako Task (nie Notification)

**Decyzja:** ✅ **Adopt TaKaDu Model.** Każde zdarzenie ma:
- Owner (assigned person)
- Close Reason (słownik)
- Comments + attachments

**Model danych (ponieważ musisz mieć to od dnia 1):**
```python
class AlarmEvent(BaseModel):
    id: str
    rule: str
    object_id: str
    severity: Literal["info", "warning", "alarm"]
    triage: Literal["actionable", "candidate", "informational"]
    state: Literal["new", "acknowledged", "muted", "suppressed"]
    
    # KLUCZOWE (nieobecne w welu systemach):
    assigned_to: Optional[str]        # user ID
    close_reason: Optional[Literal[
        "confirmed_fault", 
        "sensor_error", 
        "communication_issue",
        "maintenance", 
        "false_alarm"
    ]]
    comments: List[str]
    attachments: List[str]  # URLs
    
    created_at: datetime
    acknowledged_at: Optional[datetime]
    closed_at: Optional[datetime]
```

**Timing:** MVP Phase 1 — to decyduje o możliwości post-incident analysis.

---

### Decyzja 4: Nawigacja Flatten (4 pozycje zamiast 2-3 poziomów)

**Decyzja:** ✅ **Flatten to 4 Nav Items.** Monitoring / Obiekty / Alarmy / Raporty + Admin w user menu.

**Timing:** MVP Phase 1 — zmiana struktury `/app/*` routing'u.

---

### Decyzja 5: Nie Bierz Map / Synoptycznego w MVP

**Decyzja:** ❌ **Skip Map & Synoptic in Phase 1.** Przyjmij master-detail + checklist diagnostyczną jako jedyną wizualizację lokalizacyjną.

**Uzasadnienie:**
- Mapy = Mapbox/Leaflet integration = + 2–3 sprint'u
- Synopta = 3D biblioteki = accessibility nightmare
- TaKaDu pokazuje że zaawansowani operatorzy nie potrzebują mapy do triage'u
- Phase 3+: wtedy dodaj, gdy masz pewność że to się zwraca

---

---

## Część 8: Bibliografia & Referencje

### Produkty Zanalizowane

1. **Inventia DataPortal** (pl.inventia.pl) — wod-kan, best-in-class freshness
2. **ABB Ability Digital Powertrain** (powertrain.abb.com) — hierarchia & master-detail
3. **TaKaDu CEM** (takadu.com) — alarm triage & ownership
4. **Inductive Automation Ignition Perspective** — antipattern do ominięcia

### Standardy Odniesienia

- **ISA-101: High Performance HMI** — alarm color encoding, triple coding
- **ISA-18.2: Management of Alarm Systems** — alarm lifecycle states
- **WCAG 2.1 Level AA** — accessibility baseline
- **CVD-Safe Palettes** — Deuteranopia & Protan colorblind accessibility

### Narzędzia Techniczne

- **Playwright** (webdriver) — automated screenshot harvesting
- **React + Tailwind** — component framework
- **tokens.css** — design system foundation

### Zrzuty Konkurencji

Lokalizacja: `docs/business/assets/ux-benchmark/`

```
inventia-dataportal-art__img0.png  (1026×641) — Ekran obiektu
inventia-dataportal-art__img1.png  (1000×563) — Aplikacja wód-kan
inventia-wodkan__img*.png          (5 ekranów domowych)
abb-powertrain-help__img1.png      (1906×982) — Home page
abb-powertrain-help__img4.png      (1896×955) — Condition overview
takadu__img2.png                   (1902×846) — Events list
takadu__img3.png                   (1899×845) — Areas view
ignition-perspective__img*.png     (6 ekranów)
```

