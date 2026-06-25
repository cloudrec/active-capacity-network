@echo off
REM ACAP local private-devnet runner - STOP (loopback only, lab machine only).
REM Private devnet/testnet ONLY. No mainnet, no rewards, no public RPC.
echo Launching: "%~dp0STOP_LOCAL_DEVNET.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0STOP_LOCAL_DEVNET.ps1" %*
pause
