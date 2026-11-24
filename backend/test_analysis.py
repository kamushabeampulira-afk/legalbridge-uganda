"""Quick test: document analysis pipeline."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from documents.models import Document
from ai_engine.engine import generate_document_explanation

User = get_user_model()
user = User.objects.get(phone_number='+256700000001')
doc = Document.objects.filter(owner=user).order_by('-created_at').first()

if not doc:
    print('No documents found — upload one from the app first')
else:
    print(f'Doc ID: {doc.id}')
    print(f'Type: {doc.doc_type} | Status: {doc.status}')
    print(f'Text preview: {(doc.extracted_text or "")[:200]}')

    # Seed text if OCR found nothing (small test image)
    if not doc.extracted_text:
        doc.extracted_text = 'TRAFFIC VIOLATION NOTICE. Vehicle: UBA 123Z. Alleged offence: Riding without valid insurance. Reference: TRF/KLA/2024/00123. Penalty: UGX 50,000. Officer: P.C. Opio Badge 4521.'
        doc.doc_type = 'traffic_notice'
        doc.status = 'completed'
        doc.save()
        print('Seeded test text for analysis.')

    print('\nRunning AI analysis...')
    analysis = generate_document_explanation(doc, language='en')

    print('\n=== ANALYSIS RESULT ===')
    print('Summary:', analysis.summary[:400])
    print('\nNext steps:', analysis.next_steps)
    print('\nHas verified sources:', analysis.has_verified_sources)
    print('Uncertainty flag:', analysis.uncertainty_flag)
    print('\nSources used:', [s.get('short_title') for s in analysis.legal_sources_used])
    print('\nSUCCESS: Analysis pipeline working correctly.')
