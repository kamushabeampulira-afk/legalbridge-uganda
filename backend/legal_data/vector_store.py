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


def index_legal_source(source) -> list:
    """
    Chunk and index a LegalSource into ChromaDB.
    Returns list of ChromaDB document IDs.
    """
    collection = _get_collection()
    if collection is None:
        logger.error('ChromaDB not available; cannot index legal source.')
        return []

    if not source.full_text:
        logger.warning(f'No text to index for source: {source.id}')
        return []

    chunks = _chunk_text(source.full_text, chunk_size=800, overlap=100)
    doc_ids = []

    for i, chunk in enumerate(chunks):
        doc_id = f"{source.id}__chunk_{i}"
        metadata = {
            'source_id': str(source.id),
            'title': source.title[:200],
            'short_title': (source.short_title or source.title)[:100],
            'subject': source.subject,
            'category': source.category,
            'issuing_authority': source.issuing_authority[:200] if source.issuing_authority else '',
            'source_url': source.source_url[:500] if source.source_url else '',
            'publication_date': str(source.publication_date) if source.publication_date else '',
            'chunk_index': i,
        }
        try:
            collection.upsert(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[metadata],
            )
            doc_ids.append(doc_id)
        except Exception as e:
            logger.error(f'Failed to index chunk {i} of source {source.id}: {e}')

    logger.info(f'Indexed {len(doc_ids)} chunks for source: {source.title}')
    return doc_ids


def retrieve_relevant_chunks(query: str, subject_filter: Optional[str] = None, n_results: int = 5) -> list:
    """
    Retrieve the most relevant legal text chunks for a user query.
    Returns a list of dicts with 'text', 'metadata', 'distance'.
    """
    collection = _get_collection()
    if collection is None:
        logger.error('ChromaDB not available; cannot retrieve chunks.')
        return []

    try:
        where = {'subject': subject_filter} if subject_filter else None
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, max(1, collection.count())),
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

        # Filter out low-relevance chunks (cosine distance > 0.7 means poor match)
        chunks = [c for c in chunks if c['distance'] < 0.7]
        return chunks

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
