# Autoryzacja rozstrzyga się w zależnościach FastAPI i zwraca kontekst dostępu

Uprawnienia sprawdza fabryka zależności (`require_org_access(CAN_...)`, `require_platform_permission(PLATFORM_...)`), która zwraca `OrganizationAccess` albo `PlatformContext`. Serwis dostaje gotowy kontekst i nie sprawdza uprawnień ponownie.

## Status
Proposed

## Kontekst
Kontrola dostępu rozsiana po serwisach jest nieaudytowalna — nie da się jednym spojrzeniem na endpoint powiedzieć, czego wymaga. Fabryki w [`security/dependencies.py:166-224`](../../../backend/app/modules/security/dependencies.py#L166-L224) łączą sprawdzenie członkostwa i uprawnienia w jednym przebiegu i przekazują wynik dalej jako zamrożoną dataclass ([`security/access.py`](../../../backend/app/modules/security/access.py)). Serwisy mówią to wprost w docstringach klas: *„Callers are expected to have already validated organization membership and permissions"*.

## Decyzja
1. Każdy endpoint org-scoped deklaruje `Depends(require_org_access(KOD))`; endpoint platformowy `Depends(require_platform_permission(KOD))`.
2. Wynik (`OrganizationAccess` / `PlatformContext`) jest przekazywany do serwisu jako argument — jest jednocześnie źródłem aktora dla audytu (ADR-0003).
3. **Brak członkostwa w organizacji zwraca 404, brak uprawnienia zwraca 403.** Rozróżnienie jest celowe: 404 nie pozwala obcemu użytkownikowi ustalić, że dana organizacja czy zasób w ogóle istnieje. Ta sama zasada obowiązuje przy dostępie do zasobu spoza własnej organizacji ([`groups.py:126-136`](../../../backend/app/modules/security/services/groups.py#L126-L136)).
4. Uprawnienia żyją w dwóch rozłącznych płaszczyznach: `PLATFORM_*` tylko w grupach platformowych (`organization_id IS NULL`), `CAN_*` tylko w grupach organizacji — walidowane przy zapisie grupy ([`permissions.py:47-78`](../../../backend/app/modules/security/services/permissions.py#L47-L78)).

## Konsekwencje
- Endpoint bez `require_*` jest publiczny dla każdego zalogowanego użytkownika — brak zależności to brak kontroli, więc jej obecność jest pozycją obowiązkową w code review.
- `require_org_or_platform_permission` jest świadomym wyjątkiem: pozwala super adminowi operować na zasobach gminy, której nie jest członkiem, i zwraca wtedy kontekst z pustym zbiorem uprawnień organizacyjnych.
- Testy autoryzacji da się pisać na poziomie endpointu; serwis testuje się bez znajomości uprawnień.
