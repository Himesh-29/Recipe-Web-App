"""Web Search - Online recipe search functionality"""

import requests
from models import show_step

def search_recipe_online(food_name):
    """Search for recipe online"""
    show_step(f"Searching online for {food_name} recipe...")
    
    try:
        # Simple Google search simulation
        search_url = f"https://www.google.com/search?q={food_name}+recipe"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            show_step("Found online recipes!", "success")
            return True
        else:
            show_step("Online search failed", "warning")
            return False
    
    except Exception as e:
        show_step(f"Online search error: {e}", "warning")
        return False
