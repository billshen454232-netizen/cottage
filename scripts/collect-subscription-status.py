#!/usr/bin/env python3
"""Generate TTLINK subscription status JSON.

First version: safe local/remote collector skeleton.
- Reads service status when systemctl exists.
- Reads listening ports when ss exists.
- Reads subscription YAML markers when a YAML path is provided.
- Leaves traffic API integration as nullable fields for a later step.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SUBS_DIR = Path("/etc/letsencrypt/subs")
DEFAULT_SUBS_BASE_URL = "https://subs.ttlink.asia/subs"
DEFAULT_ACCESS_LOG = Path("/var/log/nginx/access.log")
DEFAULT_KNOWN_CLIENTS = Path("/opt/ttlink-known-clients.json")
PROXY_PATH_RULES = (
    ("/vless-", "vless"),
)
EXCLUDED_CLIENT_IPS = {"127.0.0.1", "::1", "47.253.212.27"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def run_command(args: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(args, check=False, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as exc:  # noqa: BLE001 - collector should report and continue
        return 1, "", str(exc)


def parse_nginx_time(raw: str) -> datetime | None:
    try:
        return datetime.strptime(raw, "%d/%b/%Y:%H:%M:%S %z").astimezone()
    except ValueError:
        return None


def service_status(name: str) -> dict[str, str]:
    if not shutil.which("systemctl"):
        return {"name": name, "status": "unknown"}

    code, stdout, _stderr = run_command(["systemctl", "is-active", name])
    status = stdout if code == 0 and stdout else "unknown"
    if status not in {"active", "inactive", "failed"}:
        status = "unknown"
    return {"name": name, "status": status}


def collect_ports() -> list[dict[str, Any]]:
    expected = [
        {"name": "nginx-https", "protocol": "tcp", "port": 443},
        {"name": "hysteria-quic", "protocol": "udp", "port": 443},
        {"name": "xray-vless", "protocol": "tcp", "host": "127.0.0.1", "port": 10000},
    ]

    if not shutil.which("ss"):
        return [{**item, "status": "unknown"} for item in expected]

    code, stdout, _stderr = run_command(["ss", "-lntup"])
    if code != 0:
        return [{**item, "status": "unknown"} for item in expected]

    rows = stdout.lower().splitlines()
    collected = []
    for item in expected:
        port_marker = f":{item['port']}"
        protocol = item["protocol"].lower()
        listening = any(protocol in row and port_marker in row for row in rows)
        collected.append({**item, "status": "listening" if listening else "missing"})
    return collected


def load_known_clients(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}

    known: dict[str, str] = {}
    for label, ips in data.items():
        if not isinstance(label, str) or not isinstance(ips, list):
            continue
        for ip in ips:
            if isinstance(ip, str):
                known[ip] = label
    return known


def collect_subscription_clients(access_log: Path, known_clients: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    traffic = {
        "todayBytes": 0,
        "monthBytes": None,
        "uniqueIpsToday": None,
        "uniqueIpsMonth": None,
        "sevenDay": [],
    }
    if not access_log.exists():
        traffic["todayBytes"] = None
        return [], traffic

    today = datetime.now(timezone.utc).astimezone().date()
    seen: dict[str, dict[str, Any]] = {}
    line_pattern = re.compile(
        r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) [^"]+" '
        r'(?P<status>\d{3}) (?P<body_bytes>\d+)'
    )

    with access_log.open(encoding="utf-8", errors="ignore") as file:
        for line in file:
            if not any(marker in line for marker, _node in PROXY_PATH_RULES):
                continue

            match = line_pattern.match(line)
            if not match:
                continue

            seen_at = parse_nginx_time(match.group("time"))
            if seen_at is None or seen_at.date() != today:
                continue

            path = match.group("path")
            node = next((node for marker, node in PROXY_PATH_RULES if path.startswith(marker)), None)
            if node is None:
                continue

            ip = match.group("ip")
            if ip in EXCLUDED_CLIENT_IPS:
                continue

            body_bytes = int(match.group("body_bytes"))
            traffic["todayBytes"] += body_bytes

            previous = seen.get(ip)
            if previous is None:
                seen[ip] = {"lastSeen": seen_at, "node": node, "todayBytes": body_bytes}
            else:
                previous["todayBytes"] += body_bytes
                if seen_at > previous["lastSeen"]:
                    previous["lastSeen"] = seen_at
                    previous["node"] = node

    clients = [
        {
            "id": f"ip-{ip}",
            "label": known_clients.get(ip, ip),
            "ip": ip,
            "known": ip in known_clients,
            "lastSeen": item["lastSeen"].isoformat(timespec="seconds"),
            "node": item["node"],
            "traffic": {
                "todayBytes": item["todayBytes"],
                "monthBytes": None,
            },
        }
        for ip, item in sorted(seen.items(), key=lambda entry: entry[1]["lastSeen"], reverse=True)
    ]
    traffic["uniqueIpsToday"] = len(seen)
    return clients, traffic


def discover_subscription_yaml(subs_dir: Path = DEFAULT_SUBS_DIR) -> Path | None:
    candidates = [path for path in subs_dir.glob("subs-*.yaml") if path.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def subscription_url_for(yaml_path: Path | None, fallback_url: str | None) -> str:
    if fallback_url:
        return fallback_url
    if yaml_path is not None:
        return f"{DEFAULT_SUBS_BASE_URL}/{yaml_path.name}"
    return f"{DEFAULT_SUBS_BASE_URL}/unknown.yaml"


def read_subscription(yaml_path: Path | None, subscription_url: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    info: dict[str, Any] = {
        "name": "TTLINK Personal Ops",
        "url": subscription_url,
        "status": "unknown",
        "nodeCount": 0,
        "lastModified": None,
        "containsHy2": False,
        "containsVless": False,
    }

    if yaml_path is None:
        errors.append({
            "source": "subscription-yaml",
            "message": "No YAML path provided; subscription markers are unknown",
            "severity": "warning",
        })
        return info, errors

    if not yaml_path.exists():
        errors.append({
            "source": "subscription-yaml",
            "message": f"YAML file not found: {yaml_path}",
            "severity": "warning",
        })
        return info, errors

    content = yaml_path.read_text(encoding="utf-8", errors="ignore")
    contains_hy2 = "hy2-ttlink" in content and "hy.ttlink.asia" in content
    contains_vless = "vless-ttlink" in content and "vless.ttlink.asia" in content
    node_count = int(contains_hy2) + int(contains_vless)
    mtime = datetime.fromtimestamp(yaml_path.stat().st_mtime, timezone.utc).astimezone().isoformat(timespec="seconds")

    info.update({
        "status": "active" if node_count > 0 else "unknown",
        "nodeCount": node_count,
        "lastModified": mtime,
        "containsHy2": contains_hy2,
        "containsVless": contains_vless,
    })
    return info, errors


def node_statuses() -> list[dict[str, Any]]:
    return [
        {
            "name": "hy2-ttlink",
            "type": "hysteria2",
            "domain": "hy.ttlink.asia",
            "status": "unknown",
            "source": "hysteria-traffic-api",
            "traffic": None,
            "online": {"clientCount": None},
        },
        {
            "name": "vless-ttlink",
            "type": "vless",
            "domain": "vless.ttlink.asia",
            "status": "unknown",
            "source": "xray-stats-api",
            "traffic": None,
            "online": {"clientCount": None},
        },
    ]


def build_status(yaml_path: Path | None, subscription_url: str, access_log: Path, known_clients_path: Path) -> dict[str, Any]:
    subscription, errors = read_subscription(yaml_path, subscription_url)
    known_clients = load_known_clients(known_clients_path)
    clients, traffic = collect_subscription_clients(access_log, known_clients)
    return {
        "version": 1,
        "generatedAt": now_iso(),
        "subscription": subscription,
        "services": [service_status(name) for name in ["nginx", "xray", "hysteria"]],
        "ports": collect_ports(),
        "nodes": node_statuses(),
        "clients": clients,
        "traffic": traffic,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TTLINK subscription status JSON")
    parser.add_argument(
        "--yaml",
        type=Path,
        default=None,
        help="Path to active Clash/Mihomo subscription YAML. If omitted, newest /etc/letsencrypt/subs/subs-*.yaml is used.",
    )
    parser.add_argument(
        "--subscription-url",
        default=None,
        help="Public subscription URL to expose in the generated JSON. If omitted, it is derived from the resolved YAML filename.",
    )
    parser.add_argument("--out", type=Path, default=Path("public/subscription-status.generated.json"), help="Output JSON path")
    parser.add_argument(
        "--access-log",
        type=Path,
        default=DEFAULT_ACCESS_LOG,
        help="Nginx access log path used for lightweight subscription IP activity",
    )
    parser.add_argument(
        "--known-clients",
        type=Path,
        default=DEFAULT_KNOWN_CLIENTS,
        help="JSON file mapping display labels to known IP lists",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    yaml_path = args.yaml or discover_subscription_yaml()
    subscription_url = subscription_url_for(yaml_path, args.subscription_url)
    status = build_status(yaml_path, subscription_url, args.access_log, args.known_clients)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {args.out}")
    print(f"yaml: {yaml_path if yaml_path is not None else 'not found'}")
    print(f"services: {len(status['services'])}")
    print(f"ports: {len(status['ports'])}")
    print(f"errors: {len(status['errors'])}")


if __name__ == "__main__":
    main()
