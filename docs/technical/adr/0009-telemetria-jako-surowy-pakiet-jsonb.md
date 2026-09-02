# Telemetria jest przechowywana jako surowy pakiet JSONB, bez znormalizowanej tabeli pomiarów

Pakiet z gatewaya trafia do bazy w całości, jako JSONB w kolumnie `telemetry_packets.payload`. Nie istnieje tabela pojedynczych pomiarów — odczyty (wykresy, ostatnie wartości, statusy obiektów) rozpakowują payload w serwisie.

## Status
Proposed

## Kontekst
Struktura pakietu v2 to okna agregowane z wieloma punktami ([`measurement_packet.py`](../../../backend/app/modules/telemetry/schemas/measurement_packet.py)); jedno żądanie ingestu niesie kilka okien po kilka punktów. Normalizacja do wierszy `(point_id, timestamp, value)` wymagałaby przy każdej zmianie kształtu pakietu migracji danych, a przy kilku prototypach wysyłających co ~60 s wolumen jest nieistotny. Cały odczyt idzie dziś przez `TelemetryQueryService`, który rozpakowuje `payload` ([`query.py:51-78`](../../../backend/app/modules/telemetry/services/query.py#L51-L78), [`query.py:232-268`](../../../backend/app/modules/telemetry/services/query.py#L232-L268)).

## Decyzja
`telemetry_packets` jest niezmiennym logiem tego, co urządzenie faktycznie przysłało. `measurement_points` jest wyłącznie rejestrem istniejących punktów (typ, jednostka, granice techniczne) — nie przechowuje wartości. Analiza szeregów czasowych odbywa się w Pythonie, z twardymi limitami chroniącymi pamięć procesu (`MAX_PACKETS_PER_SERIES = 5000`) i flagą `truncated` w odpowiedzi, żeby wykres nie udawał kompletnego.

## Rozpatrywane alternatywy
- **Znormalizowana tabela pomiarów**: filtrowanie i agregacja po stronie SQL, indeksy po punkcie i czasie. Odrzucone na tym etapie — koszt migracji przy każdej zmianie formatu pakietu przewyższa dziś korzyść.
- **Baza szeregów czasowych (TimescaleDB/InfluxDB)**: właściwe narzędzie dla docelowej skali, ale dokłada drugi system do utrzymania przy pilotażu.

## Konsekwencje
- Filtry, których nie da się wyrazić w SQL (status obiektu liczony z `quality`), wymagają pobrania całego zbioru przed paginacją ([`query.py:158-173`](../../../backend/app/modules/telemetry/services/query.py#L158-L173)) — to działa dla gminy z kilkunastoma obiektami i przestanie działać wcześniej niż reszta systemu.
- Próg przejścia na inne rozwiązanie warto wyznaczyć liczbą obiektów i długością retencji, zanim wykresy zaczną zwracać `truncated`.
- Zmiana formatu pakietu nie wymaga migracji danych, ale kod odczytu musi umieć czytać stare payloady — stąd `.get(..., "unknown")` w każdym rozpakowaniu.
