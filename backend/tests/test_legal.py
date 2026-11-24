"""Tests: legal question API and RAG pipeline safeguards."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        phone_number='+256700200001',
        password='testpass123',
        user_type='boda_boda',
        consented_to_processing=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_ask_requires_auth():
    client = APIClient()
    url = reverse('legal_ask')
    response = client.post(url, {'question': 'What are my rights?'}, format='json')
    assert response.status_code == 401


@pytest.mark.django_db
def test_ask_requires_question(auth_client):
    client, _ = auth_client
    url = reverse('legal_ask')
    response = client.post(url, {'question': '', 'user_category': 'boda_boda', 'language': 'en'}, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_ask_rejects_too_long_question(auth_client):
    client, _ = auth_client
    url = reverse('legal_ask')
    response = client.post(url, {
        'question': 'x' * 2001,
        'user_category': 'boda_boda',
        'language': 'en',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_ask_returns_uncertainty_when_no_sources(auth_client):
    """When ChromaDB returns no chunks, the system must return uncertainty — not hallucinate."""
    client, _ = auth_client
    url = reverse('legal_ask')

    with patch('legal_data.vector_store.retrieve_relevant_chunks', return_value=[]):
        response = client.post(url, {
            'question': 'What is the penalty for riding without a helmet?',
            'user_category': 'boda_boda',
            'language': 'en',
        }, format='json')

    assert response.status_code == 200
    data = response.data
    assert data['uncertainty_flag'] is True
    assert data['has_verified_sources'] is False
    # Must contain the uncertainty message, not an invented answer
    assert 'cannot verify' in data['answer'].lower() or 'legal professional' in data['answer'].lower()


@pytest.mark.django_db
def test_legal_categories_public():
    """Legal categories endpoint is public (no auth needed)."""
    client = APIClient()
    url = reverse('legal_categories')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ask_stores_query_in_history(auth_client):
    """Questions are logged to LegalQuery for the authenticated user."""
    from legal_data.models import LegalQuery
    client, user = auth_client
    url = reverse('legal_ask')

    with patch('legal_data.vector_store.retrieve_relevant_chunks', return_value=[]):
        client.post(url, {
            'question': 'Can an officer impound my boda?',
            'user_category': 'boda_boda',
            'language': 'en',
        }, format='json')

    assert LegalQuery.objects.filter(user=user).count() == 1
    query = LegalQuery.objects.get(user=user)
    assert 'impound' in query.question_text.lower()
