# Windows Install (Bootstrap Installer)

> **Preview installer.** Per-user, no admin, HTTPS-only, SHA-256 verified, loopback
> only. No mainnet, no rewards, no custody. Never prints/stores keys or mnemonics.

Scripts: [`../installers/windows/`](../installers/windows/).

## What the installer guarantees

- **Per-user** install under `%LOCALAPPDATA%\ACAP-Desktop-Node` — **no
  administrator rights** required (it warns if you run it elevated).
- **Never** edits the global/persistent PATH; installs **no** service or autostart.
- **HTTPS-only** downloads — non-HTTPS URLs are refused.
- **SHA-256 verified** — every downloaded archive's hash is checked before it is
  extracted or run; a mismatch aborts the install.
- **Devnet/testnet only** — loopback RPC, no mainnet, no rewards, no mining, no
  custody.
- **Never** prints or stores private keys or mnemonics.

## Install

1. Download `ACAP_INSTALL.bat` and `ACAP_INSTALL.ps1` (and verify their SHA-256 —
   see [VERIFY_RELEASES.md](VERIFY_RELEASES.md)).
2. Double-click `ACAP_INSTALL.bat` (it calls the PowerShell script with a safe
   policy). Do **not** "Run as administrator".
3. The installer fetches the ACAP package metadata over HTTPS, verifies the package
   SHA-256, and installs under your user profile. It can also fetch a portable JDK
   and Hyperledger Besu (each verified when a checksum is available).

### Options (advanced)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\ACAP_INSTALL.ps1 `
  -PortalBase https://capacity.469diamond.com `
  -JavaFeature 25 `
  -NoStart
```

- `-PortalBase` — package metadata source (HTTPS).
- `-ForceJava` — always fetch the bundled JDK.
- `-NoStart` — don't launch the node after install.

## Uninstall

Run `ACAP_UNINSTALL.bat` (or `ACAP_UNINSTALL.ps1`). It removes the per-user install
tree. Because nothing was added to PATH and no service was installed, removal is
clean.

## After install

The installer writes per-user runtime pointers (`acap-install-env.json` /
`acap-install-env.ps1`) and an install report. RPC stays loopback-only and public
P2P stays disabled.

See `installers/windows/README_INSTALLER.md` for details.
