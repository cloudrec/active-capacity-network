# START HERE — Continue ACAP + 469 Auction

Read these files in order:

1. [`docs/PROJECT_STATE_AND_HANDOFF.md`](docs/PROJECT_STATE_AND_HANDOFF.md) — what exists, current state, exact next task.
2. [`docs/MASTER_ROADMAP_TO_PRODUCTION.md`](docs/MASTER_ROADMAP_TO_PRODUCTION.md) — where the project is going and production gates.
3. [`README.md`](README.md) — public ACAP preview posture.

Last updated: 2026-07-13 (Stage 6D).

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
  (draft → … → active_registered) with hash-only evidence + tamper-evident event chain.
- **Stage 6D — Provider Readiness Integrity + Evidence Governance V1:** fixes the wrong
  equivalence `active_registered = ready`. Operational readiness is now computed
  fail-closed across separate axes; DEMO/fixture records never satisfy a production gate;
  evidence governance (hash-only, expiry, revocation, four-eyes) closes readiness on
  expiry/revocation; provider-specific operational gates; the cutover gate is split into
  `postgres_only` (no custody/PSP, payments stay off) vs `payments_enabled`, and never
  executes. Readiness only — no custody, reserves, legal title, live call, or value movement.
- **ACAP Stage 8A — Signed Node Enrolment + Validator Pilot Readiness V1:** Ed25519
  domain-separated challenge-response node enrolment. A valid signature proves control of
  a private key ONLY — never identity, trust, uptime, capacity, or validator eligibility.
  A successful enrolment makes the node an OBSERVER with zero voting power (not a validator,
  no rewards, no consensus). Key rotation (dual-signature) / lost-key recovery (admin +
  cooldown) / revocation, with an append-only hash-chained identity audit. Validator
  admission is a SEPARATE paused-by-default preview workflow (operator-majority safety +
  four-eyes) that never mutates a live validator set. A reference enrolment client keeps
  the private key on the node (never transmitted). Not live — no mainnet, rewards, or consensus.
- **ACAP Stage 8B — Validator Admission Preview Workflow V1:** a candidate-review →
  validator-admission PREVIEW pipeline. Key-control proof is NECESSARY but never SUFFICIENT:
  candidate readiness is a deterministic, fail-closed evaluation of policy inputs (software/
  build policy, declared capacity, operator review, trust/reputation thresholds, incidents,
  key age, recovery cooldown). The operator-majority (67% pilot) safety simulation blocks any
  proposal that would drop the operator below the minimum; admission is disabled + paused by
  default; partner-51 stays disabled. Four-eyes: the approver must differ from the creator and
  proposer; a single-owner override is audited + preview-only. A proposal NEVER admits a
  validator, grants voting power, or changes a node's observer/zero-voting-power state.
  Stages 8A/8B are the unblocked internal track; Stage 7 (custody/reserve/verification/legal
  providers) remains blocked. Not live — no mainnet, rewards, or consensus.

There is **no open Alembic failure** and **no open "build Settlement Engine" task**.

## Current factual state

- **Production PostgreSQL:** rehearsal passed; real host not provisioned; production not switched.
- **Schema mode:** production/staging resolve to strict (regardless of DB dialect). The
  current live runtime is SQLite and runs an explicit temporary create mode, surfaced as
  a production blocker (`legacy_explicit_create`) — not strict-ready.
- **WayForPay / Plisio:** local verification harness ready; real sandbox E2E = `blocked_external`.
- **PSP mock provider:** `local_fixture_only` (signed local fixture) — not a real provider E2E.
- **Off-host backup:** not configured. **Providers:** onboarding + readiness-integrity
  workflow ready; all kinds (custody / reserve attestation / legal review / PSP) are
  operationally NOT ready until onboarded to `production_eligible`. DEMO/fixture records
  never satisfy a production gate.

## Next active task — OWNER-GATED external actions

Stage 6B + 6C + 6D tooling is complete. What remains needs the owner (no build work is
unblocked without these):
1. Configure an off-host backup destination + enable its timer (confirm synced).
2. Onboard REAL providers (custody, reserve attestation, legal review, PSP) to
   OPERATIONAL readiness: non-demo record → configure → capability proof →
   independently-verified evidence (four-eyes) → `production_eligible`. Only
   production_eligible non-demo providers clear the payments cutover gate.
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
the strict-schema guard, the PostgreSQL rehearsal, the PSP verification harness, the
Stage 6B production-operations tooling, the Stage 6C provider onboarding and the Stage 6D
provider readiness-integrity + evidence governance are DONE — do not rebuild them. What
remains is owner-gated (off-host destination, onboarding REAL providers to
production_eligible, PostgreSQL/PSP cutover). active_registered != operationally ready;
DEMO records never satisfy a production gate. No production cutover or real payments
without explicit owner confirmation.
```
