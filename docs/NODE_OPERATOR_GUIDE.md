# Node Operator Guide

> **Preview node.** Read-only by default. No mining, no rewards, no autostart,
> holds no keys by default, binds to `127.0.0.1` only. No mainnet.

The ACAP Desktop Node source lives in [`../desktop-node/`](../desktop-node/).

## Node roles

- **Light node** — polls public-safe status from the preview portal; read-only.
  Launchers: `START_LIGHT_NODE.bat`, `START_CAPACITY_NODE.bat`.
- **Desktop node** — local desktop shell + web UI on `127.0.0.1`.
  Launchers: `START_ACAP_DESKTOP.bat` / `.ps1`.
- **Local devnet validator** — only via the loopback QBFT devnet (see
  [DEVNET_GUIDE.md](DEVNET_GUIDE.md)). Requires Besu + Java.

See `desktop-node/NODE_ROLES.md` for the full breakdown.

## What it does and does not do

- ✅ Runs locally, read-only, on loopback.
- ✅ Optional local wallet code is local-only; private keys/seeds are **never**
  printed or logged (only the public `0x` address is shown).
- ❌ No public RPC, no mining, no rewards, no autostart, no admin rights.

## Requirements

- **Windows** for the packaged launchers and installer.
- **Python 3** for the stdlib node (`acap_desktop.py`). The full release ZIP can
  bundle an embedded Python; this source tree expects a system Python 3.
- **Besu + Java 17+** only if you want the local devnet.

## Run (Windows, from source)

1. Open [`../desktop-node/`](../desktop-node/).
2. Read `README_FIRST_RUN_WINDOWS.md` and `README_DESKTOP_NODE.md`.
3. Start a launcher:
   - Light/read-only: `START_LIGHT_NODE.bat`
   - Desktop shell + UI: `START_ACAP_DESKTOP.bat`
4. The web UI opens on `http://127.0.0.1:<port>` (loopback only).

## Run the Python node directly

```bash
python3 desktop-node/acap_desktop.py
```

It boots on `127.0.0.1` only and serves `desktop-node/web/index.html`.

## QA / diagnostics

Read-only Windows QA scripts are in `desktop-node/qa/windows/` (e.g.
`RUN_FULL_QA.bat`, `CHECK_ENVIRONMENT.ps1`). They never create wallets and never
print keys/seeds/passwords. `COLLECT_DIAGNOSTICS.ps1` excludes wallet files,
private keys, seeds, mnemonics, and passwords.

## Configuration

Copy the examples and edit locally (never commit real values):

- `desktop-node/config.example.json` → `config.json`
- `desktop-node/.env.example` → `.env`
- `desktop-node/lab_config.example.json` → `data/lab_config.json` (lab machine
  only; enables local devnet status — never on a server).

## Troubleshooting

See `desktop-node/TROUBLESHOOTING_WINDOWS_NODE.md` and
`desktop-node/TROUBLESHOOTING_WINDOWS.md`.
