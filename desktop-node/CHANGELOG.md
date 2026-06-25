# Changelog — Active Capacity Windows Preview Node

## 0.5.2-psfix-preview - 2026-06-25
- **Bugfix (Windows PowerShell 5.1 ParserError):** all shipped `.ps1`/`.bat` scripts are now
  **pure ASCII**. The previous build embedded a non-ASCII dash that Windows PowerShell 5.1
  mis-decoded on non-English locales (e.g. Russian/CP1251) into mojibake, breaking string
  parsing (`Unexpected token`, `Missing closing ')'`, `value expression following '+'`).
- Added static guards: `scripts/check_powershell_syntax_static.py` and
  `scripts/check_bat_launchers.py` (run in the build + test suite).
- `.bat` launchers now print the script path being launched. No behaviour change; still
  loopback-only, no mainnet, no rewards, no custody, unsigned.

## 0.2.0-preview — 2026-06-25
- **ACAP Desktop Node shell** (`acap_desktop.py` + `web/index.html`,
  `START_ACAP_DESKTOP.bat` / `.ps1`): wallet-like local app. Binds **127.0.0.1 only**.
  Tabs: Home/Status, Wallet, Network, Node logs, Diagnostics, Update/Info.
- **Local wallet / key manager** (`acap_wallet.py`): create / unlock / encrypted
  backup / restore / address. Encryption is **stdlib-only** (scrypt KDF +
  HMAC-SHA256 keystream + Encrypt-then-MAC, constant-time tag compare). Keys are
  generated and stored **locally only**; the seed is never uploaded or logged.
  Deterministic self-test: `python acap_wallet.py selftest`.
- **Local node manager** (`acap_node_manager.py`): honest runtime detection +
  status states (offline / bundled_runtime_missing / external_besu_detected /
  devnet_config_ready / start_disabled_until_runtime / connected_local_devnet).
  Start is **refused on servers** and gated on a local lab config + runtime.
  Local RPC probe refuses non-loopback URLs (no public RPC).
- Devnet/testnet identity only — **no public mainnet, no rewards/mining/staking,
  no custody, no faked EXE.** Still a portable ZIP.

## 0.1.1-preview — 2026-06-24
- Added **guided setup wizard**: `INSTALL_GUIDED.bat` / `INSTALL_GUIDED.ps1`.
  Transparent, cancelable, no admin rights. Picks node mode, sets API base URL,
  verifies files, shows `config.json` before writing it, optional opt-in desktop
  shortcut, optional read-only diagnostics. Writes no secrets and no keys.
- Added helper scripts: `VERIFY_PACKAGE.ps1` (read-only file/hash check),
  `RUN_DIAGNOSTICS.ps1` (read-only API + node diagnostics),
  `CREATE_DESKTOP_SHORTCUT.ps1` (opt-in shortcut, no autostart).
- README updated with guided + manual quick starts.
- Still a portable ZIP. **No signed EXE, no faked binary.** No mining, no rewards,
  no background service, no autostart by default.

## 0.1.0-preview — 2026-06-24
- Initial portable Windows ZIP.
- Read-only preview node client (`acn_node.py`, standard library only).
- Commands: status, run (light/capacity/validator-preview), register, diagnostics, version.
- Batch launchers + PowerShell health check.
- Docs: README, NODE_ROLES, SECURITY_AND_PRIVACY, TROUBLESHOOTING, this changelog.
- No mining, no rewards, no background service, no autostart, no keys, no secrets.
- Not a signed installer; SHA-256 checksum published alongside the ZIP.
