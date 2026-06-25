# ACAP Tokenomics (Preview)

> **Preview tokenomics — not a public mainnet token.** No sale, no reservation, no
> contract, no contract address. Not investment advice. Source of truth:
> [`../tokenomics/acap_tokenomics.json`](../tokenomics/acap_tokenomics.json).

This document is a human-readable companion to the canonical JSON and the
[tokenomics README](../tokenomics/README.md). If anything disagrees, the JSON wins.

## Core parameters

- **Max supply:** 1,000,000,000 ACAP (one billion), **fixed hard cap**.
- **Mint policy:** no unlimited mint. Hard cap enforced.
- **Decimals:** 18 (technical). UI may display 2–4 decimals.
- **State:** `sale_active=false`, `reservation_active=false`, `buy_enabled=false`,
  `available_for_reservation=0`, `current_circulating_supply=0`.
- **Contract:** `contract_deployed=false`, `contract_address=null`.

## Allocation (100%)

10% public/community · 15% node operator reserve · 15% ecosystem ·
15% liquidity reserve · 20% treasury · 15% team (locked) · 10% strategic.
Total = 1,000,000,000 ACAP. Full table in the
[tokenomics README](../tokenomics/README.md).

## Utility (design stage)

- Node participation weight.
- Active capacity reservation for projects/issuers (no fixed term).
- Anti-spam cost on network actions.
- Future validator/operator reputation input.
- Ecosystem access.
- Possible future fee/payment unit (**not** a payment system today).

## Pricing tiers (planned, NOT open)

Pool 1 (1,000,000 ACAP) is **planned, not active**. Tiered pricing
($0.0010 → $0.0030 across four 250,000-ACAP tiers) is a **capacity-pricing
mechanism** — the cost to reserve capacity rises as the pool fills. It is **not** a
profit promise and reservation is currently disabled.

## Minting & governance controls

- Fixed cap; no unlimited mint.
- Reserve releases must be transparent and logged in the changelog.
- Future contract changes must require multisig / timelock / governance when
  implemented. No contract exists yet.

## Disclaimers

ACAP tokenomics are draft/preview and may change before any launch. No public
mainnet token sale is active. No reservation is open. No custody, trading, bridge,
payments, or public rewards are live. See [DISCLAIMERS.md](DISCLAIMERS.md).
