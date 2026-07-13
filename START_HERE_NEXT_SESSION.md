# START HERE — Continue ACAP + 469 Auction

Read these files in order:

1. [`docs/PROJECT_STATE_AND_HANDOFF.md`](docs/PROJECT_STATE_AND_HANDOFF.md) — what exists, current state, exact next task.
2. [`docs/MASTER_ROADMAP_TO_PRODUCTION.md`](docs/MASTER_ROADMAP_TO_PRODUCTION.md) — where the project is going and production gates.
3. [`README.md`](README.md) — public ACAP preview posture.

Last updated: 2026-07-13 (Stage 6B).

## Completed (do NOT rebuild)

- Alembic PostgreSQL chain repair — single head, proven on disposable PostgreSQL.
- Settlement Engine V1 + Secondary Market Preview V1 + Liquidity/Redemption/Buyback Readiness V1.
- Strict-schema startup guard V1.
- PostgreSQL cutover rehearsal V1.
- PSP signed-fixture verification harness V1.
- **Stage 6B — Production Operations Readiness V1:** unified ops-status monitoring
  (schema drift + backup freshness + off-host + provider readiness), alert dispatcher
  (disabled by default, no secrets), readiness-only provider-integration interfaces,
  cutover go/no-go gate (never executes), DR/ops docs. Off-host framework audited.
- **Stage 6C — Provider Onboarding Interfaces V1:** auditable onboarding lifecycle
  (draft → … → active_registered) with hash-only evidence + tamper-evident event chain;
  a kind's provider readiness flips ready only when its onboarding is active_registered,
  reflected into production-readiness / ops-status / cutover-gate. Admin UI + API.
  Readiness only — no custody, reserve proof, legal title, live call, or value movement.

There is **no open Alembic failure** and **no open "build Settlement Engine" task**.

## Current factual state

- **Production PostgreSQL:** rehearsal passed; real host not provisioned; production not switched.
- **Schema mode:** production/staging resolve to strict (regardless of DB dialect). The
  current live runtime is SQLite and runs an explicit temporary create mode, surfaced as
  a production blocker (`legacy_explicit_create`) — not strict-ready.
- **WayForPay / Plisio:** local verification harness ready; real sandbox E2E = `blocked_external`.
- **PSP mock provider:** `local_fixture_only` (signed local fixture) — not a real provider E2E.
- **Off-host backup:** not configured. **Providers:** onboarding workflow ready; all
  kinds (custody / reserve attestation / legal review / PSP) still `not_integrated` until
  onboarded + registered.

## Next active task — OWNER-GATED external actions

Stage 6B + 6C tooling is complete. What remains needs the owner (no build work is
unblocked without these):
1. Configure an off-host backup destination + enable its timer (confirm synced).
2. Onboard real providers (custody, reserve attestation, legal review, PSP) through the
   Stage-6C admin onboarding workflow: create → evidence → operator-review → approve →
   verify → register. Registering all four kinds clears the cutover-gate providers gate.
3. Provide real WayForPay + Plisio sandbox credentials + one confirmed callback each.
4. Provision production PostgreSQL; run the cutover rehearsal + go/no-go gate (must be GO);
   then the owner-approved cutover (set the production database URL; drop the temporary
   create mode so the schema guard resolves to strict).

No production cutover, real payment, or real-money movement without a separate, explicit
owner confirmation.

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
the strict-schema guard, the PostgreSQL rehearsal, the PSP verification harness and the
Stage 6B production-operations tooling are DONE — do not rebuild them. What remains is
owner-gated (off-host destination, provider onboarding, PostgreSQL/PSP cutover).
No production cutover or real payments without explicit owner confirmation.
```
