#!/usr/bin/env python3
"""ACAP Desktop Node — desktop shell / launcher (stdlib only).

A small LOCAL web app: binds 127.0.0.1 ONLY, serves the wallet-like node UI
(web/index.html) and a local JSON bridge that wires the browser UI to:
  - acap_wallet.py        (local encrypted wallet / key manager)
  - acap_node_manager.py  (local node runtime detection + status)
  - the PUBLIC read-only ACAP/Capacity API (network summary)

Hard limits (enforced here):
  - server binds 127.0.0.1 only — never 0.0.0.0, never a public interface;
  - the private seed is never returned over the bridge or written to logs;
  - no mainnet, no rewards, no custody; status strings stay honest.

Run:  python acap_desktop.py [--port 8599] [--no-browser]
Then open http://127.0.0.1:8599/  (the launcher opens it for you).
"""
import argparse
import json
import os
import socket
import sys
import threading
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(HERE, "web")
sys.path.insert(0, HERE)
import acap_wallet            # noqa: E402
import acap_node_manager      # noqa: E402
import acap_besu_wallet       # noqa: E402

DEFAULT_PORT = 8599
WALLET_PATH = acap_wallet.DEFAULT_WALLET
BESU_WALLET_PATH = acap_besu_wallet.BESU_WALLET
PUBLIC_API = os.environ.get("ACAP_PUBLIC_API", "https://capacity.469diamond.com")


def public_summary():
    try:
        with urllib.request.urlopen(f"{PUBLIC_API}/api/live/summary", timeout=4) as r:
            data = json.load(r)
        return {"ok": True, "source": PUBLIC_API, "summary": data}
    except Exception as e:  # noqa: BLE001 - offline is a normal state
        return {"ok": False, "error": f"offline or unreachable ({type(e).__name__})", "source": PUBLIC_API}


def wallet_status():
    if not os.path.exists(WALLET_PATH):
        return {"exists": False}
    doc = acap_wallet.load_wallet(WALLET_PATH)
    return {
        "exists": True,
        "address": doc.get("address"),
        "network": doc.get("network"),
        "mainnet": False,
        "created": doc.get("created"),
        "locked": True,  # the shell never holds the seed; unlock is per-request verify
    }


def besu_status():
    """Public-safe Besu wallet view — never returns the private key."""
    info = acap_besu_wallet.public_info(BESU_WALLET_PATH)
    return {
        "wallet_modes": ["acap_devnet_identity", "besu_secp256k1"],
        "active_wallet_mode": "besu_secp256k1" if info.get("exists") else "acap_devnet_identity",
        "acap_devnet_identity_available": True,
        "besu_account_available": True,            # real, dependency-free secp256k1+keccak
        "besu_dependency_status": "builtin_pure_python",
        "besu_address": info.get("address"),
        "besu": info,
        "mainnet": False,
    }


def devnet_manifest():
    """Public-safe devnet bundle manifest (addresses + file hashes only; NO private keys)."""
    bundle = acap_node_manager.devnet_bundle()
    out = {
        "present": bundle.get("present"),
        "valid": bundle.get("valid"),
        "non_production": True,
        "chain_id": bundle.get("chain_id"),
        "validators_count": bundle.get("validators_count"),
        "loopback_only": bundle.get("loopback_only"),
        "rpc_exposure": "loopback_only",
        "mainnet": False,
        "rewards": False,
        "errors": bundle.get("errors", []),
    }
    man_path = os.path.join(acap_node_manager.DEVNET_BUNDLE_DIR, "manifest.json")
    if os.path.exists(man_path):
        try:
            man = json.load(open(man_path, encoding="utf-8"))
            # strip nothing sensitive exists, but keep payload small + key-free
            out["manifest"] = {
                "kind": man.get("kind"),
                "consensus": man.get("consensus"),
                "host_allowlist": man.get("host_allowlist"),
                "validators": man.get("validators"),     # addresses only
                "files": man.get("files"),                # sha256 hashes only
                "warning": man.get("warning"),
            }
        except (ValueError, OSError):
            out["manifest"] = None
    return out


def tail_log(n=200):
    p = os.path.join(acap_wallet.acap_data_dir(), "logs", "node.log")
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8", errors="replace") as f:
        return "".join(f.readlines()[-n:])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj))

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    # ---- GET ----
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            return self._serve_file("index.html", "text/html; charset=utf-8")
        if path == "/local-api/wallet/status":
            return self._json(wallet_status())
        if path == "/local-api/besu/status":
            return self._json(besu_status())
        if path == "/local-api/node/status":
            return self._json(acap_node_manager.status())
        if path == "/local-api/deps":
            # Foolproof dependency report (Java 17+, Besu, RPC port, Docker-optional) with
            # exact copy-pasteable fix hints. Read-only — installs nothing, starts nothing.
            return self._json(acap_node_manager.deps())
        if path == "/local-api/devnet/status":
            return self._json(acap_node_manager.devnet_plan())
        if path == "/local-api/devnet/plan":
            return self._json(acap_node_manager.devnet_plan())
        if path == "/local-api/devnet/manifest":
            # Public-safe: bundle manifest lists addresses + file hashes only, never private keys.
            return self._json(devnet_manifest())
        if path == "/local-api/devnet/check":
            return self._json(acap_node_manager.devnet_check())
        if path == "/local-api/devnet/check-command":
            plan = acap_node_manager.devnet_plan()
            return self._json({"check": plan.get("commands", {}).get("check"),
                               "rpc_url": plan.get("rpc_url"),
                               "loopback_only": plan.get("rpc_loopback_only")})
        if path == "/local-api/network":
            return self._json(public_summary())
        if path == "/local-api/logs":
            return self._json({"log": tail_log()})
        if path == "/local-api/diagnostics":
            return self._json({
                "node": acap_node_manager.status(),
                "wallet": wallet_status(),
                "besu": besu_status(),
                "deps": acap_node_manager.deps(),
                "network": public_summary(),
                "public_api": PUBLIC_API,
            })
        if path.startswith("/web/"):
            return self._serve_file(path[len("/web/"):], "text/plain")
        return self._json({"error": "not found"}, 404)

    # ---- POST ----
    def do_POST(self):
        path = self.path.split("?", 1)[0]
        body = self._body()
        if path == "/local-api/wallet/create":
            pw = body.get("password", "")
            try:
                doc = acap_wallet.create_wallet(WALLET_PATH, pw)
                return self._json({"ok": True, "address": doc["address"]})
            except (ValueError, FileExistsError) as e:
                return self._json({"ok": False, "error": str(e)}, 400)
        if path == "/local-api/wallet/unlock":
            pw = body.get("password", "")
            try:
                acap_wallet.unlock_wallet(WALLET_PATH, pw)   # seed discarded immediately
                return self._json({"ok": True})
            except (ValueError, OSError) as e:
                return self._json({"ok": False, "error": str(e)}, 400)
        if path == "/local-api/besu/create":
            pw = body.get("password", "")
            try:
                doc = acap_besu_wallet.create_besu_wallet(BESU_WALLET_PATH, pw)
                return self._json({"ok": True, "address": doc["address"], "mode": "besu_secp256k1"})
            except (ValueError, FileExistsError) as e:
                return self._json({"ok": False, "error": str(e)}, 400)
        if path == "/local-api/besu/unlock":
            pw = body.get("password", "")
            try:
                acap_besu_wallet.unlock_besu_wallet(BESU_WALLET_PATH, pw)  # key discarded immediately
                return self._json({"ok": True})
            except (ValueError, OSError) as e:
                return self._json({"ok": False, "error": str(e)}, 400)
        if path == "/local-api/node/start":
            return self._json(acap_node_manager.start())
        if path == "/local-api/devnet/plan":
            return self._json(acap_node_manager.devnet_plan(body or {}))
        return self._json({"error": "not found"}, 404)

    def _serve_file(self, rel, ctype):
        full = os.path.normpath(os.path.join(WEB_DIR, rel))
        if not full.startswith(WEB_DIR) or not os.path.exists(full):
            return self._json({"error": "not found"}, 404)
        with open(full, "rb") as f:
            return self._send(200, f.read(), ctype)


def main(argv=None):
    p = argparse.ArgumentParser(description="ACAP Desktop Node shell (local web UI)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args(argv)

    # bind loopback ONLY
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print("ACAP Desktop Node — private preview (devnet/testnet only, no mainnet, no rewards).")
    print("Local UI:", url, "  (bound to 127.0.0.1 only — not reachable from the network)")
    if not args.no_browser:
        try:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
