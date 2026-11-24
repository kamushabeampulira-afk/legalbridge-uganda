"""Documents serializers"""
from rest_framework import serializers
from django.conf import settings
from config.languages import LANGUAGE_CODES, is_supported_language

from .models import Document, DocumentAnalysis


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'original_filename', 'user_category', 'language']
        read_only_fields = ['id']

    def validate_language(self, value):
        if not is_supported_language(value):
            raise serializers.ValidationError(
                f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'
            )
        return value

    def validate_file(self, value):
        # Size check
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if value.size > max_bytes:
            raise serializers.ValidationError(
                f'File is too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.'
            )
        # Type check — be permissive on web where content_type may be unreliable
        content_type = getattr(value, 'content_type', '') or ''
        # Derive type from filename if content_type is missing or generic
        name = getattr(value, 'name', '') or ''
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''

        allowed_types = ['image/jpeg', 'image/png', 'application/pdf',
                         'image/jpg', 'application/octet-stream', '']
        allowed_exts = ['jpg', 'jpeg', 'png', 'pdf']

        type_ok = content_type in allowed_types
        ext_ok = ext in allowed_exts

        if not type_ok and not ext_ok:
            raise serializers.ValidationError(
                f'Only JPEG, PNG and PDF files are accepted. Got: {content_type or ext or "unknown"}'
            )
        return value


class DocumentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAnalysis
        fields = [
            'id', 'summary', 'what_it_means', 'relevant_law',
            'details_to_check', 'next_steps', 'missing_information',
            'where_to_get_help', 'legal_sources_used',
            'has_verified_sources', 'uncertainty_flag',
            'audio_summary_en', 'audio_summary_lg',
            'created_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    analysis = DocumentAnalysisSerializer(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'file_type', 'file_size_kb',
            'doc_type', 'user_category', 'status', 'language',
            'extracted_text', 'ocr_confidence', 'ocr_warnings',
            'detected_dates', 'detected_amounts', 'detected_reference_numbers',
            'detected_names', 'created_at', 'analysis',
        ]


class DocumentListSerializer(serializers.ModelSerializer):
    has_analysis = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'doc_type', 'user_category',
            'status', 'created_at', 'has_analysis',
        ]

    def get_has_analysis(self, obj):
        return hasattr(obj, 'analysis')
