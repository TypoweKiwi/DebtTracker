#Requires -Version 5.0
<#
.SYNOPSIS
    Run DebtTracker in development mode on localhost.
    Launches both API (Flask) and Web (React) servers side-by-side.

.DESCRIPTION
    This script sets up and runs the backend API and frontend web app for local development.
    - API runs on http://localhost:5000 (or next available port)
    - Web runs on http://localhost:3000 (or next available port)

    Prerequisites:
    - Python 3.8+ with pip
    - Node.js 16+ with npm
    - Virtual environment for Python (recommended)

.EXAMPLE
    .\run-dev.ps1
#>

param(
    [switch]$NoFrontend,
    [switch]$NoBackend
)

# Get repo root
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "🚀 Starting DebtTracker development environment..." -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot`n" -ForegroundColor Gray

# Validate prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Cyan

$pythonFound = $false
$nodeFound = $false

try {
    $pythonVer = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python: $pythonVer" -ForegroundColor Green
        $pythonFound = $true
    }
} catch {
    Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
}

try {
    $nodeVer = & node --version
    $npmVer = & npm --version
    Write-Host "✓ Node.js: $nodeVer, npm: $npmVer" -ForegroundColor Green
    $nodeFound = $true
} catch {
    Write-Host "✗ Node.js/npm not found or not in PATH" -ForegroundColor Red
}

if (-not $pythonFound -and -not $NoBackend) {
    Write-Host "`n❌ Python is required for the backend. Install from https://python.org" -ForegroundColor Red
    exit 1
}

if (-not $nodeFound -and -not $NoFrontend) {
    Write-Host "`n❌ Node.js is required for the frontend. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Backend setup
if (-not $NoBackend) {
    Write-Host "`n📦 Setting up backend..." -ForegroundColor Cyan
    
    $apiDir = Join-Path $repoRoot "api"
    $venvDir = Join-Path $apiDir ".venv"

    # Create venv if missing
    if (-not (Test-Path $venvDir)) {
        Write-Host "Creating Python virtual environment..."
        & python -m venv $venvDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
    }

    # Activate venv and install dependencies
    $activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
    Write-Host "Activating venv and installing dependencies..."
    & $activateScript
    & pip install -q -r (Join-Path $apiDir "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Backend ready" -ForegroundColor Green
}

# Frontend setup
if (-not $NoFrontend) {
    Write-Host "`n📦 Setting up frontend..." -ForegroundColor Cyan
    
    $webDir = Join-Path $repoRoot "web"
    
    Write-Host "Installing npm dependencies..."
    Push-Location $webDir
    & npm install -q
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    Pop-Location
    Write-Host "✓ Frontend ready" -ForegroundColor Green
}

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting development servers..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Start backend
if (-not $NoBackend) {
    Write-Host "`n🔵 Backend: http://localhost:5000" -ForegroundColor Green
    $apiDir = Join-Path $repoRoot "api"
    $venvDir = Join-Path $apiDir ".venv"
    $activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
    
    $backendJob = Start-Job -ScriptBlock {
        param($apiDir, $activateScript)
        & $activateScript
        Set-Location $apiDir
        & python app.py
    } -ArgumentList $apiDir, $activateScript
    
    Write-Host "Backend PID: $($backendJob.Id)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

# Start frontend
if (-not $NoFrontend) {
    Write-Host "🟢 Frontend: http://localhost:3000" -ForegroundColor Green
    $webDir = Join-Path $repoRoot "web"
    
    $frontendJob = Start-Job -ScriptBlock {
        param($webDir)
        Set-Location $webDir
        & npm start
    } -ArgumentList $webDir
    
    Write-Host "Frontend PID: $($frontendJob.Id)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

Write-Host "`n" -ForegroundColor Cyan
Write-Host "Both servers should be running. Check the logs above for any errors." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop all servers." -ForegroundColor Yellow

# Wait for user interrupt
try {
    while ($true) {
        Start-Sleep -Seconds 10
    }
} finally {
    Write-Host "`n`nCleaning up..." -ForegroundColor Cyan
    if ($backendJob) {
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
        Write-Host "✓ Backend stopped" -ForegroundColor Green
    }
    if ($frontendJob) {
        Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Write-Host "✓ Frontend stopped" -ForegroundColor Green
    }
}
