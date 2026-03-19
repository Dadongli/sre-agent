from django.contrib import admin
from django.urls import path

from apps.controlcenter.views import dashboard_summary, agent_runbook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    path('api/agent/runbook/', agent_runbook, name='agent-runbook'),
]
