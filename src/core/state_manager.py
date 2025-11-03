"""State Manager - Session state initialization and management"""

import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'food_name' not in st.session_state:
        st.session_state.food_name = ""
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = []
    if 'generating_recipe' not in st.session_state:
        st.session_state.generating_recipe = False
    if 'user_logs' not in st.session_state:
        st.session_state.user_logs = []
    if 'recipe_generation_started' not in st.session_state:
        st.session_state.recipe_generation_started = False
    if 'recipe_data' not in st.session_state:
        st.session_state.recipe_data = None
    if 'nutrition_data' not in st.session_state:
        st.session_state.nutrition_data = None
    if 'last_uploaded_file' not in st.session_state:
        st.session_state.last_uploaded_file = None
    if 'show_logs' not in st.session_state:
        st.session_state.show_logs = False
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False


def reset_on_new_upload(uploaded_file):
    """Reset state when a new file is uploaded"""
    if uploaded_file:
        if (st.session_state.last_uploaded_file is None or 
            st.session_state.last_uploaded_file != uploaded_file.name):
            st.session_state.last_uploaded_file = uploaded_file.name
            st.session_state.analysis_done = False
            st.session_state.food_name = ""
            st.session_state.detection_results = []
            st.session_state.generating_recipe = False
            st.session_state.recipe_generation_started = False
            st.session_state.recipe_data = None
            st.session_state.nutrition_data = None
            st.session_state.user_logs = []


def clear_image_and_reset():
    """Clear image and reset state for 'Analyze New Image' button"""
    st.session_state.analysis_done = False
    st.session_state.analysis_in_progress = False
    st.session_state.food_name = ""
    st.session_state.detection_results = []
    st.session_state.generating_recipe = False
    st.session_state.recipe_generation_started = False
    st.session_state.recipe_data = None
    st.session_state.nutrition_data = None
    st.session_state.user_logs = []
    st.session_state.last_uploaded_file = None


def reset_analysis():
    """Reset analysis state (used by Analyze New Image button)"""
    st.session_state.analysis_done = False
    st.session_state.food_name = ""
    st.session_state.detection_results = []
    st.session_state.generating_recipe = False
    st.session_state.recipe_generation_started = False
    st.session_state.recipe_data = None
    st.session_state.nutrition_data = None
    st.session_state.user_logs = []


def reset_generation():
    """Reset generation state (used by Generate Recipe button)"""
    st.session_state.user_logs = []
    st.session_state.user_logs.append(("info", "Generating recipe with AI..."))
    st.session_state.generating_recipe = True
    st.session_state.recipe_generation_started = False
    st.session_state.recipe_data = None
    st.session_state.nutrition_data = None
    st.session_state.show_logs = True
