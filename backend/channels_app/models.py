"""USSD session logging model."""
import uuid
from django.db import models


class USSDSession(models.Model):
    """Logs every USSD session for monitoring and analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, db_index=True)
    phone_number = models.CharField(max_length=20)
    service_code = models.CharField(max_length=20, blank=True)
    input_text = models.TextField(blank=True)
    response_text = models.TextField(blank=True)
    language = models.CharField(max_length=5, default='en')
    menus_visited = models.JSONField(default=list)
    ended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_ussd_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f'USSD {self.session_id} ({self.phone_number})'
