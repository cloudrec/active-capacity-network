# Changelog

All notable changes to the public Active Capacity Network preview package are
documented here. This project is a **private preview / prototype**; versions track
the public materials, not a live mainnet.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0-preview] — 2026-06-25

### Added
- Initial public preview package for **Active Capacity Network (ACAP)**.
- `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ROADMAP.md`.
- Public docs set under `docs/` (overview, tokenomics, reservation model, node
  operator guide, Windows install, devnet guide, FAQ, disclaimers, release verify).
- Tokenomics preview: `tokenomics/acap_tokenomics.json` (v0.2.0-preview) + README.
  Max supply 1,000,000,000 ACAP, 18 decimals, hard cap (no unlimited mint),
  `sale_active=false`, `reservation_active=false`, no contract deployed.
- ACAP Desktop Node **source** (`desktop-node/`): Python node, web UI, Windows
  launchers, QA scripts, and the .NET launcher source.
- Windows **bootstrap installer** scripts (`installers/windows/`).
- Local **private devnet** materials (`devnet/`): QBFT genesis (chainId 469469),
  loopback-only config, NON-PRODUCTION lab key **placeholder** (real key excluded).
- Safety tooling (`scripts/`): secret scan, claim scan, release verifier.
- CI checks and GitHub issue/PR templates (`.github/`).

### Excluded (intentionally, for safety)
- `.env`, admin credentials, database files, private keys, real validator keys.
- Production backend, server/nginx configs, build binaries, embedded runtimes.

[0.1.0-preview]: https://github.com/cloudrec/active-capacity-network/releases/tag/v0.1.0-preview
