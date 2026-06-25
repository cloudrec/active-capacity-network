# ACAP Desktop Node — First Run on Windows

Private preview. **Devnet/testnet only — no mainnet, no rewards, no mining, no custody, no
public RPC, ACAP is not tradable.** Unsigned preview build: verify the SHA-256 before running.

## 1. Verify the download (recommended)

In PowerShell, in the folder where the ZIP is:
```
Get-FileHash .\active-capacity-node-windows.zip -Algorithm SHA256
```
Compare the hash to the one published on the portal node page
(`/api/node-packages/windows/checksum`). They must match.

## 2. Extract

Right-click the ZIP → **Extract All…** → pick a normal folder (e.g. your Desktop or Documents).
**Keep all files together** — do not drag `ACAP.Node.exe` out on its own. The full ZIP bundles
its own Python, so you do **not** need to install Python.

## 3. Run the app

Double-click **`ACAP.Node.exe`** (or `START_ACAP_DESKTOP.bat`). It opens a local web UI on
`http://127.0.0.1:8599/` — loopback only, not reachable from your network.

- Windows SmartScreen may warn because the EXE is **unsigned** (expected for this preview).
  Choose *More info → Run anyway* only after you verified the SHA-256 in step 1.

## 4. Create a wallet

In the UI: **Wallet** tab → set a password → *Create*. The key is generated and encrypted on
**this machine only** (scrypt + HMAC-SHA256). It is never uploaded. If you lose the password it
cannot be recovered — there is no server copy.

You can also create a **Besu / secp256k1** account (Ethereum-style 0x address) in the
**Besu wallet** tab. Devnet identity only — no funds, not mainnet.

## 5. (Optional) Run the local devnet

This is the only part that needs extra software: **Java 17+ and Hyperledger Besu**.

1. Open the **Dependencies** tab — it shows Java / Besu / RPC port status with the exact fix
   command for anything missing.
2. Install what is missing — see **`..\..\docs` → ACAP_WINDOWS_DEPENDENCY_INSTALL_GUIDE.md**
   (also shipped in the package docs).
3. Start it: run **`START_LOCAL_DEVNET.bat`** (it asks for an explicit **YES**, binds
   `127.0.0.1` only, refuses to run on a server).
4. Check it: run **`CHECK_LOCAL_DEVNET.bat`** — it prints chain id (469469), block height, and
   peer count. A single-validator devnet shows `peer_count = 0` (normal); block height should
   rise over time.
5. Stop it: run **`STOP_LOCAL_DEVNET.bat`** (kills only the devnet it started).

## 6. Run the QA self-check (recommended)

Double-click **`qa\windows\RUN_FULL_QA.bat`**. It runs read-only checks (no devnet start, no
secrets printed) and writes `qa-report.txt` / `qa-report.json` to
`%APPDATA%\ACAP-Desktop-Node\qa\`. You want **OVERALL: PASS** (or **WARN** if Besu/Java are not
installed yet).

## If something goes wrong

See **`TROUBLESHOOTING_WINDOWS_NODE.md`** in this folder, then run
`qa\windows\COLLECT_DIAGNOSTICS.ps1` and send the resulting (secret-free) file plus screenshots
to the maintainer.
