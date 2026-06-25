# ACAP Desktop Node - per-user uninstaller (private preview).
#
# Removes ONLY %LOCALAPPDATA%\ACAP-Desktop-Node. Touches no registry keys, no services,
# no global PATH, no Program Files. Requires an explicit YES.
#
# Usage (normally via ACAP_UNINSTALL.bat):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\ACAP_UNINSTALL.ps1 [-KeepData]
param(
    [switch]$KeepData
)
$ErrorActionPreference = "Stop"
$Root = Join-Path $env:LOCALAPPDATA "ACAP-Desktop-Node"

Write-Host ("ACAP Desktop Node - uninstaller") -ForegroundColor Cyan
Write-Host ("Target folder: " + $Root)
if (-not (Test-Path $Root)) {
    Write-Host "Nothing to remove (folder not found). Already uninstalled." -ForegroundColor Green
    exit 0
}

# Stop a running node UI if present (best-effort, by image path under our folder).
try {
    Get-Process -Name "ACAP.Node" -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path.StartsWith($Root)
    } | ForEach-Object { Write-Host ("  stopping " + $_.Id); Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
} catch {}

Write-Host "This will delete the per-user install folder above." -ForegroundColor Yellow
if ($KeepData) { Write-Host "data\ will be KEPT (-KeepData)." -ForegroundColor Yellow }
$ans = Read-Host "Type YES to uninstall"
if ($ans -ne "YES") { Write-Host "Aborted. Nothing was removed."; exit 0 }

if ($KeepData) {
    Get-ChildItem -Path $Root -Force | Where-Object { $_.Name -ne "data" } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host ("Removed everything except data\ under " + $Root) -ForegroundColor Green
} else {
    Remove-Item -Path $Root -Recurse -Force
    Write-Host ("Removed " + $Root) -ForegroundColor Green
}
Write-Host "Note: a local devnet chain dir under %USERPROFILE%\.acap-devnet (if any) was left untouched." -ForegroundColor Yellow
exit 0
