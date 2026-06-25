# FAQ

> **Preview/prototype.** No mainnet, sale, custody, bridge, payments, trading, or
> live rewards. Not investment advice.

**Is there a live mainnet?**
No. There is no public mainnet. Chain-style data shown anywhere is demonstration
data and is labeled as such.

**Can I buy ACAP / is there a token sale?**
No. `sale_active=false`, `reservation_active=false`, `buy_enabled=false`. There is
no Buy button, no public sale, and no reservation open.

**Is there a token contract / contract address?**
No. `contract_deployed=false` and `contract_address=null`. No on-chain contract is
deployed. Anyone showing an "ACAP contract address" is not us.

**Do I earn rewards or staking yield by running a node?**
No. There are no live rewards, no staking yield, and no mining. The node is
read-only by default and the devnet produces no value.

**Is ACAP tradable / listed on an exchange?**
No. No trading, no listing, no liquidity is live. The liquidity reserve in the
tokenomics is a planned allocation, not an active market.

**What's the max supply and decimals?**
1,000,000,000 ACAP (fixed hard cap, no unlimited mint), 18 decimals.

**What is "active capacity reservation"?**
A model where you reserve **active network capacity** rather than leasing tokens
for a fixed term. ACAP stays yours; nothing expires or is confiscated. See
[ACTIVE_CAPACITY_RESERVATION.md](ACTIVE_CAPACITY_RESERVATION.md). It is currently
disabled.

**Is the devnet safe to run?**
Yes, locally. It is loopback-only with P2P disabled and uses lab-only keys. Never
expose its RPC publicly and never reuse the lab key. See
[DEVNET_GUIDE.md](DEVNET_GUIDE.md).

**Does the installer need admin rights?**
No. It installs per-user, doesn't touch global PATH, installs no service, and
verifies every download over HTTPS with SHA-256.

**Where are the private keys?**
Not in this repo. We never publish private keys, mnemonics, `.env` files,
credentials, or database dumps. The devnet ships a placeholder; you generate your
own lab key.

**Will the tokenomics change?**
Possibly. They are a draft/preview and changes are versioned in the changelog. The
JSON (`tokenomics/acap_tokenomics.json`) is the source of truth.

**How do I report a security issue?**
Privately — see [../SECURITY.md](../SECURITY.md). Do not open a public issue for
secrets or vulnerabilities.
