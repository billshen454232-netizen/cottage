# TTLINK Personal Ops Hub

`ttlink-home` 是 TTLINK 的个人主站、运维入口和测开 / DevOps 实践项目。它不是单纯的静态展示页，而是用一个轻量站点串起 Cloudflare Pages、GitHub Actions、Aliyun 服务、订阅中心状态 JSON、Playwright 冒烟测试和后续运维自动化练习。

## 当前能力

- `home.ttlink.asia`：个人主站，部署在 Cloudflare Pages。
- `/about`：My Ops Console，聚合服务入口和操作说明。
- `/subscribe`：订阅中心前端，读取订阅状态 JSON 并展示订阅、节点、IP 活动和文档。
- GitHub Actions：运行 Astro build 和 Playwright E2E 冒烟测试。
- Aliyun collector：定时生成 `subscription-status.json`，供 `/subscribe` 前端读取。

## 架构图

```text
Developer
  |
  | git push main
  v
GitHub Repository: ttlink-home
  |
  | GitHub Actions
  | - npm run build
  | - npm run test:e2e
  |
  v
Cloudflare Pages
  |
  | serves static Astro site
  v
https://home.ttlink.asia
  |
  +--> /about
  |      Personal Ops Console
  |
  +--> /subscribe
         |
         | browser fetch
         v
https://subs.ttlink.asia/subs/subscription-status.json
  |
  | Cloudflare orange cloud
  v
Aliyun Nginx
  |
  | exact whitelist location
  v
/etc/letsencrypt/subs/subscription-status.json
  ^
  |
  | generated every 5 minutes by cron
  |
/opt/ttlink-subscription-collector.py
  |
  +--> auto-discovers newest /etc/letsencrypt/subs/subs-*.yaml
  +--> reads service status: nginx / xray / hysteria
  +--> reads listening ports: 443/tcp, 443/udp, 10000/tcp
  +--> reads nginx access log for lightweight IP activity
```

## 服务边界

| 域名 / 路径 | 作用 | 部署位置 |
|---|---|---|
| `https://home.ttlink.asia` | Personal Ops Hub 主站 | Cloudflare Pages |
| `https://home.ttlink.asia/about` | My Ops Console | Cloudflare Pages |
| `https://home.ttlink.asia/subscribe` | 订阅中心前端页面 | Cloudflare Pages |
| `https://subs.ttlink.asia/subs/subscription-status.json` | 订阅中心状态 JSON | Aliyun Nginx 静态白名单 |
| `https://subs.ttlink.asia/subs/<active>.yaml` | Clash / Mihomo 订阅 YAML | Aliyun Nginx 静态白名单 |
| `hy.ttlink.asia` | Hysteria2 UDP/QUIC 节点 | Aliyun，Cloudflare DNS-only |
| `vless.ttlink.asia` | VLESS WebSocket TLS fallback | Cloudflare orange cloud → Aliyun Nginx → Xray |

注意：`/subscribe` 页面由 Cloudflare Pages 托管，但生产数据来自 Aliyun 上的 `subs.ttlink.asia`。主站不生成订阅数据。

## 订阅状态数据流

生产环境：

```text
cron
  -> /usr/bin/python3 /opt/ttlink-subscription-collector.py --out /etc/letsencrypt/subs/subscription-status.json
  -> collector 自动发现最新 /etc/letsencrypt/subs/subs-*.yaml
  -> 写入 /etc/letsencrypt/subs/subscription-status.json
  -> nginx 通过精确 location 暴露 JSON
  -> /subscribe 前端 fetch 线上 JSON
```

本地开发：

```text
npm run dev
  -> /subscribe
  -> fetch /subscription-status.sample.json
```

设计原则：

- cron 不写死随机订阅 YAML 文件名。
- collector 未传 `--yaml` 时自动发现最新 `subs-*.yaml`。
- `subscription.url` 根据当前 YAML 文件名生成，订阅地址轮换时不需要改 cron。
- nginx 只放行指定 YAML 和 `subscription-status.json`，其他 `/subs/` 路径保持 `410`。
- `clients[]` 目前来自 nginx access log，只代表订阅相关 HTTP 访问活动，不代表 HY2/Xray 精准代理流量。
- Cloudflare 橙云下，`clients[].ip` 可能是 Cloudflare edge IP；如需真实客户端 IP，需要后续配置 nginx real IP 和 `CF-Connecting-IP`。

## 本地开发

要求：

- Node.js `>=22.12.0`
- npm

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

常用访问：

```text
http://localhost:4321
http://localhost:4321/about
http://localhost:4321/subscribe
```

## 构建与测试

构建：

```bash
npm run build
```

运行 Playwright E2E：

```bash
npm run test:e2e
```

只跑订阅中心测试：

```bash
npm run test:e2e -- tests/subscribe.spec.ts
```

当前 E2E 测试原则：

- 测核心行为，不测易变文案。
- `/subscribe` 只验证：复制按钮能复制、状态 JSON 能获取。
- 不把节点数量、节点名称、状态文案、时间戳等可配置内容写死进测试。

## 部署流程

当前部署模式：

```text
git push origin main
  -> GitHub Actions 运行 build / e2e
  -> Cloudflare Pages 自动构建部署
```

当前 GitHub Actions 不是发布闸门；Cloudflare Pages 会按自己的集成自动部署。后续可以演进为 GitHub Actions 测试全部通过后，再由 Actions 调 Cloudflare API 发布 `dist`。

## Aliyun collector 运维

服务器脚本路径：

```text
/opt/ttlink-subscription-collector.py
```

输出文件：

```text
/etc/letsencrypt/subs/subscription-status.json
```

推荐 cron：

```cron
*/5 * * * * /usr/bin/python3 /opt/ttlink-subscription-collector.py --out /etc/letsencrypt/subs/subscription-status.json >> /var/log/ttlink-subscription-collector.log 2>&1
```

手动验证 JSON：

```bash
curl -s https://subs.ttlink.asia/subs/subscription-status.json | python3 -m json.tool | head -n 80
```

查看 collector 日志：

```bash
tail -n 50 /var/log/ttlink-subscription-collector.log
```

## 关键文件

```text
src/pages/index.astro                         # 主站首页
src/pages/about.astro                         # My Ops Console
src/pages/subscribe.astro                     # 订阅中心页面
src/data/subscription.ts                      # 订阅中心静态占位数据
public/subscription-status.sample.json        # 本地开发 sample JSON
scripts/collect-subscription-status.py        # Aliyun 状态 JSON collector
tests/subscribe.spec.ts                       # /subscribe E2E 测试
docs/subscription-status-contract.md          # 状态 JSON 契约
docs/superpowers/plans/2026-06-12-subscription-ops-data-learning-plan.md
                                                # 订阅中心数据链路学习计划
```

## 后续计划

优先级从轻到重：

1. 补充 runbook 手动检查清单。
2. 配置 nginx real IP，让 `clients[]` 尽量显示真实客户端 IP。
3. 基于 `generatedAt` 增加 stale-data warning。
4. 接入 Hysteria2 Traffic Stats API。
5. 接入 Xray Stats API。
6. 稳定后再评估 Cloudflare R2 / Worker 云原生迁移。
