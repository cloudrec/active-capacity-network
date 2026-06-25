#!/usr/bin/env python3
"""ACAP Besu wallet mode — secp256k1 / Ethereum-compatible account (stdlib only).

PRIVATE PREVIEW. Devnet/testnet identity ONLY. This adds a Besu/Ethereum-compatible
account (secp256k1 key + EIP-55 0x-address) ALONGSIDE the existing hash-derived
acap1 identity, with NO third-party dependency: secp256k1 point math and keccak-256
are implemented in pure Python (see acap_keccak.py). It is therefore a REAL Besu
account path, not a dependency-gated stub — but see the security note below.

Hard rules (enforced):
  - the private key is generated locally (os.urandom) and NEVER sent to any server;
  - the private key is stored ONLY inside the password-encrypted wallet file
    (reuses acap_wallet's scrypt + HMAC-SHA256 encrypt-then-MAC);
  - the private key / mnemonic is NEVER printed or logged; only the public 0x-address
    and uncompressed public key are exported;
  - network = acap-private-devnet (chain_id 469469). No mainnet, no funds, no trading.

SECURITY NOTE (honest): pure-Python secp256k1 scalar multiplication here is NOT
constant-time and is intended for devnet/lab identity. For a hardened production
validator/signing key, install a vetted native library (coincurve / eth-keys) on
the build machine — that optimized path is documented in ACAP_BESU_WALLET_MODE.md.
"""
import argparse
import getpass
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import acap_wallet            # noqa: E402  (reuse KDF/encrypt/decrypt + data dir)
from acap_keccak import keccak256   # noqa: E402

NETWORK = "acap-private-devnet"
CHAIN_ID = 469469

# ---------------------------------------------------------------- secp256k1
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_G = (_GX, _GY)


def _inv(a, m):
    return pow(a, m - 2, m)


def _pt_add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    (x1, y1), (x2, y2) = p, q
    if x1 == x2 and (y1 + y2) % _P == 0:
        return None
    if p == q:
        m = (3 * x1 * x1) * _inv(2 * y1, _P) % _P
    else:
        m = (y2 - y1) * _inv((x2 - x1) % _P, _P) % _P
    x3 = (m * m - x1 - x2) % _P
    y3 = (m * (x1 - x3) - y1) % _P
    return (x3, y3)


def _pt_mul(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = _pt_add(result, addend)
        addend = _pt_add(addend, addend)
        k >>= 1
    return result


def privkey_to_pubkey(priv: bytes) -> bytes:
    """Return the 64-byte uncompressed public key (X||Y, no 0x04 prefix)."""
    k = int.from_bytes(priv, "big")
    if not (1 <= k < _N):
        raise ValueError("private key out of range")
    x, y = _pt_mul(k, _G)
    return x.to_bytes(32, "big") + y.to_bytes(32, "big")


def pubkey_to_address(pub64: bytes) -> str:
    """Ethereum/Besu address = 0x + last 20 bytes of keccak256(pubkey), EIP-55 checksummed."""
    h = keccak256(pub64)
    addr = h[-20:].hex()
    chk = keccak256(addr.encode("ascii")).hex()
    out = "0x" + "".join(
        c.upper() if c.isalpha() and int(chk[i], 16) >= 8 else c
        for i, c in enumerate(addr)
    )
    return out


def new_privkey() -> bytes:
    """Generate a valid secp256k1 private key (1 <= k < n)."""
    while True:
        k = os.urandom(32)
        v = int.from_bytes(k, "big")
        if 1 <= v < _N:
            return k


def derive_besu_account(priv: bytes) -> dict:
    pub = privkey_to_pubkey(priv)
    return {
        "address": pubkey_to_address(pub),
        "public_key": "0x04" + pub.hex(),   # uncompressed, with SEC1 0x04 tag
        "network": NETWORK,
        "chain_id": CHAIN_ID,
        "curve": "secp256k1",
        "mainnet": False,
    }


# ---------------------------------------------------------------- wallet file
BESU_WALLET = os.path.join(acap_wallet.acap_data_dir(), "besu_wallet.json")


def create_besu_wallet(path: str, password: str, *, priv: bytes = None) -> dict:
    if os.path.exists(path):
        raise FileExistsError(f"besu wallet already exists: {path} (refusing to overwrite)")
    if len(password) < 8:
        raise ValueError("password too short (min 8 chars). If lost, the key is UNRECOVERABLE.")
    priv = priv if priv is not None else new_privkey()
    acct = derive_besu_account(priv)
    secret = json.dumps({"priv": priv.hex(), "network": NETWORK}).encode()
    enc = acap_wallet.encrypt(secret, password)
    doc = {
        "wallet_version": 1,
        "wallet_mode": "besu_secp256k1",
        "network": NETWORK,
        "chain_id": CHAIN_ID,
        "mainnet": False,
        "created": acap_wallet._now(),
        "address": acct["address"],
        "public_key": acct["public_key"],
        "curve": "secp256k1",
        "enc": enc,
        "warning": "Devnet/testnet secp256k1 key. No funds, not mainnet. UNRECOVERABLE if password lost.",
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return doc


def load_besu_wallet(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unlock_besu_wallet(path: str, password: str) -> bytes:
    """Return the 32-byte private key (in memory only). Raises on bad password."""
    doc = load_besu_wallet(path)
    secret = json.loads(acap_wallet.decrypt(doc["enc"], password))
    return bytes.fromhex(secret["priv"])


def public_info(path: str) -> dict:
    """Public, safe view — never includes the private key."""
    if not os.path.exists(path):
        return {"exists": False, "wallet_mode": "besu_secp256k1"}
    doc = load_besu_wallet(path)
    return {
        "exists": True,
        "wallet_mode": "besu_secp256k1",
        "address": doc.get("address"),
        "public_key": doc.get("public_key"),
        "network": doc.get("network"),
        "chain_id": doc.get("chain_id"),
        "curve": "secp256k1",
        "mainnet": False,
        "created": doc.get("created"),
        "locked": True,
    }


# ---------------------------------------------------------------- self-test
def selftest() -> int:
    fails = 0

    def check(name, cond):
        nonlocal fails
        print(("  PASS: " if cond else "  FAIL: ") + name)
        if not cond:
            fails += 1

    # Well-known secp256k1 -> Ethereum address vectors (priv = 1, 2, 3).
    vectors = {
        1: "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf",
        2: "0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF",
        3: "0x6813Eb9362372EEF6200f3b1dbC3f819671cBA69",
    }
    for k, exp in vectors.items():
        priv = k.to_bytes(32, "big")
        got = pubkey_to_address(privkey_to_pubkey(priv))
        check(f"priv={k} -> {exp}", got == exp)

    # Deterministic: same key -> same address
    pk = new_privkey()
    check("address deterministic for a key", derive_besu_account(pk)["address"] == derive_besu_account(pk)["address"])
    # EIP-55 checksum well-formed (has both cases possible, 0x + 40 hex)
    a = derive_besu_account(pk)["address"]
    check("address shape 0x+40hex", a.startswith("0x") and len(a) == 42)
    # generated keys are in range
    check("key in [1,n)", 1 <= int.from_bytes(pk, "big") < _N)
    # pubkey uncompressed length
    check("pubkey 64 bytes", len(privkey_to_pubkey(pk)) == 64)

    print("BESU WALLET SELFTEST OK" if fails == 0 else f"BESU WALLET SELFTEST FAILED ({fails})")
    return 1 if fails else 0


# ---------------------------------------------------------------- CLI
def main(argv=None):
    p = argparse.ArgumentParser(description="ACAP Besu (secp256k1) wallet — devnet preview")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("create", "address", "unlock", "info"):
        s = sub.add_parser(name)
        s.add_argument("--wallet", default=BESU_WALLET)
    sub.add_parser("selftest")
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "create":
        pw = getpass.getpass("New Besu wallet password (min 8, UNRECOVERABLE if lost): ")
        if pw != getpass.getpass("Confirm password: "):
            print("Passwords do not match."); return 1
        doc = create_besu_wallet(args.wallet, pw)
        print("Besu wallet created:", args.wallet)
        print("Address:", doc["address"], "(secp256k1 devnet account — no funds, not mainnet)")
        return 0
    if args.cmd in ("address", "info"):
        info = public_info(args.wallet)
        print(json.dumps(info, indent=2) if args.cmd == "info" else info.get("address", "(no wallet)"))
        return 0
    if args.cmd == "unlock":
        pw = getpass.getpass("Password: ")
        try:
            unlock_besu_wallet(args.wallet, pw)
            print("OK: password correct (private key kept in memory only, never printed).")
            return 0
        except ValueError as e:
            print("FAILED:", e); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
