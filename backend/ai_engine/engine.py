"""
LegalBridge — AI Engine (RAG pipeline).
Retrieves verified legal context, then generates explanations via OpenAI.
"""
from __future__ import annotations
import logging
from django.conf import settings

from legal_data.vector_store import retrieve_relevant_chunks
from .prompts import (
    SYSTEM_PROMPT,
    DOCUMENT_EXPLANATION_PROMPT,
    LEGAL_QUESTION_PROMPT,
    BODA_STOPPED_PROMPT,
    EVICTION_GUIDANCE_PROMPT,
    UNCERTAINTY_RESPONSE,
)

logger = logging.getLogger('legalbridge')

USER_CATEGORY_LABELS = {
    'boda_boda': 'boda boda rider',
    'market_vendor': 'market vendor',
    'general': 'person',
}

SUBJECT_MAP = {
    'traffic_notice': 'traffic',
    'police_charge': 'traffic',
    'eviction_notice': 'markets',
    'allocation_slip': 'markets',
    'payment_receipt': 'markets',
    'market_notice': 'markets',
    'court_summons': 'general',
    'unknown': None,
}


def _get_openai_client():
    try:
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        logger.error(f'OpenAI client init failed: {e}')
        return None


def _call_openai(system_prompt: str, user_message: str, language: str = 'en') -> str:
    """Call OpenAI with the given prompts. Returns response text."""
    client = _get_openai_client()
    if not client or not settings.OPENAI_API_KEY:
        logger.warning('OpenAI not configured — returning placeholder response.')
        return _demo_fallback_response()

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            max_tokens=1500,
            temperature=0.2,  # Low temperature = more factual, less creative
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f'OpenAI API call failed: {e}')
        raise


def _format_retrieved_context(chunks: list) -> tuple[str, list, bool]:
    """
    Format retrieved chunks into a prompt-ready string.
    Returns (formatted_context, sources_list, has_verified_sources).
    """
    if not chunks:
        return UNCERTAINTY_RESPONSE, [], False

    context_parts = []
    sources = []
    for chunk in chunks:
        meta = chunk.get('metadata', {})
        source_label = meta.get('short_title') or meta.get('title', 'Unknown Source')
        context_parts.append(
            f"[Source: {source_label} | {meta.get('issuing_authority', '')}]\n{chunk['text']}"
        )
        if meta.get('title') and meta.get('title') not in [s.get('title') for s in sources]:
            sources.append({
                'title': meta.get('title', ''),
                'short_title': meta.get('short_title', ''),
                'issuing_authority': meta.get('issuing_authority', ''),
                'source_url': meta.get('source_url', ''),
                'publication_date': meta.get('publication_date', ''),
            })

    return '\n\n---\n\n'.join(context_parts), sources, True


def generate_document_explanation(document, language: str = 'en'):
    """
    Main RAG pipeline for document analysis.
    Retrieves legal context, generates explanation, saves DocumentAnalysis.
    """
    from documents.models import DocumentAnalysis

    subject = SUBJECT_MAP.get(document.doc_type)
    query = f"{document.doc_type} {document.extracted_text[:500]}"

    chunks = retrieve_relevant_chunks(query, subject_filter=subject, n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks)

    user_category_label = USER_CATEGORY_LABELS.get(document.user_category, 'person')
    system = SYSTEM_PROMPT.format(language=language)

    prompt = DOCUMENT_EXPLANATION_PROMPT.format(
        user_category_label=user_category_label,
        document_text=document.extracted_text[:3000] if document.extracted_text else '[No text extracted]',
        doc_type=document.get_doc_type_display(),
        retrieved_context=retrieved_context,
    )

    if not has_sources:
        raw_response = UNCERTAINTY_RESPONSE
        uncertainty_flag = True
    else:
        try:
            raw_response = _call_openai(system, prompt, language)
            uncertainty_flag = False
        except Exception:
            raw_response = UNCERTAINTY_RESPONSE
            uncertainty_flag = True

    sections = _parse_response_sections(raw_response)

    # Save or update analysis
    analysis, _ = DocumentAnalysis.objects.update_or_create(
        document=document,
        defaults={
            'summary': sections.get('what_your_document_says', ''),
            'what_it_means': sections.get('what_this_may_mean', ''),
            'relevant_law': sections.get('relevant_ugandan_law', ''),
            'details_to_check': sections.get('important_details_to_check', ''),
            'next_steps': sections.get('recommended_next_steps_list', []),
            'missing_information': sections.get('missing_information', ''),
            'where_to_get_help': sections.get('where_to_seek_help', ''),
            'legal_sources_used': sources,
            'has_verified_sources': has_sources,
            'uncertainty_flag': uncertainty_flag,
        }
    )
    return analysis


def answer_legal_question(question: str, user_category: str, language: str, user=None) -> dict:
    """
    Answer a free-text legal question using RAG.
    Returns a dict with answer, sources, uncertainty_flag.
    """
    from legal_data.models import LegalQuery

    subject = _infer_subject_from_question(question, user_category)
    chunks = retrieve_relevant_chunks(question, subject_filter=subject, n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks)

    user_category_label = USER_CATEGORY_LABELS.get(user_category, 'person')
    system = SYSTEM_PROMPT.format(language=language)

    if not has_sources:
        response_text = UNCERTAINTY_RESPONSE
        uncertainty_flag = True
    else:
        prompt = LEGAL_QUESTION_PROMPT.format(
            user_category_label=user_category_label,
            question=question,
            retrieved_context=retrieved_context,
        )
        try:
            response_text = _call_openai(system, prompt, language)
            uncertainty_flag = False
        except Exception:
            response_text = UNCERTAINTY_RESPONSE
            uncertainty_flag = True

    # Store the query (anonymised if no user)
    LegalQuery.objects.create(
        user=user,
        question_text=question,
        user_category=user_category,
        language=language,
        sources_retrieved=sources,
        response_text=response_text,
        has_verified_sources=has_sources,
        uncertainty_flag=uncertainty_flag,
    )

    return {
        'answer': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_sources,
        'uncertainty_flag': uncertainty_flag,
        'disclaimer': (
            'This is legal information, not legal advice. '
            'For serious legal matters, consult a qualified lawyer.'
        ),
    }


def answer_boda_stopped(data: dict, language: str = 'en', user=None) -> dict:
    """Guided response for boda riders stopped by an officer."""
    query = f"traffic violation boda boda police stop Uganda rights {data.get('told_about', '')}"
    chunks = retrieve_relevant_chunks(query, subject_filter='traffic', n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks)

    system = SYSTEM_PROMPT.format(language=language)
    prompt = BODA_STOPPED_PROMPT.format(
        told_about=data.get('told_about', 'Not specified'),
        has_written_notice=data.get('has_written_notice', 'Unknown'),
        penalty_mentioned=data.get('penalty_mentioned', 'Not mentioned'),
        has_reference=data.get('has_reference', 'Unknown'),
        additional_details=data.get('additional_details', 'None'),
        retrieved_context=retrieved_context,
    )

    if not has_sources:
        response_text = UNCERTAINTY_RESPONSE
        uncertainty_flag = True
    else:
        try:
            response_text = _call_openai(system, prompt, language)
            uncertainty_flag = False
        except Exception:
            response_text = UNCERTAINTY_RESPONSE
            uncertainty_flag = True

    return {
        'guidance': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_sources,
        'uncertainty_flag': uncertainty_flag,
        'disclaimer': 'This is legal information only. Consult a qualified lawyer for specific legal advice.',
    }


def answer_eviction_guidance(data: dict, language: str = 'en', user=None) -> dict:
    """Guided response for market vendor facing eviction."""
    query = f"eviction market vendor stall Uganda rights {data.get('reason_given', '')}"
    chunks = retrieve_relevant_chunks(query, subject_filter='markets', n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks)

    system = SYSTEM_PROMPT.format(language=language)
    prompt = EVICTION_GUIDANCE_PROMPT.format(
        has_allocation_slip=data.get('has_allocation_slip', 'Unknown'),
        has_receipts=data.get('has_receipts', 'Unknown'),
        notice_issuer=data.get('notice_issuer', 'Not specified'),
        reason_given=data.get('reason_given', 'No reason given'),
        deadline=data.get('deadline', 'Not specified'),
        additional_details=data.get('additional_details', 'None'),
        retrieved_context=retrieved_context,
    )

    if not has_sources:
        response_text = UNCERTAINTY_RESPONSE
        uncertainty_flag = True
    else:
        try:
            response_text = _call_openai(system, prompt, language)
            uncertainty_flag = False
        except Exception:
            response_text = UNCERTAINTY_RESPONSE
            uncertainty_flag = True

    return {
        'guidance': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_sources,
        'uncertainty_flag': uncertainty_flag,
        'disclaimer': 'This is legal information only. Consult a qualified lawyer for specific legal advice.',
    }


def _infer_subject_from_question(question: str, user_category: str) -> str | None:
    q = question.lower()
    if any(w in q for w in ['traffic', 'road', 'boda', 'motorcycle', 'vehicle', 'licence', 'fine']):
        return 'traffic'
    if any(w in q for w in ['market', 'stall', 'vendor', 'evict', 'allocation', 'rent']):
        return 'markets'
    if user_category == 'boda_boda':
        return 'traffic'
    if user_category == 'market_vendor':
        return 'markets'
    return None


def _parse_response_sections(text: str) -> dict:
    """Parse AI response into labelled sections for database storage."""
    import re
    sections = {}
    patterns = {
        'what_your_document_says': r'##\s*What Your Document Says\s*\n(.*?)(?=##|\Z)',
        'what_this_may_mean': r'##\s*What This May Mean\s*\n(.*?)(?=##|\Z)',
        'relevant_ugandan_law': r'##\s*Relevant Ugandan Law\s*\n(.*?)(?=##|\Z)',
        'important_details_to_check': r'##\s*Important Details to Check\s*\n(.*?)(?=##|\Z)',
        'missing_information': r'##\s*Missing Information\s*\n(.*?)(?=##|\Z)',
        'recommended_next_steps': r'##\s*Recommended Next Steps\s*\n(.*?)(?=##|\Z)',
        'where_to_seek_help': r'##\s*Where to Seek Help\s*\n(.*?)(?=##|\Z)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    # Parse next steps into a list
    raw_steps = sections.get('recommended_next_steps', '')
    if raw_steps:
        steps = re.findall(r'\d+\.\s*(.+)', raw_steps)
        sections['recommended_next_steps_list'] = steps if steps else [raw_steps]
    else:
        sections['recommended_next_steps_list'] = []

    # Fallback: if no sections parsed, store full text in summary
    if not any(sections.values()):
        sections['what_your_document_says'] = text

    return sections


def _demo_fallback_response() -> str:
    """
    Returns a clearly labelled demo response when OpenAI is not configured.
    Used during development to test the full pipeline without an API key.
    """
    return """## What Your Document Says
[DEMO MODE — OpenAI API key not configured]
This appears to be an official document that has been received by the user. 
In production, LegalBridge would analyse the full text extracted from your document.

## What This May Mean
This section would explain the practical implications of the document in simple language.

## Relevant Ugandan Law
This section would cite specific provisions from verified Ugandan law retrieved from the LegalBridge knowledge base.

## Important Details to Check
- Verify the reference number on the document
- Check the date of issue and any deadlines mentioned
- Confirm the name and designation of the issuing authority

## Missing Information
This section identifies what information appears to be absent from the document.

## Recommended Next Steps
1. Keep the original document safe
2. Note any deadlines mentioned
3. Seek assistance from a legal aid provider if needed

## Where to Seek Help
- Uganda Law Society: www.uls.or.ug
- FIDA Uganda: www.fidauganda.org
- Legal Aid Service Providers in your district

**Note: Configure OPENAI_API_KEY in your .env file to enable full AI analysis.**
"""
