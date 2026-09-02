# Modele ORM `core_data` są wspólnym słownikiem domenowym całego backendu

`User`, `Device`, `WaterObject` i `Organization` są importowane wprost przez `security`, `telemetry` i `device_identity` — jako typy w sygnaturach i jako cele zapytań SQL. Reguła „komunikacja między modułami wyłącznie przez warstwę serwisów" dotyczy **zapisu**, nie czytania i typowania.

## Status
Proposed

## Kontekst
[`01_backend-architecture.md` §2.3](../backend/01_backend-architecture.md) zakazuje importowania repozytoriów innego modułu i nie wypowiada się o modelach. W praktyce cross-modułowy import modeli `core_data` występuje w kilkunastu miejscach we wszystkich pozostałych modułach — konsekwentnie i z rozpoznawalnym uzasadnieniem: te encje są słownikiem domeny (patrz [`CONTEXT.md`](../../business/CONTEXT.md)), a nie prywatną strukturą modułu. Zapytania telemetryczne dołączają tabele `core_data` w SQL ([`queries.py`](../../../backend/app/modules/telemetry/repositories/queries.py)), bo alternatywą byłoby N+1 wywołań serwisu na każdy wiersz listy obiektów.

## Decyzja
- **Import modelu `core_data`** w innym module jest dozwolony — jako typ oraz jako cel odczytu/joinu w repozytorium.
- **Zapis do encji innego modułu** idzie przez jego serwis, bo to on zna reguły biznesowe i zapisuje audyt.
- Kierunek zależności jest jednostronny: `core_data` nie importuje modeli `telemetry` ani `device_identity`.

## Znany wyjątek
`DeviceLifecycleService` (moduł `core_data`) używa bezpośrednio `DeviceCredentialRepository` z `device_identity`, żeby usunąć credential w tej samej transakcji co resztę kaskady ([`device_lifecycle.py:59-71`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L59-L71)). To jedyny cross-modułowy zapis przez obce repozytorium; jest atomowość okupiona pominięciem warstwy serwisu i musi pozostać wyjątkiem, a nie precedensem — z audytem zapisywanym ręcznie na miejscu.

## Konsekwencje
- Zmiana kształtu modelu `core_data` może zepsuć kompilację innych modułów — to celowe sprzężenie na wspólnym słowniku, nie przypadek.
- Wydzielenie modułu do osobnego serwisu wymagałoby najpierw zerwania tych importów; przy modularnym monolicie to koszt odroczony świadomie.
