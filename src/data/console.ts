export const workItems = [
  'TTLINK Home 主站上线到 Cloudflare Pages',
  '绑定自定义域名 https://home.ttlink.asia',
  'GitHub Actions 接入 Astro build 和 Playwright 首页冒烟',
  'FastAPI Health API 完成本地开发、pytest 契约测试和 CI 接入',
  'Health API 部署到阿里云，使用 systemd、Nginx 和 Let\'s Encrypt 托管',
];

export const planItems = [
  '让主站 Console 支持真正的命令输入',
  '让 health 命令读取 https://health.ttlink.asia/api/v1/health',
  '根据需要为 FastAPI 增加 CORS 配置',
  '把 Health API 状态接入主站首页',
  '设计 GitHub Actions 控制 Cloudflare Pages 部署的发布闸门',
  '规划知识图谱 graph.ttlink.asia 的上线方式',
];

export const toolItems = [
  {
    name: 'CPA Helper',
    description: '用量统计、API Key 管理、用户余额和模型价格维护。',
    url: 'https://cpa.ttlink.asia',
  },
  {
    name: 'CLIProxyAPI',
    description: '模型代理管理面板，用于管理 provider、API Key 和路由。',
    url: 'https://cli.ttlink.asia/management.html',
  },
  {
    name: 'Subs Portal',
    description: '订阅门户，用于管理代理订阅和节点入口。',
    url: 'https://subs.ttlink.asia/subs.html',
  },
  {
    name: 'Health API',
    description: '服务健康检查接口，用于查看核心服务可用性。',
    url: 'https://health.ttlink.asia/api/v1/health',
  },
];
