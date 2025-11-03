"""Recipe Service - Web scraping and AI-powered recipe creation"""

import requests
from bs4 import BeautifulSoup
import re

def generate_recipe_with_ai(food_name, quantity, recipe_generator, detected_ingredients=None):
    """Generate recipe using web scraping and AI APIs"""
    
    # Try web scraping first for real recipes - priority!
    recipe = scrape_recipe_from_web(food_name, quantity)
    if recipe:
        return recipe
    
    # If web scraping fails, use AI API
    return generate_with_ai_api(food_name, quantity, recipe_generator, detected_ingredients)

def scrape_recipe_from_web(food_name, quantity):
    """Scrape recipes from recipe websites"""
    
    try:
        # Try BBC Good Food first - more reliable structure
        recipe = scrape_bbc_recipes(food_name, quantity)
        if recipe:
            return recipe
        
        # Try AllRecipes as backup
        search_query = f"{food_name} recipe"
        search_url = f"https://www.allrecipes.com/search?q={search_query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for recipe links - updated selectors
        recipe_links = soup.find_all('a', href=re.compile(r'/recipe/\d+'))
        
        if recipe_links:
            # Get the first recipe
            first_recipe_url = recipe_links[0].get('href')
            if not first_recipe_url.startswith('http'):
                first_recipe_url = "https://www.allrecipes.com" + first_recipe_url
            
            recipe = scrape_allrecipes_page(first_recipe_url, quantity)
            if recipe:
                return recipe
        
        return None
        
    except Exception as e:
        print(f"[DEBUG] Web scraping failed: {e}")
        return None

def scrape_allrecipes_page(url, quantity):
    """Scrape specific recipe from AllRecipes"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract recipe name - try multiple selectors
        title_elem = (soup.find('h1', class_='article-heading') or 
                     soup.find('h1', class_='headline') or 
                     soup.find('h1'))
        recipe_name = title_elem.text.strip() if title_elem else f"{quantity}g Recipe"
        
        # Extract ingredients - try multiple modern selectors
        ingredients = []
        
        # Try structured data first
        ingredient_elems = soup.select('li[class*="ingredient"], span[class*="ingredient"]')
        if not ingredient_elems:
            # Try alternative selectors
            ingredient_elems = soup.find_all('li', attrs={'data-ingredient': True})
        
        for elem in ingredient_elems[:15]:
            text = elem.get_text(strip=True)
            if text and len(text) > 2:
                ingredients.append(text)
        
        # Extract instructions - try multiple selectors
        instructions = []
        
        # Try structured data
        instruction_elems = soup.select('li[class*="instruction"], p[class*="instruction"]')
        if not instruction_elems:
            # Try alternative selectors
            instruction_elems = soup.find_all('li', attrs={'data-step': True})
        
        for elem in instruction_elems[:12]:
            text = elem.get_text(strip=True)
            if text and len(text) > 15:
                instructions.append(text)
        
        if ingredients and instructions:
            print(f"[DEBUG] Scraped AllRecipes: {recipe_name} with {len(ingredients)} ingredients and {len(instructions)} steps")
            return {
                "name": recipe_name,
                "ingredients": ingredients[:12],
                "instructions": instructions[:10],
                "quantity": f"{quantity}g serving"
            }
        else:
            print(f"[DEBUG] AllRecipes scrape incomplete - ingredients: {len(ingredients)}, instructions: {len(instructions)}")
        
    except Exception as e:
        print(f"[DEBUG] AllRecipes scraping error: {e}")
    
    return None

def scrape_bbc_recipes(food_name, quantity):
    """Scrape BBC Good Food as primary source"""
    try:
        search_url = f"https://www.bbcgoodfood.com/search?q={food_name.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for recipe cards - try multiple selectors
        recipe_links = soup.find_all('a', href=re.compile(r'/recipes/'))
        
        if not recipe_links:
            # Try alternative selector
            recipe_links = soup.select('a[href*="/recipes/"]')
        
        for link in recipe_links[:3]:  # Try first 3 results
            recipe_url = link.get('href', '')
            if recipe_url and '/recipes/' in recipe_url:
                if not recipe_url.startswith('http'):
                    recipe_url = "https://www.bbcgoodfood.com" + recipe_url
                
                recipe = scrape_bbc_recipe_page(recipe_url, quantity)
                if recipe:
                    return recipe
        
    except Exception as e:
        print(f"[DEBUG] BBC scraping failed: {e}")
    
    return None

def scrape_bbc_recipe_page(url, quantity):
    """Scrape specific BBC recipe page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title - try multiple selectors
        title_elem = soup.find('h1') or soup.find('h1', class_='heading-1')
        recipe_name = title_elem.text.strip() if title_elem else f"{quantity}g Recipe"
        
        # Extract ingredients - try multiple selectors
        ingredients = []
        
        # Try modern BBC structure
        ingredient_elems = soup.select('li.pb-xxs, li[class*="ingredient"]')
        if not ingredient_elems:
            # Try alternative structure
            ingredient_section = soup.find('section', class_='recipe__ingredients')
            if ingredient_section:
                ingredient_elems = ingredient_section.find_all('li')
        
        for elem in ingredient_elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 2 and not text.lower().startswith(('method', 'instruction', 'step')):
                ingredients.append(text)
        
        # Extract method/instructions
        instructions = []
        
        # Try modern BBC structure
        method_elems = soup.select('li.pb-xs, li[class*="method"]')
        if not method_elems:
            # Try alternative structure
            method_section = soup.find('section', class_='recipe__method')
            if method_section:
                method_elems = method_section.find_all('li')
        
        for elem in method_elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 15:  # Reasonable instruction length
                instructions.append(text)
        
        if ingredients and instructions:
            print(f"[DEBUG] Scraped BBC recipe: {recipe_name} with {len(ingredients)} ingredients and {len(instructions)} steps")
            return {
                "name": recipe_name,
                "ingredients": ingredients[:12],
                "instructions": instructions[:10],
                "quantity": f"{quantity}g serving"
            }
        else:
            print(f"[DEBUG] BBC scrape incomplete - ingredients: {len(ingredients)}, instructions: {len(instructions)}")
        
    except Exception as e:
        print(f"[DEBUG] BBC recipe page scraping error: {e}")
    
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
