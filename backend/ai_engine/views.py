"""AI Engine views — guided scenarios and direct AI queries."""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .engine import answer_boda_stopped, answer_eviction_guidance
from .openai_service import AIServiceUnavailable

logger = logging.getLogger('legalbridge')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def boda_stopped_view(request):
    """
    POST /api/ai/boda-stopped/
    Guided scenario: boda rider stopped by an officer.
    Body: { told_about, has_written_notice, penalty_mentioned, has_reference, additional_details, language }
    """
    language = request.data.get('language', request.user.preferred_language or 'en')
    try:
        result = answer_boda_stopped(request.data, language=language, user=request.user)
        return Response(result)
    except AIServiceUnavailable as e:
        return Response({'error': e.user_message, 'error_category': e.category}, status=503)
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
    language = request.data.get('language', request.user.preferred_language or 'en')
    try:
        result = answer_eviction_guidance(request.data, language=language, user=request.user)
        return Response(result)
    except AIServiceUnavailable as e:
        return Response({'error': e.user_message, 'error_category': e.category}, status=503)
    except Exception as e:
        logger.error(f'Eviction guidance failed: {e}')
        return Response({'error': 'Could not process your request. Please try again.'}, status=500)


# ── AI service status (administrators only) ──────────────────────────────────
from rest_framework.permissions import IsAdminUser  # noqa: E402


@api_view(['GET'])
@permission_classes([IsAdminUser])
def ai_status_view(request):
    """GET /api/ai/status/ — latest AI service and pipeline component status. Never includes keys."""
    from .diagnostics import service_overview
    return Response(service_overview())


@api_view(['POST'])
@permission_classes([IsAdminUser])
def ai_status_run_view(request):
    """
    POST /api/ai/status/run/  Body: {"checks": "connection" | "components" | "end_to_end"}
    Superusers (or staff with ai_engine.add_aihealthcheck) only.
    """
    from .diagnostics import check_explanation, run_all, service_overview
    from .openai_service import run_connection_check
    if not (request.user.is_superuser or request.user.has_perm('ai_engine.add_aihealthcheck')):
        return Response({'error': 'You do not have permission to run AI diagnostics.'}, status=403)
    checks = request.data.get('checks', 'connection')
    if checks == 'connection':
        run_connection_check(request.user)
    elif checks == 'components':
        run_all(request.user, include_connection=True, include_explanation=False)
    elif checks == 'end_to_end':
        check_explanation(request.user)
    else:
        return Response({'error': 'checks must be connection, components or end_to_end.'}, status=400)
    return Response(service_overview())
