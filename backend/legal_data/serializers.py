from rest_framework import serializers
from .models import LegalSource, LegalProvision, LegalQuery


class LegalSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalSource
        fields = [
            'id', 'title', 'short_title', 'category', 'subject',
            'issuing_authority', 'publication_date', 'effective_date',
            'source_url', 'summary', 'status', 'last_verified_at',
        ]


class LegalProvisionSerializer(serializers.ModelSerializer):
    source_title = serializers.CharField(source='source.title', read_only=True)

    class Meta:
        model = LegalProvision
        fields = [
            'id', 'source', 'source_title', 'section_number',
            'section_title', 'text', 'plain_language_summary', 'tags',
        ]


class LegalQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalQuery
        fields = [
            'id', 'question_text', 'user_category', 'language',
            'response_text', 'has_verified_sources', 'uncertainty_flag', 'created_at',
        ]
        read_only_fields = [
            'id', 'response_text', 'has_verified_sources',
            'uncertainty_flag', 'created_at', 'sources_retrieved',
        ]
