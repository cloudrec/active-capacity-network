# Active Capacity Network - node health check (PowerShell). Read-only HTTPS GET.
$ErrorActionPreference = "Stop"
$base = $env:ACN_CAPACITY_BASE; if (-not $base) { $base = "https://capacity.469diamond.com" }
Write-Host "Checking $base ..."
try {
    $health  = Invoke-RestMethod -Uri "$base/api/health" -TimeoutSec 15
    $summary = Invoke-RestMethod -Uri "$base/api/live/summary" -TimeoutSec 15
    Write-Host ("health.ok = {0}  preview = {1}  mainnet = {2}" -f $health.ok, $health.preview, $health.mainnet)
    Write-Host ("last_synced = {0}  stale = {1}" -f $summary.last_synced, $summary.stale)
    Write-Host "OK - this is a private-preview network. No mainnet, no rewards."
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}
