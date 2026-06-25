# Local Private Devnet Guide

> **NON-PRODUCTION / LAB ONLY.** Single-validator QBFT devnet, **loopback only**,
> **P2P disabled**. No mainnet, no rewards, no mining, no custody, no real funds.

Materials: [`../devnet/`](../devnet/).

## What this is

A one-click **local private** Ethereum-style devnet using **Hyperledger Besu**
QBFT, chain id **469469**, with a **single validator** (QBFT quorum of 1, so one
process produces blocks alone — `peers = 0` is normal and correct).

## Safety properties

- **Loopback only.** RPC binds `127.0.0.1:8545`; host allowlist is `127.0.0.1`.
  Never expose RPC publicly.
- **P2P disabled.** `p2p-enabled=false` — no listener on `0.0.0.0`, port `30303` is
  never opened on any interface.
- **Lab keys only.** Keys here are fresh lab keys — not user wallet keys and not
  any production chain's keys. See `devnet/WARNINGS_NON_PRODUCTION_KEYS.txt`.

## The validator key is NOT shipped — generate your own

For safety, this repository ships only:

- `devnet/validators/validator-1/address` — the lab validator address (public),
- `devnet/validators/validator-1/key.pub` — the public key,
- `devnet/validators/validator-1/key.example` — a **placeholder** (not a real key).

You must generate your **own** fresh lab node key before starting Besu. With Besu
installed:

```bash
# Generate a fresh node key (writes 'key' and 'key.pub' next to the data path)
besu --data-path=./devnet/validators/validator-1 public-key export-address \
     --to=./devnet/validators/validator-1/address
```

or generate any 32-byte secp256k1 private key and save it (hex, `0x`-prefixed) as
`devnet/validators/validator-1/key`. The file `key` is **git-ignored** so you never
accidentally commit it.

> If you change the key, the validator **address** changes, so the `extraData` in
> `genesis.json` (which encodes the validator set) must be regenerated to match.
> For a quick single-node lab, generate the key first, derive its address, then
> rebuild the QBFT genesis with that address.

## Requirements

- **Hyperledger Besu** (Windows uses `besu.bat`).
- **Java 17+** (Besu 26.x may prefer Java 25).

## Start / stop / check (Windows)

Use the package-level scripts in `../desktop-node/` (they refuse to run on a server
and reject non-loopback RPC):

- `START_LOCAL_DEVNET.bat` / `.ps1`
- `STOP_LOCAL_DEVNET.bat` / `.ps1`
- `CHECK_LOCAL_DEVNET.bat` / `.ps1`

The raw Besu invocation is documented in `devnet/scripts/start-devnet.ps1`:

```
besu --data-path=%USERPROFILE%\.acap-devnet --genesis-file=.\genesis.json \
     --node-private-key-file=.\validators\validator-1\key --config-file=.\config.toml
```

Chain data is written under `%USERPROFILE%\.acap-devnet`, never into the repo.

## Files

- `genesis.json` — QBFT genesis (chainId 469469; validators encoded in `extraData`).
- `config.toml` — Besu config: loopback RPC, P2P disabled, min-gas-price 0.
- `static-nodes.example.json` — optional multi-validator expansion (not needed for
  one node).
- `manifest.json` / `sha256sums.txt` — file inventory + hashes.
- `WARNINGS_NON_PRODUCTION_KEYS.txt` — read this.

## Reminder

This devnet is for local experimentation only. It is **not** mainnet, **not**
rewards, **not** staking, **not** custody. Do not reuse lab keys anywhere public.
