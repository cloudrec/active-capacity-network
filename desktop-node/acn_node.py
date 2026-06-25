#!/usr/bin/env python3
"""Active Capacity Network — Preview Node Client (Windows / cross-platform).

PRIVATE PREVIEW / PROTOTYPE. This client is a *read-only preview node*. It:
  - connects to the PUBLIC Active Capacity / Auction APIs over HTTPS;
  - displays local sync status and network summary;
  - writes logs to a local ./logs folder;
  - can register a *local node profile* and submit it as a PREVIEW REQUEST only
    (never an approved validator);
  - can export a diagnostics zip for support.

It deliberately DOES NOT, and must never:
  - mine, stake, or earn rewards (there are none);
  - run hidden background processes or autostart without explicit user action;
  - hold or generate private keys unless you explicitly run `keygen` yourself;
  - transmit private files, credentials, or scan your machine.

No mainnet, no custody, no payments, no bridge. Standard-library only (no pip install).
"""
import argparse
import json
import os
import platform
import socket
import sys
import time
import urllib.request
import urllib.error
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HERE, "logs")
PROFILE_PATH = os.path.join(HERE, "data", "node_profile.json")
DEFAULT_CONFIG = os.path.join(HERE, "config.json")
EXAMPLE_CONFIG = os.path.join(HERE, "config.example.json")
VERSION = "0.1.0-preview"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    line = f"[{_now()}] {msg}"
    print(line)
    try:
        with open(os.path.join(LOG_DIR, "node.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_config():
    path = DEFAULT_CONFIG if os.path.exists(DEFAULT_CONFIG) else EXAMPLE_CONFIG
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    cfg.setdefault("capacity_base", os.environ.get("ACN_CAPACITY_BASE", "https://capacity.469diamond.com"))
    cfg.setdefault("auction_base", os.environ.get("ACN_AUCTION_BASE", "https://auction.469diamond.com"))
    cfg.setdefault("role", os.environ.get("ACN_NODE_ROLE", "light"))
    cfg.setdefault("poll_seconds", 60)
    cfg.setdefault("node_name", socket.gethostname())
    return cfg


def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": f"acn-preview-node/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_status(cfg):
    base = cfg["capacity_base"].rstrip("/")
    out = {"client_version": VERSION, "checked_at": _now(), "role": cfg["role"],
           "capacity_base": base, "ok": False}
    try:
        health = http_get(base + "/api/health")
        summary = http_get(base + "/api/live/summary")
        out["ok"] = bool(health.get("ok"))
        out["preview"] = health.get("preview", True)
        out["mainnet"] = health.get("mainnet", False)
        out["last_synced"] = summary.get("last_synced")
        out["stale"] = summary.get("stale")
        vs = summary.get("validators") or summary.get("validator_count")
        out["validators"] = vs if isinstance(vs, int) else (len(vs) if isinstance(vs, list) else None)
        log(f"status ok role={cfg['role']} stale={out.get('stale')}")
    except Exception as e:  # noqa
        out["error"] = str(e)
        log(f"status error: {e}")
    print(json.dumps(out, indent=2))
    return out


def cmd_run(cfg):
    """Foreground preview loop. Polls public APIs, logs status. Ctrl+C to stop.
    No background daemon, no autostart, no mining."""
    role = cfg["role"]
    interval = int(cfg.get("poll_seconds", 60))
    log(f"preview node starting (role={role}, poll={interval}s). Read-only. Ctrl+C to stop.")
    print("Active Capacity preview node running. This is a private-preview, read-only client.")
    print("It does not mine, earn rewards, or run in the background. Press Ctrl+C to stop.\n")
    try:
        while True:
            cmd_status(cfg)
            if role == "validator":
                print("NOTE: validator role here is documentation/preview only. Apply via the "
                      "capacity site validator-apply form; this client cannot self-approve.")
            time.sleep(interval)
    except KeyboardInterrupt:
        log("preview node stopped by user")
        print("\nStopped.")


def cmd_register(cfg, contact):
    """Submit a LOCAL node profile as a preview request (not validator approval)."""
    profile = {
        "node_name": cfg["node_name"],
        "role_requested": cfg["role"],
        "os": platform.system(),
        "os_release": platform.release(),
        "client_version": VERSION,
        "contact": contact or "",
        "created_at": _now(),
        "note": "preview node profile — not an approved validator",
    }
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    log(f"local node profile saved: {PROFILE_PATH}")
    print("Saved local node profile (preview only). To request validator access, use the")
    print(f"validator-apply form at {cfg['capacity_base'].rstrip('/')}/#/validator-apply")
    print(json.dumps(profile, indent=2))


def cmd_diagnostics(cfg):
    """Export a diagnostics zip (logs + non-secret config + status). No private files."""
    os.makedirs(LOG_DIR, exist_ok=True)
    status = cmd_status(cfg)
    out_zip = os.path.join(HERE, f"acn-diagnostics-{int(time.time())}.zip")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("status.json", json.dumps(status, indent=2))
        z.writestr("environment.json", json.dumps({
            "python": sys.version, "platform": platform.platform(),
            "client_version": VERSION, "exported_at": _now(),
        }, indent=2))
        log_file = os.path.join(LOG_DIR, "node.log")
        if os.path.exists(log_file):
            z.write(log_file, "logs/node.log")
        if os.path.exists(PROFILE_PATH):
            z.write(PROFILE_PATH, "node_profile.json")
    print(f"Diagnostics written: {out_zip}")
    print("Contains: status, environment, local logs and local node profile only. No secrets.")


def main():
    p = argparse.ArgumentParser(description="Active Capacity Network preview node (read-only).")
    p.add_argument("command", nargs="?", default="status",
                   choices=["status", "run", "register", "diagnostics", "version"],
                   help="status (default) | run | register | diagnostics | version")
    p.add_argument("--role", choices=["light", "capacity", "validator"], help="override node role")
    p.add_argument("--contact", help="contact for register (optional)")
    args = p.parse_args()

    cfg = load_config()
    if args.role:
        cfg["role"] = args.role

    if args.command == "version":
        print(json.dumps({"client_version": VERSION, "preview": True, "mainnet": False}, indent=2))
    elif args.command == "status":
        cmd_status(cfg)
    elif args.command == "run":
        cmd_run(cfg)
    elif args.command == "register":
        cmd_register(cfg, args.contact)
    elif args.command == "diagnostics":
        cmd_diagnostics(cfg)


if __name__ == "__main__":
    main()
