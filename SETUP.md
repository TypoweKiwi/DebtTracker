# Setup & Deployment notes ✅

## Wymagane narzędzia i wersje (zalecane)
- Node.js: 16.x lub 18.x (Render obsługuje 16/18). Dodano `engines` w `web/package.json`.
- Python: 3.8+ (zrzeczenie: current environment.yml uses Python 3.7; zalecane zaktualizować do 3.10+ dla Render)
- Docker: najnowsza stabilna wersja
- PostgreSQL: 13+ (Supabase oferuje zarządzany Postgres)

## Co zmieniłem 🔧
- `api/requirements.txt` – przypięte wersje (Flask, gunicorn, eventlet, Flask-SocketIO, psycopg2-binary, python-dotenv, SQLAlchemy, alembic, requests).
- `web/package.json` – dodano `serve` (do serwowania statycznej paczki na Render) i pole `engines.node` (>=16.14.0 <20) oraz ustawiono `start` na `serve -s build`.
- Dodano `api/.env.example`, `api/Procfile` (polecenie dla Render: `gunicorn -k eventlet -w 1 "app:app" -b 0.0.0.0:$PORT`).
- Dodano skrypty `scripts/check_env.*` do szybkiego sprawdzenia wersji i zainstalowanych pakietów.

## Deploy Backend (Render)
1. W Render: utwórz nową usługę Web Service (Python).
2. Repo: wskaz repozytorium i branch.
3. Build command: `pip install -r api/requirements.txt && pip install -r requirements-dev.txt || true` (opcjonalnie użyj venv)
4. Start command: `gunicorn -k eventlet -w 1 "app:app" -b 0.0.0.0:$PORT`
5. Dodaj zmienne środowiskowe z `api/.env.example` (DATABASE_URL, SUPABASE_KEY etc.)

## Baza danych (Supabase)
- Załóż projekt na https://app.supabase.com
- Skonfiguruj zmienne środowiskowe: ustaw `DATABASE_URL` (given by Supabase) oraz ewentualnie `SUPABASE_KEY`.
- Użyj `psycopg2-binary` w backendzie do połączeń z Postgres lub klienta Supabase (supabase-py).

## Frontend (Render)
- Możesz deployować jako Static Site (Build command: `npm install && npm run build`, Publish directory: `web/build`). Alternatywnie jako Web Service ustaw start na `serve -s build`.

## Sprawdzenie środowiska
- Uruchom `./scripts/check_env.ps1` na Windows lub `./scripts/check_env.sh` na *nix, aby szybko zweryfikować wymagane narzędzia i pakiety.

---
Jeśli chcesz, mogę: 
- zaktualizować `api/environment.yml` do nowszej wersji Pythona,
- dodać `requirements-dev.txt` (pytest, black, flake8),
- skonfigurować `Dockerfile` dla backendu i frontend-u do lokalnego developmentu/CI.

Powiedz, którą z tych opcji chcesz, a wprowadzę kolejne zmiany.