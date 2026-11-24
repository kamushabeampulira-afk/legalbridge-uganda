"""
AI engine models: service health checks and a content-free log of AI requests.
Neither model stores API keys, prompts, document text or responses.
"""
import uuid
from django.conf import settings
from django.db import models

AI_STATUS_CHOICES = [
    ('operational', 'Connected and operational'),
    ('missing_key', 'API key missing'),
    ('auth_failed', 'Authentication failed'),
    ('model_unavailable', 'Model unavailable or inaccessible'),
    ('rate_limited', 'Rate limited'),
    ('quota_billing', 'Quota or billing problem'),
    ('network_error', 'Network connection failed'),
    ('timeout', 'Request timed out'),
    ('invalid_response', 'Invalid or empty response'),
    ('unknown_error', 'Unknown error'),
]

COMPONENT_STATUS_CHOICES = [
    ('pass', 'Pass'),
    ('warn', 'Working with warnings'),
    ('fail', 'Fail'),
    ('skipped', 'Not run'),
]


class AIHealthCheck(models.Model):
    """One run of a diagnostic: the OpenAI connection test or a pipeline component test."""
    KIND_CHOICES = [
        ('openai_connection', 'A. OpenAI API connection'),
        ('ocr', 'B. OCR text extraction'),
        ('legal_retrieval', 'C. Legal knowledge retrieval'),
        ('classification', 'D. Document classification'),
        ('explanation', 'E. Legal explanation generation (end to end)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    component_status = models.CharField(max_length=10, choices=COMPONENT_STATUS_CHOICES)
    # For the OpenAI connection (and the explanation test): the precise AI status
    ai_status = models.CharField(max_length=30, choices=AI_STATUS_CHOICES, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=500, blank=True)
    # Individual check results, e.g. {"key_present": true, "key_accepted": true, ...}
    details = models.JSONField(default=dict, blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_health_checks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_ai_health_checks'
        ordering = ['-created_at']
        verbose_name = 'AI service status'
        verbose_name_plural = 'AI service status'

    def __str__(self):
        return f'{self.get_kind_display()}: {self.get_component_status_display()} ({self.created_at:%Y-%m-%d %H:%M})'


class AIRequestLog(models.Model):
    """Outcome of a real AI request made while serving users. No content is stored."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purpose = models.CharField(max_length=50)  # e.g. document_explanation, legal_question
    model_name = models.CharField(max_length=100, blank=True)
    success = models.BooleanField()
    error_category = models.CharField(max_length=30, choices=AI_STATUS_CHOICES, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_ai_request_logs'
        ordering = ['-created_at']
        verbose_name = 'AI request log entry'
        verbose_name_plural = 'AI request log'

    def __str__(self):
        outcome = 'ok' if self.success else self.error_category
        return f'{self.purpose} {outcome} ({self.created_at:%Y-%m-%d %H:%M})'
