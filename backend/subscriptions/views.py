from rest_framework import generics, permissions
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer


class SubscriptionPlanListView(generics.ListAPIView):
    """GET /api/subscriptions/plans/ — public list of available plans."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)
