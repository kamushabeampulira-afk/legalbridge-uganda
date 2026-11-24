"""AI Engine views — guided scenarios and direct AI queries."""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from config.languages import LANGUAGE_CODES, validated_language

from .engine import answer_boda_stopped, answer_eviction_guidance

logger = logging.getLogger('legalbridge')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def boda_stopped_view(request):
    """
    POST /api/ai/boda-stopped/
    Guided scenario: boda rider stopped by an officer.
    Body: { told_about, has_written_notice, penalty_mentioned, has_reference, additional_details, language }
    """
    language, language_valid = validated_language(
        request.data.get('language', request.user.preferred_language)
    )
    if not language_valid:
        return Response(
            {'error': f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'},
            status=400,
        )
    try:
        result = answer_boda_stopped(request.data, language=language, user=request.user)
        return Response(result)
    except Exception as e:
        logger.error(f'Boda stopped guidance failed: {e}')
        return Response({'error': 'Could not process your request. Please try again.'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def eviction_guidance_view(request):
    """
    POST /api/ai/eviction-guidance/
    Guided scenario: market vendor facing eviction.
    Body: { has_allocation_slip, has_receipts, notice_issuer, reason_given, deadline, additional_details, language }
    """
    language, language_valid = validated_language(
        request.data.get('language', request.user.preferred_language)
    )
    if not language_valid:
        return Response(
            {'error': f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'},
            status=400,
        )
    try:
        result = answer_eviction_guidance(request.data, language=language, user=request.user)
        return Response(result)
    except Exception as e:
        logger.error(f'Eviction guidance failed: {e}')
        return Response({'error': 'Could not process your request. Please try again.'}, status=500)
