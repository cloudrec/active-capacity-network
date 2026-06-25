# Active Capacity Network — Windows Preview Node

**Private preview / prototype. No mainnet, no custody, no payments, no bridge, no rewards.**
This package is a **portable Windows ZIP**, not a signed installer. It runs a small,
**read-only** preview node client that talks to the public Active Capacity / Auction APIs.

> Portable Windows ZIP delivered. A true `.exe` installer requires a Windows build/signing
> pass (see `WINDOWS_NODE_PACKAGE.md` in the site docs). Nothing here is faked.

## What this node does
- Connects to `https://capacity.469diamond.com` and shows live network status.
- Writes logs to `.\logs\`.
- Can save a **local node profile** and point you to the validator-apply form.
- Can export a diagnostics ZIP for support.

## What this node never does
- ❌ No mining. ❌ No staking. ❌ No rewards or income (there are none in preview).
- ❌ No hidden background processes. ❌ No autostart (unless *you* set one up explicitly).
- ❌ No private keys unless you generate them yourself. ❌ No scanning/transmitting your files.

## Requirements
- Windows 10/11.
- Python 3.9+ (https://www.python.org/downloads/ — tick "Add python.exe to PATH").
  The client uses the standard library only; **no `pip install` needed**.

## Quick start — guided setup wizard (recommended)
1. Unzip this folder anywhere (e.g. `C:\acn-node`).
2. Double-click **`INSTALL_GUIDED.bat`** (or run
   `powershell -ExecutionPolicy Bypass -File .\INSTALL_GUIDED.ps1`).
3. The wizard:
   - shows the private-preview warning and package version;
   - lets you pick a node mode (light / capacity / diagnostics-only);
   - lets you set the API base URL (default `https://capacity.469diamond.com`);
   - verifies the package files (`VERIFY_PACKAGE.ps1`);
   - **shows the `config.json` it will write and asks before writing it** (no secrets, no keys);
   - offers an **opt-in** desktop shortcut to the status check (no autostart);
   - offers to run a read-only diagnostics check.
   You can cancel at any prompt. It needs **no administrator rights**.

## Quick start — manual
1. Unzip this folder anywhere (e.g. `C:\acn-node`).
2. Double-click **`CHECK_STATUS.bat`** — confirms you can reach the network.
3. Double-click **`START_LIGHT_NODE.bat`** — runs the Light Node preview loop.
   Stop it any time with **Ctrl+C** or by closing the window.

## Helper scripts (all read-only / opt-in)
- **`INSTALL_GUIDED.bat` / `INSTALL_GUIDED.ps1`** — guided setup wizard (above).
- **`VERIFY_PACKAGE.ps1`** — list package files + hash tips; writes nothing.
- **`RUN_DIAGNOSTICS.ps1`** — read-only API + node diagnostics; writes nothing.
- **`CREATE_DESKTOP_SHORTCUT.ps1`** — opt-in desktop shortcut to the status check; no autostart.

## Roles (see `NODE_ROLES.md`)
- **Light Node** — recommended for everyone. Read-only status + sync view.
- **Capacity Node** — preview of the capacity-contribution role. Still read-only here.
- **Validator Node** — documentation + application path only; this client cannot self-approve.

## Commands (advanced)
```
python acn_node.py status          # one-shot status (default)
python acn_node.py run --role light
python acn_node.py register --contact you@example.com
python acn_node.py diagnostics     # writes acn-diagnostics-*.zip
python acn_node.py version
```

## Verify your download
Check the SHA-256 of the ZIP against `active-capacity-node-windows.zip.sha256`:
```
certutil -hashfile active-capacity-node-windows.zip SHA256
```

See `SECURITY_AND_PRIVACY.md`, `TROUBLESHOOTING_WINDOWS.md`, `NODE_ROLES.md`, `CHANGELOG.md`.
