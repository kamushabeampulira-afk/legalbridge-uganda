from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import LegalAidOrganisation, LegalProfessional
from .serializers import LegalAidOrganisationSerializer, LegalProfessionalSerializer


class LegalAidListView(generics.ListAPIView):
    """GET /api/referrals/legal-aid/"""
    serializer_class = LegalAidOrganisationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['district', 'service_type', 'is_free']
    search_fields = ['name', 'description', 'district']

    def get_queryset(self):
        return LegalAidOrganisation.objects.filter(is_active=True, is_verified=True)


class LegalProfessionalListView(generics.ListAPIView):
    """GET /api/referrals/professionals/"""
    serializer_class = LegalProfessionalSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['district', 'offers_free_consultation']
    search_fields = ['full_name', 'organisation', 'district']

    def get_queryset(self):
        return LegalProfessional.objects.filter(is_active=True, is_verified=True)
