from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    AlertRule,
    AutomationExecution,
    ChatMessage,
    ChatSession,
    Environment,
    Incident,
    IncidentPrediction,
    Runbook,
    Service,
    ServiceDependency,
    ServiceEnvironment,
    Team,
)


class DashboardApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_dashboard_summary_shape(self) -> None:
        response = self.client.get('/api/dashboard/summary/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['cards']), 4)
        self.assertGreaterEqual(len(payload['timeline']), 5)
        self.assertIn('chatops_examples', payload)

    def test_runbook_sections(self) -> None:
        response = self.client.get('/api/agent/runbook/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('observability', payload)
        self.assertIn('chatops', payload)


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
