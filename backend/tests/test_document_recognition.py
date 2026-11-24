"""Tests: document classification, detail extraction, authenticity status,
legal-source currency checks and the safeguards applied to AI explanations."""
import re
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ai_engine.engine import (
    AUTH_REPLACEMENT, UNCERTAINTY_SENTENCE, _remove_authenticity_claims, build_document_explanation,
)
from ai_engine.openai_service import AIServiceUnavailable
from documents.classification import classify_document
from documents.extraction import extract_document_details
from documents.models import Document, DocumentAnalysis, DocumentVerificationRecord
from documents.samples import SAMPLE_DOCUMENTS
from documents.verification import assess_verification
from legal_data.models import LegalSource
from legal_data.vector_store import _refresh_from_database

User = get_user_model()
SAMPLES = dict(SAMPLE_DOCUMENTS)


# ── Classification ───────────────────────────────────────────────────────────

@pytest.mark.parametrize('expected,text', SAMPLE_DOCUMENTS, ids=[e for e, _ in SAMPLE_DOCUMENTS])
def test_classifies_sample_documents(expected, text):
    assert classify_document(text)['doc_type'] == expected


def test_complaint_to_police_is_not_treated_as_police_issued():
    result = classify_document(SAMPLES['complaint_to_police'])
    assert result['origin'] == 'submitted_by_public'
    assert result['issuer']['type'] == 'unknown'          # the police are the addressee, not the issuer
    assert result['issuer']['addressed_to']['type'] == 'police'


def test_police_acknowledgement_is_police_issued():
    result = classify_document(SAMPLES['police_complaint_ack'])
    assert result['origin'] == 'issued_by_institution'
    assert result['issuer']['type'] == 'police'


def test_unrelated_text_is_not_forced_into_a_category():
    assert classify_document('Minutes of the family meeting about the wedding budget.')['doc_type'] == 'unknown'
    assert classify_document('')['doc_type'] == 'unknown'


def test_police_letter_fallback_for_unrecognised_police_correspondence():
    text = 'UGANDA POLICE FORCE\nSAMPLE POLICE STATION\nDear Sir,\nRE: YOUR LETTER\nYours faithfully'
    assert classify_document(text)['doc_type'] == 'police_letter'


def test_classification_explains_itself():
    result = classify_document(SAMPLES['police_bond'])
    assert result['signals'] and result['confidence'] in ('high', 'medium')


# ── Detail extraction ────────────────────────────────────────────────────────

def test_extracts_police_summons_details():
    text = SAMPLES['police_summons']
    d = extract_document_details(text, classify_document(text), ocr_confidence=0.95)
    assert d['document_type']['status'] == 'found'
    assert 'POLICE' in d['issuing_institution']['value'].upper()
    assert d['issuing_office']['value'].lower() == 'sample police station'
    assert any('SPS/GEN/000/2026' in r for r in d['reference_numbers']['value'])
    assert d['date_of_issue']['value'] == '04/02/2026'
    assert 'John Example' in d['recipient']['value']
    assert 'REQUEST TO REPORT' in d['subject_or_offence']['value']
    assert any('06/02/2026' in x for x in d['deadlines']['value'])
    assert any('required to report' in x.lower() for x in d['instructions']['value'])


def test_signatures_and_stamps_are_never_reported_as_confirmed():
    for _expected, text in SAMPLE_DOCUMENTS:
        d = extract_document_details(text, classify_document(text), 0.95)
        assert d['signature_or_stamp']['status'] in ('unclear', 'not_found')


def test_low_ocr_confidence_marks_fields_unclear():
    text = SAMPLES['police_summons']
    d = extract_document_details(text, classify_document(text), ocr_confidence=0.3)
    assert d['reference_numbers']['status'] == 'unclear'
    assert d['recipient']['status'] == 'unclear'


def test_missing_fields_are_marked_not_found_not_guessed():
    text = 'OFFICIAL RECEIPT\nReceived from: Jane Example\nAmount paid: UGX 10,000'
    d = extract_document_details(text, classify_document(text), 0.95)
    assert d['issuing_office']['status'] == 'not_found'
    assert d['issuing_office']['value'] is None


def test_extracts_cited_provisions_and_contacts_with_caveats():
    text = ('TRAFFIC OFFENCE NOTICE\nContrary to Section 130 of the Traffic and Road Safety Act, Cap 361\n'
            'Enquiries: 0700 000 000, P.O. Box 000 Sample Town')
    d = extract_document_details(text, classify_document(text), 0.95)
    provisions = ' | '.join(d['legal_provisions_mentioned']['value'])
    assert 'Section 130' in provisions and 'Traffic and Road Safety Act, Cap 361' in provisions
    assert 'not confirmed' in d['legal_provisions_mentioned']['note']
    assert 'independently' in d['contact_information']['note']


# ── Authenticity status ──────────────────────────────────────────────────────

def _assess(text):
    c = classify_document(text)
    return assess_verification(c, extract_document_details(text, c, 0.95), text)


def test_automatic_analysis_never_marks_a_document_verified():
    for _expected, text in SAMPLE_DOCUMENTS:
        status, guidance = _assess(text)
        assert status != 'verified_official'
        assert 'cannot confirm whether a document is genuine' in guidance


def test_verification_statuses():
    assert _assess(SAMPLES['police_summons'])[0] == 'requires_confirmation'
    assert _assess(SAMPLES['complaint_to_police'])[0] == 'type_identified'
    assert _assess(SAMPLES['unknown'])[0] == 'verification_incomplete'
    assert assess_verification({}, {}, '')[0] == 'verification_incomplete'


def test_guidance_never_contains_invented_contacts():
    for _expected, text in SAMPLE_DOCUMENTS:
        _status, guidance = _assess(text)
        assert not re.search(r'\d{3}[\s-]?\d{3}[\s-]?\d{3}', guidance)
        assert 'http' not in guidance and 'www.' not in guidance
    assert 'independently' in _assess(SAMPLES['police_summons'])[1]


@pytest.fixture
def document(db, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    user = User.objects.create_user(phone_number='+256700800001', password='testpass123')
    text = SAMPLES['police_summons']
    c = classify_document(text)
    return Document.objects.create(
        owner=user, file=SimpleUploadedFile('summons.pdf', b'%PDF-1.4 test'), status='completed',
        extracted_text=text, doc_type=c['doc_type'], classification=c,
        document_details=extract_document_details(text, c, 0.95),
    )


@pytest.mark.django_db
def test_verified_status_requires_a_confirming_method(document):
    record = DocumentVerificationRecord(
        document=document, resulting_status='verified_official', method='could_not_confirm',
        institution_contacted='Sample Police Station', notes='No answer.')
    with pytest.raises(ValidationError):
        record.save()
    DocumentVerificationRecord.objects.create(
        document=document, resulting_status='verified_official', method='in_person_confirmation',
        institution_contacted='Sample Police Station', notes='O/C confirmed reference and date in person.')
    document.refresh_from_db()
    assert document.verification_status == 'verified_official'


# ── Legal source currency ────────────────────────────────────────────────────

def _source(**kwargs):
    defaults = dict(title='Example Act', category='act', subject='traffic', status='approved',
                    legal_status='in_force', last_verified_at=timezone.now(), full_text='text')
    defaults.update(kwargs)
    return LegalSource.objects.create(**defaults)


@pytest.mark.django_db
def test_currency_assessment():
    assert _source(title='Current').currency_assessment()[0] is True
    assert _source(title='Sample', is_sample=True).currency_assessment()[0] is False
    assert _source(title='Unknown', legal_status='unknown').currency_assessment()[0] is False
    stale = _source(title='Stale', last_verified_at=timezone.now() - timedelta(days=800))
    is_current, warnings = stale.currency_assessment()
    assert is_current is False and any('re-checking' in w for w in warnings)


@pytest.mark.django_db
def test_retrieval_drops_repealed_and_unapproved_sources():
    current = _source(title='Current Act')
    repealed = _source(title='Old Act', legal_status='repealed')
    pending = _source(title='Draft', status='pending_review')
    sample = _source(title='Sample Act', is_sample=True)
    chunks = [{'text': 't', 'distance': 0.2, 'metadata': {'source_id': str(s.id)}}
              for s in (current, repealed, pending, sample)]
    refreshed = {c['metadata']['title']: c['metadata'] for c in _refresh_from_database(chunks)}
    assert set(refreshed) == {'Current Act', 'Sample Act'}
    assert refreshed['Current Act']['is_current_verified'] is True
    assert refreshed['Sample Act']['is_current_verified'] is False


# ── Explanation safeguards ───────────────────────────────────────────────────

def test_authenticity_claims_are_removed_but_hedges_kept():
    text = 'This document is genuine. It asks you to report on Monday.'
    fixed, changed = _remove_authenticity_claims(text)
    assert changed and AUTH_REPLACEMENT in fixed and 'This document is genuine' not in fixed
    hedge = 'LegalBridge cannot confirm whether this document is genuine.'
    assert _remove_authenticity_claims(hedge) == (hedge, False)
    assert _remove_authenticity_claims('The notice looks fake.')[1] is True


AI_TEXT = """## What Your Document Says
This appears to be a police request to report. The document is authentic.

## What This May Mean
You may be asked to assist with inquiries.

## Relevant Ugandan Law
Under Section {section} of the Example Act, you must report.

## Important Details to Check
Check the date.

## Missing Information
No officer name.

## Recommended Next Steps
1. Confirm with the station.
2. Keep the letter.

## Where to Seek Help
A legal aid provider.
"""


def _chunk(section, current=True, sample=False):
    return {'text': f'Section {section}: duties to report.', 'distance': 0.2, 'relevance_score': 0.8,
            'metadata': {'title': 'Example Act', 'short_title': 'Example Act', 'section_number': str(section),
                         'is_current_verified': current, 'is_sample': sample, 'legal_status': 'in_force',
                         'currency_warnings': [] if current else ['Sample placeholder text, not verified law.']}}


def _explain(chunks, ai_text):
    text = SAMPLES['police_summons']
    c = classify_document(text)
    with patch('ai_engine.engine.retrieve_relevant_chunks', return_value=chunks), \
         patch('ai_engine.engine.chat_completion', return_value=ai_text):
        return build_document_explanation(text, c['doc_type'], c, extract_document_details(text, c, 0.95),
                                          'Details require confirmation with the issuing institution')


def test_law_section_replaced_when_only_unverified_sources():
    result = _explain([_chunk(12, current=False, sample=True)], AI_TEXT.format(section=12))
    law = result['sections']['relevant_ugandan_law']
    assert law.startswith(UNCERTAINTY_SENTENCE)
    assert 'not confirmed as current law' in law
    assert result['has_current_verified_sources'] is False


def test_law_section_kept_when_citing_verified_source():
    result = _explain([_chunk(12)], AI_TEXT.format(section=12))
    assert 'Section 12' in result['sections']['relevant_ugandan_law']
    assert result['has_current_verified_sources'] is True


def test_law_section_replaced_when_ai_cites_unretrieved_section():
    result = _explain([_chunk(12)], AI_TEXT.format(section=999))
    law = result['sections']['relevant_ugandan_law']
    assert '999' not in law
    assert any('unsupported_sections:999' in s for s in result['safeguards_applied'])


def test_authenticity_claim_removed_from_explanation():
    result = _explain([_chunk(12)], AI_TEXT.format(section=12))
    assert 'is authentic' not in result['sections']['what_your_document_says']
    assert AUTH_REPLACEMENT in result['sections']['what_your_document_says']


@pytest.mark.django_db
def test_analyze_reports_ai_outage_instead_of_fake_answer(document):
    api = APIClient()
    api.force_authenticate(document.owner)
    with patch('ai_engine.engine.retrieve_relevant_chunks', return_value=[]), \
         patch('ai_engine.engine.chat_completion',
               side_effect=AIServiceUnavailable('quota_billing', 'You exceeded your current quota')):
        response = api.post(reverse('document_analyze', kwargs={'pk': document.pk}), {'language': 'en'},
                            format='json')
    assert response.status_code == 503
    assert response.data['error_category'] == 'quota_billing'
    assert not DocumentAnalysis.objects.filter(document=document).exists()


@pytest.mark.django_db
def test_document_detail_exposes_recognition_and_verification(document):
    api = APIClient()
    api.force_authenticate(document.owner)
    data = api.get(reverse('document_detail', kwargs={'pk': document.pk})).data
    assert data['doc_type'] == 'police_summons'
    assert data['doc_type_label'].startswith('Police summons')
    assert 'document_details' in data and 'verification_status_label' in data
