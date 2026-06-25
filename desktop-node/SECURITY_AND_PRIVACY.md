# Security & Privacy — Active Capacity Preview Node

## What this package contains
Plain-text scripts (`.bat`, `.ps1`), one Python file (`acn_node.py`), example config, and docs.
**No secrets, no admin passwords, no private keys, no `.env` with credentials, no tokens.**
You can read every file before running it.

## Network behaviour
- Makes **outbound HTTPS GET** requests to public endpoints on `capacity.469diamond.com`
  (and optionally `auction.469diamond.com`) only.
- Sends nothing about your machine except, if **you** run `register`, a small node profile you
  can inspect at `data/node_profile.json` (node name, OS family, your contact if you provide one).
- Opens **no inbound ports**, runs **no server**, installs **no service**.

## Keys & custody
- The client does **not** create or hold private keys. There is **no wallet, no custody**.
- It never asks for a seed phrase or password.

## Guided setup wizard (`INSTALL_GUIDED.ps1`)
- Transparent and cancelable. Needs **no administrator rights**.
- The only file it writes is a plain `config.json` (API base URL, role, node name, poll
  interval) — and it **shows that JSON and asks before writing it**. No secrets, no keys.
- A desktop shortcut is **opt-in only** and points at the read-only status check; it sets
  **no autostart and no startup-folder entry**. Delete the shortcut anytime to remove it.
- `VERIFY_PACKAGE.ps1` and `RUN_DIAGNOSTICS.ps1` are read-only and write nothing.

## Background processes & autostart
- The node runs **only in the foreground** while its window is open.
- It installs **no autostart, no scheduled task, no Windows service** by default.
- The guided wizard never installs a service. Any future opt-in service install would require
  your explicit confirmation.

## Logs & diagnostics
- Logs are local only (`logs/node.log`).
- `diagnostics` bundles status + environment + local logs + your local profile into a ZIP you
  choose to share. It includes **no secrets** and does not read unrelated files.

## Verifying integrity
- Verify the ZIP SHA-256 against the published `.sha256` file before unzipping:
  `certutil -hashfile active-capacity-node-windows.zip SHA256`.
- The package is currently **unsigned**. Windows SmartScreen may warn — this is expected for an
  unsigned preview. Code-signing is a future step (see `WINDOWS_NODE_PACKAGE.md`).

## Reminder
Private preview / prototype. No mainnet, no real custody, no payments, no bridge, no rewards.
