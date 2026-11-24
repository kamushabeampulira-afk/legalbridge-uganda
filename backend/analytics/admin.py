from django.contrib import admin
from .models import DailyUsageStat, DocumentTypeStat


@admin.register(DailyUsageStat)
class DailyUsageStatAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'new_registrations', 'documents_uploaded',
        'documents_analyzed', 'legal_questions_asked',
        'ussd_sessions', 'uncertainty_flags_raised',
    ]
    ordering = ['-date']
    readonly_fields = [
        'date', 'new_registrations', 'documents_uploaded',
        'documents_analyzed', 'legal_questions_asked',
        'ussd_sessions', 'voice_transcriptions',
        'boda_boda_sessions', 'market_vendor_sessions',
        'uncertainty_flags_raised', 'created_at', 'updated_at',
    ]


@admin.register(DocumentTypeStat)
class DocumentTypeStatAdmin(admin.ModelAdmin):
    list_display = ['week_start', 'doc_type', 'count', 'uncertainty_flag_count']
    ordering = ['-week_start']
