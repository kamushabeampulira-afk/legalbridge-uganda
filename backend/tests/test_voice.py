"""Tests: voice transcription and synthesis endpoints."""
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import MagicMock, patch

User = get_user_model()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        phone_number='+256700300001',
        password='testpass123',
        user_type='market_vendor',
        preferred_language='lg',
        consented_to_processing=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def audio_upload(name='recording.m4a', content_type='audio/m4a'):
    return SimpleUploadedFile(name, b'fake-audio-payload', content_type=content_type)


@pytest.mark.django_db
def test_transcribe_requires_auth():
    response = APIClient().post(reverse('voice_transcribe'), {'audio': audio_upload()})
    assert response.status_code == 401


@pytest.mark.django_db
def test_transcribe_returns_text_and_warning(auth_client):
    client, _ = auth_client
    with patch('voice.views.transcribe_audio', return_value={
        'text': 'Ndi ne ssawa ssatu',
        'confidence': None,
        'warning': 'Luganda speech recognition has limited accuracy.',
    }):
        response = client.post(reverse('voice_transcribe'), {
            'audio': audio_upload(),
            'language': 'lg',
        })

    assert response.status_code == 200
    assert response.data['transcription'] == 'Ndi ne ssawa ssatu'
    assert response.data['language'] == 'lg'
    assert 'limited accuracy' in response.data['warning']


@pytest.mark.django_db
def test_transcribe_returns_warning_when_stt_unavailable(auth_client):
    client, _ = auth_client
    with patch('voice.views.transcribe_audio', return_value={
        'text': '', 'confidence': None, 'warning': 'Please type your question.',
    }):
        response = client.post(reverse('voice_transcribe'), {
            'audio': audio_upload(), 'language': 'en',
        })

    assert response.status_code == 200
    assert response.data['transcription'] == ''
    assert response.data['warning'] == 'Please type your question.'


@pytest.mark.django_db
def test_transcribe_rejects_unsupported_format(auth_client):
    client, _ = auth_client
    response = client.post(reverse('voice_transcribe'), {
        'audio': audio_upload(name='notes.txt', content_type='text/plain'),
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_transcribe_normalises_webm_filename(auth_client):
    """Browser WebM must reach Whisper as .webm, even if labelled .m4a."""
    client, _ = auth_client
    with patch('voice.views.transcribe_audio') as mock_stt:
        mock_stt.return_value = {'text': 'ok', 'confidence': None, 'warning': None}
        client.post(reverse('voice_transcribe'), {
            'audio': audio_upload(name='recording.m4a', content_type='audio/webm;codecs=opus'),
            'language': 'en',
        })

    uploaded = mock_stt.call_args[0][0]
    assert uploaded.name.endswith('.webm')


@pytest.mark.django_db
def test_whisper_luganda_has_no_language_hint(settings):
    """Whisper has no Luganda code; lg must not be forced to English."""
    settings.STT_PROVIDER = 'openai_whisper'
    settings.VOICE_OPENAI_API_KEY = 'sk-test-voice-key-123456'
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = MagicMock(text=' kintu ')
    with patch('openai.OpenAI', return_value=mock_client):
        from voice.stt import transcribe_audio
        result = transcribe_audio(audio_upload(), language='lg')

    kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
    assert 'language' not in kwargs
    assert kwargs['prompt'] == 'Yogera mu Luganda: '
    assert kwargs['model'] == 'whisper-1'
    assert result['text'] == 'kintu'
    assert result['warning'] is not None


@pytest.mark.django_db
def test_synthesize_returns_warning_when_no_audio(auth_client):
    client, _ = auth_client
    with patch('voice.views.synthesize_text', return_value=None):
        response = client.post(reverse('voice_synthesize'), {
            'text': 'Kale', 'language': 'lg',
        }, format='json')

    assert response.status_code == 200
    assert response.data['audio_url'] is None
    assert 'warning' in response.data


@pytest.mark.django_db
def test_synthesize_returns_media_url(auth_client):
    client, _ = auth_client
    with patch('voice.views.synthesize_text', return_value='audio/tts_demo.mp3'):
        response = client.post(reverse('voice_synthesize'), {
            'text': 'Hello', 'language': 'en',
        }, format='json')

    assert response.status_code == 200
    assert response.data['audio_url'].endswith('/media/audio/tts_demo.mp3')


# ── Sunbird AI (network always mocked) ───────────────────────────────────────

SUNBIRD_TOKEN = 'sunbird-test-token-123'


@pytest.fixture
def sunbird(settings):
    settings.STT_PROVIDER = 'sunbird'
    settings.TTS_PROVIDER = 'sunbird'
    settings.SUNBIRD_API_TOKEN = SUNBIRD_TOKEN
    settings.SUNBIRD_API_URL = 'https://api.sunbird.ai'
    settings.SUNBIRD_TTS_VOICE_EN = ''
    settings.SUNBIRD_TTS_VOICE_LG = 'Kato'
    return settings


def http_response(status=200, json_data=None, content=b'', content_type='application/json'):
    resp = MagicMock(status_code=status, content=content, headers={'Content-Type': content_type})
    resp.json.return_value = json_data or {}
    resp.text = str(json_data)
    return resp


@pytest.mark.parametrize('language,code', [('lg', 'lug'), ('en', 'eng')])
def test_sunbird_transcription(sunbird, language, code):
    from voice.stt import transcribe_audio
    reply = http_response(json_data={'audio_transcription': ' Nnina ekizibu ku katale ', 'language': code})
    with patch('requests.post', return_value=reply) as post:
        result = transcribe_audio(audio_upload(), language=language)

    assert result == {'text': 'Nnina ekizibu ku katale', 'confidence': None, 'warning': None}
    args, kwargs = post.call_args
    assert args[0] == 'https://api.sunbird.ai/tasks/audio/transcriptions'
    assert kwargs['headers'] == {'Authorization': f'Bearer {SUNBIRD_TOKEN}'}
    assert kwargs['data'] == {'language': code}
    assert kwargs['files']['audio'][0] == 'recording.m4a'


def test_sunbird_transcription_without_token_asks_to_type(sunbird):
    from voice.stt import transcribe_audio
    sunbird.SUNBIRD_API_TOKEN = ''
    with patch('requests.post') as post:
        result = transcribe_audio(audio_upload(), language='lg')
    post.assert_not_called()
    assert result['text'] == '' and 'type your question' in result['warning']


def test_sunbird_transcription_http_error_is_reported(sunbird):
    from voice.stt import transcribe_audio
    with patch('requests.post', return_value=http_response(429, {'detail': 'Too many requests'})):
        result = transcribe_audio(audio_upload(), language='en')
    assert result['text'] == '' and 'failed' in result['warning']


def test_sunbird_synthesis_saves_audio(sunbird, tmp_path):
    from voice import tts
    reply = http_response(content=b'RIFF-fake-wav', content_type='audio/wav')
    with patch.object(tts, 'AUDIO_DIR', tmp_path), patch('requests.post', return_value=reply) as post:
        path = tts.synthesize_text('Oli otya', language='lg')

    assert path.startswith('audio/tts_') and path.endswith('.wav')
    assert (tmp_path / path.split('/', 1)[1]).read_bytes() == b'RIFF-fake-wav'
    args, kwargs = post.call_args
    assert args[0] == 'https://api.sunbird.ai/tasks/audio/speech'
    assert kwargs['json'] == {'text': 'Oli otya', 'language': 'lug', 'response_mode': 'stream', 'voice': 'Kato'}


def test_sunbird_synthesis_error_returns_none(sunbird, tmp_path):
    from voice import tts
    reply = http_response(422, {'detail': 'invalid voice'})
    with patch.object(tts, 'AUDIO_DIR', tmp_path), patch('requests.post', return_value=reply):
        assert tts.synthesize_text('Hello', language='en') is None
    assert not any(tmp_path.iterdir())
