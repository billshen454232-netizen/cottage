#!/usr/bin/env bash
set -euo pipefail

TMP_DIR="tmp/collector-check"
YAML_FILE="$TMP_DIR/subscription.yaml"
OUT_FILE="$TMP_DIR/subscription-status.json"

mkdir -p "$TMP_DIR"

cat > "$YAML_FILE" <<'YAML'
proxies:
  - name: hy2-ttlink
    type: hysteria2
    server: hy.ttlink.asia
    port: 443
    sni: hy.ttlink.asia

  - name: vless-ttlink
    type: vless
    server: vless.ttlink.asia
    port: 443
    network: ws
    tls: true
YAML

python scripts/collect-subscription-status.py \
  --yaml "$YAML_FILE" \
  --out "$OUT_FILE"

python - "$OUT_FILE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
subscription = data["subscription"]

assert subscription["status"] == "active", subscription
assert subscription["nodeCount"] == 2, subscription
assert subscription["containsHy2"] is True, subscription
assert subscription["containsVless"] is True, subscription
assert data["errors"] == [], data["errors"]

print("collector local check passed")
PY
