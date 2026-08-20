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

- **Ostatni admin jest chroniony**: logika w `replace_user_groups` (patrz [`../app/modules/security/services/permissions.py`](../app/modules/security/services/permissions.py)) odrzuca operację, która usunęłaby ostatniego użytkownika z platformowej grupy Super Admin (`BadRequestError`) — system nie może zostać bez superadmina. Administrator gminy nie jest chroniony (gmina może być bez administratora; super admin może ją naprawić).
- **Grupy systemowe częściowo zablokowane**: nazwy/opisu grup systemowych nie da się zmienić (`_ensure_system_group_fields_immutable`); uprawnień grupy Super Admin (`system_key="admin"`, `organization_id IS NULL`) nie da się edytować (`_ensure_permissions_editable`). Uprawnienia gminnych grup systemowych (`organization_id <> NULL`) są edytowalne.
- Każda zmiana grupy/przypisania generuje wpis audytowy przez `AuditPort`, chyba że delta stanu jest pusta (wtedy `tx.skip_audit()`).
- **Katalog uprawnień** (`app/modules/security/permission_catalog.py`) — zamknięta lista kodów z polem `plane` (`'organization'` lub `'platform'`). Grupy organizacyjne mogą zawierać wyłącznie kody `CAN_*`; grupy platformowe wyłącznie `PLATFORM_*` (egzekwowana w `_resolve_permissions`).


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

