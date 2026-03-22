export const navigation = [
  { label: 'Overview', description: '首页总览', href: '#overview', active: true },
  { label: 'Observability', description: '指标 / 日志 / 链路', href: '#observability' },
  { label: 'Incidents', description: '告警 / 根因 / 自愈', href: '#incidents' },
  { label: 'Capabilities', description: '能力地图', href: '#capabilities' },
  { label: 'Knowledge', description: '知识库搜索', href: '#knowledge' },
  { label: 'ChatOps', description: '自然语言操作台', href: '#chatops' },
]

export const quickActions = [
  {
    title: '创建值班简报',
    description: '按当前活跃告警、风险服务和自愈动作生成可共享的交接摘要。',
    outcome: '已生成 06:00 UTC 值班简报，覆盖 7 条告警与 2 个重点服务。',
    status: 'Ready',
    tone: 'healthy',
  },
  {
    title: '触发 runbook',
    description: '拉起与当前故障最相关的 SOP，并记录审批与执行上下文。',
    outcome: '已为 checkout-api 载入缓存失效 runbook，等待人工确认执行。',
    status: 'Pending',
    tone: 'warning',
  },
  {
    title: '查看告警抑制',
    description: '查看当前静默窗口、抑制规则和到期时间，避免重复响应。',
    outcome: '发现 2 条 P3 告警处于抑制窗口，15 分钟后到期。',
    status: 'Synced',
    tone: 'improving',
  },
  {
    title: '打开知识库检索',
    description: '跳转到知识中心，直接搜索相关 SOP、架构图与复盘记录。',
    outcome: '知识库搜索已聚焦关键字“runbook”，返回 3 条相关文档。',
    status: 'Indexed',
    tone: 'healthy',
  },
]

export const workbenchTabs = [
  {
    key: 'oncall',
    label: '值班视角',
    value: 'On-call',
    headline: '先聚焦待处理告警与高风险服务，缩短故障响应路径。',
    description: '值班模式下优先展示故障风险、待确认动作和最短处置路径。',
    kpi: '7 active alerts',
    tone: 'warning',
    tasks: [
      { title: 'P1 checkout-api', detail: '支付链路 95 分位延迟升高，建议先扩容 worker。', status: 'Urgent', tone: 'warning' },
      { title: 'Runbook 审批', detail: '待确认执行缓存失效与慢查询隔离动作。', status: 'Pending', tone: 'improving' },
    ],
  },
  {
    key: 'platform',
    label: '平台视角',
    value: 'Platform',
    headline: '追踪平台容量、水位与自动化闭环的执行效果。',
    description: '平台模式用于观察资源冗余、自动化收益和跨服务稳定性趋势。',
    kpi: '18 remediations',
    tone: 'healthy',
    tasks: [
      { title: 'Kafka backlog', detail: 'log-ingestor 延迟抬升，建议重新分配 consumer。', status: 'Watching', tone: 'warning' },
      { title: 'Agent 成功率', detail: '过去 24h 工具调用成功率 98.7%，满足基线。', status: 'Stable', tone: 'healthy' },
    ],
  },
  {
    key: 'executive',
    label: '管理视角',
    value: 'Executive',
    headline: '把风险、交付影响和恢复预期汇总成管理可读的信息。',
    description: '管理模式面向决策层，强调趋势、业务影响与团队处置进展。',
    kpi: '99.982% availability',
    tone: 'improving',
    tasks: [
      { title: '业务影响', detail: '当前仅支付链路存在轻微退化，无大面积用户损失。', status: 'Controlled', tone: 'healthy' },
      { title: '错误预算', detail: 'payment-gateway 仍保有 72% error budget。', status: 'Healthy', tone: 'improving' },
    ],
  },
  {
    key: 'command',
    label: 'ChatOps',
    value: 'Command',
    headline: '自然语言触发查询、摘要和下一步动作建议。',
    description: 'ChatOps 模式让值班与管理人员通过统一对话界面获取状态和执行建议。',
    kpi: '3 preset prompts',
    tone: 'healthy',
    tasks: [
      { title: '快速摘要', detail: '生成当前活跃告警与处置建议的日报草稿。', status: 'Ready', tone: 'healthy' },
      { title: '知识引用', detail: '每次回答都附带 SOP/复盘上下文，便于人工确认。', status: 'Enabled', tone: 'improving' },
    ],
  },
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
    summary: '支付入口流量上升后已完成弹性扩容，当前恢复至绿色基线。',
  },
  {
    name: 'log-ingestor',
    owner: 'Owner: Data Platform · Kafka Pipeline',
    status: 'Degraded',
    statusTone: 'warning',
    slo: 'Lag +18%',
    lastEvent: '最近动作：非关键 topic 已限流',
    summary: '日志摄取链路存在积压，正在通过限流与 consumer rebalance 缓解。',
  },
  {
    name: 'payment-gateway',
    owner: 'Owner: FinOps Reliability · Multi AZ',
    status: 'Protected',
    statusTone: 'improving',
    slo: 'Error budget 72%',
    lastEvent: '最近动作：熔断策略已下发',
    summary: '关键依赖已进入保护模式，自愈策略完成发布并等待持续观察。',
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
      recommendedAction: 'Scale worker pool, invalidate slow cache shards, and confirm DB queue depth.',
      status: 'Needs approval',
      tone: 'warning',
      owner: '审批人：值班 SRE / 数据库 Owner',
    },
    {
      service: 'log-ingestor',
      score: 0.61,
      horizon: 'next 2 hours',
      recommendedAction: 'Throttle non-critical pipelines, inspect Kafka lag, and rebalance consumers.',
      status: 'Executing',
      tone: 'improving',
      owner: '执行中：Data Platform 自动化机器人',
    },
  ],
  chatopsExamples: [
    'Show me latency anomalies for checkout-api in production during the last 60 minutes.',
    "Summarize today's active alerts, probable root causes, and suggested next actions.",
    'Open the payment-service runbook and prepare a self-healing plan for connection saturation.',
  ],
}

export const knowledgeDocuments = [
  {
    title: 'checkout-api 缓存失效 Runbook',
    summary: '覆盖缓存击穿、慢查询、worker 扩容与回滚观察步骤。',
    tags: ['runbook', 'checkout-api', 'redis'],
    type: 'SOP',
    tone: 'healthy',
  },
  {
    title: 'log-ingestor 积压复盘',
    summary: '总结 Kafka topic 倾斜、consumer 配额和限流策略的经验。',
    tags: ['postmortem', 'kafka', 'pipeline'],
    type: 'Postmortem',
    tone: 'warning',
  },
  {
    title: 'payment-gateway 依赖拓扑',
    summary: '记录支付链路上游依赖、熔断策略与跨 AZ 容灾路径。',
    tags: ['cmdb', 'topology', 'payment'],
    type: 'CMDB',
    tone: 'improving',
  },
]

export const chatopsPresets = [
  {
    label: '汇总告警',
    prompt: '请汇总今天的活跃告警、可能根因以及建议的下一步动作。',
  },
  {
    label: '检查支付链路',
    prompt: '请检查 payment-gateway 最近 1 小时的风险状态，并给出处置建议。',
  },
  {
    label: '诊断摄取积压',
    prompt: '分析 log-ingestor 当前积压情况，并给出 runbook 建议。',
  },
]

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
