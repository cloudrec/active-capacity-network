#!/usr/bin/env python3
"""ACAP Desktop Node — local node manager (stdlib only).

Detects local node runtime + reports an honest status. It NEVER starts a node on a
shared/production server. Start/stop is only offered when an explicit local lab
config is present AND the machine is not flagged as a server.

Node lifecycle states (honest):
  offline                  - no runtime, no config
  bundled_runtime_missing  - lab config present but no Besu/runtime found
  external_besu_detected   - a Besu binary is on PATH / configured
  devnet_config_ready      - lab config + runtime present, not started
  start_disabled_until_runtime - start blocked: runtime missing
  connected_local_devnet   - local RPC answered net_version/eth_blockNumber

Network/sync fields are placeholders until a real local RPC answers. No peer/block
numbers are invented.
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LAB_CONFIG = os.path.join(HERE, "data", "lab_config.json")
DEVNET_BUNDLE_DIR = os.path.join(HERE, "runtime", "devnet")
DEFAULT_RPC = "http://127.0.0.1:8545"
# Chain data lives under the USER profile, never the install dir.
DEVNET_DATA_DIR = os.path.join(os.path.expanduser("~"), ".acap-devnet")
DEVNET_PID_FILE = os.path.join(DEVNET_DATA_DIR, "acap-devnet.pid")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_server_environment() -> bool:
    """Conservative guard: treat as server if a marker file says so or no GUI session.

    On the production host we drop a marker so this module refuses to start a node.
    Desktop users (Windows) won't have it.
    """
    if os.path.exists(os.path.join(HERE, "SERVER_DO_NOT_START")):
        return True
    if os.environ.get("ACAP_SERVER") == "1":
        return True
    return False


def detect_runtime() -> dict:
    """Look for a Besu runtime without executing it.

    Reports the launcher KIND so the UI/plan can prove the Windows package runs `besu.bat`
    (the unix `besu` shell script cannot be executed by cmd.exe). On Windows, a folder that
    ships ONLY the unix `besu` script is REFUSED — `besu_detected` stays false and the kind
    is `unix_script` with a clear hint.
    """
    installer_besu = _installer_besu_bat()
    on_path = shutil.which("besu")
    on_path_bat = shutil.which("besu.bat") if _on_windows() else None
    local = _home_besu_bin()
    found = installer_besu or on_path_bat or on_path or local
    kind = _besu_launcher_kind(found)
    refused = bool(_on_windows() and kind == "unix_script")
    installer_java = _installer_java_exe()
    java_path = installer_java or shutil.which("java")
    out = {
        "besu_path": None if refused else found,
        "besu_detected": bool(found) and not refused,
        "besu_launcher_kind": kind,
        "besu_launcher_refused": refused,
        "besu_source": "installer_runtime" if (found and found == installer_besu) else (
            "path_or_home" if found else None),
        "java_detected": bool(java_path),
        "java_path": java_path,
        "java_source": "installer_runtime" if installer_java else ("system" if java_path else None),
    }
    if refused:
        out["besu_refused_reason"] = (
            "unix_besu_on_windows: only the extensionless unix `besu` shell script was found "
            "in ~/besu/bin. Windows cannot run it via cmd.exe. Unzip the FULL Besu release so "
            "besu.bat is present (it sits next to `besu` in bin\\), then re-check."
        )
        out["besu_unix_only_path"] = found
    return out


def _on_windows() -> bool:
    return os.name == "nt"


def _besu_launcher_kind(path) -> str:
    """Classify a Besu launcher path: windows_batch | native_exe | unix_script | unknown.

    Filename-based (read-only, never executes). `besu.bat`/`.cmd` => windows_batch;
    `besu.exe` => native_exe; extensionless `besu` => unix_script; anything else unknown.
    """
    if not path:
        return "unknown"
    base = os.path.basename(path).lower()
    if base.endswith((".bat", ".cmd")):
        return "windows_batch"
    if base.endswith(".exe"):
        return "native_exe"
    if base == "besu":
        return "unix_script"
    return "unknown"


def _home_besu_bin():
    """Pick a Besu launcher in ~/besu/bin. On Windows PREFER besu.bat over the extensionless
    unix `besu` shell script (the Besu zip ships BOTH; running the unix script via cmd fails).
    On non-Windows prefer the unix `besu` script.
    """
    home_dir = os.path.expanduser(os.path.join("~", "besu", "bin"))
    unix = os.path.join(home_dir, "besu")
    win = os.path.join(home_dir, "besu.bat")
    order = (win, unix) if _on_windows() else (unix, win)
    for cand in order:
        if os.path.exists(cand):
            return cand
    return None


# --- per-user bootstrap-installer runtime (0.6.0) -------------------------------------------
# The one-click installer (ACAP_INSTALL.ps1) drops a portable Java + Besu under
#   %LOCALAPPDATA%\ACAP-Desktop-Node\runtime\{java,besu}
# and writes acap-install-env.ps1 exporting ACAP_LOCAL_RUNTIME / ACAP_JAVA_HOME / ACAP_BESU_BAT.
# These are looked up with the HIGHEST priority so a bootstrap install needs no PATH/folder work.
def _installer_runtime_dir():
    """Return the per-user installer runtime dir (env override wins; else %LOCALAPPDATA%)."""
    env = os.environ.get("ACAP_LOCAL_RUNTIME")
    if env:
        return env
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return os.path.join(base, "ACAP-Desktop-Node", "runtime")
    return None


def _installer_besu_bat():
    """besu.bat from the installer runtime (ACAP_BESU_BAT env, else runtime/besu/bin/besu.bat).

    On Windows we ONLY accept besu.bat here (never the unix `besu` script). On non-Windows
    (CI/tests) we accept either leaf so the path can be exercised.
    """
    p = os.environ.get("ACAP_BESU_BAT")
    if p and os.path.exists(p):
        return p
    rt = _installer_runtime_dir()
    if not rt:
        return None
    leaves = ("besu.bat",) if _on_windows() else ("besu.bat", "besu")
    for leaf in leaves:
        cand = os.path.join(rt, "besu", "bin", leaf)
        if os.path.exists(cand):
            return cand
    return None


def _installer_java_exe():
    """java[.exe] from the installer runtime (ACAP_JAVA_HOME env, else runtime/java/bin/java*)."""
    home = os.environ.get("ACAP_JAVA_HOME")
    roots = []
    if home:
        roots.append(home)
    rt = _installer_runtime_dir()
    if rt:
        roots.append(os.path.join(rt, "java"))
    for root in roots:
        for leaf in ("java.exe", "java"):
            cand = os.path.join(root, "bin", leaf)
            if os.path.exists(cand):
                return cand
    return None


JAVA_MIN_MAJOR = 17
DEVNET_RPC_PORT = 8545


def _run_version(cmd: list) -> str:
    """Run `cmd` and return combined stdout+stderr (version banners often go to stderr).

    Read-only: never starts a node, never opens a socket. Short timeout, fails soft to ''.
    """
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return ((p.stdout or "") + (p.stderr or "")).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _java_major(banner: str):
    """Parse the major version from a `java -version` banner. Handles 1.8.x and 17/21.x."""
    m = re.search(r'version "(\d+)(?:\.(\d+))?', banner)
    if not m:
        return None
    major = int(m.group(1))
    if major == 1 and m.group(2):   # legacy 1.8 style → 8
        major = int(m.group(2))
    return major


def detect_java() -> dict:
    """Detect Java + whether it satisfies Besu's JDK 17+ requirement. Version-aware.

    Prefers the per-user bootstrap-installer runtime (runtime/java/bin/java[.exe]) over PATH.
    """
    installer_java = _installer_java_exe()
    path = installer_java or shutil.which("java")
    out = {"present": bool(path), "path": path, "version_major": None,
           "version_raw": None, "meets_min": False, "min_required": JAVA_MIN_MAJOR,
           "source": "installer_runtime" if installer_java else ("system" if path else None)}
    if not path:
        return out
    banner = _run_version([path, "-version"])
    out["version_raw"] = banner.splitlines()[0] if banner else None
    major = _java_major(banner)
    out["version_major"] = major
    out["meets_min"] = bool(major and major >= JAVA_MIN_MAJOR)
    return out


def detect_besu() -> dict:
    """Detect a Besu binary (PATH or ~/besu/bin) + its version, without executing a node.

    Windows prefers `besu.bat` over the extensionless unix `besu` script (both ship in the
    Besu zip). A Windows folder with ONLY the unix `besu` script is REFUSED (`present=False`,
    `launcher_kind=unix_script`) — cmd.exe cannot run it.
    """
    installer_besu = _installer_besu_bat()
    on_path_bat = shutil.which("besu.bat") if _on_windows() else None
    on_path = shutil.which("besu")
    local = _home_besu_bin()
    found = installer_besu or on_path_bat or on_path or local
    kind = _besu_launcher_kind(found)
    refused = bool(_on_windows() and kind == "unix_script")
    out = {"present": bool(found) and not refused, "path": None if refused else found,
           "on_path": bool(on_path_bat or on_path), "local_folder": local,
           "installer_runtime": installer_besu,
           "source": "installer_runtime" if (found and found == installer_besu) else (
               "path_or_home" if found else None),
           "launcher_kind": kind, "refused": refused, "version": None}
    if refused:
        out["refused_reason"] = (
            "unix_besu_on_windows: found only the unix `besu` script; need besu.bat (unzip the "
            "full Besu release so besu.bat sits in bin\\)."
        )
        return out
    if found:
        banner = _run_version([found, "--version"])
        m = re.search(r"besu/v?([0-9][0-9.\-A-Za-z]*)", banner) or re.search(r"\b(\d+\.\d+\.\d+)", banner)
        if m:
            out["version"] = m.group(1)
    return out


def detect_docker() -> dict:
    """Docker is OPTIONAL (alternative way to run Besu). Detection only, never invoked."""
    path = shutil.which("docker")
    return {"present": bool(path), "path": path, "optional": True}


def deps(rpc_port: int = DEVNET_RPC_PORT) -> dict:
    """Foolproof dependency report for the desktop UI / QA scripts (read-only).

    Reports Java (17+), Besu (+version), Docker (optional), RPC port availability, and an
    overall one-click-devnet readiness with EXACT, copy-pasteable fix hints for anything
    missing. Never installs anything, never starts a node, never opens a public socket.
    """
    java = detect_java()
    besu = detect_besu()
    docker = detect_docker()
    port_free = _port_free(rpc_port)
    server = is_server_environment()

    # When the RPC port is occupied, find out WHO owns it: our own running ACAP devnet
    # (chainId 469469 answering on loopback) is NOT a blocker — it means the devnet is already
    # running. A foreign process on the port IS a blocker.
    devnet_running = False           # our ACAP devnet is up on this port
    foreign_on_port = False          # something else holds the port
    rpc_probe = {"ok": False}
    if not port_free:
        rpc_probe = probe_local_rpc(f"http://127.0.0.1:{rpc_port}")
        if rpc_probe.get("ok") and str(rpc_probe.get("chain_id")) == "469469":
            devnet_running = True
        else:
            foreign_on_port = True

    items = []
    items.append({
        "id": "java", "label": "Java (JDK 17+)", "required_for": "local devnet (Besu)",
        "ok": java["meets_min"], "detail": java["version_raw"] or "not found",
        "fix": None if java["meets_min"] else (
            "Install a JDK 17 or newer (e.g. Eclipse Temurin 21: "
            "https://adoptium.net/temurin/releases/?os=windows). Tick 'Set JAVA_HOME' / "
            "'Add to PATH'. Verify: java -version"
        ) + (f"  [found Java {java['version_major']}, need {JAVA_MIN_MAJOR}+]"
             if java["present"] and not java["meets_min"] else ""),
    })
    items.append({
        "id": "besu", "label": "Hyperledger Besu", "required_for": "local devnet",
        "ok": besu["present"], "detail": (f"besu {besu['version']}" if besu["version"]
                                          else ("found" if besu["present"] else "not found")),
        "fix": None if besu["present"] else (
            "Download Besu (needs Java 17+): https://github.com/hyperledger/besu/releases — "
            "unzip to %USERPROFILE%\\besu, then add %USERPROFILE%\\besu\\bin to PATH "
            "(or just unzip there; this app also auto-detects ~/besu/bin). Verify: besu --version"
        ),
    })
    # RPC port item: free => ready; held by OUR running devnet => OK ("local devnet running",
    # never a blocker); held by a FOREIGN process => blocker.
    if devnet_running:
        rpc_label = f"RPC port {rpc_port}"
        rpc_ok = True
        rpc_detail = (f"local devnet running (chainId 469469 on 127.0.0.1:{rpc_port}, "
                      f"block {rpc_probe.get('block_height')})")
        rpc_fix = None
    elif foreign_on_port:
        rpc_label = f"RPC port {rpc_port} free"
        rpc_ok = False
        rpc_detail = f"in use by ANOTHER process (no ACAP chainId 469469 on 127.0.0.1:{rpc_port})"
        rpc_fix = (
            f"Port {rpc_port} is held by a non-ACAP process. Stop it or pick another port, then "
            f"retry. Check: netstat -ano | findstr :{rpc_port}"
        )
    else:
        rpc_label = f"RPC port {rpc_port} free"
        rpc_ok = True
        rpc_detail = "free"
        rpc_fix = None
    items.append({
        "id": "rpc_port", "label": rpc_label, "required_for": "local devnet",
        "ok": rpc_ok, "detail": rpc_detail, "fix": rpc_fix,
        "devnet_running": devnet_running,
        "blocker_id": "rpc_port_used_by_other_process" if foreign_on_port else None,
    })
    # Docker is optional/informational only — never a blocker.
    items.append({
        "id": "docker", "label": "Docker (optional)", "required_for": "optional Besu-in-container",
        "ok": True, "detail": "present" if docker["present"] else "not installed (optional)",
        "fix": None,
    })

    required_ok = all(i["ok"] for i in items if i["id"] in ("java", "besu", "rpc_port"))
    missing = [i["id"] for i in items if i["id"] in ("java", "besu", "rpc_port") and not i["ok"]]
    # one_click_ready: the toolchain is satisfiable in one click. TRUE when Java+Besu are OK and
    # the port is either free (can start) OR already running OUR devnet. ready_to_start is FALSE
    # while the devnet is already running (nothing to start) — that is success, not a blocker.
    deps_ok = bool(java["meets_min"] and besu["present"]) and not server
    one_click_ready = deps_ok and (bool(port_free) or devnet_running)
    ready_to_start = deps_ok and bool(port_free) and not devnet_running
    if devnet_running:
        summary = ("Local devnet already RUNNING (chainId 469469, loopback RPC). "
                   "Nothing to start — open the Devnet/Home tab.")
    elif server:
        summary = "Refused: server/shared host (devnet never starts here)."
    elif required_ok:
        summary = "All local-devnet dependencies satisfied."
    else:
        summary = "Missing/blocked: " + ", ".join(missing)
    installer_runtime = _installer_runtime_dir()
    return {
        "ts": _now(),
        "server_environment": server,
        "installer_runtime_dir": installer_runtime,
        "installer_runtime_present": bool(_installer_java_exe() or _installer_besu_bat()),
        "java_runtime_source": java.get("source"),
        "besu_runtime_source": besu.get("source"),
        "java": java,
        "besu": besu,
        "docker": docker,
        "rpc_port": rpc_port,
        "rpc_port_free": bool(port_free),
        "devnet_running": devnet_running,
        "devnet_rpc": {"chain_id": rpc_probe.get("chain_id"),
                       "block_height": rpc_probe.get("block_height"),
                       "peer_count": rpc_probe.get("peer_count")} if devnet_running else None,
        "rpc_port_used_by_other_process": foreign_on_port,
        "items": items,
        "all_required_ok": required_ok and not server,
        "one_click_devnet_ready": one_click_ready,
        "ready_to_start": ready_to_start,
        "missing_required": missing,
        "blocked_by_server": server,
        "summary": summary,
        "notes": [
            "Java + Besu are needed ONLY for the optional local devnet; the wallet/UI work without them.",
            "Nothing is installed automatically. Fix hints are copy-pasteable.",
            "Local devnet RPC binds 127.0.0.1 only. No mainnet, no rewards, no public RPC.",
            "Port 8545 in use by the running ACAP devnet (chainId 469469) is NORMAL, not a blocker.",
        ],
    }


def _rpc(method: str, rpc_url: str, timeout: float = 1.5):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode()
    req = urllib.request.Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("result")


def probe_local_rpc(rpc_url: str = DEFAULT_RPC) -> dict:
    """Read-only probe of a LOCAL RPC. Refuses non-loopback URLs (no public RPC)."""
    host = rpc_url.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
    if host not in ("127.0.0.1", "localhost", "::1"):
        return {"ok": False, "error": "refused: RPC must be loopback (no public RPC exposure)"}
    out = {"ok": False, "rpc_url": rpc_url}
    try:
        ver = _rpc("net_version", rpc_url)
        bn = _rpc("eth_blockNumber", rpc_url)
        peers = _rpc("net_peerCount", rpc_url)
        out.update({
            "ok": True,
            "chain_id": ver,
            "block_height": int(bn, 16) if isinstance(bn, str) else None,
            "peer_count": int(peers, 16) if isinstance(peers, str) else None,
        })
    except (urllib.error.URLError, socket.timeout, ValueError, OSError) as e:
        out["error"] = f"no local RPC ({type(e).__name__})"
    return out


def load_lab_config() -> dict:
    if os.path.exists(LAB_CONFIG):
        try:
            return json.load(open(LAB_CONFIG, encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def status() -> dict:
    rt = detect_runtime()
    lab = load_lab_config()
    bundle_present_valid = os.path.isdir(DEVNET_BUNDLE_DIR) and devnet_bundle().get("valid", False)
    # A valid bundled devnet counts as a lab config source (no manual lab_config needed).
    has_lab = bool(lab) or bundle_present_valid
    rpc_url = lab.get("rpc_url", DEFAULT_RPC)
    probe = probe_local_rpc(rpc_url)
    server = is_server_environment()

    if probe.get("ok"):
        state = "connected_local_devnet"
    elif not has_lab and not rt["besu_detected"]:
        state = "offline"
    elif has_lab and not rt["besu_detected"]:
        state = "bundled_runtime_missing"
    elif rt["besu_detected"] and not has_lab:
        state = "external_besu_detected"
    elif has_lab and rt["besu_detected"]:
        state = "devnet_config_ready"
    else:
        state = "offline"

    can_start = (
        state == "devnet_config_ready" and not server and rt["besu_detected"]
    )
    return {
        "ts": _now(),
        "state": state,
        "server_environment": server,
        "can_start": can_start,
        "start_blocked_reason": (
            "running on a server/shared host — start disabled" if server else
            ("runtime missing — start_disabled_until_runtime" if not rt["besu_detected"] else None)
        ),
        "runtime": rt,
        "runtime_source": {
            "java": rt.get("java_source"),
            "besu": rt.get("besu_source"),
            "installer_runtime_dir": _installer_runtime_dir(),
            "installer_runtime_present": bool(_installer_java_exe() or _installer_besu_bat()),
        },
        "lab_config_present": has_lab,
        "rpc_url": rpc_url,
        "rpc": probe,
        "network": {
            "mode": "private-devnet/testnet only",
            "mainnet": False,
            "rewards": False,
            "mining": False,
            "block_height": probe.get("block_height"),
            "peer_count": probe.get("peer_count"),
            "chain_id": probe.get("chain_id"),
            "sync": "live" if probe.get("ok") else "not-connected",
        },
        "logs_path": os.path.join(HERE, "logs"),
        "notes": [
            "No public mainnet. No rewards/mining/staking.",
            "Start is local-lab only and refused on servers.",
            "Block/peer numbers are null until a real local RPC answers.",
        ],
    }


def _is_loopback(rpc_url: str) -> bool:
    host = rpc_url.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
    return host in ("127.0.0.1", "localhost", "::1")


def _port_free(port: int) -> bool:
    """True if nothing is listening on 127.0.0.1:port (best-effort, read-only)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        in_use = s.connect_ex(("127.0.0.1", port)) == 0
        return not in_use
    finally:
        s.close()


def devnet_bundle() -> dict:
    """Discover + validate the bundled NON-PRODUCTION devnet bootstrap (runtime/devnet/).

    Validates, without starting anything:
      - manifest.json parses and self-describes a loopback-only lab bundle;
      - genesis.json exists with the expected chainId + QBFT config + extraData;
      - config.toml binds RPC/P2P to 127.0.0.1 only (no public host);
      - the lab validator key file is present.
    Fails closed: any problem appears in `errors` and `valid` becomes False.
    """
    info = {
        "present": os.path.isdir(DEVNET_BUNDLE_DIR),
        "path": DEVNET_BUNDLE_DIR,
        "valid": False,
        "manifest_ok": False,
        "genesis_ok": False,
        "loopback_only": False,
        "p2p_loopback_only": False,
        "p2p_exposure": None,
        "chain_id": None,
        "validators_count": None,
        "genesis_file": None,
        "config_file": None,
        "validator_key_file": None,
        "non_production": True,
        "errors": [],
    }
    if not info["present"]:
        info["errors"].append("devnet_bundle_missing: runtime/devnet/ not found (download the full ZIP)")
        return info

    man_path = os.path.join(DEVNET_BUNDLE_DIR, "manifest.json")
    gen_path = os.path.join(DEVNET_BUNDLE_DIR, "genesis.json")
    cfg_path = os.path.join(DEVNET_BUNDLE_DIR, "config.toml")
    info["genesis_file"] = gen_path
    info["config_file"] = cfg_path

    # manifest
    try:
        man = json.load(open(man_path, encoding="utf-8"))
        info["chain_id"] = man.get("chain_id")
        info["validators_count"] = man.get("validators_count")
        if man.get("production") is True or man.get("mainnet") is True:
            info["errors"].append("bundle_not_lab: manifest must be NON-PRODUCTION (production/mainnet false)")
        if man.get("rpc_exposure") != "loopback_only":
            info["errors"].append("bundle_rpc_not_loopback: manifest rpc_exposure must be loopback_only")
        keys = man.get("validator_key_files") or []
        if keys:
            kf = os.path.join(DEVNET_BUNDLE_DIR, keys[0])
            info["validator_key_file"] = kf
            if not os.path.exists(kf):
                info["errors"].append("validator_key_missing: " + keys[0])
        else:
            info["errors"].append("validator_key_missing: manifest lists no validator key files")
        info["manifest_ok"] = not any(e.startswith(("bundle_", "validator_key")) for e in info["errors"])
    except (ValueError, OSError) as e:
        info["errors"].append(f"manifest_parse_error: {type(e).__name__}")

    # genesis
    try:
        gen = json.load(open(gen_path, encoding="utf-8"))
        cid = gen.get("config", {}).get("chainId")
        if cid != 469469:
            info["errors"].append(f"genesis_chainid_unexpected: {cid} (want 469469)")
        if "qbft" not in gen.get("config", {}):
            info["errors"].append("genesis_not_qbft: config.qbft missing")
        if not str(gen.get("extraData", "")).startswith("0x"):
            info["errors"].append("genesis_extradata_missing")
        info["chain_id"] = info["chain_id"] or cid
        info["genesis_ok"] = not any(e.startswith("genesis_") for e in info["errors"])
    except (ValueError, OSError) as e:
        info["errors"].append(f"genesis_parse_error: {type(e).__name__}")

    # config.toml loopback binding (text scan — stdlib, no toml dep)
    try:
        cfg = open(cfg_path, encoding="utf-8").read()
        host_ok = 'rpc-http-host="127.0.0.1"' in cfg
        allow_ok = 'host-allowlist=["127.0.0.1"]' in cfg
        # 0.0.0.0 is forbidden anywhere EXCEPT inside a comment line (we ship a comment that
        # explains the historical 0.0.0.0 trap). Scan only non-comment config lines.
        cfg_lines = [ln for ln in cfg.splitlines() if not ln.lstrip().startswith("#")]
        active = "\n".join(cfg_lines)
        no_public = "0.0.0.0" not in active and 'rpc-http-host="*"' not in active
        info["loopback_only"] = host_ok and allow_ok and no_public
        if not info["loopback_only"]:
            info["errors"].append("config_not_loopback: config.toml must bind rpc/host-allowlist to 127.0.0.1 only")

        # P2P posture (0.5.4): accept EITHER P2P fully disabled OR P2P interface bound to
        # loopback. Reject a public-bound or default (0.0.0.0) P2P interface.
        p2p_disabled = "p2p-enabled=false" in active.replace(" ", "")
        p2p_iface_loopback = 'p2p-interface="127.0.0.1"' in active or "p2p-interface='127.0.0.1'" in active
        info["p2p_loopback_only"] = bool(p2p_disabled or p2p_iface_loopback)
        info["p2p_exposure"] = (
            "disabled" if p2p_disabled else ("loopback_only" if p2p_iface_loopback else "unknown")
        )
        if not info["p2p_loopback_only"]:
            info["errors"].append(
                "config_p2p_not_loopback: config.toml must set p2p-enabled=false OR "
                'p2p-interface="127.0.0.1" (Besu p2p-host alone leaves the listener on 0.0.0.0)'
            )
    except OSError as e:
        info["errors"].append(f"config_read_error: {type(e).__name__}")

    info["valid"] = (
        info["manifest_ok"] and info["genesis_ok"] and info["loopback_only"]
        and info["p2p_loopback_only"] and not info["errors"]
    )
    return info


def _win(p: str) -> str:
    """Render a path the way the Windows package will see it (backslashes)."""
    return p.replace("/", "\\")


def devnet_plan(opts: dict = None) -> dict:
    """Local private-devnet runner PLAN — validates the bundle + runtime, fails closed,
    and emits the exact loopback-only start/stop/check commands sourced from the bundled
    runtime/devnet/ bootstrap. It NEVER spawns Besu from here. Refused on servers and for
    any non-loopback RPC.
    """
    opts = opts or {}
    rt = detect_runtime()
    lab = load_lab_config()
    has_lab = bool(lab)
    server = is_server_environment()
    bundle = devnet_bundle()
    rpc_url = (opts.get("rpc_url") or lab.get("rpc_url") or DEFAULT_RPC)
    loopback = _is_loopback(rpc_url)
    chain_id = bundle.get("chain_id") or lab.get("chain_id", 469469)
    try:
        port = int(rpc_url.rsplit(":", 1)[-1].split("/")[0])
    except (ValueError, IndexError):
        port = 8545

    blockers = []
    if server:
        blockers.append("server_environment: never start a devnet on a shared/production host")
    if not loopback:
        blockers.append("non_loopback_rpc: RPC URL must bind 127.0.0.1 only (no public RPC exposure)")
    if not bundle["present"]:
        blockers.append("devnet_bundle_missing: runtime/devnet/ not bundled (download the full ZIP)")
    elif not bundle["valid"]:
        blockers.append("devnet_bundle_invalid: " + "; ".join(bundle["errors"]))
    if not rt["besu_detected"]:
        if rt.get("besu_launcher_refused"):
            blockers.append("besu_launcher_unsupported: " + rt.get("besu_refused_reason",
                            "unix `besu` script on Windows; need besu.bat"))
        else:
            blockers.append("besu_runtime_missing: install Besu and put it on PATH or ~/besu/bin")
    if not rt["java_detected"]:
        blockers.append("java_missing: Besu needs a JDK (Java 17+)")

    # Bundle-sourced, loopback-only command. Chain data under the USER profile.
    genesis = _win(bundle.get("genesis_file") or os.path.join(DEVNET_BUNDLE_DIR, "genesis.json"))
    config = _win(bundle.get("config_file") or os.path.join(DEVNET_BUNDLE_DIR, "config.toml"))
    key = _win(bundle.get("validator_key_file")
               or os.path.join(DEVNET_BUNDLE_DIR, "validators", "validator-1", "key"))
    data_dir = _win(DEVNET_DATA_DIR)
    pid_file = _win(DEVNET_PID_FILE)
    besu_exe = rt.get("besu_path") or "besu"

    # P2P loopback-only posture, sourced from the validated bundle (config.toml disables P2P).
    # We ALSO pass --p2p-enabled=false explicitly on the command line so the safe posture is
    # visible/auditable in the start command and cannot be lost if config.toml is overridden.
    p2p_exposure = bundle.get("p2p_exposure") or "disabled"
    p2p_flags = ["--p2p-enabled=false"]
    besu_launcher_kind = rt.get("besu_launcher_kind", "unknown")
    start_cmd = (
        f"\"{besu_exe}\" --data-path=\"{data_dir}\" --genesis-file=\"{genesis}\" "
        f"--node-private-key-file=\"{key}\" --config-file=\"{config}\" "
        + " ".join(p2p_flags)
    )
    stop_cmd = f"Stop the PID recorded in \"{pid_file}\" (STOP_LOCAL_DEVNET.ps1 does this safely)."
    check_cmd = (
        f"curl -s -X POST http://127.0.0.1:{port} "
        f"-H \"Content-Type: application/json\" "
        f"--data \"{{\\\"jsonrpc\\\":\\\"2.0\\\",\\\"id\\\":1,\\\"method\\\":\\\"eth_blockNumber\\\",\\\"params\\\":[]}}\""
    )

    one_click_ready = (
        not blockers and bundle["valid"] and rt["besu_detected"]
        and rt["java_detected"] and loopback and not server
    )
    can_generate = loopback
    return {
        "ts": _now(),
        "runner": "acap-local-devnet",
        "server_environment": server,
        "rpc_url": rpc_url,
        "rpc_loopback_only": loopback,
        "rpc_port": port,
        "port_free": _port_free(port) if loopback else None,
        "chain_id": chain_id,
        "runtime": rt,
        "besu_launcher_kind": besu_launcher_kind,   # windows_batch | native_exe | unix_script | unknown
        "lab_config_present": has_lab,
        "bundle": bundle,
        "data_dir": data_dir,
        "pid_file": pid_file,
        "ready_to_start": (not blockers),
        "one_click_ready": one_click_ready,
        "one_click_requires_besu_java": True,
        "blockers": blockers,
        "commands": ({
            "start": start_cmd,
            "stop": stop_cmd,
            "check": check_cmd,
        } if can_generate else {"error": "refused: RPC must be loopback"}),
        "scripts": {
            "start": "START_LOCAL_DEVNET.bat / .ps1",
            "stop": "STOP_LOCAL_DEVNET.bat / .ps1",
            "check": "CHECK_LOCAL_DEVNET.bat / .ps1",
        },
        "mainnet": False,
        "rewards": False,
        "mining": False,
        "custody": False,
        "rpc_exposure": "loopback_only",
        # P2P loopback-only posture (0.5.4).
        "p2p_exposure": p2p_exposure,             # "disabled" | "loopback_only"
        "p2p_port": 30303,
        "p2p_public_listener": False,
        "p2p_flags": p2p_flags,
        "notes": [
            "Private devnet/testnet ONLY (QBFT proof-of-authority, chain_id 469469).",
            "Genesis + lab validator key come from the bundled runtime/devnet/ (NON-PRODUCTION).",
            "RPC binds 127.0.0.1 only — never 0.0.0.0/public. No public mainnet, no rewards.",
            "P2P/discovery DISABLED (single validator => no peers). Port 30303 not opened; "
            "peer_count 0 is expected.",
            "Chain data is written under %USERPROFILE%\\.acap-devnet, never the install dir.",
            "Refused on servers (SERVER_DO_NOT_START marker / ACAP_SERVER=1).",
        ],
    }


def devnet_check(rpc_url: str = DEFAULT_RPC) -> dict:
    """Read-only loopback probe for CHECK_LOCAL_DEVNET: chain id, block height, peer count."""
    probe = probe_local_rpc(rpc_url)
    return {
        "ts": _now(),
        "rpc_url": rpc_url,
        "loopback_only": _is_loopback(rpc_url),
        "connected": bool(probe.get("ok")),
        "chain_id": probe.get("chain_id"),
        "block_height": probe.get("block_height"),
        "peer_count": probe.get("peer_count"),
        "error": probe.get("error"),
        "note": "Single-validator devnet: peer_count 0 is normal. Loopback RPC only.",
    }


def start(rpc_url: str = DEFAULT_RPC) -> dict:
    """Guarded: refuses on servers / when runtime missing. Returns the command to run
    rather than spawning Besu from the portal context (the desktop launcher runs it)."""
    st = status()
    if st["server_environment"]:
        return {"started": False, "error": "refused: server environment (never start a node here)"}
    if not st["runtime"]["besu_detected"]:
        return {"started": False, "error": "start_disabled_until_runtime: no Besu runtime found"}
    if not st["lab_config_present"]:
        return {"started": False, "error": "no lab_config.json — configure devnet lab first"}
    lab = load_lab_config()
    return {
        "started": False,
        "action_required": "run the printed command on your lab machine",
        "command": lab.get("start_command", "see ACAP_DESKTOP_NODE_DEVNET_LAB.md"),
        "warning": "RPC must bind 127.0.0.1 / Tailscale IP only — never 0.0.0.0/public.",
    }


DEVNET_P2P_PORT = 30303


def _classify_listen_host(host: str) -> str:
    """loopback | public — classify the local-address host of a LISTEN socket line."""
    h = host.strip().strip("[]")
    if h.startswith("::ffff:"):
        h = h[len("::ffff:"):]
    if h in ("127.0.0.1", "::1") or h.startswith("127."):
        return "loopback"
    if h in ("0.0.0.0", "::", "*"):
        return "public"
    return "public"  # any concrete non-loopback IP is public exposure for our posture


def p2p_listener_audit(port: int = DEVNET_P2P_PORT, sample: str = None) -> dict:
    """Read-only audit: is anything LISTENING on the P2P port on a NON-loopback interface?

    Parses `netstat` (Windows: `netstat -ano`; POSIX fallback `netstat -an`). For tests/CI a
    `sample` netstat dump can be supplied instead of shelling out. Never opens a socket, never
    starts/stops anything. A public listener on :30303 means the loopback-only posture is
    VIOLATED (the bug this fix targets).
    """
    out = {
        "ts": _now(),
        "port": port,
        "public_listener": False,
        "loopback_listener": False,
        "listeners": [],
        "checked": True,
        "source": "sample" if sample is not None else "netstat",
        "note": "",
    }
    text = sample
    if text is None:
        text = _run_version(["netstat", "-ano"]) or _run_version(["netstat", "-an"])
        if not text:
            out["checked"] = False
            out["note"] = "netstat unavailable; could not audit P2P listeners."
            return out

    needle = ":%d" % port
    for line in text.splitlines():
        if needle not in line:
            continue
        low = line.lower()
        # keep only listening TCP rows (Windows 'LISTENING', POSIX 'LISTEN'); UDP discovery
        # rows have no state column on Windows, so also keep UDP rows that mention the port.
        is_tcp_listen = "listen" in low
        is_udp = low.strip().startswith("udp")
        if not (is_tcp_listen or is_udp):
            continue
        # local address is the first token containing :port
        local = next((tok for tok in line.split() if needle in tok), None)
        if not local:
            continue
        host = local.rsplit(":", 1)[0]
        kind = _classify_listen_host(host)
        out["listeners"].append({"local": local, "host": host, "kind": kind,
                                 "proto": "udp" if is_udp else "tcp"})
        if kind == "public":
            out["public_listener"] = True
        else:
            out["loopback_listener"] = True

    if not out["listeners"]:
        out["note"] = ("No P2P listener on :%d (expected: P2P is disabled for the "
                       "single-validator lab)." % port)
    elif out["public_listener"]:
        out["note"] = ("WARNING: P2P listening on a NON-loopback interface (0.0.0.0/[::]) on "
                       ":%d. Loopback-only posture VIOLATED. Set p2p-enabled=false (or "
                       'p2p-interface="127.0.0.1") and restart the devnet.' % port)
    else:
        out["note"] = "P2P listener is loopback-only on :%d." % port
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status(), indent=2))
    elif cmd == "start":
        print(json.dumps(start(), indent=2))
    elif cmd == "detect":
        print(json.dumps(detect_runtime(), indent=2))
    elif cmd == "devnet":
        print(json.dumps(devnet_plan(), indent=2))
    elif cmd == "bundle":
        print(json.dumps(devnet_bundle(), indent=2))
    elif cmd == "check":
        print(json.dumps(devnet_check(), indent=2))
    elif cmd == "deps":
        print(json.dumps(deps(), indent=2))
    elif cmd == "p2p-audit":
        print(json.dumps(p2p_listener_audit(), indent=2))
    else:
        print("usage: acap_node_manager.py "
              "[status|start|detect|deps|devnet|bundle|check|p2p-audit]")
