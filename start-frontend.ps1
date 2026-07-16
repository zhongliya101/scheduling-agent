$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $repoRoot "frontend"
$nodeDir = "C:\Program Files\nodejs"
$nodeExe = Join-Path $nodeDir "node.exe"
$npmCmd = Join-Path $nodeDir "npm.cmd"

if (-not (Test-Path $nodeExe) -or -not (Test-Path $npmCmd)) {
    Write-Host "Node.js was not found under C:\Program Files\nodejs" -ForegroundColor Red
    exit 1
}

$env:Path = "$nodeDir;$env:Path"

Set-Location $frontendDir
Write-Host "Starting frontend at http://127.0.0.1:5173" -ForegroundColor Green
& $npmCmd run dev
