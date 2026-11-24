from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.ussd_webhook, name='ussd_webhook'),
]
