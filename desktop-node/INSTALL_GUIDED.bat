@echo off
REM Active Capacity Network - Guided setup wizard launcher (private preview).
REM No admin rights required. No mining, no rewards, no autostart. You can cancel anytime.
where powershell >nul 2>nul || (echo PowerShell not found. See README_WINDOWS.md & pause & exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_GUIDED.ps1"
pause
