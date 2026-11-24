"""
LegalBridge: structured detail extraction from document text.

Only reports what is actually present in the extracted text. Every field has:
    {'status': 'found' | 'unclear' | 'not_found', 'value': ..., 'note': str}
'unclear' is used when the OCR confidence is low or the text looks garbled,
so the user is told to check rather than given a guess.
"""
from __future__ import annotations

import re

from .classification import detect_issuer
from .ocr import _extract_amounts, _extract_dates

LOW_OCR_CONFIDENCE = 0.6

MONTHS = (r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|'
          r'sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)')
DATE = rf'(?:\d{{1,2}}[/\-.]\d{{1,2}}[/\-.]\d{{2,4}}|\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS},?\s+\d{{2,4}})'

REFERENCE_PATTERNS = [
    r'\b(?:our\s+)?ref(?:erence)?\.?\s*(?:no\.?|number)?\s*[:#]?\s*([A-Z0-9][A-Z0-9\-/.]{2,})',
    r'\bs\.?d\.?\s*(?:ref|no)\.?\s*[:#]?\s*([0-9][0-9/\-]{3,})',
    r'\bcrb\s*(?:no\.?)?\s*[:#]?\s*([0-9][0-9/\-]{2,})',
    r'\b(?:case|file|notice|ticket|receipt|licen[cs]e|permit)\s+no\.?\s*[:#]?\s*([A-Z0-9][A-Z0-9\-/.]{1,})',
    r'\beps\s*[/#:]?\s*([0-9][0-9/\-]{2,})',
]

# Station names: 1-4 capitalised words on the same line, then "Police Station/Post/Division"
STATION_PATTERN = re.compile(
    r"\b((?:[A-Z][A-Za-z'\-]+[ \t]+){1,4}(?:(?:[Cc]entral|CENTRAL)[ \t]+)?(?:[Pp]olice|POLICE)[ \t]+"
    r"(?:[Ss]tation|STATION|[Pp]ost|POST|[Dd]ivision|DIVISION))\b"
)
OFFICE_PATTERN = re.compile(r'\b(office of the [a-z ,]{3,80})', re.IGNORECASE)

FIELD_LINE_PATTERNS = {
    'recipient': [
        r'^\s*to\s*[:\-]\s*(.+)$',
        r'^\s*(?:name(?: of (?:rider|driver|owner|vendor|tenant|recipient))?|rider|driver|recipient)\s*[:\-]\s*(.+)$',
        r'^\s*(the\s+(?:officer in charge|o/c|district police commander|town clerk|manager)\b.*)$',
        r'^\s*dear\s+(?!sir\b|madam\b|sir/madam\b)(.+?),?\s*$',
    ],
    'subject_or_offence': [
        r'^\s*(?:alleged\s+)?offen[cs]e\s*[:\-]\s*(.+)$',
        r'^\s*(?:re|subject|subj)\s*[:\-.]\s*(.+)$',
        r'^\s*(?:nature of (?:complaint|case|offence))\s*[:\-]\s*(.+)$',
        r'^\s*charge\s*[:\-]\s*(.+)$',
    ],
    'date_of_issue': [
        rf'^\s*(?:date(?: of issue)?|dated|issued on)\s*[:\-]?\s*({DATE})',
    ],
}

DEADLINE_PATTERNS = [
    r'\bwithin\s+(?:\w+\s+)?\(?\d{0,3}\)?\s*(?:days?|weeks?|months?|hours?)\b[^.\n]{0,60}',
    rf'\b(?:on or before|not later than|by|before|no later than)\s+{DATE}',
    rf'\b(?:on|report(?:ing)? on|appear on|hearing (?:on|date)[:\s]*)\s*{DATE}(?:\s+at\s+\d{{1,2}}[:.]\d{{2}}\s*(?:am|pm|hrs)?)?',
    r'\bvalid (?:until|up to)\s+[^.\n]{3,30}',
]

INSTRUCTION_PATTERN = re.compile(
    r'[^.\n]*\b(?:you are (?:hereby )?(?:required|requested|directed|summoned|instructed|ordered)|'
    r'report to|appear before|you must|you should|pay (?:the )?(?:fine|penalty|amount)|'
    r'vacate|bring (?:your|the|along)|produce (?:your|the)|present (?:your|the)|provide the following)'
    r'[^.\n]*',
    re.IGNORECASE,
)

SIGNATURE_STAMP_PATTERN = re.compile(
    r'\b(?:signed|signature|sign\b|stamp(?:ed)?|seal(?:ed)?|official stamp|rubber stamp|'
    r'officer in charge|o/c\b|for:? inspector general|commissioner|town clerk|market master)\b',
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(r'(?:\+?256|\b0)[\s\-]?\d{2,3}[\s\-]?\d{3}[\s\-]?\d{3,4}\b')
EMAIL_PATTERN = re.compile(r'\b[\w.+\-]+@[\w\-]+\.[\w.\-]+\b')
POBOX_PATTERN = re.compile(r'\bP\.?\s?O\.?\s*Box\s*\d+[^\n]{0,30}', re.IGNORECASE)

_TITLE_WORDS = r'(?:[A-Z][a-z]+(?:\s+(?:and|of|the|&)\s+|\s+)){1,8}'
PROVISION_PATTERNS = [
    (r'\b(?:section|sec\.|s\.)\s*\d+[A-Za-z]?(?:\s*\(\s*\w+\s*\))*', re.IGNORECASE),
    (r'\b(?:regulation|reg\.|rule|article)\s*\d+[A-Za-z]?(?:\s*\(\s*\w+\s*\))*', re.IGNORECASE),
    (r'\bcap(?:ter)?\.?\s*\d+\b', re.IGNORECASE),
    # Named Acts/Regulations, Title Case only, e.g. "Traffic and Road Safety Act, Cap 361"
    (rf'\b{_TITLE_WORDS}(?:Act|Regulations)(?:,?\s*(?:Cap\.?\s*\d+|\d{{4}}|No\.?\s*\d+\s+of\s+\d{{4}}))*', 0),
]


def _field(status, value=None, note=''):
    return {'status': status, 'value': value, 'note': note}


def _looks_garbled(value: str) -> bool:
    if not value:
        return False
    clean = re.sub(r'\s', '', value)
    if not clean:
        return False
    odd = sum(1 for c in clean if not (c.isalnum() or c in "/-.,:'()&"))
    return odd / len(clean) > 0.25


def _first_line_match(lines, patterns):
    for ln in lines:
        for p in patterns:
            m = re.match(p, ln, re.IGNORECASE)
            if m:
                return m.group(1).strip(' ,.;:')
    return None


def _uniq(items):
    seen, out = set(), []
    for it in items:
        key = re.sub(r'\s+', ' ', it.strip()).lower()
        if key and key not in seen:
            seen.add(key)
            out.append(re.sub(r'\s+', ' ', it.strip()))
    return out


def extract_document_details(text: str, classification: dict | None = None,
                             ocr_confidence: float | None = None) -> dict:
    """Return the structured details for a document. See module docstring."""
    text = text or ''
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    classification = classification or {}
    low_ocr = ocr_confidence is not None and ocr_confidence < LOW_OCR_CONFIDENCE

    def found(value, note=''):
        if value in (None, '', []):
            return _field('not_found', None, note or 'Not found in the document text.')
        values = value if isinstance(value, list) else [value]
        if low_ocr or any(_looks_garbled(str(v)) for v in values):
            return _field('unclear', value,
                          'The text was hard to read; check this against the original document.')
        return _field('found', value, note)

    details = {}

    # Document type
    doc_type = classification.get('doc_type', 'unknown')
    if doc_type == 'unknown':
        details['document_type'] = _field('unclear' if text.strip() else 'not_found', None,
                                          classification.get('note') or 'The document type could not be identified.')
    else:
        details['document_type'] = _field(
            'found' if classification.get('confidence') in ('high', 'medium') else 'unclear',
            classification.get('label'),
            f"Identified from the wording ({classification.get('confidence', 'low')} confidence).",
        )

    # Issuing institution and office
    issuer = classification.get('issuer') or detect_issuer(text)
    if issuer.get('type') not in (None, 'unknown') and issuer.get('name'):
        details['issuing_institution'] = found(issuer['name'], f"Taken from the {issuer.get('found_in', 'text').replace('_', ' ')}.")
    else:
        details['issuing_institution'] = _field('not_found', None, 'No issuing institution is named in the text.')

    station = STATION_PATTERN.search(text)
    office = OFFICE_PATTERN.search(text)
    office_value = (station.group(1) if station else None) or (office.group(1) if office else None)
    details['issuing_office'] = found(office_value, 'Police station or office named in the document.')

    # Reference numbers
    refs = []
    for p in REFERENCE_PATTERNS:
        refs.extend(m.group(1).strip(' .') for m in re.finditer(p, text, re.IGNORECASE))
    refs = [r for r in _uniq(refs) if re.search(r'\d', r)]
    details['reference_numbers'] = found(refs)

    # Date of issue, recipient, subject/offence
    details['date_of_issue'] = found(_first_line_match(lines, FIELD_LINE_PATTERNS['date_of_issue']))
    details['recipient'] = found(_first_line_match(lines, FIELD_LINE_PATTERNS['recipient']))
    details['subject_or_offence'] = found(_first_line_match(lines, FIELD_LINE_PATTERNS['subject_or_offence']))

    # Dates and deadlines
    deadlines = _uniq(m.group(0) for p in DEADLINE_PATTERNS for m in re.finditer(p, text, re.IGNORECASE))
    details['deadlines'] = found(deadlines, 'Check every deadline against the original document.')
    details['all_dates'] = found(_uniq(_extract_dates(text)))
    details['amounts'] = found(_uniq(_extract_amounts(text)))

    # Instructions / requested actions
    instructions = _uniq(m.group(0).strip(' ,;') for m in INSTRUCTION_PATTERN.finditer(text))
    details['instructions'] = found(instructions[:6])

    # Signatures / stamps: text can only *mention* them; images are not analysed
    marks = _uniq(m.group(0) for m in SIGNATURE_STAMP_PATTERN.finditer(text))
    if marks:
        details['signature_or_stamp'] = _field(
            'unclear', marks[:5],
            'The text mentions a signature, stamp or signing officer. LegalBridge cannot see or '
            'check actual signatures or stamps, and their presence does not prove a document is genuine.',
        )
    else:
        details['signature_or_stamp'] = _field(
            'not_found', None,
            'No signature or stamp is mentioned in the text. Stamps and signatures are images, '
            'so check the original document.',
        )

    # Contact information printed on the document
    contacts = _uniq([m.group(0) for m in PHONE_PATTERN.finditer(text)] +
                     [m.group(0) for m in EMAIL_PATTERN.finditer(text)] +
                     [m.group(0) for m in POBOX_PATTERN.finditer(text)])
    details['contact_information'] = found(
        contacts,
        'Printed on the document itself. Do not use these to check whether the document is genuine; '
        'find the institution\'s contact details independently.',
    ) if contacts else _field('not_found', None, 'No contact details are printed on the document.')

    # Legal provisions mentioned by the document itself
    provisions = _uniq(m.group(0).strip(' ,.') for p, flags in PROVISION_PATTERNS
                       for m in re.finditer(p, text, flags))
    details['legal_provisions_mentioned'] = found(
        provisions,
        'Quoted from the document. LegalBridge has not confirmed these provisions exist or apply.',
    ) if provisions else _field('not_found', None, 'The document does not cite any law.')

    return details
