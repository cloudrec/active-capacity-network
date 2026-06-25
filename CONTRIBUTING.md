# Contributing to Active Capacity Network

Thanks for your interest. This repository is the **public preview** of the Active
Capacity Network (ACAP): node source, installer, local devnet, tokenomics preview,
and docs. It is a prototype — please keep contributions consistent with that
status (no claims of a live mainnet, sale, or rewards).

## Ground rules

1. **Never commit secrets.** No `.env`, private keys, mnemonics, real validator
   keys, admin credentials, API tokens, or database dumps. CI will reject them.
2. **No false claims.** Do not state or imply that mainnet, custody, a bridge,
   trading, payments, or live rewards exist. Use "preview / planned / prototype".
3. **No fake contract address** and **no Buy button / live sale** wording.
4. **Loopback only for devnet.** Sample configs must keep RPC on `127.0.0.1` and
   keep public P2P disabled.
5. Keep all project communication in **English**.

## Workflow

1. Fork and create a feature branch: `git checkout -b feat/short-description`.
2. Make your change. Keep diffs focused.
3. Run the safety checks locally before pushing:
   ```bash
   python3 scripts/check_no_secrets.py
   python3 scripts/check_claims.py
   python3 scripts/verify_release.py
   ```
4. Open a Pull Request using the template. Describe what changed and why.

## Commit style

- Short, imperative subject (≤ ~72 chars), e.g. `docs: clarify devnet key generation`.
- Reference issues where relevant (`Fixes #123`).

## What we welcome

- Documentation fixes and clarifications.
- Node operator / Windows install improvements.
- Devnet ergonomics (still loopback-only).
- Safety tooling improvements (stricter secret/claim scans).
- Tokenomics doc clarity (numbers must match `tokenomics/acap_tokenomics.json`).

## What we will decline

- Anything implying the preview is a live financial product.
- Anything that adds real keys, secrets, or production deployment config.
- "Buy/invest now" features or fabricated on-chain addresses.

## Reporting security issues

Do **not** open a public issue. See [SECURITY.md](SECURITY.md).
