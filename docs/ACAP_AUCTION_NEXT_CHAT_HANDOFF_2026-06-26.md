# ACAP / 469 Diamond Auction — Next Chat Handoff

**Date:** 2026-06-26  
**User:** Andrey Pecherskiy / @cloudkroter  
**Primary server paths:** `/opt/capacity` and `/opt/diamond/auction`  
**Public sites:** `https://capacity.469diamond.com`, `https://auction.469diamond.com`  
**GitHub public repo:** `cloudrec/active-capacity-network`  

## 0. Why this handoff exists

The current chat became too long. The next chat must continue without re-explaining the project and must stop drifting into side modules. The user specifically asked to focus on **what is not done** for the blockchain and auction, then work through those blockers step by step.

The blunt rule for the next chat:

> Do not keep building decorative layers. Work the production blockers: payments, Postgres, settlement/refunds, custody/PoR, devnet/validators, bridge, mainnet.

## 1. Critical user preferences

- User wants direct Russian explanations, but Claude/Sonnet tasks must be written in English.
- For Claude tasks, include `/clear`, `PRIMARY WORKDIR`, progress report first, final report exact path, and `AI_HANDOFF_CONTEXT.md` update.
- Do not pause for minor questions. Make safe assumptions, test, report exact paths and counts.
- Always distinguish demo/preview/readiness from real production capability.
- Do not claim mainnet, custody, bridge, provider payments, on-chain token delivery, rewards/mining, audit, or legal certification unless genuinely live and verified.
- User is frustrated with long tasks that do not attack the production blockers. The next step must be practical.

## 2. Current high-level state

### ACAP / blockchain side

Done or partially done:

- ACAP tokenomics: planned fixed max supply `100,000,000,000` ACAP, 18 decimals, no future ACAP minting after deployment.
- Manual self-custody Builder allocation payment flow exists.
- ACAP / Nova Wallet Core exists as a non-custodial account/ledger/cabinet layer.
- Smart Blocks Constructor exists: 100 templates, block catalog, CapacityScript, manifest, simulator.
- Solidity export exists for safe templates.
- Export packages are checked by Hardhat, Foundry, Slither, fallback scan, checksums, golden snapshots.
- Exact package validation exists.
- Async validation queue, public validation certificates, trust registry, badges, and certificate signing are now built.
- Production validation-certificate signing is enabled with a dedicated Ed25519 validation-certificate signing key outside the repo. This signs certificate JSON only; it is not blockchain signing and not an audit.

Not live:

- No public ACAP mainnet.
- No deployed ACAP token contract.
- No on-chain token delivery.
- No live protocol fee collection.
- No validator rewards/mining/staking.
- No real bridge.
- No custody.
- No proof-of-reserves provider.
- No professional audit.
- No legal certification.

### 469 Diamond Auction side

Done or partially done:

- Partner/private demo surfaces exist.
- Marketplace/demo auction flow exists.
- Cabinet/dashboard/receipts/off-chain ledger/audit surfaces exist.
- Manual settlement and sandbox/readiness paths exist.
- External token references/proof-claims exist as reference-only.
- Payment lifecycle/reconciliation/refund/cancel scaffolding exists, admin-gated and audited.
- Postgres staging migration rehearsal exists and passed against throwaway staging Postgres.
- Observability/ops status and public health endpoint exist.

Not live:

- No real automatic payment provider.
- No payment webhook/IPN with signature verification.
- No payment idempotency key based on provider transaction ID.
- No real refund/chargeback provider flow.
- No production Postgres cutover.
- No real custody provider.
- No proof-of-reserves attestation.
- No real bridge settlement.
- No real external-token trading.
- No legal/compliance production package.
- No full external monitoring/log shipping/pentest.

## 3. Most recent Phase 8 Smart Blocks status

Phase 8 was about production signing/registry ops, not blockchain deployment.

Completed:

- Dedicated Ed25519 validation-certificate signing key created outside repo.
- Production signing enabled.
- Active eligible public certificates signed.
- Public signature verification works; tampered certificates fail verification.
- Cleanup systemd timer installed/enabled/active.
- Backup/restore runbook and scripts created.
- Registry health/ops reports created.
- Public repo release package prepared but not pushed.

Verified counts from the final Phase 8 report:

| Suite | Result |
|---|---:|
| Phase 7 trust registry | 91 / 0 |
| Phase 6 async validation | 67 / 0 |
| Phase 5 exact validation | 36 / 0 |
| Phase 4 API | 32 / 0 |
| Smart Blocks | 51 / 0 |
| Solidity export | 81 / 0 |
| Export hardening | 31 / 0 |
| Golden snapshots | 96 / 0 |
| Fee model | 68 / 0 |
| Wallet core | 45 / 0 |
| Live manual payments | 78 / 0 |
| Smoke | 118 / 0 |
| Regression total | 794 / 0 |
| Phase 8 signing ops | 88 / 0 |
| Link check | 40 / 0 |
| Public repo scanners | PASS / PASS / PASS |

Important: a certificate signature attests validation-certificate JSON only. It is not a blockchain transaction, not deployment, and not professional audit.

## 4. What must NOT be claimed as live

Never claim these are live unless the next chat actually verifies and changes them:

1. Real automatic payment provider.
2. Public ACAP mainnet.
3. Testnet/mainnet smart contract deployment from the product.
4. On-chain ACAP token delivery.
5. Custody / asset storage.
6. Cross-chain bridge.
7. Mining / rewards / staking.
8. Live protocol fee collection.
9. Professional audit.
10. Legal certification.
11. Real external token trading.
12. Proof-of-reserves attestation.
13. Production Postgres cutover.

## 5. Reports and evidence that matter

Latest important reports/files observed in the chat and uploaded artifacts:

### ACAP / Smart Blocks

- `ACAP_SMART_BLOCKS_CONSTRUCTOR_FINAL_REPORT.md`
- `ACAP_WEB3_WALLET_CORE_FINAL_REPORT.md`
- `ACAP_SMART_BLOCKS_SOLIDITY_EXPORT_FINAL_REPORT.md`
- `ACAP_SMART_BLOCKS_EXPORT_HARDENING_FINAL_REPORT.md`
- `ACAP_SMART_BLOCKS_FOUNDRY_SLITHER_CI_FINAL_REPORT.md`
- `ACAP_SMART_BLOCKS_EXACT_PACKAGE_VALIDATION_FINAL_REPORT.zip`
- `ACAP_SMART_BLOCKS_ASYNC_VALIDATION_BADGES_PROGRESS_REPORT.zip`
- `ACAP_SMART_BLOCKS_PUBLIC_TRUST_REGISTRY_FINAL_REPORT.zip`
- `ACAP_SMART_BLOCKS_PRODUCTION_SIGNING_OPS_PROGRESS_REPORT.zip` — contains final report.

### Auction / production blockers

- `POSTGRES_STAGING_DATA_MIGRATION_FINAL_REPORT.md`
- `PAYMENT_SANDBOX_TO_LIVE_READY_FINAL_REPORT.md`
- `PAYMENT_RECONCILIATION_FINAL_REPORT.md`
- `OBSERVABILITY_OPERATIONS_FINAL_REPORT.md`
- `DATA_PAYMENT_RELIABILITY_FINAL_REPORT.md`
- `DISASTER_RECOVERY_FINAL_REPORT.md`
- `OFFHOST_BACKUP_READINESS_FINAL_REPORT.md`
- `EXTERNAL_VERIFICATION_PROVIDER_READINESS_FINAL_REPORT.zip`
- `GATED_READINESS_MODULES_FINAL_REPORT.zip`
- `FINAL_REPORT_INDEX.zip`

## 6. Auction blocker details

### Postgres

Status:

- Staging migration rehearsal completed.
- Throwaway staging Postgres copied 65/65 tables and 620 rows.
- Row-count parity passed.
- Live DB remains SQLite.

Known limitation:

- Money columns were still Float -> double precision in staging rehearsal; exact money model needs Numeric cutover.
- Live service was not switched to Postgres.
- Production cutover and maintenance-window plan still needed.

### Payment provider

Status:

- Payment provider module audited.
- Sandbox/inert provider logic exists.
- Real-charge capability structurally absent by design.
- `AUCTION_REAL_PAYMENTS=false` by default.

Real-money blockers:

1. Legal / AML / KYC sign-off.
2. Real merchant account with selected PSP.
3. Audited live provider class with `supports_real_charge=True`.
4. Webhook endpoint + signature verification.
5. Payment idempotency keyed on provider transaction id.
6. Refund/chargeback handling + ledger reconciliation.
7. Settlement path wired to fail closed until provider verified.
8. Only then set `AUCTION_REAL_PAYMENTS=true` in reviewed monitored env.

### Payment reconciliation/refunds

Status:

- Cancel/expire/fail/refund/reconcile/poll scaffolding exists.
- Admin-gated routes exist.
- Live refunds are blocked.
- Provider status polling is skeleton only; no network call.
- Every action audited.

Still missing:

- Real provider calls.
- Real refund/chargeback handling.
- Real reconciliation against PSP events.

### Observability / ops

Status:

- `/api/auction/health` now pings DB and returns public-safe status.
- Admin ops-status exists with production prerequisites and blockers.

Still missing/recommended:

- Metrics endpoint behind admin.
- External uptime alerts.
- Off-host log shipping.
- External pentest.

## 7. Correct next plan

The next chat should NOT continue Smart Blocks unless needed for cleanup. Smart Blocks is strong enough for now.

The next practical sequence:

1. Create one master blocker board for Auction + ACAP + Shared Infra.
2. Confirm current server repo status and report what is uncommitted.
3. Commit/push safe public repo docs if owner approves or already asked.
4. Start **Auction Production Track**:
   - Numeric money model audit.
   - Postgres production cutover plan and dry-run.
   - Payment provider selection and live integration spec.
   - Webhook + signature verification.
   - Idempotency + reconciliation.
5. Start **ACAP Blockchain Track** only after infra/payment track is sane:
   - Real devnet/validator plan.
   - ACAP contract deployment gate.
   - Claim/on-chain delivery design.
   - Bridge/custody/PoR only after real settlement/custody exists.

## 8. First task for Claude in the new chat

Use this exact direction. The user wants work, not theory.

```text
/clear

PRIMARY WORKDIRS:
/opt/capacity
/opt/diamond/auction

AUTONOMOUS TASK: Create the production blocker board for ACAP blockchain + 469 Diamond Auction, then start with the first practical blocker: Auction Postgres/Numeric/payment-provider readiness.

Do not build new decorative modules.
Do not continue Smart Blocks unless a production blocker depends on it.
Do not claim bridge/mainnet/custody/provider/audit/legal are live.

Create first:
- /opt/capacity/reports/NEXT_CHAT_BLOCKER_BOARD_PROGRESS_REPORT.md
- /opt/diamond/auction/reports/NEXT_CHAT_BLOCKER_BOARD_PROGRESS_REPORT.md

Goals:
1. Read current reports, env flags, service status, git status, DB config, readiness endpoints.
2. Produce a single blocker board divided into:
   - ACAP Blockchain
   - 469 Auction
   - Shared Infra/Ops
3. For every blocker mark:
   - done / partial / not live / blocked
   - evidence path
   - exact env flags
   - code module involved
   - external dependency required
   - next concrete action
4. Start implementation on the first blocker:
   - verify Auction money model Float/Decimal/Numeric state
   - verify Postgres staging migration state
   - prepare the production Postgres cutover runbook and safety gate
   - verify payment provider blockers and exact code gaps
5. Run tests and produce exact counts.
6. Do not enable real payments.
7. Do not switch production DB unless explicitly approved.
8. Do not deploy contracts.
9. Do not push secrets.
10. Update AI_HANDOFF_CONTEXT.md.

Final reports:
- /opt/capacity/reports/ACAP_AUCTION_PRODUCTION_BLOCKER_BOARD_FINAL_REPORT.md
- /opt/diamond/auction/reports/AUCTION_POSTGRES_PAYMENT_READINESS_NEXT_STEPS_FINAL_REPORT.md

Final response must end with exact report paths.
```

## 9. Git status / public repo note

Known public repo:

- `cloudrec/active-capacity-network`
- User has push/admin permissions through GitHub connector.
- In-server public repo path from reports: `/opt/capacity/public_repo/active-capacity-network`.
- Many tasks prepared safe docs but did not push.
- The main app dir `/opt/capacity` itself was reported as not being a git repo in Phase 8.

What was committed in this chat through GitHub connector:

- A safe handoff/context file for the next chat should be present in `cloudrec/active-capacity-network` under `docs/` after this handoff step.

What still requires server-side Claude or SSH:

- Committing actual server-local generated code and reports from `/opt/capacity` or `/opt/diamond/auction`.
- Running git status inside `/opt/capacity/public_repo/active-capacity-network` and pushing the accumulated safe docs.
- Ensuring no private key, `.env`, DB, logs, payment evidence, or user data are included.

## 10. Reminder to next assistant

Be direct. The user is right to complain about drift. Explain what is real, what is demo, and what exact blocker is being closed next. Do not write another huge side-task unless it attacks payments, Postgres, settlement, custody/PoR, devnet/validators, bridge, or mainnet.
