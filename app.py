import streamlit as st
import os
from PIL import Image
from datetime import datetime

# Handle UptimeRobot monitoring pings
if 'heartbeat' in st.query_params:
    st.write(f"✅ App is alive at {datetime.now()}")
    st.stop()

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

# Import from new modular structure
from src.api.huggingface_client import load_models
from src.utils.image_utils import load_and_process_image
from src.ui.components import render_log, render_rag_stats
from src.core.state_manager import initialize_session_state, reset_on_new_upload, clear_image_and_reset
from src.services.recipe_service import generate_recipe_with_ai
from src.services.nutrition_service import get_nutrition_info
from src.services.web_search_service import search_recipe_online
from src.services.rag_manager import rag_manager
from src.services.cache_migration import check_migration_needed, migrate_cache_to_unified_format

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
    
    # Run cache migration if needed (converts old format to unified documents)
    if check_migration_needed():
        with st.spinner("Upgrading cache format..."):
            migrate_cache_to_unified_format()
    
    # Display RAG cache stats in sidebar
    render_rag_stats(rag_manager)
    
    # Initialize session state
    initialize_session_state()
    
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
    
    # Reset state when new file is uploaded
    reset_on_new_upload(uploaded_file)
    
    if uploaded_file:
        image = load_and_process_image(uploaded_file)
        size = 400
        st.divider()
        # Main layout: Image on left, everything else on right
        col_left, col_right = st.columns([1, 3], gap="large")
        
        with col_left:
            st.image(image, caption="Food Image", width=size)
            # Analysis button - disabled after analysis or during processing
            if not st.session_state.analysis_done:
                if st.button("🔍 Analyze Food", type="primary", use_container_width=True, key="analyze_btn", disabled=st.session_state.analysis_in_progress):
                    st.session_state.analysis_in_progress = True
                    st.session_state.user_logs = []  # Clear logs for new analysis
                    st.session_state.user_logs.append(("info", "Analyzing food image..."))
                    st.session_state.show_logs = True
                # Do the actual analysis without rerun
                if st.session_state.analysis_in_progress and not st.session_state.detection_results:
                    try:
                        results = food_classifier(image, top_k=3)
                        st.session_state.user_logs.append(("info", f"Food classifier completed"))
                        st.session_state.detection_results = results
                        if results and results[0]['score'] > 0.3:
                            detected_food = results[0]['label']
                            st.session_state.food_name = detected_food
                            st.session_state.user_logs.append(("success", f"Detected: {detected_food}"))
                        else:
                            if results:
                                potential_food = results[0]['label']
                                search_recipe_online(potential_food)
                                st.session_state.food_name = potential_food
                                st.session_state.user_logs.append(("info", f"Fallback food: {potential_food}"))
                        st.session_state.analysis_done = True
                        st.session_state.analysis_in_progress = False
                    except Exception as e:
                        st.session_state.user_logs.append(("error", f"Analysis failed: {e}"))
                        st.session_state.analysis_in_progress = False
                        st.error(f"Analysis failed: {e}")
                        return
            else:
                if st.button("🔄 Analyze New Image", type="secondary", use_container_width=True, key="reset_btn"):
                    clear_image_and_reset()
                    st.rerun()
        with col_right:
            if not st.session_state.analysis_done:
                st.info("👈 Click **'Analyze Food'** to start AI analysis")
            else:
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
                    # Show the button - it will be disabled during generation
                    if st.button("🍳 Generate Recipe & Nutrition", 
                               disabled=st.session_state.generating_recipe, 
                               type="primary", 
                               use_container_width=True,
                               key="generate_btn"):
                        st.session_state.user_logs = []  # Clear previous logs
                        st.session_state.user_logs.append(("info", "Generating recipe with AI..."))
                        st.session_state.generating_recipe = True
                        st.session_state.recipe_generation_started = False  # Reset for new generation
                        st.session_state.recipe_data = None
                        st.session_state.nutrition_data = None
                        st.session_state.show_logs = True
        if st.session_state.analysis_done and food_name and (st.session_state.generating_recipe or st.session_state.recipe_data):
            st.divider()
            detected_ingredients = [result['label'] for result in st.session_state.detection_results[:3]] if st.session_state.detection_results else None
            
            # Show loading spinner during generation
            if st.session_state.generating_recipe and not st.session_state.recipe_generation_started:
                with st.spinner("🔄 Generating recipe and nutrition info... Please wait..."):
                    st.session_state.user_logs.append(("info", "Generating with AI API..."))
                    st.session_state.recipe_generation_started = True
                    
                    recipe = generate_recipe_with_ai(food_name, quantity, recipe_generator, detected_ingredients)
                    st.session_state.recipe_data = recipe
                    if recipe:
                        st.session_state.user_logs.append(("success", "AI recipe generated!"))
                    
                    nutrition = get_nutrition_info(food_name, quantity, recipe_generator)
                    st.session_state.nutrition_data = nutrition
                    if nutrition:
                        st.session_state.user_logs.append(("info", "Calculating nutrition information..."))
                        st.session_state.user_logs.append(("success", f"Nutrition calculated for {quantity}g!"))
                    
                    st.session_state.generating_recipe = False
            
            # Show content
            recipe = st.session_state.recipe_data
            nutrition = st.session_state.nutrition_data
            
            col_recipe, col_nutrition = st.columns([2, 1], gap="large")
            with col_recipe:
                # Determine expander title based on state
                if st.session_state.generating_recipe:
                    current_step = get_current_step()
                    if current_step:
                        expander_title = f"🔄 Current step: {current_step}"
                    else:
                        expander_title = "🔍 AI Logs"
                    is_expanded = st.session_state.get('show_logs', False)
                else:
                    expander_title = "🔍 AI Logs"
                    is_expanded = False
                
                with st.expander(expander_title, expanded=is_expanded):
                    for log_type, message in st.session_state.user_logs:
                        render_log(log_type, message)
                
                # Show recipe only if generation is complete
                if recipe and not st.session_state.generating_recipe:
                    st.subheader(f"🍳 {recipe['name']}")
                    st.caption(f"Serving: {recipe['quantity']}")
                    with st.expander("🥘 **Ingredients**", expanded=True):
                        for ingredient in recipe['ingredients']:
                            st.markdown(f"• {ingredient}")
                    st.divider()
                    st.markdown("**👨‍🍳 Instructions**")
                    for i, step in enumerate(recipe['instructions'], 1):
                        st.markdown(f"{i}. {step}")
            
            with col_nutrition:
                # Show nutrition only if generation is complete
                if not st.session_state.generating_recipe:
                    if nutrition:
                        st.subheader("📊 Nutrition Facts")
                        st.caption(f"Per {quantity}g serving")
                        st.metric("🔥 Calories", f"{nutrition['calories']} kcal")
                        st.metric("💪 Protein", f"{nutrition['protein']}g")
                        st.metric("🌾 Carbs", f"{nutrition['carbs']}g")
                        st.metric("🧈 Fat", f"{nutrition['fat']}g")
                    else:
                        st.info("💡 Nutrition data not available")

# Helper to get current step for expander title
def get_current_step():
    if st.session_state.user_logs:
        last_type, last_msg = st.session_state.user_logs[-1]
        if last_type == "info" and ("..." in last_msg or "Analyzing" in last_msg or "Generating" in last_msg or "Calculating" in last_msg):
            return last_msg
    return None

if __name__ == "__main__":
    main()
