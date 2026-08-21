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

User (bez organization_id, bez status — uprawnienia wyłącznie z grup)
  ↔ UsersOrganizations (M:N membership, brak kolumny roli)
  ↔ SecurityGroup (moduł security: grupy uprawnień z organization_id=NULL dla platform,
                    lub organization_id<UUID> dla gmin)
```

| Encja | Reprezentuje |
|---|---|
| `Organization` | Gmina / niezależny ZWiK — klient platformy |
| `WaterObject` | Fizyczny obiekt infrastruktury: przepompownia, hydrofornia, stacja uzdatniania, pomiar na sieci |
| `Device` | Gateway terenowy (ESP32 + modem) zainstalowany na obiekcie |
| `MeasurementPoint` | Kanał pomiarowy podłączony do urządzenia |
| `User` | Konto z dostępem do platformy (bez przypisania do organizacji) |
| `UsersOrganizations` | Członkostwo M:N — użytkownik należy do gminy, uprawnienia z grup |

## 3. Kluczowe reguły i niezmienniki

**Org-scoping i 404 zamiast 403** — Endpointy `/api/v1/orgs/{org_id}/...` wstrzykują `OrganizationAccess` (patrz [`01_backend-architecture.md`](./01_backend-architecture.md#72-autoryzacja-organizationaccess-i-platformcontext) §7.2):

```python
# FastAPI dependency
@router.get("/")
async def list_objects(access: OrganizationAccess = Depends(require_org_membership)):
    # access.organization_id zawsze pokrywa się z {org_id} z URL
    # access.actor to zalogowany użytkownik
    # access.permissions to kody uprawnień tego usera w tej gminie
```

- Użytkownik, który nie jest członkiem gminy, dostaje `NotFoundError(404)` już na poziomie `require_org_membership`, **zanim serwis w ogóle wejdzie w grę** — to świadomy wybór anty-enumeracyjny: `404` nie zdradza, czy gmina istnieje; `403` potwierdzałoby jej istnienie.
- Członkostwo sprawdzane na żywo przez `OrganizationAccess` na każde żądanie, niezależnie od JWT. Revoking dostępu (usunięcie z gminy) działa natychmiast, bez czekania na wygaśnięcie tokenu.

**`find_by_id` vs `get_by_id`** — `DeviceService.get_by_id` celowo woła `water_object_repo.find_by_id` (zwraca `None`), nie `get_by_id` (rzuca):

```python
def get_by_id(self, device_id: UUID, access: OrganizationAccess):
    device = self.repo.find_by_id(device_id)
    water_obj = self.water_object_repo.find_by_id(device.water_object_id)
    # Jeśli water_obj jest None, AttributeError zamknęła by lukę: nie przepuszczamy
    # urządzenia bez sprawdzenia, że jego obiekt należy do tej gminy
    assert_same_organization(access.organization_id, water_obj.organization_id)
    return device
```

Fail-closed (awaria zamknięta): jeśli relacja danych jest uszkodzona, rzucamy błąd zamiast pomijać weryfikację.

## 4. Nieoczywiste decyzje projektowe

- **404 zamiast 403 na cross-org dostęp** — patrz wyżej. Standardowa praktyka anty-enumeracyjna: `403` potwierdza, że zasób istnieje (tylko nie masz do niego dostępu); `404` nie zdradza nic.
- **`SQLRepository.transaction()` / `tx.skip_audit()`** — każdy serwis w tym module używa wspólnego context managera opisanego w [`01_backend-architecture.md`](./01_backend-architecture.md#42-infrastructure), zamiast powtarzanego `try/except/rollback/raise`. `tx.skip_audit()` używane, gdy `PATCH` nie zmienił żadnego pola (delta pusta) — commit bez wpisu audytowego.


