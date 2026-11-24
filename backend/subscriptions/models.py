"""
LegalBridge — Subscriptions and sponsored access.
No live payment processing in MVP. Plans are configurable by admin.
"""
import uuid
from django.db import models
from django.conf import settings
from users.models import Organisation


class SubscriptionPlan(models.Model):
    """Admin-configurable plans. Prices in UGX."""
    PLAN_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('organisation_small', 'Organisation (up to 50 members)'),
        ('organisation_medium', 'Organisation (up to 200 members)'),
        ('organisation_large', 'Organisation (200+ members)'),
        ('sponsored', 'Sponsored Access'),
        ('ngo_partner', 'NGO Partner'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    plan_type = models.CharField(max_length=30, choices=PLAN_TYPE_CHOICES)
    description = models.TextField(blank=True)
    price_ugx_monthly = models.PositiveIntegerField(default=0)
    price_ugx_annual = models.PositiveIntegerField(default=0)
    max_members = models.PositiveIntegerField(null=True, blank=True)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_subscription_plans'

    def __str__(self):
        return f"{self.name} — UGX {self.price_ugx_monthly:,}/mo"


class OrganisationSubscription(models.Model):
    """An organisation's active subscription."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_beneficiaries = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_org_subscriptions'

    def __str__(self):
        return f"{self.organisation} — {self.plan} ({self.status})"


class SponsoredAccess(models.Model):
    """
    An organisation sponsors access for a community of users.
    Tracks beneficiary count without exposing personal data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sponsor_organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name='sponsored_access'
    )
    description = models.CharField(
        max_length=300,
        help_text='e.g. "Boda boda riders in Kampala Central"'
    )
    target_user_category = models.CharField(max_length=30, blank=True)
    max_beneficiaries = models.PositiveIntegerField()
    current_beneficiary_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_sponsored_access'

    def __str__(self):
        return f"Sponsored by {self.sponsor_organisation} — {self.description}"

    @property
    def has_capacity(self):
        return self.current_beneficiary_count < self.max_beneficiaries
