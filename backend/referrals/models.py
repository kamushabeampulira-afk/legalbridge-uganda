"""
LegalBridge — Referrals: legal aid organisations and professional directory.
Only verified organisations and professionals should appear in this directory.
"""
import uuid
from django.db import models


class LegalAidOrganisation(models.Model):
    """
    Verified legal aid organisations.
    Data is manually entered and verified by LegalBridge admins.
    DO NOT invent organisations. Only add organisations that have been verified.
    """
    SERVICE_CHOICES = [
        ('general_legal_aid', 'General Legal Aid'),
        ('women_family', 'Women and Family Law'),
        ('land_rights', 'Land Rights'),
        ('labour', 'Labour and Employment'),
        ('criminal', 'Criminal Defence'),
        ('community', 'Community Legal Education'),
        ('refugee', 'Refugee / Asylum'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    acronym = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    services = models.JSONField(default=list)
    service_type = models.CharField(max_length=30, choices=SERVICE_CHOICES, default='general_legal_aid')
    district = models.CharField(max_length=100, blank=True)
    physical_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    eligibility = models.TextField(
        blank=True,
        help_text='Who is eligible for their services (e.g. women, low income, specific districts)'
    )
    is_free = models.BooleanField(default=True)
    consultation_info = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_legal_aid_orgs'
        ordering = ['name']

    def __str__(self):
        return self.name


class LegalProfessional(models.Model):
    """
    Verified legal professionals willing to list on LegalBridge.
    Listing does NOT imply endorsement of legal outcomes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True, help_text='e.g. Advocate, Legal Officer')
    organisation = models.CharField(max_length=300, blank=True)
    specialisations = models.JSONField(default=list)
    district = models.CharField(max_length=100, blank=True)
    physical_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    consultation_fee_ugx = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Leave blank if free or not disclosed'
    )
    offers_free_consultation = models.BooleanField(default=False)
    languages_spoken = models.JSONField(default=list)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_legal_professionals'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.title} {self.full_name}".strip()
