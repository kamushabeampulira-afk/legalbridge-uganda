from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_legal, name='legal_ask'),
    path('categories/', views.LegalCategoriesView.as_view(), name='legal_categories'),
    path('sources/<uuid:pk>/', views.LegalSourceDetailView.as_view(), name='legal_source_detail'),
    path('history/', views.query_history, name='legal_query_history'),
]
