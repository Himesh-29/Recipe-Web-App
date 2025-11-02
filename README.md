# 🍽️ AI Recipe & Nutrition App

Simple AI-powered app that:
- **Identifies food** from uploaded images using Hugging Face models
- **Searches web** if food not recognized clearly  
- **Asks user input** as fallback
- **Generates recipes** using free AI models (no OpenAI charges)
- **Provides nutrition info** for specified quantities

## Setup & Run

### Deploy to Streamlit Cloud
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with main file: `app.py`

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
