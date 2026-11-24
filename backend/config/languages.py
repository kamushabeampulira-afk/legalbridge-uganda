"""
Shared supported-language registry for LegalBridge.

Codes are ISO 639-1 where available ('en', 'lg') and ISO 639-3 otherwise
('nyn' Runyankore, 'ach' Acholi, 'lgg' Lugbara). The same codes are used by
the mobile app and the Africa's Talking USSD menus.
"""

DEFAULT_LANGUAGE = 'en'

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'lg': 'Luganda',
    'nyn': 'Runyankore',
    'ach': 'Acholi',
    'lgg': 'Lugbara',
}

LANGUAGE_CODES = tuple(SUPPORTED_LANGUAGES.keys())

LANGUAGE_CHOICES = [(code, name) for code, name in SUPPORTED_LANGUAGES.items()]


def is_supported_language(value) -> bool:
    return isinstance(value, str) and value in SUPPORTED_LANGUAGES


def normalize_language(value, default: str = DEFAULT_LANGUAGE) -> str:
    """Return a supported code, falling back to the default for unknown values."""
    return value if is_supported_language(value) else default


def validated_language(value, default: str = DEFAULT_LANGUAGE):
    """
    Validate a request-supplied language.
    Returns (language_code, is_valid). Empty values use the default and are valid.
    """
    if value in (None, ''):
        return default, True
    if is_supported_language(value):
        return value, True
    return default, False
