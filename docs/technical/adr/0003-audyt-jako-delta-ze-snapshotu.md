# Audyt zapisuje deltę wyliczoną z migawki stanu encji

Każdy serwis zapisujący dane ma prywatne `_state(entity) -> dict` (jawna lista pól istotnych dla audytu) i `_record_audit(...)`. Metoda zapisu robi migawkę przed zmianą, migawkę po zmianie i zapisuje różnicę policzoną przez `calculate_delta`.

## Status
Proposed

## Kontekst
Wzorzec powtarza się w sześciu serwisach bez kontrprzykładu: [`devices.py:32-59`](../../../backend/app/modules/core_data/services/devices.py#L32-L59), [`measurement_points.py:40-66`](../../../backend/app/modules/core_data/services/measurement_points.py#L40-L66), [`water_objects.py:31-56`](../../../backend/app/modules/core_data/services/water_objects.py#L31-L56), [`organizations.py:39-59`](../../../backend/app/modules/core_data/services/organizations.py#L39-L59), [`users.py:28-53`](../../../backend/app/modules/core_data/services/users.py#L28-L53), [`groups.py:42-62`](../../../backend/app/modules/security/services/groups.py#L42-L62). Tam, gdzie tej samej migawki potrzebuje więcej niż jeden moduł, jest ona wyniesiona do `audit_state.py` ([`core_data/audit_state.py`](../../../backend/app/modules/core_data/audit_state.py), [`security/audit_state.py`](../../../backend/app/modules/security/audit_state.py)).

## Decyzja
Kanoniczny kształt metody zapisu:

```python
with self.repo.transaction() as tx:
    entity = self.repo.find_...(...)      # brak encji = błąd, patrz ADR-0005
    old_state = self._state(entity)
    self.repo.update(entity, ...)
    self.repo.flush(); self.repo.refresh(entity)
    new_state = self._state(entity)
    if not calculate_delta(old_state, new_state):
        tx.skip_audit()                    # brak zmiany = brak wpisu, ADR-0002
        return entity
    self._record_audit("UPDATE", entity, actor, old_state, new_state)
    return entity
```

Migawka jest **jawną listą pól**, nie `__dict__` encji: pola techniczne (`updated_at`) i wrażliwe (`hashed_password`) nie trafiają do logu. Zmianę hasła odnotowuje się jako `{"password": {"old": "[ukryte]", "new": "[zmieniono]"}}` ([`users.py:145-149`](../../../backend/app/modules/core_data/services/users.py#L145-L149)) — fakt zmiany bez wartości.

## Rozpatrywane alternatywy
- **Nasłuchiwacze zdarzeń SQLAlchemy (`before_update`) generujące audyt automatycznie**: zero powtórzeń w serwisach, ale audyt traci pojęcie aktora i intencji („UPDATE" zamiast „PERMISSIONS_UPDATE"), a każde pole ORM ląduje w logu. Odrzucone.
- **Zapis pełnych migawek zamiast delty**: prostsze, ale log rośnie liniowo z liczbą pól i nie odpowiada wprost na pytanie „co się zmieniło".

## Konsekwencje
- Dodanie pola do encji nie trafia do audytu, dopóki ktoś nie dopisze go do `_state` — to świadomy koszt jawności i pozycja do sprawdzenia w code review.
- `changes` musi być deterministycznym JSON-em: `audit_value()` normalizuje `UUID`, `datetime` i `set` przed zapisem.
