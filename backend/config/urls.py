"""LegalBridge Informal — Root URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API v1
    path('api/users/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/legal/', include('legal_data.urls')),
    path('api/ai/', include('ai_engine.urls')),
    path('api/voice/', include('voice.urls')),
    path('api/referrals/', include('referrals.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),

    # USSD webhook
    path('api/ussd/', include('channels_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
