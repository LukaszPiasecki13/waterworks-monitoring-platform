# Moduł `core_data`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`core_data` trzyma dane referencyjne, na których budują wszystkie pozostałe moduły: organizacje (klientów/gminy), obiekty wodociągowe, urządzenia (gateway'e terenowe), punkty pomiarowe i użytkowników. To CRUD backbone systemu — standardowa struktura warstw z sekcji 5 architektury, bez wyjątków.

Czym `core_data` **nie jest**: nie robi autentykacji ani hashowania haseł (to `security/`), nie przechowuje samych pomiarów (to `telemetry/`).

## 2. Struktura

```text
modules/core_data/
├─ api/
│  ├─ organizations.py       # prefix /organizations
│  ├─ users.py                # prefix /users
│  ├─ water_objects.py        # prefix /objects
│  ├─ devices.py               # prefix /devices
│  └─ measurement_points.py    # prefix /measurement-points
├─ models/                     # Organization, User, WaterObject, Device, MeasurementPoint
├─ repositories/                # jeden na encję, dziedziczy SQLRepository
├─ schemas/
├─ services/                    # jeden na encję
├─ utils/
│  └─ org_scope.py              # assert_same_organization, resolve_organization_id
└─ tests/
```

Router modułu montowany jest w `main.py` pod prefiksem `/api/v1` (`app.include_router(core_data_router, prefix=API_V1_PREFIX)`).

## 3. Model domenowy

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

## 4. Endpointy API

Wszystkie pod `/api/v1`. Standardowy zestaw CRUD dla każdej encji (`GET` lista + paginacja, `POST` create, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`), plus:

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/organizations`, `/objects`, `/devices`, `/measurement-points`, `/users` | Lista z paginacją i filtrami |
| POST / GET / PATCH / DELETE | `.../{id}` | Standardowy CRUD |
| GET | `/users/{user_id}/audit` | Historia zmian użytkownika (odczyt z modułu `audit`) |

## 5. Kluczowe reguły i niezmienniki

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

## 6. Nieoczywiste decyzje projektowe

- **404 zamiast 403 na cross-org dostęp** — patrz wyżej. Standardowa praktyka anty-enumeracyjna: `403` potwierdza, że zasób istnieje (tylko nie masz do niego dostępu); `404` nie zdradza nic.
- **`SQLRepository.transaction()` / `tx.skip_audit()`** — każdy serwis w tym module używa wspólnego context managera opisanego w [`01_backend-architecture.md`](./01_backend-architecture.md#42-infrastructure), zamiast powtarzanego `try/except/rollback/raise`. `tx.skip_audit()` używane, gdy `PATCH` nie zmienił żadnego pola (delta pusta) — commit bez wpisu audytowego.

## 7. Zależności międzymodułowe

- Korzysta z `security.services.password` (`hash_password`) przy tworzeniu/aktualizacji użytkownika i sekretu urządzenia
- Korzysta z `security.services.permissions.PermissionService` (`assign_default_group`) po utworzeniu użytkownika
- Zapisuje zmiany przez `AuditPort` (`core/audit.py`), którego implementację dostarcza moduł `audit`
- `telemetry` czyta z modeli `Device`, `WaterObject`, `Organization` tego modułu (przez własne repozytoria — zgodnie z regułą "cross-module przez serwisy" to formalnie odstępstwo ograniczone do odczytu w zapytaniach agregujących, patrz [`04_telemetry_module.md`](./04_telemetry_module.md))

## 8. Testowanie

Testy jednostkowe serwisów z mockowanymi repozytoriami (`app/modules/core_data/tests/unit/`) + testy integracyjne z realną bazą (`tests/integration/`). Org-scoping ma dedykowane przypadki: dostęp cross-org musi zwrócić `404`, nie `403` ani `200`.
