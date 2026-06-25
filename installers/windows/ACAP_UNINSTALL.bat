@echo off
REM ACAP Desktop Node - per-user uninstaller launcher (private preview).
REM Removes ONLY %LOCALAPPDATA%\ACAP-Desktop-Node after an explicit YES. No admin needed.
where powershell >nul 2>nul || (echo PowerShell not found. & pause & exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ACAP_UNINSTALL.ps1" %*
pause
