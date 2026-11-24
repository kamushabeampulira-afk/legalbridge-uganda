"""Tests: user registration, authentication, profile management."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.phone import normalize_phone

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def registered_user(db):
    return User.objects.create_user(
        phone_number='+256700000001',
        password='testpass123',
        full_name='Test Rider',
        user_type='boda_boda',
        consented_to_processing=True,
    )


@pytest.mark.django_db
def test_register_user(client):
    url = reverse('register')
    data = {
        'phone_number': '+256700000002',
        'password': 'securepass1',
        'password_confirm': 'securepass1',
        'full_name': 'Jane Vendor',
        'user_type': 'market_vendor',
        'preferred_language': 'en',
        'consented_to_processing': True,
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert 'user_id' in response.data


@pytest.mark.django_db
def test_register_requires_consent(client):
    url = reverse('register')
    data = {
        'phone_number': '+256700000003',
        'password': 'securepass1',
        'password_confirm': 'securepass1',
        'consented_to_processing': False,
    }
    response = client.post(url, data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_password_mismatch(client):
    url = reverse('register')
    data = {
        'phone_number': '+256700000004',
        'password': 'securepass1',
        'password_confirm': 'wrongpass',
        'consented_to_processing': True,
    }
    response = client.post(url, data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_obtain_token(client, registered_user):
    url = reverse('token_obtain_pair')
    response = client.post(url, {
        'phone_number': '+256700000001',
        'password': 'testpass123',
    })
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_profile_requires_auth(client):
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_returns_data(client, registered_user):
    client.force_authenticate(user=registered_user)
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['phone_number'] == '+256700000001'


@pytest.mark.django_db
def test_set_language(client, registered_user):
    client.force_authenticate(user=registered_user)
    url = reverse('set_language')
    response = client.post(url, {'language': 'lg'})
    assert response.status_code == 200
    registered_user.refresh_from_db()
    assert registered_user.preferred_language == 'lg'


@pytest.mark.django_db
@pytest.mark.parametrize('code', ['nyn', 'ach', 'lgg'])
def test_set_additional_languages(client, registered_user, code):
    client.force_authenticate(user=registered_user)
    url = reverse('set_language')
    response = client.post(url, {'language': code})
    assert response.status_code == 200
    registered_user.refresh_from_db()
    assert registered_user.preferred_language == code


@pytest.mark.django_db
def test_set_invalid_language(client, registered_user):
    client.force_authenticate(user=registered_user)
    url = reverse('set_language')
    response = client.post(url, {'language': 'fr'})
    assert response.status_code == 400


# ── Phone number normalisation ───────────────────────────────────────────────

@pytest.mark.parametrize('raw', [
    '0701066872',
    '+256701066872',
    '256701066872',
    '+256 701 066 872',
    '0701-066-872',
    '00256701066872',
    '701066872',
    ' 0701066872 ',
])
def test_normalize_phone_ugandan_formats(raw):
    assert normalize_phone(raw) == '+256701066872'


@pytest.mark.parametrize('raw', [
    '+442079460958',
    'deleted_b85f2447-a373-428e-8d7e-9d9e4f557f18',
])
def test_normalize_phone_leaves_other_values_alone(raw):
    assert normalize_phone(raw) == raw


@pytest.mark.django_db
@pytest.mark.parametrize('register_as,login_as', [
    ('0701066872', '+256 701 066 872'),
    ('+256701066872', '0701066872'),
    ('256701066872', '0701 066 872'),
])
def test_login_with_different_phone_format_than_registration(client, register_as, login_as):
    response = client.post(reverse('register'), {
        'phone_number': register_as,
        'password': 'securepass1',
        'password_confirm': 'securepass1',
        'consented_to_processing': True,
    })
    assert response.status_code == 201
    assert response.data['phone_number'] == '+256701066872'

    response = client.post(reverse('token_obtain_pair'), {
        'phone_number': login_as,
        'password': 'securepass1',
    })
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_register_duplicate_number_in_other_format_is_rejected(client, registered_user):
    response = client.post(reverse('register'), {
        'phone_number': '0700 000 001',  # same number as registered_user
        'password': 'securepass1',
        'password_confirm': 'securepass1',
        'consented_to_processing': True,
    })
    assert response.status_code == 400
    assert 'phone_number' in response.data


@pytest.mark.django_db
def test_create_user_normalizes_phone():
    user = User.objects.create_user(phone_number='0700 123 456', password='x' * 8)
    assert user.phone_number == '+256700123456'
