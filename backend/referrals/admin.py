from django.contrib import admin
from .models import LegalAidOrganisation, LegalProfessional


@admin.register(LegalAidOrganisation)
class LegalAidOrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'district', 'service_type', 'is_free', 'is_verified', 'is_active']
    list_filter = ['service_type', 'district', 'is_free', 'is_verified', 'is_active']
    search_fields = ['name', 'acronym', 'district']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LegalProfessional)
class LegalProfessionalAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'district', 'offers_free_consultation', 'is_verified', 'is_active']
    list_filter = ['district', 'offers_free_consultation', 'is_verified', 'is_active']
    search_fields = ['full_name', 'organisation', 'district']
