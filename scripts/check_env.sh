#!/usr/bin/env bash
set -e

echo "Checking system tools..."
python --version || echo "python not found"
node --version || echo "node not found"
docker --version || echo "docker not found"
psql --version || echo "psql not found"

echo "Checking Python packages (api)..."
REQS=("Flask" "gunicorn" "eventlet" "Flask-SocketIO" "psycopg2-binary" "python-dotenv")
for p in "${REQS[@]}"; do
  pip show "$p" > /dev/null || echo "$p not installed"
done

echo "Check frontend deps in ./web"
if [ -f "./web/package.json" ]; then
  (cd web && npm ls --depth=0) || echo "Run 'npm install' in ./web"
else
  echo "./web/package.json not found"
fi

echo "Done."