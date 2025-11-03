"""Recipe Service - AI-powered recipe creation with RAG caching and TheMealDB integration"""

from .shared_cache import embedding_store
from ..api.themealdb_client import TheMealDBClient

# Initialize TheMealDB client
themealdb = TheMealDBClient()

def generate_recipe_with_ai(food_name, quantity, recipe_generator, detected_ingredients=None):
    """Generate recipe using smart flow: RAG Cache → TheMealDB → AI API"""
    
    # Step 1: Check if recipe exists in embeddings (unified document with both recipe + nutrition)
    cached_document = embedding_store.find_similar_recipe(food_name)
    if cached_document and cached_document.get("recipe"):
        print(f"[DEBUG] Serving cached recipe for '{food_name}'")
        return cached_document["recipe"]
    
    # Step 2: Try TheMealDB first (real recipes, free, reliable)
    recipe = themealdb.get_recipe(food_name, quantity)
    if recipe:
        # Get nutrition data if available from cache or generation
        nutrition_data = None
        if cached_document and cached_document.get("nutrition"):
            nutrition_data = cached_document["nutrition"]
        
        # Store unified document (recipe + nutrition) in embeddings for future use
        embedding_store.add_unified_document(food_name, recipe, nutrition_data)
        print(f"[DEBUG] Using TheMealDB recipe for '{food_name}'")
        return recipe
    
    # Step 3: Fall back to AI API (for unique foods not in TheMealDB)
    recipe = generate_with_ai_api(food_name, quantity, recipe_generator, detected_ingredients)
    if recipe:
        # Get nutrition data if available from cache or generation
        nutrition_data = None
        if cached_document and cached_document.get("nutrition"):
            nutrition_data = cached_document["nutrition"]
        
        # Store unified document (recipe + nutrition) in embeddings for future use
        embedding_store.add_unified_document(food_name, recipe, nutrition_data)
        print(f"[DEBUG] Using AI-generated recipe for '{food_name}'")
        return recipe
    
    return None

def generate_with_ai_api(food_name, quantity, recipe_generator, detected_ingredients=None):
    """Use API for better recipe generation"""
    
    try:
        # Use detected ingredients or common ones
        ingredients = detected_ingredients or ["salt", "pepper", "oil", "onion", "garlic"]
        
        # Generate recipe using API
        generated_text = recipe_generator.generate_recipe(food_name, ingredients)
        
        if generated_text:
            # Parse the API response
            recipe = parse_ai_recipe(generated_text, food_name, quantity)
            if recipe:
                return recipe
        
    except Exception as e:
        print(f"[DEBUG] AI API Exception: {e}")  # Internal logging
    
    # No fallback - return None to show error
    return None

def parse_ai_recipe(text, food_name, quantity):
    """Parse AI generated recipe text"""
    try:
        lines = text.split('\n')
        ingredients = []
        instructions = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_lower = line.lower()
            if 'ingredient' in line_lower and ':' in line:
                current_section = 'ingredients'
                continue
            elif 'instruction' in line_lower or 'method' in line_lower or 'step' in line_lower:
                current_section = 'instructions'
                continue
            elif 'tip' in line_lower or 'note' in line_lower or 'variation' in line_lower:
                # Stop parsing when we hit tips/notes section
                break
                
            # Parse ingredients
            if current_section == 'ingredients':
                if line.startswith(('-', '•', '*')):
                    ingredient = line[1:].strip()
                    # Skip lines that are tips or notes
                    if not any(keyword in ingredient.lower() for keyword in ['you can', 'for an extra', 'to make', 'simply', 'note:', 'tip:']):
                        ingredients.append(ingredient)
                elif line[0].isdigit() or line.startswith('1/') or line.startswith('½'):
                    # Lines starting with quantities
                    if not any(keyword in line.lower() for keyword in ['you can', 'for an extra', 'to make', 'simply']):
                        ingredients.append(line)
            
            # Parse instructions
            elif current_section == 'instructions':
                # Look for numbered steps or detailed instructions
                if len(line) > 15:  # Reasonable instruction length
                    # Remove step numbers if present
                    cleaned = line
                    if line[0].isdigit() and '.' in line[:3]:
                        cleaned = line.split('.', 1)[1].strip()
                    
                    # Skip tips in instructions
                    if not any(keyword in cleaned.lower() for keyword in ['you can also', 'for an extra', 'to make ahead', 'tip:', 'note:']):
                        instructions.append(cleaned)
        
        if ingredients and instructions:
            return {
                "name": f"{food_name.title()} Recipe",
                "ingredients": ingredients[:12],  # Limit to 12 ingredients
                "instructions": instructions[:10],  # Limit to 10 steps
                "quantity": f"{quantity}g"
            }
    
    except Exception as e:
        print(f"[DEBUG] Recipe parsing error: {e}")
    
    return None
