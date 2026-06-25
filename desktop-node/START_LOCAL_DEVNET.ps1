# ACAP local private-devnet runner - START (loopback only, lab machine only).
# Private devnet/testnet ONLY. No mainnet, no rewards, no public RPC.
# Uses the bundled NON-PRODUCTION runtime/devnet/ genesis + lab validator key.
# Validates the plan, refuses on servers / non-loopback RPC, requires an explicit YES,
# writes chain data under your user profile, and records a PID for a safe STOP.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $here "runtime\python\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "ACAP local devnet - validating plan (bundled genesis, loopback only, no mainnet/rewards)..." -ForegroundColor Cyan
$plan = & $py (Join-Path $here "acap_node_manager.py") devnet | ConvertFrom-Json

if ($plan.server_environment) { Write-Host "REFUSED: server environment. Never start a devnet here." -ForegroundColor Red; exit 1 }
if (-not $plan.rpc_loopback_only) { Write-Host "REFUSED: RPC is not loopback (127.0.0.1 only)." -ForegroundColor Red; exit 1 }
if (-not $plan.bundle.present) { Write-Host "REFUSED: devnet bundle missing (runtime/devnet/). Download the full ZIP." -ForegroundColor Red; exit 1 }
if (-not $plan.bundle.valid)   { Write-Host "REFUSED: devnet bundle invalid: $($plan.bundle.errors -join '; ')" -ForegroundColor Red; exit 1 }
if (-not $plan.one_click_ready) {
  Write-Host "Not ready to start. Blockers:" -ForegroundColor Yellow
  $plan.blockers | ForEach-Object { Write-Host "  - $_" }
  Write-Host "Besu + Java (17+) are required for the local devnet." -ForegroundColor Yellow
  exit 2
}

$dataDir = $plan.data_dir
$pidFile = $plan.pid_file
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

Write-Host "Bundle  : $($plan.bundle.path)  (NON-PRODUCTION lab keys)" -ForegroundColor Green
Write-Host "RPC     : $($plan.rpc_url)  chain_id: $($plan.chain_id)  (loopback only)" -ForegroundColor Green
Write-Host "P2P     : $($plan.p2p_exposure)  (single validator - no peers; port 30303 not opened)" -ForegroundColor Green
Write-Host "Data dir: $dataDir" -ForegroundColor Green
Write-Host "Start command:" -ForegroundColor Green
Write-Host "  $($plan.commands.start)"
$ans = Read-Host "Run this LOCAL devnet now? (type YES to proceed)"
if ($ans -ne "YES") { Write-Host "Aborted. (Command shown above - run it manually if you prefer.)"; exit 0 }

if (Test-Path $pidFile) {
  $old = Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
    Write-Host "A tracked devnet (PID $old) is already running. Use STOP_LOCAL_DEVNET first." -ForegroundColor Yellow
    exit 3
  }
}

Write-Host "Starting local Besu devnet (127.0.0.1 only, P2P disabled)..." -ForegroundColor Cyan
$besu    = $plan.runtime.besu_path
$genesis = $plan.bundle.genesis_file
$key     = $plan.bundle.validator_key_file
$config  = $plan.bundle.config_file
# P2P stays loopback-only: config.toml sets p2p-enabled=false; we also pass it explicitly so
# the safe posture cannot be lost. Besu p2p-host alone would still listen on all interfaces.
$besuArgs = @(
  "--data-path=$dataDir",
  "--genesis-file=$genesis",
  "--node-private-key-file=$key",
  "--config-file=$config",
  "--p2p-enabled=false"
)
$proc = Start-Process -FilePath $besu -ArgumentList $besuArgs -PassThru -NoNewWindow
Set-Content -Path $pidFile -Value $proc.Id
Write-Host "Started. PID $($proc.Id) recorded at $pidFile" -ForegroundColor Green
Write-Host "Check status with CHECK_LOCAL_DEVNET.bat ; stop with STOP_LOCAL_DEVNET.bat" -ForegroundColor Green
