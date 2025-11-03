"""TheMealDB API Client - Free recipe database with 1000+ real meals"""

import requests

class TheMealDBClient:
    """Client for TheMealDB API - Free recipe lookup"""
    
    def __init__(self):
        """Initialize TheMealDB client with free API key"""
        self.base_url = "https://www.themealdb.com/api/json/v1/1"
        self.api_key = "1"  # Free public test key
        print(f"[DEBUG] TheMealDB Client initialized with free API key")
    
    def search_meal_by_name(self, food_name):
        """
        Search for a meal by name
        
        Args:
            food_name: Name of the meal (e.g., "Arrabiata", "Garlic Bread")
        
        Returns:
            Meal data dict or None if not found
        """
        try:
            url = f"{self.base_url}/search.php?s={food_name}"
            print(f"[DEBUG] Searching TheMealDB for: {food_name}")
            print(f"[DEBUG] URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"[DEBUG] TheMealDB Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('meals') and len(data['meals']) > 0:
                    meal = data['meals'][0]  # Get first result
                    print(f"[DEBUG] Found meal: {meal['strMeal']}")
                    return meal
                else:
                    print(f"[DEBUG] No meal found for: {food_name}")
            else:
                print(f"[DEBUG] TheMealDB Error: {response.status_code}")
                
        except Exception as e:
            print(f"[DEBUG] TheMealDB search error: {e}")
        
        return None
    
    def parse_meal_to_recipe(self, meal, quantity=100):
        """
        Convert TheMealDB meal response to recipe format
        
        Args:
            meal: Meal dict from TheMealDB API
            quantity: Quantity in grams (for display)
        
        Returns:
            Recipe dict with name, ingredients, instructions, quantity
        """
        try:
            recipe_name = meal.get('strMeal', 'Recipe')
            
            # Extract ingredients and measurements
            ingredients = []
            for i in range(1, 21):  # TheMealDB has up to 20 ingredients
                ingredient_key = f'strIngredient{i}'
                measure_key = f'strMeasure{i}'
                
                ingredient = meal.get(ingredient_key, '').strip()
                measure = meal.get(measure_key, '').strip()
                
                if ingredient:  # Only add if ingredient exists
                    if measure:
                        ingredients.append(f"{measure} {ingredient}")
                    else:
                        ingredients.append(ingredient)
            
            # Extract instructions
            instructions_text = meal.get('strInstructions', '')
            # Split by periods or numbers to create steps
            instructions = []
            if instructions_text:
                # Try to split by numbered format first
                steps = instructions_text.split('. ')
                for step in steps:
                    step = step.strip()
                    if step and len(step) > 10:  # Only reasonable steps
                        # Remove leading numbers if present
                        if step[0].isdigit() and '.' in step[:3]:
                            step = step.split('.', 1)[1].strip()
                        instructions.append(step)
            
            # Limit to 12 ingredients and 10 steps
            ingredients = ingredients[:12]
            instructions = instructions[:10]
            
            if ingredients and instructions:
                print(f"[DEBUG] Parsed meal: {len(ingredients)} ingredients, {len(instructions)} steps")
                return {
                    "name": recipe_name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "quantity": f"{quantity}g",
                    "source": "TheMealDB"  # Track source
                }
        
        except Exception as e:
            print(f"[DEBUG] Error parsing meal data: {e}")
        
        return None
    
    def get_recipe(self, food_name, quantity=100):
        """
        Get complete recipe for a food
        
        Args:
            food_name: Name of the food/meal
            quantity: Quantity in grams
        
        Returns:
            Recipe dict or None if not found
        """
        meal = self.search_meal_by_name(food_name)
        if meal:
            recipe = self.parse_meal_to_recipe(meal, quantity)
            if recipe:
                print(f"[DEBUG] Successfully fetched recipe from TheMealDB: {food_name}")
                return recipe
        
        print(f"[DEBUG] Recipe not found in TheMealDB: {food_name}")
        return None
