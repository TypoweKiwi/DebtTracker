# PowerShell script to check basic environment setup (Windows)
Write-Output "Checking system tools and versions..."
python --version
node --version
docker --version
psql --version 2>$null | Out-Null; if ($LASTEXITCODE -eq 0) { psql --version } else { Write-Output "psql not found (Postgres client)" }

Write-Output "Checking required Python packages (api)..."
$packages = @("Flask","gunicorn","eventlet","Flask-SocketIO","psycopg2-binary","python-dotenv")
foreach ($p in $packages) {
    $pkg = pip show $p 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Output "$p not found" } else { Write-Output "$p installed" }
}

Write-Output "Checking npm packages (web)..."
if (Test-Path "./web/package.json") {
    Push-Location ./web
    npm ls --depth=0 2>$null | Out-Null; if ($LASTEXITCODE -eq 0) { npm ls --depth=0 } else { Write-Output "Some npm packages may be missing (run npm install in ./web)" }
    Pop-Location
} else { Write-Output "web/package.json not found" }

Write-Output "Done."