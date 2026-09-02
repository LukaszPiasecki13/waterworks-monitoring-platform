# Kontrakt błędu API: `detail` plus opcjonalny `code`

Odpowiedź błędu ma kształt natywny dla FastAPI: `{"detail": "..."}`, a tam, gdzie frontend musi rozpoznać konkretny przypadek biznesowy, dochodzi `{"detail": "...", "code": "ACTIVATION_CODE_EXPIRED"}`. Warstwy `api/` i `services/` rzucają wyjątki domenowe z `core/errors.py`; `HTTPException` pojawia się wyłącznie w warstwie zależności uwierzytelniających.

## Status
Proposed

## Kontekst
Hierarchia `APIError` ([`core/errors.py`](../../../backend/app/core/errors.py)) niesie `status_code` i opcjonalny `code`, a globalny handler tłumaczy ją na JSON. W całym backendzie nie ma ani jednego `HTTPException` w `api/` ani w `services/` — wszystkie 14 wystąpień są w [`security/dependencies.py`](../../../backend/app/modules/security/dependencies.py) i [`device_identity/dependencies.py`](../../../backend/app/modules/device_identity/dependencies.py), gdzie odpowiedź 401 musi nieść nagłówek `WWW-Authenticate`. Po drugiej stronie kontraktu frontend czyta dokładnie ten kształt i mapuje `code` na polski komunikat ([`frontend/src/lib/errors.ts:31-41`](../../../frontend/src/lib/errors.ts#L31-L41)).

## Decyzja
- Kod statusu i treść wynikają z klasy wyjątku; serwis nie zna HTTP.
- `detail` jest komunikatem opisowym, nie identyfikatorem — może się zmienić bez zmiany kontraktu.
- `code` jest stabilnym identyfikatorem przypadku i pojawia się tylko tam, gdzie interfejs ma pokazać własny, przetłumaczony komunikat albo zareagować inaczej niż na generyczny błąd.
- Walidacja Pydantica zwraca natywny kształt FastAPI (`detail` jako lista błędów pól) — frontend rozpoznaje go po statusie 422.

## Rozpatrywane alternatywy
- **Koperta `{"error": {"code", "message"}}`** (wymagana przez `ai-tools/.claude/rules/error-handling-patterns.md`): spójniejsza teoretycznie, ale rozjeżdża się z natywnymi odpowiedziami FastAPI dla 422 i wymusza przepisanie parsera po stronie frontendu. Odrzucone — reguła jest tu nieaktualna względem kodu, propozycja korekty w [`07_analiza_paradygmatow.md`](../backend/07_analiza_paradygmatow.md).

## Konsekwencje
- Błąd bez `code` jest dla interfejsu nierozpoznawalny — pokaże surowy `detail`. Dziś `code` ma tylko 12 miejsc, a komunikaty `detail` są pisane raz po angielsku, raz po polsku; to dług, nie własność kontraktu.
- Kod odpowiedzi 500 nigdy nie niesie szczegółów — handler loguje traceback i zwraca stałe „Internal server error".
