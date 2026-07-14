# Node Operator Guide

> **Preview node.** Read-only by default. No mining, no rewards, no autostart,
> holds no keys by default, binds to `127.0.0.1` only. No mainnet.

The ACAP Desktop Node source lives in [`../desktop-node/`](../desktop-node/).

## Node roles

- **Light node** — polls public-safe status from the preview portal; read-only.
  Launchers: `START_LIGHT_NODE.bat`, `START_CAPACITY_NODE.bat`.
- **Desktop node** — local desktop shell + web UI on `127.0.0.1`.
  Launchers: `START_ACAP_DESKTOP.bat` / `.ps1`.
- **Local devnet validator** — only via the loopback QBFT devnet (see
  [DEVNET_GUIDE.md](DEVNET_GUIDE.md)). Requires Besu + Java.

See `desktop-node/NODE_ROLES.md` for the full breakdown.

## What it does and does not do

- ✅ Runs locally, read-only, on loopback.
- ✅ Optional local wallet code is local-only; private keys/seeds are **never**
  printed or logged (only the public `0x` address is shown).
- ❌ No public RPC, no mining, no rewards, no autostart, no admin rights.

## Requirements

- **Windows** for the packaged launchers and installer.
- **Python 3** for the stdlib node (`acap_desktop.py`). The full release ZIP can
  bundle an embedded Python; this source tree expects a system Python 3.
- **Besu + Java 17+** only if you want the local devnet.

## Run (Windows, from source)

1. Open [`../desktop-node/`](../desktop-node/).
2. Read `README_FIRST_RUN_WINDOWS.md` and `README_DESKTOP_NODE.md`.
3. Start a launcher:
   - Light/read-only: `START_LIGHT_NODE.bat`
   - Desktop shell + UI: `START_ACAP_DESKTOP.bat`
4. The web UI opens on `http://127.0.0.1:<port>` (loopback only).

## Run the Python node directly

```bash
python3 desktop-node/acap_desktop.py
```

It boots on `127.0.0.1` only and serves `desktop-node/web/index.html`.

## QA / diagnostics

Read-only Windows QA scripts are in `desktop-node/qa/windows/` (e.g.
`RUN_FULL_QA.bat`, `CHECK_ENVIRONMENT.ps1`). They never create wallets and never
print keys/seeds/passwords. `COLLECT_DIAGNOSTICS.ps1` excludes wallet files,
private keys, seeds, mnemonics, and passwords.

## Configuration

Copy the examples and edit locally (never commit real values):

- `desktop-node/config.example.json` → `config.json`
- `desktop-node/.env.example` → `.env`
- `desktop-node/lab_config.example.json` → `data/lab_config.json` (lab machine
  only; enables local devnet status — never on a server).

## Troubleshooting

See `desktop-node/TROUBLESHOOTING_WINDOWS_NODE.md` and
`desktop-node/TROUBLESHOOTING_WINDOWS.md`.

## Signed node enrolment (preview)

ACAP supports a signed node enrolment protocol (`ACAP_NODE_ENROLMENT_V1`, Ed25519).

What it is — and is not:

- A valid signature proves **control of a private key ONLY**. It does **not** prove
  identity, trustworthiness, uptime, location, hardware capacity, or validator eligibility.
- A successful enrolment makes the node an **observer with zero voting power** — not a
  validator, no rewards, no consensus membership, no mainnet.
- Validator admission is a **separate, paused-by-default preview workflow**. No signature
  ever creates a candidate or validator or grants voting power.

Key safety:

- The node generates its Ed25519 identity key **locally**. The private key is never sent
  to the server, never logged, and never placed in a URL. The server stores only the
  public key + fingerprint + status.
- Do **not** reuse the node identity key as a wallet, payment, or consensus key. Back up
  the local key file securely.

Flow: request enrolment (public key + safe metadata) → receive a single-use, short-lived
challenge → review and sign the exact payload locally → submit the signature → the
operator explicitly registers the node as an observer. Key rotation uses a dual-signature
(old + new) challenge; lost-key recovery is admin-gated with a cooldown; revocation
immediately blocks further use.

## Governance state durability (Stage 8D)

Node identity, enrolments, keys, challenges, the identity audit, admission proposals and
activation evidence are held in a durable, transactional governance store rather than loose
files. Each enrolment/rotation/revocation step commits atomically (a crash never leaves a
half-written state), a challenge nonce can be consumed only once, one active key fingerprint
can bind to only one node, and the identity audit is a fork-proof, per-stream hash chain you
can verify. The server still stores only your PUBLIC key + fingerprint — never a private key,
and never the raw challenge nonce. None of this activates a validator, grants voting power, or
starts consensus; validator admission stays disabled + paused and every node stays an observer
with zero voting power.

## Multi-operator governance identities (Stage 8E)

Governance actions (proposing a validator candidate, approving it, signing off) are attributed
to registered GOVERNANCE PRINCIPALS with separated roles (proposer / approver / owner sign-off /
auditor). A principal authenticates with a bearer token issued server-side and shown once — only
its hash is stored, never the token itself. Because a real production activation four-eyes now
requires DISTINCT registered principals for the approver and owner sign-off (independent of the
creator and proposer), a single operator acting alone stays production NO-GO. This is governance
plumbing only: it never activates a validator, grants voting power, or starts consensus; every
node stays an observer with zero voting power and validator admission stays disabled + paused.

## Consensus lab + security-review prep (Stage 8F)

Consensus safety and liveness are studied in a SANDBOXED lab — a deterministic simulator that is
a pure function of the scenario it is given (validator power, operator share, crash / byzantine
faults). It never touches any live network state, never admits or activates a validator, and
starts no consensus; it only produces analysis (safety / liveness / operator-majority / BFT
tolerance). Alongside it, a machine-readable security-review pack asserts the standing safety
invariants of the whole stack and produces a redacted evidence bundle for an external reviewer
that contains no secret material. Neither claims mainnet readiness or attack resistance.

## Adversarial self-audit (Stage 8G)

The governance safety invariants are not only asserted — they are attacked. An executable
red-team harness actively tries to break each one (forge a token, replay a challenge, bind a
duplicate key, fork the audit chain, bypass four-eyes, push an override to production, leak a
token, activate a validator, escape the consensus lab, tamper the store, reuse stale evidence)
and proves every attack is blocked. It runs only against a throwaway store — never the production
database — and activates nothing. A passing run means every attack failed; it is an internal
check, not a substitute for an external independent security review.

Everything here is private preview / readiness. No mainnet, rewards, or live consensus.
