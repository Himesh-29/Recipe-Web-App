"""UI Components - Reusable UI rendering functions"""

import streamlit as st


def render_log(log_type, message):
    """Render a colored log message based on type"""
    if log_type == "info":
        st.markdown(
            f'<div style="background:#eef4fd;padding:10px;border-radius:8px;margin-bottom:8px;display:flex;align-items:center">'
            f'<span style="font-size:1.2em;margin-right:8px">📝</span> {message}</div>',
            unsafe_allow_html=True
        )
    elif log_type == "success":
        st.markdown(
            f'<div style="background:#eafaf1;padding:10px;border-radius:8px;margin-bottom:8px;display:flex;align-items:center">'
            f'<span style="font-size:1.2em;margin-right:8px">✅</span> {message}</div>',
            unsafe_allow_html=True
        )
    elif log_type == "error":
        st.markdown(
            f'<div style="background:#fdeaea;padding:10px;border-radius:8px;margin-bottom:8px;display:flex;align-items:center">'
            f'<span style="font-size:1.2em;margin-right:8px">❌</span> {message}</div>',
            unsafe_allow_html=True
        )
    else:
        st.write(message)


def render_detection_results(detection_results):
    """Render detection results expander"""
    st.success("✅ Food Detected!")
    with st.expander("🎯 Detection Results", expanded=True):
        for i, result in enumerate(detection_results[:3]):
            confidence = result['score'] * 100
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i+1}.** {result['label']}")
            with col2:
                st.write(f"`{confidence:.1f}%`")


def render_recipe_section(recipe, quantity):
    """Render recipe details section"""
    st.subheader(f"🍳 {recipe['name']}")
    st.caption(f"Serving: {recipe['quantity']}")
    with st.expander("🥘 **Ingredients**", expanded=True):
        for ingredient in recipe['ingredients']:
            st.markdown(f"• {ingredient}")
    st.divider()
    st.markdown("**👨‍🍳 Instructions**")
    for i, step in enumerate(recipe['instructions'], 1):
        st.markdown(f"{i}. {step}")


def render_nutrition_section(nutrition, quantity):
    """Render nutrition facts section"""
    if nutrition:
        st.subheader("📊 Nutrition Facts")
        st.caption(f"Per {quantity}g serving")
        st.metric("🔥 Calories", f"{nutrition['calories']} kcal")
        st.metric("💪 Protein", f"{nutrition['protein']}g")
        st.metric("🌾 Carbs", f"{nutrition['carbs']}g")
        st.metric("🧈 Fat", f"{nutrition['fat']}g")
    else:
        st.info("💡 Nutrition data not available")


def render_logs_expander(user_logs, generating_recipe, show_logs):
    """Render AI logs expander with dynamic title"""
    current_step = get_current_step(user_logs)
    
    if generating_recipe:
        if current_step:
            expander_title = f"🔄 Current step: {current_step}"
        else:
            expander_title = "🔍 AI Logs"
        is_expanded = show_logs
    else:
        expander_title = "🔍 AI Logs"
        is_expanded = False
    
    with st.expander(expander_title, expanded=is_expanded):
        for log_type, message in user_logs:
            render_log(log_type, message)


def get_current_step(user_logs):
    """Extract current step from logs for expander title"""
    if user_logs:
        last_type, last_msg = user_logs[-1]
        if last_type == "info" and ("..." in last_msg or "Analyzing" in last_msg or "Generating" in last_msg or "Calculating" in last_msg):
            return last_msg
    return None


def render_rag_stats(rag_manager):
    """Render RAG cache statistics in sidebar with FAISS info"""
    stats = rag_manager.get_stats()
    
    with st.sidebar:
        st.divider()
        st.subheader("🧠 RAG Cache")
        st.metric("Cached Recipes", stats["total_cached_recipes"])
        st.metric("Embedding Dim", stats["embedding_dimension"])
        
        if stats["model_available"]:
            st.success("✓ Embeddings Ready")
        else:
            st.warning("⚠ Install: pip install sentence-transformers faiss-cpu")
        
        if st.button("🗑️ Clear Cache", key="clear_rag_cache"):
            if rag_manager.clear_cache():
                st.success("Cache cleared!")
                st.rerun()
