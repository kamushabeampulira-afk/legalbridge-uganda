"""
LegalBridge: OpenAI service layer.

Every OpenAI chat request goes through chat_completion(), which:
- refuses to run without an API key (unless AI_DEMO_MODE is explicitly on),
- applies a timeout,
- classifies failures into a fixed set of categories,
- logs the outcome (no content) to AIRequestLog,
- raises AIServiceUnavailable instead of letting callers mistake a failure for a legal answer.

run_connection_check() performs a real, minimal API request and records the result.
API keys are never logged, stored or returned; error messages are sanitised.
"""
from __future__ import annotations

import logging
import re
import time

from django.conf import settings

logger = logging.getLogger('legalbridge')

QUOTA_CODES = {'insufficient_quota', 'credit_balance_exhausted', 'billing_hard_limit_reached',
               'billing_not_active'}

USER_MESSAGES = {
    'missing_key': 'The legal explanation service is not set up yet.',
    'auth_failed': 'The legal explanation service could not sign in to its AI provider.',
    'model_unavailable': 'The AI model used for explanations is not available.',
    'rate_limited': 'The legal explanation service is busy. Please try again in a minute.',
    'quota_billing': 'The legal explanation service is temporarily unavailable (AI usage limit reached).',
    'network_error': 'The legal explanation service could not be reached. Please try again later.',
    'timeout': 'The legal explanation service took too long to respond. Please try again.',
    'invalid_response': 'The legal explanation service returned an unusable response. Please try again.',
    'unknown_error': 'The legal explanation service is temporarily unavailable. Please try again later.',
}

_KEY_PATTERN = re.compile(r'(sk|gsk|xai|key|proj|org)[-_][A-Za-z0-9_\-*]{6,}', re.IGNORECASE)
_GOOGLE_KEY_PATTERN = re.compile(r'AIza[0-9A-Za-z_\-]{20,}')


class AIServiceUnavailable(Exception):
    """Raised when an AI request cannot produce a usable response."""

    def __init__(self, category: str, detail: str = ''):
        self.category = category
        self.detail = sanitize(detail)
        self.user_message = USER_MESSAGES.get(category, USER_MESSAGES['unknown_error'])
        super().__init__(f'{category}: {self.detail}')


def sanitize(text) -> str:
    """Mask anything that looks like an API key and cap the length."""
    if not text:
        return ''
    text = _KEY_PATTERN.sub(lambda m: m.group(1) + '-***', str(text))
    text = _GOOGLE_KEY_PATTERN.sub('AIza-***', text)
    return text[:400]


def _setting(name, default):
    return getattr(settings, name, default)


def is_configured() -> bool:
    return bool(_setting('OPENAI_API_KEY', ''))


def get_client(timeout: float | None = None, max_retries: int | None = None):
    from openai import OpenAI
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=_setting('OPENAI_BASE_URL', '') or None,  # None: OpenAI's own API
        timeout=timeout if timeout is not None else _setting('OPENAI_TIMEOUT_SECONDS', 60),
        max_retries=max_retries if max_retries is not None else _setting('OPENAI_MAX_RETRIES', 1),
    )


def _completion_options(max_tokens: int) -> dict:
    """Output limit plus optional provider settings for thinking models (see settings.py)."""
    options = {'max_tokens': max_tokens + max(0, int(_setting('OPENAI_EXTRA_MAX_TOKENS', 0) or 0))}
    effort = _setting('OPENAI_REASONING_EFFORT', '')
    if effort:
        options['reasoning_effort'] = effort
    return options


def classify_error(exc: Exception) -> tuple[str, str]:
    """Map an exception from the OpenAI SDK to (category, sanitised message)."""
    import openai

    message = sanitize(getattr(exc, 'message', None) or str(exc))
    code = (getattr(exc, 'code', None) or '').lower()
    err_type = (getattr(exc, 'type', None) or '').lower()
    lowered = message.lower()

    if isinstance(exc, openai.APITimeoutError):
        return 'timeout', 'The request timed out.'
    if isinstance(exc, openai.APIConnectionError):
        return 'network_error', 'Could not connect to the API.'
    if isinstance(exc, openai.AuthenticationError):
        return 'auth_failed', message
    if isinstance(exc, openai.RateLimitError):
        if code in QUOTA_CODES or err_type in QUOTA_CODES or any(
                w in lowered for w in ('quota', 'credit', 'billing')):
            return 'quota_billing', message
        return 'rate_limited', message
    if isinstance(exc, openai.NotFoundError):
        return 'model_unavailable', message
    if isinstance(exc, openai.PermissionDeniedError):
        if 'model' in lowered:
            return 'model_unavailable', message
        return 'auth_failed', message
    if isinstance(exc, openai.BadRequestError) and (code == 'model_not_found' or 'model' in code):
        return 'model_unavailable', message
    if isinstance(exc, openai.APIStatusError) and 'api key' in lowered and any(
            w in lowered for w in ('not valid', 'invalid', 'expired')):
        # Google Gemini reports a bad key as HTTP 400 "API key not valid"
        return 'auth_failed', message
    if isinstance(exc, openai.APIStatusError):
        return 'unknown_error', f'HTTP {getattr(exc, "status_code", "?")}: {message}'
    return 'unknown_error', sanitize(f'{type(exc).__name__}: {exc}')


def _log_request(purpose: str, success: bool, category: str = '', latency_ms: int | None = None):
    try:
        from .models import AIRequestLog
        AIRequestLog.objects.create(
            purpose=purpose[:50],
            model_name=_setting('OPENAI_MODEL', '')[:100],
            success=success,
            error_category=category,
            latency_ms=latency_ms,
        )
    except Exception as e:  # logging must never break a user request
        logger.warning(f'Could not record AI request log: {e}')


def chat_completion(system_prompt: str, user_message: str, purpose: str,
                    max_tokens: int = 1500, temperature: float = 0.2) -> str:
    """
    Run one chat completion. Returns the response text, or raises AIServiceUnavailable.
    Never returns placeholder text unless AI_DEMO_MODE is explicitly enabled.
    """
    if not is_configured():
        if _setting('AI_DEMO_MODE', False):
            from .engine import _demo_fallback_response
            return _demo_fallback_response()
        _log_request(purpose, False, 'missing_key')
        raise AIServiceUnavailable('missing_key', 'OPENAI_API_KEY is not set.')

    start = time.monotonic()
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            temperature=temperature,
            **_completion_options(max_tokens),
        )
    except Exception as exc:
        latency = int((time.monotonic() - start) * 1000)
        category, detail = classify_error(exc)
        logger.error(f'OpenAI request failed [{purpose}] {category}: {detail}')
        _log_request(purpose, False, category, latency)
        raise AIServiceUnavailable(category, detail) from None

    latency = int((time.monotonic() - start) * 1000)
    content = None
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        pass
    if not content or not str(content).strip():
        _log_request(purpose, False, 'invalid_response', latency)
        raise AIServiceUnavailable('invalid_response', 'The response contained no text.')

    _log_request(purpose, True, '', latency)
    return content


def run_connection_check(triggered_by=None):
    """
    Test the real OpenAI connection with a minimal request and record an AIHealthCheck.
    The configured model must actually return a valid response for 'operational'.
    """
    from .models import AIHealthCheck

    model = _setting('OPENAI_MODEL', '')
    timeout = _setting('OPENAI_HEALTHCHECK_TIMEOUT_SECONDS', 20)
    slow_ms = _setting('OPENAI_HEALTHCHECK_SLOW_MS', 10000)
    checks = {
        'key_present': is_configured(),
        'key_accepted': None,
        'model_accessible': None,
        'test_request_succeeded': None,
        'response_valid': None,
        'within_time_limit': None,
        'time_limit_ms': slow_ms,
    }

    def record(ai_status, component_status, summary, latency_ms=None):
        return AIHealthCheck.objects.create(
            kind='openai_connection',
            component_status=component_status,
            ai_status=ai_status,
            model_name=model[:100],
            latency_ms=latency_ms,
            summary=sanitize(summary)[:500],
            details=checks,
            triggered_by=triggered_by if getattr(triggered_by, 'pk', None) else None,
        )

    if not checks['key_present']:
        return record('missing_key', 'fail', 'OPENAI_API_KEY is not set in backend/.env.')

    try:
        client = get_client(timeout=timeout, max_retries=0)
    except Exception as exc:
        category, detail = classify_error(exc)
        return record(category, 'fail', f'Could not create the OpenAI client: {detail}')

    # Step 1: is the key accepted, and can it see the configured model? (no tokens used)
    try:
        client.models.retrieve(model)
        checks['key_accepted'] = True
        checks['model_accessible'] = True
    except Exception as exc:
        category, detail = classify_error(exc)
        if category in ('auth_failed', 'network_error', 'timeout'):
            if category == 'auth_failed':
                checks['key_accepted'] = False
            return record(category, 'fail', detail)
        if category == 'model_unavailable':
            # Key works, but the model lookup failed. Confirm with the test request
            # below, since some OpenAI-compatible providers don't implement this lookup.
            checks['key_accepted'] = True
            checks['model_accessible'] = False

    # Step 2: a minimal real completion (a few tokens)
    start = time.monotonic()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'Reply with exactly the word OK.'}],
            temperature=0,
            **_completion_options(5),
        )
    except Exception as exc:
        latency = int((time.monotonic() - start) * 1000)
        category, detail = classify_error(exc)
        checks['test_request_succeeded'] = False
        if category == 'auth_failed':
            checks['key_accepted'] = False
        if category in ('quota_billing', 'rate_limited'):
            checks['key_accepted'] = True
        return record(category, 'fail', detail, latency)

    latency = int((time.monotonic() - start) * 1000)
    checks['test_request_succeeded'] = True
    checks['key_accepted'] = True
    checks['model_accessible'] = True
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        content = None
    checks['response_valid'] = bool(content and str(content).strip())
    checks['within_time_limit'] = latency <= slow_ms

    if not checks['response_valid']:
        return record('invalid_response', 'fail', 'The API answered but returned no text.', latency)
    if not checks['within_time_limit']:
        return record('operational', 'warn',
                      f'Connected, but the test request took {latency} ms (limit {slow_ms} ms).', latency)
    return record('operational', 'pass', f'Connected. Test request answered in {latency} ms.', latency)
