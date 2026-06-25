@echo off
REM RUN_FULL_QA.bat - double-clickable launcher for the ACAP Windows QA suite.
REM Read-only. Does NOT start the local devnet. No admin required. No secrets printed.
REM Reports are written to %APPDATA%\ACAP-Desktop-Node\qa\ (qa-report.json / qa-report.txt).
setlocal
echo Running ACAP Windows QA suite (read-only, no devnet start)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_FULL_QA.ps1" %*
echo.
echo QA finished. See the qa-report.txt / qa-report.json path printed above.
pause
endlocal
