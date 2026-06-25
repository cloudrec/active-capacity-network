#!/usr/bin/env python3
"""Release/package verifier: validates tokenomics invariants and runs the secret +
claim scans. Use before publishing or cutting a release.

Run:  python3 scripts/verify_release.py   (0 = all pass, 1 = any failure)
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_tokenomics() -> list[str]:
    errs: list[str] = []
    p = ROOT / "tokenomics" / "acap_tokenomics.json"
    if not p.exists():
        return [f"missing {p}"]
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return [f"tokenomics JSON invalid: {e}"]

    def want(key, val):
        if d.get(key) != val:
            errs.append(f"tokenomics.{key} = {d.get(key)!r}, expected {val!r}")

    want("max_supply", 1_000_000_000)
    want("decimals", 18)
    want("sale_active", False)
    want("reservation_active", False)
    want("buy_enabled", False)
    want("available_for_reservation", 0)
    want("contract_deployed", False)
    if d.get("contract_address") not in (None, ""):
        errs.append(f"tokenomics.contract_address must be null, got {d.get('contract_address')!r}")
    if d.get("mainnet") is True:
        errs.append("tokenomics.mainnet must be false")
    if d.get("preview") is not True:
        errs.append("tokenomics.preview must be true")

    # allocation must sum to 100% and to max supply.
    allocs = d.get("allocations", [])
    pct = sum(a.get("percent", 0) for a in allocs)
    tok = sum(a.get("tokens", 0) for a in allocs)
    if pct != 100:
        errs.append(f"allocation percent sums to {pct}, expected 100")
    if tok != 1_000_000_000:
        errs.append(f"allocation tokens sum to {tok:,}, expected 1,000,000,000")

    mint = d.get("minting", {})
    if mint.get("unlimited_mint") is not False:
        errs.append("minting.unlimited_mint must be false")
    if mint.get("hard_cap") != 1_000_000_000:
        errs.append("minting.hard_cap must be 1,000,000,000")
    return errs


def validate_all_json() -> list[str]:
    errs: list[str] = []
    skip = {".git", "node_modules", "bin", "obj", "__pycache__"}
    for p in ROOT.rglob("*.json"):
        if set(p.relative_to(ROOT).parts) & skip:
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            errs.append(f"invalid JSON {p.relative_to(ROOT)}: {e}")
    return errs


def run(script: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main() -> int:
    failed = False

    print("== tokenomics invariants ==")
    terrs = check_tokenomics()
    if terrs:
        failed = True
        for e in terrs:
            print("  FAIL " + e)
    else:
        print("  PASS")

    print("== JSON validity ==")
    jerrs = validate_all_json()
    if jerrs:
        failed = True
        for e in jerrs:
            print("  FAIL " + e)
    else:
        print("  PASS")

    for script in ("check_no_secrets.py", "check_claims.py"):
        print(f"== {script} ==")
        code, out = run(script)
        print("  " + out.replace("\n", "\n  "))
        if code != 0:
            failed = True

    print("\nRELEASE VERIFY: " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
