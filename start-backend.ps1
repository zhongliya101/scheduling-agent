$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
$configPath = Join-Path $backendDir "config\llm.json"

if (-not (Test-Path $venvPython)) {
    Write-Host "Missing backend virtual environment: $venvPython" -ForegroundColor Red
    Write-Host "Create it first with Python 3.12 and install backend requirements." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $configPath)) {
    Write-Host "Warning: backend/config/llm.json not found. Agent calls will fall back." -ForegroundColor Yellow
}

Set-Location $backendDir
Write-Host "Starting backend at http://127.0.0.1:8000" -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000
