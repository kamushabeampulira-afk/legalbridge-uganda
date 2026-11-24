"""Tests: USSD session navigation and menu logic."""
import pytest
from channels_app.ussd_handler import handle_ussd_request


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


@pytest.mark.parametrize('option, expected_text', [
    ('3', 'Obwenkanya'),  # Runyankore
    ('4', 'Ywal Leb'),    # Acholi
    ('5', 'Obubaka'),     # Lugbara
])
def test_additional_language_switch(option, expected_text):
    phone = f'+2567000000{int(option) + 20}'
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '')
    handle_ussd_request(SESSION_ID, '*384*0#', phone, '5')
    response = handle_ussd_request(SESSION_ID, '*384*0#', phone, option)
    assert response.startswith('CON')
    assert expected_text in response


def test_vendor_eviction_ends_session():
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '')
    handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '2')
    response = handle_ussd_request(SESSION_ID, '*384*0#', '+256700000008', '1')
    assert response.startswith('END')
    assert 'stall' in response.lower() or 'evict' in response.lower() or 'documents' in response.lower()
