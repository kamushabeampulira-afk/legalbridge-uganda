from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('history/', views.DocumentListView.as_view(), name='document_history'),
    path('<uuid:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<uuid:pk>/analyze/', views.analyze_document, name='document_analyze'),
    path('<uuid:pk>/delete/', views.delete_document, name='document_delete'),
]
