# Subscription Center UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign `/subscribe` into a monochrome starlight Subscription Workspace and add a Subscription Center entry point to `/about`.

**Architecture:** Keep the implementation native to the existing Astro app. Expand the static subscription data model in `src/data/subscription.ts`, update `/subscribe` as a self-contained workspace, and add a small console command/module link on `/about` without replacing the existing terminal console.

**Tech Stack:** Astro 6, TypeScript data modules, scoped Astro CSS, small inline browser scripts for copy and anchor behavior, Playwright e2e smoke tests, `npm run build` verification.

---

## File Structure

- Modify: `src/data/subscription.ts`
  - Owns all mock data for the subscription workspace.
  - Adds IP detail fields used by the redesigned IP activity window.
  - Adds a `subscriptionWorkspaceNav` array for the five anchor entries.

- Modify: `src/data/console.ts`
  - Adds a `subscriptionModule` object for `/about`.
  - Adds `subscribe` to `toolItems` or keeps existing tool items while the page imports `subscriptionModule` directly.

- Modify: `src/pages/about.astro`
  - Adds a `subscribe` console command.
  - Adds a visible Subscription Center module near the terminal output startup text.
  - Keeps all existing console behavior working.

- Replace: `src/pages/subscribe.astro`
  - Implements the approved monochrome starlight ops visual direction.
  - Hides full subscription URL by default.
  - Keeps copy/open YAML actions.
  - Makes anchor navigation scroll to page sections.
  - Makes IP activity the primary content window.

- Create: `tests/subscribe.spec.ts`
  - Verifies key UI, hidden URL behavior, copy action, anchor navigation, and `/about` entry point.

---

## Task 1: Expand subscription mock data

**Files:**
- Modify: `src/data/subscription.ts`

- [ ] **Step 1: Replace `src/data/subscription.ts` with the expanded data model**

Use this complete file content:

```ts
export const subscriptionOverview = {
  title: 'TTLINK Subscription Workspace',
  subtitle: 'STDIN | Subscribe >> /ops/workspace',
  planName: 'Personal Ops · Self-hosted',
  status: 'online',
  statusLabel: 'ONLINE',
  subscriptionUrl: 'https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml',
  urlVisibilityLabel: 'URL hidden',
  lastUpdated: '2026-06-11 16:30',
  usedTrafficGb: 128.6,
  todayTrafficGb: 4.2,
  activeNodes: 2,
  totalNodes: 2,
  uniqueIpsToday: 3,
  uniqueIpsMonth: 9,
};

export const subscriptionWorkspaceNav = [
  { id: 'subscription', icon: '⌁', label: '订阅' },
  { id: 'ip-activity', icon: '◌', label: 'IP 活动' },
  { id: 'nodes', icon: '◇', label: '节点' },
  { id: 'traffic', icon: '▦', label: '流量' },
  { id: 'docs', icon: '☼', label: '文档' },
];

export const ipStats = [
  {
    ip: '192.168.1.24',
    label: 'Home PC',
    location: 'Local LAN',
    isp: 'Home network',
    asn: 'private',
    lastSeen: '2 min',
    firstSeenToday: '09:14',
    sessionCount: 6,
    today: '2.8 GB',
    month: '74.2 GB',
    node: 'HY2',
    source: 'home',
    trustLevel: 'known',
    note: 'Primary desktop client',
  },
  {
    ip: '172.16.8.12',
    label: 'Laptop',
    location: 'Remote work',
    isp: 'China Mobile',
    asn: 'AS9808',
    lastSeen: '18 min',
    firstSeenToday: '10:32',
    sessionCount: 3,
    today: '1.1 GB',
    month: '31.6 GB',
    node: 'VLESS',
    source: 'remote',
    trustLevel: 'known',
    note: 'Fallback route during remote work',
  },
  {
    ip: '10.0.0.8',
    label: 'Mobile',
    location: 'Cellular',
    isp: 'China Unicom',
    asn: 'AS4837',
    lastSeen: '1 h',
    firstSeenToday: '12:48',
    sessionCount: 2,
    today: '0.3 GB',
    month: '22.8 GB',
    node: 'HY2',
    source: 'mobile',
    trustLevel: 'known',
    note: 'Phone client',
  },
];

export const trafficBars = [
  { day: 'Mon', value: 18 },
  { day: 'Tue', value: 32 },
  { day: 'Wed', value: 24 },
  { day: 'Thu', value: 46 },
  { day: 'Fri', value: 38 },
  { day: 'Sat', value: 62 },
  { day: 'Sun', value: 54 },
];

export const proxyNodes = [
  {
    name: 'hy2-ttlink',
    role: 'MAIN',
    roleLabel: '主力',
    domain: 'hy.ttlink.asia',
    protocol: 'Hysteria2 / UDP / QUIC',
    route: 'DNS only / grey cloud',
    status: 'ONLINE',
    latency: '86 ms',
    usage: '92.4 GB',
    description: '主力高速节点。UDP/QUIC 直连源站，不走 Cloudflare。',
  },
  {
    name: 'vless-ttlink',
    role: 'FALLBACK',
    roleLabel: '保底',
    domain: 'vless.ttlink.asia',
    protocol: 'VLESS / WebSocket / TLS',
    route: 'Cloudflare proxied / orange cloud',
    status: 'ONLINE',
    latency: '142 ms',
    usage: '36.2 GB',
    description: '保底节点。HY2 不稳定或 UDP 受限时切换，走 HTTPS/WebSocket。',
  },
];

export const opsDocs = [
  {
    id: 'import',
    title: '订阅导入',
    summary: 'Clash Verge / Mihomo 订阅导入流程。',
    steps: [
      '复制 Clash 订阅链接。',
      'Clash Verge → Profiles → New → Remote。',
      '粘贴 URL 后保存并刷新。',
      '确认 PROXY 组包含 hy2-ttlink 与 vless-ttlink。',
    ],
  },
  {
    id: 'switch',
    title: '节点切换',
    summary: 'HY2 与 VLESS 的使用边界。',
    steps: [
      '默认使用 hy2-ttlink，速度优先。',
      '如果 UDP 不稳定、HY2 断连或节点测速异常，切换 vless-ttlink。',
      'vless-ttlink 走 Cloudflare 橙云，适合作为保底链路。',
      '外发订阅如需隐藏源站，只提供 VLESS 节点。',
    ],
  },
  {
    id: 'ops',
    title: '运维检查',
    summary: '双节点架构的最小检查清单。',
    steps: [
      'nginx / xray / hysteria 三个服务应为 active。',
      'hy.ttlink.asia 应解析到源站 IP。',
      'subs.ttlink.asia 与 vless.ttlink.asia 应解析到 Cloudflare IP。',
      '订阅 YAML 中 HY2 server/sni 应为 hy.ttlink.asia。',
    ],
  },
  {
    id: 'topology',
    title: '架构说明',
    summary: '订阅站、主力节点与保底节点的职责拆分。',
    steps: [
      'subs.ttlink.asia：订阅中心与 YAML 分发。',
      'hy.ttlink.asia：HY2 主力节点，灰云直连 UDP 443。',
      'vless.ttlink.asia：VLESS WS TLS 保底节点，橙云 HTTPS。',
      'cli.ttlink.asia：CLIProxyAPI 管理入口。',
    ],
  },
];
```

- [ ] **Step 2: Run a build to verify data imports still compile**

Run:

```bash
npm run build
```

Expected: build succeeds. If it fails because `totalTrafficGb` is missing from the old `/subscribe` page, continue to Task 2, which replaces that page.

- [ ] **Step 3: Commit the data model change**

```bash
git add src/data/subscription.ts
git commit -m "feat: expand subscription workspace data"
```

---

## Task 2: Add the `/subscribe` smoke test before implementation

**Files:**
- Create: `tests/subscribe.spec.ts`

- [ ] **Step 1: Create the failing Playwright test**

Create `tests/subscribe.spec.ts` with:

```ts
import { expect, test } from '@playwright/test';

test('subscription workspace shows hidden subscription actions and IP activity', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/subscribe');

  await expect(page.getByRole('heading', { name: 'TTLINK' })).toBeVisible();
  await expect(page.getByText('STDIN | Subscribe >> /ops/workspace')).toBeVisible();

  await expect(page.getByRole('link', { name: /订阅/ })).toHaveAttribute('href', '#subscription');
  await expect(page.getByRole('link', { name: /IP 活动/ })).toHaveAttribute('href', '#ip-activity');
  await expect(page.getByRole('link', { name: /节点/ })).toHaveAttribute('href', '#nodes');
  await expect(page.getByRole('link', { name: /流量/ })).toHaveAttribute('href', '#traffic');
  await expect(page.getByRole('link', { name: /文档/ })).toHaveAttribute('href', '#docs');

  await expect(page.getByText('URL hidden')).toBeVisible();
  await expect(page.getByText('https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml')).toHaveCount(0);

  await expect(page.getByRole('heading', { name: 'IP 使用窗口' })).toBeVisible();
  await expect(page.getByText('192.168.1.24')).toBeVisible();
  await expect(page.getByText('China Mobile')).toBeVisible();
  await expect(page.getByText('AS9808')).toBeVisible();

  await page.getByRole('button', { name: '复制订阅' }).click();
  await expect(page.getByRole('button', { name: '已复制' })).toBeVisible();

  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toBe('https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml');

  await expect(page.getByRole('link', { name: '打开 YAML' })).toHaveAttribute(
    'href',
    'https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml',
  );
});
```

- [ ] **Step 2: Run the test and verify it fails against the current page**

Run:

```bash
npm run test:e2e -- tests/subscribe.spec.ts
```

Expected: FAIL because the current page does not have the new `TTLINK` heading, hidden URL behavior, or IP activity fields.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/subscribe.spec.ts
git commit -m "test: add subscription workspace smoke test"
```

---

## Task 3: Replace `/subscribe` with the monochrome starlight workspace

**Files:**
- Replace: `src/pages/subscribe.astro`
- Test: `tests/subscribe.spec.ts`

- [ ] **Step 1: Replace the frontmatter and markup in `src/pages/subscribe.astro`**

Use this complete page structure. Keep the `<style>` and `<script>` additions for the next steps in this task.

```astro
---
import Layout from '../layouts/Layout.astro';
import {
  ipStats,
  opsDocs,
  proxyNodes,
  subscriptionOverview,
  subscriptionWorkspaceNav,
  trafficBars,
} from '../data/subscription';
---

<Layout>
  <main class="subscription-page">
    <div class="star star-a" aria-hidden="true"></div>
    <div class="star star-b" aria-hidden="true"></div>
    <div class="star star-c" aria-hidden="true"></div>

    <section class="identity" aria-labelledby="workspace-title">
      <h1 id="workspace-title">TTLINK</h1>
      <p>{subscriptionOverview.subtitle}</p>
    </section>

    <nav class="portal-nav" aria-label="Subscription workspace sections">
      {subscriptionWorkspaceNav.map((item, index) => (
        <a class:list={[index === 0 && 'active']} href={`#${item.id}`}>
          <span aria-hidden="true">{item.icon}</span>
          <b>{item.label}</b>
        </a>
      ))}
    </nav>

    <section class="action-panel" id="subscription" aria-label="Active subscription">
      <div>
        <div class="action-line">
          <strong>Active subscription</strong>
          <span class="status-pill">{subscriptionOverview.statusLabel}</span>
          <small>{subscriptionOverview.urlVisibilityLabel} · updated {subscriptionOverview.lastUpdated}</small>
        </div>
        <p>复制当前 Clash/Mihomo 订阅，或打开 active YAML。</p>
      </div>
      <div class="action-buttons">
        <button id="copyButton" type="button" data-copy-url={subscriptionOverview.subscriptionUrl}>复制订阅</button>
        <a href={subscriptionOverview.subscriptionUrl} target="_blank" rel="noreferrer">打开 YAML</a>
      </div>
    </section>

    <section class="workspace-grid" aria-label="Subscription operations workspace">
      <article class="data-window ip-window" id="ip-activity" aria-labelledby="ip-heading">
        <header class="window-head">
          <div>
            <h2 id="ip-heading">IP 使用窗口</h2>
            <p>最后活动、所在地、ISP、ASN、节点和用量。</p>
          </div>
          <span>{subscriptionOverview.uniqueIpsToday} today / {subscriptionOverview.uniqueIpsMonth} month</span>
        </header>

        <div class="ip-table" role="table" aria-label="IP usage activity">
          <div class="ip-row ip-head" role="row">
            <span>IP / Device</span>
            <span>Location / ISP</span>
            <span>Last seen</span>
            <span>Today</span>
            <span>Node</span>
          </div>
          <div class="ip-scroll">
            {ipStats.map((item, index) => (
              <div class:list={['ip-row', index === 0 && 'current']} role="row">
                <span><b>{item.ip}</b><small>{item.label}</small></span>
                <span><b>{item.location}</b><small>{item.isp} · {item.asn}</small></span>
                <span><b>{item.lastSeen}</b><small>first {item.firstSeenToday} · {item.sessionCount} sessions</small></span>
                <span><b>{item.today}</b><small>{item.month} month</small></span>
                <span><b>{item.node}</b><small>{item.note}</small></span>
              </div>
            ))}
          </div>
        </div>
      </article>

      <aside class="side-stack" aria-label="Node and traffic summary">
        <article class="data-window compact-window" id="nodes" aria-labelledby="nodes-heading">
          <h2 id="nodes-heading">节点</h2>
          <div class="node-list">
            {proxyNodes.map((node) => (
              <div>
                <div><strong>{node.name}</strong><span>{node.latency}</span></div>
                <p>{node.roleLabel} {node.protocol}</p>
                <small>{node.route}</small>
              </div>
            ))}
          </div>
        </article>

        <article class="data-window compact-window" id="traffic" aria-labelledby="traffic-heading">
          <h2 id="traffic-heading">流量</h2>
          <div class="traffic-summary">
            <span>今日 <b>{subscriptionOverview.todayTrafficGb} GB</b></span>
            <span>本月 <b>{subscriptionOverview.usedTrafficGb} GB</b></span>
          </div>
          <div class="bar-chart" aria-label="7 day traffic trend">
            {trafficBars.map((bar) => <i style={`height:${bar.value}%`} title={bar.day}></i>)}
          </div>
        </article>
      </aside>
    </section>

    <section class="data-window docs-window" id="docs" aria-labelledby="docs-heading">
      <header class="window-head">
        <div>
          <h2 id="docs-heading">文档</h2>
          <p>导入、切换、检查和架构说明。</p>
        </div>
      </header>
      <div class="docs-grid">
        {opsDocs.map((doc) => (
          <details>
            <summary>{doc.title}</summary>
            <p>{doc.summary}</p>
            <ol>{doc.steps.map((step) => <li>{step}</li>)}</ol>
          </details>
        ))}
      </div>
    </section>
  </main>
</Layout>
```

- [ ] **Step 2: Add the copy script before `</Layout>`**

Add this script after the `</main>` and before `</Layout>`:

```astro
  <script>
    const copyButton = document.getElementById('copyButton');

    copyButton?.addEventListener('click', async () => {
      const url = copyButton.getAttribute('data-copy-url') ?? '';
      try {
        await navigator.clipboard.writeText(url);
        copyButton.textContent = '已复制';
      } catch {
        copyButton.textContent = '复制失败';
      }

      setTimeout(() => {
        copyButton.textContent = '复制订阅';
      }, 1400);
    });
  </script>
```

- [ ] **Step 3: Add the page styles**

Add this style block after `</Layout>`. It intentionally uses CSS only and no external dependencies.

```astro
<style>
  :global(*) { box-sizing: border-box; }

  :global(html) { scroll-behavior: smooth; }

  :global(body) {
    margin: 0;
    min-height: 100vh;
    color: #f3f4f6;
    background: #030405;
    font-family: Inter, "Microsoft Yahei", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }

  .subscription-page {
    position: relative;
    min-height: 100vh;
    overflow: hidden;
    padding: 28px min(34px, 4vw) 42px;
    background:
      radial-gradient(circle at 12% 22%, rgba(255,255,255,.35) 0 1px, transparent 2px),
      radial-gradient(circle at 78% 16%, rgba(255,255,255,.45) 0 1px, transparent 2px),
      radial-gradient(circle at 46% 31%, rgba(255,255,255,.28) 0 1px, transparent 2px),
      radial-gradient(circle at 88% 58%, rgba(255,255,255,.24) 0 1px, transparent 2px),
      linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px),
      #030405;
    background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 42px 42px, 42px 42px, auto;
  }

  .subscription-page::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 50% 12%, rgba(255,255,255,.12), transparent 22%),
      linear-gradient(to bottom, rgba(3,4,5,.05), rgba(3,4,5,.45) 36%, rgba(3,4,5,.12));
  }

  .star {
    position: absolute;
    background:
      linear-gradient(90deg, transparent 48%, rgba(255,255,255,.72) 50%, transparent 52%),
      linear-gradient(0deg, transparent 48%, rgba(255,255,255,.72) 50%, transparent 52%);
    pointer-events: none;
  }

  .star-a { left: 12%; top: 25%; width: 38px; height: 38px; opacity: .34; }
  .star-b { right: 18%; top: 18%; width: 26px; height: 26px; opacity: .5; }
  .star-c { right: 7%; top: 46%; width: 42px; height: 42px; opacity: .22; }

  .identity,
  .portal-nav,
  .action-panel,
  .workspace-grid,
  .docs-window {
    position: relative;
    z-index: 1;
  }

  .identity {
    text-align: center;
    margin-bottom: 27px;
  }

  h1 {
    margin: 0;
    color: #fff;
    font-size: clamp(36px, 5vw, 48px);
    font-weight: 400;
    letter-spacing: -0.045em;
    line-height: 1;
    text-shadow: 0 0 16px rgba(255,255,255,.22);
  }

  .identity p {
    margin: 14px 0 0;
    color: #bababa;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 14px;
    letter-spacing: .22em;
  }

  .portal-nav {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 18px;
    width: min(720px, 100%);
    margin: 0 auto 28px;
  }

  .portal-nav a {
    position: relative;
    display: grid;
    gap: 8px;
    justify-items: center;
    color: #cecece;
    text-decoration: none;
  }

  .portal-nav a.active,
  .portal-nav a:hover,
  .portal-nav a:focus-visible {
    color: #fff;
  }

  .portal-nav a.active::after {
    content: "";
    position: absolute;
    bottom: -13px;
    width: 78%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.92), transparent);
    box-shadow: 0 0 20px rgba(255,255,255,.42);
  }

  .portal-nav span { font-size: 22px; }
  .portal-nav b { font-size: 16px; font-weight: 500; }

  .action-panel,
  .data-window {
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(16,18,22,.94);
    box-shadow: 0 28px 80px rgba(0,0,0,.58);
  }

  .action-panel {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 16px;
    align-items: center;
    width: min(900px, 100%);
    margin: 0 auto 24px;
    padding: 16px 18px;
    border-radius: 18px;
    backdrop-filter: blur(2px);
  }

  .action-line {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }

  .action-line strong { color: #fff; font-weight: 520; }
  .action-line small { color: #aaa; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }

  .status-pill {
    border-radius: 999px;
    padding: 4px 9px;
    color: #08090a;
    background: #f2f2f2;
    font-size: 12px;
    font-weight: 700;
  }

  .action-panel p {
    margin: 7px 0 0;
    color: #cfcfcf;
  }

  .action-buttons {
    display: flex;
    gap: 10px;
  }

  button,
  .action-buttons a {
    min-height: 42px;
    border-radius: 12px;
    padding: 0 16px;
    font: inherit;
    font-weight: 750;
    text-decoration: none;
    cursor: pointer;
  }

  button {
    border: 0;
    color: #050607;
    background: #f1f1f1;
  }

  .action-buttons a {
    display: inline-flex;
    align-items: center;
    border: 1px solid #454a52;
    color: #eeeeee;
    background: #1d2025;
  }

  button:focus-visible,
  a:focus-visible,
  summary:focus-visible {
    outline: 2px solid #fff;
    outline-offset: 3px;
  }

  .workspace-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 18px;
    align-items: start;
  }

  .data-window {
    border-radius: 20px;
    overflow: hidden;
  }

  .window-head {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: end;
    padding: 18px 20px;
    border-bottom: 1px solid rgba(255,255,255,.11);
  }

  h2 {
    margin: 0;
    color: #fff;
    font-size: 24px;
    font-weight: 560;
  }

  .window-head p {
    margin: 5px 0 0;
    color: #b2b2b2;
  }

  .window-head span {
    color: #c0c0c0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 13px;
    white-space: nowrap;
  }

  .ip-table { display: grid; }

  .ip-row {
    display: grid;
    grid-template-columns: 1.15fr 1fr .75fr .65fr .65fr;
    gap: 14px;
    align-items: center;
    padding: 18px 20px;
    border-top: 1px solid rgba(255,255,255,.085);
  }

  .ip-head {
    padding: 11px 20px;
    border-top: 0;
    color: #b5b5b5;
    background: rgba(255,255,255,.04);
    font-size: 12px;
  }

  .ip-scroll {
    max-height: 330px;
    overflow: auto;
  }

  .ip-row.current {
    background: rgba(255,255,255,.045);
    box-shadow: inset 3px 0 0 rgba(255,255,255,.72);
  }

  .ip-row b,
  .ip-row small {
    display: block;
  }

  .ip-row b {
    color: #fff;
    font-weight: 520;
  }

  .ip-row small {
    margin-top: 5px;
    color: #b8b8b8;
    font-size: 13px;
  }

  .ip-row span:first-child b,
  .ip-row span:nth-child(4) b {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }

  .side-stack {
    display: grid;
    gap: 14px;
  }

  .compact-window {
    padding: 17px;
  }

  .compact-window h2 {
    margin-bottom: 12px;
    font-size: 20px;
  }

  .node-list {
    display: grid;
    gap: 10px;
  }

  .node-list > div {
    border-top: 1px solid rgba(255,255,255,.11);
    padding-top: 10px;
  }

  .node-list div div,
  .traffic-summary {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .node-list p,
  .node-list small {
    margin: 4px 0 0;
    color: #b7b7b7;
    font-size: 13px;
  }

  .traffic-summary {
    color: #ededed;
    margin-bottom: 12px;
  }

  .bar-chart {
    display: flex;
    align-items: end;
    gap: 6px;
    height: 62px;
  }

  .bar-chart i {
    flex: 1;
    min-height: 8px;
    border-radius: 4px 4px 0 0;
    background: #666;
  }

  .bar-chart i:nth-child(6) {
    background: #f0f0f0;
    box-shadow: 0 0 16px rgba(255,255,255,.26);
  }

  .docs-window {
    margin-top: 18px;
  }

  .docs-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    padding: 18px 20px 20px;
  }

  details {
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 14px;
    padding: 14px;
    background: rgba(255,255,255,.025);
  }

  summary {
    color: #fff;
    cursor: pointer;
    font-weight: 650;
  }

  details p,
  details li {
    color: #c9c9c9;
    line-height: 1.65;
  }

  details ol {
    padding-left: 20px;
  }

  @media (prefers-reduced-motion: reduce) {
    :global(html) { scroll-behavior: auto; }
  }

  @media (max-width: 980px) {
    .workspace-grid,
    .action-panel,
    .docs-grid {
      grid-template-columns: 1fr;
    }

    .side-stack {
      grid-template-columns: 1fr 1fr;
    }

    .action-buttons {
      justify-content: stretch;
    }
  }

  @media (max-width: 720px) {
    .subscription-page {
      padding: 22px 14px 32px;
    }

    .identity p {
      font-size: 11px;
      letter-spacing: .12em;
    }

    .portal-nav {
      display: flex;
      overflow-x: auto;
      padding-bottom: 14px;
    }

    .portal-nav a {
      min-width: 76px;
    }

    .action-buttons,
    .side-stack {
      display: grid;
      grid-template-columns: 1fr;
    }

    .ip-head {
      display: none;
    }

    .ip-row,
    .ip-row.current {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .window-head {
      display: grid;
    }
  }
</style>
```

- [ ] **Step 4: Run the Playwright subscription test**

Run:

```bash
npm run test:e2e -- tests/subscribe.spec.ts
```

Expected: PASS.

- [ ] **Step 5: Run build**

Run:

```bash
npm run build
```

Expected: PASS.

- [ ] **Step 6: Commit the redesigned subscription page**

```bash
git add src/pages/subscribe.astro src/data/subscription.ts tests/subscribe.spec.ts
git commit -m "feat: redesign subscription workspace"
```

---

## Task 4: Add Subscription Center entry to `/about`

**Files:**
- Modify: `src/data/console.ts`
- Modify: `src/pages/about.astro`
- Test: `tests/console.spec.ts`

- [ ] **Step 1: Add a Subscription Center module to `src/data/console.ts`**

Append this export after `toolItems`:

```ts
export const subscriptionModule = {
  name: 'Subscription Center',
  status: 'ONLINE',
  summary: '订阅工作区，用于复制 active YAML、查看 IP 使用活动、节点状态和流量趋势。',
  url: '/subscribe',
  metrics: ['2/2 nodes', '3 IP today', 'updated 16:30'],
};
```

- [ ] **Step 2: Update the import in `src/pages/about.astro`**

Change line 3 from:

```astro
import { planItems, toolItems, workItems } from '../data/console';
```

to:

```astro
import { planItems, subscriptionModule, toolItems, workItems } from '../data/console';
```

- [ ] **Step 3: Add `subscribe` to the command list**

In the `commands` array, add this entry after `tools`:

```ts
['subscribe', 'Open Subscription Center workspace.'],
```

The command list should include:

```ts
const commands = [
  ['help', 'Show this command list.'],
  ['services', 'List service entrypoints.'],
  ['tools', 'List personal operation tools.'],
  ['subscribe', 'Open Subscription Center workspace.'],
  ['health', 'Fetch health API status.'],
  ['work', 'Show recent project work.'],
  ['plan', 'Show current learning plan.'],
  ['clear', 'Clear terminal screen.'],
  ['exit', 'Exit console and return home.'],
];
```

- [ ] **Step 4: Add a visible module card inside the terminal output**

After the existing Ready line in `#terminalOutput`, add:

```astro
<div class="subscription-module" aria-label="Subscription Center module">
  <div>
    <span class="tag ok">{subscriptionModule.status}</span>
    <strong>{subscriptionModule.name}</strong>
    <p>{subscriptionModule.summary}</p>
    <small>{subscriptionModule.metrics.join(' · ')}</small>
  </div>
  <a href={subscriptionModule.url}>Open Workspace</a>
</div>
```

- [ ] **Step 5: Include `subscriptionModule` in the client script variables**

Change the script opening from:

```astro
<script define:vars={{ commands, planItems, services, toolItems, workItems }}>
```

to:

```astro
<script define:vars={{ commands, planItems, services, subscriptionModule, toolItems, workItems }}>
```

- [ ] **Step 6: Add `renderSubscribe` in the client script**

Add this function after `renderTools`:

```js
    const renderSubscribe = () => `
      <div class="subscription-output">
        <p><span class="tag ok">${escapeHtml(subscriptionModule.status)}</span> ${escapeHtml(subscriptionModule.name)}</p>
        <p>${escapeHtml(subscriptionModule.summary)}</p>
        <p class="muted">${subscriptionModule.metrics.map(escapeHtml).join('    ')}</p>
        <p><a href="${escapeHtml(subscriptionModule.url)}">Open Subscription Workspace</a></p>
      </div>
    `;
```

- [ ] **Step 7: Route the new command**

Add this branch after the `tools` branch in `runCommand`:

```js
      if (command === 'subscribe') {
        append(renderSubscribe());
        return;
      }
```

- [ ] **Step 8: Add styles for the module card**

Add these styles near the existing `.tool-output` styles:

```css
  .subscription-module,
  .subscription-output {
    display: grid;
    gap: 10px;
    margin: 14px 0 18px;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px;
    padding: 14px;
    background: rgba(255,255,255,0.04);
  }

  .subscription-module {
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
  }

  .subscription-module strong {
    color: #f8fafc;
  }

  .subscription-module p,
  .subscription-output p {
    margin: 6px 0 0;
  }

  .subscription-module small {
    display: block;
    margin-top: 6px;
    color: #a1a1aa;
  }

  .subscription-module > a {
    border: 1px solid rgba(163, 230, 53, 0.45);
    border-radius: 10px;
    padding: 8px 12px;
    white-space: nowrap;
  }

  @media (max-width: 680px) {
    .subscription-module {
      grid-template-columns: 1fr;
    }
  }
```

- [ ] **Step 9: Update the console test**

Append this test to `tests/console.spec.ts`:

```ts
test('console exposes subscription center entry and command', async ({ page }) => {
  await page.goto('/about');

  await expect(page.getByLabel('Subscription Center module')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Open Workspace' })).toHaveAttribute('href', '/subscribe');

  const commandInput = page.getByRole('textbox', { name: 'Console command' });
  await commandInput.fill('subscribe');
  await commandInput.press('Enter');

  await expect(page.getByText('Open Subscription Workspace')).toBeVisible();
});
```

- [ ] **Step 10: Run console tests**

Run:

```bash
npm run test:e2e -- tests/console.spec.ts
```

Expected: PASS.

- [ ] **Step 11: Commit the `/about` integration**

```bash
git add src/data/console.ts src/pages/about.astro tests/console.spec.ts
git commit -m "feat: add subscription center to ops console"
```

---

## Task 5: Final verification and cleanup

**Files:**
- Verify all changed files.
- No new production files expected.

- [ ] **Step 1: Run the full frontend build**

```bash
npm run build
```

Expected: PASS.

- [ ] **Step 2: Run the full Playwright suite**

```bash
npm run test:e2e
```

Expected: PASS for `tests/home.spec.ts`, `tests/console.spec.ts`, and `tests/subscribe.spec.ts`.

- [ ] **Step 3: Inspect git status**

```bash
git status --short
```

Expected: only intentional uncommitted files, or clean if every task was committed. Do not commit unrelated untracked directories such as `.superpowers/`, `.agents/`, `.claude/`, or `skills-lock.json` unless the user explicitly asks.

- [ ] **Step 4: Manual browser verification**

Run:

```bash
npm run dev
```

Open:

```text
http://localhost:4321/about
http://localhost:4321/subscribe
```

Verify:

- `/about` shows the Subscription Center module.
- `subscribe` command prints the subscription workspace link.
- `/subscribe` visually follows the approved v6 direction: black, sparse starlight, centered TTLINK, monochrome panels.
- The five icon entries scroll to their corresponding sections and do not behave as tabs.
- The full subscription URL is not visible as page text.
- Copy subscription copies the URL and shows `已复制`.
- Open YAML points to the real subscription URL.
- IP activity is the largest first-screen data window.
- Traffic is a compact supporting panel with no quota/budget card.
- Mobile viewport has no horizontal overflow.

- [ ] **Step 5: Commit any final fixes**

If Step 4 requires adjustments, commit only those files:

```bash
git add src/pages/subscribe.astro src/pages/about.astro src/data/subscription.ts src/data/console.ts tests/subscribe.spec.ts tests/console.spec.ts
git commit -m "fix: polish subscription workspace verification issues"
```

Skip this commit if no fixes are needed.

---

## Self-Review

Spec coverage:

- `/subscribe` redesign: covered by Tasks 2 and 3.
- `/about` integration: covered by Task 4.
- Hidden URL and copy/open actions: covered by Task 3 and `tests/subscribe.spec.ts`.
- IP activity as primary content: covered by Task 3.
- No traffic quota: covered by data model and Task 3 layout.
- Five icon entries as anchors, not tabs: covered by Task 3 and test assertions.
- Monochrome starlight visual direction: covered by Task 3 CSS and manual verification.
- Mobile usability: covered by Task 3 CSS and Task 5 manual verification.

Placeholder scan:

- No `TBD`, `TODO`, `implement later`, or unspecified edge handling remains.
- Every code-changing step includes concrete code or exact replacement snippets.

Type consistency:

- `subscriptionOverview`, `subscriptionWorkspaceNav`, `ipStats`, `proxyNodes`, `trafficBars`, and `opsDocs` are defined in Task 1 and used consistently in Task 3.
- `subscriptionModule` is defined in Task 4 and used consistently in `/about` markup and client script.
