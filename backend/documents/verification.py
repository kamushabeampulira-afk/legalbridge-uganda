"""
LegalBridge: authenticity status and guidance for an uploaded document.

Recognising a document's type is NOT the same as confirming it is genuine.
Logos, stamps, signatures, reference numbers and official wording can all be
copied, so automatic analysis never concludes a document is authentic. The
'verified_official' status is only set by an administrator through a
DocumentVerificationRecord that records the authorised method used.

Guidance never includes phone numbers, websites or officer names: users are
told to obtain the institution's contact details independently.
"""
from __future__ import annotations

from .doc_types import DOC_TYPE_GROUPS

ALWAYS = ('LegalBridge can explain what a document says, but it cannot confirm whether a '
          'document is genuine. A logo, stamp, signature or reference number does not prove '
          'that a document is real.')

INDEPENDENT_CONTACT = ('Get the contact details independently: visit the office in person, or use '
                       'contact details from the institution\'s official channels. Do not rely only '
                       'on phone numbers or names printed on this document.')

ISSUER_GUIDANCE = {
    'police': ('Before acting on it (for example before paying money or reporting at a stated '
               'time), confirm the details with the police station or office named on the '
               'document. Ask them to confirm the reference number, the date and the name of '
               'the officer. '),
    'court': ('Confirm with the registry of the court named on the document that the case '
              'number and hearing date exist. '),
    'local_authority': ('Confirm the notice with the council or authority office named on it before '
                        'paying any money or leaving your trading space. '),
    'market_authority': ('Confirm the notice with the market management office before paying any '
                         'money or leaving your trading space. '),
    'government_agency': 'Confirm the details with the government office named on the document. ',
    'landlord': ('Keep a copy, and ask the landlord to confirm in writing anything that is unclear. '),
}

OFFICIAL_GROUPS = {'traffic', 'police_correspondence', 'police_case', 'court',
                   'local_authority', 'market_trade', 'property'}


def _has(details: dict, key: str) -> bool:
    return (details.get(key) or {}).get('status') in ('found', 'unclear')


def assess_verification(classification: dict, details: dict, text: str) -> tuple[str, str]:
    """Return (verification_status, guidance) for a newly processed document."""
    classification = classification or {}
    details = details or {}

    if not (text or '').strip():
        return 'verification_incomplete', (
            'The document could not be read, so its details could not be checked. Try a clearer, '
            'well-lit photo or a PDF. ' + ALWAYS
        )

    doc_type = classification.get('doc_type', 'unknown')
    group = DOC_TYPE_GROUPS.get(doc_type, 'other')
    issuer_type = (classification.get('issuer') or {}).get('type', 'unknown')
    origin = classification.get('origin', 'unclear')

    if doc_type == 'unknown':
        return 'verification_incomplete', (
            'LegalBridge could not identify what kind of document this is, so it could not check it. '
            'If it affects your rights, show it to a legal aid provider. ' + ALWAYS
        )

    if origin == 'submitted_by_public':
        guidance = ('This appears to be written by a member of the public (for example a complaint), '
                    'not issued by the police or another authority. ')
        if doc_type == 'complaint_to_police':
            guidance += ('If you need proof the police received it, ask the station for a written '
                         'acknowledgement or the reference number your complaint was recorded under. ')
        return 'type_identified', guidance + ALWAYS

    issued_by_institution = issuer_type != 'unknown' or group in OFFICIAL_GROUPS
    if not issued_by_institution:
        return 'type_identified', (
            'Check that the names, amounts and dates match what you agreed or paid. ' + ALWAYS
        )

    guidance = ISSUER_GUIDANCE.get(issuer_type, '')
    if not guidance:
        if group in ('traffic', 'police_correspondence', 'police_case'):
            guidance = ISSUER_GUIDANCE['police']
        else:
            guidance = ('The document does not clearly name who issued it. Ask the person who gave it '
                        'to you which office issued it, then confirm with that office. ')
    if issuer_type != 'landlord':
        guidance += INDEPENDENT_CONTACT + ' '

    action_needed = any(_has(details, k) for k in ('deadlines', 'instructions', 'amounts'))
    status = 'requires_confirmation' if action_needed else 'official_looking_unverified'
    if action_needed:
        guidance = ('This document asks you to do something or sets a deadline or amount. ' + guidance)
    return status, guidance + ALWAYS
