"""Documents views — upload, process, analyse, delete."""
import logging
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from config.languages import LANGUAGE_CODES, validated_language

from .models import Document, DocumentAnalysis
from .serializers import (
    DocumentUploadSerializer,
    DocumentDetailSerializer,
    DocumentListSerializer,
)
from .ocr import extract_text_from_file, extract_key_fields, classify_document_type

logger = logging.getLogger('legalbridge')


class DocumentUploadView(generics.CreateAPIView):
    """
    POST /api/documents/upload/
    Accepts a file upload, validates it, saves it and kicks off processing.
    """
    serializer_class = DocumentUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        content_type = getattr(file_obj, 'content_type', '') or ''
        name = getattr(file_obj, 'name', '') or ''
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        ext_map = {
            'image/jpeg': 'jpg', 'image/jpg': 'jpg',
            'image/png': 'png',
            'application/pdf': 'pdf',
        }
        file_type = ext_map.get(content_type) or ext or 'unknown'
        doc = serializer.save(
            owner=self.request.user,
            original_filename=name,
            file_type=file_type,
            file_size_bytes=file_obj.size if file_obj else 0,
            status='uploaded',
        )
        # Kick off synchronous processing (use Celery in production)
        self._process_document(doc)

    def _process_document(self, doc: Document):
        """Run OCR and classification synchronously for MVP."""
        try:
            doc.status = 'processing'
            doc.processing_started_at = timezone.now()
            doc.save(update_fields=['status', 'processing_started_at'])

            result = extract_text_from_file(doc.file.path)
            fields = extract_key_fields(result['text'])
            doc_type = classify_document_type(result['text'])

            doc.extracted_text = result['text']
            doc.ocr_confidence = result['confidence']
            doc.ocr_warnings = '; '.join(result['warnings'])
            doc.doc_type = doc_type
            doc.detected_dates = fields['dates']
            doc.detected_amounts = fields['amounts']
            doc.detected_reference_numbers = fields['reference_numbers']
            doc.status = 'completed'
            doc.processing_completed_at = timezone.now()
            doc.save()

        except Exception as e:
            logger.error(f'Document processing failed for {doc.id}: {e}')
            doc.status = 'failed'
            doc.processing_error = str(e)
            doc.save(update_fields=['status', 'processing_error'])


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_document(request, pk):
    """
    POST /api/documents/<pk>/analyze/
    Triggers AI analysis of an already-uploaded document.
    """
    try:
        doc = Document.objects.get(pk=pk, owner=request.user, is_deleted=False)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found.'}, status=404)

    if doc.status not in ('completed', 'uploaded'):
        return Response({'error': f'Document is not ready for analysis (status: {doc.status}).'}, status=400)

    language, language_valid = validated_language(request.data.get('language', doc.language))
    if not language_valid:
        return Response(
            {'error': f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'},
            status=400,
        )

    # Import here to avoid circular imports
    from ai_engine.engine import generate_document_explanation
    try:
        analysis = generate_document_explanation(doc, language=language)
        from .serializers import DocumentAnalysisSerializer
        return Response(DocumentAnalysisSerializer(analysis).data, status=200)
    except Exception as e:
        logger.error(f'AI analysis failed for doc {doc.id}: {e}')
        return Response({'error': 'Analysis failed. Please try again.'}, status=500)


class DocumentListView(generics.ListAPIView):
    """GET /api/documents/history/"""
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user,
            is_deleted=False,
        ).order_by('-created_at')


class DocumentDetailView(generics.RetrieveAPIView):
    """GET /api/documents/<pk>/"""
    serializer_class = DocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user, is_deleted=False)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_document(request, pk):
    """DELETE /api/documents/<pk>/  — user deletes their own document."""
    try:
        doc = Document.objects.get(pk=pk, owner=request.user, is_deleted=False)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found.'}, status=404)

    # Soft delete — do not permanently destroy without a retention policy
    doc.is_deleted = True
    doc.deleted_at = timezone.now()
    doc.extracted_text = '[DELETED BY USER]'
    doc.save()

    # Remove physical file
    try:
        if doc.file:
            import os
            if os.path.exists(doc.file.path):
                os.remove(doc.file.path)
    except Exception as e:
        logger.warning(f'Could not remove file for doc {doc.id}: {e}')

    return Response({'message': 'Document deleted.'}, status=200)
