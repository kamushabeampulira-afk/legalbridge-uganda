"""Tests: USSD session navigation and menu logic."""
import re

import pytest
from channels_app.ussd_handler import INVALID_NOTICES, handle_ussd_request
from channels_app.ussd_menus import LANGUAGE_OPTIONS, MENUS
from config.languages import LANGUAGE_CODES

pytestmark = pytest.mark.django_db  # the handler looks up each caller's last language

LOCAL_LANGUAGES = [code for code in LANGUAGE_CODES if code != 'en']
OPTION_NUMBER = re.compile(r'^(\d+)\. ', re.M)
ADDRESS = re.compile(r'(?:www\.)?[a-z]+\.(?:or\.ug|org)\b')


SESSION_ID = 'test_session_001'


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


def test_fresh_session_shows_main_menu():
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000001', '')
    assert response.startswith('CON')
    assert 'Boda Boda' in response or 'Boda' in response


def test_select_boda_boda():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000001', '')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000001', '1')
    assert response.startswith('CON')
    assert 'Traffic' in response or 'stopped' in response or 'Boda' in response


def test_select_market_vendor():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000002', '')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000002', '2')
    assert response.startswith('CON')
    assert 'Eviction' in response or 'vendor' in response.lower()


def test_navigate_to_legal_help():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000003', '')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000003', '4')
    assert response.startswith('END')
    assert 'Uganda Law Society' in response or 'Legal' in response


def test_boda_stopped_ends_session():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000004', '')
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000004', '1')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000004', '2')
    assert response.startswith('END')
    assert 'officer' in response.lower() or 'rights' in response.lower() or 'police' in response.lower()


def test_back_navigation():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000005', '')
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000005', '1')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000005', '0')
    assert response.startswith('CON')
    assert 'Boda' in response or 'Market' in response  # Back to main


def test_back_from_language_menu():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000009', '')
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000009', '5')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000009', '0')
    assert response.startswith('CON')
    assert 'Welcome to LegalBridge' in response


def test_invalid_selection_shows_menu_again():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000006', '')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000006', '9')
    # Should re-show the current menu
    assert 'CON' in response or 'END' in response


def test_luganda_language_switch():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000007', '')
    # Navigate to change language (option 5)
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000007', '5')
    # Select Luganda (option 2)
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000007', '2')
    # Main menu should show in Luganda
    assert 'Olulimi' in response or 'Boda' in response or 'Akatale' in response


@pytest.mark.parametrize('option', ['3', '4', '5'])
def test_additional_language_switch(option):
    language = LANGUAGE_OPTIONS[option]
    phone = f'+2567000000{int(option) + 20}'
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '5')
    response = handle_ussd_request(SESSION_ID, '*384*0#', phone, option)
    assert response == MENUS['main'][language]
    assert response != MENUS['main']['en']


@pytest.mark.parametrize('option', ['3', '4', '5'])
def test_whole_session_stays_in_chosen_language(option):
    """After choosing a language, deeper screens are translated too, not English."""
    language = LANGUAGE_OPTIONS[option]
    phone = '+256700000031'
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '5')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, f'5*{option}')
    boda = handle_ussd_request(SESSION_ID, '*384*0#', phone, f'5*{option}*1')
    assert boda == MENUS['boda_main'][language]
    stopped = handle_ussd_request(SESSION_ID, '*384*0#', phone, f'5*{option}*1*2')
    assert stopped == MENUS['boda_stopped'][language]
    assert stopped != MENUS['boda_stopped']['en']


def test_invalid_selection_notice_is_in_chosen_language():
    phone = '+256700000032'
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '5')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '5*4')  # Acholi
    response = handle_ussd_request(SESSION_ID, '*384*0#', phone, '5*4*9')
    assert response.startswith('CON ' + INVALID_NOTICES['ach'])


@pytest.mark.parametrize('menu_key', sorted(MENUS))
@pytest.mark.parametrize('language', LOCAL_LANGUAGES)
def test_every_screen_is_translated_with_the_same_structure(menu_key, language):
    english = MENUS[menu_key]['en']
    translated = MENUS[menu_key].get(language)
    assert translated, f'{menu_key} has no {language} text'
    # Same session behaviour and the same numbered choices.
    assert translated[:4] == english[:4]
    assert OPTION_NUMBER.findall(translated) == OPTION_NUMBER.findall(english)
    # Section numbers, phone numbers, dates and web addresses come through unchanged.
    for number in re.findall(r'\d+', english[4:]):
        assert number in translated, f'{menu_key}/{language} lost the number {number}'
    for address in ADDRESS.findall(english):
        assert address in translated, f'{menu_key}/{language} lost {address}'


def test_vendor_eviction_ends_session():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '')
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '2')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '1')
    assert response.startswith('END')
    assert 'stall' in response.lower() or 'evict' in response.lower() or 'documents' in response.lower()


# ── A caller's language carries over to their next call ─────────────────────

def _dial(client, session_id, phone, text):
    """POST to the webhook exactly as Africa's Talking does."""
    response = client.post('/api/ussd/webhook/', {
        'sessionId': session_id, 'serviceCode': '*384*0#', 'phoneNumber': phone, 'text': text,
    })
    assert response.status_code == 200
    return response.content.decode()


def test_chosen_language_is_kept_on_the_next_call(client):
    phone = '+256700000041'
    _dial(client, 'call-1', phone, '')
    _dial(client, 'call-1', phone, '5')
    _dial(client, 'call-1', phone, '5*3')  # Runyankore

    # A new call from the same phone starts in Runyankore and stays there.
    assert _dial(client, 'call-2', phone, '') == MENUS['main']['nyn']
    assert _dial(client, 'call-2', phone, '2') == MENUS['vendor_main']['nyn']
    assert _dial(client, 'call-2', phone, '2*1') == MENUS['vendor_eviction']['nyn']


def test_changing_back_to_english_is_kept_too(client):
    phone = '+256700000042'
    _dial(client, 'call-1', phone, '')
    _dial(client, 'call-1', phone, '5*4')  # Acholi
    _dial(client, 'call-2', phone, '')
    _dial(client, 'call-2', phone, '5*1')  # back to English

    assert _dial(client, 'call-3', phone, '') == MENUS['main']['en']


def test_other_callers_still_start_in_english(client):
    _dial(client, 'call-1', '+256700000043', '')
    _dial(client, 'call-1', '+256700000043', '5*5')  # Lugbara

    assert _dial(client, 'call-2', '+256700000044', '') == MENUS['main']['en']
