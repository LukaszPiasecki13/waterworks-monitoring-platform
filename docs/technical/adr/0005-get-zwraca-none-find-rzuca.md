# `get_` zwraca `None`, `find_` rzuca — konwencja wiążąca warstwę repozytoriów

W repozytorium prefiks nazwy metody jest kontraktem: `get_*` zwraca `Model | None` (albo kolekcję) i nigdy nie rzuca, `find_*` zwraca model i rzuca `NotFoundError`. Konwencja obowiązuje repozytoria; nazwy metod serwisów opisują przypadek użycia, nie sposób sygnalizowania braku.

## Status
Proposed

## Kontekst
Konwencja jest opisana w [`01_backend-architecture.md` §5.2](../backend/01_backend-architecture.md#konwencja-get_-vs-find_), a inwentaryzacja potwierdza ją bez jednego kontrprzykładu: 43 metody odczytu w 13 repozytoriach pięciu modułów — każde `get_*` ma w sygnaturze `| None` (lub typ kolekcji) i nie zawiera `raise`, każde `find_*` zwraca typ nieopcjonalny i rzuca. Dzięki temu serwis nie powtarza `if not x: raise NotFoundError(...)` przy każdym odczycie.

## Decyzja
Repozytorium udostępnia `find_*` wszędzie tam, gdzie brak obiektu jest błędem dla wołającego, i `get_*` tam, gdzie brak jest poprawnym stanem (sprawdzenie unikalności, idempotencja, warunkowe czyszczenie). Serwis wybiera wariant zamiast sam sprawdzać wynik.

## Granice reguły
- **Warstwa serwisów nie dziedziczy tej semantyki.** `DeviceService.get_by_id` rzuca, a `DeviceService.get_by_external_id` zwraca `None` — obie nazwy są poprawne, bo opisują przypadek użycia. Rozróżnienie `get_`/`find_` czytamy w repozytorium, nie w serwisie.
- **`MeasurementPointService.get_or_create_internal`** ([`measurement_points.py:158`](../../../backend/app/modules/core_data/services/measurement_points.py#L158)) nie łamie konwencji: to metoda serwisu, a jej nazwa mówi wprost, co robi. Łamie natomiast [ADR-0004](0004-transaction-jedyna-granica-transakcji.md), bo sięga po `repo.session` — to osobna sprawa, opisana jako dług.
- **`security/repositories/groups.py` nie ma ani jednej metody `find_*`** — brak obiektu obsługuje serwis, powtarzając `if not group: raise NotFoundError(...)` w czterech miejscach. To jedyny moduł odstający; drobny dług, nie osobna reguła.
