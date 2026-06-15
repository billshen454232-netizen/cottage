export type ServiceEntry = {
  name: string;
  description: string;
  url: string;
  status: '已上线' | '计划中';
};

export type ToolEntry = {
  name: string;
  description: string;
  url: string;
};

export const serviceEntries: ServiceEntry[] = [
  {
    name: '订阅门户',
    description: '订阅工作区，用于复制 active YAML、查看 IP 使用活动、节点状态和流量趋势。',
    url: '/subscribe',
    status: '已上线',
  },
  {
    name: 'CLI Proxy API',
    description: '模型代理管理面板，用于管理 provider、API Key 和路由。',
    url: 'https://cli.ttlink.asia/management.html',
    status: '已上线',
  },
  {
    name: '个人博客',
    description: '博客内容入口。',
    url: 'https://blog.ttlink.asia',
    status: '计划中',
  },
  {
    name: '知识图谱',
    description: '个人知识图谱入口。',
    url: 'https://graph.ttlink.asia',
    status: '计划中',
  },
];

export const scriptTools: ToolEntry[] = [
  {
    name: 'Health API',
    description: '无界面的健康检查脚本，用于查看核心服务可用性。',
    url: 'https://health.ttlink.asia/api/v1/health',
  },
];

export const services = serviceEntries;
