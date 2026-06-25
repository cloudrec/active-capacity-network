@echo off
REM ACAP Desktop Node - wallet-like local shell (private preview, devnet/testnet only).
REM Opens a LOCAL web UI on 127.0.0.1 only. No mainnet, no rewards, no key upload.
setlocal
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required. Install from https://www.python.org/downloads/ ^(check "Add to PATH"^).
  pause
  exit /b 1
)
echo Starting ACAP Desktop Node (local UI on http://127.0.0.1:8599 )...
python "%~dp0acap_desktop.py" --port 8599
pause
