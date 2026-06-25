# Active Capacity Network - package verification (PowerShell, read-only).
# Confirms the expected files are present and prints each file's SHA-256 so you can
# compare against MANIFEST.json. Writes nothing. Needs no admin rights.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$required = @(
    "acn_node.py", "config.example.json", ".env.example",
    "README_WINDOWS.md", "NODE_ROLES.md", "SECURITY_AND_PRIVACY.md",
    "TROUBLESHOOTING_WINDOWS.md", "CHANGELOG.md", "VERSION.txt", "MANIFEST.json",
    "INSTALL_GUIDED.ps1", "INSTALL_GUIDED.bat", "VERIFY_PACKAGE.ps1",
    "RUN_DIAGNOSTICS.ps1", "CREATE_DESKTOP_SHORTCUT.ps1"
)
$missing = @()
foreach ($f in $required) {
    if (Test-Path (Join-Path $root $f)) { Write-Host ("  OK   {0}" -f $f) }
    else { Write-Host ("  MISS {0}" -f $f); $missing += $f }
}

# refuse to bless any stray .exe (preview ships none)
$exes = Get-ChildItem -Path $root -Filter *.exe -File -ErrorAction SilentlyContinue
if ($exes) { Write-Host ("  WARNING: unexpected .exe present: {0}" -f ($exes.Name -join ', ')) }
else { Write-Host "  OK   no .exe in package (portable preview)" }

Write-Host ""
Write-Host "MANIFEST cross-check tip: compute a file hash and compare to MANIFEST.json:"
Write-Host "  Get-FileHash .\acn_node.py -Algorithm SHA256"
Write-Host ""
if ($missing.Count -gt 0) {
    Write-Host ("Verification incomplete: {0} file(s) missing." -f $missing.Count)
    exit 1
}
Write-Host "Package verification OK."
exit 0
