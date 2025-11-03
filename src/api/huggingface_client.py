"""AI Models - Food classification and recipe generation"""

import streamlit as st

def show_step(message, type="info"):
    """Show execution steps to user"""
    if type == "info":
        st.info(f"🔄 {message}")
    elif type == "success":
        st.success(f"✅ {message}")
    elif type == "warning":
        st.warning(f"⚠️ {message}")
    elif type == "error":
        st.error(f"❌ {message}")

def load_models():
    """Initialize API-based models (no heavy loading)"""
    # Silently initialize - no message boxes
    food_classifier = FoodClassifierAPI()
    recipe_generator = RecipeGeneratorAPI()
    
    return food_classifier, recipe_generator

class FoodClassifierAPI:
    """Hugging Face API for food classification with HF_TOKEN"""
    def __init__(self):
        import os
        
        # New Hugging Face router format with authentication
        self.api_url = "https://router.huggingface.co/hf-inference/models/nateraw/food"
        
        # Get HF_TOKEN from environment
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("[DEBUG] Warning: HF_TOKEN not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {hf_token}" if hf_token else "",
            "Content-Type": "image/jpeg"
        }
    
    def __call__(self, image, top_k=3):
        import requests
        import io
        from PIL import Image
        
        # Convert PIL image to bytes
        img_bytes = io.BytesIO()
        if isinstance(image, Image.Image):
            image.save(img_bytes, format='JPEG', quality=85)
            img_bytes = img_bytes.getvalue()
        
        try:
            print(f"[DEBUG] Calling food classification API: {self.api_url}")  # Internal logging
            print(f"[DEBUG] Headers: {dict(self.headers) if 'Bearer' in str(self.headers) else 'No auth token'}")
            
            response = requests.post(
                self.api_url, 
                headers=self.headers,
                data=img_bytes, 
                timeout=30
            )
            print(f"[DEBUG] API Response Status: {response.status_code}")  # Internal logging
            
            if response.status_code == 200:
                results = response.json()
                print(f"[DEBUG] API Results: {results}")  # Internal logging
                return results[:top_k] if isinstance(results, list) else []
            else:
                print(f"[DEBUG] API Error Response: {response.text}")  # Internal logging
                return []
        except Exception as e:
            print(f"[DEBUG] Food classification Exception: {e}")  # Internal logging
            show_step(f"Food classification API error: {e}", "warning")
            return []

class RecipeGeneratorAPI:
    """API for recipe generation using Llama via Hugging Face router"""
    def __init__(self):
        import os
        
        # Use Hugging Face router with chat completions endpoint
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        
        # Get HF_TOKEN from environment
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("[DEBUG] Warning: HF_TOKEN not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {hf_token}" if hf_token else "",
            "Content-Type": "application/json"
        }
    
    def generate_recipe(self, food_name, ingredients_list):
        import requests
        
        # Create better prompt for recipe generation
        ingredients_str = ', '.join(ingredients_list) if ingredients_list else 'common ingredients'
        prompt = f"""Create a detailed recipe for {food_name}. 

Format the response exactly like this:
Ingredients:
- [list ingredients with quantities]

Instructions:
1. [step by step instructions]

Keep it concise and practical."""
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            print(f"[DEBUG] Calling Llama API: {self.api_url}")  # Internal logging
            print(f"[DEBUG] Payload model: {payload['model']}")  # Internal logging
            
            response = requests.post(
                self.api_url, 
                headers=self.headers,
                json=payload, 
                timeout=30
            )
            print(f"[DEBUG] Recipe API Response Status: {response.status_code}")  # Internal logging
            
            if response.status_code == 200:
                result = response.json()
                print(f"[DEBUG] Recipe API Result: {result}")  # Internal logging
                
                if "choices" in result and result["choices"]:
                    generated_text = result["choices"][0]["message"]["content"]
                    print(f"[DEBUG] Generated recipe text: {generated_text[:200]}...")  # Internal logging
                    return generated_text
                else:
                    print(f"[DEBUG] No choices in API response")  # Internal logging
                    return None
            else:
                print(f"[DEBUG] Recipe API Error Response: {response.text}")  # Internal logging
                return None
                
        except Exception as e:
            print(f"[DEBUG] Recipe generation Exception: {e}")  # Internal logging
            show_step(f"Recipe generation API error: {e}", "warning")
            return None
    
    def get_nutrition_facts(self, food_name):
        """Fetch nutrition facts per 100g of food using AI"""
        import requests
        from ..services.nutrition_service import parse_nutrition_response
        
        # Create focused prompt for nutrition facts only
        prompt = f"""Provide nutrition facts for {food_name} per 100g in this exact format ONLY:
Calories: [number]
Protein: [number]
Carbs: [number]
Fat: [number]

Do not include units or any other text. Only these 4 lines."""
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "max_tokens": 100,
            "temperature": 0.3  # Lower temperature for more consistent nutrition values
        }
        
        try:
            print(f"[DEBUG] Calling Llama API for nutrition: {self.api_url}")
            print(f"[DEBUG] Nutrition prompt for: {food_name}")
            
            response = requests.post(
                self.api_url, 
                headers=self.headers,
                json=payload, 
                timeout=30
            )
            print(f"[DEBUG] Nutrition API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and result["choices"]:
                    nutrition_text = result["choices"][0]["message"]["content"]
                    print(f"[DEBUG] Nutrition API Response: {nutrition_text}")
                    
                    # Parse the nutrition response
                    from ..services.nutrition_service import parse_nutrition_response
                    nutrition = parse_nutrition_response(nutrition_text)
                    
                    if nutrition:
                        print(f"[DEBUG] Successfully parsed nutrition for {food_name}: {nutrition}")
                        return nutrition
                    else:
                        print(f"[DEBUG] Failed to parse nutrition from: {nutrition_text}")
                else:
                    print(f"[DEBUG] No choices in nutrition API response")
            else:
                print(f"[DEBUG] Nutrition API Error: {response.text}")
                
        except Exception as e:
            print(f"[DEBUG] Nutrition API Exception: {e}")
        
        return None
