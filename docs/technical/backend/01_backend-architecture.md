# Architektura Backendu — Dokumentacja Techniczna

---

## Spis treści

- [Architektura Backendu — Dokumentacja Techniczna](#architektura-backendu--dokumentacja-techniczna)
  - [Spis treści](#spis-treści)
- [1. Przegląd architektury](#1-przegląd-architektury)
- [2. Zasady architektury](#2-zasady-architektury)
  - [2.1. Dozwolone zależności między warstwami](#21-dozwolone-zależności-między-warstwami)
  - [2.2. Zakaz przeskakiwania warstw](#22-zakaz-przeskakiwania-warstw)
  - [2.3. Komunikacja między modułami](#23-komunikacja-między-modułami)
  - [2.4. Zakaz zależności cyklicznych](#24-zakaz-zależności-cyklicznych)
- [3. Struktura projektu](#3-struktura-projektu)
- [4. Warstwy współdzielone](#4-warstwy-współdzielone)
  - [4.1. `core/`](#41-core)
  - [4.2. `infrastructure/`](#42-infrastructure)
    - [`infrastructure/sql/`](#infrastructuresql)
- [5. Template modułu domenowego](#5-template-modułu-domenowego)
  - [5.1. Struktura katalogów](#51-struktura-katalogów)
  - [5.2. Odpowiedzialność każdej warstwy](#52-odpowiedzialność-każdej-warstwy)
    - [`api/<resource>.py`](#apiresourcepy)
    - [`services/<resource>.py`](#servicesresourcepy)
    - [`repositories/<resource>.py`](#repositoriesresourcepy)
      - [Konwencja `get_` vs `find_`](#konwencja-get_-vs-find_)
    - [`schemas/<resource>.py`](#schemasresourcepy)
    - [`models/<resource>.py`](#modelsresourcepy)
    - [`exceptions.py`](#exceptionspy)
  - [5.3. Wiring zależności — `dependencies.py`](#53-wiring-zależności--dependenciespy)
- [6. Moduły biznesowe](#6-moduły-biznesowe)
  - [6.1. `core_data/`](#61-core_data)
  - [6.2. `security/`](#62-security)
  - [6.3. `telemetry/`](#63-telemetry)
  - [6.4. `audit/`](#64-audit)
- [7. Płaszczyzny dostępu i routing API](#7-płaszczyzny-dostępu-i-routing-api)
- [8. Obsługa błędów](#8-obsługa-błędów)
  - [7.1. Przepływ wyjątków](#71-przepływ-wyjątków)
  - [7.2. Hierarchia wyjątków (`core/errors.py`)](#72-hierarchia-wyjątków-coreerrorspy)
  - [7.3. Globalny handler wyjątków (`main.py`)](#73-globalny-handler-wyjątków-mainpy)
- [9. Strategia testowania](#9-strategia-testowania)
  - [9.1. Poziomy testów](#91-poziomy-testów)
  - [9.2. Testy jednostkowe serwisów](#92-testy-jednostkowe-serwisów)
  - [9.3. Testy integracyjne endpointów](#93-testy-integracyjne-endpointów)

---

# 1. Przegląd architektury

Architektura systemu to **architektura warstwowa (Layered Architecture)** zorganizowana jako **modularny monolit (Modular Monolith)**.

Kod podzielony jest na cztery poziome warstwy: **API → Services → Repositories → Infrastructure**. Każda warstwa ma jedno jasno określone zadanie i zależy wyłącznie od warstwy bezpośrednio poniżej. Warstwy `core/` i `errors` są przekrojowe — mogą być importowane na każdym poziomie.

:::mermaid
flowchart TB
    API["API"]
    SERVICES["Services"]
    REPOSITORIES["Repositories"]
    INFRASTRUCTURE["Infrastructure"]

    CORE["Core"]
    ERRORS["Errors"]

    API --> SERVICES
    SERVICES --> REPOSITORIES
    REPOSITORIES --> INFRASTRUCTURE

    API -.-> CORE
    SERVICES -.-> CORE
    REPOSITORIES -.-> CORE
    INFRASTRUCTURE -.-> CORE

    API -.-> ERRORS
    SERVICES -.-> ERRORS
    REPOSITORIES -.-> ERRORS
    INFRASTRUCTURE -.-> ERRORS
:::

**Dlaczego architektura warstwowa, a nie Clean Architecture?**
Skupia się na praktycznym, poziomym podziale odpowiedzialności — bardziej czytelnym i dopasowanym do typowego workflow zespołu.

**Korzyści:**

| Korzyść | Opis |
|---|---|
| Podział odpowiedzialności | Każda warstwa ma jedno główne zadanie |
| Testowalność | Serwisy testowane jednostkowo z mockami repozytoriów |
| Łatwość utrzymania | Zmiany w jednym module mają minimalny wpływ na inne |
| Onboarding | Nowi developerzy szybko rozumieją strukturę |
| Skalowalność | Moduły mogą zostać wydzielone do mikroserwisów |
| Spójność | Wszystkie moduły mają identyczną strukturę |
| Zarządzanie zależnościami | Jasne zasady zapobiegają splątanym zależnościom |

---

# 2. Zasady architektury

## 2.1. Dozwolone zależności między warstwami

| Warstwa | Może importować z |
|---|---|
| **API** | Services (własny moduł), Core, Errors |
| **Services** | Repositories (własny moduł), inne Services, Core, Errors |
| **Repositories** | Infrastructure, Core, Errors |
| **Infrastructure** | Core, Errors |

## 2.2. Zakaz przeskakiwania warstw

Każda operacja musi przechodzić przez pełny łańcuch: `API → Services → Repositories → Infrastructure`.

```
✅  API → Services → Repositories → Infrastructure
❌  API → Repositories              (pominięcie Services)
❌  API → Infrastructure
❌  Services → Infrastructure       (pominięcie Repositories)
```

## 2.3. Komunikacja między modułami

Cross-module odbywa się **wyłącznie przez warstwę serwisów**:

```python
from app.modules.notifications.services.email import EmailService    # ✅
from app.modules.notifications.repositories.email import EmailRepository  # ❌
```

## 2.4. Zakaz zależności cyklicznych

Jeśli dwa serwisy wzajemnie się potrzebują:
- Wydziel wspólną logikę do `core/` lub osobnego modułu
- Zastąp bezpośrednie wywołanie zdarzeniem (event/message)
- Zrewiduj podział — być może moduły powinny być scalone

---

# 3. Struktura projektu

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ dependencies.py
│  │  ├─ base.py
│  │  └─ errors.py
│  ├─ infrastructure/
│  │  ├─ sql/
│  │  │  ├─ base.py
│  │  │  ├─ factory.py
│  │  │  └─ models_registry.py
│  │  ├─ nosql/
│  │  │  └─ factory.py
│  │  └─ storage/
│  │     └─ client.py
│  └─ modules/
│     ├─ <domain_module>/          ← template opisany w sekcji 5
│     │  ├─ api/
│     │  ├─ services/
│     │  ├─ repositories/
│     │  ├─ schemas/
│     │  ├─ models/
│     │  ├─ dependencies.py
│     │  ├─ exceptions.py
│     │  └─ tests/
│     ├─ core_data/               ← sekcja 6.1
│     └─ security/                 ← sekcja 6.2
│
├─ alembic/
│  ├─ versions/
│  ├─ env.py
│  └─ script.py.mako
│
├─ alembic.ini
├─ pyproject.toml
├─ .env
├─ .env.example
└─ README.md
```

---

# 4. Warstwy współdzielone

## 4.1. `core/`

Zawiera elementy współdzielone przez wszystkie moduły. **Nie zawiera logiki biznesowej.**

| Plik | Odpowiedzialność |
|---|---|
| `config.py` | Ustawienia aplikacji z zmiennych środowiskowych (`Pydantic BaseSettings`): połączenia z bazą danych, klucze JWT, nazwy bucketów, flagi feature |
| `dependencies.py` | Globalne zależności FastAPI (`Depends()`): `get_db_session`, `get_current_user`, `get_nosql_client` |
| `base.py` | Abstrakcyjne klasy bazowe: `BaseRepository`, `BaseService` — spójny interfejs dla wszystkich modułów |
| `errors.py` | Hierarchia wyjątków aplikacji: `BaseAppException` i klasy pochodne (szczegóły w sekcji 7) |
| `rate_limit.py` | `slowapi` limiter per-IP, in-memory — chroni `/auth/token` przed brute-force (szczegóły w [`03_security_module.md`](./03_security_module.md#6-nieoczywiste-decyzje-projektowe)) |

## 4.2. `infrastructure/`

Dostarcza narzędzia techniczne do komunikacji z zewnętrznymi systemami. **Nie zawiera logiki biznesowej ani domenowej.**

### `infrastructure/sql/`

| Plik | Odpowiedzialność |
|---|---|
| `base.py` | `DeclarativeBase` SQLAlchemy — wszystkie modele ORM dziedziczą z tej klasy |
| `factory.py` | `SQLConnectionFactory` — cache silników per URL, tworzy `sessionmaker`/`scoped_session` związany z `AuditAwareSession` (patrz niżej) |
| `repository.py` | `SQLRepository` — bazowa klasa repozytorium, dostarcza `transaction()` (patrz niżej) |
| `models_registry.py` | Importuje wszystkie modele ORM dla Alembic `autogenerate` — **każdy nowy model musi być tu zarejestrowany** |

**`SQLRepository.transaction()`** — współdzielony context manager zastępujący powtarzany w każdym serwisie blok `try: ... commit() except Exception: rollback(); raise`:

```python
@contextmanager
def transaction(self, *, skip_audit: bool = False) -> Iterator[Transaction]:
    tx = Transaction()
    if skip_audit:
        tx.skip_audit()
    try:
        yield tx
    except Exception:
        self.rollback()
        raise
    self.commit(skip_audit=tx.audit_skipped)
```

Użycie w serwisie: `with self.repo.transaction() as tx: ...` — commit następuje automatycznie po bezusterkowym wyjściu z bloku, rollback + re-raise przy dowolnym wyjątku. `tx.skip_audit()` pozwala zacommitować operację, która świadomie nie generuje zdarzenia audytowego (np. update bez realnej zmiany danych), bez ręcznego wołania `commit(skip_audit=True)`.

**`AuditAwareSession`** (podklasa `Session`, ustawiana jako `class_` w `sessionmaker`) — blokuje `commit()`, jeśli w ramach sesji nie zarejestrowano zdarzenia audytowego i nie przekazano jawnie `skip_audit=True`. Niezmiennik "żadna zmiana biznesowa nie commituje się bez śladu w audit logu" jest w ten sposób wymuszony na poziomie sesji SQLAlchemy, nie tylko konwencją w kodzie serwisu.

---

# 5. Template modułu domenowego

## 5.1. Struktura katalogów

Każdy moduł domenowy stosuje identyczną strukturę:

```text
modules/<domain>/
├─ api/
│  └─ <resource>.py        # Endpointy HTTP
├─ services/
│  └─ <resource>.py        # Logika biznesowa
├─ repositories/
│  └─ <resource>.py        # Dostęp do danych
├─ schemas/
│  └─ <resource>.py        # Schematy Pydantic (request/response)
├─ models/
│  └─ <resource>.py        # Modele ORM SQLAlchemy
├─ dependencies.py         # Fabryki DI dla FastAPI
├─ exceptions.py           # Wyjątki domenowe modułu
└─ tests/
```

## 5.2. Odpowiedzialność każdej warstwy

### `api/<resource>.py`

- Definiuje endpointy HTTP (`@router.get`, `@router.post`, itd.)
- Waliduje dane wejściowe przez schematy Pydantic
- Ustawia kody statusu HTTP i formatuje odpowiedź
- **Nie zawiera** logiki biznesowej — deleguje do serwisu
- **Nie importuje** repozytoriów ani modeli ORM

```python
@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    data: ResourceCreateRequest,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponse:
    return await service.create(data)
```

### `services/<resource>.py`

- Implementuje logikę biznesową i przypadki użycia
- Orkestruje wiele wywołań repozytoriów w jednej operacji
- Może korzystać z serwisów innych modułów (bez zależności cyklicznych)
- **Nie importuje** `Request`, `Response` ani typów HTTP
- **Nie wykonuje** bezpośrednich zapytań do bazy danych

```python
class ResourceService:
    def __init__(self, repository: ResourceRepository):
        self._repo = repository

    async def create(self, data: ResourceCreateRequest) -> ResourceResponse:
        if await self._repo.exists(name=data.name):
            raise ResourceAlreadyExistsError(data.name)
        entity = await self._repo.create(data)
        return ResourceResponse.model_validate(entity)
```

### `repositories/<resource>.py`

- Wykonuje operacje odczytu i zapisu danych (SQL/NoSQL)
- Zawiera wyłącznie logikę dostępu do danych — **żadnej logiki biznesowej**
- Zwraca modele domenowe lub ORM, nigdy obiekty sesji/kursorów
- **Nie importuje** nic z warstwy `api/` ani `services/`

#### Konwencja `get_` vs `find_`

Repozytorium powinno udostępniać dwie metody odczytania obiektu:

| Metoda | Zachowanie | Użycie |
|---|---|---|
| `get_by_id(id)` | Zwraca `None` jeśli nie znaleziono | Wewnętrzne sprawdzenia, gdy brak = stan poprawny |
| `find_by_id(id)` | Rzuca `NotFoundError` jeśli nie znaleziono | Publiczne API, gdy brak = błąd |

**Implementacja w repozytorium:**

```python
def get_by_id(self, item_id: UUID) -> Item | None:
    """Low-level read — returns None if not found."""
    return self.session.query(Item).filter(Item.id == item_id).first()

def find_by_id(self, item_id: UUID) -> Item:
    """High-level read — raises NotFoundError if not found."""
    item = self.get_by_id(item_id)
    if not item:
        raise NotFoundError(f"Item {item_id} not found")
    return item
```

**Użycie w serwisach:**

```python
class ItemService:
    def get_by_id(self, item_id: UUID) -> Item:
        """Publiczna metoda — jeśli nie znaleziono, to błąd."""
        # ✅ Używaj find_by_id — wyrzuci NotFoundError automatycznie
        item = self.repo.find_by_id(item_id)
        # Nie trzeba sprawdzać: if not item: raise NotFoundError()
        return item
    
    def update(self, item_id: UUID, data: UpdateRequest) -> Item:
        """Aktualizacja — brak obiektu to błąd."""
        # ✅ find_by_id automatycznie wyrzuci NotFoundError
        item = self.repo.find_by_id(item_id)
        # ... logika aktualizacji ...
        return item
    
    def internal_check(self, item_id: UUID) -> bool:
        """Wewnętrze sprawdzenie — brak = stan normalny."""
        # ✅ Używaj get_by_id — zwraca None bez wyjątków
        item = self.repo.get_by_id(item_id)
        return item is not None
```

**Zasada:** W serwisach **prawie nigdy nie sprawdzamy wyniku `find_by_id`** — jeśli wywoływanie go jest konieczne, oznacza to, że brak obiektu to błąd. `find_by_id` wyrzuca automatycznie, zatem nie duplikujemy logiki sprawdzania w każdej metodzie serwisu.

### `schemas/<resource>.py`

- Definiuje schematy Pydantic do walidacji danych wejściowych i wyjściowych
- Konwencja nazewnictwa: `<Resource>CreateRequest`, `<Resource>UpdateRequest`, `<Resource>Response`
- Wyłącznie walidacja i transformacja danych — **brak logiki biznesowej**

### `models/<resource>.py`

- Definiuje modele ORM SQLAlchemy mapowane na tabele bazy danych
- Dziedziczy z `Base` z `infrastructure/sql/base.py`
- **Wymagane:** zarejestrowanie w `infrastructure/sql/models_registry.py`

### `exceptions.py`

- Wyjątki domenowe specyficzne dla modułu
- Dziedziczą z klas bazowych w `core/errors.py`

## 5.3. Wiring zależności — `dependencies.py`

Plik konfiguruje łańcuch wstrzykiwania zależności FastAPI:

```
API  →  Depends(get_<resource>_service)
         └─ Service  →  Depends(get_<resource>_repository)
                          └─ Repository  →  Depends(get_db_session)  [z core/]
```

**Zasady:**
- `api/` deklaruje `Depends()` **wyłącznie** na funkcjach zwracających Service
- `services/` **nie używają** `Depends()` — przyjmują zależności przez `__init__`
- Sesję DB (`AsyncSession`) wstrzykuje **wyłącznie** Repository

```python
def get_resource_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ResourceRepository:
    return ResourceRepository(session)

def get_resource_service(
    repository: ResourceRepository = Depends(get_resource_repository),
) -> ResourceService:
    return ResourceService(repository)
```

**Zabronione wzorce:**

```python
# ❌ API wstrzykuje Repository bezpośrednio
async def get_items(repo: ItemRepository = Depends(get_item_repository)): ...

# ❌ API wstrzykuje sesję DB bezpośrednio
async def get_items(session: AsyncSession = Depends(get_db_session)): ...

# ✅ API wstrzykuje wyłącznie Service
async def get_items(service: ItemService = Depends(get_item_service)): ...
```

---

# 6. Moduły biznesowe

Każdy moduł ma własny, szczegółowy dokument z modelem danych, endpointami, regułami biznesowymi i uzasadnieniem nieoczywistych decyzji projektowych — tu tylko krótkie streszczenie i granice odpowiedzialności.

## 6.1. `core_data/`

Dane referencyjne współdzielone przez inne moduły domenowe: organizacje, obiekty wodociągowe, urządzenia, punkty pomiarowe, użytkownicy. CRUD backbone, na którym budują pozostałe moduły. Inne moduły korzystają z jego serwisów — nigdy bezpośrednio z repozytoriów.

→ Pełny opis: [`02_core_data_module.md`](./02_core_data_module.md)

## 6.2. `security/`

Autentykacja (login, JWT access/refresh) i autoryzacja (uprawnienia) dla całej aplikacji, plus hashowanie haseł. **Nie** przechowuje danych usera — to `core_data/`. Inne moduły korzystają z niego wyłącznie przez jego warstwę serwisów (`get_current_user`, `require_role(...)` itp.), nigdy przez `security/repositories/`.

→ Pełny opis: [`03_security_module.md`](./03_security_module.md)

## 6.3. `telemetry/`

Przyjmuje pakiety pomiarowe z gatewayów terenowych (`POST /telemetry/ingest`) i wystawia zapytania szeregów czasowych dla dashboardu. Ingest commituje zawsze przez `transaction(skip_audit=True)` — dane z urządzenia IoT, nie zmiana wywołana przez użytkownika, więc nie generuje wpisu w audit logu. Pakiet ląduje w dwóch miejscach naraz: surowy blob JSONB w `telemetry_packets` (audyt i replay) oraz wiersz na pomiar w partycjonowanej tabeli `measurements` (odczyty dashboardu, historia, przyszłe alarmy i eksport).

→ Pełny opis: [`04_telemetry_module.md`](./04_telemetry_module.md)

## 6.4. `audit/`

Niezmienny, append-only log zmian biznesowych. Nie ma własnej warstwy `api/` — inne moduły zależą od abstrakcyjnego `AuditPort` (`core/audit.py`), a ten moduł dostarcza jego implementację SQL.

→ Pełny opis: [`05_audit_module.md`](./05_audit_module.md)

## 6.5. `device_identity/`

Asymetryczna autentykacja urządzeń IoT — każde urządzenie generuje na sobie parę kluczy EC P-256 i dowodzi jej posiadania podpisem (challenge/response), bez współdzielonego sekretu z backendem. Provisioning przez jednorazowe kody aktywacyjne (operator platformy) lub ścieżkę administracyjną (import fabryczny). Moduł operuje na poziomie urządzenia, bez powiązania z organizacjami; org-scoping (przypisanie do obiektu wodociągowego) to osobny krok, wykonywany po zakończeniu auth.

**Nowe:** [`DeviceLifecycleService`](../../backend/app/modules/device_identity/services/device_lifecycle.py) — orchestrator kaskadowego usunięcia urządzenia z platformy: usuwa telemetrię, device record (cascaduje measurement_points), credential. Atomowy w jednej transakcji.

→ Pełny opis: [`06_device_identity_module.md`](./06_device_identity_module.md)

---

# 7. Płaszczyzny dostępu i routing API

System wykorzystuje **dwie niezależne płaszczyzny dostępu**:

| Płaszczyzna | Użytkownik | Dostęp | Routing | Autoryzacja |
|---|---|---|---|---|
| **Organizacji** | Członek gminy | Do danych tej gminy: obiekty, urządzenia, punkty, członkowie | `/api/v1/orgs/{org_id}/...` | `CAN_*` kody, scoped per organizacja |
| **Platformy** | Super admin | Rejestr gmin, globalny rejestr kont, audyt | `/api/v1/platform/...` | `PLATFORM_*` kody, globalne |

Użytkownik może należeć do wielu gmin (pierwszy plan) i/lub być super adminem (drugi plan) — dwie niezależne roli. Super admin bez członkostwa w gminie nie widzi jej danych pomiarowych.

# 8. Obsługa błędów

## 7.1. Przepływ wyjątków

```
Repository  →  rzuca wyjątek domenowy (np. ResourceNotFoundError)
    ↓
Service     →  przepuszcza lub transformuje wyjątek domenowy
    ↓
API         →  tłumaczy wyjątek domenowy na HTTPException
    ↓
Client      ←  odpowiedź HTTP z kodem błędu i komunikatem
```

## 7.2. Hierarchia wyjątków (`core/errors.py`)

```python
class BaseAppException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

class NotFoundError(BaseAppException):
    status_code = 404

class ValidationError(BaseAppException):
    status_code = 422

class PermissionDeniedError(BaseAppException):
    status_code = 403

class ConflictError(BaseAppException):
    status_code = 409
```

Wyjątki domenowe modułów dziedziczą z powyższych klas:

```python
# modules/<domain>/exceptions.py
class ResourceNotFoundError(NotFoundError):
    def __init__(self, resource_id: int):
        self.detail = f"Resource {resource_id} not found"

class ResourceAlreadyExistsError(ConflictError):
    def __init__(self, name: str):
        self.detail = f"Resource '{name}' already exists"
```

## 7.3. Globalny handler wyjątków (`main.py`)

Automatycznie tłumaczy wyjątki domenowe na odpowiedzi HTTP — warstwa API nie musi obsługiwać każdego wyjątku ręcznie:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.errors import BaseAppException

app = FastAPI()

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
```

---

# 9. Strategia testowania

## 9.1. Poziomy testów

| Poziom | Co testujemy | Narzędzia | Izolacja |
|---|---|---|---|
| **Unit** | Logika w serwisach | `pytest`, `pytest-mock` | Mock repozytoriów |
| **Integration** | Endpointy API + baza danych | `pytest`, `TestClient`, baza testowa | Prawdziwa baza (rollback transakcji) |
| **E2E** | Pełny flow HTTP | `httpx`, zewnętrzna baza | Brak izolacji |

## 9.2. Testy jednostkowe serwisów

Serwisy testujemy **bez bazy danych** — repozytoria są mockowane przez `AsyncMock`:

```python
# tests/test_services.py
from unittest.mock import AsyncMock
import pytest
from app.modules.example.services.resource import ResourceService
from app.modules.example.exceptions import ResourceNotFoundError

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def service(mock_repo):
    return ResourceService(repository=mock_repo)

async def test_get_resource_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.get_by_id(resource_id=999)
```

## 9.3. Testy integracyjne endpointów

Używają `TestClient` z FastAPI. Każdy test weryfikuje jeden endpoint z nagłówkami autoryzacji i sprawdza kod statusu oraz kształt odpowiedzi.
