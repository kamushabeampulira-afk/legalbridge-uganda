"""
LegalBridge — Speech-to-Text module.
Uses OpenAI Whisper by default. Modular for future provider swaps.
Local-language STT note: Whisper reliably supports English only. Luganda,
Runyankore, Acholi and Lugbara are auto-detected and always return a warning
asking the user to check the transcription.
"""
import logging
import os
import tempfile
from django.conf import settings

from config.languages import SUPPORTED_LANGUAGES

logger = logging.getLogger('legalbridge')


def transcribe_audio(audio_file, language: str = 'en') -> dict:
    """
    Transcribe an audio file.
    audio_file: file-like object or path string
    language: one of config.languages.LANGUAGE_CODES
    Returns: { 'text': str, 'confidence': float|None, 'warning': str|None }
    """
    provider = settings.STT_PROVIDER

    if provider == 'openai_whisper':
        return _transcribe_whisper(audio_file, language)
    else:
        logger.warning(f'Unknown STT provider: {provider}')
        return {
            'text': '',
            'confidence': None,
            'warning': 'Speech recognition is not available. Please type your question instead.',
        }


def _transcribe_whisper(audio_file, language: str) -> dict:
    """Transcribe using OpenAI Whisper API."""
    if not settings.OPENAI_API_KEY:
        return {
            'text': '',
            'confidence': None,
            'warning': 'Speech recognition is not configured. Please type your question.',
        }

    # Only English has a reliable Whisper hint. Other supported languages are
    # auto-detected (no hint) and always return a transcription warning.
    whisper_lang = 'en' if language == 'en' else None

    warning = None
    if language != 'en':
        warning = (
            f'Speech recognition for {SUPPORTED_LANGUAGES.get(language, language)} has limited accuracy. '
            'Please check the transcription and correct any errors before submitting.'
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # audio_file may be a Django InMemoryUploadedFile
        kwargs = {
            'model': 'whisper-1',
            'file': audio_file,
        }
        if whisper_lang:
            kwargs['language'] = whisper_lang

        transcript = client.audio.transcriptions.create(**kwargs)
        return {
            'text': transcript.text.strip(),
            'confidence': None,  # Whisper API does not return confidence scores
            'warning': warning,
        }
    except Exception as e:
        logger.error(f'Whisper transcription failed: {e}')
        return {
            'text': '',
            'confidence': None,
            'warning': f'Speech recognition failed. Please type your question instead.',
        }
