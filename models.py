"""AI Models - Food classification and recipe generation"""

import streamlit as st
from transformers import pipeline

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

@st.cache_resource
def load_models():
    """Load required AI models"""
    show_step("Loading AI models...")
    
    try:
        # Food classification model
        food_classifier = pipeline("image-classification", model="nateraw/food", use_fast=True)
        
        # Recipe generation model (better free model)
        recipe_generator = pipeline("text-generation", model="gpt2", use_fast=True)
        
        show_step("Models loaded successfully!", "success")
        return food_classifier, recipe_generator
    
    except Exception as e:
        show_step(f"Error loading models: {e}", "error")
        return None, None
