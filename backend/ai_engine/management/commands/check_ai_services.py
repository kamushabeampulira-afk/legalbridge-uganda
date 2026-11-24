"""
python manage.py check_ai_services [--connection-only] [--end-to-end] [--list-models]

Tests each part of the document-analysis pipeline separately:
  A. OpenAI connection   B. OCR   C. Legal retrieval   D. Classification
  E. End-to-end explanation (only with --end-to-end; uses one AI request)
Results are saved and shown on the admin "AI service status" page. No API key is printed.
"""
from django.core.management.base import BaseCommand

from ai_engine import diagnostics
from ai_engine.openai_service import run_connection_check

SYMBOL = {'pass': 'PASS', 'warn': 'WARN', 'fail': 'FAIL', 'skipped': 'SKIP'}


class Command(BaseCommand):
    help = 'Test the OpenAI connection and each document-analysis component separately.'

    def add_arguments(self, parser):
        parser.add_argument('--connection-only', action='store_true', help='Only test the OpenAI connection.')
        parser.add_argument('--end-to-end', action='store_true',
                            help='Also generate one explanation end to end (uses one AI request).')
        parser.add_argument('--list-models', action='store_true',
                            help='List the models the configured key can use (no AI request is made).')

    def handle(self, *args, **options):
        if options['list_models']:
            return self.list_models()
        if options['connection_only']:
            results = [run_connection_check()]
        else:
            results = diagnostics.run_all(include_connection=True, include_explanation=options['end_to_end'])

        for r in results:
            line = f"[{SYMBOL[r.component_status]}] {r.get_kind_display()}: {r.summary}"
            style = {'pass': self.style.SUCCESS, 'warn': self.style.WARNING}.get(r.component_status, self.style.ERROR)
            self.stdout.write(style(line))
            if r.kind == 'openai_connection':
                self.stdout.write(f"       status: {r.get_ai_status_display()} | model: {r.model_name}"
                                  + (f" | {r.latency_ms} ms" if r.latency_ms is not None else ''))
                for key, value in r.details.items():
                    if key != 'time_limit_ms':
                        shown = 'yes' if value is True else 'no' if value is False else 'not reached'
                        self.stdout.write(f"       - {key.replace('_', ' ')}: {shown}")

        overview = diagnostics.service_overview()['document_analysis']
        self.stdout.write(f"\nDocument analysis service: {overview['label']}. {overview['note']}")

    def list_models(self):
        from ai_engine.openai_service import classify_error, get_client, is_configured
        if not is_configured():
            self.stdout.write(self.style.ERROR('OPENAI_API_KEY is not set in backend/.env.'))
            return
        try:
            ids = sorted(m.id.removeprefix('models/') for m in get_client(timeout=20, max_retries=0).models.list())
        except Exception as exc:
            category, detail = classify_error(exc)
            self.stdout.write(self.style.ERROR(f'Could not list models ({category}): {detail}'))
            return
        for model_id in ids:
            self.stdout.write(model_id)
        self.stdout.write(f'\n{len(ids)} model(s). Put the one you want in OPENAI_MODEL in backend/.env.')
