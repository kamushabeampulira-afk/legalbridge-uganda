from django.urls import path
from . import views

urlpatterns = [
    path('boda-stopped/', views.boda_stopped_view, name='boda_stopped'),
    path('eviction-guidance/', views.eviction_guidance_view, name='eviction_guidance'),
]
