# W operacji obejmującej kilka modułów serwisy wystawiają rdzenie bez commitu, a transakcję trzyma orkiestrator

Metoda serwisu, która ma być użyta jako krok większej operacji, **nie otwiera własnego `transaction()`** — tylko zapisuje i flushuje, zostawiając commit wołającemu. Kontrakt jest zapisany w docstringu, dosłownie: „No-commit core — transaction belongs to caller." (`DeviceService.delete_device_record`) i „Flushes rather than commits: the transaction belongs to the caller." (`TelemetryIngestService.delete_all_for_device`, `TelemetryPacketRepository.create`).

## Status

Proposed

## Kontekst

Kasowanie urządzenia z platformy musi być atomowe przez trzy moduły: telemetria (pakiety), `core_data` (urządzenie, kaskadowo punkty pomiarowe), `device_identity` (credential). Gdyby każdy serwis commitował po swojemu, awaria w połowie zostawiłaby urządzenie bez pomiarów albo credential bez urządzenia.

## Decyzja

- Metoda przeznaczona do złożenia w większą operację jest „rdzeniem bez commitu": zapisuje przez repozytorium, woła `flush()` gdy potrzebuje ID, i **nie** commituje.
- Fakt ten jest deklarowany w docstringu, bo z sygnatury nie wynika.
- Transakcję otwiera jedna klasa-orkiestrator (`DeviceLifecycleService`) i to ona odpowiada za atomowość.
- Działa to wyłącznie dzięki współdzielonej sesji na żądanie — patrz [ADR-0001](0001-jedna-sesja-na-request.md).

## Konsekwencje

- Rdzeń bez commitu wywołany bez otwartej transakcji **po cichu nic nie zapisze** — zmiany zginą przy zamknięciu sesji. Nic tego nie wykrywa; jedyną ochroną jest docstring.
- Ten sam serwis ma więc dwa rodzaje metod: samodzielne (własny `with transaction()`) i rdzenie. `DeviceService` ma oba, co widać po `detach_from_organization` (samodzielna) i `delete_device_record` (rdzeń).
- Alternatywa — parametr `commit: bool = True` — byłaby widoczna w sygnaturze, ale rozgałęzia każdą metodę i zachęca do wołania z `commit=False` w miejscach, gdzie nie ma orkiestratora. Odrzucona na rzecz jawnej konwencji nazewniczo-dokumentacyjnej.
