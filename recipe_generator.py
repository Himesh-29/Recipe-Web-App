"""Recipe Generation - Web scraping and AI-powered recipe creation"""

import requests
from bs4 import BeautifulSoup
import re
from transformers import pipeline
from models import show_step

def generate_recipe_with_ai(food_name, quantity, recipe_generator):
    """Generate recipe using web scraping and AI models"""
    
    # Try web scraping first for real recipes
    recipe = scrape_recipe_from_web(food_name, quantity)
    if recipe:
        return recipe
    
    # Fallback to better AI generation
    return generate_with_better_ai(food_name, quantity)

def scrape_recipe_from_web(food_name, quantity):
    """Scrape recipes from recipe websites"""
    show_step("Searching for recipes online...")
    
    try:
        # Search on AllRecipes or similar recipe sites
        search_query = f"{food_name} recipe"
        search_url = f"https://www.allrecipes.com/search/results/?search={search_query.replace(' ', '%20')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for recipe links
        recipe_links = soup.find_all('a', href=re.compile(r'/recipe/'))
        
        if recipe_links:
            # Get the first recipe
            first_recipe_url = "https://www.allrecipes.com" + recipe_links[0]['href']
            recipe = scrape_allrecipes_page(first_recipe_url, quantity)
            if recipe:
                show_step("Recipe found online!", "success")
                return recipe
        
        # Try BBC Good Food as backup
        return scrape_bbc_recipes(food_name, quantity)
        
    except Exception as e:
        show_step(f"Web scraping failed: {e}", "warning")
        return None

def scrape_allrecipes_page(url, quantity):
    """Scrape specific recipe from AllRecipes"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract recipe name
        title_elem = soup.find('h1', class_='headline heading-content')
        recipe_name = title_elem.text.strip() if title_elem else "Delicious Recipe"
        
        # Extract ingredients
        ingredients = []
        ingredient_elems = soup.find_all('span', class_='recipe-ingred_txt')
        for elem in ingredient_elems:
            ingredient_text = elem.text.strip()
            if ingredient_text:
                ingredients.append(ingredient_text)
        
        # Extract instructions
        instructions = []
        instruction_elems = soup.find_all('span', class_='recipe-directions__list--item')
        for elem in instruction_elems:
            instruction_text = elem.text.strip()
            if instruction_text and len(instruction_text) > 10:
                instructions.append(instruction_text)
        
        if ingredients and instructions:
            return {
                "name": recipe_name,
                "ingredients": ingredients[:12],  # Limit to 12 ingredients
                "instructions": instructions[:8],  # Limit to 8 steps
                "quantity": f"{quantity}g serving"
            }
        
    except Exception as e:
        show_step(f"AllRecipes scraping failed: {e}", "warning")
    
    return None

def scrape_bbc_recipes(food_name, quantity):
    """Scrape BBC Good Food as backup"""
    try:
        search_url = f"https://www.bbcgoodfood.com/search?q={food_name.replace(' ', '%20')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for recipe cards
        recipe_links = soup.find_all('a', class_='link')
        
        for link in recipe_links[:3]:  # Try first 3 results
            if '/recipes/' in link.get('href', ''):
                recipe_url = "https://www.bbcgoodfood.com" + link['href']
                recipe = scrape_bbc_recipe_page(recipe_url, quantity)
                if recipe:
                    return recipe
        
    except Exception as e:
        show_step(f"BBC scraping failed: {e}", "warning")
    
    return None

def scrape_bbc_recipe_page(url, quantity):
    """Scrape specific BBC recipe page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1')
        recipe_name = title_elem.text.strip() if title_elem else "BBC Recipe"
        
        # Extract ingredients
        ingredients = []
        ingredient_elems = soup.find_all('li', class_='pb-xxs')
        for elem in ingredient_elems:
            text = elem.text.strip()
            if text and len(text) > 3:
                ingredients.append(text)
        
        # Extract method
        instructions = []
        method_elems = soup.find_all('li', class_='pb-xs')
        for elem in method_elems:
            text = elem.text.strip()
            if text and len(text) > 10:
                instructions.append(text)
        
        if ingredients and instructions:
            return {
                "name": recipe_name,
                "ingredients": ingredients[:10],
                "instructions": instructions[:6],
                "quantity": f"{quantity}g serving"
            }
        
    except Exception as e:
        pass
    
    return None

def generate_with_better_ai(food_name, quantity):
    """Use better AI model for recipe generation"""
    show_step("Generating with advanced AI model...")
    
    try:
        # Use a better text generation model
        generator = pipeline("text-generation", 
                           model="microsoft/DialoGPT-large", 
                           max_length=512,
                           do_sample=True,
                           temperature=0.7)
        
        # Better structured prompt
        prompt = f"""Recipe: {food_name.title()}
Serving size: {quantity}g

Ingredients:
- """
        
        result = generator(prompt, max_length=400, num_return_sequences=1, pad_token_id=50256)
        generated_text = result[0]['generated_text']
        
        # Better parsing
        recipe = parse_ai_recipe(generated_text, food_name, quantity)
        if recipe:
            show_step("AI recipe generated!", "success")
            return recipe
        
    except Exception as e:
        show_step(f"Advanced AI failed: {e}", "warning")
    
    # Final fallback with structured approach
    return create_structured_fallback(food_name, quantity)

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
                
            if 'ingredient' in line.lower() or line.startswith('-'):
                current_section = 'ingredients'
                if line.startswith('-'):
                    ingredients.append(line[1:].strip())
            elif 'instruction' in line.lower() or 'method' in line.lower() or 'step' in line.lower():
                current_section = 'instructions'
            elif current_section == 'ingredients' and (line.startswith('-') or line.startswith('•')):
                ingredients.append(line[1:].strip())
            elif current_section == 'instructions' and len(line) > 10:
                instructions.append(line)
        
        if ingredients and instructions:
            return {
                "name": f"{food_name.title()} Recipe",
                "ingredients": ingredients[:10],
                "instructions": instructions[:8],
                "quantity": f"{quantity}g"
            }
    
    except Exception as e:
        pass
    
    return None

def create_structured_fallback(food_name, quantity):
    """Create a structured fallback recipe"""
    show_step("Creating structured recipe...", "info")
    
    # Basic cooking methods by food type
    cooking_methods = {
        'rice': ['rinse', 'boil', 'simmer', 'fluff'],
        'pasta': ['boil water', 'cook pasta', 'drain', 'serve'],
        'chicken': ['season', 'heat oil', 'cook', 'rest'],
        'fish': ['season', 'heat pan', 'cook', 'serve'],
        'vegetables': ['wash', 'chop', 'sauté', 'season']
    }
    
    # Determine cooking method
    method = 'vegetables'  # default
    for key in cooking_methods.keys():
        if key in food_name.lower():
            method = key
            break
    
    # Generate basic recipe structure
    base_ingredients = [
        f"{quantity}g {food_name}",
        "2 tbsp olive oil",
        "Salt to taste",
        "Black pepper to taste"
    ]
    
    if 'rice' in food_name.lower() or 'grain' in food_name.lower():
        base_ingredients.extend(["2 cups water", "1 tsp salt"])
    elif 'meat' in food_name.lower() or 'chicken' in food_name.lower():
        base_ingredients.extend(["1 clove garlic", "Fresh herbs"])
    else:
        base_ingredients.append("Lemon juice (optional)")
    
    basic_steps = cooking_methods.get(method, cooking_methods['vegetables'])
    instructions = [
        f"Prepare the {food_name} by cleaning and cutting as needed",
        "Heat olive oil in a suitable pan over medium heat",
        f"Add the {food_name} and cook according to type",
        "Season with salt and pepper during cooking",
        "Cook until tender and properly done",
        "Taste and adjust seasoning before serving"
    ]
    
    return {
        "name": f"Simple {food_name.title()}",
        "ingredients": base_ingredients,
        "instructions": instructions,
        "quantity": f"{quantity}g"
    }
