# Commit bez wpisu audytowego jest błędem, nie przeoczeniem

`AuditAwareSession.commit()` rzuca `MissingAuditRecordError`, jeśli w sesji nie zarejestrowano zdarzenia audytowego i nie przekazano jawnie `skip_audit=True`. Niezmiennik „żadna zmiana biznesowa nie zapisuje się bez śladu" jest wymuszony na poziomie sesji SQLAlchemy, nie konwencją w serwisie.

## Status
Proposed

## Kontekst
System trafia do gminy — podmiotu publicznego, od którego można oczekiwać rozliczalności zmian w danych. Konwencja „pamiętaj o `audit.record()`" jest łamana przez pierwszy serwis napisany w pośpiechu; żeby ją utrzymać, musi być egzekwowana mechanicznie. Mechanizm opisuje [`05_audit_module.md` §4](../backend/05_audit_module.md); ten ADR zapisuje samą decyzję i jej granice.

## Decyzja
Sesja jest podklasą blokującą commit ([`infrastructure/sql/factory.py:12-30`](../../../backend/app/infrastructure/sql/factory.py#L12-L30)); flagę zdejmuje wyłącznie `AuditRepository.mark_recorded()` wołane z `SqlAuditService.record()`. Pominięcie audytu wymaga jawnej deklaracji (`transaction(skip_audit=True)` albo `tx.skip_audit()`) i jest dopuszczalne **tylko** w trzech przypadkach, wszystkich obecnych dziś w kodzie:

1. **Brak realnej zmiany** — delta stanu jest pusta, więc nie ma czego audytować (11 wystąpień, m.in. [`devices.py:159-161`](../../../backend/app/modules/core_data/services/devices.py#L159-L161), [`groups.py:203-205`](../../../backend/app/modules/security/services/groups.py#L203-L205)).
2. **Zapis, który nie jest zmianą biznesową** — strumień pomiarowy ([`ingest.py:131`](../../../backend/app/modules/telemetry/services/ingest.py#L131)) i przejściowy stan uwierzytelnienia, np. nonce challenge'a ([`device_auth.py:54`](../../../backend/app/modules/device_identity/services/device_auth.py#L54)).
3. **Bootstrap bez aktora** — seed uprawnień przy starcie aplikacji ([`seed.py:40`](../../../backend/app/modules/security/services/seed.py#L40)), gdzie nie istnieje użytkownik, którego można by wpisać jako sprawcę.

Zdarzenia cyklu życia **urządzenia** (redeem kodu, pierwszy claim) audytowi podlegają — patrz [ADR-0008](0008-dwa-podmioty-jeden-bearer.md). „Zapis zainicjowany przez urządzenie" **nie** jest samo w sobie powodem do pominięcia audytu; powodem jest wyłącznie to, że pomiar nie jest zmianą stanu biznesowego.

## Konsekwencje
- Nowy serwis, który zapomni o `audit.record()`, wywróci się na commicie w pierwszym teście integracyjnym — nie na produkcji, po fakcie.
- Testy jednostkowe podające zwykłą `Session` omijają ten strażnik świadomie ([`repository.py:54-59`](../../../backend/app/infrastructure/sql/repository.py#L54-L59)) — cena za możliwość testowania serwisów bez pełnej infrastruktury.
