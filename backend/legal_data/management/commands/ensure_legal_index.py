"""Ensure the ChromaDB index exists, without re-seeding the database."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from legal_data.models import LegalSource
from legal_data.vector_store import _get_collection, index_legal_source


class Command(BaseCommand):
    help = (
        'Index approved legal sources into ChromaDB only when the collection is '
        'empty. Useful on ephemeral hosts where the vector store is lost on '
        'restart but PostgreSQL is not.'
    )

    def handle(self, *args, **options):
        collection = _get_collection()
        if collection is None:
            self.stderr.write(self.style.WARNING(
                'ChromaDB unavailable — legal index was not rebuilt.'
            ))
            return

        if collection.count() > 0:
            self.stdout.write('Legal index already populated — skipping.')
            return

        sources = LegalSource.objects.filter(status='approved').exclude(
            legal_status='repealed'
        )
        indexed = 0
        for source in sources:
            ids = index_legal_source(source)
            if ids:
                source.is_indexed = True
                source.indexed_at = timezone.now()
                source.chroma_doc_ids = ids
                source.save(update_fields=['is_indexed', 'indexed_at', 'chroma_doc_ids'])
                indexed += len(ids)

        self.stdout.write(self.style.SUCCESS(
            f'Legal index rebuilt: {indexed} chunks from {sources.count()} sources.'
        ))
