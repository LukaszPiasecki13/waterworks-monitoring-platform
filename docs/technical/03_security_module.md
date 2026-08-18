# Moduł `security`

> Część serii dokumentacji per-moduł. Ogólna architektura backendu: [`01_backend-architecture.md`](./01_backend-architecture.md).

## 1. Cel modułu

`security` odpowiada za trzy rzeczy: **authentication** (login, wydawanie i odświeżanie tokenów JWT), **authorization** (grupy uprawnień, sprawdzanie dostępu) i **hashowanie haseł**. Inne moduły korzystają z niego wyłącznie przez jego serwisy — nigdy przez `security/repositories/`.

## 2. Model domenowy

`UserGroup` (grupa uprawnień) ↔ `Permission` (many-to-many) ↔ `User` (many-to-many, przez `security_user_group` po stronie `core_data.User`). Dwie grupy systemowe (`is_system=True`): **Admin** i **Staff** — nie da się ich usunąć ani zmienić nazwy/opisu; uprawnienia grupy Staff są edytowalne przez admina, uprawnienia grupy Admin — nie (żeby admin nie mógł odciąć sobie dostępu).


## 3. Kluczowe reguły i niezmienniki

- **Ostatni admin jest chroniony**: `_protect_last_admin` i logika w `replace_user_groups` odrzucają operację, która usunęłaby ostatniego użytkownika z grupy Admin (`BadRequestError`) — system nie może zostać bez administratora.
- **Grupy systemowe częściowo zablokowane**: nazwy/opisu grup systemowych nie da się zmienić; uprawnień — tylko Staff da się edytować, Admin nie (`_ensure_permissions_editable`).
- Każda zmiana grupy/przypisania generuje wpis audytowy przez `AuditPort`, chyba że delta stanu jest pusta (wtedy `tx.skip_audit()`).

## 4. Nieoczywiste decyzje projektowe

**`burn_password_verification` — obrona przed user-enumeration przez timing attack.** Bcrypt/pbkdf2 są celowo wolne. Gdyby `AuthService.login` przy nieistniejącym userze zwracał błąd natychmiast (bez próby weryfikacji hasła), czas odpowiedzi zdradzałby, czy dany login/email istnieje w systemie — mimo identycznego komunikatu błędu. Rozwiązanie w [`password.py:43-50`](../../backend/app/modules/security/services/password.py#L43-L50):

```python
_DUMMY_HASH = hash_password(secrets.token_urlsafe(32))  # policzony raz, przy starcie

def burn_password_verification(plain: str) -> None:
    verify_password(plain, _DUMMY_HASH)
```

`AuthService.login` woła to zamiast pomijać weryfikację, gdy user nie istnieje — koszt CPU jest statystycznie taki sam niezależnie od tego, czy konto istnieje.

**Rate limiting na `/auth/token` — obrona przed brute-force haseł.** `slowapi`, limiter per-IP, liczniki w pamięci procesu. Definicja w [`core/rate_limit.py`](../../backend/app/core/rate_limit.py):

```python
limiter = Limiter(key_func=get_remote_address)
```

Zastosowanie na endpointzie w [`security/api/auth.py:33-34`](../../backend/app/modules/security/api/auth.py#L33-L34):

```python
@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, ...):
```

Szósta próba logowania z tego samego IP w ciągu minuty dostaje `429 {"detail": "Too many requests"}` — zanim `AuthService.login` w ogóle sięgnie do hasła. `register_rate_limiting(app)` w `main.py` podpina exception handler na `RateLimitExceeded`, żeby odpowiedź miała ten sam kształt co reszta API (`detail`, nie domyślny format slowapi).

Dwa ograniczenia do pamiętania:
- **In-memory, jedna instancja.** Liczniki nie są współdzielone między procesami — przy wielu instancjach backendu za load balancerem limit efektywnie się mnoży (`limits`/`slowapi` wspiera magazyn Redis, gdyby to się stało problemem).
- **Klucz to `request.client.host`.** Jeśli backend stanie za reverse proxy (nginx, Render, Cloudflare), wszystkie żądania przychodzą z adresu proxy — limit liczyłby się wtedy dla całego ruchu naraz, nie per użytkownik. W repo nie ma obecnie żadnej konfiguracji `--proxy-headers`/zaufanych proxy — do zweryfikowania przed deploymentem za dowolnym reverse proxy.

Limit liczy próby per-IP, nie per-konto — nie chroni przed rozproszonym brute-force z wielu adresów, tylko przed najprostszym atakiem z jednego miejsca. Test: `test_login_rate_limited_after_repeated_attempts` (`test_auth_api.py`); fixture `reset_rate_limiter` (autouse, `conftest.py`) czyści liczniki między testami, bo `TestClient` wysyła wszystkie żądania z jednego syntetycznego adresu.

**Dwa wspierane formaty hasha** — `verify_password` rozpoznaje po prefiksie zarówno `bcrypt`, jak i `pbkdf2_sha256$<iterations>$<salt>$<hash>`. Test jednostkowy nazywa to wprost `test_verify_password_supports_legacy_pbkdf2_hashes` — obsługa istnieje z myślą o hashach ze starszego/innego źródła danych, ale kod ani testy nie dokumentują, skąd konkretnie te dane pochodzą; nowe hasła zawsze powstają przez `hash_password` (czysty bcrypt).

