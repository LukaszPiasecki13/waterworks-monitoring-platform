# Moduł `audit`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`audit` trzyma niezmienny, append-only log zmian biznesowych: kto, co, kiedy zmienił, i jaka była delta. Nie ma własnej warstwy `api/` — nie jest wystawiony jako samodzielny router; inne moduły czytają jego historię przez własne endpointy (np. `GET /users/{id}/audit` w `core_data`).

## 2. Model domenowy

`AuditEvent` (tabela `audit_events`): `entity_type`, `entity_id`, `action`, `actor_id`, `actor_display_name`, `context_type`/`context_id` (opcjonalny grupujący kontekst, np. grupa uprawnień dla zmiany członkostwa), `changes` (JSONB), `created_at`. Klucz główny złożony: `(id, created_at)` — `created_at` jest częścią PK, co wspiera partycjonowanie tabeli po czasie (patrz `backend/alembic/README.md`).

`EntityType` (w `core/audit.py`) — zamknięty katalog auditowalnych encji: `core_data_user`, `security_user_group`, `attachment`, `core_data_organization`, `core_data_water_object`, `core_data_device`, `core_data_measurement_point`.

## 3. Kluczowe reguły i niezmienniki

**Append-only wymuszone na poziomie ORM**, nie tylko konwencją ([`models/audit.py:62-75`](../../backend/app/modules/audit/models/audit.py#L62-L75)):

```python
def _reject_mutation(mapper, connection, target: AuditEvent) -> None:
    raise RuntimeError("Audit events are append-only")

event.listen(AuditEvent, "before_update", _reject_mutation)
event.listen(AuditEvent, "before_delete", _reject_mutation)
```

Każda próba `UPDATE`/`DELETE` na `AuditEvent` przez SQLAlchemy — z jakiegokolwiek modułu — rzuca `RuntimeError` zanim zapytanie dotrze do bazy.

**`AuditEntry` jest niemutowalny** (`@dataclass(frozen=True, slots=True)` w `core/audit.py`) — raz zbudowany wpis audytowy nie może zostać przypadkiem zmodyfikowany po drodze do zapisu.

## 4. Nieoczywiste decyzje projektowe

**Commit bez audytu jest zablokowany na poziomie sesji, nie konwencją serwisu.** `AuditAwareSession.commit()` (`infrastructure/sql/factory.py`, opisane ogólnie w [`01_backend-architecture.md`](./01_backend-architecture.md#42-infrastructure)) sprawdza flagę `session.info["audit_recorded"]` i rzuca `MissingAuditRecordError`, jeśli jej nie ma i nikt nie przekazał `skip_audit=True`. Tę flagę ustawia wyłącznie `AuditRepository.mark_recorded()`:

```python
def mark_recorded(self) -> None:
    self.session.info["audit_recorded"] = True
```

...wołane z `SqlAuditService.record()` przy każdym zapisanym `AuditEvent`. Efekt: nie da się napisać nowego serwisu, który zapomni zapisać zdarzenia audytowego przy zmianie danych — commit po prostu nie przejdzie, dopóki `audit.record(...)` nie zostanie wywołane (albo transakcja jawnie nie zadeklaruje `skip_audit=True` przez `tx.skip_audit()`).

**Inversion of control przez `AuditPort`** — serwisy biznesowe (`core_data`, `security`) zależą od protokołu `AuditPort` z `core/audit.py`, nie od tego modułu bezpośrednio. FastAPI wstrzykuje konkretną implementację (`SqlAuditService`) przez `get_audit_service` (`audit/dependencies.py`). Dzięki temu moduł `audit` można by podmienić (np. na zapis do zewnętrznego systemu logowania) bez zmiany ani jednej linii w serwisach, które go używają.

**`calculate_delta` normalizuje wartości przed zapisem** (`audit_value()` w `core/audit.py`) — `UUID` → `str`, `datetime`/`date` → ISO 8601, `set` → posortowana lista (deterministyczny JSON, żeby dwa identyczne stany zawsze dawały identyczny zapis w kolumnie `changes`).

