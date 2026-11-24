from django.urls import path
from . import views

urlpatterns = [
    path('legal-aid/', views.LegalAidListView.as_view(), name='legal_aid_list'),
    path('professionals/', views.LegalProfessionalListView.as_view(), name='professionals_list'),
]
