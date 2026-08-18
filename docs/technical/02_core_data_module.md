# Moduł `core_data`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`core_data` trzyma dane referencyjne, na których budują wszystkie pozostałe moduły: organizacje (klientów/gminy), obiekty wodociągowe, urządzenia (gateway'e terenowe), punkty pomiarowe i użytkowników. To CRUD backbone systemu — standardowa struktura warstw z sekcji 5 architektury, bez wyjątków.


## 2. Model domenowy

```
Organization
  └─ WaterObject (organization_id)
       └─ Device (water_object_id)
            └─ MeasurementPoint (device_id)

User (organization_id, nullable — NULL = platform admin, widzi wszystkie organizacje)
```

| Encja | Reprezentuje |
|---|---|
| `Organization` | Gmina / niezależny ZWiK — klient platformy |
| `WaterObject` | Fizyczny obiekt infrastruktury: przepompownia, hydrofornia, stacja uzdatniania, pomiar na sieci |
| `Device` | Gateway terenowy (ESP32 + modem) zainstalowany na obiekcie |
| `MeasurementPoint` | Kanał pomiarowy podłączony do urządzenia |
| `User` | Konto z dostępem do platformy |

## 3. Kluczowe reguły i niezmienniki

**Org-scoping** (`utils/org_scope.py`):

```python
def assert_same_organization(actor: User, resource_organization_id: UUID) -> None:
    if actor.organization_id is not None and actor.organization_id != resource_organization_id:
        raise NotFoundError("Resource not found")
```

- Non-admin (`actor.organization_id is not None`) jest przypięty do własnej organizacji — próba dostępu do zasobu innej organizacji kończy się `404`, **nie `403`**: to świadomy wybór, żeby nie zdradzać samego istnienia zasobu w cudzej organizacji.
- `resolve_organization_id` — dla non-admina zawsze zwraca `actor.organization_id` (ignoruje to, co przyszło z klienta); platform admin (`organization_id is None`) dostaje to, co faktycznie zażądał.

**`find_by_id` vs `get_by_id`** — `DeviceService.get_by_id` celowo woła `water_object_repo.find_by_id` (zwraca `None`), nie `get_by_id` (rzuca):

```python
def get_by_id(self, device_id: UUID, actor: User):
    device = self.repo.find_by_id(device_id)
    water_obj = self.water_object_repo.find_by_id(device.water_object_id)
    assert_same_organization(actor, water_obj.organization_id)
    return device
```

Jeśli `water_object_id` urządzenia nie da się rozwiązać, `water_obj` jest `None` i `assert_same_organization(actor, None.organization_id)` rzuci `AttributeError` zamiast po cichu przepuścić urządzenie bez sprawdzenia organizacji — awaria zamknięta (fail-closed), nie otwarta.

## 4. Nieoczywiste decyzje projektowe

- **404 zamiast 403 na cross-org dostęp** — patrz wyżej. Standardowa praktyka anty-enumeracyjna: `403` potwierdza, że zasób istnieje (tylko nie masz do niego dostępu); `404` nie zdradza nic.
- **`SQLRepository.transaction()` / `tx.skip_audit()`** — każdy serwis w tym module używa wspólnego context managera opisanego w [`01_backend-architecture.md`](./01_backend-architecture.md#42-infrastructure), zamiast powtarzanego `try/except/rollback/raise`. `tx.skip_audit()` używane, gdy `PATCH` nie zmienił żadnego pola (delta pusta) — commit bez wpisu audytowego.


