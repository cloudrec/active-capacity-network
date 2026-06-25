# ACAP Desktop Node - Windows Bootstrap Installer

One double-click sets up the whole node: it downloads the ACAP package, a portable Java (JDK),
and Hyperledger Besu, verifies every download with SHA-256, installs everything under your user
profile, and starts the node. No admin rights. No manual PATH or folder work.

> PRIVATE PREVIEW. Devnet/testnet only. No mainnet, no rewards, no mining, no custody.
> The local RPC binds to `127.0.0.1` only and P2P is disabled.

## Use it
1. Download `ACAP_INSTALL.bat` (and `ACAP_INSTALL.ps1` next to it) from
   `https://capacity.469diamond.com` (Update / Info tab).
2. Double-click **ACAP_INSTALL.bat**.
3. Follow the prompts. When asked, type `YES` to start a local devnet (optional).

That is it. The node UI opens on `http://127.0.0.1:8599`.

## What it installs (per-user, no admin)
```
%LOCALAPPDATA%\ACAP-Desktop-Node\
  app\                ACAP.Node.exe + node scripts + bundled Python + web UI
  runtime\java\       portable Temurin JDK (only if you do not already have a suitable Java)
  runtime\besu\       Hyperledger Besu (only if you do not already have besu.bat)
  data\  logs\  downloads\
  acap-install-env.json / .ps1   runtime pointers (no global PATH change)
  install-report.json / .txt
```

## Options
Run from a PowerShell prompt for options:
```
powershell -NoProfile -ExecutionPolicy Bypass -File .\ACAP_INSTALL.ps1 -JavaFeature 25 -ForceJava -NoStart
```
- `-PortalBase <url>` - portal base (default `https://capacity.469diamond.com`).
- `-JavaFeature <n>` - Temurin JDK feature to fetch if Java is missing (default `25`; Besu 26.6.x needs 25).
- `-ForceJava` - download the bundled JDK even if a system Java is found.
- `-NoStart` - do not launch the node UI after install.
- Proxy: honors `HTTPS_PROXY` / `HTTP_PROXY`.

## Verify the downloads
The installer verifies SHA-256 itself:
- ACAP package against the portal metadata `sha256` (mismatch aborts the install).
- Java against the Adoptium API checksum.
- Besu against the release `.zip.sha256` sidecar (if the release ships one).

## Uninstall
Double-click **ACAP_UNINSTALL.bat** and type `YES`. It removes only
`%LOCALAPPDATA%\ACAP-Desktop-Node`. Add `-KeepData` to keep `data\`. A local devnet chain dir
under `%USERPROFILE%\.acap-devnet` (if any) is left untouched.

## Safety
HTTPS-only downloads. SHA-256 verified before extract/run. No admin. No global PATH edit. No
service or autostart. Loopback-only RPC. P2P disabled. Never selects the unix `besu` script over
`besu.bat`. Never prints private keys or mnemonics. No mainnet / rewards / custody claims.
