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
def test_whisper_luganda_has_no_language_hint():
    """Whisper has no Luganda code; lg must not be forced to English."""
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
