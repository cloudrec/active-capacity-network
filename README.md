# Active Capacity Network (ACAP)

> **Private preview / prototype.** No public mainnet. No live rewards. No custody.
> No bridge. No trading. No public token sale. Tokenomics are a **preview**. All
> chain-style data shown anywhere in this project is demonstration data and is
> clearly labeled. Nothing here moves real value.

**Active Capacity Network (ACN)** is a protocol concept for **moving, project-bound
capacity** — network capacity that is allocated to approved projects, moved, and
whose activity is tracked and provable. The token unit is **ACAP**. The consensus
idea is **Proof of Active Capacity (PoAC)**: selection by stake, uptime, activity,
and reputation — no Proof of Work.

This repository is the **public preview package**: node source, a Windows
bootstrap installer, a local devnet, a tokenomics preview, and operator docs. It
exists to be transparent about what the project is — and, just as importantly,
what it is **not** yet.

---

## What ACAP is

- A **design + working prototype** of a capacity protocol (PoAC), with ACAP as the
  internal capacity/utility unit.
- A **desktop node** you can read, build, and run **locally** (loopback only).
- A **local private devnet** (single-validator QBFT) for experimentation.
- A **preview tokenomics** registry with a fixed hard cap and everything disabled.

## Current status

| Area | Status |
|------|--------|
| Public mainnet | ❌ not live |
| Token sale / reservation | ❌ disabled (`sale_active=false`, `reservation_active=false`) |
| On-chain contract | ❌ none deployed (no contract address) |
| Rewards / staking yield | ❌ not live |
| Custody / bridge / payments / trading | ❌ not live |
| Desktop node (local, read-only) | ✅ source here |
| Local private devnet (loopback) | ✅ materials here |
| Tokenomics preview | ✅ `tokenomics/` (preview only) |

## Windows node preview

The **ACAP Desktop Node** is a local, read-only-by-default node:

- No mining, no rewards, no autostart, holds no keys by default.
- Binds to `127.0.0.1` only; never exposes a public RPC.
- Source: [`desktop-node/`](desktop-node/) (Python node + web UI + Windows
  launchers + QA scripts + .NET launcher source).

See [docs/NODE_OPERATOR_GUIDE.md](docs/NODE_OPERATOR_GUIDE.md).

## One-click installer

The Windows **bootstrap installer** ([`installers/windows/`](installers/windows/)):

- **Per-user** install under `%LOCALAPPDATA%` — **no administrator rights**.
- **Never** edits the global PATH; installs no service / autostart.
- **HTTPS-only** downloads; **every** archive's **SHA-256 is verified** before use.
- Devnet/testnet only: no mainnet, no rewards, loopback RPC only.
- Never prints or stores private keys or mnemonics.

See [docs/WINDOWS_INSTALL.md](docs/WINDOWS_INSTALL.md).

## Local devnet

A **local, private** QBFT devnet (chainId `469469`), single validator, in
[`devnet/`](devnet/):

- **Loopback only** — RPC binds `127.0.0.1:8545`; host allowlist `127.0.0.1`.
- **P2P disabled** — no listener on `0.0.0.0`, port `30303` never opened.
- **NON-PRODUCTION lab keys only.** The real key is **not** shipped — generate your
  own; the repo ships a `key.example` placeholder.
- No mainnet, no rewards, no mining, no custody, no real funds.

See [docs/DEVNET_GUIDE.md](docs/DEVNET_GUIDE.md).

## Tokenomics preview

[`tokenomics/acap_tokenomics.json`](tokenomics/acap_tokenomics.json) — preview only:

- **Max supply:** 1,000,000,000 ACAP — **fixed hard cap, no unlimited mint**.
- **Decimals:** 18.
- `sale_active=false`, `reservation_active=false`, `available_for_reservation=0`.
- `contract_deployed=false`, `contract_address=null`.
- **Active Capacity Reservation** model: no fixed term, no forced expiration; ACAP
  remains the holder's. Pricing tiers are a capacity mechanism, **not** an
  investment promise.

See [tokenomics/README.md](tokenomics/README.md) and
[docs/ACAP_TOKENOMICS.md](docs/ACAP_TOKENOMICS.md).

## How to verify downloads

Every released artifact is published with a **SHA-256**. Always verify before
running:

```powershell
Get-FileHash .\active-capacity-node-windows.zip -Algorithm SHA256
```

```bash
sha256sum active-capacity-node-windows.zip
```

Compare against the published checksum. See
[docs/VERIFY_RELEASES.md](docs/VERIFY_RELEASES.md) and
`scripts/verify_release.py`.

## How to run a local node

1. Read [docs/NODE_OPERATOR_GUIDE.md](docs/NODE_OPERATOR_GUIDE.md).
2. (Windows) run a launcher under `desktop-node/`, e.g. `START_LIGHT_NODE.bat` —
   read-only, loopback only.
3. (Optional) bring up the local devnet per [docs/DEVNET_GUIDE.md](docs/DEVNET_GUIDE.md)
   after installing Besu + Java and generating your own lab key.

## Roadmap

See [ROADMAP.md](ROADMAP.md). Every value-bearing milestone (testnet, contract,
any distribution) is **gated** behind legal, security, and governance review and
is **not live** today.

## Safety disclaimer

This is a preview/prototype, **not** a financial product and **not** investment
advice. No mainnet, sale, custody, bridge, payments, trading, or live rewards
exist. Numbers and design may change and are versioned in the changelog. Full
statement: [docs/DISCLAIMERS.md](docs/DISCLAIMERS.md).

## Repository layout

```
active-capacity-network/
├── README.md / LICENSE / NOTICE / SECURITY.md / CONTRIBUTING.md
├── CODE_OF_CONDUCT.md / ROADMAP.md / CHANGELOG.md
├── docs/                 # public docs (overview, tokenomics, node, devnet, FAQ…)
├── tokenomics/           # preview tokenomics JSON + README
├── desktop-node/         # ACAP Desktop Node source (py, web, launchers, qa, dotnet)
├── installers/windows/   # one-click bootstrap installer (per-user, no admin)
├── devnet/               # local private devnet (loopback, lab key placeholder)
├── scripts/              # safety scans + release verifier
└── .github/              # CI checks, issue/PR templates
```

## License

[Apache-2.0](LICENSE). Copyright (c) 2026 Active Capacity Network / Andrey Pecherskiy.
