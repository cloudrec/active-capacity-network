#!/usr/bin/env python3
"""Fail if the repo makes unsafe claims (live mainnet/rewards/custody/trading,
a fake contract address, or a Buy/sale-active flow).

A claim is only a violation when it asserts the thing is LIVE/ACTIVE. Negations
("no public mainnet", "not live", "sale_active=false") are allowed and expected.

Run:  python3 scripts/check_claims.py    (0 = clean, 1 = findings)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = {"scripts/check_claims.py", "scripts/check_no_secrets.py",
        "scripts/verify_release.py"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "bin", "obj"}
TEXT_SUFFIX = {".md", ".txt", ".json", ".html", ".js", ".py", ".ps1", ".bat",
               ".toml", ".yml", ".yaml", ".cs", ".csproj"}

# Negation / safe context. Matched in a window that spans wrapped lines so a
# sentence like "No custody, trading, ... are live." is recognised as safe even
# when it wraps onto the line the claim regex hits.
NEG = re.compile(
    r"(?i)\b(no|not|never|without|disabled?|false|planned|prototype|preview|"
    r"draft|design|future|gated|will|would|once|when|if|cannot|can't|n[o']t|"
    r"don't|does not|isn't|aren't|demonstration|demo|mock|simulat|example|"
    r"placeholder|refus|reject|deny|forbid|prohibit|fabricat|fake|decline|"
    r"out of scope|unsafe|fail|must not|claim that|implying)\b"
)

# (label, regex asserting the unsafe thing). We then require NO negation nearby.
CLAIMS = [
    ("live mainnet", re.compile(r"(?i)\b(mainnet)\b\s+(is|are)?\s*(now\s+)?(live|launched|running|open|available)")),
    ("live rewards", re.compile(r"(?i)\b(rewards?|staking\s+yield|apy|apr)\b\s+(are|is)\s+(live|active|enabled|paid|guaranteed)")),
    ("live custody", re.compile(r"(?i)\bcustody\b\s+(is|are)\s+(live|available|enabled|active)")),
    ("live trading", re.compile(r"(?i)\b(trading|listed|listing|exchange\s+listing|liquidity)\b\s+(is|are)\s+(live|active|open|available)")),
    ("live bridge", re.compile(r"(?i)\bbridge\b\s+(is|are)\s+(live|active|enabled|available)")),
    ("live payments", re.compile(r"(?i)\b(payments?|payment\s+processing)\b\s+(is|are)\s+(live|active|enabled|available)")),
    ("buy/sale active", re.compile(r"(?i)\b(buy\s+now|sale\s+is\s+(live|open|active)|token\s+sale\s+(is\s+)?(live|open)|invest\s+now|presale\s+(is\s+)?(live|open))\b")),
]

# Fake contract address: a non-null 0x40-hex presented as THE contract address.
CONTRACT_LINE = re.compile(r"(?i)contract[_\s]*address")
ETH_ADDR = re.compile(r"0x[a-fA-F0-9]{40}\b")


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


def context_ok(text: str, start: int) -> bool:
    """True if a negation/safe word appears near the match, across wrapped lines.

    Looks back 140 chars and ahead 80 chars (newlines collapsed to spaces) so a
    safety sentence that wraps still clears the claim on the wrapped line.
    """
    window = text[max(0, start - 140):start + 80].replace("\n", " ")
    return bool(NEG.search(window))


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        r = rel(path)
        if r in SELF or set(Path(r).parts) & SKIP_DIRS:
            continue
        if path.suffix.lower() not in TEXT_SUFFIX:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pat in CLAIMS:
            for m in pat.finditer(text):
                if not context_ok(text, m.start()):
                    ln = line_of(text, m.start())
                    snippet = text[m.start():m.start() + 90].splitlines()[0]
                    findings.append(f"{r}:{ln}: unsafe claim ({label}): {snippet.strip()}")
        for lineno, line in enumerate(text.splitlines(), 1):
            if CONTRACT_LINE.search(line):
                for am in ETH_ADDR.finditer(line):
                    findings.append(f"{r}:{lineno}: contract address present (must be null): {am.group(0)}")

    # tokenomics JSON must keep the safe flags.
    tj = ROOT / "tokenomics" / "acap_tokenomics.json"
    if tj.exists():
        data = json.loads(tj.read_text())
        if data.get("contract_address") not in (None, "", "null"):
            findings.append("tokenomics: contract_address must be null")
        for flag in ("sale_active", "reservation_active", "buy_enabled"):
            if data.get(flag) is True:
                findings.append(f"tokenomics: {flag} must be false in preview")

    if findings:
        print("CLAIM SCAN: FAIL")
        for f in findings:
            print("  " + f)
        return 1
    print("CLAIM SCAN: PASS (no live-mainnet/rewards/custody/trading/sale claims, no fake contract)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
