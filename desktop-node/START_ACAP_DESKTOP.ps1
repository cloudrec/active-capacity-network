# ACAP Desktop Node - wallet-like local shell (private preview, devnet/testnet only).
# Binds 127.0.0.1 ONLY. No mainnet, no rewards, no key upload.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) {
  Write-Host "Python 3 required. Install from https://www.python.org/downloads/ (Add to PATH)."
  Read-Host "Press Enter to exit"; exit 1
}
Write-Host "Starting ACAP Desktop Node (local UI: http://127.0.0.1:8599 )..."
& python (Join-Path $here "acap_desktop.py") --port 8599
