from django.contrib import admin

from .models import (
    AgentSnapshot,
    AlertRule,
    AuditLog,
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


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_type', 'contact_email', 'slack_channel')
    search_fields = ('name', 'slug', 'contact_email')


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'environment_type', 'region', 'is_customer_facing')
    search_fields = ('name', 'slug', 'region')


class ServiceEnvironmentInline(admin.TabularInline):
    model = ServiceEnvironment
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'lifecycle', 'owning_team')
    search_fields = ('name', 'slug')
    list_filter = ('tier', 'lifecycle', 'owning_team')
    inlines = [ServiceEnvironmentInline]


@admin.register(ServiceDependency)
class ServiceDependencyAdmin(admin.ModelAdmin):
    list_display = ('upstream_service', 'downstream_service', 'dependency_type', 'criticality')
    list_filter = ('dependency_type', 'criticality')


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'environment', 'source', 'severity', 'enabled')
    list_filter = ('source', 'severity', 'enabled')
    search_fields = ('name', 'service__name', 'environment__name')


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'service', 'environment', 'severity', 'status', 'detected_at')
    list_filter = ('severity', 'status', 'environment')
    search_fields = ('public_id', 'title', 'service__name')


@admin.register(IncidentPrediction)
class IncidentPredictionAdmin(admin.ModelAdmin):
    list_display = ('service', 'environment', 'risk_score', 'confidence', 'generated_at')
    list_filter = ('source', 'environment')


@admin.register(Runbook)
class RunbookAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'risk_level', 'requires_approval', 'linked_service')
    list_filter = ('domain', 'risk_level', 'requires_approval')
    search_fields = ('name', 'slug')


@admin.register(AutomationExecution)
class AutomationExecutionAdmin(admin.ModelAdmin):
    list_display = ('runbook', 'service', 'environment', 'status', 'executor_type', 'created_at')
    list_filter = ('status', 'executor_type', 'environment', 'dry_run')


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'service', 'freshness_at')
    list_filter = ('document_type',)
    search_fields = ('title', 'slug')


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'persona', 'user_identifier', 'service', 'last_message_at')
    list_filter = ('persona',)
    search_fields = ('session_id', 'user_identifier')
    inlines = [ChatMessageInline]


@admin.register(AgentSnapshot)
class AgentSnapshotAdmin(admin.ModelAdmin):
    list_display = ('status', 'queue_depth', 'tool_success_rate', 'active_incidents', 'snapshot_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'target_type', 'result', 'occurred_at')
    list_filter = ('result', 'target_type')
    search_fields = ('actor', 'action', 'target_identifier')
