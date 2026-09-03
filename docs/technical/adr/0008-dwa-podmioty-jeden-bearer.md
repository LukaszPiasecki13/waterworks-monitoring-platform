# Użytkownik i urządzenie to dwa podmioty na jednym schemacie bearer, rozróżniane claimem `type`

Backend uwierzytelnia dwa różne rodzaje podmiotów tym samym nagłówkiem `Authorization: Bearer`. Rozróżnia je claim `type` w tokenie: `access` (użytkownik), `refresh` (odnowienie sesji), `device` (gateway). Każda zależność sprawdza oczekiwany typ i odrzuca pozostałe.

## Status
Proposed

## Kontekst
`TokenService` emituje trzy rodzaje tokenów ([`token.py:26-56`](../../../backend/app/modules/security/services/token.py#L26-L56)), a dwie równoległe zależności je konsumują: `get_current_user` wymaga `type == "access"` ([`security/dependencies.py:101`](../../../backend/app/modules/security/dependencies.py#L101)), `get_current_device` wymaga `type == "device"` ([`device_identity/dependencies.py:116`](../../../backend/app/modules/device_identity/dependencies.py#L116)), a `AuthService.refresh` wymaga `type == "refresh"`. Bez tego sprawdzenia token urządzenia — ważny 36 godzin i przechowywany w pamięci gatewaya w terenie — otwierałby endpointy organizacji.

## Decyzja
- Typ podmiotu jest częścią tokenu i **jest weryfikowany zawsze**, niezależnie od poprawności podpisu i daty ważności.
- Urządzenie jest pełnoprawnym aktorem audytu: zdarzenia jego cyklu życia (redeem kodu aktywacyjnego, pierwszy claim) zapisują się z `actor_id` równym identyfikatorowi credentiala i `actor_display_name` w formacie `device:<serial>` ([`activation_codes.py:295-296`](../../../backend/app/modules/device_identity/services/activation_codes.py#L295-L296), [`device_auth.py:154-155`](../../../backend/app/modules/device_identity/services/device_auth.py#L154-L155)). Nie audytuje się natomiast strumienia pomiarowego — patrz [ADR-0002](0002-commit-bez-audytu-jest-bledem.md).
- Urządzenie nie należy do żadnej organizacji na poziomie tożsamości; przypisanie do obiektu wodociągowego to osobny krok po uwierzytelnieniu.

## Rozpatrywane alternatywy
- **Osobny nagłówek lub schemat dla urządzeń**: czytelniejsze rozdzielenie, ale duplikuje obsługę tokenu i nie chroni lepiej — sprawdzenie claimu `type` daje ten sam efekt przy jednym mechanizmie.
- **mTLS zamiast tokenu**: mocniejsze, ale wymaga PKI i obsługi certyfikatów na urządzeniu w terenie; przy kilku prototypach nieproporcjonalne.

## Konsekwencje
- Dodanie czwartego typu tokenu wymaga świadomego przejrzenia wszystkich zależności — brak sprawdzenia `type` w nowej zależności to natychmiastowa eskalacja uprawnień.
- Tokeny są podpisywane symetrycznie (HS256, wspólny `secret_key`), więc kompromitacja sekretu pozwala podrobić dowolny podmiot. To znane odstępstwo od `security-checklist` (RS256), opisane w raporcie.
