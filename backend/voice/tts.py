"""
LegalBridge — Text-to-Speech module.
Supports OpenAI TTS, ElevenLabs and Sunbird AI (free; English and Luganda voices).
Modular: swap provider (TTS_PROVIDER) without breaking the app.
"""
from __future__ import annotations
import logging
import os
import re
import uuid
from pathlib import Path
from django.conf import settings

logger = logging.getLogger('legalbridge')

AUDIO_DIR = Path(settings.MEDIA_ROOT) / 'audio'


def synthesize_text(text: str, language: str = 'en') -> str | None:
    """
    Convert text to speech. Returns the relative media path of the audio file,
    or None if synthesis fails.
    language: one of config.languages.LANGUAGE_CODES
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    provider = settings.TTS_PROVIDER
    text = speakable_text(text, getattr(settings, 'TTS_MAX_CHARS', 4096) or 4096)
    if not text:
        return None

    if provider == 'elevenlabs':
        return _synthesize_elevenlabs(text, language)
    elif provider == 'openai':
        return _synthesize_openai(text, language)
    elif provider == 'sunbird':
        return _synthesize_sunbird(text, language)
    else:
        logger.warning(f'Unknown TTS provider: {provider}. Voice synthesis skipped.')
        return None


def speakable_text(text: str, max_chars: int) -> str:
    """Remove Markdown symbols a voice would read aloud, and cut long text at a sentence end."""
    text = re.sub(r'^\s*(?:[-•]|\d+\.)\s+', '', text or '', flags=re.M)  # list markers
    text = re.sub(r'[*_`#>|]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    end = max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
    return cut[:end + 1] if end >= max_chars // 2 else cut.rsplit(' ', 1)[0]


def _synthesize_openai(text: str, language: str) -> str | None:
    """OpenAI TTS, or an OpenAI-compatible provider (e.g. Groq) via VOICE_OPENAI_BASE_URL."""
    api_key = getattr(settings, 'VOICE_OPENAI_API_KEY', '')
    if not api_key:
        logger.warning('OpenAI voice key (VOICE_OPENAI_API_KEY) not configured. Skipping TTS.')
        return None
    languages = [code.strip() for code in (getattr(settings, 'TTS_OPENAI_LANGUAGES', '') or '').split(',')
                 if code.strip()]
    if languages and language not in languages:
        logger.info(f'TTS voice does not support language {language!r}. Voice synthesis skipped.')
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=getattr(settings, 'VOICE_OPENAI_BASE_URL', '') or None)

        audio_format = getattr(settings, 'TTS_OPENAI_FORMAT', '') or 'mp3'
        filename = f'tts_{uuid.uuid4()}.{audio_format}'
        filepath = AUDIO_DIR / filename

        response = client.audio.speech.create(
            model=getattr(settings, 'TTS_OPENAI_MODEL', '') or 'tts-1',
            voice=getattr(settings, 'TTS_OPENAI_VOICE', '') or 'alloy',
            input=text,
            response_format=audio_format,
        )
        response.write_to_file(str(filepath))
        return f'audio/{filename}'
    except Exception as e:
        logger.error(f'OpenAI TTS failed: {e}')
        return None


def _synthesize_elevenlabs(text: str, language: str) -> str | None:
    """Use ElevenLabs TTS."""
    api_key = settings.ELEVENLABS_API_KEY
    if not api_key:
        logger.warning('ElevenLabs API key not configured. Skipping TTS.')
        return None

    voice_ids = {
        'en': settings.ELEVENLABS_VOICE_EN,
        'lg': settings.ELEVENLABS_VOICE_LG,
        'nyn': settings.ELEVENLABS_VOICE_NYN,
        'ach': settings.ELEVENLABS_VOICE_ACH,
        'lgg': settings.ELEVENLABS_VOICE_LGG,
    }
    voice_id = voice_ids.get(language)
    if not voice_id:
        logger.warning(f'No ElevenLabs voice ID configured for language: {language}')
        return None

    try:
        import requests
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        headers = {
            'xi-api-key': api_key,
            'Content-Type': 'application/json',
        }
        payload = {
            'text': text[:5000],
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75},
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()

        filename = f'tts_{uuid.uuid4()}.mp3'
        filepath = AUDIO_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        return f'audio/{filename}'
    except Exception as e:
        logger.error(f'ElevenLabs TTS failed: {e}')
        return None


def _synthesize_sunbird(text: str, language: str) -> str | None:
    """Use Sunbird AI TTS. Returns the audio as a file in media/audio/."""
    token = getattr(settings, 'SUNBIRD_API_TOKEN', '')
    if not token:
        logger.warning('Sunbird API token (SUNBIRD_API_TOKEN) not configured. Skipping TTS.')
        return None

    payload = {
        'text': text,
        'language': 'lug' if language == 'lg' else 'eng',
        'response_mode': 'stream',  # audio bytes in the response, nothing stored at Sunbird
    }
    voice = settings.SUNBIRD_TTS_VOICE_LG if language == 'lg' else settings.SUNBIRD_TTS_VOICE_EN
    if voice:
        payload['voice'] = voice

    try:
        import requests
        resp = requests.post(
            settings.SUNBIRD_API_URL.rstrip('/') + '/tasks/audio/speech',
            json=payload,
            headers={'Authorization': f'Bearer {token}'},
            timeout=settings.SUNBIRD_TIMEOUT_SECONDS,
        )
        content_type = resp.headers.get('Content-Type', '').lower()
        if resp.status_code != 200 or 'json' in content_type or not resp.content:
            detail = resp.text[:300] if 'json' in content_type else f'content type {content_type!r}'
            logger.error(f'Sunbird TTS failed: HTTP {resp.status_code}: {detail}')
            return None

        extension = '.mp3' if 'mpeg' in content_type or 'mp3' in content_type else '.wav'
        filename = f'tts_{uuid.uuid4()}{extension}'
        with open(AUDIO_DIR / filename, 'wb') as f:
            f.write(resp.content)
        return f'audio/{filename}'
    except Exception as e:
        logger.error(f'Sunbird TTS failed: {type(e).__name__}: {e}')
        return None
