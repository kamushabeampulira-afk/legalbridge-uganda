"""
LegalBridge — Documents models
Tracks uploaded documents and their OCR/AI processing results.
"""
import uuid
import os
from django.db import models
from django.conf import settings


def upload_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return f'documents/{instance.owner.id}/{uuid.uuid4()}.{ext}'


class Document(models.Model):
    """An uploaded document from a user."""

    DOC_TYPE_CHOICES = [
        ('traffic_notice', 'Traffic Violation Notice'),
        ('police_charge', 'Police Charge Sheet'),
        ('court_summons', 'Court Summons'),
        ('eviction_notice', 'Eviction Notice'),
        ('allocation_slip', 'Market Allocation Slip'),
        ('payment_receipt', 'Payment Receipt'),
        ('rent_record', 'Rent Payment Record'),
        ('market_notice', 'Market Management Notice'),
        ('employment_letter', 'Employment Letter'),
        ('contract', 'Contract / Agreement'),
        ('other_official', 'Other Official Document'),
        ('unknown', 'Unknown / Unclassified'),
    ]

    USER_CATEGORY_CHOICES = [
        ('boda_boda', 'Boda Boda Rider'),
        ('market_vendor', 'Market Vendor'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Analysis Completed'),
        ('failed', 'Processing Failed'),
        ('deleted', 'User Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    file = models.FileField(upload_to=upload_path)
    original_filename = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=20, blank=True)  # jpg, png, pdf
    file_size_bytes = models.PositiveIntegerField(default=0)

    doc_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES, default='unknown')
    user_category = models.CharField(max_length=20, choices=USER_CATEGORY_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # OCR results
    extracted_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    ocr_warnings = models.TextField(blank=True)

    # Key fields detected
    detected_dates = models.JSONField(default=list, blank=True)
    detected_amounts = models.JSONField(default=list, blank=True)
    detected_names = models.JSONField(default=list, blank=True)
    detected_reference_numbers = models.JSONField(default=list, blank=True)

    # Processing metadata
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)

    # Language of the submission
    language = models.CharField(max_length=5, default='en')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete flag (user deleted their own document)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lb_documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} — {self.owner} ({self.created_at.date()})"

    @property
    def file_size_kb(self):
        return round(self.file_size_bytes / 1024, 1)


class DocumentAnalysis(models.Model):
    """
    The AI-generated legal explanation for a document.
    Stored separately so it can be regenerated without re-uploading.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='analysis')

    # Explanation sections
    summary = models.TextField(blank=True, help_text="What your document says (simple language)")
    what_it_means = models.TextField(blank=True, help_text="What this may mean for you")
    relevant_law = models.TextField(blank=True, help_text="Relevant Ugandan law")
    details_to_check = models.TextField(blank=True, help_text="Important details to verify")
    next_steps = models.JSONField(default=list, help_text="Practical next steps as a list")
    missing_information = models.TextField(blank=True, help_text="Information that appears to be missing")
    where_to_get_help = models.TextField(blank=True, help_text="Where to seek assistance")

    # Sources used
    legal_sources_used = models.JSONField(default=list)

    # Audio versions
    audio_summary_en = models.FileField(upload_to='audio/', null=True, blank=True)
    audio_summary_lg = models.FileField(upload_to='audio/', null=True, blank=True)

    # Confidence and flags
    ai_confidence = models.FloatField(null=True, blank=True)
    has_verified_sources = models.BooleanField(default=False)
    uncertainty_flag = models.BooleanField(
        default=False,
        help_text="Set if no verified source was found — AI uncertainty message shown"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_document_analyses'

    def __str__(self):
        return f"Analysis for {self.document}"
