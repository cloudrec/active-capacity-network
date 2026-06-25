# Active Capacity Network - diagnostics (PowerShell, read-only HTTPS GET).
# Calls the public preview API and the node client's own diagnostics. Writes nothing,
# stores nothing, needs no admin rights. Private preview: no mainnet, no rewards.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$base = $env:ACN_CAPACITY_BASE
if (-not $base) {
    $cfgPath = Join-Path $root "config.json"
    if (Test-Path $cfgPath) {
        try { $base = (Get-Content -Raw $cfgPath | ConvertFrom-Json).capacity_base } catch {}
    }
}
if (-not $base) { $base = "https://capacity.469diamond.com" }

Write-Host ("Diagnostics against {0}" -f $base)
Write-Host "(read-only; nothing is uploaded or stored)"
Write-Host ("-" * 56)
try {
    $health = Invoke-RestMethod -Uri "$base/api/health" -TimeoutSec 15
    Write-Host ("health.ok={0} preview={1} mainnet={2}" -f $health.ok, $health.preview, $health.mainnet)
} catch { Write-Host ("health check failed: {0}" -f $_.Exception.Message) }
try {
    $sum = Invoke-RestMethod -Uri "$base/api/live/summary" -TimeoutSec 15
    Write-Host ("last_synced={0} stale={1}" -f $sum.last_synced, $sum.stale)
} catch { Write-Host ("summary check failed: {0}" -f $_.Exception.Message) }

# also run the node client's own diagnostics if Python is available
foreach ($cand in @("python", "py")) {
    try {
        & $cand --version *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ("-" * 56)
            Write-Host "Node client diagnostics:"
            & $cand (Join-Path $root "acn_node.py") diagnostics
            break
        }
    } catch {}
}
Write-Host ("-" * 56)
Write-Host "Done. Private preview only - no mainnet, no rewards, no custody."
