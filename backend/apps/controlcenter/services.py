from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class StatCard:
    label: str
    value: str
    trend: str
    status: str


@dataclass(frozen=True)
class IncidentPrediction:
    service: str
    score: float
    horizon: str
    recommended_action: str


DASHBOARD_CARDS = [
    StatCard('Availability', '99.982%', '+0.12%', 'healthy'),
    StatCard('Active Alerts', '7', '-3', 'warning'),
    StatCard('Auto Remediations', '18', '+5', 'healthy'),
    StatCard('Knowledge Coverage', '86%', '+9%', 'improving'),
]

METRICS_TIMELINE = [
    {'time': '09:00', 'latency': 142, 'error_rate': 0.9, 'cpu': 41},
    {'time': '09:30', 'latency': 155, 'error_rate': 1.2, 'cpu': 47},
    {'time': '10:00', 'latency': 187, 'error_rate': 1.8, 'cpu': 53},
    {'time': '10:30', 'latency': 171, 'error_rate': 1.1, 'cpu': 49},
    {'time': '11:00', 'latency': 163, 'error_rate': 0.7, 'cpu': 45},
]

PREDICTIONS = [
    IncidentPrediction(
        service='checkout-api',
        score=0.82,
        horizon='next 30 minutes',
        recommended_action='Scale worker pool and invalidate slow cache shards.',
    ),
    IncidentPrediction(
        service='log-ingestor',
        score=0.61,
        horizon='next 2 hours',
        recommended_action='Throttle non-critical pipelines and inspect Kafka lag.',
    ),
]

RUNBOOK = {
    'observability': [
        'Aggregate Prometheus, Loki, and OpenTelemetry signals into a unified service health graph.',
        'Track golden signals, deploy changes, and error budgets per service and environment.',
    ],
    'agent_operations': [
        'Continuously monitor the agent itself with heartbeats, queue depth, token usage, and tool success rate.',
        'Trigger alerts, explain root cause hypotheses, predict incidents, and execute guarded self-healing actions.',
    ],
    'knowledge_base': [
        'Index SOPs, architecture docs, incident postmortems, and CMDB metadata for retrieval.',
        'Surface citations and recommended runbooks during every operator conversation.',
    ],
    'chatops': [
        'Provide a conversational control plane for operators and managers to inspect metrics, logs, incidents, and actions.',
        'Support role-based prompts such as incident commander mode and executive status briefing mode.',
    ],
}


def build_dashboard_payload() -> dict[str, Any]:
    return {
        'cards': [asdict(card) for card in DASHBOARD_CARDS],
        'timeline': METRICS_TIMELINE,
        'predictions': [asdict(item) for item in PREDICTIONS],
        'chatops_examples': [
            'Show me latency anomalies for checkout-api in production during the last 60 minutes.',
            'Summarize today\'s active alerts, probable root causes, and suggested next actions.',
            'Open the payment-service runbook and prepare a self-healing plan for connection saturation.',
        ],
    }


def build_runbook_payload() -> dict[str, Any]:
    return RUNBOOK
