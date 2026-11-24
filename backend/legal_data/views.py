"""Legal data API views."""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from config.languages import LANGUAGE_CODES, validated_language

from .models import LegalSource, LegalQuery
from .serializers import LegalSourceSerializer, LegalQuerySerializer


class LegalCategoriesView(generics.ListAPIView):
    """GET /api/legal/categories/ — list approved legal sources by subject."""
    serializer_class = LegalSourceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        subject = self.request.query_params.get('subject')
        qs = LegalSource.objects.filter(status='approved')
        if subject:
            qs = qs.filter(subject=subject)
        return qs


class LegalSourceDetailView(generics.RetrieveAPIView):
    """GET /api/legal/sources/<pk>/"""
    serializer_class = LegalSourceSerializer
    permission_classes = [permissions.AllowAny]
    queryset = LegalSource.objects.filter(status='approved')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ask_legal(request):
    """
    POST /api/legal/ask/
    Free-text legal question answered using the RAG pipeline.
    Body: { question, user_category, language }
    """
    question = request.data.get('question', '').strip()
    user_category = request.data.get('user_category', 'general')
    language, language_valid = validated_language(
        request.data.get('language', request.user.preferred_language)
    )
    if not language_valid:
        return Response(
            {'error': f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'},
            status=400,
        )

    if not question:
        return Response({'error': 'Question text is required.'}, status=400)
    if len(question) > 2000:
        return Response({'error': 'Question is too long. Please keep it under 2000 characters.'}, status=400)

    from ai_engine.engine import answer_legal_question
    from ai_engine.openai_service import AIServiceUnavailable
    try:
        result = answer_legal_question(
            question=question,
            user_category=user_category,
            language=language,
            user=request.user,
        )
        return Response(result, status=200)
    except AIServiceUnavailable as e:
        return Response({'error': e.user_message, 'error_category': e.category}, status=503)
    except Exception as e:
        import logging
        logging.getLogger('legalbridge').error(f'Ask legal failed: {e}')
        return Response({
            'error': 'Could not process your question at this time. Please try again.'
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def query_history(request):
    """GET /api/legal/history/ — user's previous legal questions."""
    queries = LegalQuery.objects.filter(user=request.user).order_by('-created_at')[:50]
    serializer = LegalQuerySerializer(queries, many=True)
    return Response(serializer.data)
