# COLLECT_DIAGNOSTICS.ps1 - gather a safe diagnostics bundle to send back to the maintainer.
# Read-only. Collects OS / PowerShell / Java / Besu / port / package layout / dependency report.
# NEVER includes wallet files, private keys, seeds, mnemonics, or passwords. No node is started.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$dataDir = Get-QaDataDir
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outFile = Join-Path $dataDir "acap-diagnostics-$stamp.txt"

Write-Host "ACAP QA - collecting diagnostics (no secrets)..." -ForegroundColor Cyan

$lines = @()
$lines += "ACAP Desktop Node - diagnostics ($stamp)"
$lines += "NOTE: no private keys / seeds / passwords are included."
$lines += "-----------------------------------------------------------"
$lines += "package_root : $pkg"
$lines += "python       : $py"
try { $lines += "os           : " + ((Get-CimInstance Win32_OperatingSystem).Caption) } catch { $lines += "os           : " + [System.Environment]::OSVersion.VersionString }
$lines += "ps_version   : " + $PSVersionTable.PSVersion.ToString()
$lines += "arch         : " + $env:PROCESSOR_ARCHITECTURE

$ver = Join-Path $pkg "VERSION.txt"
if (Test-Path $ver) { $lines += "pkg_version  : " + (Get-Content $ver -Raw).Trim() }

# Dependency report (version-aware) - JSON, no secrets.
$deps = & $py (Join-Path $pkg "acap_node_manager.py") deps 2>&1 | Out-String
$lines += ""
$lines += "=== dependencies (acap_node_manager.py deps) ==="
$lines += $deps.Trim()

# Devnet bundle validation - addresses + hashes only.
$bundle = & $py (Join-Path $pkg "acap_node_manager.py") bundle 2>&1 | Out-String
$lines += ""
$lines += "=== devnet bundle (acap_node_manager.py bundle) ==="
$lines += $bundle.Trim()

# Node log tail, if any (the node never logs secrets).
$logCandidates = @(
    (Join-Path $env:APPDATA "ACAP-Desktop-Node\logs\node.log"),
    (Join-Path $env:USERPROFILE ".acap-desktop-node\logs\node.log")
)
foreach ($lp in $logCandidates) {
    if ($lp -and (Test-Path $lp)) {
        $lines += ""
        $lines += "=== node.log (last 60 lines) : $lp ==="
        $lines += (Get-Content $lp -Tail 60)
        break
    }
}

$lines | Set-Content -Path $outFile -Encoding UTF8
Write-Host ("Diagnostics written: {0}" -f $outFile) -ForegroundColor Green
Write-Host "Send THIS file (plus screenshots) to the maintainer. It contains no secrets." -ForegroundColor Green
[pscustomobject]@{ name = "diagnostics"; output = $outFile }
