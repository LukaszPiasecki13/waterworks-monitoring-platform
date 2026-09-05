# Jedna sesja SQLAlchemy na żądanie; `transaction()` z dowolnego repozytorium obejmuje całą jednostkę pracy

Wszystkie repozytoria dostają sesję z tej samej zależności `get_db`, więc w obrębie jednego żądania HTTP dzielą **jedną** `Session`. `SQLRepository.transaction()` nie otwiera własnej transakcji — otwiera blok, który na wyjściu commituje całą sesję. Dzięki temu serwis może pisać przez kilka repozytoriów (także z innych modułów) w jednym bloku `with`, bez przekazywania obiektu transakcji ani wzorca Unit of Work.

## Status

Proposed

## Kontekst

Operacje biznesowe rzadko dotykają jednej tabeli: redempcja kodu aktywacyjnego zapisuje kod i credential, tworzenie punktu pomiarowego czyta urządzenie i zapisuje punkt, kasowanie urządzenia rusza trzy moduły naraz. Alternatywą byłby jawny obiekt Unit of Work przekazywany do serwisów, albo transakcja per repozytorium z koordynacją na wyższym poziomie.

## Decyzja

- `core/dependencies.py` tworzy jedną `sessionmaker` (`expire_on_commit=False`, `AuditAwareSession` jako `class_`), a `get_db` wydaje sesję na żądanie i zamyka ją po odpowiedzi.
- Każde `<X>Repository(session)` w `dependencies.py` modułu dostaje `Depends(get_db)` — nigdy własnej sesji.
- `with jakies_repo.transaction():` **domyka wszystko**, co w tym żądaniu zapisano przez którekolwiek repozytorium.

## Konsekwencje

- Serwis nie potrzebuje obiektu transakcji w sygnaturze — stąd wzorzec „rdzeni bez commitu" opisany w [ADR-0008](0008-rdzenie-bez-commitu-w-operacjach-wielomodulowych.md).
- **`transaction()` nie jest re-entrantne.** Zagnieżdżony blok commituje zewnętrzną jednostkę pracy w połowie operacji. Jedyne takie miejsce w kodzie (`DeviceAuthService.verify` → `DeviceService.create_claimed`) radzi sobie obejściem: wewnętrzny commit konsumuje flagę audytu, więc zewnętrzny blok musi jawnie zawołać `tx.skip_audit()`. To działa, ale jest pułapką dla następnej osoby dodającej orkiestrację — patrz dług D-06 w [`07_analiza_paradygmatow.md`](../backend/07_analiza_paradygmatow.md#6-lista-długu-technicznego).
- Zależność między modułami przestaje być widoczna w sygnaturach: to, że `code_repo.transaction()` domyka też zapisy `credential_repo`, wynika wyłącznie ze współdzielonej sesji.
- Testy jednostkowe mogą podstawić zwykłą `Session` — `SQLRepository.commit()` wykrywa brak `AuditAwareSession` i pomija sprawdzenie audytu.
