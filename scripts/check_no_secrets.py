#!/usr/bin/env python3
"""Fail if the repository contains secrets, private keys, .env content, or credentials.

Run from the repo root:  python3 scripts/check_no_secrets.py
Exit code 0 = clean, 1 = findings.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files/dirs we never scan (binary, vendored, build, the scanner's own patterns).
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "bin", "obj",
             "runtime/python"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".7z", ".gz",
               ".exe", ".dll", ".pyd", ".so", ".pdb", ".cat", ".pth"}
# This scanner and the claim scanner both legitimately contain pattern strings.
SELF = {"scripts/check_no_secrets.py", "scripts/check_claims.py",
        "scripts/verify_release.py"}

# secp256k1 field/order/generator constants — legitimately appear in wallet math.
ALLOW_HEX = {
    "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
    "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    "0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
    "0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",
}

PATTERNS = [
    ("PEM private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[0-9A-Za-z-]{10,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{30,}\b")),
    ("Bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}")),
    ("Generic mnemonic", re.compile(r"\b(?:mnemonic|seed[_ ]?phrase)\b\s*[:=]\s*['\"][a-z ]{20,}['\"]", re.I)),
]

# 64-hex private key (with optional 0x). Allowlist curve constants + obvious hashes.
HEX64 = re.compile(r"\b(0x)?[0-9a-fA-F]{64}\b")
# secret-ish assignment with a real-looking value
ASSIGN = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|secret|password|passwd|token|access[_-]?key|private[_-]?key)\b\s*[:=]\s*['\"]([^'\"]{6,})['\"]"
)
PLACEHOLDER = re.compile(
    r"(?i)(change[-_ ]?me|example|placeholder|replace[_-]?with|your[-_ ]?|set-a-|<[^>]+>|xxx+|0{8,}|todo|dummy|sample|n/a|none)"
)
# field where a 64-hex is a public artifact, not a secret
PUBLIC_HEX_CONTEXT = re.compile(r"(?i)(sha256|sha-256|checksum|hash|mixhash|extradata|key\.pub|pubkey|public[_-]?key|address|enode|nodekey_pub)")


def is_text(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIX:
        return False
    try:
        path.read_text(encoding="utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def skip(path: Path) -> bool:
    r = rel(path)
    if r in SELF:
        return True
    parts = set(Path(r).parts)
    if parts & SKIP_DIRS:
        return True
    if "runtime/python" in r:
        return True
    # the devnet validator private key must never exist; the placeholder may.
    return False


def main() -> int:
    findings: list[str] = []
    # Hard rule: a real private-key file must not exist.
    for p in ROOT.rglob("validators/*/key"):
        findings.append(f"{rel(p)}: FORBIDDEN real validator private-key file present")

    for path in ROOT.rglob("*"):
        if not path.is_file() or skip(path) or not is_text(path):
            continue
        r = rel(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, pat in PATTERNS:
                if pat.search(line):
                    findings.append(f"{r}:{lineno}: {name}")
            m = ASSIGN.search(line)
            if m and not PLACEHOLDER.search(m.group(2)):
                findings.append(f"{r}:{lineno}: hardcoded {m.group(1).lower()} = '{m.group(2)[:6]}…'")
            for hm in HEX64.finditer(line):
                val = hm.group(0)
                up = val.upper() if val.startswith("0x") else ("0x" + val.upper())
                if up in ALLOW_HEX:
                    continue
                if PUBLIC_HEX_CONTEXT.search(line):
                    continue
                # a bare 64-hex with a 0x prefix in a 'key' file = likely privkey
                if val.startswith("0x") and ("key" in r.lower() and "key.pub" not in r.lower()
                                             and "key.example" not in r.lower()):
                    findings.append(f"{r}:{lineno}: possible private key {val[:10]}…")

    if findings:
        print("SECRET SCAN: FAIL")
        for f in findings:
            print("  " + f)
        return 1
    print("SECRET SCAN: PASS (no secrets / private keys / credentials found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
