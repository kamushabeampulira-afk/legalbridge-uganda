"""
Admin: AI service status dashboard and AI request log.
The dashboard replaces the AIHealthCheck change list. Running tests is restricted
to superusers (or staff granted ai_engine.add_aihealthcheck). No API keys,
prompts or document content are ever displayed.
"""
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from . import diagnostics
from .models import AIHealthCheck, AIRequestLog
from .openai_service import run_connection_check


def _can_run(request):
    return request.user.is_active and request.user.is_staff and (
        request.user.is_superuser or request.user.has_perm('ai_engine.add_aihealthcheck'))


@admin.register(AIHealthCheck)
class AIServiceStatusAdmin(admin.ModelAdmin):
    list_display = ['kind', 'component_status', 'ai_status', 'latency_ms', 'created_at']
    readonly_fields = ['kind', 'component_status', 'ai_status', 'model_name', 'latency_ms', 'summary',
                       'details', 'triggered_by', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path('run/', self.admin_site.admin_view(self.run_checks_view), name='%s_%s_run' % info),
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        context = {
            **self.admin_site.each_context(request),
            'title': 'AI service status',
            'opts': self.model._meta,
            'overview': diagnostics.service_overview(),
            'history': AIHealthCheck.objects.select_related('triggered_by')[:25],
            'can_run': _can_run(request),
        }
        return TemplateResponse(request, 'admin/ai_engine/ai_status.html', context)

    def run_checks_view(self, request):
        if request.method != 'POST':
            return redirect('admin:ai_engine_aihealthcheck_changelist')
        if not _can_run(request):
            raise PermissionDenied
        action = request.POST.get('action')
        if action == 'connection':
            result = run_connection_check(request.user)
            level = messages.SUCCESS if result.component_status == 'pass' else (
                messages.WARNING if result.component_status == 'warn' else messages.ERROR)
            self.message_user(request, f'OpenAI connection: {result.get_ai_status_display()}. {result.summary}', level)
        elif action == 'components':
            results = diagnostics.run_all(request.user, include_connection=True, include_explanation=False)
            failed = [r.get_kind_display() for r in results if r.component_status == 'fail']
            self.message_user(request, 'Component checks finished. ' + (
                f"Failing: {', '.join(failed)}." if failed else 'No component failed.'),
                messages.ERROR if failed else messages.SUCCESS)
        elif action == 'end_to_end':
            result = diagnostics.check_explanation(request.user)
            level = messages.SUCCESS if result.component_status == 'pass' else (
                messages.WARNING if result.component_status == 'warn' else messages.ERROR)
            self.message_user(request, f'End-to-end explanation test: {result.summary}', level)
        else:
            self.message_user(request, 'Unknown action.', messages.ERROR)
        return redirect('admin:ai_engine_aihealthcheck_changelist')


@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'purpose', 'success', 'error_category', 'latency_ms', 'model_name']
    list_filter = ['success', 'error_category', 'purpose']
    readonly_fields = ['purpose', 'model_name', 'success', 'error_category', 'latency_ms', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
