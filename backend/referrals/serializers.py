from rest_framework import serializers
from .models import LegalAidOrganisation, LegalProfessional


class LegalAidOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalAidOrganisation
        fields = [
            'id', 'name', 'acronym', 'description', 'services',
            'service_type', 'district', 'physical_address',
            'phone_number', 'email', 'website',
            'eligibility', 'is_free', 'consultation_info',
        ]


class LegalProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalProfessional
        fields = [
            'id', 'full_name', 'title', 'organisation',
            'specialisations', 'district', 'physical_address',
            'phone_number', 'email',
            'consultation_fee_ugx', 'offers_free_consultation',
            'languages_spoken',
        ]
