# ACAP Desktop Node (wallet-like shell) — quick start

**Private preview. Devnet/testnet only. No public mainnet. No rewards, mining, or staking.
No custody — your keys stay on your machine.**

## Run
1. Install Python 3 (https://www.python.org/downloads/, tick *Add to PATH*).
2. Double-click **`START_ACAP_DESKTOP.bat`** (or run `START_ACAP_DESKTOP.ps1`).
3. Your browser opens **http://127.0.0.1:8599/** — the local UI.
   The server binds **127.0.0.1 only**; nothing is exposed to your network or the internet.

## What you get
- **Home / Status** — node state, Besu/Java detection, local RPC, block/peer (— until a local devnet runs).
- **Wallet** — create an encrypted local wallet, see your `acap1…` devnet address, unlock to verify password.
- **Network** — read-only public ACAP network summary (works only when online).
- **Node logs** — tail of `logs/node.log`.
- **Diagnostics** — copyable status bundle (no secrets / private keys).
- **Update / Info** — honest mode flags; check the portal node page for the latest package + SHA-256.

## Wallet safety
- Encryption: scrypt + HMAC-SHA256 (encrypt-then-MAC), Python stdlib only.
- The wallet file lives in `data/wallet.json` on **your** machine. **If you lose the password it is
  unrecoverable** — there is no server copy. Back it up (Wallet → backup is still encrypted).
- The private seed is never sent over the local bridge, never uploaded, never written to logs.

## CLI (optional, no browser)
```
python acap_wallet.py create        # create encrypted wallet
python acap_wallet.py address       # print your devnet address
python acap_wallet.py selftest      # run crypto self-tests
python acap_node_manager.py status  # JSON node status
```

## Running a local devnet (advanced / lab only)
This shell does NOT start a blockchain on your behalf, and **never** on a server. To run a real
private devnet, see `ACAP_DESKTOP_NODE_DEVNET_LAB.md` (Besu QBFT, RPC bound to 127.0.0.1 /
Tailscale only). Once your local RPC answers, the Home tab flips to `connected_local_devnet`.
