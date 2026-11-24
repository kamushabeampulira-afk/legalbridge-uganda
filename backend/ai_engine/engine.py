"""
LegalBridge — AI Engine (RAG pipeline).
Retrieves verified legal context, then generates explanations via OpenAI.

AI failures raise openai_service.AIServiceUnavailable. They are never turned
into a legal-sounding answer: the caller reports the service as unavailable.
"""
from __future__ import annotations
import logging
import re

from legal_data.vector_store import retrieve_relevant_chunks, MAX_RELEVANT_DISTANCE
from .openai_service import AIServiceUnavailable, chat_completion  # noqa: F401 (re-exported)
from .prompts import (
    SYSTEM_PROMPT,
    DOCUMENT_EXPLANATION_PROMPT,
    LEGAL_QUESTION_PROMPT,
    BODA_STOPPED_PROMPT,
    EVICTION_GUIDANCE_PROMPT,
    uncertainty_response,
)

logger = logging.getLogger('legalbridge')

USER_CATEGORY_LABELS = {
    'boda_boda': 'boda boda rider',
    'market_vendor': 'market vendor',
    'general': 'person',
}

UNCERTAINTY_SENTENCE = ('I cannot verify the applicable legal provision from the information '
                        'currently available.')

LEGAL_STATUS_LABELS = {
    'in_force': 'in force',
    'amended': 'in force, as amended',
    'partially_repealed': 'partially repealed',
    'repealed': 'repealed',
    'unknown': 'not confirmed',
}

DETAIL_LABELS = {
    'document_type': 'Document type',
    'issuing_institution': 'Issuing institution',
    'issuing_office': 'Issuing station/office',
    'reference_numbers': 'Reference number(s)',
    'date_of_issue': 'Date of issue',
    'recipient': 'Recipient',
    'subject_or_offence': 'Subject / alleged offence',
    'deadlines': 'Dates and deadlines',
    'amounts': 'Amounts',
    'instructions': 'Instructions / requested actions',
    'signature_or_stamp': 'Signature or stamp',
    'contact_information': 'Contact information printed on it',
    'legal_provisions_mentioned': 'Laws the document mentions',
}


def _call_openai(system_prompt: str, user_message: str, language: str = 'en',
                 purpose: str = 'general') -> str:
    """Kept for backwards compatibility; raises AIServiceUnavailable on failure."""
    return chat_completion(system_prompt, user_message, purpose=purpose)


# ── Legal context ─────────────────────────────────────────────────────────────

def _format_retrieved_context(chunks: list, language: str = 'en') -> tuple[str, list, bool]:
    """
    Format retrieved chunks into a prompt-ready string with citation labels.
    Returns (formatted_context, sources_list, has_relevant_sources).
    Each source records whether it is confirmed current law (is_current_verified).
    """
    chunks = [c for c in (chunks or []) if c.get('distance', 0) < MAX_RELEVANT_DISTANCE]
    if not chunks:
        return uncertainty_response(language), [], False

    context_parts = []
    sources = []
    seen = set()
    for chunk in chunks:
        meta = chunk.get('metadata', {})
        title = meta.get('title', 'Unknown Source')
        short = meta.get('short_title') or title
        is_current = bool(meta.get('is_current_verified', False))
        warnings = list(meta.get('currency_warnings') or [])
        status = LEGAL_STATUS_LABELS.get(meta.get('legal_status', 'unknown'), 'not confirmed')

        label = [f"Source: {short}"]
        if meta.get('instrument_number'):
            label.append(meta['instrument_number'])
        if meta.get('section_number'):
            label.append(f"Section {meta['section_number']}"
                         + (f": {meta['section_title']}" if meta.get('section_title') else ''))
        if meta.get('issuing_authority'):
            label.append(meta['issuing_authority'])
        if meta.get('is_sample'):
            label.append('SAMPLE TEXT, NOT VERIFIED LAW')
        elif is_current:
            label.append(f"CURRENT: {status}, last verified {meta.get('last_verified_at') or 'unknown'}")
        else:
            label.append('NOT CONFIRMED AS CURRENT LAW')
        context_parts.append(f"[{' | '.join(label)}]\n{chunk['text']}")

        key = (title, meta.get('section_number', ''))
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            'title': title,
            'short_title': meta.get('short_title', ''),
            'instrument_number': meta.get('instrument_number', ''),
            'section_number': meta.get('section_number', ''),
            'section_title': meta.get('section_title', ''),
            'issuing_authority': meta.get('issuing_authority', ''),
            'source_url': meta.get('source_url', ''),
            'publication_date': meta.get('publication_date', ''),
            'commencement_date': meta.get('commencement_date', ''),
            'legal_status': status,
            'last_verified_at': meta.get('last_verified_at', ''),
            'is_sample': bool(meta.get('is_sample', False)),
            'is_current_verified': is_current,
            'currency_warnings': warnings,
        })

    return '\n\n---\n\n'.join(context_parts), sources, True


def _has_current_verified(sources: list) -> bool:
    return any(s.get('is_current_verified') for s in sources)


# ── Deterministic safeguards applied to AI output ────────────────────────────

_AUTH_CLAIM = re.compile(
    r'\b(?:is|are|appears? to be|seems? to be|looks?(?: to be)?|is likely|is clearly|is definitely|'
    r'is probably)\s+(?:an?\s+)?(?:genuine|authentic|legitimate|real|fake|forged|fraudulent|counterfeit|'
    r'not genuine|not authentic|not real)\b',
    re.IGNORECASE,
)
_AUTH_HEDGE = re.compile(
    r"\b(?:cannot|can't|can not|unable|not (?:been )?(?:verified|confirmed|able)|whether|if it is|"
    r'check|confirm with|verify|unverified)\b',
    re.IGNORECASE,
)
AUTH_REPLACEMENT = 'LegalBridge cannot confirm whether this document is genuine.'


def _remove_authenticity_claims(text: str) -> tuple[str, bool]:
    """Replace sentences that declare a document genuine or fake."""
    if not text:
        return text, False
    changed = False

    def fix(match):
        nonlocal changed
        sentence = match.group(0)
        if _AUTH_CLAIM.search(sentence) and not _AUTH_HEDGE.search(sentence):
            changed = True
            return AUTH_REPLACEMENT
        return sentence

    fixed = re.sub(r'[^.!?\n]+[.!?]?', fix, text)
    return fixed, changed


_SECTION_REF = re.compile(r'\b(?:section|sec\.|s\.)\s*(\d+[A-Za-z]?)', re.IGNORECASE)


def _unsupported_sections(law_text: str, sources: list, context: str) -> set:
    cited = {m.upper() for m in _SECTION_REF.findall(law_text or '')}
    allowed = {str(s.get('section_number', '')).upper() for s in sources if s.get('section_number')}
    allowed |= {m.upper() for m in _SECTION_REF.findall(context or '')}
    return cited - allowed


def _unverified_law_text(sources: list) -> str:
    text = UNCERTAINTY_SENTENCE
    unverified = [s for s in sources if not s.get('is_current_verified')]
    if unverified:
        text += ('\n\nThe LegalBridge knowledge base has related material, but it is not confirmed as '
                 'current law, so it has not been relied on:')
        for s in unverified[:5]:
            name = s.get('short_title') or s.get('title')
            if s.get('section_number'):
                name += f", section {s['section_number']}"
            reason = '; '.join(s.get('currency_warnings') or ['not confirmed as current law'])
            text += f'\n- {name}: {reason}'
    text += '\n\nAsk a qualified lawyer or a legal aid provider which law applies to your situation.'
    return text


def _verified_law_listing(sources: list) -> str:
    lines = ['The following verified sources were found. The automatic explanation of them was removed '
             'because it referred to provisions that are not in these sources:']
    for s in sources:
        if not s.get('is_current_verified'):
            continue
        name = s.get('title')
        if s.get('instrument_number'):
            name += f" ({s['instrument_number']})"
        if s.get('section_number'):
            name += f", section {s['section_number']}" + (f": {s['section_title']}" if s.get('section_title') else '')
        lines.append(f'- {name}')
    lines.append('Ask a qualified lawyer or legal aid provider how these apply to you.')
    return '\n'.join(lines)


# ── Document explanation ──────────────────────────────────────────────────────

def _format_details_for_prompt(details: dict) -> str:
    lines, missing = [], []
    for key, label in DETAIL_LABELS.items():
        field = (details or {}).get(key) or {}
        status, value = field.get('status'), field.get('value')
        if status in ('found', 'unclear') and value:
            shown = '; '.join(map(str, value)) if isinstance(value, list) else str(value)
            lines.append(f'  - {label}: {shown[:300]}' + ('  [UNCLEAR, needs checking]' if status == 'unclear' else ''))
        else:
            missing.append(label.lower())
    if missing:
        lines.append(f"  - Not found in the text: {', '.join(missing)}")
    return '\n'.join(lines) or '  (none detected)'


def build_document_explanation(text: str, doc_type: str, classification: dict, details: dict,
                               verification_status_label: str, user_category: str = 'general',
                               language: str = 'en', purpose: str = 'document_explanation') -> dict:
    """
    Retrieve legal context and generate a guarded explanation. Writes nothing to the
    database except the AI request log. Raises AIServiceUnavailable if the AI fails.
    """
    from documents.doc_types import DOC_TYPE_LABELS, legal_subjects_for

    classification = classification or {}
    details = details or {}

    # Document-specific retrieval: the type, what the document is about, and laws it cites
    query_parts = [DOC_TYPE_LABELS.get(doc_type, '')]
    for key in ('subject_or_offence', 'legal_provisions_mentioned'):
        value = (details.get(key) or {}).get('value')
        if value:
            query_parts.append(' '.join(value) if isinstance(value, list) else str(value))
    query_parts.append((text or '')[:400])
    subjects = legal_subjects_for(doc_type) if doc_type != 'unknown' else None
    chunks = retrieve_relevant_chunks(' '.join(p for p in query_parts if p), subjects=subjects, n_results=6)

    retrieved_context, sources, has_sources = _format_retrieved_context(chunks)
    has_current = _has_current_verified(sources)
    if not has_sources:
        legal_note = 'NO RELEVANT LEGAL SOURCES WERE FOUND IN THE VERIFIED KNOWLEDGE BASE.'
        retrieved_context = ''
    elif not has_current:
        legal_note = ('The sources below are NOT CONFIRMED AS CURRENT LAW (sample or unverified text). '
                      'Do not cite them as law.')
    else:
        legal_note = 'Only sources marked CURRENT have been verified against an official source.'

    issuer = classification.get('issuer') or {}
    origin = {
        'issued_by_institution': 'appears to be issued by an institution',
        'submitted_by_public': 'appears to be written by a member of the public, not by an authority',
    }.get(classification.get('origin'), 'unclear')

    prompt = DOCUMENT_EXPLANATION_PROMPT.format(
        user_category_label=USER_CATEGORY_LABELS.get(user_category, 'person'),
        document_text=(text or '')[:3000] or '[No text extracted]',
        doc_type=DOC_TYPE_LABELS.get(doc_type, doc_type),
        classification_confidence=classification.get('confidence', 'unknown'),
        issuer=issuer.get('name') or 'not stated in the text',
        origin=origin,
        extracted_details=_format_details_for_prompt(details),
        verification_status=verification_status_label,
        legal_context_note=legal_note,
        retrieved_context=retrieved_context,
    )
    raw_response = chat_completion(SYSTEM_PROMPT.format(language=language), prompt, purpose=purpose)

    sections = _parse_response_sections(raw_response)
    safeguards = []

    for key in list(sections):
        if isinstance(sections[key], str):
            sections[key], changed = _remove_authenticity_claims(sections[key])
            if changed:
                safeguards.append(f'authenticity_claim_removed:{key}')
    sections['recommended_next_steps_list'] = [
        _remove_authenticity_claims(s)[0] for s in sections.get('recommended_next_steps_list', [])
    ]

    if not has_current:
        sections['relevant_ugandan_law'] = _unverified_law_text(sources)
        safeguards.append('law_section_replaced:no_current_verified_sources')
    else:
        unsupported = _unsupported_sections(sections.get('relevant_ugandan_law', ''), sources, retrieved_context)
        if unsupported:
            sections['relevant_ugandan_law'] = _verified_law_listing(sources)
            safeguards.append(f"law_section_replaced:unsupported_sections:{','.join(sorted(unsupported))}")

    if safeguards:
        logger.warning(f'Explanation safeguards applied: {safeguards}')

    return {
        'sections': sections,
        'sources': sources,
        'has_relevant_sources': has_sources,
        'has_current_verified_sources': has_current,
        'safeguards_applied': safeguards,
    }


def generate_document_explanation(document, language: str = 'en'):
    """
    Main pipeline for document analysis. Saves and returns a DocumentAnalysis.
    Raises AIServiceUnavailable (and saves nothing) if the AI service fails.
    """
    from documents.models import DocumentAnalysis

    result = build_document_explanation(
        text=document.extracted_text,
        doc_type=document.doc_type,
        classification=document.classification,
        details=document.document_details,
        verification_status_label=document.get_verification_status_display(),
        user_category=document.user_category,
        language=language,
    )
    sections = result['sections']
    has_current = result['has_current_verified_sources']
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
            'legal_sources_used': result['sources'],
            'has_verified_sources': has_current,
            'uncertainty_flag': not has_current,
        }
    )
    return analysis


# ── Questions and guided scenarios ───────────────────────────────────────────

def answer_legal_question(question: str, user_category: str, language: str, user=None) -> dict:
    """
    Answer a free-text legal question using RAG.
    Returns a dict with answer, sources, uncertainty_flag. Raises AIServiceUnavailable.
    """
    from legal_data.models import LegalQuery

    subject = _infer_subject_from_question(question, user_category)
    chunks = retrieve_relevant_chunks(question, subject_filter=subject, n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks, language=language)
    has_current = _has_current_verified(sources)

    user_category_label = USER_CATEGORY_LABELS.get(user_category, 'person')
    system = SYSTEM_PROMPT.format(language=language)

    if not has_sources:
        response_text = uncertainty_response(language)
    else:
        prompt = LEGAL_QUESTION_PROMPT.format(
            user_category_label=user_category_label,
            question=question,
            retrieved_context=retrieved_context,
        )
        response_text = chat_completion(system, prompt, purpose='legal_question')

    # Store the query (anonymised if no user)
    LegalQuery.objects.create(
        user=user,
        question_text=question,
        user_category=user_category,
        language=language,
        sources_retrieved=sources,
        response_text=response_text,
        has_verified_sources=has_current,
        uncertainty_flag=not has_current,
    )

    return {
        'answer': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_current,
        'uncertainty_flag': not has_current,
        'disclaimer': (
            'This is legal information, not legal advice. '
            'For serious legal matters, consult a qualified lawyer.'
        ),
    }


def answer_boda_stopped(data: dict, language: str = 'en', user=None) -> dict:
    """Guided response for boda riders stopped by an officer. Raises AIServiceUnavailable."""
    query = f"traffic violation boda boda police stop Uganda rights {data.get('told_about', '')}"
    chunks = retrieve_relevant_chunks(query, subjects=['traffic', 'police'], n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks, language=language)
    has_current = _has_current_verified(sources)

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
        response_text = uncertainty_response(language)
    else:
        response_text = chat_completion(system, prompt, purpose='boda_stopped')

    return {
        'guidance': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_current,
        'uncertainty_flag': not has_current,
        'disclaimer': 'This is legal information only. Consult a qualified lawyer for specific legal advice.',
    }


def answer_eviction_guidance(data: dict, language: str = 'en', user=None) -> dict:
    """Guided response for market vendor facing eviction. Raises AIServiceUnavailable."""
    query = f"eviction market vendor stall Uganda rights {data.get('reason_given', '')}"
    chunks = retrieve_relevant_chunks(query, subjects=['markets', 'local_gov', 'land'], n_results=5)
    retrieved_context, sources, has_sources = _format_retrieved_context(chunks, language=language)
    has_current = _has_current_verified(sources)

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
        response_text = uncertainty_response(language)
    else:
        response_text = chat_completion(system, prompt, purpose='eviction_guidance')

    return {
        'guidance': response_text,
        'legal_sources': sources,
        'has_verified_sources': has_current,
        'uncertainty_flag': not has_current,
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
    Clearly labelled placeholder text, used ONLY when AI_DEMO_MODE=True and no
    API key is configured (local development without an AI provider).
    """
    return """## What Your Document Says
[DEMO MODE — no AI provider configured. This is placeholder text, not an explanation of your document.]

## What This May Mean
This section would explain the practical implications of the document in simple language.

## Relevant Ugandan Law
I cannot verify the applicable legal provision from the information currently available.

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
"""
