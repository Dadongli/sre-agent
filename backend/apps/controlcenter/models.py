from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(TimestampedModel):
    class TeamType(models.TextChoices):
        PLATFORM = 'platform', 'Platform'
        APPLICATION = 'application', 'Application'
        SRE = 'sre', 'SRE'
        SECURITY = 'security', 'Security'

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    team_type = models.CharField(max_length=32, choices=TeamType.choices, default=TeamType.SRE)
    contact_email = models.EmailField(blank=True)
    slack_channel = models.CharField(max_length=80, blank=True)
    escalation_policy = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Environment(TimestampedModel):
    class EnvironmentType(models.TextChoices):
        PRODUCTION = 'production', 'Production'
        STAGING = 'staging', 'Staging'
        TEST = 'test', 'Test'
        DEVELOPMENT = 'development', 'Development'

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    environment_type = models.CharField(
        max_length=32,
        choices=EnvironmentType.choices,
        default=EnvironmentType.PRODUCTION,
    )
    region = models.CharField(max_length=64, blank=True)
    is_customer_facing = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Service(TimestampedModel):
    class Tier(models.TextChoices):
        TIER_0 = 'tier0', 'Tier 0'
        TIER_1 = 'tier1', 'Tier 1'
        TIER_2 = 'tier2', 'Tier 2'
        TIER_3 = 'tier3', 'Tier 3'

    class Lifecycle(models.TextChoices):
        EXPERIMENT = 'experiment', 'Experiment'
        ACTIVE = 'active', 'Active'
        DEPRECATED = 'deprecated', 'Deprecated'

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=16, choices=Tier.choices, default=Tier.TIER_2)
    lifecycle = models.CharField(max_length=16, choices=Lifecycle.choices, default=Lifecycle.ACTIVE)
    owning_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='services')
    repository_url = models.URLField(blank=True)
    runbook_url = models.URLField(blank=True)
    environments = models.ManyToManyField(Environment, through='ServiceEnvironment', related_name='services')

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ServiceEnvironment(TimestampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_environments')
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='service_environments')
    namespace = models.CharField(max_length=120, blank=True)
    cluster = models.CharField(max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['service__name', 'environment__name']
        constraints = [
            models.UniqueConstraint(fields=['service', 'environment'], name='unique_service_environment'),
        ]

    def __str__(self) -> str:
        return f'{self.service} @ {self.environment}'


class ServiceDependency(TimestampedModel):
    class DependencyType(models.TextChoices):
        SYNCHRONOUS = 'synchronous', 'Synchronous'
        ASYNCHRONOUS = 'asynchronous', 'Asynchronous'
        DATA = 'data', 'Data'
        THIRD_PARTY = 'third_party', 'Third Party'

    class Criticality(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    upstream_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='downstream_dependencies')
    downstream_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='upstream_dependencies')
    dependency_type = models.CharField(max_length=32, choices=DependencyType.choices)
    criticality = models.CharField(max_length=16, choices=Criticality.choices, default=Criticality.MEDIUM)
    slo_impact = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['upstream_service__name', 'downstream_service__name']
        constraints = [
            models.UniqueConstraint(
                fields=['upstream_service', 'downstream_service'],
                name='unique_service_dependency',
            ),
            models.CheckConstraint(
                condition=~models.Q(upstream_service=models.F('downstream_service')),
                name='prevent_self_service_dependency',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.upstream_service} -> {self.downstream_service}'


class AlertRule(TimestampedModel):
    class Severity(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        CRITICAL = 'critical', 'Critical'

    class Source(models.TextChoices):
        PROMETHEUS = 'prometheus', 'Prometheus'
        LOKI = 'loki', 'Loki'
        TEMPO = 'tempo', 'Tempo'
        CLOUD_MONITOR = 'cloud_monitor', 'Cloud Monitor'

    name = models.CharField(max_length=160)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='alert_rules')
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='alert_rules')
    source = models.CharField(max_length=32, choices=Source.choices)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.WARNING)
    expression = models.TextField()
    threshold = models.CharField(max_length=120, blank=True)
    for_duration = models.DurationField(null=True, blank=True)
    summary_template = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['service__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['service', 'environment', 'name'], name='unique_alert_rule_scope'),
        ]

    def __str__(self) -> str:
        return f'{self.service} / {self.name}'


class Incident(TimestampedModel):
    class Severity(models.TextChoices):
        SEV0 = 'sev0', 'SEV0'
        SEV1 = 'sev1', 'SEV1'
        SEV2 = 'sev2', 'SEV2'
        SEV3 = 'sev3', 'SEV3'

    class Status(models.TextChoices):
        DETECTED = 'detected', 'Detected'
        TRIAGED = 'triaged', 'Triaged'
        MITIGATING = 'mitigating', 'Mitigating'
        MONITORING = 'monitoring', 'Monitoring'
        RESOLVED = 'resolved', 'Resolved'

    public_id = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='incidents')
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT, related_name='incidents')
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    severity = models.CharField(max_length=8, choices=Severity.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DETECTED)
    detected_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    root_cause_summary = models.TextField(blank=True)
    impact_summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self) -> str:
        return self.public_id

    @property
    def duration_minutes(self) -> int:
        end = self.resolved_at or timezone.now()
        return int((end - self.detected_at).total_seconds() // 60)


class IncidentPrediction(TimestampedModel):
    class PredictionSource(models.TextChoices):
        RULE_ENGINE = 'rule_engine', 'Rule Engine'
        STATISTICAL = 'statistical', 'Statistical'
        LLM = 'llm', 'LLM'
        HYBRID = 'hybrid', 'Hybrid'

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='incident_predictions')
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='incident_predictions')
    source = models.CharField(max_length=32, choices=PredictionSource.choices, default=PredictionSource.HYBRID)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(1)])
    confidence = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(1)])
    horizon_minutes = models.PositiveIntegerField()
    probable_cause = models.CharField(max_length=255)
    recommended_action = models.TextField()
    supporting_signals = models.JSONField(default=list, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self) -> str:
        return f'{self.service} risk={self.risk_score}'

    @property
    def is_high_risk(self) -> bool:
        return float(self.risk_score) >= 0.75


class Runbook(TimestampedModel):
    class Domain(models.TextChoices):
        OBSERVABILITY = 'observability', 'Observability'
        INCIDENT = 'incident', 'Incident'
        AUTOMATION = 'automation', 'Automation'
        KNOWLEDGE = 'knowledge', 'Knowledge'
        CHATOPS = 'chatops', 'ChatOps'
        GOVERNANCE = 'governance', 'Governance'

    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True)
    domain = models.CharField(max_length=32, choices=Domain.choices)
    description = models.TextField()
    steps = models.JSONField(default=list, blank=True)
    risk_level = models.CharField(max_length=16, choices=RiskLevel.choices, default=RiskLevel.MEDIUM)
    requires_approval = models.BooleanField(default=True)
    linked_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='runbooks')

    class Meta:
        ordering = ['domain', 'name']

    def __str__(self) -> str:
        return self.name


class AutomationExecution(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        RUNNING = 'running', 'Running'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        ROLLED_BACK = 'rolled_back', 'Rolled Back'

    class ExecutorType(models.TextChoices):
        HUMAN = 'human', 'Human'
        AGENT = 'agent', 'Agent'
        WORKFLOW = 'workflow', 'Workflow'

    runbook = models.ForeignKey(Runbook, on_delete=models.PROTECT, related_name='executions')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='automation_executions')
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT, related_name='automation_executions')
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name='automation_executions')
    executor_type = models.CharField(max_length=16, choices=ExecutorType.choices, default=ExecutorType.AGENT)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    approval_reference = models.CharField(max_length=120, blank=True)
    dry_run = models.BooleanField(default=False)
    execution_log = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.runbook} ({self.status})'

    @property
    def is_finished(self) -> bool:
        return self.status in {self.Status.SUCCEEDED, self.Status.FAILED, self.Status.ROLLED_BACK}


class KnowledgeDocument(TimestampedModel):
    class DocumentType(models.TextChoices):
        SOP = 'sop', 'SOP'
        POSTMORTEM = 'postmortem', 'Postmortem'
        ARCHITECTURE = 'architecture', 'Architecture'
        CMDB = 'cmdb', 'CMDB'
        FAQ = 'faq', 'FAQ'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    source_uri = models.URLField(blank=True)
    summary = models.TextField()
    body = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='knowledge_documents')
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name='knowledge_documents')
    freshness_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class ChatSession(TimestampedModel):
    class Persona(models.TextChoices):
        OPERATOR = 'operator', 'Operator'
        INCIDENT_COMMANDER = 'incident_commander', 'Incident Commander'
        EXECUTIVE = 'executive', 'Executive'
        AGENT = 'agent', 'Agent'

    session_id = models.CharField(max_length=64, unique=True)
    persona = models.CharField(max_length=32, choices=Persona.choices, default=Persona.OPERATOR)
    user_identifier = models.CharField(max_length=120)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions')
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions')
    context_snapshot = models.JSONField(default=dict, blank=True)
    last_message_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self) -> str:
        return self.session_id


class ChatMessage(TimestampedModel):
    class Sender(models.TextChoices):
        USER = 'user', 'User'
        AGENT = 'agent', 'Agent'
        SYSTEM = 'system', 'System'

    class MessageType(models.TextChoices):
        QUERY = 'query', 'Query'
        ANSWER = 'answer', 'Answer'
        ACTION = 'action', 'Action'
        SUMMARY = 'summary', 'Summary'

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=16, choices=Sender.choices)
    message_type = models.CharField(max_length=16, choices=MessageType.choices, default=MessageType.QUERY)
    content = models.TextField()
    citations = models.JSONField(default=list, blank=True)
    token_usage = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'{self.session.session_id} / {self.sender}'


class AgentSnapshot(TimestampedModel):
    status = models.CharField(max_length=32)
    queue_depth = models.PositiveIntegerField(default=0)
    tool_success_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(1)])
    token_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active_incidents = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    snapshot_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-snapshot_at']

    def __str__(self) -> str:
        return f'AgentSnapshot<{self.snapshot_at.isoformat()}>'


class AuditLog(TimestampedModel):
    class Result(models.TextChoices):
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        DENIED = 'denied', 'Denied'

    actor = models.CharField(max_length=120)
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=80)
    target_identifier = models.CharField(max_length=120)
    result = models.CharField(max_length=16, choices=Result.choices)
    details = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-occurred_at']

    def __str__(self) -> str:
        return f'{self.actor} {self.action} {self.target_type}'
