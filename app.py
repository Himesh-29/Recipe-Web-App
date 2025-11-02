import streamlit as st
from PIL import Image

# Import our modules
from models import load_models, show_step
from web_search import search_recipe_online
from recipe_generator import generate_recipe_with_ai
from nutrition import get_nutrition_info

# Page config
st.set_page_config(
    page_title="🍽️ Recipe & Nutrition AI",
    page_icon="🍽️",
    layout="wide"
)

def main():
    st.title("🍽️ AI Recipe & Nutrition Analyzer")
    st.markdown("Upload a food image to get recipes and nutrition info!")
    
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
    food_classifier, recipe_generator = load_models()
    
    if not food_classifier or not recipe_generator:
        st.error("Failed to load AI models. Please refresh the page.")
        return
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📷 Upload food image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of food"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Uploaded Image", width='stretch')
        
        with col2:
            st.markdown("### 🤖 AI Analysis")
            
            if st.button("Analyze Food", type="primary") or st.session_state.analysis_done:
                if not st.session_state.analysis_done:
                    # Step 1: Identify food
                    show_step("Identifying food in image...")
                    
                    try:
                        results = food_classifier(image, top_k=3)
                        st.session_state.detection_results = results
                        
                        if results and results[0]['score'] > 0.3:
                            detected_food = results[0]['label']
                            confidence = results[0]['score'] * 100
                            
                            show_step(f"Detected: {detected_food} ({confidence:.1f}% confidence)", "success")
                            st.session_state.food_name = detected_food
                            
                        else:
                            show_step("Food not clearly identified", "warning")
                            
                            # Step 2: Try web search
                            if results:
                                potential_food = results[0]['label']
                                if search_recipe_online(potential_food):
                                    st.session_state.food_name = potential_food
                        
                        st.session_state.analysis_done = True
                        st.rerun()
                        
                    except Exception as e:
                        show_step(f"Analysis failed: {e}", "error")
                        return
                
                # Show detection results if available
                if st.session_state.detection_results:
                    st.markdown("### 🎯 Detection Results")
                    for i, result in enumerate(st.session_state.detection_results[:3]):
                        st.write(f"{i+1}. {result['label']} - {result['score']*100:.1f}%")
                
                # Step 3: Manual input option
                manual_input = st.checkbox("Enter food name manually")
                
                if manual_input:
                    food_name = st.text_input("What food is this?", value=st.session_state.food_name)
                else:
                    food_name = st.session_state.food_name
                
                if food_name:
                    st.markdown("### ⚖️ Quantity")
                    quantity = st.number_input(
                        "How much do you want to make? (grams)", 
                        min_value=1, 
                        value=100, 
                        step=10
                    )
                    
                    # Show button text based on state
                    button_text = "🔄 Generating..." if st.session_state.generating_recipe else "Generate Recipe & Nutrition"
                    
                    if st.button(button_text, disabled=st.session_state.generating_recipe):
                        # Set generating state
                        st.session_state.generating_recipe = True
                        st.rerun()
                    
                    # Process recipe generation if in generating state
                    if st.session_state.generating_recipe:
                        # Step 4: Generate recipe with AI
                        show_step("Generating recipe...")
                        recipe = generate_recipe_with_ai(food_name, quantity, recipe_generator)
                        
                        # Step 5: Get nutrition info
                        show_step("Getting nutrition info...")
                        nutrition = get_nutrition_info(food_name, quantity)
                        
                        # Reset generating state
                        st.session_state.generating_recipe = False
                        
                        # Display results
                        st.markdown("---")
                        
                        col_recipe, col_nutrition = st.columns([1, 1])
                        
                        with col_recipe:
                            st.markdown("### 🍳 Recipe")
                            st.markdown(f"**{recipe['name']}**")
                            st.markdown(f"*For {recipe['quantity']}*")
                            
                            st.markdown("**Ingredients:**")
                            for ingredient in recipe['ingredients']:
                                st.write(f"• {ingredient}")
                            
                            st.markdown("**Instructions:**")
                            for i, step in enumerate(recipe['instructions'], 1):
                                st.write(f"{i}. {step}")
                        
                        with col_nutrition:
                            st.markdown("### 📊 Nutrition Info")
                            if nutrition:
                                st.metric("Calories", nutrition['calories'])
                                
                                col_p, col_c, col_f = st.columns(3)
                                with col_p:
                                    st.metric("Protein", f"{nutrition['protein']}g")
                                with col_c:
                                    st.metric("Carbs", f"{nutrition['carbs']}g")
                                with col_f:
                                    st.metric("Fat", f"{nutrition['fat']}g")
                            else:
                                st.info("Nutrition data not available for this food item")
            
            # Reset button
            if st.session_state.analysis_done:
                if st.button("🔄 Analyze New Image"):
                    st.session_state.analysis_done = False
                    st.session_state.food_name = ""
                    st.session_state.detection_results = []
                    st.session_state.generating_recipe = False
                    st.rerun()

if __name__ == "__main__":
    main()
