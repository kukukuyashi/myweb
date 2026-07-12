# CYINC local API dev server (uvicorn --reload)
# Usage: npm run dev:api   OR   cd backend; .\scripts\dev.ps1

$ErrorActionPreference = "Stop"
$BackendRoot = Split-Path $PSScriptRoot -Parent
Set-Location $BackendRoot

$python = Join-Path $BackendRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Missing backend\.venv — run: python -m venv .venv; pip install -r requirements.txt"
}

if (-not (Test-Path (Join-Path $BackendRoot ".env"))) {
    Write-Warning "Missing backend\.env — copy from .env.example before starting."
}

Write-Host "==> CYINC API  http://127.0.0.1:8000"
Write-Host "    Swagger    http://127.0.0.1:8000/api/docs"
Write-Host "    Admin      http://127.0.0.1:8000/admin"
Write-Host "    Ctrl+C to stop; code changes auto-reload"
Write-Host ""

& $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
