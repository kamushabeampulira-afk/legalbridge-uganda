"""Tests: document upload, validation, and deletion."""
import pytest
import tempfile
import os
from io import BytesIO
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        phone_number='+256700100001',
        password='testpass123',
        user_type='boda_boda',
        consented_to_processing=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def make_image_upload(filename='test.jpg', content_type='image/jpeg'):
    """Create a minimal valid JPEG for upload testing."""
    # 1x1 pixel white JPEG
    jpeg_bytes = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e'
        b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00'
        b'\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00'
        b'\x08\x01\x01\x00\x00?\x00\xf5\x00\xff\xd9'
    )
    return SimpleUploadedFile(filename, jpeg_bytes, content_type=content_type)


@pytest.mark.django_db
def test_upload_requires_auth():
    client = APIClient()
    url = reverse('document_upload')
    response = client.post(url, {})
    assert response.status_code == 401


@pytest.mark.django_db
def test_upload_rejects_missing_file(auth_client):
    client, _ = auth_client
    url = reverse('document_upload')
    response = client.post(url, {'user_category': 'boda_boda', 'language': 'en'})
    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_rejects_invalid_type(auth_client):
    client, _ = auth_client
    url = reverse('document_upload')
    bad_file = SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain')
    response = client.post(
        url,
        {'file': bad_file, 'user_category': 'boda_boda', 'language': 'en'},
        format='multipart',
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_history_returns_empty_for_new_user(auth_client):
    client, _ = auth_client
    url = reverse('document_history')
    response = client.get(url)
    assert response.status_code == 200
    data = response.data
    results = data.get('results', data) if isinstance(data, dict) else data
    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.django_db
def test_delete_nonexistent_document(auth_client):
    client, _ = auth_client
    import uuid
    url = reverse('document_delete', kwargs={'pk': str(uuid.uuid4())})
    response = client.delete(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_history_requires_auth():
    client = APIClient()
    url = reverse('document_history')
    response = client.get(url)
    assert response.status_code == 401
