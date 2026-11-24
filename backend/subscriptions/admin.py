from django.contrib import admin
from .models import SubscriptionPlan, OrganisationSubscription, SponsoredAccess


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_ugx_monthly', 'price_ugx_annual', 'max_members', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']


@admin.register(OrganisationSubscription)
class OrganisationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'plan', 'status', 'billing_cycle', 'started_at', 'expires_at']
    list_filter = ['status', 'billing_cycle']
    search_fields = ['organisation__name']


@admin.register(SponsoredAccess)
class SponsoredAccessAdmin(admin.ModelAdmin):
    list_display = [
        'sponsor_organisation', 'description', 'target_user_category',
        'max_beneficiaries', 'current_beneficiary_count', 'is_active',
    ]
    list_filter = ['is_active', 'target_user_category']
