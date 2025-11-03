"""Cache Migration - Convert old separate recipe/nutrition format to unified documents"""

import json
import os
from .shared_cache import embedding_store


def migrate_cache_to_unified_format():
    """
    Migrate existing cache from old format (separate recipe and nutrition documents)
    to new unified format (single document with both recipe + nutrition).
    
    This function:
    1. Identifies documents with nutrition_{food_name} keys (old nutrition format)
    2. Pairs them with their corresponding recipe documents
    3. Creates unified documents combining both
    4. Updates metadata and FAISS index
    """
    print("[DEBUG] Starting cache migration to unified format...")
    
    try:
        metadata = embedding_store.metadata
        food_names = embedding_store.food_names
        migrated_count = 0
        
        # Collect nutrition and recipe entries
        nutrition_entries = {}
        recipe_entries = {}
        
        for key in list(metadata.keys()):
            if key.startswith("nutrition_"):
                # Extract food name from nutrition key
                food_name = key.replace("nutrition_", "").lower().strip()
                nutrition_entries[food_name] = metadata[key]
            else:
                # This is a recipe entry
                recipe_entries[key] = metadata[key]
        
        # Pair and merge nutrition data into recipe documents
        for food_name, nutrition_data in nutrition_entries.items():
            if food_name in recipe_entries:
                # Found matching recipe, merge nutrition into it
                recipe_entry = recipe_entries[food_name]
                recipe_entry["nutrition"] = nutrition_data.get("nutrition")
                metadata[food_name]["nutrition"] = nutrition_data.get("nutrition")
                
                # Remove old nutrition entry
                nutrition_key = f"nutrition_{food_name}"
                if nutrition_key in metadata:
                    del metadata[nutrition_key]
                if nutrition_key in food_names:
                    food_names.remove(nutrition_key)
                
                migrated_count += 1
                print(f"[DEBUG] Migrated nutrition for '{food_name}' into unified document")
            else:
                # No matching recipe, just convert nutrition entry to recipe entry with nutrition field
                recipe_entry = {
                    "food_name": nutrition_data.get("food_name", food_name),
                    "recipe": None,
                    "nutrition": nutrition_data.get("nutrition"),
                    "timestamp": nutrition_data.get("timestamp"),
                    "index_id": nutrition_data.get("index_id")
                }
                # Remove old nutrition entry
                nutrition_key = f"nutrition_{food_name}"
                if nutrition_key in metadata:
                    del metadata[nutrition_key]
                    metadata[food_name] = recipe_entry
                if nutrition_key in food_names:
                    food_names_idx = food_names.index(nutrition_key)
                    food_names[food_names_idx] = food_name
                
                migrated_count += 1
                print(f"[DEBUG] Converted standalone nutrition entry for '{food_name}' to unified format")
        
        # Update the embedding store's metadata
        embedding_store.metadata = metadata
        embedding_store.food_names = food_names
        
        # Save the migrated cache
        embedding_store._save_store()
        
        print(f"[DEBUG] Cache migration complete! Migrated {migrated_count} entries to unified format")
        return True
    
    except Exception as e:
        print(f"[DEBUG] Error during cache migration: {e}")
        return False


def check_migration_needed():
    """Check if cache migration is needed (old format detected)"""
    try:
        metadata = embedding_store.metadata
        for key in metadata.keys():
            if key.startswith("nutrition_"):
                print("[DEBUG] Old cache format detected, migration needed")
                return True
        print("[DEBUG] Cache is already in unified format or empty")
        return False
    except Exception as e:
        print(f"[DEBUG] Error checking migration status: {e}")
        return False
