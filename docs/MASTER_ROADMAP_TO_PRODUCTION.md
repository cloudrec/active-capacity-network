# ACAP Network + 469 Diamond Auction — Master Roadmap to Production

**Last updated:** 2026-07-13

This roadmap is authoritative for direction, not proof that a capability is live. Live status must always be verified from current code, configuration, tests and operator evidence.

## Stage 0 — Safety and continuity

- Mandatory verified backup before every agent task.
- Encrypted off-host backup destination and restore drill.
- Current-report-only policy; deleted historical reports are not restored automatically.
- Secrets excluded from backups, reports and Git.
- Reproducible tests and migration rehearsals.

## Stage 1 — ACAP Network Core

**V1 completed as private preview/readiness.**

- Node Registry.
- Observer/candidate/validator roles.
- Validator Admission Safety.
- Operator Safety Quorum.
- Capacity, Trust and Reputation scoring.
- Movement Echo simulator.
- Public/admin network status.

Production gates still required:
- signed enrolment;
- key lifecycle;
- validator ceremony;
- partner policies;
- independent security review;
- consensus lab.

## Stage 2 — Digital Asset Lifecycle

**V1 completed in Auction as preview/readiness.**

- Issuer and Asset registries.
- Document, Verification and Certificate registries.
- Ownership platform records.
- Servicing event history.
- Lifecycle state machine.
- Readiness evaluators.
- Diamond reference asset flow.

Production gates:
- real verification providers;
- custody model;
- legal-title mapping by jurisdiction;
- retention/privacy review;
- production Postgres.

## Stage 3 — Smart Blocks Runtime

**V1 completed as simulation-only.**

- Deterministic bounded rule engine.
- Versioned templates.
- Simulation previews and hashes.
- No arbitrary code execution.
- No chain, payment, custody or transfer side effects.

Production gates:
- independent review;
- signed template governance;
- certificate signing policy;
- formal change control;
- runtime reproducibility and audit.

## Stage 4 — RWA Issuance Engine

**V1 completed as private-preview simulation.**

- Issuance request lifecycle.
- Supply-term validation.
- Readiness gates.
- Smart Block simulation binding.
- Propose-not-apply lifecycle transition.
- Diamond issuance reference flow.

Production gates:
- legal classification;
- custody;
- verified issuer onboarding;
- production settlement rails;
- on-chain deployment review;
- no token is issued before these gates.

## Stage 5 — Settlement, Secondary Market and Liquidity Readiness

**COMPLETED V1.** Alembic chain repaired (single head, proven on disposable PostgreSQL +
SQLite, Numeric types + row preservation verified). Plus strict-schema startup guard,
PostgreSQL cutover rehearsal, and PSP signed-fixture verification harness. Stage 6B/6C/6D
tooling is COMPLETE; the current unblocked internal track has advanced through ACAP Stages
8A–8D (see below). The next direction is Stage 8E / Stage 9 preparation — no consensus, no
mainnet.

Delivered:
- Settlement Engine with payment/settlement separation;
- explicit ownership platform-record action;
- reconciliation, refund, chargeback and dispute readiness;
- preview-only listing, offers and deterministic matching;
- redemption request readiness;
- buyback policy readiness;
- reserve evidence statuses;
- market-maker candidate/readiness profiles;
- lifecycle servicing integration;
- Smart Block readiness simulations.

No live market, transfer, reserve, buyback or liquidity guarantee is allowed in this stage.

## Stage 6 — Payment and database production readiness

Stage 6A (COMPLETED): strict Alembic-controlled schema startup (production/staging ⇒
strict regardless of dialect; the live SQLite runtime is on an explicit temporary create
mode flagged as a production blocker); PostgreSQL cutover rehearsal toolkit
(backup/restore/migrate/rollback on a disposable DB); PSP signed-fixture verification
harness (the `mock` provider is local-fixture only, WayForPay/Plisio real sandbox E2E
`blocked_external`); a callback can never complete settlement.

**Stage 6B — Production Operations Readiness — tooling COMPLETED:**
- [x] Unified ops-status monitoring (service health, schema drift, backup freshness,
  off-host, provider readiness, disk) + CLI + admin endpoint.
- [x] Alert dispatcher (disabled by default, redacted, no secrets) + systemd templates.
- [x] Disaster-recovery + operations runbook.
- [x] Readiness-only provider integration interfaces (custody, reserve attestation,
  legal review, PSP real-sandbox onboarding).
- [x] Cutover go/no-go gate (never executes). Off-host backup framework audited.

**Stage 6C — Provider Onboarding Interfaces — COMPLETED:**
- [x] Auditable onboarding lifecycle (draft → … → active_registered), hash-only evidence
  + tamper-evident event chain; admin UI + API. Readiness only.

**Stage 6D — Provider Readiness Integrity + Evidence Governance — COMPLETED:**
- [x] `active_registered != operationally_ready`; DEMO/fixture fail-closed out of
  production readiness; evidence governance (hash-only, expiry, revocation, four-eyes).
- [x] Provider-specific operational gates; adapter capability contract; cutover gate split
  (`postgres_only` vs `payments_enabled`, never executes).

**ACAP Stage 8A — Signed Node Enrolment + Validator Pilot Readiness — COMPLETED:**
- [x] Ed25519 domain-separated challenge-response; signature proves key control ONLY
- [x] Observer-only registration (zero voting power, not admitted, no rewards)
- [x] Key rotation (dual-signature) / lost-key recovery (admin + cooldown) / revocation +
  append-only hash-chained identity audit
- [x] Validator admission = separate paused-by-default preview workflow (operator-majority
  safety + four-eyes); never mutates a live validator set

**ACAP Stage 8B — Validator Admission Preview Workflow — COMPLETED:**
- [x] Candidate-review → admission PREVIEW state machine; deterministic fail-closed candidate
  readiness (key-control necessary, NOT sufficient)
- [x] Operator-majority (67%) safety simulation blocks unsafe proposals; disabled+paused by
  default; partner-51 stays blocked
- [x] Four-eyes (approver != creator/proposer) + audited owner override, all preview-only; a
  proposal never admits a validator, grants voting power, or changes observer/vp0 state
- These (8A/8B) are the unblocked internal track. Stage 7 (custody/reserve/verification/legal) remains blocked.

**ACAP Stage 8E — Multi-Operator Governance Identities — COMPLETED:**
- [x] Durable registry of governance principals (separated roles: proposer / approver /
      owner sign-off / auditor / operator admin); bearer token shown once, stored as SHA-256
      HASH ONLY (+ last-4 hint) — never the token or any secret; register / rotate / suspend /
      revoke audit-logged; a suspended or rotated token no longer authenticates.
- [x] Real separation of duties — production activation four-eyes requires DISTINCT active
      registered principals for the approver + owner sign-off, independent of creator/proposer;
      single-owner deployment stays production NO-GO; owner override never satisfies it.
- [x] Server-derived acting identity (bearer token or admin session), never the request body;
      admission + activation actions attributed to the principal. Nothing activates a validator.

**ACAP Stage 8F — Isolated Consensus Lab + Independent Security-Review Prep — COMPLETED:**
- [x] Sandboxed consensus simulator: deterministic safety / liveness / operator-majority /
      BFT `f=floor((n-1)/3)` for crash + byzantine faults; pure function of its scenario;
      imports no live-mutating module; mutates no live state; activates nothing (self-checked).
- [x] Independent security-review prep: machine-readable checklist of standing invariants +
      REDACTED evidence bundle (no secrets/tokens/keys/nonces/DSN/host paths); claims no mainnet
      readiness or attack resistance.
- [x] Public consensus-lab + security-review pages; admin sim/read endpoints 401-gated.
      Nothing activates a validator; observer/vp0.

### Next direction — Stage 9 preparation (NOT started; no consensus, no mainnet)
- [ ] External independent security review using the prepared evidence bundle.
- [ ] Only under a separate, explicit owner decision: a scoped, still-sandboxed consensus-lab
      expansion (never wired to the live preview).

**ACAP Stage 8D — Durable Governance State + Activation Manifest Integrity — COMPLETED:**
- [x] Durable transactional governance store (SQLite WAL / FK / synchronous FULL / secure
      permissions): atomic transitions, fail-closed on corruption, DB-enforced uniqueness
      (one active fingerprint, single-use nonce, idempotency), fork-proof per-stream hash-chained
      audit. Authoritative registry not forked; no silent JSON fallback.
- [x] Verified JSON→store migration (preflight / dry-run / migrate / verify / rollback); legacy
      JSON snapshotted immutable; count + chain parity checked.
- [x] Immutable hashed activation manifest; rehearsals + owner sign-offs bind to it; any change
      to key / build / policy / incidents / voting power / distribution makes them stale.
- [x] Production four-eyes hardened (owner override never satisfies production; single-owner stays
      NO-GO); server-derived actor identity (no body spoofing); activation still NO-GO + inert.
- [x] Stage 8E (multi-operator governance identities) now COMPLETED — see above.

**ACAP Stage 8C — Validator Pilot Activation Readiness — COMPLETED:**
- [x] Twelve fail-closed activation gates (approved-preview reached, four-eyes/override
  recorded, candidate readiness current, node still observer/vp0, key active, no incident,
  distribution safe [operator ≥67% / external ≤33% / single ≤5%], admission enabled, admission
  unpaused, rehearsal passed, owner sign-off recorded, cooldown elapsed) → NO-GO by default
- [x] Rehearsal is a pure dry-run projection (mutates no live set); owner sign-off is a
  governance gate bound to the proposed voting power
- [x] `request_activation` is ALWAYS blocked + performs no live change; even a fully-GO gate
  is blocked (`live_activation_is_a_separate_owner_gated_action`). Nothing activates a
  validator, changes a node's role, or grants voting power. Live activation stays a separate,
  owner-gated action outside this readiness system.

**Owner-gated remainder (external Auction actions):**
- [ ] Off-host backup destination configured + timer enabled (confirm synced).
- [ ] Real providers onboarded to OPERATIONAL readiness (non-demo → configured →
  capability-proven → independently-verified evidence with four-eyes → production_eligible).
  Only production_eligible non-demo providers clear the payments cutover gate.
- [ ] Provision production PostgreSQL; run the rehearsal + go/no-go gate (must be GO);
  owner-approved cutover; remove the temporary create mode so production resolves to
  strict; verify the guard at head; Numeric-at-rest verification after cutover.
- [ ] WayForPay/Plisio real sandbox callback proof; idempotency + reconciliation proof;
  refund/chargeback operating procedures.

No production cutover or real payments without a separate, explicit owner confirmation.

## Stage 7 — Custody, verification and proof

- Custody partner selection and integration.
- Asset inspection and verification-provider adapters.
- Attestation expiry/revocation.
- Reserve evidence schema and independent attestation.
- Delivery/redemption operating model.
- Proof references must state exactly what they prove and do not prove.

## Stage 8 — Partner validator pilot

- Signed node enrolment.
- Operator and partner validator identities.
- Voting-power policy and caps.
- Admission/withdrawal cooldowns.
- Monitoring and incident response.
- Operator minimum voting power maintained by policy, not raw node count.
- No fake decentralisation.

## Stage 9 — Consensus laboratory and audited pilot chain

- Evaluate QBFT/IBFT, CometBFT/Tendermint and HotStuff-style approaches.
- Run isolated multi-validator lab.
- Safety/liveness/fault tests.
- Key compromise and disaster-recovery drills.
- Independent security review.
- No public mainnet claim.

## Stage 10 — Production consideration

Only consider public production after all of the following:

- legal classification and jurisdictional review;
- security audit;
- audited contracts if contracts are used;
- custody and verification providers;
- production payments and reconciliation;
- production PostgreSQL and off-host backups;
- monitoring, alerts and incident response;
- validator governance;
- transparent token/fee policy;
- clear risk disclosures;
- evidence that users and partners exist;
- no guaranteed liquidity or profits.

## Permanent principles

1. Tokenization is not liquidity.
2. ACAP is infrastructure, not asset backing.
3. Platform ownership records are not automatically legal title.
4. On-chain transaction confirmation is not ownership, custody, value or proof of reserve.
5. Payment observation is not payment verification; payment verification is not settlement finality.
6. A simulation must never silently become execution.
7. Every state-changing action requires authorization, validation and an audit event.
8. No raw node count security claims; use validator admission and voting power.
9. Status labels must remain honest.
10. Build continuously, but never cross a production gate without evidence.
