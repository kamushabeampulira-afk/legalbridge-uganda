"""
LegalBridge — Users models
Custom user model supporting phone number auth (common for Uganda).
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from config.languages import LANGUAGE_CHOICES as LANGUAGE_CHOICES_FROM_REGISTRY

from .phone import normalize_phone


class UserManager(BaseUserManager):
    def get_by_natural_key(self, phone_number):
        # Used by authenticate() for JWT and admin login: accept any format
        # the user types (0701..., +256 701..., 256701...).
        return self.get(**{self.model.USERNAME_FIELD: normalize_phone(phone_number)})

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        phone_number = normalize_phone(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Primary user model.
    Phone number is the login credential — most Ugandan informal workers
    are more likely to have a phone number than an email address.
    """
    USER_TYPE_CHOICES = [
        ('boda_boda', 'Boda Boda Rider'),
        ('market_vendor', 'Market Vendor'),
        ('general', 'General User'),
        ('organisation', 'Organisation'),
        ('legal_professional', 'Legal Professional'),
        ('admin', 'Administrator'),
    ]

    LANGUAGE_CHOICES = LANGUAGE_CHOICES_FROM_REGISTRY

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='general')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    # Privacy
    consented_to_processing = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'lb_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name or 'User'} ({self.phone_number})"


class Organisation(models.Model):
    """
    Organisations that subscribe to LegalBridge for their members.
    E.g. boda boda SACCOs, market vendor associations, NGOs.
    """
    ORG_TYPE_CHOICES = [
        ('boda_sacco', 'Boda Boda SACCO'),
        ('market_association', 'Market Vendor Association'),
        ('ngo', 'NGO / Civil Society'),
        ('legal_aid', 'Legal Aid Organisation'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    org_type = models.CharField(max_length=30, choices=ORG_TYPE_CHOICES)
    registration_number = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    admin_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='administered_orgs'
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lb_organisations'
        verbose_name = 'Organisation'

    def __str__(self):
        return self.name


class OrganisationMember(models.Model):
    """Links users to organisations (for subscription benefits)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='org_memberships')
    member_number = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lb_org_members'
        unique_together = ('organisation', 'user')
