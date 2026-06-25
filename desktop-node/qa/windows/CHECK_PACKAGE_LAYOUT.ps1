# CHECK_PACKAGE_LAYOUT.ps1 - verify the extracted ZIP has the expected files.
# Read-only. Confirms ACAP.Node.exe, bundled Python, node modules, devnet bundle, and the
# START/STOP/CHECK devnet scripts are all present. No mainnet claims. No node is started.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$checks = @()

Write-Host "ACAP QA - package layout" -ForegroundColor Cyan

function Test-Member {
    param([string]$Id, [string]$Label, [string]$Rel, [string]$Fix, [switch]$Optional)
    $full = Join-Path $pkg $Rel
    if (Test-Path $full) {
        $size = (Get-Item $full).Length
        return New-QaCheck $Id $Label "PASS" ("found ({0:N0} B): {1}" -f $size, $Rel)
    }
    $st = if ($Optional) { "WARN" } else { "FAIL" }
    return New-QaCheck $Id $Label $st ("missing: $Rel") $Fix
}

$zipFix = "Re-extract the full active-capacity-node-windows.zip (do not move files out of the folder)."
$checks += Test-Member "exe"        "ACAP.Node.exe"           "ACAP.Node.exe"                       $zipFix
$checks += Test-Member "python"     "Bundled Python runtime"  "runtime\python\python.exe"           "Use the full ZIP - it bundles Python (runtime/python/). The standalone EXE needs system Python."
$checks += Test-Member "desktop"    "Desktop node module"     "acap_desktop.py"                     $zipFix
$checks += Test-Member "wallet"     "Wallet module"           "acap_wallet.py"                      $zipFix
$checks += Test-Member "besuwallet" "Besu wallet module"      "acap_besu_wallet.py"                 $zipFix
$checks += Test-Member "nodemgr"    "Node manager"            "acap_node_manager.py"               $zipFix
$checks += Test-Member "keccak"     "Keccak module"           "acap_keccak.py"                      $zipFix
$checks += Test-Member "genesis"    "Devnet genesis"          "runtime\devnet\genesis.json"        $zipFix
$checks += Test-Member "devmani"    "Devnet manifest"         "runtime\devnet\manifest.json"       $zipFix
$checks += Test-Member "devcfg"     "Devnet config (loopback)" "runtime\devnet\config.toml"        $zipFix
$checks += Test-Member "startdev"   "START_LOCAL_DEVNET.ps1"  "START_LOCAL_DEVNET.ps1"             $zipFix
$checks += Test-Member "stopdev"    "STOP_LOCAL_DEVNET.ps1"   "STOP_LOCAL_DEVNET.ps1"              $zipFix
$checks += Test-Member "checkdev"   "CHECK_LOCAL_DEVNET.ps1"  "CHECK_LOCAL_DEVNET.ps1"             $zipFix
$checks += Test-Member "startapp"   "START_ACAP_DESKTOP.ps1"  "START_ACAP_DESKTOP.ps1"             $zipFix
$checks += Test-Member "manifest"   "Package MANIFEST.json"   "MANIFEST.json"                      $zipFix

# Honesty: a real devnet bundle must NOT advertise mainnet.
$genPath = Join-Path $pkg "runtime\devnet\genesis.json"
if (Test-Path $genPath) {
    try {
        $gen = Get-Content $genPath -Raw | ConvertFrom-Json
        $cid = $gen.config.chainId
        $okChain = ($cid -eq 469469)
        $checks += New-QaCheck "chainid" "Devnet chainId 469469" ($(if($okChain){"PASS"}else{"FAIL"})) ("chainId=$cid") `
            "Genesis chainId must be 469469 for the private lab devnet."
    } catch {
        $checks += New-QaCheck "chainid" "Devnet chainId 469469" "FAIL" "could not parse genesis.json" $zipFix
    }
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "package_layout"; checks = $checks }
