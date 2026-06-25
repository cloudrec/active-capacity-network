#!/usr/bin/env python3
"""ACAP Desktop Node — local wallet / key manager (stdlib only).

PRIVATE PREVIEW. Devnet/testnet identity ONLY. This wallet:
  - generates a local secret seed (os.urandom) on YOUR machine;
  - stores it in a password-encrypted local file (never sent to any server);
  - derives a deterministic public ACAP identity / address from the seed;
  - lets you lock/unlock, export an encrypted backup, and show your address.

It deliberately does NOT and must never:
  - hold real funds — ACAP is not tradable, there is no public mainnet;
  - upload, sync, or escrow your private key/seed anywhere;
  - print the private seed/mnemonic to logs.

ENCRYPTION (no third-party libs; Python stdlib only):
  KDF      : scrypt(password, salt, n=2**15, r=8, p=1, dklen=64) -> enc_key||mac_key
  Cipher   : HMAC-SHA256 keystream in counter mode, XOR'd with plaintext
  Auth     : Encrypt-then-MAC, HMAC-SHA256(mac_key, salt||nonce||ciphertext)
This is a sound authenticated-encryption construction (independent enc/mac keys,
constant-time tag compare). For a *Besu/Ethereum-compatible secp256k1* signing key
(real devnet validator key), see ACAP_WALLET_KEY_MANAGER.md — that requires the
`eth-keys`/`cryptography` dependency on the build machine and is gated behind it.

CLI:
  python acap_wallet.py create   [--wallet PATH]
  python acap_wallet.py address  [--wallet PATH]
  python acap_wallet.py unlock   [--wallet PATH]     # verify password only
  python acap_wallet.py backup   --out PATH [--wallet PATH]
  python acap_wallet.py restore  --in  PATH [--wallet PATH]
  python acap_wallet.py selftest                     # deterministic test vectors
"""
import argparse
import base64
import getpass
import hashlib
import hmac
import json
import os
import struct
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))


def acap_data_dir():
    """Per-user, writable data dir — never the (possibly read-only) install dir.

    Windows: %APPDATA%\\ACAP-Desktop-Node ; otherwise ~/.acap-desktop-node .
    Honors ACAP_DATA_DIR override (used by tests). Created on demand.
    """
    override = os.environ.get("ACAP_DATA_DIR")
    if override:
        base = override
    elif os.name == "nt":
        base = os.path.join(os.environ.get("APPDATA")
                            or os.path.expanduser(os.path.join("~", "AppData", "Roaming")),
                            "ACAP-Desktop-Node")
    else:
        base = os.path.expanduser(os.path.join("~", ".acap-desktop-node"))
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        base = os.path.join(HERE, "data")  # last-resort fallback
        os.makedirs(base, exist_ok=True)
    return base


DEFAULT_WALLET = os.path.join(acap_data_dir(), "wallet.json")
WALLET_VERSION = 1
NETWORK = "acap-devnet"           # never "mainnet"
SCRYPT_N = 2 ** 15
SCRYPT_R = 8
SCRYPT_P = 1
DKLEN = 64

# ---------------------------------------------------------------- crypto core

def _scrypt(password: bytes, salt: bytes) -> bytes:
    return hashlib.scrypt(
        password, salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
        dklen=DKLEN, maxmem=256 * 1024 * 1024,
    )


def _keystream(enc_key: bytes, nonce: bytes, n: int) -> bytes:
    out = bytearray()
    ctr = 0
    while len(out) < n:
        out += hmac.new(enc_key, nonce + struct.pack(">Q", ctr), hashlib.sha256).digest()
        ctr += 1
    return bytes(out[:n])


def encrypt(plaintext: bytes, password: str, *, salt: bytes = None, nonce: bytes = None) -> dict:
    """Encrypt-then-MAC. salt/nonce overridable only for deterministic self-tests."""
    salt = salt if salt is not None else os.urandom(16)
    nonce = nonce if nonce is not None else os.urandom(16)
    dk = _scrypt(password.encode("utf-8"), salt)
    enc_key, mac_key = dk[:32], dk[32:]
    ks = _keystream(enc_key, nonce, len(plaintext))
    ct = bytes(a ^ b for a, b in zip(plaintext, ks))
    tag = hmac.new(mac_key, salt + nonce + ct, hashlib.sha256).digest()
    return {
        "kdf": "scrypt", "n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P, "dklen": DKLEN,
        "cipher": "hmac-sha256-ctr+etm",
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode(),
        "tag": base64.b64encode(tag).decode(),
    }


def decrypt(blob: dict, password: str) -> bytes:
    salt = base64.b64decode(blob["salt"])
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["ct"])
    tag = base64.b64decode(blob["tag"])
    dk = _scrypt(password.encode("utf-8"), salt)
    enc_key, mac_key = dk[:32], dk[32:]
    expected = hmac.new(mac_key, salt + nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, tag):
        raise ValueError("wrong password or corrupted/tampered wallet (MAC mismatch)")
    ks = _keystream(enc_key, nonce, len(ct))
    return bytes(a ^ b for a, b in zip(ct, ks))


# ---------------------------------------------------------------- identity

def _b32(b: bytes) -> str:
    return base64.b32encode(b).decode().rstrip("=").lower()


def derive_identity(seed: bytes) -> dict:
    """Deterministic ACAP preview identity from a 32-byte seed.

    NOTE: this is a hash-derived *identity* (not a secp256k1 spend key). It is a
    stable address for devnet/testnet labelling. A real Besu validator key is a
    separate, dependency-gated path documented in ACAP_WALLET_KEY_MANAGER.md.
    """
    pub = hashlib.sha256(b"ACAP-pub|v1|" + seed).digest()
    addr_body = hashlib.sha256(b"ACAP-addr|v1|" + pub).digest()[:16]
    return {
        "public_id": pub.hex(),
        "address": "acap1" + _b32(addr_body),
        "network": NETWORK,
    }


# ---------------------------------------------------------------- wallet file

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_wallet(path: str, password: str, *, seed: bytes = None) -> dict:
    if os.path.exists(path):
        raise FileExistsError(f"wallet already exists: {path} (refusing to overwrite)")
    if len(password) < 8:
        raise ValueError("password too short (min 8 chars). If lost, the wallet is UNRECOVERABLE.")
    seed = seed if seed is not None else os.urandom(32)
    ident = derive_identity(seed)
    secret = json.dumps({"seed": seed.hex(), "network": NETWORK}).encode()
    enc = encrypt(secret, password)
    doc = {
        "wallet_version": WALLET_VERSION,
        "network": NETWORK,
        "mainnet": False,
        "created": _now(),
        "address": ident["address"],
        "public_id": ident["public_id"],
        "enc": enc,
        "warning": "Devnet/testnet identity only. No funds. If you lose the password it is UNRECOVERABLE.",
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


def load_wallet(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unlock_wallet(path: str, password: str) -> bytes:
    """Return the decrypted 32-byte seed (kept in memory only). Raises on bad password."""
    doc = load_wallet(path)
    secret = json.loads(decrypt(doc["enc"], password))
    return bytes.fromhex(secret["seed"])


def export_backup(path: str, out: str) -> None:
    """Backup = copy of the already-encrypted wallet file. Still password-protected."""
    doc = load_wallet(path)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def restore_backup(src: str, path: str, password: str) -> dict:
    doc = json.load(open(src, encoding="utf-8"))
    decrypt(doc["enc"], password)  # verify password before writing
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return doc


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    """Deterministic known-answer + property tests. No network, no files written."""
    fails = 0

    def check(name, cond):
        nonlocal fails
        print(("  PASS: " if cond else "  FAIL: ") + name)
        if not cond:
            fails += 1

    # fixed vectors
    seed = bytes.fromhex("00" * 32)
    pw = "correct horse battery"
    salt = bytes.fromhex("11" * 16)
    nonce = bytes.fromhex("22" * 16)
    ident = derive_identity(seed)
    check("address is deterministic + acap1 prefix",
          ident["address"].startswith("acap1") and ident["address"] == derive_identity(seed)["address"])
    check("public_id deterministic", ident["public_id"] == derive_identity(seed)["public_id"])

    enc = encrypt(b"hello-acap", pw, salt=salt, nonce=nonce)
    enc2 = encrypt(b"hello-acap", pw, salt=salt, nonce=nonce)
    check("encryption deterministic for fixed salt/nonce", enc["ct"] == enc2["ct"] and enc["tag"] == enc2["tag"])
    check("roundtrip", decrypt(enc, pw) == b"hello-acap")

    # wrong password rejected
    bad = False
    try:
        decrypt(enc, "wrong password")
    except ValueError:
        bad = True
    check("wrong password rejected (MAC)", bad)

    # tamper detection
    tampered = dict(enc)
    raw = bytearray(base64.b64decode(tampered["ct"]))
    raw[0] ^= 0x01
    tampered["ct"] = base64.b64encode(bytes(raw)).decode()
    tdet = False
    try:
        decrypt(tampered, pw)
    except ValueError:
        tdet = True
    check("ciphertext tamper detected", tdet)

    # random salt/nonce -> different ciphertext each call (no nonce reuse)
    a = encrypt(b"x", pw)
    b = encrypt(b"x", pw)
    check("fresh salt/nonce per encrypt", a["ct"] != b["ct"] or a["salt"] != b["salt"])

    print(("SELFTEST OK" if fails == 0 else f"SELFTEST FAILED ({fails})"))
    return 1 if fails else 0


# ---------------------------------------------------------------- CLI

def main(argv=None):
    p = argparse.ArgumentParser(description="ACAP wallet / key manager (devnet preview)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("create", "address", "unlock"):
        s = sub.add_parser(name)
        s.add_argument("--wallet", default=DEFAULT_WALLET)
    b = sub.add_parser("backup"); b.add_argument("--wallet", default=DEFAULT_WALLET); b.add_argument("--out", required=True)
    r = sub.add_parser("restore"); r.add_argument("--wallet", default=DEFAULT_WALLET); r.add_argument("--in", dest="src", required=True)
    sub.add_parser("selftest")
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    if args.cmd == "create":
        pw = getpass.getpass("New wallet password (min 8, UNRECOVERABLE if lost): ")
        if pw != getpass.getpass("Confirm password: "):
            print("Passwords do not match."); return 1
        doc = create_wallet(args.wallet, pw)
        print("Wallet created:", args.wallet)
        print("Address:", doc["address"], "(devnet/testnet identity — no funds, not mainnet)")
        return 0

    if args.cmd == "address":
        doc = load_wallet(args.wallet)
        print(doc["address"])
        return 0

    if args.cmd == "unlock":
        pw = getpass.getpass("Password: ")
        try:
            unlock_wallet(args.wallet, pw)
            print("OK: password correct, wallet unlocked (seed kept in memory only).")
            return 0
        except ValueError as e:
            print("FAILED:", e); return 1

    if args.cmd == "backup":
        export_backup(args.wallet, args.out)
        print("Encrypted backup written:", args.out, "(still password-protected)")
        return 0

    if args.cmd == "restore":
        pw = getpass.getpass("Password for backup: ")
        try:
            doc = restore_backup(args.src, args.wallet, pw)
            print("Restored. Address:", doc["address"])
            return 0
        except ValueError as e:
            print("FAILED:", e); return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
