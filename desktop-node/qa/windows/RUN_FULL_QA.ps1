# RUN_FULL_QA.ps1 - run the full ACAP Windows QA suite and write a report.
#
# SAFE BY DEFAULT: read-only. It does NOT start the local devnet (it never produces blocks
# on its own). It does NOT create wallets, never asks for or prints passwords / private keys /
# seeds, and never contacts a public/remote RPC. Runs fine as a normal (non-admin) user.
#
# Produces, in your user data dir (%APPDATA%\ACAP-Desktop-Node\qa):
#   qa-report.json   (machine-readable, PASS/WARN/FAIL per check)
#   qa-report.txt    (human-readable summary)
#
# The live-devnet check is SKIPPED unless you pass -IncludeLiveDevnet (and even then it only
# *probes* a devnet you started yourself - it still never starts one).
param(
    [switch]$IncludeLiveDevnet
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$dataDir = Get-QaDataDir
$stamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " ACAP Desktop Node - Windows QA suite (read-only, no devnet start)" -ForegroundColor Cyan
Write-Host " package: $pkg" -ForegroundColor DarkGray
Write-Host "=================================================================" -ForegroundColor Cyan

$sections = @()
$scripts = @(
    "CHECK_ENVIRONMENT.ps1",
    "CHECK_PACKAGE_LAYOUT.ps1",
    "CHECK_WALLET.ps1",
    "CHECK_BESU_WALLET.ps1",
    "CHECK_DEVNET_BUNDLE.ps1"
)
if ($IncludeLiveDevnet) { $scripts += "CHECK_LOCAL_DEVNET.ps1" }

foreach ($s in $scripts) {
    Write-Host ""
    $sp = Join-Path $here $s
    try {
        $res = & $sp
        # A section script emits one object with .name + .checks; collect the last such object.
        $obj = $res | Where-Object { $_.PSObject.Properties.Name -contains "checks" } | Select-Object -Last 1
        if ($obj) { $sections += $obj }
    } catch {
        Write-Host ("  [FAIL] $s crashed: " + $_.Exception.Message) -ForegroundColor Red
        $sections += [pscustomobject]@{ name = $s; checks = @(
            [pscustomobject]@{ id = "run"; label = $s; status = "FAIL"; detail = $_.Exception.Message; fix = "" }) }
    }
}

# Tally.
$all = @()
foreach ($sec in $sections) { foreach ($c in $sec.checks) { $all += $c } }
$pass = ($all | Where-Object { $_.status -eq "PASS" }).Count
$warn = ($all | Where-Object { $_.status -eq "WARN" }).Count
$fail = ($all | Where-Object { $_.status -eq "FAIL" }).Count
$overall = if ($fail -gt 0) { "FAIL" } elseif ($warn -gt 0) { "WARN" } else { "PASS" }

$report = [pscustomobject]@{
    product       = "ACAP Desktop Node"
    qa_pack       = "windows"
    generated_at  = $stamp
    package_root  = $pkg
    overall       = $overall
    counts        = [pscustomobject]@{ pass = $pass; warn = $warn; fail = $fail }
    live_devnet_included = [bool]$IncludeLiveDevnet
    safety        = "read-only; no devnet started; no keys/seeds/passwords printed; loopback only; no mainnet/rewards/custody"
    sections      = $sections
}

$jsonPath = Join-Path $dataDir "qa-report.json"
$txtPath  = Join-Path $dataDir "qa-report.txt"
$report | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding UTF8

$txt = @()
$txt += "ACAP Desktop Node - Windows QA report"
$txt += "generated: $stamp"
$txt += "package  : $pkg"
$txt += "OVERALL  : $overall   (PASS=$pass  WARN=$warn  FAIL=$fail)"
$txt += "safety   : read-only; no devnet started; no secrets printed; loopback only; no mainnet/rewards"
$txt += "-----------------------------------------------------------"
foreach ($sec in $sections) {
    $txt += ""
    $txt += "[" + $sec.name + "]"
    foreach ($c in $sec.checks) {
        $txt += ("  {0,-4} {1} - {2}" -f $c.status, $c.label, $c.detail)
        if ($c.status -ne "PASS" -and $c.fix) { $txt += ("        fix: " + $c.fix) }
    }
}
$txt | Set-Content -Path $txtPath -Encoding UTF8

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
$col = switch ($overall) { "PASS" { "Green" } "WARN" { "Yellow" } default { "Red" } }
Write-Host (" OVERALL: {0}   PASS={1}  WARN={2}  FAIL={3}" -f $overall, $pass, $warn, $fail) -ForegroundColor $col
Write-Host (" report : {0}" -f $jsonPath) -ForegroundColor Green
Write-Host (" report : {0}" -f $txtPath) -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
if (-not $IncludeLiveDevnet) {
    Write-Host "Tip: after you start the devnet (START_LOCAL_DEVNET.bat), re-run with -IncludeLiveDevnet" -ForegroundColor DarkGray
    Write-Host "     to also verify chain id / block height / peers on the running devnet." -ForegroundColor DarkGray
}
exit $(if ($overall -eq "FAIL") { 1 } else { 0 })
