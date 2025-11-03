"""Web Search Service - Online recipe search functionality"""

import requests

def search_recipe_online(food_name):
    """Search for recipe online"""
    
    try:
        # Simple Google search simulation
        search_url = f"https://www.google.com/search?q={food_name}+recipe"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    
    except Exception as e:
        return False
