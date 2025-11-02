"""Nutrition Calculator - Food nutrition analysis"""

from models import show_step

def get_nutrition_info(food_name, quantity):
    """Get nutrition information"""
    show_step("Calculating nutrition information...")
    
    # Basic nutrition database
    nutrition_db = {
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
        "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
        "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3.2},
        "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
        "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1},
        "potato": {"calories": 77, "protein": 2, "carbs": 17, "fat": 0.1}
    }
    
    # Find matching nutrition data
    food_key = food_name.lower()
    base_nutrition = None
    
    for key, data in nutrition_db.items():
        if key in food_key or food_key in key:
            base_nutrition = data
            break
    
    if base_nutrition:
        # Calculate for given quantity (base is per 100g)
        multiplier = quantity / 100
        nutrition = {
            "calories": round(base_nutrition["calories"] * multiplier),
            "protein": round(base_nutrition["protein"] * multiplier, 1),
            "carbs": round(base_nutrition["carbs"] * multiplier, 1),
            "fat": round(base_nutrition["fat"] * multiplier, 1)
        }
        show_step("Nutrition calculated!", "success")
        return nutrition
    else:
        show_step("Nutrition data not available for this food", "warning")
        return None
