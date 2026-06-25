# _qa_lib.ps1 - shared helpers for the ACAP Windows QA pack (dot-sourced by the CHECK_*.ps1).
# Safe, read-only helpers. No admin. No private-key / mnemonic printing. No public RPC.
# Local devnet is NEVER started from any QA script.

$ErrorActionPreference = "Stop"

function Get-QaPackageRoot {
    param([string]$ScriptDir)
    # qa/windows/<script> -> package root is two levels up.
    return (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
}

function Get-QaPython {
    param([string]$PackageRoot)
    # Prefer the bundled embedded Python shipped in the full ZIP; fall back to system python.
    $bundled = Join-Path $PackageRoot "runtime\python\python.exe"
    if (Test-Path $bundled) { return $bundled }
    foreach ($c in @("py", "python", "python3")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd) { if ($c -eq "py") { return "py" } else { return $cmd.Source } }
    }
    return "python"
}

function Get-QaDataDir {
    # Logs/reports go under the USER profile, never the install dir (Program Files may be read-only).
    if ($env:APPDATA) { $d = Join-Path $env:APPDATA "ACAP-Desktop-Node\qa" }
    else { $d = Join-Path $env:USERPROFILE ".acap-desktop-node\qa" }
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    return $d
}

function New-QaCheck {
    param([string]$Id, [string]$Label, [string]$Status, [string]$Detail = "", [string]$Fix = "")
    # Status is one of PASS / WARN / FAIL.
    return [pscustomobject]@{ id = $Id; label = $Label; status = $Status; detail = $Detail; fix = $Fix }
}

function Write-QaCheck {
    param($Check)
    $color = switch ($Check.status) { "PASS" { "Green" } "WARN" { "Yellow" } "FAIL" { "Red" } default { "Gray" } }
    Write-Host ("  [{0}] {1}: {2}" -f $Check.status, $Check.label, $Check.detail) -ForegroundColor $color
    if ($Check.status -ne "PASS" -and $Check.fix) {
        Write-Host ("         fix: {0}" -f $Check.fix) -ForegroundColor DarkYellow
    }
}

function Invoke-QaPython {
    # Run a package python module/command and return parsed JSON (or $null on failure).
    param([string]$Py, [string]$PackageRoot, [string]$Module, [string[]]$PyArgs = @())
    try {
        $script = Join-Path $PackageRoot $Module
        $raw = & $Py $script @PyArgs 2>$null
        if (-not $raw) { return $null }
        return ($raw | Out-String | ConvertFrom-Json)
    } catch { return $null }
}
