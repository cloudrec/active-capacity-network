@echo off
REM ACAP Desktop Node - one-click Windows bootstrap installer launcher (private preview).
REM Per-user install under %LOCALAPPDATA%. No admin rights. No global PATH edit. No autostart.
REM Devnet/testnet only: no mainnet, no rewards, no mining, no custody, loopback RPC only.
where powershell >nul 2>nul || (echo PowerShell not found. Install Windows PowerShell 5.1. & pause & exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ACAP_INSTALL.ps1" %*
echo.
echo Done. See %LOCALAPPDATA%\ACAP-Desktop-Node\install-report.txt for details.
pause
