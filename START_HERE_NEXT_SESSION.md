# START HERE — Continue ACAP + 469 Auction

Read these files in order:

1. [`docs/PROJECT_STATE_AND_HANDOFF.md`](docs/PROJECT_STATE_AND_HANDOFF.md) — what exists, current state, exact next task.
2. [`docs/MASTER_ROADMAP_TO_PRODUCTION.md`](docs/MASTER_ROADMAP_TO_PRODUCTION.md) — where the project is going and production gates.
3. [`README.md`](README.md) — public ACAP preview posture.

Last updated: 2026-07-13 (Stage 6A closure).

## Completed (do NOT rebuild)

- Alembic PostgreSQL chain repair — single head, proven on disposable PostgreSQL.
- Settlement Engine V1 + Secondary Market Preview V1 + Liquidity/Redemption/Buyback Readiness V1.
- Strict-schema startup guard V1.
- PostgreSQL cutover rehearsal V1.
- PSP signed-fixture verification harness V1.

There is **no open Alembic failure** and **no open "build Settlement Engine" task**.

## Current factual state

- **Production PostgreSQL:** rehearsal passed; real host not provisioned; production not switched.
- **Schema mode:** production/staging resolve to strict (regardless of DB dialect). The
  current live runtime is SQLite and runs an explicit temporary create mode, surfaced as
  a production blocker (`legacy_explicit_create`) — not strict-ready.
- **WayForPay / Plisio:** local verification harness ready; real sandbox E2E = `blocked_external`.
- **PSP mock provider:** `local_fixture_only` (signed local fixture) — not a real provider E2E.
- **Off-host backup:** not configured. **Custody:** not integrated. **Legal review:** not
  completed. **Reserve attestation:** not integrated.

## Next active task

**Stage 6B — Production Operations Readiness:** off-host backup framework, monitoring and
alerting, disaster-recovery runbooks, provider integration interfaces, and owner-gated
PostgreSQL/PSP cutover preparation. No production cutover, real payment, or real-money
movement without a separate, explicit owner confirmation.

## Do NOT

Enable production DB, enable real payments, restore deleted reports, recreate a
`FINAL_REPORT_INDEX.md` stub, present the `mock` provider as a real sandbox verification,
or claim custody / legal title / real transfer / guaranteed liquidity.

## Prompt for a new chat

```text
Continue ACAP Network + 469 Diamond Auction.
Read START_HERE_NEXT_SESSION.md and docs/PROJECT_STATE_AND_HANDOFF.md in cloudrec/active-capacity-network before answering.
Do not ask me to repeat project history.
Settlement Engine V1, Secondary Market V1, Liquidity Readiness V1, the Alembic repair,
the strict-schema guard, the PostgreSQL rehearsal and the PSP verification harness are
DONE — do not rebuild them. Continue with Stage 6B (Production Operations Readiness).
No production cutover or real payments without explicit owner confirmation.
```
