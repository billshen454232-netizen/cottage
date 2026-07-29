# Subscription Ops Data Learning Plan

> **Process rule for this project:** This is a learning-oriented 测开 / 运维 / 自动化 practice task. Execute step by step. Claude should explain each step, give the user commands, wait for output when useful, and explain results before moving on. Do not silently implement the whole plan.

**Goal:** Turn the subscription center from a static UI prototype into a real operations panel through a gradual data pipeline, while using the work to practice test-development, Linux ops, automation, deployment, and verification.

**Architecture:** Keep the data source on Aliyun because the real service state lives there. Generate a static `subscription-status.json` on Aliyun, expose only that JSON through an exact nginx whitelist location on `subs.ttlink.asia`, and let the Cloudflare Pages `/subscribe` frontend read it cross-origin. Cloudflare / R2 / Worker migration is a later learning phase after the Aliyun data loop is stable.

**Tech Stack:** Astro frontend prototype, Python collector script, JSON contract, Aliyun Linux, nginx static files, systemctl, ss, Hysteria2 Traffic Stats API later, Xray Stats API later, optional Cloudflare Pages/R2/Workers in later phases.

---

## Project boundary

Current service roles:

```text
home.ttlink.asia
  Cloudflare Pages
  Personal Ops Hub main site
  Only links to the subscription center; it does not fetch subscription data.

subs.ttlink.asia
  Cloudflare orange cloud → Aliyun nginx
  Subscription center page and subscription YAML distribution.
  Future source of subscription-status.json.

hy.ttlink.asia
  Cloudflare DNS-only / grey cloud
  Hysteria2 UDP/QUIC main node.

vless.ttlink.asia
  Cloudflare orange cloud → Aliyun nginx → Xray 127.0.0.1:10000
  VLESS WebSocket TLS fallback node.

cli.ttlink.asia
  Cloudflare orange cloud → Aliyun nginx → CLIProxyAPI
```

Important: `home.ttlink.asia` is still only the Personal Ops Hub entry point. The subscription panel page is deployed with the same Cloudflare Pages frontend, but its production data source belongs to `subs.ttlink.asia` and is generated on Aliyun. The main site does not own or generate subscription data.

---

## Scope correction — do not drift into low-value metrics

The panel's usage view is about **proxy service usage**, not subscription-page visits.

Do not treat these as meaningful usage metrics:

```text
/subs.html
/subs/subscription-status.json
```

Those paths mostly show the owner's browser or the frontend refreshing JSON. They should not drive the IP activity panel.

Useful usage sources, from lightest to most accurate:

1. **VLESS WebSocket access log** — temporary source for recent proxy-user exit IPs. It can answer: "which public IPs are currently using the VLESS service?"
2. **Xray Stats API** — accurate VLESS traffic counters by user/email/inbound.
3. **Hysteria2 Traffic Stats API** — accurate HY2 traffic and online data.

Keep the implementation aligned with this rule:

```text
Automation should reduce repeated manual checking of real proxy usage.
If a metric only shows page visits or creates maintenance noise, do not put it in the panel.
```

---

## Phase 1 — Aliyun static JSON data loop

**Purpose:** Build the smallest real data loop before adding API servers or databases.

Data flow:

```text
Aliyun collector script
  → auto-discovers newest /etc/letsencrypt/subs/subs-*.yaml
  → reads local service/YAML/port state
  → writes /etc/letsencrypt/subs/subscription-status.json
  → nginx serves exact whitelisted https://subs.ttlink.asia/subs/subscription-status.json
  → Cloudflare Pages /subscribe fetches the production JSON
```

Learning focus:

- JSON data contract
- Python collector script
- Linux service inspection
- nginx static file serving
- local vs server environment differences
- verification commands
- safe incremental deployment

### Phase 1 checkpoints

- [x] Define first `subscription-status.json` contract in `docs/subscription-status-contract.md`.
- [x] Create sample JSON in `public/subscription-status.sample.json`.
- [x] Create first collector skeleton in `scripts/collect-subscription-status.py`.
- [x] Understand local collector output and why some values are `unknown` on Windows.
- [x] Run collector against a local sample YAML so `containsHy2` / `containsVless` become real.
- [x] Decide deployment path on Aliyun for the collector script: `/opt/ttlink-subscription-collector.py`.
- [x] Run collector manually on Aliyun with the real YAML path.
- [x] Verify generated JSON with `python3 -m json.tool` on Aliyun.
- [x] Verify nginx can serve `/subs/subscription-status.json` through an exact whitelist location.
- [x] Update `/subscribe` UI to read local sample JSON in development and production JSON from `subs.ttlink.asia` when deployed.
- [ ] Add one manual verification checklist to the runbook.

---

## Phase 2 — Scheduled generation and frontend consumption

**Purpose:** Make the JSON update automatically and make the UI consume it reliably.

Data flow:

```text
cron
  → runs collector every 5 minutes
  → collector discovers current subs-*.yaml
  → updates subscription-status.json
  → subscription center displays generatedAt and current service state
```

Learning focus:

- cron vs systemd timer tradeoff
- atomic file writes
- stale data detection
- frontend fallback behavior
- deployment verification

### Phase 2 checkpoints

- [ ] Add atomic write behavior to the collector.
- [ ] Add `--pretty` or stable output option if needed.
- [x] Add cron entry on Aliyun.
- [x] Keep cron stable by omitting `--yaml`; collector auto-discovers the newest `/etc/letsencrypt/subs/subs-*.yaml`.
- [x] Verify repeated generation updates JSON and does not break frontend consumption.
- [x] Make the UI show `generatedAt`.
- [x] Keep sample/mock fallback for local development.
- [ ] Add stale-data warning in the UI.

---

## Phase 2.5 — Lightweight proxy usage visibility

**Purpose:** Show recent public exit IPs that are actually using proxy services on this VPS, without pretending nginx logs are full traffic accounting.

Temporary data source:

```text
nginx access.log
  → only VLESS WebSocket paths (`/vless-*`)
  → status 101 WebSocket connections
  → recent public exit IPs
```

Do not include:

```text
/subs.html
/subs/subscription-status.json
/subs/subs-*.yaml
```

Those are subscription-page or subscription-file visits, not proxy service usage.

Learning focus:

- distinguish panel-useful metrics from low-value page analytics
- understand Cloudflare real IP handling with `CF-Connecting-IP`
- understand limits of nginx access logs for proxy traffic
- keep this as a temporary bridge before official stats APIs

### Phase 2.5 checkpoints

- [x] Configure nginx real IP handling for Cloudflare so new logs can show client public exit IPs instead of Cloudflare edge IPs.
- [ ] Ensure `clients[]` is based on VLESS WebSocket usage, not subscription-page refreshes.
- [ ] Keep the display label clear: these are public exit IPs observed by the VPS, not guaranteed physical device IPs.
- [ ] Limit or age out old log records so stale Cloudflare edge IPs from before real-IP setup do not dominate the panel.
- [ ] Do not build complex traffic accounting on nginx logs; move to official stats APIs for accurate counters.

---

## Phase 3 — Official proxy stats APIs

**Purpose:** Replace placeholder traffic values and nginx-log estimates with real proxy service stats.

Preferred data sources:

```text
HY2:
  Hysteria2 Traffic Stats API
  GET /traffic
  GET /online

VLESS:
  Xray stats API / xray api
  user>>>email>>>traffic>>>uplink
  user>>>email>>>traffic>>>downlink
```

Learning focus:

- enabling service metrics safely
- auth/secret handling
- parsing bytes and counters
- per-node vs per-client traffic
- failure-tolerant collectors

### Phase 3 checkpoints

- [ ] Check whether Hysteria2 `trafficStats` is enabled.
- [ ] If not enabled, plan a safe config change and rollback.
- [ ] Check whether Xray stats and user email fields are configured.
- [ ] Add HY2 stats collection.
- [ ] Add Xray stats collection.
- [ ] Keep `errors[]` populated when stats APIs are unavailable.

---

## Phase 4 — Cloudflare learning track

**Purpose:** Learn cloud-native patterns only after the Aliyun loop is stable.

Possible future architecture:

```text
Aliyun collector
  → uploads subscription-status.json / YAML to R2
  → Cloudflare Pages or Worker serves subscription center and data
```

Learning focus:

- Cloudflare Pages deployment
- R2 object storage
- Worker as lightweight API/access layer
- token and secret management
- caching and invalidation
- versioned JSON/YAML publish

### Phase 4 checkpoints

- [ ] Decide whether `subs.ttlink.asia` should remain on Aliyun or move frontend to Cloudflare.
- [ ] If moving, preserve existing subscription URL compatibility.
- [ ] Prototype R2 upload with a non-sensitive test JSON.
- [ ] Add Worker read path only after access rules are clear.

---

## Current next step

The static JSON loop is working end to end:

```text
cron → collector → subscription-status.json → nginx exact whitelist → Cloudflare Pages /subscribe
```

The project is now in **Phase 2.5: lightweight proxy usage visibility**.

Current task:

```text
Make clients[] show recent VLESS WebSocket user exit IPs from this VPS, not subscription-page visitors.
```

Immediate constraints:

- Do not count `/subs.html` or `/subs/subscription-status.json` as usage.
- Do not spend more time building a custom Cloudflare-IP filtering system unless it directly cleans current VLESS usage output.
- Prefer short time windows, such as recent VLESS connections, over parsing all of today's mixed historical logs.
- Keep HY2 traffic out of nginx-log assumptions; HY2 requires Hysteria2 Traffic Stats API.
- After VLESS recent IPs are reasonable, stop and move to Phase 3 discovery: check whether Xray Stats API and Hysteria2 Traffic Stats API are already enabled.

Do not add FastAPI, a database, Cloudflare R2/Worker, GeoIP, ASN lookup, or complex traffic charts until official proxy stats APIs are understood.
