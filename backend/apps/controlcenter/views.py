from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services import build_dashboard_payload, build_runbook_payload


@require_GET
def dashboard_summary(request):
    return JsonResponse(build_dashboard_payload())


@require_GET
def agent_runbook(request):
    return JsonResponse(build_runbook_payload())
