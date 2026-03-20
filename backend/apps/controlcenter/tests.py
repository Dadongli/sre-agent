from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    AgentSnapshot,
    AlertRule,
    AutomationExecution,
    ChatMessage,
    ChatSession,
    Environment,
    Incident,
    IncidentPrediction,
    KnowledgeDocument,
    Runbook,
    Service,
    ServiceDependency,
    ServiceEnvironment,
    Team,
)


class DashboardApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.team = Team.objects.create(
            name='SRE Platform',
            slug='sre-platform',
            team_type=Team.TeamType.SRE,
            contact_email='sre@example.com',
        )
        self.prod = Environment.objects.create(
            name='Production',
            slug='production',
            environment_type=Environment.EnvironmentType.PRODUCTION,
            region='us-east-1',
        )
        self.staging = Environment.objects.create(
            name='Staging',
            slug='staging',
            environment_type=Environment.EnvironmentType.STAGING,
            region='us-east-1',
            is_customer_facing=False,
        )
        self.checkout = Service.objects.create(
            name='checkout-api',
            slug='checkout-api',
            tier=Service.Tier.TIER_0,
            owning_team=self.team,
        )
        self.search = Service.objects.create(
            name='search-api',
            slug='search-api',
            tier=Service.Tier.TIER_1,
            owning_team=self.team,
        )
        ServiceEnvironment.objects.create(
            service=self.checkout,
            environment=self.prod,
            namespace='checkout',
            cluster='prod-main',
            is_primary=True,
        )
        ServiceEnvironment.objects.create(
            service=self.search,
            environment=self.staging,
            namespace='search',
            cluster='staging-main',
            is_primary=True,
        )

        detected_at = timezone.now() - timedelta(minutes=45)
        Incident.objects.create(
            public_id='INC-1001',
            title='Checkout latency spike',
            summary='Latency increased after deploy.',
            service=self.checkout,
            environment=self.prod,
            severity=Incident.Severity.SEV1,
            status=Incident.Status.MITIGATING,
            detected_at=detected_at,
        )
        Incident.objects.create(
            public_id='INC-1002',
            title='Search cache cold start',
            summary='Recovered after warmup.',
            service=self.search,
            environment=self.staging,
            severity=Incident.Severity.SEV3,
            status=Incident.Status.RESOLVED,
            detected_at=detected_at - timedelta(minutes=20),
            resolved_at=detected_at - timedelta(minutes=5),
        )
        IncidentPrediction.objects.create(
            service=self.checkout,
            environment=self.prod,
            risk_score=Decimal('0.91'),
            confidence=Decimal('0.83'),
            horizon_minutes=30,
            probable_cause='Cache shard saturation',
            recommended_action='Scale worker pool',
            supporting_signals=['latency', 'cache-hit-rate'],
        )
        Runbook.objects.create(
            name='Investigate checkout latency',
            slug='investigate-checkout-latency',
            domain=Runbook.Domain.OBSERVABILITY,
            description='Inspect p95 latency, traces, and deploy diff.',
            steps=['Check dashboards', 'Compare traces'],
            linked_service=self.checkout,
            requires_approval=False,
        )
        Runbook.objects.create(
            name='Execute guarded rollback',
            slug='execute-guarded-rollback',
            domain=Runbook.Domain.AUTOMATION,
            description='Roll back the latest release with approval guardrails.',
            steps=['Validate blast radius', 'Rollback deployment'],
            linked_service=self.checkout,
        )
        KnowledgeDocument.objects.create(
            title='Checkout architecture',
            slug='checkout-architecture',
            document_type=KnowledgeDocument.DocumentType.ARCHITECTURE,
            summary='Service topology and dependency critical path.',
            service=self.checkout,
        )
        KnowledgeDocument.objects.create(
            title='Operator FAQ',
            slug='operator-faq',
            document_type=KnowledgeDocument.DocumentType.FAQ,
            summary='Common operator prompts and escalation paths.',
        )
        runbook = Runbook.objects.get(slug='execute-guarded-rollback')
        AutomationExecution.objects.create(
            runbook=runbook,
            service=self.checkout,
            environment=self.prod,
            status=AutomationExecution.Status.SUCCEEDED,
            created_at=timezone.now() - timedelta(days=1),
        )
        AgentSnapshot.objects.create(
            status='healthy',
            queue_depth=3,
            tool_success_rate=Decimal('0.98'),
            token_cost=Decimal('12.50'),
            active_incidents=1,
            snapshot_at=timezone.now() - timedelta(minutes=10),
        )
        AgentSnapshot.objects.create(
            status='healthy',
            queue_depth=2,
            tool_success_rate=Decimal('0.99'),
            token_cost=Decimal('11.25'),
            active_incidents=1,
            snapshot_at=timezone.now(),
        )

    def test_dashboard_summary_shape(self) -> None:
        response = self.client.get('/api/dashboard/summary/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['cards']), 4)
        self.assertGreaterEqual(len(payload['timeline']), 2)
        self.assertIn('chatops_examples', payload)
        self.assertIn('scope', payload)
        self.assertIn('service_overview', payload)

    def test_dashboard_summary_supports_service_and_environment_filters(self) -> None:
        response = self.client.get('/api/dashboard/summary/?service=checkout-api&environment=production')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['scope']['service'], 'checkout-api')
        self.assertEqual(payload['scope']['environment'], 'production')
        self.assertEqual(payload['scope']['service_count'], 1)
        self.assertEqual(payload['cards'][1]['value'], '1')
        self.assertEqual(payload['predictions'][0]['service'], 'checkout-api')
        self.assertEqual(payload['service_overview'][0]['open_incidents'], 1)

    def test_runbook_sections(self) -> None:
        response = self.client.get('/api/agent/runbook/?service=checkout-api')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('observability', payload)
        self.assertIn('chatops', payload)
        self.assertTrue(any('Investigate checkout latency' in item for item in payload['observability']))
        self.assertTrue(any('Operator FAQ' in item for item in payload['chatops']))


class ControlCenterModelTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(
            name='SRE Platform',
            slug='sre-platform',
            team_type=Team.TeamType.SRE,
            contact_email='sre@example.com',
            slack_channel='#sre-platform',
        )
        self.prod = Environment.objects.create(
            name='Production',
            slug='production',
            environment_type=Environment.EnvironmentType.PRODUCTION,
            region='us-east-1',
        )
        self.staging = Environment.objects.create(
            name='Staging',
            slug='staging',
            environment_type=Environment.EnvironmentType.STAGING,
            region='us-east-1',
            is_customer_facing=False,
        )
        self.checkout = Service.objects.create(
            name='checkout-api',
            slug='checkout-api',
            tier=Service.Tier.TIER_0,
            owning_team=self.team,
        )
        self.payment = Service.objects.create(
            name='payment-worker',
            slug='payment-worker',
            tier=Service.Tier.TIER_1,
            owning_team=self.team,
        )
        ServiceEnvironment.objects.create(
            service=self.checkout,
            environment=self.prod,
            namespace='checkout',
            cluster='prod-main',
            is_primary=True,
        )

    def test_service_environment_unique_constraint(self) -> None:
        with self.assertRaises(IntegrityError):
            ServiceEnvironment.objects.create(
                service=self.checkout,
                environment=self.prod,
            )

    def test_service_dependency_prevents_self_reference(self) -> None:
        with self.assertRaises(IntegrityError):
            ServiceDependency.objects.create(
                upstream_service=self.checkout,
                downstream_service=self.checkout,
                dependency_type=ServiceDependency.DependencyType.SYNCHRONOUS,
            )

    def test_incident_duration_minutes_uses_resolved_time(self) -> None:
        detected_at = timezone.now() - timedelta(minutes=35)
        resolved_at = detected_at + timedelta(minutes=20)
        incident = Incident.objects.create(
            public_id='INC-1001',
            title='Checkout latency spike',
            summary='Latency increased after deploy.',
            service=self.checkout,
            environment=self.prod,
            severity=Incident.Severity.SEV1,
            status=Incident.Status.RESOLVED,
            detected_at=detected_at,
            resolved_at=resolved_at,
        )

        self.assertEqual(incident.duration_minutes, 20)

    def test_prediction_high_risk_flag(self) -> None:
        prediction = IncidentPrediction.objects.create(
            service=self.checkout,
            environment=self.prod,
            risk_score=Decimal('0.82'),
            confidence=Decimal('0.74'),
            horizon_minutes=30,
            probable_cause='Cache shard saturation',
            recommended_action='Scale worker pool',
            supporting_signals=['latency', 'cache-hit-rate'],
        )

        self.assertTrue(prediction.is_high_risk)

    def test_runbook_execution_completion_flag(self) -> None:
        runbook = Runbook.objects.create(
            name='Mitigate checkout saturation',
            slug='mitigate-checkout-saturation',
            domain=Runbook.Domain.AUTOMATION,
            description='Scale worker pool and clear cache.',
            steps=['Scale deployment', 'Invalidate cache'],
            linked_service=self.checkout,
        )
        execution = AutomationExecution.objects.create(
            runbook=runbook,
            service=self.checkout,
            environment=self.prod,
            status=AutomationExecution.Status.SUCCEEDED,
        )

        self.assertTrue(execution.is_finished)

    def test_chat_session_orders_messages_by_creation(self) -> None:
        session = ChatSession.objects.create(
            session_id='chat-001',
            persona=ChatSession.Persona.OPERATOR,
            user_identifier='alice@example.com',
            service=self.checkout,
        )
        first = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.Sender.USER,
            message_type=ChatMessage.MessageType.QUERY,
            content='Show latency anomalies',
        )
        second = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.Sender.AGENT,
            message_type=ChatMessage.MessageType.ANSWER,
            content='Latency increased 22% in production.',
            citations=['runbook://checkout'],
        )

        self.assertEqual(list(session.messages.all()), [first, second])

    def test_alert_rule_scope_unique_per_service_environment(self) -> None:
        AlertRule.objects.create(
            name='High latency p95',
            service=self.checkout,
            environment=self.prod,
            source=AlertRule.Source.PROMETHEUS,
            severity=AlertRule.Severity.CRITICAL,
            expression='histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.8',
            summary_template='Checkout p95 latency breached',
        )

        with self.assertRaises(IntegrityError):
            AlertRule.objects.create(
                name='High latency p95',
                service=self.checkout,
                environment=self.prod,
                source=AlertRule.Source.PROMETHEUS,
                severity=AlertRule.Severity.CRITICAL,
                expression='up == 0',
                summary_template='Duplicate should fail',
            )
