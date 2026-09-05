# Commit bez wpisu audytowego jest blokowany na poziomie sesji, a pominięcie audytu ma dwa dozwolone powody

`AuditAwareSession.commit()` rzuca `MissingAuditRecordError`, jeśli w sesji nie ustawiono flagi `audit_recorded` — a ustawia ją wyłącznie `AuditRepository.mark_recorded()`, wołane z `SqlAuditService.record()`. Niezmiennik „żadna zmiana biznesowa nie commituje się bez śladu" jest więc wymuszony przez SQLAlchemy, a nie przez dyscyplinę autora serwisu. Pominięcie audytu jest możliwe, ale musi być jawne i ma dokładnie dwa dopuszczalne uzasadnienia.

## Status

Proposed

## Kontekst

Log audytowy jest wymogiem produktowym (gmina musi wiedzieć, kto zmienił konfigurację obiektu), a nie wygodą deweloperską. Konwencja „pamiętaj zawołać `audit.record()`" przestaje działać przy pierwszym nowym serwisie napisanym w pośpiechu. Trzeba było wybrać między konwencją, przeglądem kodu a mechanizmem.

## Decyzja

Mechanizm, z dwiema jawnymi furtkami:

| Forma | Kiedy wolno | Wystąpienia |
|---|---|---|
| `transaction(skip_audit=True)` | **całą operację inicjuje urządzenie, nie człowiek** — nie ma aktora, o którym log miałby mówić | ingest telemetrii, zapis nonce'a challenge'u |
| `tx.skip_audit()` | operacja użytkownika, która **okazała się** niczego nie zmieniać (`calculate_delta` zwrócił pusto) albo powtórzone idempotentne żądanie; oraz gdy audyt zapisało już wywołanie zagnieżdżone | 13 miejsc w `core_data`, `security`, `device_identity` |

Każde inne pominięcie audytu jest błędem.

## Rozpatrywane alternatywy

- **Dekorator `@audited` na metodach serwisu** — łatwiejszy w czytaniu, ale nie broni się przed zapisem z pominięciem udekorowanej metody; niezmiennik na sesji broni się zawsze.
- **Trigger w bazie** — najmocniejszy, ale audyt potrzebuje kontekstu aplikacyjnego (aktor, delta pól, `context_id`), którego trigger nie ma.

## Konsekwencje

- Nowy serwis pisany bez audytu **nie przejdzie testów** — commit rzuci wyjątkiem. To zamierzone.
- Cena: `SecuritySeedService` (seed startowy poza ścieżką żądania) musi jawnie zawołać `commit(skip_audit=True)`, a każda ścieżka „nic się nie zmieniło" musi to udowodnić deltą, zamiast po prostu nie robić nic.
- Flaga jest per-sesja, nie per-encja: jeden `audit.record()` odblokowuje commit całej jednostki pracy. Niezmiennik brzmi więc „każdy commit ma **co najmniej jeden** wpis", a nie „każda zmieniona encja ma wpis".
