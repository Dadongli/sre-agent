export const dashboard = {
  cards: [
    { label: 'Availability', value: '99.982%', trend: '+0.12%', status: 'healthy' },
    { label: 'Active Alerts', value: '7', trend: '-3', status: 'warning' },
    { label: 'Auto Remediations', value: '18', trend: '+5', status: 'healthy' },
    { label: 'Knowledge Coverage', value: '86%', trend: '+9%', status: 'improving' },
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
    'Summarize today\'s active alerts, probable root causes, and suggested next actions.',
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
