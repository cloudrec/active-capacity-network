# ACAP Local Private Devnet — Bootstrap Bundle (NON-PRODUCTION LAB ONLY)

This bundle lets a lab/desktop machine start a **local private QBFT devnet**
(chain id `469469`) with one click, **when Besu + Java (17+) are installed**.

* **NON-PRODUCTION / LAB ONLY.** Validator keys here are fresh lab keys, not user
  wallet keys and not the production chain's keys. See `WARNINGS_NON_PRODUCTION_KEYS.txt`.
* **Loopback only.** RPC binds `127.0.0.1:8545`; host allowlist is `127.0.0.1`.
  No public RPC, ever.
* **P2P DISABLED.** A single validator needs no peers, so P2P/discovery are turned off
  (`p2p-enabled=false`) — port 30303 is never opened on any interface. `peers = 0` is
  expected and correct. (This replaces the old `p2p-host="127.0.0.1"`, which only set the
  *advertised* host and still left the listener on `0.0.0.0:30303`.)
* **No mainnet, no rewards, no mining, no custody, no real funds.**
* **1 lab validator** — a single Besu process produces blocks alone (QBFT quorum of 1),
  which is what makes the local devnet truly one-click. `peers = 0` is normal.

## Files
* `genesis.json` — QBFT genesis (chainId 469469, validators encoded in `extraData`).
* `config.toml` — Besu config: loopback RPC, **P2P disabled** (loopback interface), min-gas-price 0.
* `validators/validator-N/key` — LAB validator private key (Besu node-key format).
* `static-nodes.example.json` — optional multi-validator expansion (not needed for one node).
* `manifest.json` / `sha256sums.txt` — file inventory + hashes.

## Start / Stop / Check
Use the package-level scripts (they refuse to run on a server and reject non-loopback RPC):
* `START_LOCAL_DEVNET.bat` / `.ps1`
* `STOP_LOCAL_DEVNET.bat` / `.ps1`
* `CHECK_LOCAL_DEVNET.bat` / `.ps1`

Chain data is written under your user profile (`%USERPROFILE%\.acap-devnet`), never
into the install folder.
