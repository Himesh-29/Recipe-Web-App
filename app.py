import streamlit as st
from PIL import Image
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv not installed, try to load manually
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Import our modules
from models import load_models, show_step
from web_search import search_recipe_online
from recipe_generator import generate_recipe_with_ai
from nutrition import get_nutrition_info

# Page config
st.set_page_config(
    page_title="Recipe & Nutrition AI",
    page_icon="🍽️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Header using Streamlit components
    st.title("🍽️ AI Recipe & Nutrition Analyzer")
    st.markdown("Upload a food image to get personalized recipes and nutrition info!")
    st.divider()
    
    # Initialize session state
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'food_name' not in st.session_state:
        st.session_state.food_name = ""
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = []
    if 'generating_recipe' not in st.session_state:
        st.session_state.generating_recipe = False
    
    # Load models
    with st.spinner("Initializing AI services..."):
        food_classifier, recipe_generator = load_models()
    
    if not food_classifier or not recipe_generator:
        st.error("Failed to load AI models. Please refresh the page.")
        return
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📷 Upload Your Food Image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of food for AI analysis"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # Resize image to smaller size (250x250 max for better layout)
        max_size = 250
        img_width, img_height = image.size
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size/img_width, max_size/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        st.divider()
        
        # Main layout: Image on left, everything else on right
        col_left, col_right = st.columns([1, 2], gap="large")
        
        with col_left:
            st.image(image, caption="Food Image", use_container_width=True)
            
            # Analysis button - disabled after analysis
            if not st.session_state.analysis_done:
                if st.button("🔍 Analyze Food", type="primary", use_container_width=True, key="analyze_btn"):
                    with st.spinner("🔍 Analyzing food..."):
                        try:
                            results = food_classifier(image, top_k=3)
                            st.session_state.detection_results = results
                            
                            if results and results[0]['score'] > 0.3:
                                detected_food = results[0]['label']
                                st.session_state.food_name = detected_food
                            else:
                                if results:
                                    potential_food = results[0]['label']
                                    search_recipe_online(potential_food)
                                    st.session_state.food_name = potential_food
                            
                            st.session_state.analysis_done = True
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
                            return
            else:
                # Show "Analyze New Image" button after analysis
                if st.button("🔄 Analyze New Image", type="secondary", use_container_width=True, key="reset_btn"):
                    st.session_state.analysis_done = False
                    st.session_state.food_name = ""
                    st.session_state.detection_results = []
                    st.session_state.generating_recipe = False
                    st.rerun()
        
        with col_right:
            if not st.session_state.analysis_done:
                st.info("👈 Click **'Analyze Food'** to start AI analysis")
            else:
                # Detection Results - Open by default
                if st.session_state.detection_results:
                    st.success("✅ Food Detected!")
                    with st.expander("🎯 Detection Results", expanded=True):
                        for i, result in enumerate(st.session_state.detection_results[:3]):
                            confidence = result['score']*100
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{i+1}.** {result['label']}")
                            with col2:
                                st.write(f"`{confidence:.1f}%`")
                
                st.divider()
                
                # Food Input Section
                st.subheader("🍽️ Recipe Generation")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    food_name = st.text_input(
                        "Food Name", 
                        value=st.session_state.food_name, 
                        placeholder="e.g., paella, pizza, garlic bread...",
                        label_visibility="collapsed",
                        key="food_input"
                    )
                with col2:
                    quantity = st.number_input(
                        "Grams", 
                        min_value=1, 
                        value=100, 
                        step=10,
                        label_visibility="collapsed",
                        key="quantity_input"
                    )
                
                if food_name:
                    st.caption(f"📊 Generating for **{quantity}g** of {food_name}")
                    
                    # Generate button
                    if st.button("🍳 Generate Recipe & Nutrition", 
                               disabled=st.session_state.generating_recipe, 
                               type="primary", 
                               use_container_width=True,
                               key="generate_btn"):
                        st.session_state.generating_recipe = True
                        st.rerun()
        
        # Recipe Results - Side by side layout below
        if st.session_state.analysis_done and food_name and st.session_state.generating_recipe:
            st.divider()
            
            with st.spinner("🔄 Generating recipe and nutrition info..."):
                # Generate recipe
                detected_ingredients = [result['label'] for result in st.session_state.detection_results[:3]] if st.session_state.detection_results else None
                recipe = generate_recipe_with_ai(food_name, quantity, recipe_generator, detected_ingredients)
                
                # Get nutrition
                nutrition = get_nutrition_info(food_name, quantity)
                
                # Reset generating state
                st.session_state.generating_recipe = False
            
            if not recipe:
                st.error("❌ Recipe generation failed. Please try again or check your internet connection.")
                st.info("💡 Try entering the food name manually for better results.")
            else:
                # Two column layout for recipe and nutrition
                col_recipe, col_nutrition = st.columns([2, 1], gap="large")
                
                with col_recipe:
                    # Recipe section
                    st.subheader(f"🍳 {recipe['name']}")
                    st.caption(f"Serving: {recipe['quantity']}")
                    
                    # Ingredients
                    with st.expander("🥘 **Ingredients**", expanded=True):
                        for ingredient in recipe['ingredients']:
                            st.markdown(f"• {ingredient}")
                    
                    st.divider()
                    
                    # Instructions
                    st.markdown("**👨‍🍳 Instructions**")
                    for i, step in enumerate(recipe['instructions'], 1):
                        with st.container():
                            st.markdown(f"**Step {i}**")
                            st.write(step)
                            if i < len(recipe['instructions']):
                                st.write("")  # Spacing
                
                with col_nutrition:
                    # Nutrition info card
                    if nutrition:
                        st.subheader("📊 Nutrition Facts")
                        st.caption(f"Per {quantity}g serving")
                        
                        # Nutrition metrics in a nice card format
                        st.metric("� Calories", f"{nutrition['calories']} kcal")
                        st.metric("💪 Protein", f"{nutrition['protein']}g")
                        st.metric("🌾 Carbs", f"{nutrition['carbs']}g")
                        st.metric("🧈 Fat", f"{nutrition['fat']}g")
                    else:
                        st.info("💡 Nutrition data not available")

if __name__ == "__main__":
    main()
