# Moduł wspierający nie ma własnej warstwy `api/` — udostępnia się przez port w `core/`

`audit` jest jedynym modułem bez katalogu `api/`. Nie wystawia routera; inne moduły zależą od protokołów `AuditPort` / `AuditReaderPort` z `core/audit.py`, a ten moduł dostarcza ich implementację SQL.

## Status
Proposed

## Kontekst
Cztery z pięciu modułów mają `api/` i własne endpointy. `audit` nie ma, bo nie ma własnego zasobu w rozumieniu API — historia zmian jest zawsze historią *czegoś* i naturalnie należy do endpointu tej encji (`GET /users/{id}/audit` w `core_data`) albo do płaszczyzny platformy ([`security/api/platform_audit.py`](../../../backend/app/modules/security/api/platform_audit.py)). Oba miejsca konsumują `AuditReaderPort`, nie moduł bezpośrednio.

## Decyzja
Moduł zostaje bez warstwy `api/`, gdy spełnia oba warunki:
1. nie ma zasobu, dla którego dałoby się sensownie napisać własną ścieżkę URL — jego dane są zawsze podrzędne wobec encji innego modułu;
2. jego kontrakt da się wyrazić jako protokół w `core/`, a moduły biznesowe mogą od niego zależeć bez importowania modułu (odwrócenie zależności).

Skutek uboczny jest celowy: `core_data` i `security` nie wiedzą, że `audit` istnieje — widzą tylko `AuditPort`. Podmiana implementacji (np. wysyłka do zewnętrznego systemu logowania) nie zmienia ani jednej linii w serwisach biznesowych.

## Konsekwencje
- Uprawnienia do czytania audytu definiuje moduł, który wystawia endpoint — `audit` nie zna pojęcia uprawnień ani organizacji.
- Jedyne odstępstwo od zasady „warstwy niższe nie znają modułów" leży po stronie infrastruktury: [`infrastructure/sql/factory.py:7`](../../../backend/app/infrastructure/sql/factory.py#L7) importuje `MissingAuditRecordError` z modułu `audit`. Ten wyjątek powinien mieszkać w `core/errors.py` — pozycja na liście długu.
