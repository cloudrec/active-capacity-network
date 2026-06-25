# ACAP local private-devnet runner - STOP.
# Stops ONLY the local devnet process recorded in the PID file by START_LOCAL_DEVNET.
# It never kills arbitrary Besu/Java processes.
$ErrorActionPreference = "SilentlyContinue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $here "runtime\python\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$plan = & $py (Join-Path $here "acap_node_manager.py") devnet | ConvertFrom-Json
$pidFile = $plan.pid_file
if (-not $pidFile) { $pidFile = Join-Path $env:USERPROFILE ".acap-devnet\acap-devnet.pid" }

if (-not (Test-Path $pidFile)) {
  Write-Host "No tracked devnet PID file ($pidFile). Nothing to stop." -ForegroundColor Yellow
  exit 0
}
$procId = Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $procId) { Write-Host "PID file empty. Nothing to stop." -ForegroundColor Yellow; exit 0 }

$proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
if ($proc) {
  Write-Host "Stopping tracked local devnet PID $procId ..." -ForegroundColor Cyan
  Stop-Process -Id $procId -Force
  Write-Host "Stopped PID $procId. (Only the tracked local process was affected.)" -ForegroundColor Green
} else {
  Write-Host "Tracked PID $procId is not running. Clearing stale PID file." -ForegroundColor Yellow
}
Remove-Item $pidFile -ErrorAction SilentlyContinue
