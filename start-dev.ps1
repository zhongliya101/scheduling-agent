$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendScript = Join-Path $repoRoot "start-backend.ps1"
$frontendScript = Join-Path $repoRoot "start-frontend.ps1"

if (-not (Test-Path $backendScript) -or -not (Test-Path $frontendScript)) {
    Write-Host "Startup scripts are missing." -ForegroundColor Red
    exit 1
}

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $backendScript
) -WorkingDirectory $repoRoot

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $frontendScript
) -WorkingDirectory $repoRoot

Write-Host "Opened backend and frontend startup windows." -ForegroundColor Green
