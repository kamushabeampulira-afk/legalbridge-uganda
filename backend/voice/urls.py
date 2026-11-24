from django.urls import path
from . import views

urlpatterns = [
    path('transcribe/', views.transcribe_view, name='voice_transcribe'),
    path('synthesize/', views.synthesize_view, name='voice_synthesize'),
]
