"""
LegalBridge — Text-to-Speech module.
Supports OpenAI TTS and ElevenLabs. Modular: swap provider without breaking the app.
"""
from __future__ import annotations
import logging
import os
import uuid
from pathlib import Path
from django.conf import settings

logger = logging.getLogger('legalbridge')

AUDIO_DIR = Path(settings.MEDIA_ROOT) / 'audio'


def synthesize_text(text: str, language: str = 'en') -> str | None:
    """
    Convert text to speech. Returns the relative media path of the audio file,
    or None if synthesis fails.
    language: 'en' | 'lg'
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    provider = settings.TTS_PROVIDER

    if provider == 'elevenlabs':
        return _synthesize_elevenlabs(text, language)
    elif provider == 'openai':
        return _synthesize_openai(text, language)
    else:
        logger.warning(f'Unknown TTS provider: {provider}. Voice synthesis skipped.')
        return None


def _synthesize_openai(text: str, language: str) -> str | None:
    """Use OpenAI TTS (supports English well; Luganda limited)."""
    if not settings.OPENAI_API_KEY:
        logger.warning('OpenAI API key not configured. Skipping TTS.')
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        voice = 'alloy'  # Neutral voice; can be configured per language
        filename = f'tts_{uuid.uuid4()}.mp3'
        filepath = AUDIO_DIR / filename

        response = client.audio.speech.create(
            model='tts-1',
            voice=voice,
            input=text[:4096],  # OpenAI TTS limit
        )
        response.stream_to_file(str(filepath))
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

    voice_id = settings.ELEVENLABS_VOICE_LG if language == 'lg' else settings.ELEVENLABS_VOICE_EN
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
