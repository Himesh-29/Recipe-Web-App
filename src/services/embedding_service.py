"""Embedding Service - Generate and manage recipe embeddings wi        # Initialize embedding model with Streamlit caching
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print(f"[DEBUG] Loading embedding model: {model_name}")
            if load_sentence_transformer:
                self.model = load_sentence_transformer(model_name)  # Streamlit cached
            else:
                self.model = get_model(model_name)  # Manual cache
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        else:
            print("[WARNING] SentenceTransformer not available")ector DB"""

import json
import os
import numpy as np
import pickle
from pathlib import Path

# Add Streamlit caching for better performance
try:
    import streamlit as st
    @st.cache_resource
    def load_sentence_transformer(model_name):
        """Cache model loading in Streamlit"""
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name)
except ImportError:
    load_sentence_transformer = None

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARNING] FAISS not installed. Install with: pip install faiss-cpu")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[WARNING] sentence-transformers not installed. Install with: pip install sentence-transformers")


# Global model cache for Streamlit
_model_cache = {}

def get_model(model_name="all-MiniLM-L6-v2"):
    """Get or create cached model"""
    if model_name not in _model_cache:
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache.get(model_name)


class EmbeddingStore:
    """Store and retrieve recipe embeddings using FAISS vector database"""
    
    def __init__(self, 
                 store_dir="src/data",
                 model_name="all-MiniLM-L6-v2"):
        """
        Initialize embedding store with FAISS and sentence transformers
        
        Args:
            store_dir: Directory to store embeddings and metadata
            model_name: Hugging Face model for embeddings (lightweight: all-MiniLM-L6-v2)
        """
        self.store_dir = store_dir
        self.metadata_path = os.path.join(store_dir, "metadata.json")
        self.index_path = os.path.join(store_dir, "faiss_index")
        self.food_names_path = os.path.join(store_dir, "food_names.pkl")
        
        # Initialize embedding model
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print(f"[DEBUG] Loading embedding model: {model_name}")
            self.model = get_model(model_name)  # Use cached model
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        else:
            print("[WARNING] SentenceTransformer not available")
        
        # Initialize FAISS index
        self.index = None
        self.food_names = []
        self.metadata = {}
        
        os.makedirs(store_dir, exist_ok=True)
        self._load_store()
    
    def _load_store(self):
        """Load FAISS index and metadata from disk"""
        try:
            # Load FAISS index
            if FAISS_AVAILABLE and os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"[DEBUG] Loaded FAISS index with {self.index.ntotal} recipes")
            else:
                # Create new empty index
                if FAISS_AVAILABLE:
                    self.index = faiss.IndexFlatL2(self.embedding_dim)
                    print(f"[DEBUG] Created new FAISS index")
            
            # Load food names
            if os.path.exists(self.food_names_path):
                with open(self.food_names_path, 'rb') as f:
                    self.food_names = pickle.load(f)
                print(f"[DEBUG] Loaded {len(self.food_names)} food names")
            
            # Load metadata
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print(f"[DEBUG] Loaded metadata for {len(self.metadata)} recipes")
        
        except Exception as e:
            print(f"[DEBUG] Error loading store: {e}")
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.food_names = []
            self.metadata = {}
    
    def _save_store(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            if FAISS_AVAILABLE and self.index is not None:
                faiss.write_index(self.index, self.index_path)
            
            # Save food names
            with open(self.food_names_path, 'wb') as f:
                pickle.dump(self.food_names, f)
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            print(f"[DEBUG] Saved store with {len(self.food_names)} recipes")
        
        except Exception as e:
            print(f"[DEBUG] Error saving store: {e}")
    
    def _generate_embedding(self, text):
        """Generate embedding using sentence transformer"""
        if not self.model:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"[DEBUG] Error generating embedding: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def add_unified_document(self, food_name, recipe_data, nutrition_data=None):
        """
        Add unified recipe + nutrition document to FAISS index
        
        Args:
            food_name: Name of the food
            recipe_data: Recipe dictionary with name, ingredients, instructions, quantity
            nutrition_data: Optional nutrition dictionary with calories, protein, carbs, fat (per 100g)
        """
        if not FAISS_AVAILABLE or not self.index or not self.model:
            print("[WARNING] FAISS or SentenceTransformer not available")
            return False
        
        try:
            # Generate embedding from food name (semantic key for retrieval)
            embedding = self._generate_embedding(food_name)
            embedding = embedding.reshape(1, -1)
            
            # Add to FAISS index
            self.index.add(embedding)
            
            # Store unified document in metadata
            key = food_name.lower().strip()
            self.food_names.append(key)
            self.metadata[key] = {
                "food_name": food_name,
                "recipe": recipe_data,
                "nutrition": nutrition_data,
                "timestamp": str(__import__('datetime').datetime.now()),
                "index_id": self.index.ntotal - 1
            }
            
            # Save to disk
            self._save_store()
            print(f"[DEBUG] Added unified document for '{food_name}' (recipe + nutrition) to FAISS index")
            return True
        
        except Exception as e:
            print(f"[DEBUG] Error adding unified document: {e}")
            return False
    
    def add_recipe(self, food_name, recipe_data):
        """Add recipe to FAISS index with metadata (legacy method - now unified)"""
        if not FAISS_AVAILABLE or not self.index or not self.model:
            print("[WARNING] FAISS or SentenceTransformer not available")
            return False
        
        try:
            # Generate embedding
            embedding = self._generate_embedding(food_name)
            embedding = embedding.reshape(1, -1)
            
            # Add to FAISS index
            self.index.add(embedding)
            
            # Store metadata
            key = food_name.lower().strip()
            self.food_names.append(key)
            self.metadata[key] = {
                "food_name": food_name,
                "recipe": recipe_data,
                "nutrition": None,
                "timestamp": str(__import__('datetime').datetime.now()),
                "index_id": self.index.ntotal - 1
            }
            
            # Save to disk
            self._save_store()
            print(f"[DEBUG] Added recipe '{food_name}' to FAISS index")
            return True
        
        except Exception as e:
            print(f"[DEBUG] Error adding recipe: {e}")
            return False
    
    def find_similar_recipe(self, query_food_name, k=1, threshold=0.6):
        """
        Find similar unified document (recipe + nutrition) using FAISS similarity search
        
        Args:
            query_food_name: Food name to search for
            k: Number of similar results to return
            threshold: Similarity threshold (0-1, where 1 is identical)
        
        Returns:
            Dictionary with 'recipe' and 'nutrition' keys, or None
        """
        if not self.index or not self.model or self.index.ntotal == 0:
            print(f"[DEBUG] Index empty or unavailable")
            return None
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query_food_name)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search in FAISS
            distances, indices = self.index.search(query_embedding, k)
            
            # Check if best match exceeds threshold
            if distances[0][0] < threshold:  # Lower distance = better match
                best_idx = indices[0][0]
                best_food_name = self.food_names[best_idx]
                document = self.metadata[best_food_name]
                
                print(f"[DEBUG] Found similar document for '{query_food_name}': '{best_food_name}' (distance: {distances[0][0]:.4f})")
                return {
                    "recipe": document.get("recipe"),
                    "nutrition": document.get("nutrition")
                }
            
            print(f"[DEBUG] No similar document found for '{query_food_name}' (best distance: {distances[0][0]:.4f})")
            return None
        
        except Exception as e:
            print(f"[DEBUG] Error searching index: {e}")
            return None
    
    def get_all_recipes(self):
        """Get all cached recipes"""
        recipes = {}
        for key, data in self.metadata.items():
            recipes[key] = data["recipe"]
        return recipes
    
    def get_stats(self):
        """Get store statistics"""
        return {
            "total_recipes": len(self.food_names),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "model_available": self.model is not None
        }
    
    def clear_store(self):
        """Clear all recipes from store AND delete cached files"""
        try:
            # Clear in-memory data
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.food_names = []
            self.metadata = {}
            
            # Delete cached files from disk
            import os
            try:
                if os.path.exists(self.index_path):
                    os.remove(self.index_path)
                    print(f"[DEBUG] Deleted FAISS index file: {self.index_path}")
            except Exception as e:
                print(f"[DEBUG] Error deleting FAISS index: {e}")
            
            try:
                if os.path.exists(self.food_names_path):
                    os.remove(self.food_names_path)
                    print(f"[DEBUG] Deleted food names file: {self.food_names_path}")
            except Exception as e:
                print(f"[DEBUG] Error deleting food names: {e}")
            
            try:
                if os.path.exists(self.metadata_path):
                    os.remove(self.metadata_path)
                    print(f"[DEBUG] Deleted metadata file: {self.metadata_path}")
            except Exception as e:
                print(f"[DEBUG] Error deleting metadata: {e}")
            
            print("[DEBUG] Cleared embeddings store and deleted all cached files")
            return True
        except Exception as e:
            print(f"[DEBUG] Error clearing store: {e}")
            return False

