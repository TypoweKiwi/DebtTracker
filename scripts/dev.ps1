param(
    [ValidateSet("sqlite", "supabase")]
    [string]$Db = "sqlite",
    [switch]$MockData
)

$useSqlite = $Db -eq "sqlite"
$env:USE_SQLITE = if ($useSqlite) { "1" } else { "0" }

if ($useSqlite) {
    Write-Host "Using SQLite (USE_SQLITE=1)"
} else {
    Write-Host "Using DATABASE_URL from api/.env (USE_SQLITE=0)"
}

if ($MockData) {
    Write-Host "Seeding mock data..."
    python api/seed.py
}

python api/app.py
