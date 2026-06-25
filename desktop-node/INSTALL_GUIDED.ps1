# Active Capacity Network - Guided setup wizard (PowerShell, private preview).
#
# SAFETY / TRANSPARENCY:
#   * Read-only preview node. No mining, no rewards, no autostart, no background service.
#   * Requires NO administrator rights. Does NOT write outside this folder unless you
#     explicitly opt in to a desktop shortcut.
#   * Stores NO secrets and NO private keys. The only file written is a plain config.json
#     built from config.example.json, shown to you before it is saved.
#   * You can cancel at any prompt (Ctrl+C, or answer "n").
#
# Run from the unzipped package folder:
#   powershell -ExecutionPolicy Bypass -File .\INSTALL_GUIDED.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Line { Write-Host ("-" * 64) }
function Ask([string]$q, [string]$default) {
    if ($default) { $p = "$q [$default]: " } else { $p = "$q: " }
    $a = Read-Host $p
    if ([string]::IsNullOrWhiteSpace($a)) { return $default } else { return $a.Trim() }
}
function YesNo([string]$q, [string]$default = "n") {
    $a = Read-Host "$q (y/n) [$default]"
    if ([string]::IsNullOrWhiteSpace($a)) { $a = $default }
    return ($a.Trim().ToLower() -eq "y")
}

Line
Write-Host "Active Capacity Network - Guided setup wizard"
Write-Host "PRIVATE PREVIEW / PROTOTYPE. Not a production network."
Write-Host "No mainnet. No custody. No payments. No bridge. No rewards. No mining."
Line
$ver = (Get-Content -Raw -Path (Join-Path $root "VERSION.txt") -ErrorAction SilentlyContinue)
if ($ver) { Write-Host ("Package version: {0}" -f $ver.Trim()) }
Write-Host "This wizard only prepares a local config and (optionally) a shortcut."
Write-Host "It does not install a service, does not auto-start, and needs no admin rights."
Line

if (-not (YesNo "Continue with guided setup?" "y")) {
    Write-Host "Cancelled. Nothing was written."
    exit 0
}

# --- Step 1: Python check (informational; the node uses stdlib Python 3) ---
Write-Host ""
Write-Host "[1/6] Checking for Python 3 (needed to run the node client)..."
$py = $null
foreach ($cand in @("python", "py")) {
    try { & $cand --version *> $null; if ($LASTEXITCODE -eq 0) { $py = $cand; break } } catch {}
}
if ($py) { Write-Host ("  Found Python launcher: {0}" -f $py) }
else { Write-Host "  Python 3 not found. Install from https://www.python.org/downloads/ (see README_WINDOWS.md). You can still finish setup now." }

# --- Step 2: node mode ---
Write-Host ""
Write-Host "[2/6] Choose a node mode:"
Write-Host "  1) light       - light preview node (default, lowest footprint)"
Write-Host "  2) capacity    - capacity preview node"
Write-Host "  3) diagnostics - diagnostics only, no node run loop"
$modeSel = Ask "Enter 1, 2 or 3" "1"
switch ($modeSel) {
    "2" { $role = "capacity" }
    "3" { $role = "diagnostics" }
    default { $role = "light" }
}
Write-Host ("  Selected mode: {0}" -f $role)

# --- Step 3: API base URL ---
Write-Host ""
Write-Host "[3/6] API base URL (the public preview endpoint to talk to)."
$apiBase = Ask "API base URL" "https://capacity.469diamond.com"
$nodeName = Ask "Node name (local label only)" "my-acn-node"

# --- Step 4: verify package files ---
Write-Host ""
Write-Host "[4/6] Verifying package files..."
& powershell -ExecutionPolicy Bypass -File (Join-Path $root "VERIFY_PACKAGE.ps1")

# --- Step 5: show config, then write only on confirmation ---
Write-Host ""
Write-Host "[5/6] The following local config.json will be created:"
$cfg = [ordered]@{
    capacity_base = $apiBase
    auction_base  = "https://auction.469diamond.com"
    role          = ($(if ($role -eq "diagnostics") { "light" } else { $role }))
    poll_seconds  = 60
    node_name     = $nodeName
}
$cfgJson = ($cfg | ConvertTo-Json -Depth 4)
Line
Write-Host $cfgJson
Line
Write-Host "No secrets and no private keys are stored. This file is plain text in this folder."
if (YesNo "Write config.json now?" "y") {
    $cfgPath = Join-Path $root "config.json"
    if (Test-Path $cfgPath) {
        if (-not (YesNo "config.json already exists. Overwrite?" "n")) {
            Write-Host "  Kept existing config.json."
        } else {
            $cfgJson | Set-Content -Path $cfgPath -Encoding UTF8
            Write-Host ("  Wrote {0}" -f $cfgPath)
        }
    } else {
        $cfgJson | Set-Content -Path $cfgPath -Encoding UTF8
        Write-Host ("  Wrote {0}" -f $cfgPath)
    }
} else {
    Write-Host "  Skipped writing config.json."
}

# --- Step 6: optional shortcut + optional diagnostics ---
Write-Host ""
Write-Host "[6/6] Optional extras."
if (YesNo "Create an opt-in desktop shortcut to the status check?" "n") {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $root "CREATE_DESKTOP_SHORTCUT.ps1")
}
if (YesNo "Run a quick read-only diagnostics check now?" "y") {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $root "RUN_DIAGNOSTICS.ps1")
}

Line
Write-Host "Setup complete. To run the node later:"
Write-Host ("  - Light node:    START_LIGHT_NODE.bat")
Write-Host ("  - Capacity node: START_CAPACITY_NODE.bat")
Write-Host ("  - Status check:  CHECK_STATUS.bat")
Write-Host "Remember: private preview only. No mainnet, no rewards, no custody."
Line
exit 0
