"""Nutrition Service - Food nutrition analysis and calculations using AI"""

from .shared_cache import embedding_store

def get_nutrition_info(food_name, quantity, recipe_generator=None):
    """
    Get nutrition information from unified document in cache or AI model
    
    Args:
        food_name: Name of the food
        quantity: Quantity in grams (will be scaled from 100g base)
        recipe_generator: Hugging Face API recipe generator with AI model access
    
    Returns:
        Dictionary with calories, protein, carbs, fat scaled to the quantity or None
    """
    
    # Check if nutrition data is cached in embeddings store (unified document)
    cached_document = embedding_store.find_similar_recipe(food_name, threshold=0.5)
    if cached_document and cached_document.get("nutrition"):
        nutrition_100g = cached_document["nutrition"]
        print(f"[DEBUG] Found cached nutrition for {food_name}: {nutrition_100g}")
        # Scale to requested quantity
        multiplier = quantity / 100.0
        return {
            "calories": round(nutrition_100g["calories"] * multiplier),
            "protein": round(nutrition_100g["protein"] * multiplier, 1),
            "carbs": round(nutrition_100g["carbs"] * multiplier, 1),
            "fat": round(nutrition_100g["fat"] * multiplier, 1)
        }
    
    # If not cached, fetch from AI model
    if recipe_generator:
        nutrition_100g = fetch_nutrition_from_ai(food_name, recipe_generator)
        if nutrition_100g:
            # Get cached recipe if available and update it with nutrition data
            cached_document = embedding_store.find_similar_recipe(food_name, threshold=0.5)
            recipe_data = cached_document.get("recipe") if cached_document else None
            
            # Store unified document (recipe + nutrition) in embeddings
            embedding_store.add_unified_document(food_name, recipe_data, nutrition_100g)
            print(f"[DEBUG] Cached nutrition for {food_name}: {nutrition_100g}")
            
            # Scale to requested quantity
            multiplier = quantity / 100.0
            return {
                "calories": round(nutrition_100g["calories"] * multiplier),
                "protein": round(nutrition_100g["protein"] * multiplier, 1),
                "carbs": round(nutrition_100g["carbs"] * multiplier, 1),
                "fat": round(nutrition_100g["fat"] * multiplier, 1)
            }
    
    return None

def fetch_nutrition_from_ai(food_name, recipe_generator):
    """
    Fetch nutrition facts per 100g from AI model
    Returns base values that will be scaled by user quantity
    """
    try:
        # Use the recipe generator's underlying model to make a direct API call
        # This is a specialized nutrition-only request, not a recipe
        nutrition_100g = recipe_generator.get_nutrition_facts(food_name)
        
        if nutrition_100g:
            return nutrition_100g
    except Exception as e:
        print(f"[DEBUG] Error fetching nutrition from AI: {e}")
    
    return None

def parse_nutrition_response(text):
    """Parse nutrition data from AI response (per 100g)"""
    try:
        lines = text.split('\n')
        nutrition = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Match "Calories: XXX" or "Calories: XXX kcal"
            if line_lower.startswith('calories'):
                parts = line.split(':')
                if len(parts) > 1:
                    # Extract all digits and decimals
                    value_str = parts[1].strip()
                    value = ''.join(filter(lambda x: x.isdigit() or x == '.', value_str.split()[0]))
                    if value:
                        nutrition['calories'] = float(value)
                        print(f"[DEBUG] Parsed calories: {nutrition['calories']}")
            
            elif line_lower.startswith('protein'):
                parts = line.split(':')
                if len(parts) > 1:
                    value_str = parts[1].strip()
                    value = ''.join(filter(lambda x: x.isdigit() or x == '.', value_str.split()[0]))
                    if value:
                        nutrition['protein'] = float(value)
                        print(f"[DEBUG] Parsed protein: {nutrition['protein']}")
            
            elif line_lower.startswith('carbs') or line_lower.startswith('carbohydrates'):
                parts = line.split(':')
                if len(parts) > 1:
                    value_str = parts[1].strip()
                    value = ''.join(filter(lambda x: x.isdigit() or x == '.', value_str.split()[0]))
                    if value:
                        nutrition['carbs'] = float(value)
                        print(f"[DEBUG] Parsed carbs: {nutrition['carbs']}")
            
            elif line_lower.startswith('fat'):
                parts = line.split(':')
                if len(parts) > 1:
                    value_str = parts[1].strip()
                    value = ''.join(filter(lambda x: x.isdigit() or x == '.', value_str.split()[0]))
                    if value:
                        nutrition['fat'] = float(value)
                        print(f"[DEBUG] Parsed fat: {nutrition['fat']}")
        
        # Validate we have all required fields
        if all(key in nutrition for key in ['calories', 'protein', 'carbs', 'fat']):
            print(f"[DEBUG] Successfully parsed nutrition: {nutrition}")
            return nutrition
        else:
            print(f"[DEBUG] Missing nutrition fields. Got: {list(nutrition.keys())}")
    
    except Exception as e:
        print(f"[DEBUG] Error parsing nutrition: {e}")
    
    return None
