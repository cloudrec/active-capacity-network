# Security Policy

## Status of this project

Active Capacity Network is a **private preview / prototype**. There is **no public
mainnet, no token sale, no custody, no bridge, no payments, and no live rewards**.
Nothing in this repository moves real value. Treat all chain-style data as
demonstration data.

## Scope

In scope for reports:

- The **ACAP Desktop Node** source (`desktop-node/`).
- The **Windows bootstrap installer** (`installers/windows/`).
- The **local devnet** materials (`devnet/`).
- The **safety scripts** (`scripts/`).
- Any secret, private key, credential, or production config that you believe was
  published in this repo by mistake.

Out of scope:

- The hosted preview website and any production backend (not part of this repo).
- Social-engineering, physical, or DoS testing.

## Reporting a vulnerability

Please report security issues **privately**. Do not open a public issue for
anything that could expose users or secrets.

- Use GitHub's **"Report a vulnerability"** (Security advisories) on this repo, or
- Open a minimal private channel with the maintainers referencing
  `cloudrec/active-capacity-network`.

Include: affected file/path, a description, reproduction steps, and impact. Please
allow a reasonable time for a fix before any public disclosure.

## Handling keys and secrets

- This repo must **never** contain real private keys, mnemonics, `.env` files,
  admin credentials, API tokens, or database dumps.
- The devnet ships a **placeholder** validator key (`key.example`) only. Generate
  your own fresh lab key locally — see `docs/DEVNET_GUIDE.md`.
- The desktop node and installer are designed to **never print or store** private
  keys or seed phrases, and to bind RPC to `127.0.0.1` only.
- If you find a leaked secret, report it privately and we will rotate/remove it.

## Safety checks

Automated checks run in CI (`.github/workflows/checks.yml`) and can be run locally:

```bash
python3 scripts/check_no_secrets.py
python3 scripts/check_claims.py
python3 scripts/verify_release.py
```

They fail the build on private-key patterns, `.env` content, credentials, and
unsafe "mainnet/rewards/custody/trading is live" claims.
