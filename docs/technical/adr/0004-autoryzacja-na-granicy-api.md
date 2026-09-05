# Autoryzacja żyje wyłącznie na granicy API; serwis dostaje udowodniony kontekst dostępu

Żaden serwis biznesowy nie sprawdza uprawnień. Zależność FastAPI (`require_org_access(...)`, `require_platform_permission(...)`) weryfikuje członkostwo i uprawnienia **raz**, i przekazuje serwisowi niemutowalny `OrganizationAccess` albo `PlatformContext`. Serwis temu obiektowi ufa: jego istnienie *jest* dowodem autoryzacji.

## Status

Proposed

## Kontekst

Wcześniejszy wariant — sprawdzanie członkostwa wewnątrz każdej metody serwisu — powielał tę samą logikę „404 czy 403?" w każdym CRUD-zie i był łatwy do pominięcia w nowej metodzie. Docstring `OrganizationAccess` mówi o tym wprost: „Replaces duplicated 404-vs-403 logic across service methods".

## Decyzja

- `require_org_access(*codes)` łączy dwa sprawdzenia w jednym przejściu: brak członkostwa → **404** (nie 403 — nie zdradzamy, że cudza gmina istnieje), brak uprawnienia → **403**.
- Zwrócony `OrganizationAccess` (`frozen=True`) niesie aktora, `organization_id` i zbiór uprawnień; serwis używa go do scope'owania zapytań i do wypełnienia aktora w audycie.
- `PlatformContext` robi to samo dla płaszczyzny platformowej.
- Kontrakt jest zapisany w docstringu każdej klasy serwisu, która go przyjmuje: „Callers are expected to have already validated organization membership and permissions".

## Konsekwencje

- Serwis wywołany z pominięciem zależności (np. z CLI albo z innego serwisu) **nie ma żadnej ochrony**. Każde nowe wejście do systemu musi samo zbudować kontekst — to jest cena tej decyzji i najważniejsza rzecz do zapamiętania.
- Test jednostkowy serwisu nie musi stawiać uwierzytelnienia — wystarczy zbudować `OrganizationAccess`.
- Wariant `require_org_or_platform_permission` obsługuje admina platformy działającego na zasobach gminy, której nie jest członkiem: zwraca `OrganizationAccess` z **pustym** zbiorem uprawnień. Serwis, który zacząłby czytać `org_access.permissions`, zachowa się wtedy inaczej niż dla członka — dziś żaden tego nie robi.
