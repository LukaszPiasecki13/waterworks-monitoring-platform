# Backend jest w pełni synchroniczny

Cały backend — endpointy, serwisy, repozytoria i sesja SQLAlchemy — jest synchroniczny (`def`, `Session`, nie `async def`/`AsyncSession`). FastAPI wykonuje synchroniczne handlery w puli wątków, więc blokujące zapytania do bazy nie wstrzymują pętli zdarzeń.

## Status
Proposed

## Kontekst
Dokumentacja architektury pokazuje w przykładach `async def` i `AsyncSession` ([`01_backend-architecture.md` §5.2](../backend/01_backend-architecture.md)), ale w kodzie nie ma ani jednej asynchronicznej ścieżki dostępu do danych: `AsyncSession` nie występuje nigdzie, a wszystkie serwisy i repozytoria są synchroniczne. Przy skali „kilka gatewayów wysyłających pakiet co ~60 s" wąskim gardłem nie jest współbieżność I/O, tylko prostota utrzymania.

## Decyzja
Nowy kod backendu pisze się synchronicznie. `async def` jest dopuszczalne wyłącznie tam, gdzie wymaga tego framework (`lifespan`, handlery wyjątków FastAPI) — nigdy dla endpointu, który wywołuje synchroniczny serwis.

## Rozpatrywane alternatywy
- **Pełny stos async (`AsyncSession`, `asyncpg`)**: wyższa przepustowość na połączenie, ale wymusza asynchroniczne repozytoria, inne testy i ostrożność przy każdej bibliotece blokującej. Odrzucone — brak realnego obciążenia, które by to uzasadniało.
- **Mieszanie async i sync**: najgorsze z obu światów — `async def` wołające blokujący kod blokuje pętlę zdarzeń i to właśnie dzieje się dziś w `device_identity/api/` (patrz „Znane odstępstwo").

## Znane odstępstwo
Wszystkie 10 endpointów w [`device_identity/api/`](../../../backend/app/modules/device_identity/api/) jest zadeklarowanych jako `async def`, choć wołają synchroniczne serwisy i synchroniczną sesję — każde takie żądanie blokuje pętlę zdarzeń na czas zapytania do bazy. To odstępstwo bez uzasadnienia, opisane jako dług w [`07_analiza_paradygmatow.md`](../backend/07_analiza_paradygmatow.md).

## Konsekwencje
- Endpointy wykonują się w puli wątków FastAPI — domyślnie 40 wątków; przy większym ruchu to jest limit, nie liczba połączeń.
- Testy nie potrzebują `pytest-asyncio` dla ścieżek biznesowych.
- `01_backend-architecture.md` §5.2 i `ai-tools/.claude/rules/python-coding-standards.md` (sekcja FastAPI) pokazują `async def` — do skorygowania, patrz raport.
