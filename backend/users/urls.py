from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('delete/', views.delete_account, name='delete_account'),
    path('language/', views.set_language, name='set_language'),
    path('organisations/', views.OrganisationListCreateView.as_view(), name='organisations'),
]
