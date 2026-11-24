"""Tests: legal aid directory and referrals API."""
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from referrals.models import LegalAidOrganisation


@pytest.fixture
def verified_org(db):
    return LegalAidOrganisation.objects.create(
        name='Test Legal Aid Uganda',
        service_type='general_legal_aid',
        district='Kampala',
        phone_number='+256414000001',
        website='https://example.org',
        is_free=True,
        is_verified=True,
        is_active=True,
        last_verified_at=timezone.now(),
    )


@pytest.fixture
def unverified_org(db):
    return LegalAidOrganisation.objects.create(
        name='Unverified Org',
        service_type='general_legal_aid',
        is_verified=False,
        is_active=True,
    )


@pytest.mark.django_db
def test_legal_aid_list_is_public(verified_org):
    client = APIClient()
    url = reverse('legal_aid_list')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_legal_aid_only_returns_verified(verified_org, unverified_org):
    client = APIClient()
    url = reverse('legal_aid_list')
    response = client.get(url)
    names = [item['name'] for item in (response.data.get('results', response.data))]
    assert 'Test Legal Aid Uganda' in names
    assert 'Unverified Org' not in names


@pytest.mark.django_db
def test_legal_aid_filter_by_district(verified_org):
    client = APIClient()
    url = reverse('legal_aid_list')
    response = client.get(url, {'district': 'Kampala'})
    assert response.status_code == 200
    results = response.data.get('results', response.data)
    assert all(r['district'] == 'Kampala' for r in results)


@pytest.mark.django_db
def test_legal_aid_filter_by_free(verified_org):
    client = APIClient()
    url = reverse('legal_aid_list')
    response = client.get(url, {'is_free': 'true'})
    assert response.status_code == 200
    results = response.data.get('results', response.data)
    assert all(r['is_free'] for r in results)
