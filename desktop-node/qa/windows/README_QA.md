# ACAP Desktop Node — Windows QA pack

Self-checks for the ACAP Desktop Node preview package. Everything here is **read-only and
safe for a normal (non-admin) user**. These scripts:

- never start the local devnet (they never produce blocks on their own);
- never create a wallet, never ask for or print a password / private key / seed / mnemonic;
- never contact a public or remote RPC (loopback `127.0.0.1` only);
- make no mainnet / rewards / mining / custody / trading claims;
- write logs/reports under your user profile, never the install folder.

## Quick start

1. Extract the full `active-capacity-node-windows.zip`.
2. Open the `qa\windows\` folder.
3. Double-click **`RUN_FULL_QA.bat`** (or run `RUN_FULL_QA.ps1` in PowerShell).

It writes two reports to `%APPDATA%\ACAP-Desktop-Node\qa\`:

- `qa-report.json` — machine-readable, one `PASS` / `WARN` / `FAIL` per check.
- `qa-report.txt` — human-readable summary with fix hints.

Overall result is `PASS` (no failures), `WARN` (only optional/soft issues, e.g. Besu not
installed yet), or `FAIL` (something required is broken).

## What each script checks

| Script | Checks |
|---|---|
| `RUN_FULL_QA.ps1` / `.bat` | Runs all checks below (except live devnet) and writes the report. |
| `CHECK_ENVIRONMENT.ps1` | OS, PowerShell, **Java 17+**, **Besu (+version)**, Docker (optional), RPC port 8545 free. |
| `CHECK_PACKAGE_LAYOUT.ps1` | `ACAP.Node.exe`, bundled Python, node modules, devnet bundle, START/STOP/CHECK scripts, chainId 469469. |
| `CHECK_WALLET.ps1` | ACAP wallet crypto self-test (deterministic vectors). |
| `CHECK_BESU_WALLET.ps1` | Keccak-256 + Besu secp256k1 / EIP-55 self-tests (canonical vectors). |
| `CHECK_DEVNET_BUNDLE.ps1` | Validates the NON-PRODUCTION devnet bundle + verifies `sha256sums.txt`. |
| `CHECK_LOCAL_DEVNET.ps1` | **After you start the devnet yourself**, probes loopback RPC for chain id / block height / peers. |
| `COLLECT_DIAGNOSTICS.ps1` | Writes a secret-free diagnostics file to send back with screenshots. |

## Checking a running devnet

The live-devnet check is **skipped by default** because it requires Java 17+ and Besu and a
devnet you started yourself. To include it:

```powershell
# 1) Install Java 17+ and Besu (see ..\..\docs equivalents / DEPENDENCY guide).
# 2) Start the devnet (asks for an explicit YES, loopback only):
..\..\START_LOCAL_DEVNET.bat
# 3) Re-run QA including the live check:
.\RUN_FULL_QA.ps1 -IncludeLiveDevnet
```

A single-validator devnet shows `peer_count = 0` — that is normal. Run the live check twice a
few seconds apart: the block height should increase.

## If something fails

1. Read the `fix:` hint next to the failing line in `qa-report.txt`.
2. For dependency issues, see **`README_FIRST_RUN_WINDOWS.md`**,
   **`ACAP_WINDOWS_DEPENDENCY_INSTALL_GUIDE.md`**, and **`TROUBLESHOOTING_WINDOWS_NODE.md`**
   in the package root.
3. Run `COLLECT_DIAGNOSTICS.ps1` and send the resulting file (it contains no secrets) plus
   screenshots to the maintainer.

## Execution policy note

If PowerShell blocks the scripts, the `.bat` launchers already pass
`-ExecutionPolicy Bypass` for the current process only (it does not change any system
setting). To run a `.ps1` directly you can use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_FULL_QA.ps1
```
