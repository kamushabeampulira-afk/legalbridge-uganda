"""
Draft missing app translations with Sunbird AI's translation model.

The mobile app's text lives in two kinds of file:
  mobile/i18n/locales/<code>.json   screens and buttons (key -> text)
  mobile/i18n/content/<code>.json   Know Your Rights guides (English text -> text)

English and Luganda are written by hand. This command fills in entries that are
missing for Runyankore (nyn), Acholi (ach) and Lugbara (lgg) using Sunbird AI,
whose models are trained on Ugandan languages. Existing entries are kept unless
--overwrite is given. Machine translations are drafts: have a native speaker
review them before release.

A translation that drops a number (a section, a fee, a number of days) or a
name such as "Markets Act" is not saved; the app shows the English instead.

  python manage.py translate_app_text --check
  python manage.py translate_app_text --language lgg --limit 5 --dry-run
  python manage.py translate_app_text --language lgg
"""
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

LANGUAGES = {'nyn': 'Runyankore', 'ach': 'Acholi', 'lgg': 'Lugbara'}

# Names and codes that must come through translation unchanged.
PROTECTED_TERMS = (
    'LegalBridge', 'USSD', 'UNBS', 'KCCA', 'JPG', 'PNG', 'PDF', 'UGX', 'MB', 'Class M',
    'Markets Act', 'Traffic and Road Safety', 'Uganda National Bureau of Standards',
)
NUMBER = re.compile(r'\d+')
# English/Luganda pairs in mobile/constants/LegalRights.ts.
GUIDE_TEXT = re.compile(r"\ben:\s*'((?:[^'\\]|\\.)*)',\s*lg:\s*'((?:[^'\\]|\\.)*)'", re.S)
RETRY_STATUSES = {429, 502, 503}
MAX_ATTEMPTS = 4
SAVE_EVERY = 20


@dataclass
class Catalog:
    name: str
    source: dict          # key -> English text to translate, in display order
    folder: Path          # where <code>.json lives
    keys: tuple = ()      # every key the app knows, including names that stay in English

    def path(self, language):
        return self.folder / f'{language}.json'

    @property
    def known_keys(self):
        return self.keys or tuple(self.source)


def _read_json(path):
    if not path.exists():
        return {}
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def _unescape(text):
    return re.sub(r'\\(.)', r'\1', text)


def load_catalogs(mobile_dir: Path):
    """The English source text of each catalog, without names that are not translated."""
    locales = mobile_dir / 'i18n' / 'locales'
    english = _read_json(locales / 'en.json')
    luganda = _read_json(locales / 'lg.json')
    if not english:
        raise CommandError(f'No English strings found at {locales / "en.json"}.')
    # A string written the same in English and Luganda is a name (LegalBridge, Boda Boda).
    ui = {key: text for key, text in english.items() if luganda.get(key) != text}

    guides = {}
    rights_file = mobile_dir / 'constants' / 'LegalRights.ts'
    if rights_file.exists():
        for en, lg in GUIDE_TEXT.findall(rights_file.read_text(encoding='utf-8')):
            en, lg = _unescape(en), _unescape(lg)
            if en != lg:  # official titles of Acts stay in English
                guides.setdefault(en, en)

    return [
        Catalog('screens', ui, locales, keys=tuple(english)),
        Catalog('rights guides', guides, mobile_dir / 'i18n' / 'content'),
    ]


def translation_problem(source, translated):
    """Why a machine translation must not be used, or None if it looks safe."""
    if not translated or not translated.strip():
        return 'empty translation'
    missing_numbers = sorted(set(NUMBER.findall(source)) - set(NUMBER.findall(translated)), key=int)
    if missing_numbers:
        return f'numbers missing: {", ".join(missing_numbers)}'
    missing_terms = [term for term in PROTECTED_TERMS if term in source and term not in translated]
    if missing_terms:
        return f'names missing: {", ".join(missing_terms)}'
    return None


class Command(BaseCommand):
    help = 'Draft missing Runyankore, Acholi and Lugbara app text with Sunbird AI.'

    def add_arguments(self, parser):
        parser.add_argument('--language', action='append', choices=sorted(LANGUAGES),
                            help='Language to fill in (repeatable). Default: all three.')
        parser.add_argument('--check', action='store_true',
                            help='Only report how much of each language is translated.')
        parser.add_argument('--limit', type=int, default=0,
                            help='Translate at most this many strings per language.')
        parser.add_argument('--overwrite', action='store_true',
                            help='Replace existing translations too (default: only fill gaps).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Show translations without saving them.')
        parser.add_argument('--delay', type=float, default=0.3,
                            help='Seconds to wait between requests.')
        parser.add_argument('--mobile-dir', help='Path to the mobile app (default: ../mobile).')

    def handle(self, *args, **options):
        mobile_dir = Path(options['mobile_dir'] or Path(settings.BASE_DIR).parent / 'mobile')
        catalogs = load_catalogs(mobile_dir)
        languages = options['language'] or list(LANGUAGES)

        if options['check']:
            for language in languages:
                self._report(language, catalogs)
            return

        self.token = getattr(settings, 'SUNBIRD_API_TOKEN', '')
        if not self.token:
            raise CommandError(
                'SUNBIRD_API_TOKEN is not set. Register at https://api.sunbird.ai/register, '
                'copy your token from https://api.sunbird.ai/keys and add it to backend/.env.')
        self.url = getattr(settings, 'SUNBIRD_API_URL', 'https://api.sunbird.ai').rstrip('/') + '/tasks/translate'
        self.timeout = getattr(settings, 'SUNBIRD_TIMEOUT_SECONDS', 120)
        self.delay = max(0.0, options['delay'])

        for language in languages:
            self._translate_language(language, catalogs, options)

    # ── Reporting ────────────────────────────────────────────────────────────

    def _report(self, language, catalogs):
        self.stdout.write(self.style.MIGRATE_HEADING(f'{LANGUAGES[language]} ({language})'))
        for catalog in catalogs:
            existing = _read_json(catalog.path(language))
            done = sum(1 for key in catalog.source if existing.get(key))
            self.stdout.write(f'  {catalog.name}: {done}/{len(catalog.source)} translated')
            unknown = [key for key in existing if key not in catalog.known_keys]
            if unknown:
                self.stdout.write(self.style.WARNING(
                    f'  {len(unknown)} entries no longer match the English text and are not shown:'))
                for key in unknown[:10]:
                    self.stdout.write(f'    - {key[:90]}')

    # ── Translation ──────────────────────────────────────────────────────────

    def _translate_language(self, language, catalogs, options):
        self.stdout.write(self.style.MIGRATE_HEADING(f'{LANGUAGES[language]} ({language})'))
        budget = options['limit'] or None
        saved = rejected = 0

        for catalog in catalogs:
            path = catalog.path(language)
            existing = _read_json(path)
            todo = [(key, text) for key, text in catalog.source.items()
                    if options['overwrite'] or not existing.get(key)]
            if budget is not None:
                if budget <= 0:
                    break
                todo = todo[:budget]
                budget -= len(todo)
            if not todo:
                self.stdout.write(f'  {catalog.name}: nothing to translate')
                continue
            self.stdout.write(f'  {catalog.name}: translating {len(todo)} strings...')

            pending = 0
            for key, text in todo:
                translated = self._translate(text, language)
                problem = translation_problem(text, translated)
                if problem:
                    rejected += 1
                    self.stdout.write(self.style.WARNING(f'    skipped {key[:60]!r}: {problem}'))
                    continue
                existing[key] = translated.strip()
                saved += 1
                pending += 1
                if options['dry_run']:
                    self.stdout.write(f'    {text[:70]}\n      -> {translated.strip()[:70]}')
                elif pending >= SAVE_EVERY:
                    _write_json(path, self._ordered(existing, catalog))
                    pending = 0
                if self.delay:
                    time.sleep(self.delay)

            if not options['dry_run']:
                _write_json(path, self._ordered(existing, catalog))

        verb = 'would save' if options['dry_run'] else 'saved'
        self.stdout.write(self.style.SUCCESS(
            f'  {verb} {saved} translations; {rejected} skipped (shown in English).'))
        if saved and not options['dry_run']:
            self.stdout.write('  These are machine drafts: ask a native speaker to review them.')

    @staticmethod
    def _ordered(existing, catalog):
        """Entries in the same order as the English, then any that no longer match it."""
        ordered = {key: existing[key] for key in catalog.known_keys if key in existing}
        ordered.update((key, value) for key, value in existing.items() if key not in ordered)
        return ordered

    def _translate(self, text, language):
        body = {'source_language': 'eng', 'target_language': language, 'text': text}
        headers = {'Authorization': f'Bearer {self.token}'}
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = requests.post(self.url, json=body, headers=headers, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt == MAX_ATTEMPTS:
                    raise CommandError(f'Could not reach Sunbird AI: {type(exc).__name__}') from exc
                time.sleep(5 * attempt)
                continue

            if response.status_code == 401:
                raise CommandError('Sunbird AI rejected the token (401). Check SUNBIRD_API_TOKEN.')
            if response.status_code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                wait = response.headers.get('Retry-After', '')
                time.sleep(min(float(wait), 60) if wait.replace('.', '', 1).isdigit() else 5 * attempt)
                continue
            if response.status_code != 200:
                raise CommandError(
                    f'Sunbird AI returned HTTP {response.status_code}: {response.text[:200]}')

            data = response.json()
            output = data.get('output') or {}
            if data.get('status') == 'FAILED' or not isinstance(output, dict):
                return ''
            return output.get('translated_text') or output.get('text') or ''
        return ''
