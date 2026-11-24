from rest_framework import serializers
from .models import SubscriptionPlan, OrganisationSubscription, SponsoredAccess


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description',
            'price_ugx_monthly', 'price_ugx_annual',
            'max_members', 'features',
        ]


class OrganisationSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    organisation_name = serializers.CharField(source='organisation.name', read_only=True)

    class Meta:
        model = OrganisationSubscription
        fields = [
            'id', 'organisation_name', 'plan', 'status',
            'billing_cycle', 'started_at', 'expires_at',
            'max_beneficiaries',
        ]
