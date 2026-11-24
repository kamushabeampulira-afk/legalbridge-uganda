"""
LegalBridge — Analytics models.
Stores ANONYMISED, AGGREGATE statistics only.
No identifiable user data or document content is stored here.
"""
import uuid
from django.db import models


class DailyUsageStat(models.Model):
    """Aggregate daily counts — no personal data."""
    date = models.DateField(unique=True)
    new_registrations = models.PositiveIntegerField(default=0)
    documents_uploaded = models.PositiveIntegerField(default=0)
    documents_analyzed = models.PositiveIntegerField(default=0)
    legal_questions_asked = models.PositiveIntegerField(default=0)
    ussd_sessions = models.PositiveIntegerField(default=0)
    voice_transcriptions = models.PositiveIntegerField(default=0)
    boda_boda_sessions = models.PositiveIntegerField(default=0)
    market_vendor_sessions = models.PositiveIntegerField(default=0)
    uncertainty_flags_raised = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_daily_usage_stats'
        ordering = ['-date']

    def __str__(self):
        return f'Stats: {self.date}'


class DocumentTypeStat(models.Model):
    """Aggregate counts of document types processed — no personal data."""
    week_start = models.DateField()
    doc_type = models.CharField(max_length=30)
    count = models.PositiveIntegerField(default=0)
    uncertainty_flag_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'lb_doc_type_stats'
        unique_together = ('week_start', 'doc_type')
        ordering = ['-week_start']
