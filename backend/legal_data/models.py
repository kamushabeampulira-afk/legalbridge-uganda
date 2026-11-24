"""
LegalBridge — Legal Data models.
Stores verified Ugandan legal sources used by the RAG pipeline.
Only approved documents are used in production responses.
"""
import uuid
from django.db import models
from django.conf import settings


class LegalSource(models.Model):
    """A verified Ugandan legal document, Act, regulation or instrument."""

    CATEGORY_CHOICES = [
        ('act', 'Act of Parliament'),
        ('regulation', 'Regulation / Statutory Instrument'),
        ('bylaw', 'By-Law / Local Government Instrument'),
        ('policy', 'Government Policy / Circular'),
        ('court_ruling', 'Court Ruling / Judgment'),
        ('guidance', 'Official Guidance Document'),
        ('other', 'Other'),
    ]

    SUBJECT_CHOICES = [
        ('traffic', 'Traffic and Road Safety'),
        ('police', 'Police Powers and Procedure'),
        ('criminal_procedure', 'Criminal Procedure and Courts'),
        ('markets', 'Markets and Trade'),
        ('employment', 'Employment and Labour'),
        ('land', 'Land and Property'),
        ('local_gov', 'Local Government'),
        ('consumer', 'Consumer Protection'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved for Production'),
        ('superseded', 'Superseded / Outdated'),
        ('rejected', 'Rejected'),
    ]

    LEGAL_STATUS_CHOICES = [
        ('in_force', 'In force'),
        ('amended', 'In force, as amended'),
        ('partially_repealed', 'Partially repealed'),
        ('repealed', 'Repealed'),
        ('unknown', 'Not yet confirmed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    short_title = models.CharField(max_length=200, blank=True)
    instrument_number = models.CharField(
        max_length=200, blank=True,
        help_text='Act, chapter, regulation or statutory instrument number exactly as published, '
                  'e.g. "Act No. 15 of 1998" or "S.I. No. 12 of 2004".',
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES, default='general')
    issuing_authority = models.CharField(max_length=300, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(
        null=True, blank=True, verbose_name='Commencement / effective date',
    )
    source_url = models.URLField(max_length=1000, blank=True)
    version_or_amendment = models.CharField(
        max_length=200, blank=True, verbose_name='Version / amendment notes',
    )
    legal_status = models.CharField(
        max_length=20, choices=LEGAL_STATUS_CHOICES, default='unknown',
        help_text='Whether the provision is currently in force. Only "In force" or '
                  '"In force, as amended" sources are presented as current law.',
    )
    is_sample = models.BooleanField(
        default=False,
        help_text='Placeholder/demo text. Never presented to users as verified law.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review')

    # The actual text content
    full_text = models.TextField(blank=True)
    summary = models.TextField(blank=True, help_text='Plain-language summary for quick reference')

    # RAG indexing
    is_indexed = models.BooleanField(default=False, help_text='Has this source been indexed in ChromaDB?')
    indexed_at = models.DateTimeField(null=True, blank=True)
    chroma_doc_ids = models.JSONField(default=list, blank=True)

    # Verification tracking
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_sources',
    )
    last_verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_legal_sources'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_production_ready(self):
        return self.status == 'approved' and self.is_indexed

    def currency_assessment(self, max_age_days=None):
        """
        Decide whether this source may be presented to users as current law.
        Returns (is_current_verified: bool, warnings: list[str]).
        A source counts as current verified law only if it is approved, not sample text,
        confirmed in force, and was verified within LEGAL_SOURCE_MAX_AGE_DAYS.
        """
        from django.utils import timezone
        if max_age_days is None:
            max_age_days = getattr(settings, 'LEGAL_SOURCE_MAX_AGE_DAYS', 365)

        warnings = []
        if self.is_sample:
            warnings.append('Sample placeholder text, not verified law.')
        if self.status != 'approved':
            warnings.append(f'Not approved for use (status: {self.get_status_display()}).')
        if self.legal_status == 'repealed':
            warnings.append('Recorded as repealed.')
        elif self.legal_status == 'partially_repealed':
            warnings.append('Partially repealed. Check the specific provision is still in force.')
        elif self.legal_status == 'unknown':
            warnings.append('Whether this law is currently in force has not been confirmed.')
        if not self.last_verified_at:
            warnings.append('Has never been verified against an official source.')
        elif (timezone.now() - self.last_verified_at).days > max_age_days:
            warnings.append(
                f'Last verified {self.last_verified_at.date().isoformat()}; '
                f'needs re-checking against the official source.'
            )
        is_current = (
            not self.is_sample
            and self.status == 'approved'
            and self.legal_status in ('in_force', 'amended')
            and bool(self.last_verified_at)
            and (timezone.now() - self.last_verified_at).days <= max_age_days
        )
        return is_current, warnings


class LegalProvision(models.Model):
    """
    A specific provision or section within a LegalSource.
    Allows granular retrieval and citation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(LegalSource, on_delete=models.CASCADE, related_name='provisions')
    section_number = models.CharField(max_length=50, blank=True)
    section_title = models.CharField(max_length=500, blank=True)
    text = models.TextField()
    plain_language_summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True, help_text='Keywords for retrieval')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_legal_provisions'
        ordering = ['source', 'section_number']

    def __str__(self):
        return f"{self.source.short_title or self.source.title} — s.{self.section_number}"


class LegalQuery(models.Model):
    """
    Records user legal questions (anonymised for improvement tracking).
    Does not store the response — that is on DocumentAnalysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='legal_queries',
    )
    question_text = models.TextField()
    user_category = models.CharField(max_length=30, blank=True)
    language = models.CharField(max_length=5, default='en')
    sources_retrieved = models.JSONField(default=list)
    response_text = models.TextField(blank=True)
    has_verified_sources = models.BooleanField(default=False)
    uncertainty_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_legal_queries'
        ordering = ['-created_at']
