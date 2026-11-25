import logging
import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()


def _warm_up():
    """Load the legal search model now, so the first user's question does not wait for it.

    On a small server (e.g. Render's free 0.1 CPU) loading the embedding model takes
    far longer than answering, and it otherwise happens during someone's first question.
    """
    try:
        from legal_data.vector_store import retrieve_relevant_chunks
        retrieve_relevant_chunks('driving licence', n_results=1)
        logging.getLogger('legalbridge').info('Warm-up finished: legal search is ready.')
    except Exception:  # a failed warm-up must never stop the server
        logging.getLogger('legalbridge').exception('Warm-up failed')


if os.environ.get('WARM_UP_ON_START', '').strip().lower() in ('1', 'true', 'yes'):
    threading.Thread(target=_warm_up, name='warm-up', daemon=True).start()
