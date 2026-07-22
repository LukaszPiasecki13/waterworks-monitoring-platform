# Backend

FastAPI backend z SQLAlchemy ORM i Alembic do migracji.

## 📋 Wymagania

- **Python:** 3.12+
- **Database:** PostgreSQL 14+
- **Inne:** pip, Alembic

## 🚀 Setup Lokalny

### 1. Środowisko wirtualne

```powershell
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Unix/Linux)
source venv/bin/activate
```

### 2. Instalacja zależności

```bash
cd backend
pip install -r requirements.txt
```

### 3. Konfiguracja bazy danych

Utwórz plik `.env` w folderze głównym projektu (lub `backend/`):

```env
# Database
DATABASE_URL=postgresql://postgres:haslo@localhost:5432/xxx

# Security
SECRET_KEY=your-super-secret-key-here-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Attachments
ATTACHMENT_STORAGE_PATH=storage/attachments
```

### 4. Migracje (Alembic)

```bash
cd backend

# Sprawdź status migracji
alembic current

# Wykonaj migracje
alembic upgrade head

# Wgraj wymagane dane startowe (po każdej migracji/deploymentcie)
python -m scripts.seed_required_data

# Utwórz nową migrację (jeśli edytujesz modele)
alembic revision --autogenerate -m "Opis zmian"

# Cofnij ostatnią migrację
alembic downgrade -1
```

### 5. Uruchomienie serwera

```bash
cd backend

# Development (ze reload)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Aplikacja będzie dostępna pod: **http://127.0.0.1:8000**  
Dokumentacja OpenAPI (Swagger): **http://127.0.0.1:8000/docs**  
ReDoc: **http://127.0.0.1:8000/redoc**


## 🏗️ Architektura Modułów

Każdy moduł biznesowy (`security`, `core_data`,..) trzyma własne endpointy,
schematy, serwisy, repozytoria, modele i testy:

```
module/
├── __init__.py           # Exports
├── api/
│   ├── __init__.py       # Exports router
│   └── {resource}.py     # FastAPI endpoints
├── schemas/
│   ├── __init__.py       # Exports schemas
│   └── {resource}.py     # Pydantic models
├── services/
│   ├── __init__.py       # Exports services
│   └── {resource}.py     # Business logic, transaction mgmt
├── repositories/
│   ├── __init__.py       # Exports repos
│   └── {resource}.py     # Data access (no transactions)
├── models/
│   ├── __init__.py       # Exports models
│   └── {resource}.py     # SQLAlchemy ORM models
├── dependencies.py       # Dependency injection
└── tests/
    ├── conftest.py       # Fixtures
    ├── test_api.py
    └── test_service.py
```

## 🔧 Główne Zależności

| Pakiet | Wersja | Opis |
|--------|--------|------|
| fastapi | 0.115+ | Web framework |
| sqlalchemy | 2.0+ | ORM |
| alembic | 1.13+ | Database migrations |
| psycopg2-binary | 2.9+ | PostgreSQL adapter |
| pydantic | 2.0+ | Data validation |
| python-jose | 3.3+ | JWT tokens |
| passlib | 1.7+ | Password hashing |
| bcrypt | 4.0+ | Bcrypt password hashing |
