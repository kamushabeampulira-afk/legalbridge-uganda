"""
Phone number normalisation.

Users type the same Ugandan number in many shapes (0701066872, +256 701 066 872,
256701066872). Phone number is the login credential, so every entry point must
store and look it up in one canonical form: E.164, e.g. +256701066872.
This also matches the format Africa's Talking sends for USSD sessions.
"""
import re

UGANDA_CODE = '256'


def normalize_phone(raw):
    """
    Return the canonical +256XXXXXXXXX form of a Ugandan phone number.

    Separators (spaces, dashes, dots, brackets) are removed. Numbers that do not
    look like Ugandan numbers are returned with separators stripped but otherwise
    unchanged. Values that are not phone numbers at all (e.g. the
    'deleted_<uuid>' placeholder for anonymised accounts) are returned as-is.
    """
    if raw is None:
        return raw
    cleaned = re.sub(r'[\s\-().]', '', str(raw))
    if not re.fullmatch(r'\+?\d+', cleaned):
        return str(raw).strip()
    if cleaned.startswith('00'):
        cleaned = '+' + cleaned[2:]

    if re.fullmatch(r'\+256\d{9}', cleaned):
        return cleaned
    if re.fullmatch(r'256\d{9}', cleaned):
        return '+' + cleaned
    if re.fullmatch(r'0\d{9}', cleaned):
        return '+' + UGANDA_CODE + cleaned[1:]
    if re.fullmatch(r'[1-9]\d{8}', cleaned):
        return '+' + UGANDA_CODE + cleaned
    return cleaned
