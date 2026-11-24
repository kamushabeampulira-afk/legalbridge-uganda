"""
LegalBridge — Speech-to-Text module.
Providers (STT_PROVIDER): 'openai_whisper' (default) or 'sunbird' (Sunbird AI, free,
with real Luganda support). Luganda STT accuracy note: Whisper has limited Luganda support.
Human-recorded prompts are the fallback for Luganda voice interaction.
"""
import logging
import os
import tempfile
from django.conf import settings

logger = logging.getLogger('legalbridge')

# App language codes -> Sunbird ISO 639-3 codes
SUNBIRD_LANGUAGES = {'en': 'eng', 'lg': 'lug'}
FAILED = {
    'text': '',
    'confidence': None,
    'warning': 'Speech recognition failed. Please type your question instead.',
}


def transcribe_audio(audio_file, language: str = 'en') -> dict:
    """
    Transcribe an audio file.
    audio_file: file-like object or path string
    language: 'en' | 'lg'
    Returns: { 'text': str, 'confidence': float|None, 'warning': str|None }
    """
    provider = settings.STT_PROVIDER

    if provider == 'openai_whisper':
        return _transcribe_whisper(audio_file, language)
    elif provider == 'sunbird':
        return _transcribe_sunbird(audio_file, language)
    else:
        logger.warning(f'Unknown STT provider: {provider}')
        return {
            'text': '',
            'confidence': None,
            'warning': 'Speech recognition is not available. Please type your question instead.',
        }


def _transcribe_whisper(audio_file, language: str) -> dict:
    """Transcribe using OpenAI Whisper API."""
    api_key = getattr(settings, 'VOICE_OPENAI_API_KEY', '')
    if not api_key:
        return {
            'text': '',
            'confidence': None,
            'warning': 'Speech recognition is not configured. Please type your question.',
        }

    # Map language codes to Whisper language hints
    lang_map = {'en': 'en', 'lg': None}  # Whisper has no native Luganda support
    whisper_lang = lang_map.get(language, 'en')

    warning = None
    if language == 'lg':
        warning = (
            'Luganda speech recognition has limited accuracy. '
            'Please check the transcription and correct any errors before submitting.'
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # audio_file may be a Django InMemoryUploadedFile
        kwargs = {
            'model': 'whisper-1',
            'file': audio_file,
        }
        if whisper_lang:
            kwargs['language'] = whisper_lang
        elif language == 'lg':
            # Whisper has no ISO code for Luganda (the API rejects 'lg').
            # A prompt biases it toward Luganda instead of hallucinating English.
            kwargs['prompt'] = 'Yogera mu Luganda: '

        transcript = client.audio.transcriptions.create(**kwargs)
        return {
            'text': transcript.text.strip(),
            'confidence': None,  # Whisper API does not return confidence scores
            'warning': warning,
        }
    except Exception as e:
        logger.error(f'Whisper transcription failed: {e}')
        return dict(FAILED)


def _transcribe_sunbird(audio_file, language: str) -> dict:
    """Transcribe using Sunbird AI (supports English and Luganda natively)."""
    token = getattr(settings, 'SUNBIRD_API_TOKEN', '')
    if not token:
        return {
            'text': '',
            'confidence': None,
            'warning': 'Speech recognition is not configured. Please type your question.',
        }

    url = settings.SUNBIRD_API_URL.rstrip('/') + '/tasks/audio/transcriptions'
    opened = None
    try:
        import requests
        if isinstance(audio_file, (str, os.PathLike)):
            audio_file = opened = open(audio_file, 'rb')
        elif hasattr(audio_file, 'seek'):
            audio_file.seek(0)
        name = os.path.basename(getattr(audio_file, 'name', '') or 'recording.wav')
        content_type = getattr(audio_file, 'content_type', None) or 'application/octet-stream'

        resp = requests.post(
            url,
            headers={'Authorization': f'Bearer {token}'},
            files={'audio': (name, audio_file, content_type)},
            data={'language': SUNBIRD_LANGUAGES.get(language, 'eng')},
            timeout=settings.SUNBIRD_TIMEOUT_SECONDS,
        )
        if resp.status_code != 200:
            logger.error(f'Sunbird transcription failed: HTTP {resp.status_code}: {resp.text[:300]}')
            return dict(FAILED)
        text = (resp.json().get('audio_transcription') or '').strip()
    except Exception as e:
        logger.error(f'Sunbird transcription failed: {type(e).__name__}: {e}')
        return dict(FAILED)
    finally:
        if opened:
            opened.close()

    if not text:
        return {
            'text': '',
            'confidence': None,
            'warning': 'No speech was recognised. Please try again or type your question.',
        }
    return {
        'text': text,
        'confidence': None,  # Sunbird does not return a confidence score
        'warning': None,
    }
