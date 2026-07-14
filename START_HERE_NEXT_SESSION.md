# START HERE — Continue ACAP + 469 Auction

Read these files in order:

1. [`docs/PROJECT_STATE_AND_HANDOFF.md`](docs/PROJECT_STATE_AND_HANDOFF.md) — what exists, current state, exact next task.
2. [`docs/MASTER_ROADMAP_TO_PRODUCTION.md`](docs/MASTER_ROADMAP_TO_PRODUCTION.md) — where the project is going and production gates.
3. [`README.md`](README.md) — public ACAP preview posture.

Last updated: 2026-07-14 (Stage 8G).

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
- **ACAP Stage 8C — Validator Pilot Activation Readiness V1:** the gates + evidence +
  rehearsal that would have to be GREEN before an approved-preview proposal could — in a
  future, SEPARATE, owner-gated action — become a live validator. Twelve fail-closed gates
  (approved-preview reached, four-eyes/override recorded, candidate readiness current, node
  still observer / vp 0, key active, no incident, distribution safe [operator ≥67% / external
  ≤33% / single ≤5%], admission enabled, admission unpaused, rehearsal passed, owner sign-off
  recorded, cooldown elapsed). Admission is disabled + paused by default, so the activation
  gate is **NO-GO by default**. A rehearsal is a pure dry-run projection that mutates no live
  set; owner sign-off is a governance gate bound to the proposed voting power; and
  `request_activation` is ALWAYS blocked and performs NO live change (even a fully-GO gate is
  blocked with `live_activation_is_a_separate_owner_gated_action`). Nothing here activates a
  validator, changes a node's role, or grants voting power. Not live — no mainnet, rewards, or
  consensus.
- **ACAP Stage 8D — Durable Governance State + Activation Manifest Integrity V1:** all ACAP
  governance state moved into a durable transactional store (SQLite WAL / foreign keys /
  synchronous FULL / secure permissions) — atomic multi-collection transitions, fail-closed on
  corruption, DB-enforced uniqueness (one active key fingerprint, single-use challenge nonce,
  idempotency), and a fork-proof per-stream hash-chained identity audit. The authoritative node
  registry is NOT forked and there is no silent fallback to the old JSON. A verified migration
  tool (preflight / dry-run / migrate / verify / rollback) snapshots the legacy JSON immutably
  and imports it in one transaction with count + chain parity checks. An immutable, hashed
  ACTIVATION MANIFEST binds rehearsals and owner sign-offs; any change to the key, software/build,
  policy, incidents, proposed voting power, or power distribution makes them stale. Production
  four-eyes is hardened: an owner override never satisfies the production activation gate, a
  single-owner deployment stays production NO-GO, and the recorded actor is the server-derived
  authenticated principal (the request body cannot spoof it). Activation stays NO-GO by default
  and the activation request is always inert — nothing activates a validator, admission stays
  disabled + paused, observer / zero voting power. This is the unblocked internal track; the next
  direction is Stage 8E / Stage 9 preparation (multi-operator governance identities, an isolated
  consensus lab, and independent security-review preparation) — WITHOUT starting consensus or
  claiming mainnet. Not live — no mainnet, rewards, or consensus.
- **ACAP Stage 8E — Multi-Operator Governance Identities V1:** a durable registry of governance
  principals — the distinct, individually-authenticated operators who fill separated governance
  roles (proposer / approver / owner sign-off / auditor). Each authenticates with a bearer token
  generated server-side and shown ONCE; only its SHA-256 hash and a last-4 hint are stored — never
  the token, a password, or any secret. Register / rotate-token / suspend / revoke are audit-logged
  and a suspended or rotated token no longer authenticates. This makes the Stage-8D production
  four-eyes REAL: the production activation gate now requires DISTINCT, ACTIVE, REGISTERED
  principals for the approver and owner sign-off, independent of the creator and proposer — a
  single-owner deployment stays production NO-GO and an owner override never satisfies it. The
  acting identity is resolved server-side from a bearer token or the admin session (never the
  request body, so it cannot be spoofed) and the admission and activation actions are attributed to
  that principal. This is the unblocked internal track; the next direction is an isolated consensus
  lab (sandboxed, never wired to the live preview) and independent security-review preparation —
  WITHOUT starting consensus or claiming mainnet. Nothing here activates a validator, grants voting
  power, or starts consensus. Not live.
- **ACAP Stage 8F — Isolated Consensus Lab + Independent Security-Review Prep V1:** (a) a SANDBOXED
  consensus simulator — a deterministic, pure function of its scenario that computes consensus
  safety, liveness, operator-majority and the BFT bound `f = floor((n-1)/3)` for crash and
  byzantine fault models. It imports no live-mutating module, never reads or writes the live node
  registry / governance store / activation state, persists nothing, and activates nothing; a
  self-check confirms the live registry is byte-identical after a run. Every result is labelled
  sandbox / not-live. (b) INDEPENDENT SECURITY-REVIEW PREPARATION — a machine-readable checklist of
  the standing safety invariants (admission disabled + paused, activation NO-GO, durable fork-proof
  audit, token-hash-only identities, real four-eyes, consensus-lab isolation) plus a REDACTED
  evidence bundle for an external reviewer that explicitly excludes every kind of secret (tokens,
  hashes, private keys, node public keys, nonces, operator identities, database contents, DSNs,
  host paths, IPs, credentials). It claims no mainnet readiness and no attack resistance. This is
  the unblocked internal track; the next direction is an external independent security review using
  the prepared bundle — WITHOUT starting consensus or claiming mainnet. Nothing here runs consensus,
  activates a validator, or grants voting power. Not live.
- **ACAP Stage 8G — Adversarial Governance Self-Audit V1:** an executable red-team harness that
  actively tries to break every standing safety invariant of the governance stack and proves each
  attack is BLOCKED — a forged bearer token cannot become a principal, a consumed challenge nonce
  cannot be replayed, one public key cannot bind two active nodes, concurrent audit appends cannot
  fork the chain, a single principal cannot self-satisfy production four-eyes, an owner override
  never satisfies the production gate, a plaintext token is never stored, `request_activation`
  stays inert, the consensus lab cannot mutate live state, a tampered audit event is detected,
  changing a bound input invalidates the rehearsal + sign-off, and the evidence bundle carries no
  secret. The suite runs ONLY against a throwaway store (it refuses the production database), and
  the admin endpoint runs it in an isolated subprocess so the live store is byte-identical
  afterwards. A redacted reviewer handoff package pairs the checklist with the adversarial run and
  reproduction steps. It is explicitly NOT an external independent review. This is the unblocked
  internal track; the next direction is an external independent review using the prepared handoff
  bundle — WITHOUT starting consensus or claiming mainnet. Nothing here activates a validator,
  grants voting power, or starts consensus. Not live.

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
