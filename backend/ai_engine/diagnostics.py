"""
LegalBridge: component diagnostics for the document-analysis pipeline.

Each component is tested on its own, so a failure can be traced to the right place:
    A. OpenAI API connection        (openai_service.run_connection_check)
    B. OCR text extraction          (Tesseract on a generated image, PyMuPDF on a generated PDF)
    C. Legal knowledge retrieval    (ChromaDB index + database verification status)
    D. Document classification      (synthetic samples with known types)
    E. Explanation generation       (full AI pipeline on a synthetic document; uses one AI request)

service_overview() combines the latest results with real request history. The document
analysis service is only reported operational when an explanation has actually been
generated end to end; a passing connection test alone is not enough.
"""
from __future__ import annotations

import io
import logging
import os
import tempfile
import time
from datetime import timedelta

from django.utils import timezone

from .models import AIHealthCheck, AIRequestLog
from .openai_service import AIServiceUnavailable, run_connection_check, sanitize

logger = logging.getLogger('legalbridge')

OCR_PHRASE = 'LEGALBRIDGE OCR TEST 2468'

DOC_SERVICE_LABELS = {
    'operational': 'Operational',
    'operational_with_warnings': 'Operational, with warnings',
    'degraded': 'Degraded',
    'unavailable': 'Unavailable',
    'not_confirmed': 'Not confirmed',
}


def _save(kind, status, summary, details=None, triggered_by=None, latency_ms=None, ai_status='',
          model_name=''):
    return AIHealthCheck.objects.create(
        kind=kind, component_status=status, summary=sanitize(summary)[:500], details=details or {},
        triggered_by=triggered_by if getattr(triggered_by, 'pk', None) else None,
        latency_ms=latency_ms, ai_status=ai_status, model_name=model_name[:100],
    )


def _font(size):
    from PIL import ImageFont
    for name in ('arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def check_ocr(triggered_by=None):
    """B. OCR: Tesseract on a generated image, and PDF text extraction."""
    from documents.ocr import _ocr_image_bytes, _extract_pdf
    details = {'tesseract_version': None, 'image_ocr': None, 'pdf_extraction': None}
    start = time.monotonic()

    try:
        import pytesseract
        details['tesseract_version'] = str(pytesseract.get_tesseract_version())
    except Exception as e:
        details['tesseract_error'] = sanitize(str(e))

    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (900, 140), 'white')
        ImageDraw.Draw(img).text((20, 40), OCR_PHRASE, fill='black', font=_font(48))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        result = _ocr_image_bytes(buf.getvalue(), source='diagnostic')
        read = ' '.join(result.get('text', '').upper().split())
        details['image_ocr'] = OCR_PHRASE in read
        details['image_ocr_confidence'] = result.get('confidence')
        if not details['image_ocr']:
            details['image_ocr_read'] = read[:80]
            details['image_ocr_warnings'] = result.get('warnings', [])
    except Exception as e:
        details['image_ocr'] = False
        details['image_ocr_error'] = sanitize(str(e))

    try:
        import fitz
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        try:
            pdf = fitz.open()
            pdf.new_page().insert_text((72, 72), OCR_PHRASE, fontsize=14)
            pdf.save(path)
            pdf.close()
            text = _extract_pdf(path).get('text', '')
            details['pdf_extraction'] = OCR_PHRASE in ' '.join(text.upper().split())
        finally:
            os.remove(path)
    except Exception as e:
        details['pdf_extraction'] = False
        details['pdf_error'] = sanitize(str(e))

    latency = int((time.monotonic() - start) * 1000)
    if details['image_ocr'] and details['pdf_extraction']:
        return _save('ocr', 'pass', f"Photo OCR and PDF text extraction work (Tesseract {details['tesseract_version']}).",
                     details, triggered_by, latency)
    if details['pdf_extraction']:
        reason = 'Tesseract is not installed or not on PATH' if not details['tesseract_version'] \
            else 'Tesseract could not read the test image'
        return _save('ocr', 'warn', f'PDFs with text work, but photos cannot be read: {reason}.',
                     details, triggered_by, latency)
    return _save('ocr', 'fail', 'Text could not be extracted from the test image or PDF.', details,
                 triggered_by, latency)


def check_legal_retrieval(triggered_by=None):
    """C. Legal knowledge retrieval: index availability, verification state, and a test query."""
    from legal_data.models import LegalSource
    from legal_data.vector_store import _get_collection, retrieve_relevant_chunks

    start = time.monotonic()
    approved = list(LegalSource.objects.filter(status='approved'))
    current = [s for s in approved if s.currency_assessment()[0]]
    details = {
        'approved_sources': len(approved),
        'indexed_approved_sources': sum(1 for s in approved if s.is_indexed),
        'current_verified_sources': len(current),
        'sample_sources': sum(1 for s in approved if s.is_sample),
        'index_chunks': None,
        'test_query_results': None,
    }

    collection = _get_collection()
    if collection is None:
        return _save('legal_retrieval', 'fail', 'The ChromaDB legal index could not be opened.', details,
                     triggered_by)
    details['index_chunks'] = collection.count()
    if not details['index_chunks']:
        return _save('legal_retrieval', 'fail',
                     'The legal index is empty. Approve and index legal sources in the admin.', details,
                     triggered_by)

    chunks = retrieve_relevant_chunks('traffic offence notice police summons market eviction', n_results=5)
    details['test_query_results'] = len(chunks)
    details['test_query_current_verified'] = sum(1 for c in chunks if c['metadata'].get('is_current_verified'))
    latency = int((time.monotonic() - start) * 1000)

    if not chunks:
        return _save('legal_retrieval', 'fail', 'The index has content, but a test search returned nothing.',
                     details, triggered_by, latency)
    if not current:
        return _save('legal_retrieval', 'warn',
                     'Search works, but no source is verified as current law (only sample or unverified '
                     'text). Every explanation will say the applicable law cannot be verified.',
                     details, triggered_by, latency)
    return _save('legal_retrieval', 'pass',
                 f"Search works; {len(current)} source(s) verified as current law.", details, triggered_by, latency)


def check_classification(triggered_by=None):
    """D. Classification against synthetic samples with known types."""
    from documents.classification import classify_document
    from documents.samples import SAMPLE_DOCUMENTS

    start = time.monotonic()
    mismatches = []
    for expected, text in SAMPLE_DOCUMENTS:
        got = classify_document(text)['doc_type']
        if got != expected:
            mismatches.append({'expected': expected, 'got': got})
    total = len(SAMPLE_DOCUMENTS)
    correct = total - len(mismatches)
    details = {'samples': total, 'correct': correct, 'mismatches': mismatches}
    latency = int((time.monotonic() - start) * 1000)
    if not mismatches:
        return _save('classification', 'pass', f'All {total} sample documents classified correctly.',
                     details, triggered_by, latency)
    status = 'warn' if correct / total >= 0.8 else 'fail'
    return _save('classification', status, f'{correct} of {total} sample documents classified correctly.',
                 details, triggered_by, latency)


def check_explanation(triggered_by=None):
    """E. Full explanation pipeline on a synthetic document. Uses one AI request."""
    from django.conf import settings
    from documents.classification import classify_document
    from documents.extraction import extract_document_details
    from documents.samples import SAMPLE_DOCUMENTS
    from documents.verification import assess_verification
    from documents.models import VERIFICATION_STATUS_CHOICES
    from .engine import build_document_explanation

    text = dict(SAMPLE_DOCUMENTS)['police_summons']
    classification = classify_document(text)
    details = extract_document_details(text, classification, 0.95)
    status, _guidance = assess_verification(classification, details, text)
    start = time.monotonic()
    try:
        result = build_document_explanation(
            text=text, doc_type=classification['doc_type'], classification=classification,
            details=details, verification_status_label=dict(VERIFICATION_STATUS_CHOICES)[status],
            user_category='general', language='en', purpose='diagnostic_explanation',
        )
    except AIServiceUnavailable as e:
        latency = int((time.monotonic() - start) * 1000)
        return _save('explanation', 'fail', f'The AI request failed: {e.detail or e.category}',
                     {'error_category': e.category}, triggered_by, latency, ai_status=e.category,
                     model_name=getattr(settings, 'OPENAI_MODEL', ''))
    except Exception as e:
        logger.exception('Explanation diagnostic failed')
        return _save('explanation', 'fail', f'The pipeline raised an error: {type(e).__name__}: {e}',
                     {}, triggered_by, ai_status='unknown_error')

    latency = int((time.monotonic() - start) * 1000)
    sections = result['sections']
    expected = ['what_your_document_says', 'what_this_may_mean', 'relevant_ugandan_law',
                'important_details_to_check', 'recommended_next_steps', 'where_to_seek_help']
    present = [k for k in expected if (sections.get(k) or '').strip()]
    info = {
        'sections_present': len(present),
        'sections_expected': len(expected),
        'sources_retrieved': len(result['sources']),
        'current_verified_sources': result['has_current_verified_sources'],
        'safeguards_applied': result['safeguards_applied'],
    }
    model = getattr(settings, 'OPENAI_MODEL', '')
    if len(present) < 4:
        return _save('explanation', 'fail',
                     f'The AI answered, but only {len(present)} of {len(expected)} sections could be read.',
                     info, triggered_by, latency, ai_status='invalid_response', model_name=model)
    if not result['has_current_verified_sources']:
        return _save('explanation', 'warn',
                     'An explanation was generated end to end, but no current verified law was found, so '
                     'the law section shows the uncertainty message.', info, triggered_by, latency,
                     ai_status='operational', model_name=model)
    return _save('explanation', 'pass', 'An explanation was generated end to end with verified sources.',
                 info, triggered_by, latency, ai_status='operational', model_name=model)


def run_all(triggered_by=None, include_connection=True, include_explanation=False) -> list:
    results = []
    if include_connection:
        results.append(run_connection_check(triggered_by))
    results.append(check_ocr(triggered_by))
    results.append(check_legal_retrieval(triggered_by))
    results.append(check_classification(triggered_by))
    if include_explanation:
        results.append(check_explanation(triggered_by))
    return results


def service_overview() -> dict:
    """Latest result per component plus real-request statistics, for the dashboard and API."""
    from django.conf import settings

    latest = {}
    for kind, _label in AIHealthCheck.KIND_CHOICES:
        latest[kind] = AIHealthCheck.objects.filter(kind=kind).first()

    conn = latest['openai_connection']
    last_ok_conn = AIHealthCheck.objects.filter(kind='openai_connection', ai_status='operational').first()
    last_bad_conn = AIHealthCheck.objects.filter(kind='openai_connection').exclude(ai_status='operational').first()

    week = timezone.now() - timedelta(days=7)
    recent = AIRequestLog.objects.filter(created_at__gte=week)
    ok_latencies = list(recent.filter(success=True, latency_ms__isnull=False).values_list('latency_ms', flat=True))
    last_failed = AIRequestLog.objects.filter(success=False).first()
    last_doc_ok = AIRequestLog.objects.filter(
        success=True, purpose__in=('document_explanation', 'diagnostic_explanation')).first()
    last_doc_fail = AIRequestLog.objects.filter(
        success=False, purpose__in=('document_explanation', 'diagnostic_explanation')).first()

    # Document analysis service: confirmed only by an actual end-to-end explanation
    blocking = [k for k in ('ocr', 'legal_retrieval', 'classification')
                if latest[k] and latest[k].component_status == 'fail']
    conn_ok = bool(conn and conn.ai_status == 'operational')
    e2e = latest['explanation']
    e2e_ok_time = max(filter(None, [
        e2e.created_at if e2e and e2e.component_status in ('pass', 'warn') else None,
        last_doc_ok.created_at if last_doc_ok else None,
    ]), default=None)
    e2e_fail_time = max(filter(None, [
        e2e.created_at if e2e and e2e.component_status == 'fail' else None,
        last_doc_fail.created_at if last_doc_fail else None,
    ]), default=None)

    if conn and not conn_ok:
        doc_status, doc_note = 'unavailable', f'OpenAI connection: {conn.get_ai_status_display()}.'
    elif blocking:
        doc_status, doc_note = 'degraded', 'Failing component(s): ' + ', '.join(blocking) + '.'
    elif e2e_ok_time and (not e2e_fail_time or e2e_ok_time > e2e_fail_time):
        warn = any(latest[k] and latest[k].component_status == 'warn'
                   for k in ('ocr', 'legal_retrieval', 'classification', 'explanation'))
        doc_status = 'operational_with_warnings' if warn else 'operational'
        doc_note = 'An explanation was generated end to end.'
    elif e2e_fail_time:
        doc_status, doc_note = 'unavailable', 'The most recent explanation attempt failed.'
    else:
        doc_status, doc_note = 'not_confirmed', ('No explanation has been generated end to end yet. '
                                                 'Run the end-to-end test.')

    return {
        'model': getattr(settings, 'OPENAI_MODEL', ''),
        'api_key_configured': bool(getattr(settings, 'OPENAI_API_KEY', '')),
        'openai': {
            'status': conn.ai_status if conn else 'not_tested',
            'status_label': conn.get_ai_status_display() if conn else 'Not tested yet',
            'summary': conn.summary if conn else '',
            'checks': conn.details if conn else {},
            'last_tested_at': conn.created_at if conn else None,
            'last_successful_test_at': last_ok_conn.created_at if last_ok_conn else None,
            'last_failed_test_at': last_bad_conn.created_at if last_bad_conn else None,
            'last_failed_test_category': last_bad_conn.get_ai_status_display() if last_bad_conn else '',
        },
        'requests_7_days': {
            'total': recent.count(),
            'failed': recent.filter(success=False).count(),
            'average_response_ms': int(sum(ok_latencies) / len(ok_latencies)) if ok_latencies else None,
        },
        'last_failed_request': {
            'at': last_failed.created_at,
            'purpose': last_failed.purpose,
            'category': last_failed.get_error_category_display(),
        } if last_failed else None,
        'document_analysis': {'status': doc_status, 'label': DOC_SERVICE_LABELS[doc_status], 'note': doc_note},
        'components': {
            kind: {
                'label': label,
                'status': latest[kind].component_status if latest[kind] else 'skipped',
                'summary': latest[kind].summary if latest[kind] else 'Not run yet.',
                'at': latest[kind].created_at if latest[kind] else None,
                'latency_ms': latest[kind].latency_ms if latest[kind] else None,
            }
            for kind, label in AIHealthCheck.KIND_CHOICES
        },
    }
