"""
LegalBridge — ChromaDB vector store for RAG pipeline.
Manages indexing and retrieval of verified Ugandan legal documents.
"""
from __future__ import annotations
import logging
import uuid
from typing import Optional
from django.conf import settings

logger = logging.getLogger('legalbridge')

_client = None
_collection = None


def _get_collection():
    """Lazily initialise the ChromaDB client and collection."""
    global _client, _collection
    if _collection is not None:
        return _collection

    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
        )
        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'},
        )
        logger.info(f'ChromaDB collection ready: {settings.CHROMA_COLLECTION_NAME}')
        return _collection
    except Exception as e:
        logger.error(f'ChromaDB initialisation failed: {e}')
        return None


MAX_RELEVANT_DISTANCE = 0.7  # cosine distance; larger means a poor match


def _source_metadata(source) -> dict:
    """Citation metadata stored with every chunk (ChromaDB only accepts str/int/float/bool)."""
    return {
        'source_id': str(source.id),
        'title': source.title[:200],
        'short_title': (source.short_title or source.title)[:100],
        'instrument_number': (source.instrument_number or '')[:200],
        'subject': source.subject,
        'category': source.category,
        'issuing_authority': (source.issuing_authority or '')[:200],
        'source_url': (source.source_url or '')[:500],
        'publication_date': str(source.publication_date or ''),
        'commencement_date': str(source.effective_date or ''),
        'legal_status': source.legal_status,
        'is_sample': bool(source.is_sample),
        'last_verified_at': source.last_verified_at.date().isoformat() if source.last_verified_at else '',
        'section_number': '',
        'section_title': '',
        'provision_id': '',
    }


def index_legal_source(source) -> list:
    """
    Index a LegalSource into ChromaDB: its full text in overlapping chunks, plus
    each LegalProvision as its own chunk so results can cite a specific section.
    Returns the list of ChromaDB document IDs.
    """
    collection = _get_collection()
    if collection is None:
        logger.error('ChromaDB not available; cannot index legal source.')
        return []

    base = _source_metadata(source)
    entries = []  # (id, text, metadata)

    if source.full_text:
        for i, chunk in enumerate(_chunk_text(source.full_text, chunk_size=800, overlap=100)):
            entries.append((f'{source.id}__chunk_{i}', chunk, {**base, 'chunk_index': i}))

    for provision in source.provisions.all():
        heading = f'Section {provision.section_number}' if provision.section_number else 'Provision'
        if provision.section_title:
            heading += f': {provision.section_title}'
        entries.append((
            f'{source.id}__prov_{provision.id}',
            f'{heading}\n{provision.text}',
            {**base, 'section_number': provision.section_number[:50],
             'section_title': provision.section_title[:200], 'provision_id': str(provision.id),
             'chunk_index': -1},
        ))

    if not entries:
        logger.warning(f'No text to index for source: {source.id}')
        return []

    doc_ids = []
    for doc_id, text, metadata in entries:
        try:
            collection.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])
            doc_ids.append(doc_id)
        except Exception as e:
            logger.error(f'Failed to index {doc_id}: {e}')

    logger.info(f'Indexed {len(doc_ids)} chunks for source: {source.title}')
    return doc_ids


def _refresh_from_database(chunks: list) -> list:
    """
    Re-check every retrieved chunk against the current LegalSource record, since
    the index may be stale. Drops sources that are no longer approved or are
    repealed, and attaches is_current_verified + currency_warnings to the rest.
    """
    from legal_data.models import LegalSource

    ids = {c['metadata'].get('source_id') for c in chunks if c['metadata'].get('source_id')}
    sources = {str(s.id): s for s in LegalSource.objects.filter(id__in=ids)}
    refreshed = []
    for chunk in chunks:
        source = sources.get(chunk['metadata'].get('source_id'))
        if source is None or source.status != 'approved' or source.legal_status == 'repealed':
            continue
        is_current, warnings = source.currency_assessment()
        meta = {**chunk['metadata'], **{k: v for k, v in _source_metadata(source).items()
                                        if k not in ('section_number', 'section_title', 'provision_id')}}
        meta['is_current_verified'] = is_current
        meta['currency_warnings'] = warnings
        refreshed.append({**chunk, 'metadata': meta})
    return refreshed


def retrieve_relevant_chunks(query: str, subject_filter: Optional[str] = None, n_results: int = 5,
                             subjects: Optional[list] = None) -> list:
    """
    Retrieve the most relevant legal text chunks for a query.
    `subjects` (a list) searches several subjects at once; `subject_filter` is a single subject.
    Returns dicts with 'text', 'metadata' (including is_current_verified and
    currency_warnings from the database), 'distance' and 'relevance_score'.
    """
    collection = _get_collection()
    if collection is None:
        logger.error('ChromaDB not available; cannot retrieve chunks.')
        return []

    try:
        if subjects:
            where = {'subject': {'$in': list(subjects)}} if len(subjects) > 1 else {'subject': subjects[0]}
        elif subject_filter:
            where = {'subject': subject_filter}
        else:
            where = None

        total = collection.count()
        if total == 0:
            return []
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, total),
            where=where,
            include=['documents', 'metadatas', 'distances'],
        )

        chunks = []
        if results and results.get('documents'):
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0],
            ):
                chunks.append({
                    'text': doc,
                    'metadata': meta,
                    'distance': dist,
                    'relevance_score': round(1 - dist, 3),
                })

        chunks = [c for c in chunks if c['distance'] < MAX_RELEVANT_DISTANCE]
        return _refresh_from_database(chunks)

    except Exception as e:
        logger.error(f'ChromaDB retrieval failed: {e}')
        return []


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def remove_source_from_index(source_id: str):
    """Remove all chunks for a legal source from ChromaDB."""
    collection = _get_collection()
    if collection is None:
        return
    try:
        collection.delete(where={'source_id': str(source_id)})
        logger.info(f'Removed index entries for source: {source_id}')
    except Exception as e:
        logger.error(f'Failed to remove source {source_id} from index: {e}')


def collection_count() -> int:
    collection = _get_collection()
    if collection is None:
        return 0
    try:
        return collection.count()
    except Exception:
        return 0
