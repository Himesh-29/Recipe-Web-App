"""RAG Manager - Retrieval-Augmented Generation with FAISS vector database"""

from .shared_cache import embedding_store


class RAGManager:
    """Centralized RAG management with semantic similarity search"""
    
    def __init__(self):
        """Initialize RAG manager with shared embedding store"""
        # Use the shared embedding store instance (already initialized in shared_cache)
        self.embedding_store = embedding_store
    
    def retrieve(self, query, k=1, threshold=0.6):
        """
        Retrieve unified document (recipe + nutrition) from vector database
        
        Args:
            query: Food name to search for
            k: Number of results
            threshold: Similarity threshold
        
        Returns:
            Dictionary with 'recipe' and 'nutrition' keys, or None
        """
        return self.embedding_store.find_similar_recipe(query, k=k, threshold=threshold)
    
    def store_unified(self, food_name, recipe_data, nutrition_data=None):
        """Store unified document (recipe + nutrition) with semantic embeddings"""
        return self.embedding_store.add_unified_document(food_name, recipe_data, nutrition_data)
    
    def store(self, food_name, recipe_data):
        """Store recipe with semantic embeddings (legacy method - use store_unified for new code)"""
        return self.embedding_store.add_recipe(food_name, recipe_data)
    
    def get_stats(self):
        """Get RAG statistics"""
        stats = self.embedding_store.get_stats()
        return {
            "total_cached_recipes": stats["total_recipes"],
            "index_size": stats["index_size"],
            "embedding_dimension": stats["embedding_dim"],
            "model_available": stats["model_available"]
        }
    
    def clear_cache(self):
        """Clear all cached recipes"""
        return self.embedding_store.clear_store()


# Global RAG manager instance with semantic search
rag_manager = RAGManager()
