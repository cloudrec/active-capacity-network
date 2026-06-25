# ACAP local private-devnet runner - CHECK.
# Read-only LOOPBACK RPC probe: chain id / block height / peer count. Never calls a
# remote/public endpoint.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $here "runtime\python\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "ACAP local devnet - loopback RPC check (127.0.0.1 only):" -ForegroundColor Cyan
$chk = & $py (Join-Path $here "acap_node_manager.py") check | ConvertFrom-Json
Write-Host ("  connected   : {0}" -f $chk.connected)
Write-Host ("  chain id    : {0}" -f $chk.chain_id)
Write-Host ("  block height: {0}" -f $chk.block_height)
Write-Host ("  peer count  : {0}" -f $chk.peer_count)
if (-not $chk.connected) { Write-Host ("  note        : {0}" -f $chk.error) -ForegroundColor Yellow }
Write-Host ("  {0}" -f $chk.note) -ForegroundColor DarkGray

Write-Host ""
Write-Host "Declared posture (from devnet plan / config):" -ForegroundColor Cyan
$plan = & $py (Join-Path $here "acap_node_manager.py") devnet | ConvertFrom-Json
Write-Host ("  P2P exposure      : {0}" -f $plan.p2p_exposure)
Write-Host ("  P2P public listener: {0}" -f $plan.p2p_public_listener)
Write-Host ("  RPC exposure      : {0}" -f $plan.rpc_exposure)
Write-Host ("  Besu launcher kind: {0}" -f $plan.besu_launcher_kind)
if ($plan.besu_launcher_kind -eq "unix_script") {
  Write-Host "  WARN: unix besu script on Windows - need besu.bat (unzip full Besu release)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "P2P exposure audit (port 30303 must NOT listen on a public/non-loopback interface):" -ForegroundColor Cyan
$audit = & $py (Join-Path $here "acap_node_manager.py") p2p-audit | ConvertFrom-Json
if (-not $audit.checked) {
  Write-Host ("  WARN: {0}" -f $audit.note) -ForegroundColor Yellow
} elseif ($audit.public_listener) {
  Write-Host ("  FAIL: {0}" -f $audit.note) -ForegroundColor Red
  foreach ($l in $audit.listeners) {
    if ($l.kind -eq "public") { Write-Host ("        public listener: {0} ({1})" -f $l.local, $l.proto) -ForegroundColor Red }
  }
  Write-Host "        Fix: ensure p2p-enabled=false in runtime\devnet\config.toml, then restart." -ForegroundColor Yellow
} else {
  Write-Host ("  OK  : {0}" -f $audit.note) -ForegroundColor Green
}

Write-Host ""
Write-Host "Devnet plan (bundle + blockers):" -ForegroundColor Cyan
& $py (Join-Path $here "acap_node_manager.py") devnet
