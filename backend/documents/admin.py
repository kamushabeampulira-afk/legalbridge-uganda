from django.contrib import admin
from .models import Document, DocumentAnalysis, DocumentVerificationRecord


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'doc_type', 'verification_status', 'user_category', 'status',
                    'ocr_confidence', 'created_at']
    list_filter = ['doc_type', 'verification_status', 'user_category', 'status', 'language']
    search_fields = ['owner__phone_number', 'original_filename']
    readonly_fields = ['extracted_text', 'ocr_confidence', 'classification', 'document_details',
                       'verification_status', 'verification_guidance', 'processing_error', 'created_at']
    ordering = ['-created_at']

    def has_change_permission(self, request, obj=None):
        # Admins should not edit document content
        return False


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'has_verified_sources', 'uncertainty_flag', 'created_at']
    list_filter = ['has_verified_sources', 'uncertainty_flag']
    readonly_fields = ['document', 'created_at', 'legal_sources_used']


@admin.register(DocumentVerificationRecord)
class DocumentVerificationRecordAdmin(admin.ModelAdmin):
    """
    Record of checking a document with its issuing institution. The only way a
    document can be marked 'verified'; the model refuses that status unless the
    method actually confirmed the document.
    """
    list_display = ['document', 'resulting_status', 'method', 'institution_contacted', 'verified_by', 'created_at']
    list_filter = ['resulting_status', 'method']
    raw_id_fields = ['document']
    readonly_fields = ['verified_by', 'created_at']
    fields = ['document', 'method', 'institution_contacted', 'notes', 'resulting_status', 'verified_by', 'created_at']

    def has_change_permission(self, request, obj=None):
        return False  # records are an audit trail: add a new record instead of editing

    def save_model(self, request, obj, form, change):
        obj.verified_by = request.user
        super().save_model(request, obj, form, change)
