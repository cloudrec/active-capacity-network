# Roadmap

> **Preview roadmap.** Items below are goals and design stages, not commitments or
> dates. Nothing here implies a live mainnet, sale, custody, or rewards. Each gated
> milestone must pass legal, security, and technical review before it goes live.

## Now (preview / prototype — what exists today)

- ACAP concept: **Proof of Active Capacity (PoAC)** — capacity that is allocated,
  moved, and made provable. Token unit: **ACAP**.
- **Tokenomics preview** (`tokenomics/`): 1,000,000,000 hard cap, 18 decimals,
  fixed cap (no unlimited mint). Sale and reservation are **off**.
- **ACAP Desktop Node** source + Windows launchers, read-only by default.
- **One-click Windows bootstrap installer** (per-user, no admin, HTTPS + SHA-256).
- **Local private devnet** (single-validator QBFT, chainId 469469, loopback only).
- Public-safe portal mirror of the first use case (469 Diamond auction PoAC data).

## Next (design / hardening)

- Multi-validator local devnet (still lab-only, no public RPC/P2P).
- Node operator reputation/activity model (design stage).
- Signed Windows release artifacts + reproducible build notes.
- Public testnet design (no value, faucet-style lab tokens only).

## Later (gated — requires review before any go-live)

Each of the following is **NOT live** and is gated behind explicit legal,
security, and governance review:

- Public testnet with multiple independent operators.
- Token contract design + audit (no contract is deployed today).
- Any reservation or distribution program (currently disabled).
- Governance, treasury, and reserve release rules (multisig / timelock).

## Explicitly NOT planned as "live" in this preview

- Public mainnet, custody, cross-chain bridge, payment processing.
- Live staking yield or guaranteed rewards.
- Token trading, listing, or a public sale / Buy flow.

See [docs/DISCLAIMERS.md](docs/DISCLAIMERS.md) for the full safety statement.
