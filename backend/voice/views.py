"""Voice API views — transcribe audio, synthesize speech."""
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .stt import transcribe_audio
from .tts import synthesize_text

logger = logging.getLogger('legalbridge')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def transcribe_view(request):
    """
    POST /api/voice/transcribe/
    Accepts an audio file (mp3, wav, m4a, webm, ogg).
    Returns transcribed text.
    """
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return Response({'error': 'No audio file provided.'}, status=400)

    max_mb = 25  # Whisper limit
    if audio_file.size > max_mb * 1024 * 1024:
        return Response({'error': f'Audio file must be under {max_mb} MB.'}, status=400)

    allowed_types = [
        'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav',
        'audio/mp4', 'audio/m4a', 'audio/webm', 'audio/ogg',
        'video/webm',  # webm recordings from browsers
    ]
    content_type = (getattr(audio_file, 'content_type', '') or '').split(';')[0].strip().lower()
    if content_type not in allowed_types:
        return Response(
            {'error': 'Unsupported audio format. Please use MP3, WAV, M4A, or WebM.'},
            status=400
        )

    # Whisper infers the container from the filename. Browser recordings are
    # WebM even if a client labels them .m4a — keep the two in sync.
    extension_by_type = {
        'audio/mpeg': '.mp3', 'audio/mp3': '.mp3',
        'audio/wav': '.wav', 'audio/x-wav': '.wav',
        'audio/mp4': '.m4a', 'audio/m4a': '.m4a',
        'audio/webm': '.webm', 'video/webm': '.webm',
        'audio/ogg': '.ogg',
    }
    expected_ext = extension_by_type.get(content_type)
    if expected_ext and not audio_file.name.lower().endswith(expected_ext):
        audio_file.name = f'recording{expected_ext}'

    language = request.data.get('language', request.user.preferred_language or 'en')

    result = transcribe_audio(audio_file, language=language)
    return Response({
        'transcription': result['text'],
        'warning': result.get('warning'),
        'language': language,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def synthesize_view(request):
    """
    POST /api/voice/synthesize/
    Body: { text, language }
    Returns: { audio_url }
    """
    text = request.data.get('text', '').strip()
    language = request.data.get('language', request.user.preferred_language or 'en')

    if not text:
        return Response({'error': 'Text is required.'}, status=400)
    if len(text) > 5000:
        return Response({'error': 'Text is too long for speech synthesis (max 5000 characters).'}, status=400)

    audio_path = synthesize_text(text, language=language)

    if not audio_path:
        return Response({
            'audio_url': None,
            'warning': 'Voice synthesis is not available at this time. Please read the text version.',
        })

    from django.conf import settings
    audio_url = request.build_absolute_uri(settings.MEDIA_URL + audio_path)
    return Response({'audio_url': audio_url, 'language': language})
