# Active Capacity Network - optional desktop shortcut (opt-in, PowerShell).
# Creates a single shortcut on YOUR desktop that runs CHECK_STATUS.bat (read-only
# status check). Opt-in only. No autostart, no startup-folder entry, no admin rights.
# Delete the shortcut anytime to remove it.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$target = Join-Path $root "CHECK_STATUS.bat"
if (-not (Test-Path $target)) { Write-Host "CHECK_STATUS.bat not found; aborting."; exit 1 }

$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = Join-Path $desktop "Active Capacity - Status Check.lnk"

try {
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($lnkPath)
    $lnk.TargetPath = $target
    $lnk.WorkingDirectory = $root
    $lnk.Description = "Active Capacity Network - read-only status check (private preview)"
    $lnk.Save()
    Write-Host ("Created shortcut: {0}" -f $lnkPath)
    Write-Host "This shortcut only runs a read-only status check. It does NOT auto-start anything."
} catch {
    Write-Host ("Could not create shortcut: {0}" -f $_.Exception.Message)
    exit 1
}
