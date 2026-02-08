# API (Flask Backend)

REST API dla DebtTracker.

## Uruchomienie

Z repo root:

```bash
.\scripts\run-dev.ps1     # Windows
./scripts/run-dev.sh      # Linux/macOS
```

Lub ręcznie:

```bash
cd api
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

API dostępne: `http://localhost:5000`

## API Endpoints

- **POST `/auth/register`** — rejestracja
  - Payload: `{"email": "...", "password": "..."}`
  - Min. 8 znaków hasła

- **POST `/auth/login`** — logowanie
  - Payload: `{"email": "...", "password": "..."}`
  - Zwraca: `{"ok": true, "token": "..."}`

- **GET `/auth/me`** — profil
  - Header: `Authorization: Bearer <token>`

## Testy

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Zmienne env

Skopiuj `api/.env.example` do `api/.env` (opcjonalne dla dev):

```bash
cp .env.example .env
```

**ARGON2_TIME_COST**, **ARGON2_MEMORY_COST**, **ARGON2_PARALLELISM** — hasło

**PASSWORD_PEPPER** — opcjonalnie (tajny pepper)

## Struktura

```
api/
├── app.py              # Flask entry
├── models.py           # User model
├── auth/
│   └── argon2_hash.py  # Hasher
├── routes/
│   └── auth.py         # Endpoints
└── tests/
    ├── test_auth.py
    └── test_hash.py
```

