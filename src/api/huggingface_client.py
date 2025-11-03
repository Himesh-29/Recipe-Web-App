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
