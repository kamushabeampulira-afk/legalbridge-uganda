"""Tests: AI engine safeguards — no hallucination, uncertainty flags."""
import pytest
from unittest.mock import patch, MagicMock
from ai_engine.engine import (
    _parse_response_sections,
    _infer_subject_from_question,
    _format_retrieved_context,
    answer_legal_question,
)
from ai_engine.prompts import UNCERTAINTY_RESPONSE


def test_parse_response_sections_extracts_all_sections():
    sample = """
## What Your Document Says
This is a traffic violation notice.

## What This May Mean
You may have been alleged to have committed an offence.

## Relevant Ugandan Law
Traffic and Road Safety Act, Cap 361, Section 130.

## Important Details to Check
- Reference number
- Payment deadline

## Missing Information
No signature from officer.

## Recommended Next Steps
1. Keep the notice safe.
2. Note the reference number.
3. Seek legal advice.

## Where to Seek Help
Uganda Law Society — www.uls.or.ug
"""
    sections = _parse_response_sections(sample)
    assert 'traffic violation' in sections.get('what_your_document_says', '').lower()
    assert 'Traffic and Road Safety' in sections.get('relevant_ugandan_law', '')
    assert isinstance(sections.get('recommended_next_steps_list', []), list)
    assert len(sections['recommended_next_steps_list']) == 3


def test_parse_response_sections_fallback_on_no_sections():
    plain = "This is an answer without section headers."
    sections = _parse_response_sections(plain)
    assert plain in sections.get('what_your_document_says', '')


def test_format_retrieved_context_empty_returns_uncertainty():
    context, sources, has_sources = _format_retrieved_context([])
    assert has_sources is False
    assert len(sources) == 0
    assert 'cannot verify' in context.lower() or 'legal professional' in context.lower()


def test_format_retrieved_context_with_chunks():
    chunks = [{
        'text': 'Section 130 — penalty notices must specify the alleged offence.',
        'metadata': {
            'title': 'Traffic and Road Safety Act',
            'short_title': 'Traffic & Road Safety Act',
            'issuing_authority': 'Parliament of Uganda',
            'source_url': 'https://ulii.org',
            'publication_date': '1998-01-01',
        },
        'distance': 0.15,
        'relevance_score': 0.85,
    }]
    context, sources, has_sources = _format_retrieved_context(chunks)
    assert has_sources is True
    assert len(sources) == 1
    assert 'Traffic' in sources[0]['title']
    assert 'Section 130' in context


def test_format_retrieved_context_filters_low_relevance():
    chunks = [{
        'text': 'Barely relevant text.',
        'metadata': {'title': 'Some Act', 'short_title': 'Some Act'},
        'distance': 0.85,  # Too far — should be filtered
        'relevance_score': 0.15,
    }]
    context, sources, has_sources = _format_retrieved_context(chunks)
    assert has_sources is False


def test_infer_subject_traffic_keywords():
    assert _infer_subject_from_question('traffic fine for boda boda', 'general') == 'traffic'
    assert _infer_subject_from_question('motorcycle licence expired', 'general') == 'traffic'
    assert _infer_subject_from_question('police stopped me on the road', 'general') == 'traffic'


def test_infer_subject_market_keywords():
    assert _infer_subject_from_question('eviction from market stall', 'general') == 'markets'
    assert _infer_subject_from_question('allocation slip for vendor', 'general') == 'markets'


def test_infer_subject_from_user_category():
    assert _infer_subject_from_question('I need help', 'boda_boda') == 'traffic'
    assert _infer_subject_from_question('I need help', 'market_vendor') == 'markets'


def test_infer_subject_returns_none_for_general():
    result = _infer_subject_from_question('tell me about law', 'general')
    assert result is None


@pytest.mark.django_db
def test_answer_legal_question_uncertainty_when_no_chunks():
    """Core anti-hallucination test: no chunks = uncertainty message returned."""
    with patch('legal_data.vector_store.retrieve_relevant_chunks', return_value=[]):
        result = answer_legal_question(
            question='What is the fine for speeding?',
            user_category='boda_boda',
            language='en',
            user=None,
        )
    assert result['uncertainty_flag'] is True
    assert result['has_verified_sources'] is False
    assert 'cannot verify' in result['answer'].lower() or 'legal professional' in result['answer'].lower()


@pytest.mark.django_db
def test_answer_legal_question_uses_retrieved_context():
    """When chunks are available, OpenAI is called with context."""
    mock_chunks = [{
        'text': 'Section 130 — penalty notices must specify alleged offence.',
        'metadata': {
            'title': 'Traffic and Road Safety Act',
            'short_title': 'Traffic Act',
            'issuing_authority': 'Parliament of Uganda',
            'source_url': 'https://ulii.org',
            'publication_date': '1998-01-01',
        },
        'distance': 0.2,
        'relevance_score': 0.8,
    }]

    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "According to the Traffic and Road Safety Act, Section 130, "
        "a penalty notice must specify the alleged offence. "
        "This is legal information, not legal advice."
    )

    with patch('legal_data.vector_store.retrieve_relevant_chunks', return_value=mock_chunks), \
         patch('ai_engine.engine._get_openai_client') as mock_client_fn:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_fn.return_value = mock_client

        result = answer_legal_question(
            question='What must a traffic penalty notice include?',
            user_category='boda_boda',
            language='en',
            user=None,
        )

    assert result['has_verified_sources'] is True
    assert result['uncertainty_flag'] is False
    assert len(result['legal_sources']) == 1
