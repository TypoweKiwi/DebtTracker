# DebtTracker 💰

Aplikacja do śledzenia długów między znajomymi. Full-stack: **React** (frontend) + **Flask** (backend) + **Supabase/PostgreSQL** (baza danych).

## 🚀 Szybki start (lokalne dev)

### Wymagania
- Python 3.8+
- Node.js 16+ (z npm)
- (Opcjonalnie) Docker & Docker Compose

### Uruchomienie backendu + frontendu jedną komendą

**Windows PowerShell:**
```powershell
.\scripts\run-dev.ps1
```

**Linux/macOS/WSL:**
```bash
./scripts/run-dev.sh
```

Otwórz przeglądarkę: `http://localhost:3000`

---

## 📁 Struktura projektu

```
DebtTracker/
├── api/                    # Backend (Flask)
│   ├── app.py             # Entry point
│   ├── models.py          # SQLAlchemy models
│   ├── requirements.txt    # Python dependencies
│   ├── README.md          # API documentation
│   ├── auth/              # Authentication utilities
│   ├── routes/            # API endpoints
│   └── tests/             # Unit & integration tests
│
├── web/                    # Frontend (React)
│   ├── package.json       # npm dependencies
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   └── context/       # Socket.IO context
│   └── README.md
│
├── scripts/               # Development scripts
│   ├── run-dev.ps1       # Dev server launcher (Windows)
│   ├── run-dev.sh        # Dev server launcher (Unix)
│   └── check_env.ps1/sh  # Environment checker
│
├── docker/               # Docker configs
│   ├── api.dockerfile
│   ├── nginx.dockerfile
│   └── docker-compose.yml
│
├── supabase/            # Database migrations & config
│   └── migrations/
│
└── SETUP.md             # Detailed setup & deployment guide
```

---

## 🛠️ Development

### Backend (Flask API)

```bash
cd api
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
python app.py
```

API będzie dostępny na: `http://localhost:5000`

Szczegóły: [api/README.md](api/README.md)

### Frontend (React)

```bash
cd web
npm install
npm start
```

Frontend będzie dostępny na: `http://localhost:3000`

---

## 🧪 Testy

Testy backendu:

```bash
cd api
pip install -r requirements-dev.txt
pytest -q
```

Testy frontendu:

```bash
cd web
npm test
```

---

## 🗄️ Baza danych

Projekt korzysta z **Supabase** (zarządzany PostgreSQL). 

### Lokalne dev bez Supabase
- Backend automatycznie używa SQLite in-memory w trybie testowym
- Baza danych jest resetowana przy każdym restarcie

### Setup z Supabase

1. Załóż projekt na [app.supabase.com](https://app.supabase.com)
2. Skopiuj **Connection String** z Supabase
3. Dodaj do `api/.env`:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

Migracje:

```bash
cd supabase
supabase db reset  # applies migrations locally
```

Szczegóły: [supabase/LOCAL_SUPABASE_INSTRUCTIONS.md](supabase/LOCAL_SUPABASE_INSTRUCTIONS.md)

---

## 🔐 Zmienne środowiskowe

Skopiuj przykłady do lokalnych plików `.env`:

```bash
cp api/.env.example api/.env
```

Opcjonalne:
- `PASSWORD_PEPPER` — tajny pepper do hashowania haseł (Argon2)
- `ARGON2_TIME_COST`, `ARGON2_MEMORY_COST`, `ARGON2_PARALLELISM` — parametry Argon2

**Ważne:** Nigdy nie commituj `.env` — plik jest w `.gitignore`.

---

## 🚢 Deployment

### Render.com (rekomendowane)

1. **Backend:** Web Service (Python)
   - Build: `pip install -r api/requirements.txt`
   - Start: `gunicorn -k eventlet -w 1 "app:app" -b 0.0.0.0:$PORT`

2. **Frontend:** Static Site
   - Build: `cd web && npm install && npm run build`
   - Publish directory: `web/build`

### Docker Compose (lokalny full-stack)

```bash
docker-compose -f docker/docker-compose.yml up
```

Szczegóły: [SETUP.md](SETUP.md)

---

## 📝 Autentykacja

API endpoints:

- **POST `/auth/register`** — rejestracja nowego użytkownika
- **POST `/auth/login`** — logowanie (zwraca token)
- **GET `/auth/me`** — dane zalogowanego użytkownika

Hasła są hashowane za pomocą **Argon2** z konfigurowalnym time cost, memory cost i parallelism.

Szczegóły: [api/README.md](api/README.md)

---

## 🤝 Contributing

1. Fork repo
2. Stwórz branch `feature/xyz`
3. Commituj zmiany
4. Uruchom testy: `pytest` (backend) + `npm test` (frontend)
5. Push i otwórz Pull Request

---

## 📜 Licencja

[LICENSE](LICENSE) lub [LICENSE.md](LICENSE.md)

---

## ❓ FAQ

**P: Jak uruchomić front + back razem?**
A: Użyj skryptu: `.\scripts\run-dev.ps1` (Windows) lub `./scripts/run-dev.sh` (Unix)

**P: Gdzie przechowywane są hasła?**
A: W bazie danych w kolumnie `password_hash` (hasło jest hashowane Argon2, nigdy nie w plaintext)

**P: Czy mogę zmienić parametry Argon2?**
A: Tak — ustaw `ARGON2_TIME_COST`, `ARGON2_MEMORY_COST`, `ARGON2_PARALLELISM` w `api/.env`

**P: Co to jest pepper?**
A: Tajny String dołączany do hasła przed hashowaniem (dodatkowa warstwa bezpieczeństwa). Ustaw `PASSWORD_PEPPER` w `api/.env`

---

**Ostatnia aktualizacja:** 2026-02-04
