"""Which speech provider handles each language.

Sunbird AI understands and speaks Luganda well but takes 25-40 seconds per
request; Groq (an OpenAI-compatible provider) answers English in a few seconds.
SUNBIRD_VOICE_LANGUAGES lists the app languages that always use Sunbird, e.g.
"lg"; every other language uses STT_PROVIDER / TTS_PROVIDER.
"""
from django.conf import settings


def sunbird_voice_languages() -> set:
    raw = getattr(settings, 'SUNBIRD_VOICE_LANGUAGES', '') or ''
    return {code.strip() for code in raw.split(',') if code.strip()}


def provider_for(language: str, default: str) -> str:
    """'sunbird' for languages in SUNBIRD_VOICE_LANGUAGES (when a token is set), else the default."""
    if language in sunbird_voice_languages() and getattr(settings, 'SUNBIRD_API_TOKEN', ''):
        return 'sunbird'
    return default
