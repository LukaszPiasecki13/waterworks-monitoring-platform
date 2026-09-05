# Serwisy CRUD zwracają encje ORM; DTO buduje FastAPI przez `response_model`

`DeviceService.get_by_id()` zwraca `Device`, `MeasurementPointService.create()` zwraca `MeasurementPoint`, `AuthService.update_profile()` zwraca `User` — czyli obiekty SQLAlchemy, nie schematy Pydantica. Konwersja dzieje się dopiero w warstwie HTTP, przez `response_model=` na dekoratorze i `ConfigDict(from_attributes=True)` na schemacie odpowiedzi.

## Status

Proposed

## Kontekst

`01_backend-architecture.md §5.2` pokazuje w przykładzie serwis kończący się `return ResourceResponse.model_validate(entity)`. Kod robi inaczej — konsekwentnie, we wszystkich modułach CRUD-owych. Ten ADR zapisuje stan faktyczny i jego uzasadnienie; przykład w dokumentacji architektury wymaga korekty.

## Decyzja

- Serwis operujący na encji zwraca encję. Za serializację odpowiada FastAPI.
- Warunkiem, który to umożliwia, jest `expire_on_commit=False` w `sessionmaker` — bez tego encja po commicie miałaby wygaszone atrybuty i serializacja wywołałaby `SELECT` na zamkniętej sesji.
- **Wyjątek: serwisy odczytowe.** `TelemetryQueryService` buduje i zwraca DTO (`ObjectSummaryResponse`, `MeasurementsResponse`), bo agreguje dane z pola JSONB i z kilku tabel — nie ma encji, którą mógłby zwrócić.

Kryterium: **CRUD nad encją → ORM; model odczytowy albo agregat → DTO.**

## Konsekwencje

- Mniej boilerplate'u: nie ma warstwy mapowania encja→DTO w każdym serwisie.
- Kontraktem odpowiedzi jest `response_model=`, a nie adnotacja zwrotu w Pythonie. Dlatego brak adnotacji `->` na handlerze API nie jest usterką — ale brak `response_model` już tak, bo wtedy FastAPI zserializuje **całą** encję, łącznie z polami, których nie chcemy pokazywać (np. `User.hashed_password`).
- Serwis pośrednio zależy od konfiguracji sesji. Zmiana `expire_on_commit` na `True` zepsułaby serializację w każdym endpointcie zapisującym — bez żadnego błędu w samych serwisach.
- Cena: encja ORM przecieka o warstwę wyżej, niż mówi model warstwowy. Świadomie akceptowana przy tej skali.
