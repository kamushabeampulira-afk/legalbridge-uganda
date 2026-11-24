"""
LegalBridge — Documents models
Tracks uploaded documents and their OCR/AI processing results.
"""
import uuid
import os
from django.db import models
from django.conf import settings

from .doc_types import DOC_TYPE_CHOICES

# Verification statuses. Recognising what a document *is* is separate from
# confirming it is *genuine*: only 'verified_official' says the latter, and it
# is only ever set through a DocumentVerificationRecord made by an administrator
# who records the authorised method used. Automatic analysis never sets it.
VERIFICATION_STATUS_CHOICES = [
    ('type_identified', 'Document type identified'),
    ('official_looking_unverified', 'Official-looking document, authenticity not independently verified'),
    ('requires_confirmation', 'Details require confirmation with the issuing institution'),
    ('verified_official', 'Verification confirmed through an authorised official source or process'),
    ('verification_incomplete', 'Verification could not be completed'),
]


def upload_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return f'documents/{instance.owner.id}/{uuid.uuid4()}.{ext}'


class Document(models.Model):
    """An uploaded document from a user."""

    DOC_TYPE_CHOICES = DOC_TYPE_CHOICES
    VERIFICATION_STATUS_CHOICES = VERIFICATION_STATUS_CHOICES

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

    # Classification evidence: confidence, matched signals, issuer, who produced it
    classification = models.JSONField(default=dict, blank=True)
    # Structured details read from the document text; each field carries a status
    # ('found' | 'unclear' | 'not_found') so nothing is presented as certain when it isn't.
    document_details = models.JSONField(default=dict, blank=True)

    # Authenticity: see VERIFICATION_STATUS_CHOICES
    verification_status = models.CharField(
        max_length=30, choices=VERIFICATION_STATUS_CHOICES, default='verification_incomplete',
    )
    verification_guidance = models.TextField(blank=True)

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


class DocumentVerificationRecord(models.Model):
    """
    An administrator's record of checking a document's authenticity with the
    issuing institution (or another authorised process). This is the only way
    a document's verification_status can become 'verified_official'.
    """
    METHOD_CHOICES = [
        ('issuing_institution_confirmed', 'Confirmed directly with the issuing institution'),
        ('official_system_lookup', 'Confirmed through an official verification system'),
        ('in_person_confirmation', 'Confirmed in person at the issuing office'),
        ('could_not_confirm', 'Attempted, but could not be confirmed'),
        ('institution_denied', 'Issuing institution said it did not issue this document'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='verification_records')
    resulting_status = models.CharField(max_length=30, choices=VERIFICATION_STATUS_CHOICES)
    method = models.CharField(max_length=40, choices=METHOD_CHOICES)
    institution_contacted = models.CharField(
        max_length=300,
        help_text='Institution/office contacted, using contact details obtained independently '
                  'of the document itself.',
    )
    notes = models.TextField(help_text='What was checked and what the institution confirmed.')
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='document_verifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_document_verifications'
        ordering = ['-created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        confirming_methods = {'issuing_institution_confirmed', 'official_system_lookup', 'in_person_confirmation'}
        if self.resulting_status == 'verified_official' and self.method not in confirming_methods:
            raise ValidationError(
                'A document can only be marked verified when the method actually confirmed it.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        Document.objects.filter(pk=self.document_id).update(verification_status=self.resulting_status)
