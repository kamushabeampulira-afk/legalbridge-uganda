"""Tests for the deployment health endpoint."""
import pytest
from django.test import Client


@pytest.mark.django_db
def test_healthz_returns_ok():
    response = Client().get('/healthz')
    assert response.status_code == 200
    assert response.content == b'ok'
