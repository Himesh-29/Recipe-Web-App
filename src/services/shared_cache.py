"""Shared Cache - Single instance of EmbeddingStore for all services"""

from .embedding_service import EmbeddingStore

# Single shared instance - initialized once and reused everywhere
# This prevents duplicate model loading and FAISS initialization
embedding_store = EmbeddingStore()
