from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    AgentSnapshot,
    AutomationExecution,
    Environment,
    Incident,
    IncidentPrediction,
    KnowledgeDocument,
    Runbook,
    Service,
)


@dataclass(frozen=True)
class StatCard:
    label: str
    value: str
    trend: str
    status: str


@dataclass(frozen=True)
class PredictionCard:
    service: str
    score: float
    horizon: str
    recommended_action: str
    probable_cause: str
    confidence: float


FALLBACK_TIMELINE = [
    {'time': '09:00', 'latency': 142, 'error_rate': 0.9, 'cpu': 41},
    {'time': '09:30', 'latency': 155, 'error_rate': 1.2, 'cpu': 47},
    {'time': '10:00', 'latency': 187, 'error_rate': 1.8, 'cpu': 53},
    {'time': '10:30', 'latency': 171, 'error_rate': 1.1, 'cpu': 49},
    {'time': '11:00', 'latency': 163, 'error_rate': 0.7, 'cpu': 45},
]

FALLBACK_RUNBOOK = {
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

RUNBOOK_DOMAIN_MAPPING = {
    'observability': {Runbook.Domain.OBSERVABILITY},
    'agent_operations': {Runbook.Domain.AUTOMATION, Runbook.Domain.GOVERNANCE, Runbook.Domain.INCIDENT},
    'knowledge_base': {Runbook.Domain.KNOWLEDGE},
    'chatops': {Runbook.Domain.CHATOPS},
}

KNOWLEDGE_TYPE_MAPPING = {
    'observability': {KnowledgeDocument.DocumentType.ARCHITECTURE, KnowledgeDocument.DocumentType.CMDB},
    'agent_operations': {KnowledgeDocument.DocumentType.SOP, KnowledgeDocument.DocumentType.POSTMORTEM},
    'knowledge_base': {KnowledgeDocument.DocumentType.FAQ, KnowledgeDocument.DocumentType.SOP},
    'chatops': {KnowledgeDocument.DocumentType.FAQ},
}


class ControlCenterDomainService:
    def __init__(self, service_slug: str | None = None, environment_slug: str | None = None):
        self.service_slug = service_slug
        self.environment_slug = environment_slug

    def build_dashboard_payload(self) -> dict[str, Any]:
        services = self._services()
        environments = self._environments()
        incidents = self._incidents()
        predictions = self._predictions()
        snapshots = self._snapshots()
        executions = self._executions()

        return {
            'scope': self._scope_payload(services, environments),
            'cards': [
                asdict(self._build_availability_card(incidents)),
                asdict(self._build_active_alerts_card(incidents)),
                asdict(self._build_auto_remediation_card(executions)),
                asdict(self._build_knowledge_coverage_card(services)),
            ],
            'timeline': self._build_timeline(snapshots),
            'predictions': self._build_predictions(predictions),
            'chatops_examples': self._build_chatops_examples(),
            'service_overview': self._build_service_overview(services, incidents),
        }

    def build_runbook_payload(self) -> dict[str, Any]:
        services = self._services()
        runbooks = self._runbooks()
        knowledge_documents = self._knowledge_documents()

        payload = {
            section: self._build_runbook_section(section, runbooks, knowledge_documents)
            for section in FALLBACK_RUNBOOK
        }

        return {
            **payload,
            'scope': self._scope_payload(services, self._environments()),
        }

    def _services(self):
        queryset = Service.objects.select_related('owning_team').all()
        if self.service_slug:
            queryset = queryset.filter(slug=self.service_slug)
        if self.environment_slug:
            queryset = queryset.filter(environments__slug=self.environment_slug)
        return queryset.distinct()

    def _environments(self):
        queryset = Environment.objects.all()
        if self.environment_slug:
            queryset = queryset.filter(slug=self.environment_slug)
        if self.service_slug:
            queryset = queryset.filter(services__slug=self.service_slug)
        return queryset.distinct()

    def _incidents(self):
        queryset = Incident.objects.select_related('service', 'environment')
        if self.service_slug:
            queryset = queryset.filter(service__slug=self.service_slug)
        if self.environment_slug:
            queryset = queryset.filter(environment__slug=self.environment_slug)
        return queryset

    def _predictions(self):
        queryset = IncidentPrediction.objects.select_related('service', 'environment')
        if self.service_slug:
            queryset = queryset.filter(service__slug=self.service_slug)
        if self.environment_slug:
            queryset = queryset.filter(environment__slug=self.environment_slug)
        return queryset.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now()))

    def _snapshots(self):
        return AgentSnapshot.objects.order_by('-snapshot_at')[:6]

    def _executions(self):
        queryset = AutomationExecution.objects.select_related('service', 'environment')
        if self.service_slug:
            queryset = queryset.filter(service__slug=self.service_slug)
        if self.environment_slug:
            queryset = queryset.filter(environment__slug=self.environment_slug)
        return queryset

    def _runbooks(self):
        queryset = Runbook.objects.select_related('linked_service')
        if self.service_slug:
            queryset = queryset.filter(Q(linked_service__slug=self.service_slug) | Q(linked_service__isnull=True))
        return queryset

    def _knowledge_documents(self):
        queryset = KnowledgeDocument.objects.select_related('service')
        if self.service_slug:
            queryset = queryset.filter(Q(service__slug=self.service_slug) | Q(service__isnull=True))
        return queryset

    def _scope_payload(self, services, environments) -> dict[str, Any]:
        service_names = list(services.values_list('name', flat=True)[:5])
        environment_names = list(environments.values_list('name', flat=True)[:5])
        return {
            'service': self.service_slug,
            'environment': self.environment_slug,
            'service_count': services.count(),
            'environment_count': environments.count(),
            'services': service_names,
            'environments': environment_names,
        }

    def _build_availability_card(self, incidents) -> StatCard:
        total = incidents.count()
        resolved = incidents.filter(status=Incident.Status.RESOLVED).count()
        availability = 100.0 if total == 0 else (resolved / total) * 100
        return StatCard(
            label='Availability',
            value=f'{availability:.3f}%',
            trend=f'{resolved}/{total or 0} resolved incidents',
            status='healthy' if availability >= 99 else 'warning',
        )

    def _build_active_alerts_card(self, incidents) -> StatCard:
        active_count = incidents.exclude(status=Incident.Status.RESOLVED).count()
        sev0_or_sev1 = incidents.filter(
            severity__in=[Incident.Severity.SEV0, Incident.Severity.SEV1],
        ).exclude(status=Incident.Status.RESOLVED).count()
        return StatCard(
            label='Active Alerts',
            value=str(active_count),
            trend=f'{sev0_or_sev1} high-severity incidents',
            status='warning' if active_count else 'healthy',
        )

    def _build_auto_remediation_card(self, executions) -> StatCard:
        recent_window = timezone.now() - timezone.timedelta(days=7)
        succeeded_count = executions.filter(
            status=AutomationExecution.Status.SUCCEEDED,
            created_at__gte=recent_window,
        ).count()
        running_count = executions.filter(status=AutomationExecution.Status.RUNNING).count()
        return StatCard(
            label='Auto Remediations',
            value=str(succeeded_count),
            trend=f'{running_count} running workflows',
            status='healthy' if running_count == 0 else 'warning',
        )

    def _build_knowledge_coverage_card(self, services) -> StatCard:
        total_services = services.count()
        documented_services = KnowledgeDocument.objects.exclude(service__isnull=True)
        if self.service_slug:
            documented_services = documented_services.filter(service__slug=self.service_slug)
        covered_count = documented_services.values('service').distinct().count()
        coverage = 100.0 if total_services == 0 else (covered_count / total_services) * 100
        return StatCard(
            label='Knowledge Coverage',
            value=f'{coverage:.0f}%',
            trend=f'{covered_count}/{total_services or 0} services documented',
            status='improving' if coverage >= 70 else 'warning',
        )

    def _build_timeline(self, snapshots) -> list[dict[str, Any]]:
        snapshot_items = list(snapshots)
        if not snapshot_items:
            return FALLBACK_TIMELINE

        timeline = []
        for snapshot in reversed(snapshot_items):
            error_rate = round(
                min(snapshot.active_incidents * 0.35 + (1 - float(snapshot.tool_success_rate)) * 100, 100),
                2,
            )
            timeline.append(
                {
                    'time': snapshot.snapshot_at.strftime('%H:%M'),
                    'latency': int(120 + snapshot.queue_depth * 6 + snapshot.active_incidents * 14),
                    'error_rate': error_rate,
                    'cpu': min(35 + snapshot.queue_depth * 4, 100),
                }
            )
        return timeline

    def _build_predictions(self, predictions) -> list[dict[str, Any]]:
        prediction_cards = [
            PredictionCard(
                service=item.service.name,
                score=float(item.risk_score),
                horizon=f'next {item.horizon_minutes} minutes',
                recommended_action=item.recommended_action,
                probable_cause=item.probable_cause,
                confidence=float(item.confidence),
            )
            for item in predictions.order_by('-risk_score', '-confidence', 'service__name')[:5]
        ]
        if prediction_cards:
            return [asdict(item) for item in prediction_cards]
        return [
            asdict(
                PredictionCard(
                    service='checkout-api',
                    score=0.82,
                    horizon='next 30 minutes',
                    recommended_action='Scale worker pool and invalidate slow cache shards.',
                    probable_cause='Cache shard saturation',
                    confidence=0.74,
                )
            )
        ]

    def _build_chatops_examples(self) -> list[str]:
        service_target = self.service_slug or 'checkout-api'
        environment_target = self.environment_slug or 'production'
        return [
            f'Show me latency anomalies for {service_target} in {environment_target} during the last 60 minutes.',
            f'Summarize active incidents and probable root causes for {service_target}.',
            f'List the safest runbook and automation steps for {service_target} in {environment_target}.',
        ]

    def _build_service_overview(self, services, incidents) -> list[dict[str, Any]]:
        service_counts = {
            item['service__slug']: item['open_incidents']
            for item in incidents.exclude(status=Incident.Status.RESOLVED)
            .values('service__slug')
            .annotate(open_incidents=Count('id'))
        }

        overview = []
        for service in services[:6]:
            overview.append(
                {
                    'service': service.name,
                    'team': service.owning_team.name,
                    'tier': service.tier,
                    'lifecycle': service.lifecycle,
                    'open_incidents': service_counts.get(service.slug, 0),
                }
            )
        return overview

    def _build_runbook_section(self, section: str, runbooks, knowledge_documents) -> list[str]:
        section_runbooks = runbooks.filter(domain__in=RUNBOOK_DOMAIN_MAPPING[section]).order_by('name')[:3]
        entries = [f'{runbook.name}: {runbook.description}' for runbook in section_runbooks]

        section_documents = knowledge_documents.filter(
            document_type__in=KNOWLEDGE_TYPE_MAPPING[section],
        ).order_by('title')[:2]
        entries.extend(f'{document.title}: {document.summary}' for document in section_documents)

        return entries or FALLBACK_RUNBOOK[section]


def build_dashboard_payload(service_slug: str | None = None, environment_slug: str | None = None) -> dict[str, Any]:
    service = ControlCenterDomainService(service_slug=service_slug, environment_slug=environment_slug)
    return service.build_dashboard_payload()


def build_runbook_payload(service_slug: str | None = None, environment_slug: str | None = None) -> dict[str, Any]:
    service = ControlCenterDomainService(service_slug=service_slug, environment_slug=environment_slug)
    return service.build_runbook_payload()
