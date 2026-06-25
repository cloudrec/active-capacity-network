# CHECK_ENVIRONMENT.ps1 - Windows + dependency environment for the ACAP local devnet.
# Read-only. Reports OS, PowerShell, Java (17+), Besu (+version), Docker (optional), port 8545.
# Never installs anything, never starts a node. Safe for a normal (non-admin) user.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$checks = @()

Write-Host "ACAP QA - environment / dependencies" -ForegroundColor Cyan

# OS + PowerShell (informational)
$os = try { (Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption } catch { $null }
if (-not $os) { $os = [System.Environment]::OSVersion.VersionString }
$checks += New-QaCheck "os" "Operating system" "PASS" $os
$psv = $PSVersionTable.PSVersion.ToString()
$checks += New-QaCheck "powershell" "PowerShell version" "PASS" $psv

# Ask the node manager for the authoritative dependency report (version-aware).
$deps = Invoke-QaPython $py $pkg "acap_node_manager.py" @("deps")
if ($null -eq $deps) {
    $checks += New-QaCheck "deps_probe" "Dependency probe (acap_node_manager.py deps)" "FAIL" `
        "could not run the Python dependency probe" `
        "Ensure the full ZIP is extracted (runtime/python/python.exe present) or install Python 3."
} else {
    foreach ($it in $deps.items) {
        $status = if ($it.ok) { "PASS" } elseif ($it.id -eq "docker") { "WARN" } else { "FAIL" }
        $checks += New-QaCheck $it.id $it.label $status $it.detail ([string]$it.fix)
    }
    if ($deps.blocked_by_server) {
        $checks += New-QaCheck "server_guard" "Server/shared-host guard" "WARN" `
            "this host is flagged as a server - local devnet start is refused here (expected on servers)"
    }
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "environment"; checks = $checks }
