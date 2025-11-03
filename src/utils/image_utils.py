"""Image Utilities - Image processing and manipulation"""

from PIL import Image
import streamlit as st


def load_and_process_image(uploaded_file, target_size=400):
    """
    Load image and process it (center crop to square and resize)
    
    Args:
        uploaded_file: Streamlit uploaded file object
        target_size: Target square size (default 400x400)
    
    Returns:
        Processed PIL Image object
    """
    image = Image.open(uploaded_file)
    img_width, img_height = image.size
    
    # Center crop to square
    if img_width != img_height:
        min_dim = min(img_width, img_height)
        left = (img_width - min_dim) // 2
        top = (img_height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        image = image.crop((left, top, right, bottom))
    
    # Resize to target size
    image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    return image
