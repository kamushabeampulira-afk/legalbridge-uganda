"""Analytics views — admin-only aggregate stats."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import DailyUsageStat
from documents.models import Document
from legal_data.models import LegalQuery
from channels_app.models import USSDSession


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """GET /api/analytics/dashboard/ — admin aggregate summary."""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    total_docs = Document.objects.filter(is_deleted=False).count()
    total_queries = LegalQuery.objects.count()
    total_ussd = USSDSession.objects.count()
    uncertainty_rate = LegalQuery.objects.filter(uncertainty_flag=True).count()

    weekly_docs = Document.objects.filter(
        created_at__date__gte=week_ago, is_deleted=False
    ).count()
    weekly_queries = LegalQuery.objects.filter(created_at__date__gte=week_ago).count()

    doc_type_breakdown = (
        Document.objects.filter(is_deleted=False)
        .values('doc_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return Response({
        'totals': {
            'documents_uploaded': total_docs,
            'legal_questions': total_queries,
            'ussd_sessions': total_ussd,
            'uncertainty_flags': uncertainty_rate,
        },
        'last_7_days': {
            'documents': weekly_docs,
            'questions': weekly_queries,
        },
        'document_types': list(doc_type_breakdown),
    })
