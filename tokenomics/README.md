# ACAP Tokenomics (Preview)

> **Preview tokenomics — not a public mainnet token.** No sale is active, no
> reservation is open, no contract is deployed, and no contract address exists.
> Numbers are draft and versioned in the changelog. This is **not** investment
> advice and **not** a profit promise.

Machine-readable source of truth: [`acap_tokenomics.json`](acap_tokenomics.json)
(v0.2.0-preview). If anything here disagrees with the JSON, **the JSON wins**.

## Hard facts

| Field | Value |
|-------|-------|
| Token name | Active Capacity Token |
| Ticker | ACAP |
| **Max supply** | **1,000,000,000** (one billion) |
| **Decimals** | **18** (UI may show 2–4) |
| Mint policy | **Fixed hard cap — no unlimited mint** |
| `sale_active` | **false** |
| `reservation_active` | **false** |
| `buy_enabled` | **false** |
| `available_for_reservation` | **0** |
| `current_circulating_supply` | 0 |
| `contract_deployed` | **false** |
| `contract_address` | **null** (none) |

## Active Capacity Reservation model

ACAP uses an **Active Capacity Reservation** model — **not** a fixed-term lease:

- ACAP belongs to the holder. There is **no fixed expiration term**.
- You reserve **active network capacity** — you are not renting tokens for a period.
- ACAP remains yours while held; nothing expires or is confiscated after a term.
- Active-capacity status depends on **movement, node use, reservation activity, or
  other participation**.
- Inactive ACAP is **not confiscated**, but its active-capacity weight may pause,
  decay, or become inactive until reactivated (via movement / node participation /
  other defined network actions).
- Value comes from capacity, movement, participation, anti-spam, and network
  usefulness — **not** from a rental clock and **not** from a profit promise.

## Allocation (preview)

| Allocation | % | Tokens | Locked |
|------------|---|--------|--------|
| Public / community / early users | 10% | 100,000,000 | no |
| Node operator reserve | 15% | 150,000,000 | yes |
| Ecosystem grants / developers / integrations | 15% | 150,000,000 | yes |
| Liquidity / exchange reserve | 15% | 150,000,000 | yes |
| Treasury / company reserve | 20% | 200,000,000 | yes |
| Team / founders (locked) | 15% | 150,000,000 | yes |
| Strategic partners / advisors / legal / infra | 10% | 100,000,000 | yes |
| **Total** | **100%** | **1,000,000,000** | |

No trading or listing is live. Locked reserves release only by transparent,
documented rule.

## Pricing tiers (planned — NOT open)

Pool 1 is **planned, not active** (`available_now=0`). Tiered pricing is a
**capacity-pricing mechanism**, not an investment instrument:

| Tier | Range (ACAP reserved) | Price (USD) | Status |
|------|-----------------------|-------------|--------|
| 1 | 0 – 250,000 | $0.0010 | planned |
| 2 | 250,001 – 500,000 | $0.0015 | planned |
| 3 | 500,001 – 750,000 | $0.0020 | planned |
| 4 | 750,001 – 1,000,000 | $0.0030 | planned |

## Minting controls

- `unlimited_mint=false`, hard cap 1,000,000,000.
- Any reserve release must be transparent and documented in the changelog.
- Future contract changes must require multisig / timelock / governance when
  implemented. **No contract is deployed today.**

## Disclaimers

See the `disclaimers` array in `acap_tokenomics.json` and
[../docs/DISCLAIMERS.md](../docs/DISCLAIMERS.md). In short: preview only; no
mainnet, custody, trading, bridge, payments, or public rewards are live.
