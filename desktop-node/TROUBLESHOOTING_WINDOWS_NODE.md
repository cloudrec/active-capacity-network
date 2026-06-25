# Troubleshooting — ACAP Desktop Node (Windows)

Private preview, devnet/testnet only. No mainnet, no rewards, no public RPC. When in doubt run
`qa\windows\RUN_FULL_QA.bat` and read `qa-report.txt`.

---

### SmartScreen / "Windows protected your PC"
The EXE is an **unsigned** preview build, so SmartScreen warns. After verifying the SHA-256
(`Get-FileHash`), click *More info → Run anyway*. A signed build is on the roadmap.

### "ACAP.Node.exe was blocked" / antivirus quarantine
Unsigned self-contained .NET apps are sometimes flagged heuristically. Verify the SHA-256
matches the portal, then allow it. If unsure, do not run it.

### App opens then the window closes immediately
Run it from a terminal to see the message:
```
.\ACAP.Node.exe
```
- *"No Python runtime was found"* → you ran the **standalone** EXE without Python. Use the full
  ZIP (it bundles Python), or install Python 3 and tick *Add to PATH*.
- *"could not locate or extract the ACAP node files"* → re-extract the full ZIP; keep files
  together.

### PowerShell: "running scripts is disabled on this system"
Use the `.bat` launchers (they pass `-ExecutionPolicy Bypass` for that one process), or run:
```
powershell -NoProfile -ExecutionPolicy Bypass -File .\qa\windows\RUN_FULL_QA.ps1
```
This does not change any system-wide setting.

### Browser does not open / "can't reach this page"
The UI is at `http://127.0.0.1:8599/`. Open it manually. If the port is busy, start with a
different port:
```
.\ACAP.Node.exe --port 8600
```

### Java not detected
`java -version` must report **17 or higher** in a **new** terminal. If it says "not recognized",
Java is not on PATH — reinstall Temurin with *Add to PATH* (see
ACAP_WINDOWS_DEPENDENCY_INSTALL_GUIDE.md). If it reports `1.8` or `11`, that is too old.

### Besu not detected
- Unzip Besu to `%USERPROFILE%\besu` (so `%USERPROFILE%\besu\bin\besu.bat` exists) — the app
  auto-detects `~/besu/bin`.
- Or add `%USERPROFILE%\besu\bin` to PATH and verify with `besu --version` in a new terminal.

### START_LOCAL_DEVNET says "Not ready to start" / lists blockers
Read the blockers — usually `besu_runtime_missing` or `java_missing`. Install them, re-open the
**Dependencies** tab (or run `CHECK_ENVIRONMENT.ps1`) until Java + Besu + port 8545 are all PASS.

### START_LOCAL_DEVNET says "REFUSED: server environment"
The machine is flagged as a server (`SERVER_DO_NOT_START` marker or `ACAP_SERVER=1`). The devnet
intentionally never starts on a server/shared host. Use a normal desktop/lab machine.

### Port 8545 already in use
```
netstat -ano | findstr :8545
```
Stop the process on that PID, or run `STOP_LOCAL_DEVNET.bat` if a previous devnet is still up.

### CHECK_LOCAL_DEVNET shows "not connected"
The devnet is not running yet. Start it with `START_LOCAL_DEVNET.bat` first, wait a few seconds,
then check again. `peer_count = 0` on a single-validator devnet is normal.

### Block height does not change
Give it ~10–15 seconds and run `CHECK_LOCAL_DEVNET.bat` again. A fresh QBFT single-validator
chain produces blocks on a short interval; the height should increase between checks.

### Wallet password lost
There is no recovery and no server copy — by design. Create a new wallet (a lost devnet wallet
holds no real funds).

---

## Collect diagnostics to report a problem
```
qa\windows\COLLECT_DIAGNOSTICS.ps1
```
Writes `%APPDATA%\ACAP-Desktop-Node\qa\acap-diagnostics-<timestamp>.txt` — **no private keys,
seeds, or passwords are included**. Send that file plus screenshots to the maintainer.
