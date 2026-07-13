# ACAP Network + 469 Diamond Auction — Master Project State and Handoff

**Last updated:** 2026-07-13
**Purpose:** Authoritative continuation document for a new AI/chat/engineering session.

> Read this file first. Do not ask the owner to repeat project history. Verify current code and current reports, then continue from the **NEXT ACTIVE TASK** section.

## 1. Project identity

### ACAP Network
- Public preview domain: `https://acap.network`
- Server workdir: `/opt/capacity`
- Runtime: FastAPI on `127.0.0.1:3470`
- Purpose: capacity/trust/validation infrastructure for RWA issuance, servicing, proof references, Smart Blocks and future validator participation.
- ACAP is **not** the liquidity source for asset-backed tokens.

### 469 Diamond Auction
- Public preview domain: `https://auction.469diamond.com`
- Server workdir: `/opt/diamond/auction`
- Runtime: FastAPI on `127.0.0.1:3469`
- Purpose: RWA issuance, auction, settlement-state, ownership-record and servicing platform, initially focused on diamonds.

## 2. Non-negotiable operating rules

1. **Backup first.** Every agent task begins with a verified full-project backup of both workdirs where relevant. Create SHA256, verify `tar -tzf`, create manifest, stop if backup fails.
2. **Do not restore deleted reports.** The owner intentionally removes old reports. Use `reports/CURRENT_REPORTS_INDEX.md`. Do not reconstruct history unless explicitly requested.
3. **No false production claims.** Mainnet, real payments, custody, bridge, rewards, staking, mining, legal title, proof of reserves and guaranteed liquidity are not live unless independently verified.
4. **Fail closed.** New external nodes default to observer/zero voting power; validator admission disabled/paused by default; no automatic balance credit or lifecycle transition.
5. **No secrets in Git or reports.** Never commit `.env`, keys, credentials, RPC URLs with secrets, personal data or production dumps.
6. **Do not toggle live flags merely to pass tests.** Report pre-existing failures separately.
7. **One current final report per major session.** Update `CURRENT_REPORTS_INDEX.md`.

## 3. Completed architecture and implementation layers

### A. ACAP domain and preview infrastructure
- `acap.network` serves the Capacity app with TLS and Cloudflare.
- Legacy `capacity.469diamond.com` redirects to `acap.network`.
- Existing sibling Auction domain remains intact.

### B. Read-only on-chain verification
- Ethereum mainnet read-only verifier enabled.
- Real confirmed-transaction E2E HTTP path proven.
- RPC method allow-list; no signing, keys, custody or balance credit.
- RPC failover support, contract-sensitive cache, rate limiting and admin diagnostics implemented.
- Honest `proves` / `does_not_prove` output is mandatory.

### C. ACAP Network Core V1
Implemented in `/opt/capacity`:
- Node Registry.
- Validator Admission Safety calculator.
- Operator Safety Quorum calculator.
- Capacity Score.
- Trust and Reputation scores.
- Movement Echo deterministic unsigned hash-chain simulator.
- Public/admin API and frontend status pages.

Safety posture:
- New external node = observer.
- Voting power = 0.
- Admission disabled and paused by default.
- No live consensus, validator process, rewards or mainnet.

### D. ACAP-to-Auction network reference integration
- Auction references ACAP by `node_id` only.
- ACAP remains authoritative for network facts.
- Auction does not copy RPC URLs, keys, IP addresses or consensus state.
- Current integration is readiness/reference-only, not a live dependency.

### E. Digital Asset Lifecycle Engine V1
Implemented in Auction:
- Fail-closed lifecycle state machine.
- Issuer Registry.
- Asset Registry and Asset Class Registry.
- Document, Verification and Certificate registries.
- Platform Ownership Record registry.
- Servicing Event registry with hash-chain history.
- Deterministic readiness evaluators.
- Diamond reference flow.
- Public/admin APIs and frontend asset pages.

Important truth labels:
- Platform ownership record is not legal title.
- Settlement state is not final legal settlement.
- Verification types remain distinct: self-reported, operator-reviewed, independent-provider, on-chain-reference, legal-review and custody-attestation.

### F. Smart Blocks Runtime V1
Implemented in Capacity:
- Deterministic, bounded, fail-closed rule engine.
- No `eval`, `exec`, network, filesystem or environment access from a rule.
- Template Registry with version/status lifecycle.
- Seven RWA reference templates.
- Simulation-only execution previews.
- Public/admin API and frontend pages.

### G. RWA Issuance Engine V1
Implemented in Auction:
- IssuanceRequest lifecycle.
- Eleven readiness gates.
- Smart Block binding and simulation.
- Propose-not-apply lifecycle integration.
- Numeric requested supply.
- Hash-chained readiness snapshots and approval events.
- Diamond issuance reference flow.
- No token issued, no balance credited, no custody or payment.

### H. Landing, registration and lead operations
Implemented in Auction:
- Institutional landing and honest live/not-live status copy.
- Public early-access registration.
- Admin lead list, filtering, status workflow, notes and CSV export.
- UTM/source tracking.
- Outreach and partner-acquisition materials.
- Current reports policy fixed so old deleted reports are not restored.

## 4. Current technical debt and blockers

### Critical technical blocker before more production DB work
The complete Alembic chain on a fresh PostgreSQL database has previously failed at revision:

`a1b2c3d4e5f6_money_float_to_numeric.py`

The failure concerns Float/double-precision to Numeric conversion of money columns, including:
- `payment_attempt_logs.amount`
- `payment_webhook_events.amount`

The latest task requires reproducing and safely fixing this migration before adding Settlement/Secondary Market tables.

### External/owner-dependent blockers
- Off-host backup destination credentials/target not fully configured.
- WayForPay/Plisio sandbox callbacks not independently confirmed.
- Production PostgreSQL host/cutover not approved.
- Custody provider not integrated.
- Jurisdiction-specific legal review not complete.
- Alert provider not wired.
- Windows executable signing certificate/runner unavailable.

## 5. Product positioning

Preferred positioning:

**RWA Issuance, Auction & Servicing Platform**

or

**Tokenized RWA Issuance, Auction & Servicing Infrastructure**

Market context may cite institutional movement toward issuance, compliance-aware workflows, privacy, distribution and asset servicing. Never imply partnership or endorsement by Deutsche Bank, DAMA 2, Axelar, zkSync or any other institution.

### Liquidity doctrine
Tokenization does not create liquidity. Liquidity can only come from:
- Primary auction demand.
- Real secondary buyers.
- Issuer redemption windows.
- Contracted buyback programs.
- Verified reserve policy.
- Qualified market makers with real capital.
- Custody-enabled delivery/redemption.
- Regulated/qualified distribution partners.

ACAP is infrastructure/capacity/trust utility, not backing and not a buyback reserve.

## 6. Security doctrine

- Do not measure 51% security by raw node count.
- Security is based on validator admission and voting power.
- Pilot operator minimum voting power target: 67%.
- Future partner-mode minimum: 51%, only after governance/security review.
- Observer and candidate nodes do not affect consensus.
- No automatic validator autoscaling is enabled.
- Reserve-node calculations are advisory only.

## 7. Current known test baselines

Latest reported baselines before the active Settlement task:
- Auction full suite after Lifecycle Engine: 818 passed, 0 failed, 7 skipped.
- Auction full suite after Issuance Engine: 842 passed, 0 failed, 7 skipped.
- Capacity Network Core focused suites and smoke were green.
- Capacity Smart Runtime focused tests were green.

Always rerun current tests; do not treat these historical counts as current proof.

## 8. NEXT ACTIVE TASK

**Repair the full PostgreSQL Alembic chain, then implement Settlement Engine V1 + Secondary Market Preview V1 + Liquidity/Redemption/Buyback Readiness V1.**

Required sequence:

1. Create verified full backups.
2. Reproduce fresh PostgreSQL `alembic upgrade head` failure.
3. Fix `a1b2c3d4e5f6` safely:
   - inspect table/column/current type;
   - alter only Float/real/double precision;
   - explicit PostgreSQL `USING ...::numeric(...)`;
   - skip already-Numeric;
   - preserve rows/defaults/indexes;
   - test fresh PostgreSQL, existing-like PostgreSQL, SQLite and downgrade/re-upgrade.
4. Verify exact types:
   - money: `NUMERIC(20,2)`;
   - token quantities: `NUMERIC(30,8)`;
   - issuance supply: `NUMERIC(38,0)`.
5. Build Settlement Engine with strict payment/settlement separation.
6. Build explicit platform ownership-record action; no legal-title claim.
7. Build preview-only secondary listing/offer/matching with deterministic price-time priority.
8. Build redemption, buyback policy, reserve and market-maker readiness models.
9. Append servicing events.
10. Add Smart Block readiness simulations.
11. Add APIs, frontend, migrations and tests.
12. Keep everything Preview/Readiness; no real payment, custody, transfer or guaranteed liquidity.

Expected final paths for the active task:
- `/opt/capacity/docs/ACAP_SETTLEMENT_SECONDARY_MARKET_LIQUIDITY_V1.md`
- `/opt/capacity/reports/ACAP_SETTLEMENT_LIQUIDITY_ARCHITECTURE_V1_FINAL_REPORT.md`
- `/opt/diamond/auction/reports/AUCTION_SETTLEMENT_SECONDARY_MARKET_V1_FINAL_REPORT.md`

## 9. Longer-term destination

The intended progression is:

1. Network Core — completed V1.
2. Digital Asset Lifecycle Engine — completed V1.
3. Smart Blocks Runtime — completed V1.
4. RWA Issuance Engine — completed V1.
5. Settlement + Secondary Market + Liquidity Readiness — active next step.
6. PSP sandbox proof and payment reconciliation hardening.
7. Production PostgreSQL provisioning/cutover after backup and migration proof.
8. Custody and verification-provider integrations.
9. Signed node enrolment and partner-validator pilot.
10. Safe consensus laboratory and audited pilot chain.
11. Only after legal/security/custody/payment/monitoring gates: consideration of a public network.

## 10. New-session instruction

Start a new chat with:

> Continue ACAP Network + 469 Diamond Auction. Read `docs/PROJECT_STATE_AND_HANDOFF.md` in `cloudrec/active-capacity-network` first. The next active task is the PostgreSQL Alembic chain repair followed by Settlement Engine V1 + Secondary Market/Liquidity Readiness. Do not ask me to repeat project history. Do not restore old reports. Always backup first.
