"""
pytest-django configuration for LegalBridge backend tests.
pytest-django reads DJANGO_SETTINGS_MODULE and calls django.setup() automatically.
Do NOT call django.setup() manually here — it causes fixture teardown failures.
"""
import django
from django.conf import settings


def pytest_configure(config):
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
