from django.contrib import admin, messages
from django.utils import timezone
from .models import LegalSource, LegalProvision, LegalQuery
from .vector_store import index_legal_source, remove_source_from_index


@admin.register(LegalSource)
class LegalSourceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'instrument_number', 'subject', 'status', 'legal_status', 'is_sample',
        'is_indexed', 'last_verified_at',
    ]
    list_filter = ['category', 'subject', 'status', 'legal_status', 'is_sample', 'is_indexed']
    search_fields = ['title', 'short_title', 'instrument_number', 'issuing_authority']
    readonly_fields = ['is_indexed', 'indexed_at', 'chroma_doc_ids', 'created_at', 'updated_at']
    actions = ['approve_and_index', 'reindex', 'remove_from_index']

    @admin.action(description='Approve and index selected sources')
    def approve_and_index(self, request, queryset):
        not_confirmed = []
        for source in queryset:
            source.status = 'approved'
            source.reviewed_by = request.user
            source.last_verified_at = timezone.now()
            source.save()
            remove_source_from_index(str(source.id))
            ids = index_legal_source(source)
            if ids:
                source.is_indexed = True
                source.indexed_at = timezone.now()
                source.chroma_doc_ids = ids
                source.save()
            if not source.currency_assessment()[0]:
                not_confirmed.append(source.short_title or source.title)
        self.message_user(request, f'{queryset.count()} source(s) approved and indexed.')
        if not_confirmed:
            self.message_user(
                request,
                'Not presented as current law until marked "In force" and not sample text: '
                + ', '.join(not_confirmed),
                level=messages.WARNING,
            )

    @admin.action(description='Re-index selected sources')
    def reindex(self, request, queryset):
        for source in queryset:
            remove_source_from_index(str(source.id))
            ids = index_legal_source(source)
            source.is_indexed = bool(ids)
            source.indexed_at = timezone.now() if ids else None
            source.chroma_doc_ids = ids
            source.save()
        self.message_user(request, f'{queryset.count()} source(s) re-indexed.')

    @admin.action(description='Remove selected sources from index')
    def remove_from_index(self, request, queryset):
        for source in queryset:
            remove_source_from_index(str(source.id))
            source.is_indexed = False
            source.chroma_doc_ids = []
            source.save()
        self.message_user(request, f'{queryset.count()} source(s) removed from index.')


@admin.register(LegalProvision)
class LegalProvisionAdmin(admin.ModelAdmin):
    list_display = ['source', 'section_number', 'section_title']
    list_filter = ['source__subject']
    search_fields = ['section_number', 'section_title', 'text']


@admin.register(LegalQuery)
class LegalQueryAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_category', 'language', 'has_verified_sources', 'uncertainty_flag', 'created_at']
    list_filter = ['user_category', 'language', 'has_verified_sources', 'uncertainty_flag']
    readonly_fields = ['user', 'question_text', 'response_text', 'sources_retrieved', 'created_at']
    # Protect user questions from casual admin browsing
    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).none()
