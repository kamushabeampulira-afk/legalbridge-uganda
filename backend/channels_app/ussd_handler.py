"""
LegalBridge — USSD session handler.
Processes Africa's Talking USSD webhook requests.
Session state stored in Django cache (configure Redis for production).
"""
import logging
from django.core.cache import cache
from config.languages import LANGUAGE_CODES, normalize_language

from .ussd_menus import MENUS, LANGUAGE_OPTIONS

logger = logging.getLogger('legalbridge')

SESSION_TTL = 300  # 5 minutes — USSD sessions are short-lived


def _session_key(session_id: str) -> str:
    return f'ussd_session_{session_id}'


def _get_session(session_id: str) -> dict:
    return cache.get(_session_key(session_id), {
        'menu': 'main',
        'language': 'en',
        'history': [],
    })


def _save_session(session_id: str, state: dict):
    cache.set(_session_key(session_id), state, timeout=SESSION_TTL)


def _clear_session(session_id: str):
    cache.delete(_session_key(session_id))


def get_session_language(session_id: str) -> str:
    """Return the language currently selected for a USSD session."""
    return normalize_language(_get_session(session_id).get('language'))


def remembered_language(phone_number: str) -> str:
    """The language this phone used on its last call, so callers don't have to pick it again.

    Every call is logged in USSDSession with the language it ended in (see views.py),
    so a caller who chose Runyankore keeps Runyankore until they change it.
    """
    if not phone_number:
        return 'en'
    from .models import USSDSession
    try:
        language = (
            USSDSession.objects.filter(phone_number=phone_number)
            .order_by('-updated_at')
            .values_list('language', flat=True)
            .first()
        )
    except Exception as exc:  # a failed lookup must never block the menu
        logger.warning(f'Could not look up USSD language for caller: {exc}')
        return 'en'
    return normalize_language(language) if language else 'en'


def handle_ussd_request(
    session_id: str,
    service_code: str,
    phone_number: str,
    text: str,
) -> str:
    """
    Main USSD request handler.
    Returns the response string (CON to continue, END to terminate).
    """
    try:
        state = _get_session(session_id)
        current_menu_key = state.get('menu', 'main')
        language = normalize_language(state.get('language'))

        # text is the full input string accumulated across the session
        # e.g. '' = fresh session, '1' = first choice, '1*2' = second choice
        parts = [p.strip() for p in text.split('*') if p.strip()] if text else []
        user_input = parts[-1] if parts else ''

        # Fresh session — always go to main, in the language this phone used last time
        if not text:
            language = remembered_language(phone_number)
            state['menu'] = 'main'
            state['history'] = []
            state['language'] = language
            _save_session(session_id, state)
            return _render_menu('main', language)

        if user_input == '0':
            # Back — pop history. Checked before language selection so 0 also
            # works on the language menu.
            history = state.get('history', [])
            if history:
                prev_menu = history.pop()
                state['history'] = history
                state['menu'] = prev_menu
                _save_session(session_id, state)
                return _render_menu(prev_menu, language)
            else:
                state['menu'] = 'main'
                _save_session(session_id, state)
                return _render_menu('main', language)

        # Handle language change. The menu sends a digit; older sessions may
        # send a __set_lang_<code>__ sentinel directly.
        selected_language = None
        if current_menu_key == 'change_language':
            selected_language = LANGUAGE_OPTIONS.get(user_input)
        if selected_language is None and user_input.startswith('__set_lang_'):
            code = user_input[len('__set_lang_'):-2]
            if code in LANGUAGE_CODES:
                selected_language = code

        if selected_language:
            state['language'] = selected_language
            state['menu'] = 'main'
            _save_session(session_id, state)
            return _render_menu('main', selected_language)

        # Look up the menu definition
        menu = MENUS.get(current_menu_key)
        if not menu:
            logger.warning(f'Unknown menu key: {current_menu_key}')
            _clear_session(session_id)
            return _error_response(language)

        options = menu.get('options', {})

        if user_input not in options:
            # Invalid selection
            return _invalid_selection(current_menu_key, language)

        next_menu_key = options[user_input]

        # Push current to history for back navigation
        history = state.get('history', [])
        history.append(current_menu_key)
        state['history'] = history[-10:]  # cap history depth
        state['menu'] = next_menu_key
        _save_session(session_id, state)

        return _render_menu(next_menu_key, language)

    except Exception as e:
        logger.error(f'USSD handler error (session {session_id}): {e}')
        return "END Sorry, something went wrong. Please try again or use the LegalBridge app."


def _render_menu(menu_key: str, language: str) -> str:
    menu = MENUS.get(menu_key)
    if not menu:
        return "END An error occurred. Please try again."
    return menu.get(language) or menu.get('en', "END Menu not available.")


ERROR_NOTICES = {
    'en': "END An error occurred. Please try again or use the LegalBridge app.",
    'lg': "END Waliwo okusooka. Gezaako nate oba kozesa app ya LegalBridge.",
    'nyn': "END Hariho enshobe ebaireho. Ninkushaba ogyezeho bundi nari okozese app ya LegalBridge.",
    'ach': "END Bal mo otime. Tim ber item odoco onyo itii ki app me LegalBridge.",
    'lgg': "END E'yo azini i 'ye ra. Kirikirisi mi o'bi dika kani ku mi ayu app LegalBridge niri'i",
}

INVALID_NOTICES = {
    'en': "Invalid selection. Please choose from the options below.\n\n",
    'lg': "Londa ennyukuta eziri wansi.\n\n",
    'nyn': "Eki watoorana tikirimu. Ninkushaba otoorane ahansi aha.\n\n",
    'ach': "Yer ni pe atir. Tim ber iyer ki i gin ma piny-ni.\n\n",
    'lgg': "E'yo 'bani pe ri ma okpo yo. Kirikirisi mi pe engazu e'yo 'diyi ma alia elea.\n\n",
}


def _error_response(language: str) -> str:
    return ERROR_NOTICES.get(language, ERROR_NOTICES['en'])


def _invalid_selection(menu_key: str, language: str) -> str:
    base = _render_menu(menu_key, language)
    notice = INVALID_NOTICES.get(language, INVALID_NOTICES['en'])
    # Keep CON/END prefix but insert notice after it
    if base.startswith('CON '):
        return 'CON ' + notice + base[4:]
    return base
