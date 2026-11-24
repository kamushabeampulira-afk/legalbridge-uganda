"""Tests: OpenAI error classification, health check, request logging, status dashboard and API.
The OpenAI client is always mocked: no test makes a network request."""
from unittest.mock import MagicMock, patch

import httpx
import openai
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from ai_engine import diagnostics
from ai_engine.models import AIHealthCheck, AIRequestLog
from ai_engine.openai_service import (
    AIServiceUnavailable, chat_completion, classify_error, run_connection_check, sanitize,
)

User = get_user_model()
REQ = httpx.Request('POST', 'https://api.openai.com/v1/chat/completions')
FAKE_KEY = 'sk-test-abcdefghijklmnopqrstuvwxyz123456'


def status_error(cls, status, code=None, message='error'):
    return cls(message, response=httpx.Response(status, request=REQ), body={'code': code, 'message': message})


def ok_response(text='OK'):
    resp = MagicMock()
    resp.choices[0].message.content = text
    return resp


@pytest.fixture
def ai_settings(settings):
    settings.OPENAI_API_KEY = FAKE_KEY
    settings.OPENAI_MODEL = 'gpt-4o'
    settings.AI_DEMO_MODE = False
    return settings


# ── Error classification ─────────────────────────────────────────────────────

@pytest.mark.parametrize('exc,expected', [
    (status_error(openai.AuthenticationError, 401, 'invalid_api_key'), 'auth_failed'),
    (status_error(openai.RateLimitError, 429, 'insufficient_quota'), 'quota_billing'),
    (status_error(openai.RateLimitError, 429, 'credit_balance_exhausted'), 'quota_billing'),
    (status_error(openai.RateLimitError, 429, 'rate_limit_exceeded', 'Rate limit reached'), 'rate_limited'),
    (status_error(openai.NotFoundError, 404, 'model_not_found'), 'model_unavailable'),
    (status_error(openai.PermissionDeniedError, 403, 'model_not_found',
                  'Project does not have access to model gpt-4o'), 'model_unavailable'),
    (openai.APITimeoutError(request=REQ), 'timeout'),
    (openai.APIConnectionError(request=REQ), 'network_error'),
    (status_error(openai.InternalServerError, 500), 'unknown_error'),
    (ValueError('something odd'), 'unknown_error'),
])
def test_classify_error(exc, expected):
    assert classify_error(exc)[0] == expected


def test_sanitize_masks_keys_and_project_ids():
    text = f'Incorrect API key provided: {FAKE_KEY}. Project proj_ABCdef123456 has no access.'
    clean = sanitize(text)
    assert FAKE_KEY not in clean
    assert 'proj_ABCdef123456' not in clean


# ── Health check ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_health_check_missing_key(settings):
    settings.OPENAI_API_KEY = ''
    result = run_connection_check()
    assert result.ai_status == 'missing_key'
    assert result.component_status == 'fail'
    assert result.details['key_present'] is False


@pytest.mark.django_db
def test_health_check_operational_requires_real_response(ai_settings):
    client = MagicMock()
    client.chat.completions.create.return_value = ok_response('OK')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'operational'
    assert result.component_status == 'pass'
    checks = result.details
    assert all(checks[k] is True for k in ('key_present', 'key_accepted', 'model_accessible',
                                           'test_request_succeeded', 'response_valid', 'within_time_limit'))
    # The test request is minimal
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs['max_tokens'] <= 10


@pytest.mark.django_db
def test_health_check_auth_failed(ai_settings):
    client = MagicMock()
    client.models.retrieve.side_effect = status_error(openai.AuthenticationError, 401, 'invalid_api_key')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'auth_failed'
    assert result.details['key_accepted'] is False
    client.chat.completions.create.assert_not_called()


@pytest.mark.django_db
def test_health_check_quota_problem_is_not_operational(ai_settings):
    client = MagicMock()
    client.chat.completions.create.side_effect = status_error(openai.RateLimitError, 429, 'insufficient_quota',
                                                              'You exceeded your current quota')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'quota_billing'
    assert result.component_status == 'fail'
    assert result.details['key_accepted'] is True
    assert result.details['test_request_succeeded'] is False


@pytest.mark.django_db
def test_health_check_model_unavailable(ai_settings):
    client = MagicMock()
    err = status_error(openai.NotFoundError, 404, 'model_not_found', 'The model does not exist')
    client.models.retrieve.side_effect = err
    client.chat.completions.create.side_effect = err
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'model_unavailable'
    assert result.details['key_accepted'] is True
    assert result.details['model_accessible'] is False


@pytest.mark.django_db
def test_health_check_timeout_and_network(ai_settings):
    for exc, expected in ((openai.APITimeoutError(request=REQ), 'timeout'),
                          (openai.APIConnectionError(request=REQ), 'network_error')):
        client = MagicMock()
        client.models.retrieve.side_effect = exc
        with patch('ai_engine.openai_service.get_client', return_value=client):
            assert run_connection_check().ai_status == expected


@pytest.mark.django_db
def test_health_check_empty_response_is_invalid(ai_settings):
    client = MagicMock()
    client.chat.completions.create.return_value = ok_response('')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'invalid_response'
    assert result.component_status == 'fail'


@pytest.mark.django_db
def test_health_check_slow_response_warns(ai_settings):
    ai_settings.OPENAI_HEALTHCHECK_SLOW_MS = -1  # any response time exceeds this
    client = MagicMock()
    client.chat.completions.create.return_value = ok_response('OK')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        result = run_connection_check()
    assert result.ai_status == 'operational'
    assert result.component_status == 'warn'
    assert result.details['within_time_limit'] is False


# ── Real requests ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_chat_completion_without_key_raises_and_logs(settings):
    settings.OPENAI_API_KEY = ''
    settings.AI_DEMO_MODE = False
    with pytest.raises(AIServiceUnavailable) as info:
        chat_completion('sys', 'user', purpose='document_explanation')
    assert info.value.category == 'missing_key'
    log = AIRequestLog.objects.get()
    assert log.success is False and log.error_category == 'missing_key'


@pytest.mark.django_db
def test_chat_completion_demo_mode_is_opt_in(settings):
    settings.OPENAI_API_KEY = ''
    settings.AI_DEMO_MODE = True
    assert 'DEMO MODE' in chat_completion('sys', 'user', purpose='test')


@pytest.mark.django_db
def test_chat_completion_failure_is_categorised_and_logged(ai_settings):
    client = MagicMock()
    client.chat.completions.create.side_effect = status_error(openai.RateLimitError, 429, 'insufficient_quota')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        with pytest.raises(AIServiceUnavailable) as info:
            chat_completion('sys', 'user', purpose='document_explanation')
    assert info.value.category == 'quota_billing'
    assert FAKE_KEY not in info.value.user_message + info.value.detail
    assert AIRequestLog.objects.get().error_category == 'quota_billing'


@pytest.mark.django_db
def test_chat_completion_success_logs_latency_without_content(ai_settings):
    client = MagicMock()
    client.chat.completions.create.return_value = ok_response('An answer')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        assert chat_completion('secret system prompt', 'secret document', purpose='legal_question') == 'An answer'
    log = AIRequestLog.objects.get()
    assert log.success is True and log.latency_ms is not None
    assert not any('secret' in str(getattr(log, f.name)) for f in AIRequestLog._meta.fields)


# ── Overview: a passing connection test alone does not mean documents work ──

@pytest.mark.django_db
def test_overview_not_confirmed_when_only_connection_passes(ai_settings):
    client = MagicMock()
    client.chat.completions.create.return_value = ok_response('OK')
    with patch('ai_engine.openai_service.get_client', return_value=client):
        run_connection_check()
    overview = diagnostics.service_overview()
    assert overview['openai']['status'] == 'operational'
    assert overview['document_analysis']['status'] == 'not_confirmed'


@pytest.mark.django_db
def test_overview_unavailable_when_latest_connection_fails(settings):
    settings.OPENAI_API_KEY = ''
    run_connection_check()
    assert diagnostics.service_overview()['document_analysis']['status'] == 'unavailable'


@pytest.mark.django_db
def test_classification_component_check_passes():
    result = diagnostics.check_classification()
    assert result.component_status == 'pass', result.details


# ── Admin dashboard and API ──────────────────────────────────────────────────

@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(phone_number='+256700900001', password='adminpass123')


@pytest.mark.django_db
def test_admin_dashboard_shows_status_without_key(client, superuser, ai_settings):
    # Tests run with DEBUG off, where the manifest storage needs collectstatic; use plain storage
    ai_settings.STORAGES = {**ai_settings.STORAGES,
                            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}}
    client.force_login(superuser)
    response = client.get(reverse('admin:ai_engine_aihealthcheck_changelist'))
    assert response.status_code == 200
    content = response.content.decode()
    assert 'AI service status' in content
    assert 'Test OpenAI connection' in content
    assert FAKE_KEY not in content


@pytest.mark.django_db
def test_admin_can_run_connection_test(client, superuser, ai_settings):
    client.force_login(superuser)
    fake = MagicMock()
    fake.chat.completions.create.return_value = ok_response('OK')
    with patch('ai_engine.openai_service.get_client', return_value=fake):
        response = client.post(reverse('admin:ai_engine_aihealthcheck_run'), {'action': 'connection'})
    assert response.status_code == 302
    check = AIHealthCheck.objects.get()
    assert check.ai_status == 'operational' and check.triggered_by == superuser


@pytest.mark.django_db
def test_staff_without_permission_cannot_run_tests(client, db):
    staff = User.objects.create_user(phone_number='+256700900002', password='staffpass123', is_staff=True)
    client.force_login(staff)
    response = client.post(reverse('admin:ai_engine_aihealthcheck_run'), {'action': 'connection'})
    assert response.status_code == 403
    assert not AIHealthCheck.objects.exists()


@pytest.mark.django_db
def test_status_api_is_admin_only(superuser, ai_settings):
    api = APIClient()
    regular = User.objects.create_user(phone_number='+256700900003', password='userpass123')
    api.force_authenticate(regular)
    assert api.get(reverse('ai_status')).status_code == 403
    api.force_authenticate(superuser)
    response = api.get(reverse('ai_status'))
    assert response.status_code == 200
    assert FAKE_KEY not in str(response.data)
    assert response.data['document_analysis']['status'] in (
        'not_confirmed', 'unavailable', 'degraded', 'operational', 'operational_with_warnings')
