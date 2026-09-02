# Punkty pomiarowe powstają automatycznie z pierwszego pakietu, który je zgłosi

Gdy pakiet telemetryczny zawiera `point_id`, którego nie ma w bazie, backend zakłada `MeasurementPoint` sam — bez działania operatora i bez wpisu w audit logu. Ręczne API tworzenia punktów istnieje równolegle, do korekty metadanych.

## Status
Proposed

## Kontekst
Montaż w terenie wygląda tak: technik podłącza czujnik, urządzenie zaczyna go raportować. Wymaganie, żeby ktoś wcześniej wyklikał punkt w panelu, oznaczałoby, że pierwszy pakiet z nowym czujnikiem jest odrzucany, a dane z niego przepadają. `get_or_create_internal` ([`measurement_points.py:158-190`](../../../backend/app/modules/core_data/services/measurement_points.py#L158-L190)) rozwiązuje to po stronie ingestu ([`ingest.py:187-194`](../../../backend/app/modules/telemetry/services/ingest.py#L187-L194)).

## Decyzja
Urządzenie jest źródłem prawdy o tym, jakie punkty istnieje. Backend zapisuje przy autoprovisioningu to, co przysłało urządzenie (`point_type`, `unit`), po wcześniejszym sprawdzeniu, że `point_type` jest w rejestrze ([ADR-0011](0011-zakres-sensor-registry.md)). Późniejsza rozbieżność między zgłoszonym typem/jednostką a tym, co już jest w bazie, **nie** nadpisuje rekordu — generuje wpis `POINT_TYPE_MISMATCH` o powadze `critical` w `telemetry_errors`, a pakiet jest przyjmowany.

## Rozpatrywane alternatywy
- **Odrzucanie pakietów z nieznanym punktem (409/400)**: wymusza dyscyplinę konfiguracji, ale kosztuje utratą danych z terenu i telefonem do wsparcia przy każdym nowym czujniku. Odrzucone.
- **Nadpisywanie typu/jednostki tym, co przysłało urządzenie**: milcząco zmieniałoby znaczenie historycznych danych tego punktu. Odrzucone na rzecz zapisu niezgodności jako błędu.

## Konsekwencje
- Punkt utworzony automatycznie nie ma `min_technical`/`max_technical` — te uzupełnia się ręcznie przez API.
- Literówka w `point_id` po stronie firmware tworzy nowy, trwały punkt pomiarowy. Nie ma dziś mechanizmu scalania ani usuwania takich sierot poza usunięciem całego urządzenia.
- Autoprovisioning świadomie nie zapisuje audytu (nie jest zmianą wywołaną przez człowieka), ale odbywa się wewnątrz transakcji ingestu, która i tak deklaruje `skip_audit=True`.
