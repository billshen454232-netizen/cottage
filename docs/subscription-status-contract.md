# Subscription Status JSON Contract

This document defines the first lightweight data contract for the TTLINK subscription center.

## Goal

Expose one static JSON document that the `/subscribe` frontend can read before a full backend API exists.

```text
collector script → subscription-status.json → static frontend fetch
```

This first version is intentionally small: no database, no FastAPI, no login, no long-term history.

## File location

Local development sample:

```text
public/subscription-status.sample.json
```

Future production location on the subscription server:

```text
https://subs.ttlink.asia/subs/subscription-status.json
```

## Top-level shape

```json
{
  "version": 1,
  "generatedAt": "2026-06-11T17:30:00+08:00",
  "subscription": {},
  "services": [],
  "ports": [],
  "nodes": [],
  "clients": [],
  "traffic": {},
  "errors": []
}
```

## Fields

### `subscription`

Describes the active subscription YAML.
Node marker fields are descriptive, not mandatory health checks.

- `containsHy2: false` does not automatically mean the subscription is broken.
- `containsVless: false` does not automatically mean the subscription is broken.
- `nodeCount` should reflect how many known nodes the collector recognizes.
- A single-node subscription is allowed; the frontend should display the current shape instead of treating missing optional nodes as an error.

```json
{
  "name": "TTLINK Personal Ops",
  "url": "https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml",
  "status": "active",
  "nodeCount": 2,
  "lastModified": "2026-06-11T16:30:00+08:00",
  "containsHy2": true,
  "containsVless": true
}
```

### `services`

Represents service manager status.

```json
[
  { "name": "nginx", "status": "active" },
  { "name": "xray", "status": "active" },
  { "name": "hysteria", "status": "active" }
]
```

Allowed status values:

```text
active | inactive | failed | unknown
```

### `ports`

Represents the minimal expected listening ports.

```json
[
  { "name": "nginx-https", "protocol": "tcp", "port": 443, "status": "listening" },
  { "name": "hysteria-quic", "protocol": "udp", "port": 443, "status": "listening" },
  { "name": "xray-vless", "protocol": "tcp", "port": 10000, "host": "127.0.0.1", "status": "listening" }
]
```

Allowed status values:

```text
listening | missing | unknown
```

### `nodes`

Represents subscription nodes. Traffic fields are bytes, not formatted strings.

```json
[
  {
    "name": "hy2-ttlink",
    "type": "hysteria2",
    "domain": "hy.ttlink.asia",
    "status": "online",
    "source": "hysteria-traffic-api",
    "traffic": {
      "uplinkBytes": 0,
      "downlinkBytes": 0,
      "usedBytes": 0
    },
    "online": {
      "clientCount": 0
    }
  }
]
```

For the first collector version, traffic may be `null` if the service stats API is not enabled yet.

### `clients`

Represents lightweight IP activity for subscription-related HTTP paths. In the current production collector, this is derived from nginx access logs, not from HY2/Xray traffic APIs.

Tracked paths:

```text
/subs.html
/subs/subscription-status.json
/subs/subs-*.yaml
```

```json
[
  {
    "id": "ip-192.0.2.10",
    "label": "192.0.2.10",
    "ip": "192.0.2.10",
    "lastSeen": "2026-06-15T18:26:11+08:00",
    "node": "subscription",
    "traffic": {
      "todayBytes": null,
      "monthBytes": null
    }
  }
]
```

Notes:

- `clients[]` is for recent subscription-center access visibility, not precise proxy-user accounting.
- `traffic.todayBytes` and `traffic.monthBytes` stay `null` until real traffic APIs are integrated.
- Because `subs.ttlink.asia` is behind Cloudflare orange cloud, collected IPs may be Cloudflare edge IPs unless nginx real IP handling is configured with `CF-Connecting-IP` and trusted Cloudflare IP ranges.

### `traffic`

Aggregated display data for the frontend.

```json
{
  "todayBytes": 0,
  "monthBytes": 0,
  "uniqueIpsToday": 0,
  "uniqueIpsMonth": 0,
  "sevenDay": [
    { "day": "Mon", "bytes": 0 }
  ]
}
```

### `errors`

Collector errors should not crash the frontend. Store recoverable issues here.

```json
[
  {
    "source": "xray-stats-api",
    "message": "Xray stats API is not enabled",
    "severity": "warning"
  }
]
```

Allowed severity values:

```text
info | warning | error
```

## First implementation rule

The first collector should prefer safe, verifiable fields:

- service status
- port listening status
- YAML file existence and node markers
- generated timestamp
- lightweight IP activity from nginx access logs

Traffic APIs can be added later without changing the top-level contract.

## Production collector behavior

The production collector should not hard-code the subscription YAML filename in cron.

When `--yaml` is omitted, it discovers the newest file matching:

```text
/etc/letsencrypt/subs/subs-*.yaml
```

The generated `subscription.url` is derived from that YAML filename. This keeps the cron entry stable when the subscription URL is rotated.

The current cron entry should call the collector through a stable command shape:

```text
/usr/bin/python3 /opt/ttlink-subscription-collector.py --out /etc/letsencrypt/subs/subscription-status.json
```

The nginx exposure remains whitelist-based:

- the active subscription YAML has an exact `location = /subs/<file>.yaml` rule;
- `subscription-status.json` has an exact `location = /subs/subscription-status.json` rule;
- the broader `/subs/` prefix still returns `410` to avoid exposing arbitrary files.

