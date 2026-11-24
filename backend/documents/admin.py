from django.contrib import admin
from .models import Document, DocumentAnalysis


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'doc_type', 'user_category', 'status', 'ocr_confidence', 'created_at']
    list_filter = ['doc_type', 'user_category', 'status', 'language']
    search_fields = ['owner__phone_number', 'original_filename']
    readonly_fields = ['extracted_text', 'ocr_confidence', 'processing_error', 'created_at']
    ordering = ['-created_at']

    def has_change_permission(self, request, obj=None):
        # Admins should not edit document content
        return False


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'has_verified_sources', 'uncertainty_flag', 'created_at']
    list_filter = ['has_verified_sources', 'uncertainty_flag']
    readonly_fields = ['document', 'created_at', 'legal_sources_used']
