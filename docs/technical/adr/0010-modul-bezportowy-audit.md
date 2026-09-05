# Moduł bez warstwy `api/`: `audit` wystawia się przez port w `core/`, a jego endpointy mieszkają w modułach właścicieli danych

`audit` jest jedynym z pięciu modułów bez katalogu `api/`. Zamiast routera wystawia dwa protokoły w `core/audit.py`: `AuditPort` (zapis, wstrzykiwany do serwisów biznesowych) i `AuditReaderPort` (odczyt, wstrzykiwany bezpośrednio do endpointów cudzych modułów).

## Status

Proposed

## Kontekst

Historia audytu jest widoczna w UI, więc musi być gdzieś wystawiona. Naturalny odruch to `GET /audit?entity_type=…&entity_id=…` we własnym routerze modułu.

## Decyzja

Modułu nie wystawiamy — wystawiają go moduły, których dane opisuje. Kryterium, kiedy moduł ma być bezportowy:

> **Moduł nie dostaje własnego `api/`, jeśli jego dane nie mają samodzielnego przypadku użycia — czytane są zawsze *w kontekście* encji innego modułu, i to tamta encja rządzi uprawnieniem do ich odczytu.**

Historii audytu nikt nie ogląda „samej w sobie": ogląda się ją dla użytkownika (`GET /platform/users/{id}/audit` w `core_data`) albo dla gminy. Uprawnienie do obejrzenia należy do tamtej encji, więc endpoint też tam należy. Wyjątkiem jest globalny podgląd platformowy — mieszka w `security/api/platform_audit.py`, bo jego uprawnieniem jest `PLATFORM_VIEW_AUDIT`, czyli obiekt modułu `security`.

## Konsekwencje

- Implementację `audit` można podmienić (np. na zapis do zewnętrznego systemu logowania) bez zmiany ani jednej linii w serwisach, które go używają — zależą od protokołu z `core/`, nie od modułu.
- Cena: endpoint audytu w `security/api/` importuje `audit.dependencies` i `audit.schemas`, czyli sięga po zależności i schematy cudzego modułu. Jest to odstępstwo od zasady „cross-module wyłącznie przez serwisy" (`01_backend-architecture.md §2.3`) — świadome, bo port *jest* tu warstwą serwisową, ale warto, żeby zasada w architekturze wprost dopuszczała porty z `core/`.
- Nie ma jednego miejsca, w którym widać wszystkie endpointy audytu. Kto szuka „gdzie jest API audytu", nie znajdzie go po nazwie modułu.
