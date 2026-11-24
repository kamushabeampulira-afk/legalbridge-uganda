"""
Management command: python manage.py import_ulii_pdf <pdf> --subject <subject> [options]

Imports an Act downloaded as a PDF from ULII (ulii.org / Laws.Africa) into a
LegalSource with one LegalProvision per section.

- The source is created as "Pending Review". It is NOT approved or indexed here:
  an admin must review it and run "Approve and index selected sources".
- Every section listed in the PDF's table of contents must be found in the body,
  otherwise nothing is saved.
- Repealed sections (shown as *** in ULII PDFs) are skipped.
- Sections are stored as provisions; full_text holds only the long title and the
  schedules, so the same text is not indexed twice.

Use --dry-run first to check the result without saving anything.
"""
import os
import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from legal_data.models import LegalSource, LegalProvision

LIGATURES = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl'}
FOOTER = 'By Ulii.org and Laws.Africa. Share widely and freely.'
SECTION_NUM = re.compile(r'^(\d+[A-Z]{0,2})\.$')
TOC_ENTRY = re.compile(r'^(.*?)\s*\.{4,}\s*\S+$')
TOC_SECTION = re.compile(r'^(\d+[A-Z]{0,2})\.\s+(.*)$')
SCHEDULE = re.compile(r'^((First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+)?Schedule\b')
MARKER = re.compile(r'^\((?:\d+[a-z]*|[a-z]{1,2}|[ivxlcdm]+)\)$')
DATE = r'(\d{1,2} [A-Z][a-z]+ \d{4})'


def _norm(text):
    return ' '.join(text.split())


def _date(text):
    try:
        return datetime.strptime(text, '%d %B %Y').date()
    except (TypeError, ValueError):
        return None


def _page_lines(page_text):
    """Lines of one page without the running header and the ULII footer."""
    for bad, good in LIGATURES.items():
        page_text = page_text.replace(bad, good)
    lines = [ln.rstrip() for ln in page_text.splitlines()]
    if len(lines) >= 2 and re.search(r'\(Chapter \d+\)\s*$', lines[0]) and lines[1].strip() == 'Uganda':
        lines = lines[2:]
    for i, ln in enumerate(lines):
        if ln.strip() == FOOTER:
            lines = lines[:i]
            break
    return [ln for ln in lines if ln.strip()]


def _reflow(lines):
    """Join PDF lines into readable paragraphs: one per subsection/paragraph marker."""
    paras, cur, after_marker = [], '', False
    for line in lines:
        s = line.strip()
        if MARKER.match(s):
            if after_marker:
                cur += ' ' + s
                continue
            if cur:
                paras.append(cur)
            cur, after_marker = s, True
        elif after_marker:
            cur, after_marker = cur + ' ' + s, False
        elif not cur or s.startswith('[') or cur.endswith((';', ':', '—', '.', ']')):
            if cur:
                paras.append(cur)
            cur = s
        elif cur.endswith('-'):
            cur += s
        else:
            cur += ' ' + s
    if cur:
        paras.append(cur)
    return '\n'.join(paras)


def parse_ulii_pdf(path):
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    pages = [_page_lines(page.get_text()) for page in doc]
    first_page = pages[0]
    lines = [ln for page in pages for ln in page]

    # The body starts at the first line that is just "1." (TOC lines carry the title on the same line).
    try:
        body_start = next(i for i, ln in enumerate(lines) if SECTION_NUM.match(ln.strip())
                          and SECTION_NUM.match(ln.strip()).group(1) == '1')
    except StopIteration:
        raise CommandError('Could not find section 1 in the PDF. Is this a ULII Act PDF?')
    front = lines[:body_start]
    front_text = _norm(' '.join(front))

    # Table of contents
    toc_sections, headings, schedules = [], set(), []
    for ln in front:
        m = TOC_ENTRY.match(ln.strip())
        if not m:
            continue
        entry = _norm(m.group(1))
        sm = TOC_SECTION.match(entry)
        if sm:
            toc_sections.append((sm.group(1), sm.group(2)))
        elif SCHEDULE.match(entry):
            schedules.append(entry)
        elif entry != 'Contents':
            headings.add(entry)
    if not toc_sections:
        raise CommandError('No table of contents found in the PDF.')

    # Metadata from the cover and the start of the body
    meta = {
        'title': first_page[1].strip() if len(first_page) > 1 else os.path.basename(path),
        'chapter': None, 'as_at': None, 'frbr': None, 'publication_date': None,
        'effective_date': None, 'amendments': [], 'long_title': '',
    }
    if m := re.search(r'Chapter (\d+)', ' '.join(first_page[:4])):
        meta['chapter'] = m.group(1)
    if m := re.search(r'Legislation as at ' + DATE, front_text):
        meta['as_at'] = m.group(1)
    if m := re.search(r'FRBR URI: (\S+)', front_text):
        meta['frbr'] = m.group(1)
    if m := re.search(r'Published in .+? on ' + DATE, front_text):
        meta['publication_date'] = _date(m.group(1))
    if m := re.search(r'[Cc]ommenced on ' + DATE, front_text):
        meta['effective_date'] = _date(m.group(1))
    meta['amendments'] = re.findall(r'\[Amended by (.+?) on ' + DATE + r'\]', front_text)
    if m := re.search(r'(An Act to .+?)(?: \[Act | Part I )', front_text + ' Part I '):
        meta['long_title'] = m.group(1).strip()

    # Body: split into sections, then schedules
    toc_numbers = [num for num, _ in toc_sections]
    toc_titles = dict(toc_sections)
    schedule_set = set(schedules)
    sections, schedule_blocks, warnings = [], [], []
    current, next_idx = None, 0
    body = lines[body_start:]
    i = 0
    while i < len(body):
        s = _norm(body[i])
        if s in schedule_set:
            current = {'heading': s, 'lines': []}
            schedule_blocks.append(current)
            i += 1
            continue
        m = SECTION_NUM.match(s)
        if (m and not schedule_blocks and m.group(1) in toc_numbers[next_idx:next_idx + 3]):
            number = m.group(1)
            next_idx = toc_numbers.index(number) + 1
            expected = _norm(toc_titles[number])
            # The title may wrap onto several lines; consume lines until they match the TOC title.
            title, consumed = _norm(body[i + 1]) if i + 1 < len(body) else '', 1
            while title != expected and consumed < 4 and i + consumed + 1 < len(body) \
                    and len(title) < len(expected):
                consumed += 1
                title = _norm(title + ' ' + body[i + consumed])
            if title != expected:
                warnings.append(f's.{number}: title in text "{_norm(body[i + 1])}" '
                                f'differs from contents "{expected}"; used the first line.')
                title, consumed = _norm(body[i + 1]), 1
            current = {'number': number, 'title': title, 'lines': []}
            sections.append(current)
            i += consumed + 1
            continue
        if current is not None and s not in headings:
            current['lines'].append(body[i])
        i += 1

    found = {sec['number'] for sec in sections}
    missing = [num for num in toc_numbers if num not in found and toc_titles[num].strip() != '***']
    provisions, repealed = [], []
    for sec in sections:
        text = _reflow(sec['lines'])
        if sec['title'] == '***':
            repealed.append(sec['number'])
            continue
        if not text:
            warnings.append(f's.{sec["number"]}: no text found.')
        provisions.append({'section_number': sec['number'], 'section_title': sec['title'], 'text': text})

    schedule_text = [f"{blk['heading']}\n{_reflow(blk['lines'])}" for blk in schedule_blocks]
    return {
        'meta': meta, 'provisions': provisions, 'repealed': repealed, 'missing': missing,
        'schedules': schedule_text, 'warnings': warnings, 'toc_count': len(toc_sections),
    }


class Command(BaseCommand):
    help = 'Import an Act from a ULII PDF as a Pending Review legal source with one provision per section.'

    def add_arguments(self, parser):
        parser.add_argument('pdf', help='Path to the PDF downloaded from ulii.org')
        parser.add_argument('--subject', required=True, choices=[c for c, _ in LegalSource.SUBJECT_CHOICES])
        parser.add_argument('--category', default='act', choices=[c for c, _ in LegalSource.CATEGORY_CHOICES])
        parser.add_argument('--title', help='Override the title read from the PDF')
        parser.add_argument('--short-title', default='')
        parser.add_argument('--summary', default='', help='Plain-language summary')
        parser.add_argument('--issuing-authority', default='Parliament of Uganda')
        parser.add_argument('--legal-status', default='unknown',
                            choices=[c for c, _ in LegalSource.LEGAL_STATUS_CHOICES])
        parser.add_argument('--replace', action='store_true',
                            help='Replace an existing source with the same instrument number '
                                 '(resets it to Pending Review and removes it from the index)')
        parser.add_argument('--dry-run', action='store_true', help='Parse and report, save nothing')
        parser.add_argument('--show', help='With --dry-run, print the full text of this section number')

    def handle(self, *args, **opts):
        path = opts['pdf']
        if not os.path.isfile(path):
            raise CommandError(f'File not found: {path}')
        result = parse_ulii_pdf(path)
        meta = result['meta']

        instrument = ''
        if meta['frbr'] and (m := re.match(r'/akn/ug/act/(\d{4})/(\d+)', meta['frbr'])):
            instrument = f'Act No. {m.group(2)} of {m.group(1)}'
            if meta['chapter']:
                instrument += f'; Cap. {meta["chapter"]}'
        title = opts['title'] or meta['title']
        source_url = f"https://ulii.org{meta['frbr']}" if meta['frbr'] else ''

        last_amendment = meta['amendments'][-1][0] if meta['amendments'] else ''
        version = f"ULII text as at {meta['as_at']}" if meta['as_at'] else 'ULII text'
        if last_amendment:
            version += f'; last amended by {last_amendment}'
        amendment_list = '; '.join(f'{a} ({d})' for a, d in meta['amendments']) or 'none listed'
        notes = (
            f"Imported {timezone.now().date().isoformat()} from the ULII/Laws.Africa PDF "
            f"{os.path.basename(path)} (FRBR URI {meta['frbr'] or 'unknown'}). "
            f"Text extracted automatically: spot-check sections against the PDF before approving. "
            f"Amendments applied in this version: {amendment_list}. "
            f"Repealed sections not imported: {', '.join(result['repealed']) or 'none'}."
        )
        full_text = (
            'Sections of this Act are stored separately as Legal provisions (one per section). '
            'This field holds the long title and the schedules.\n\n'
            + (f"Long title: {meta['long_title']}\n\n" if meta['long_title'] else '')
            + '\n\n'.join(result['schedules'])
        ).strip()

        self.stdout.write(f'\n{title}  [{instrument or "no instrument number found"}]')
        self.stdout.write(f'  Source URL:        {source_url or "-"}')
        self.stdout.write(f'  Version:           {version}')
        self.stdout.write(f"  Published / commenced: {meta['publication_date'] or '-'} / {meta['effective_date'] or '-'}")
        self.stdout.write(f"  Contents entries:  {result['toc_count']}")
        self.stdout.write(f"  Sections to import: {len(result['provisions'])}")
        self.stdout.write(f"  Repealed (skipped): {len(result['repealed'])} {result['repealed']}")
        self.stdout.write(f"  Schedules:         {len(result['schedules'])}")
        for w in result['warnings']:
            self.stdout.write(self.style.WARNING(f'  ! {w}'))
        if result['missing']:
            raise CommandError(f"Sections listed in the contents but not found in the text: {result['missing']}. "
                               'Nothing was saved.')

        if opts['dry_run']:
            if opts['show']:
                prov = next((p for p in result['provisions'] if p['section_number'] == opts['show']), None)
                if prov:
                    self.stdout.write(f"\n--- s.{prov['section_number']} {prov['section_title']} ---\n{prov['text']}\n")
                else:
                    self.stdout.write(f"\nSection {opts['show']} not found (or repealed).")
            self.stdout.write(self.style.SUCCESS('\nDry run: nothing saved.'))
            return

        existing = LegalSource.objects.filter(instrument_number=instrument).first() if instrument else None
        if existing is None:
            existing = LegalSource.objects.filter(title=title).first()
        if existing and not opts['replace']:
            raise CommandError(f'"{existing.title}" already exists. Use --replace to overwrite it.')

        fields = {
            'title': title, 'short_title': opts['short_title'], 'instrument_number': instrument,
            'category': opts['category'], 'subject': opts['subject'],
            'issuing_authority': opts['issuing_authority'],
            'publication_date': meta['publication_date'], 'effective_date': meta['effective_date'],
            'source_url': source_url, 'version_or_amendment': version[:200],
            'legal_status': opts['legal_status'], 'is_sample': False, 'status': 'pending_review',
            'full_text': full_text, 'summary': opts['summary'], 'verification_notes': notes,
            'reviewed_by': None, 'last_verified_at': None,
            'is_indexed': False, 'indexed_at': None, 'chroma_doc_ids': [],
        }
        with transaction.atomic():
            if existing:
                from legal_data.vector_store import remove_source_from_index
                remove_source_from_index(str(existing.id))
                existing.provisions.all().delete()
                for key, value in fields.items():
                    setattr(existing, key, value)
                existing.save()
                source = existing
            else:
                source = LegalSource.objects.create(**fields)
            LegalProvision.objects.bulk_create(
                [LegalProvision(source=source, **p) for p in result['provisions']])

        self.stdout.write(self.style.SUCCESS(
            f"\n{'Replaced' if existing else 'Created'} \"{source.title}\" with "
            f"{len(result['provisions'])} provisions, status Pending Review.\n"
            'Next: review it in the admin, then run "Approve and index selected sources".'))
