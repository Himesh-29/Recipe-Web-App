"""Nutrition Calculator - Food nutrition analysis"""

from models import show_step

def get_nutrition_info(food_name, quantity):
    """Get nutrition information"""
    show_step("Calculating nutrition information...")
    
    # Basic nutrition database (per 100g)
    nutrition_db = {
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
        "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
        "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3.2},
        "garlic bread": {"calories": 350, "protein": 8.5, "carbs": 42, "fat": 16},
        "garlic_bread": {"calories": 350, "protein": 8.5, "carbs": 42, "fat": 16},
        "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
        "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1},
        "potato": {"calories": 77, "protein": 2, "carbs": 17, "fat": 0.1},
        "pizza": {"calories": 266, "protein": 11, "carbs": 33, "fat": 10},
        "salad": {"calories": 15, "protein": 1, "carbs": 3, "fat": 0.2},
        "fish": {"calories": 206, "protein": 22, "carbs": 0, "fat": 12},
        "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15},
        "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33}
    }
    
    # Find matching nutrition data
    food_key = food_name.lower().replace(' ', '_')
    base_nutrition = None
    
    # Try exact match first
    if food_key in nutrition_db:
        base_nutrition = nutrition_db[food_key]
    else:
        # Try partial match
        for key, data in nutrition_db.items():
            if key in food_key or food_key.replace('_', ' ') in key or key in food_key.replace('_', ' '):
                base_nutrition = data
                break
    
    if base_nutrition:
        # Calculate for given quantity (base is per 100g)
        multiplier = quantity / 100.0
        nutrition = {
            "calories": round(base_nutrition["calories"] * multiplier),
            "protein": round(base_nutrition["protein"] * multiplier, 1),
            "carbs": round(base_nutrition["carbs"] * multiplier, 1),
            "fat": round(base_nutrition["fat"] * multiplier, 1)
        }
        show_step(f"Nutrition calculated for {quantity}g!", "success")
        return nutrition
    else:
        show_step("Nutrition data not available for this food", "warning")
        return None
