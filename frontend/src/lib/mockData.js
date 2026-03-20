export const navigation = [
  { label: 'Overview', description: '首页总览', href: '#overview', active: true },
  { label: 'Observability', description: '指标 / 日志 / 链路', href: '#observability' },
  { label: 'Incidents', description: '告警 / 根因 / 自愈', href: '#incidents' },
  { label: 'Capabilities', description: '能力地图', href: '#capabilities' },
  { label: 'ChatOps', description: '自然语言操作台', href: '#chatops' },
]

export const quickActions = ['创建值班简报', '触发 runbook', '查看告警抑制', '打开知识库检索']

export const workbenchTabs = [
  { label: '值班视角', value: 'On-call' },
  { label: '平台视角', value: 'Platform' },
  { label: '管理视角', value: 'Executive' },
]

export const capabilityHighlights = [
  {
    tag: 'Observability',
    title: '统一信号入口',
    description: '将指标、日志、链路、变更事件统一编排到首页视图，降低故障定位切换成本。',
  },
  {
    tag: 'Automation',
    title: '受控自愈闭环',
    description: '为故障预测、风险评估、Runbook 执行与审核确认预留标准化 UI 承载层。',
  },
  {
    tag: 'Knowledge',
    title: '知识检索基座',
    description: '沉淀 SOP、架构文档、复盘结论和 CMDB 元数据的统一消费入口。',
  },
]

export const serviceHealth = [
  {
    name: 'checkout-api',
    owner: 'Owner: Commerce SRE · Region: ap-southeast-1',
    status: 'Healthy',
    statusTone: 'healthy',
    slo: '99.95% SLO',
    lastEvent: '最近动作：扩容 worker 30 分钟前完成',
  },
  {
    name: 'log-ingestor',
    owner: 'Owner: Data Platform · Kafka Pipeline',
    status: 'Degraded',
    statusTone: 'warning',
    slo: 'Lag +18%',
    lastEvent: '最近动作：非关键 topic 已限流',
  },
  {
    name: 'payment-gateway',
    owner: 'Owner: FinOps Reliability · Multi AZ',
    status: 'Protected',
    statusTone: 'improving',
    slo: 'Error budget 72%',
    lastEvent: '最近动作：熔断策略已下发',
  },
]

export const dashboard = {
  cards: [
    {
      label: 'Availability',
      value: '99.982%',
      trend: '+0.12%',
      status: 'healthy',
      statusTone: 'healthy',
      badge: 'Stable',
      meta: '近 24h 聚合可用性',
    },
    {
      label: 'Active Alerts',
      value: '7',
      trend: '-3',
      status: 'warning',
      statusTone: 'warning',
      badge: 'Needs triage',
      meta: 'P1=1 / P2=2 / P3=4',
    },
    {
      label: 'Auto Remediations',
      value: '18',
      trend: '+5',
      status: 'healthy',
      statusTone: 'healthy',
      badge: 'Executed',
      meta: '过去 7 天自动闭环次数',
    },
    {
      label: 'Knowledge Coverage',
      value: '86%',
      trend: '+9%',
      status: 'improving',
      statusTone: 'improving',
      badge: 'Growing',
      meta: '关键服务 SOP 覆盖率',
    },
  ],
  timeline: [
    { time: '09:00', latency: 142, errorRate: 0.9, cpu: 41 },
    { time: '09:30', latency: 155, errorRate: 1.2, cpu: 47 },
    { time: '10:00', latency: 187, errorRate: 1.8, cpu: 53 },
    { time: '10:30', latency: 171, errorRate: 1.1, cpu: 49 },
    { time: '11:00', latency: 163, errorRate: 0.7, cpu: 45 },
  ],
  predictions: [
    {
      service: 'checkout-api',
      score: 0.82,
      horizon: 'next 30 minutes',
      recommendedAction: 'Scale worker pool and invalidate slow cache shards.',
    },
    {
      service: 'log-ingestor',
      score: 0.61,
      horizon: 'next 2 hours',
      recommendedAction: 'Throttle non-critical pipelines and inspect Kafka lag.',
    },
  ],
  chatopsExamples: [
    'Show me latency anomalies for checkout-api in production during the last 60 minutes.',
    "Summarize today's active alerts, probable root causes, and suggested next actions.",
    'Open the payment-service runbook and prepare a self-healing plan for connection saturation.',
  ],
}

export const runbook = {
  observability: [
    'Prometheus + Loki + OpenTelemetry unified signal graph',
    'Golden signals, release markers, and error budgets per service',
  ],
  agentOperations: [
    'Heartbeat, queue depth, token usage, tool success rate, and policy audit',
    'Alerts, root cause hypotheses, failure prediction, and guarded self-healing',
  ],
  knowledgeBase: [
    'Index SOPs, postmortems, CMDB records, and architecture decisions',
    'Cited retrieval to support every ChatOps answer',
  ],
  chatops: [
    'Natural-language commands for metrics, logs, traces, incidents, and reports',
    'Dedicated operator and management conversation modes',
  ],
}
