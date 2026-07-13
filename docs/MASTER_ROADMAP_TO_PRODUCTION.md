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

**Current active stage.**

First unblock PostgreSQL:
- repair the full Alembic chain at `a1b2c3d4e5f6`;
- prove fresh PostgreSQL and SQLite upgrades;
- verify Numeric types and row preservation.

Then implement:
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

- WayForPay/Plisio real sandbox callback proof.
- Signature canonicalisation verified against provider evidence.
- Idempotency and reconciliation proof.
- Refund and chargeback operating procedures.
- Provision production PostgreSQL.
- Verified off-host backup before cutover.
- Maintenance window and rollback rehearsal.
- Numeric-at-rest verification after cutover.

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
