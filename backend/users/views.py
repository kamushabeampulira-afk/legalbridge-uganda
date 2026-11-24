"""Users views"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from config.languages import LANGUAGE_CODES, is_supported_language

from .serializers import UserRegistrationSerializer, UserProfileSerializer, OrganisationSerializer
from .models import Organisation

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'Account created successfully.',
                'user_id': str(user.id),
                'phone_number': user.phone_number,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """Allow a user to delete their own account and associated data."""
    user = request.user
    # Anonymise rather than hard-delete to preserve audit integrity
    user.full_name = 'Deleted User'
    user.email = None
    user.phone_number = f'deleted_{user.id}'
    user.is_active = False
    user.save()
    return Response({'message': 'Your account has been deleted.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_language(request):
    lang = request.data.get('language', 'en')
    if not is_supported_language(lang):
        return Response(
            {'error': f'Unsupported language. Use one of: {", ".join(LANGUAGE_CODES)}.'},
            status=400,
        )
    request.user.preferred_language = lang
    request.user.save(update_fields=['preferred_language'])
    return Response({'language': lang})


class OrganisationListCreateView(generics.ListCreateAPIView):
    queryset = Organisation.objects.filter(is_active=True)
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(admin_user=self.request.user)
