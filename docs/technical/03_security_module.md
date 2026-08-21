# Moduł `security`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`security` odpowiada za trzy rzeczy: **authentication** (login, wydawanie i odświeżanie tokenów JWT), **authorization** (grupy uprawnień, sprawdzanie dostępu) i **hashowanie haseł**. Inne moduły korzystają z niego wyłącznie przez jego serwisy — nigdy przez `security/repositories/`.

## 2. Model domenowy

`UserGroup` (grupa uprawnień) ↔ `Permission` (many-to-many) ↔ `User` (many-to-many, przez `security_user_groups`). Grupy mogą być **platformowe** (`organization_id IS NULL`) lub **organizacyjne** (`organization_id = <UUID>`).

| Typ grupy | Kiedy tworzona | Uprawnienia | Może być edytowana |
|---|---|---|---|
| Platformowa Super Admin | CLI `create-superadmin` lub seed na start | wszystkie `PLATFORM_*` + brak dostępu do danych gmin | tylko przez super admina (no-op w UI) |
| Organizacyjna Admin | Seed przy tworzeniu gminy | wszystkie `CAN_*` danej gminy | przez administratora tej gminy |
| Organizacyjna Operator, Viewer | Seed przy tworzeniu gminy | ograniczone `CAN_*` | przez administratora tej gminy |

Unikalność nazw grupowych jest **złożona**: `UNIQUE (organization_id, name)` i `UNIQUE (organization_id, system_key)` — każda gmina ma własny komplet grup o tych samych nazwach systemu (`admin`, `operator`, `viewer`), grupa platformowa jest jedna. Systemowe grupy (`is_system=True`) nie mogą mieć zmienianej nazwy/opisu, ale uprawnienia grupy Super Admin są zamorożone (nie edytowalne, żeby admin nie mógł sobie odebrać dostępu).


## 3. Kluczowe reguły i niezmienniki

- **Ostatni admin jest chroniony**: logika w `replace_user_groups` (patrz [`../app/modules/security/services/groups.py`](../app/modules/security/services/groups.py)) odrzuca operację, która usunęłaby ostatniego użytkownika z platformowej grupy Super Admin (`BadRequestError`) — system nie może zostać bez superadmina. Administrator gminy nie jest chroniony (gmina może być bez administratora; super admin może ją naprawić).
- **Grupy systemowe częściowo zablokowane**: nazwy/opisu grup systemowych nie da się zmienić (`_ensure_custom_group`); uprawnień grupy Super Admin (`system_key="admin"`, `organization_id IS NULL`) nie da się edytować (`_ensure_permissions_editable`). Uprawnienia gminnych grup systemowych (`organization_id <> NULL`) są edytowalne.
- Każda zmiana grupy/przypisania generuje wpis audytowy przez `AuditPort`, chyba że delta stanu jest pusta (wtedy `tx.skip_audit()`).
- **Katalog uprawnień** (`app/modules/security/permission_catalog.py`) — zamknięta lista kodów. Grupy organizacyjne mogą zawierać wyłącznie kody `CAN_*`; grupy platformowe wyłącznie `PLATFORM_*` (egzekwowana w `PermissionService.resolve_permissions()`).


## 4. Struktura API

Module `security/api/` zawiera cztery pliki:

| Plik | Endpointy | Autoryzacja |
|---|---|---|
| `auth.py` | `/auth/token`, `/auth/refresh` | Brak (public token endpoint) |
| `permissions.py` | `GET /security/me/permissions` | Wymagany aktywny user |
| `groups.py` | Dwa oddzielne routery (patrz poniżej) | Zależne od routera |
| `platform_audit.py` | `GET /platform/audit` | `PLATFORM_VIEW_AUDIT` |

### Organizacyjne grupy (`/api/v1/orgs/{org_id}/groups`)

Oryginalnie w `core_data/api/org_groups.py`, przeniesione do `security/api/groups.py::org_router` (§1.1 planu separacji). Umożliwia członkom organizacji zarządzać grupami bezpieczeństwa tej organizacji.

- Autoryzacja: `require_org_or_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)` — członek organizacji OR admin platformy
- Walidacja: `_ensure_group_belongs_to_org()` zapobiega IDOR-om (404 zamiast 403 na cross-org access)
- Permissiony grupy: wyłącznie `CAN_*` (organizacyjne kody z katalogu)

### Platformowe grupy (`/api/v1/platform/groups`)

Oryginalnie w `core_data/api/platform_groups.py`, przeniesione do `security/api/groups.py::platform_router`. Umożliwia super adminom zarządzać grupami bezpieczeństwa platformy.

- Autoryzacja: `require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)`
- Permissiony grupy: wyłącznie `PLATFORM_*`

### Audyt platformy (`/api/v1/platform/audit`)

Oryginalnie w `core_data/api/platform_audit.py`, przeniesione do `security/api/platform_audit.py`. Pokazuje wszystkie zdarzenia audytowe w systemie (dostęp ograniczony do `PLATFORM_VIEW_AUDIT`).

Implementacja: zapytanie do `AuditReaderPort.list_all()` bez filtrowania po encji (w odróżnieniu od `/security/groups/{id}/audit`, które czyta historię konkretnej grupy).

## 6. Nieoczywiste decyzje projektowe

**`burn_password_verification` — obrona przed user-enumeration przez timing attack.** Bcrypt/pbkdf2 są celowo wolne. Gdyby `AuthService.login` przy nieistniejącym userze zwracał błąd natychmiast (bez próby weryfikacji hasła), czas odpowiedzi zdradzałby, czy dany login/email istnieje w systemie. Rozwiązanie:

```python
_DUMMY_HASH = hash_password(secrets.token_urlsafe(32))  # policzony raz

def burn_password_verification(plain: str) -> None:
    verify_password(plain, _DUMMY_HASH)
```

`AuthService.login` woła to zamiast pomijać weryfikację, gdy user nie istnieje — koszt CPU statystycznie równy.

**Rate limiting na `/auth/token`** — obrona przed brute-force haseł. `slowapi`, limiter per-IP (5 prób/minutę). Liczniki w-pamięciowe (nie wspóldzielone między procesami). Jeśli backend stanie za reverse proxy bez konfiguracji zaufanych hostów, limit będzie liczony globalnie zamiast per IP.

**Dwa wspierane formaty hasha** — `verify_password` rozpoznaje zarówno `bcrypt` jak i legacy `pbkdf2_sha256`. Nowe hasła zawsze `bcrypt`.

