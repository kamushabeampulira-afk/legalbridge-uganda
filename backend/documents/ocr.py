"""
LegalBridge — OCR and document text extraction module.

Supports:
- PDF text extraction via PyMuPDF
- Image OCR via Tesseract
- Basic image pre-processing via OpenCV/Pillow
"""
import io
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger('legalbridge')


def extract_text_from_file(file_path: str) -> dict:
    """
    Main entry point. Accepts a file path and returns a dict:
    {
        'text': str,
        'confidence': float | None,
        'warnings': list[str],
        'method': str,
    }
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.pdf':
        return _extract_pdf(file_path)
    elif suffix in ('.jpg', '.jpeg', '.png', '.tiff', '.bmp'):
        return _extract_image(file_path)
    else:
        return {
            'text': '',
            'confidence': None,
            'warnings': [f'Unsupported file type: {suffix}'],
            'method': 'none',
        }


def _extract_pdf(file_path: str) -> dict:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        full_text = '\n'.join(pages_text).strip()

        if len(full_text) < 50:
            # PDF may be scanned — fall back to image OCR on first page
            return _extract_pdf_as_image(file_path)

        return {
            'text': full_text,
            'confidence': 0.95,
            'warnings': [],
            'method': 'pymupdf',
        }
    except Exception as e:
        logger.error(f'PDF extraction failed: {e}')
        return {
            'text': '',
            'confidence': None,
            'warnings': [f'PDF extraction failed: {str(e)}'],
            'method': 'pymupdf_failed',
        }


def _extract_pdf_as_image(file_path: str) -> dict:
    """Render first page of PDF as image, then OCR it."""
    try:
        import fitz
        doc = fitz.open(file_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes('png')
        doc.close()
        return _ocr_image_bytes(img_bytes, source='pdf_render')
    except Exception as e:
        logger.error(f'PDF-as-image OCR failed: {e}')
        return {
            'text': '',
            'confidence': None,
            'warnings': ['Could not render PDF for OCR. The document may be protected or corrupted.'],
            'method': 'pdf_ocr_failed',
        }


def _extract_image(file_path: str) -> dict:
    """Pre-process image and run Tesseract OCR."""
    try:
        with open(file_path, 'rb') as f:
            img_bytes = f.read()
        return _ocr_image_bytes(img_bytes, source='image')
    except Exception as e:
        logger.error(f'Image OCR failed: {e}')
        return {
            'text': '',
            'confidence': None,
            'warnings': [f'Image OCR failed: {str(e)}'],
            'method': 'ocr_failed',
        }


def _ocr_image_bytes(img_bytes: bytes, source: str = 'image') -> dict:
    """Run Tesseract OCR on raw image bytes with pre-processing."""
    warnings = []
    try:
        import pytesseract
        from PIL import Image
        import numpy as np

        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')

        # Pre-processing: convert to numpy, greyscale, threshold
        try:
            import cv2
            img_array = np.array(image)
            grey = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            # Adaptive thresholding improves OCR on low-quality scans
            processed = cv2.adaptiveThreshold(
                grey, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            image = Image.fromarray(processed)
        except ImportError:
            warnings.append('OpenCV not available; using basic image without pre-processing.')

        # Run OCR — try English + Luganda (if language pack installed)
        try:
            data = pytesseract.image_to_data(
                image,
                lang='eng',
                output_type=pytesseract.Output.DICT
            )
            confidences = [int(c) for c in data['conf'] if str(c).lstrip('-').isdigit() and int(c) >= 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            text = pytesseract.image_to_string(image, lang='eng')

            if avg_confidence < 50:
                warnings.append(
                    'OCR confidence is low. The document image may be unclear, '
                    'blurry or damaged. Some text may have been misread.'
                )

            return {
                'text': text.strip(),
                'confidence': round(avg_confidence / 100, 2),
                'warnings': warnings,
                'method': f'tesseract_{source}',
            }
        except Exception as te:
            warnings.append(f'Tesseract OCR error: {str(te)}. Tesseract may not be installed.')
            return {
                'text': '',
                'confidence': None,
                'warnings': warnings,
                'method': 'tesseract_error',
            }

    except Exception as e:
        return {
            'text': '',
            'confidence': None,
            'warnings': [f'Image processing failed: {str(e)}'],
            'method': 'image_failed',
        }


# ------------------------------------------------------------------
# Field extraction helpers
# ------------------------------------------------------------------

def extract_key_fields(text: str) -> dict:
    """
    Extract common key fields from OCR'd legal document text.
    Returns dates, amounts (UGX), names, and reference numbers.
    These are heuristic — results must be verified by the user.
    """
    dates = _extract_dates(text)
    amounts = _extract_amounts(text)
    refs = _extract_references(text)

    return {
        'dates': dates,
        'amounts': amounts,
        'reference_numbers': refs,
    }


def _extract_dates(text: str) -> list:
    patterns = [
        r'\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b',
        r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
        r'\s+\d{2,4}\b',
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text, re.IGNORECASE))
    return list(set(found))


def _extract_amounts(text: str) -> list:
    patterns = [
        r'UGX\s?[\d,]+',
        r'Shs\.?\s?[\d,]+',
        r'Uganda Shillings\s?[\d,]+',
        r'[\d,]+/[=\-]',  # e.g. 50,000/=
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text, re.IGNORECASE))
    return list(set(found))


def _extract_references(text: str) -> list:
    patterns = [
        r'Ref(?:erence)?[\s#.:]*([A-Z0-9\-/]+)',
        r'Case\s+No\.?\s*([A-Z0-9\-/]+)',
        r'Receipt\s+No\.?\s*([A-Z0-9\-/]+)',
        r'Notice\s+No\.?\s*([A-Z0-9\-/]+)',
        r'File\s+No\.?\s*([A-Z0-9\-/]+)',
    ]
    found = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        found.extend(matches)
    return list(set(found))


def classify_document_type(text: str) -> str:
    """
    Return the doc_type code for the text. Kept for backwards compatibility;
    the classifier lives in documents.classification (see classify_document).
    """
    from .classification import classify_document_type as _classify
    return _classify(text)
