# 🍽️ AI Recipe & Nutrition App

An intelligent web application that analyzes food images and provides personalized recipes with nutritional information.

## Features

- **AI Food Detection** - Upload an image and get instant food identification using Hugging Face models
- **Smart Recipe Generation** - Get recipes from web scraping or AI-powered generation as fallback
- **Nutrition Analysis** - Calculate detailed nutrition facts (calories, protein, carbs, fat) for any quantity
- **User-Friendly Logs** - Track all processing steps with styled, collapsible logs
- **Modern UI** - Clean, responsive interface built with Streamlit

## How It Works

1. Upload a food image
2. AI analyzes and identifies the food
3. Select quantity (in grams)
4. Get recipe suggestions and nutrition info
5. View all processing steps in logs

## Project Structure

```
app.py                 - Main application
src/
├── api/              - Hugging Face API clients
├── services/         - Business logic (recipes, nutrition, search)
├── core/             - State management
├── ui/               - UI components
└── utils/            - Image processing utilities
```

## Setup & Run

### Try Online
👉 **[Open App](https://recipe-web-app-himesh.streamlit.app/)**

### Run Locally with pip
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Run Locally with conda
```bash
conda create -n recipe_app python=3.11
conda activate recipe_app
pip install -r requirements.txt
streamlit run app.py
```

### Run Locally with uv (fastest)
```bash
uv venv
uv pip install -r requirements.txt
uv run streamlit run app.py
```
