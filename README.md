# Nano Hack – Project Explorer

Student-friendly app to discover Nano Banana writeups using Gemini.

## Quick Start

1. Install deps
   - `python3 -m venv venv && source venv/bin/activate`
   - `pip install -r requirements.txt`
2. Set Gemini API key
   - Locally: `export GEMINI_API_KEY=your_key_here`
   - Streamlit Cloud: add `GEMINI_API_KEY` in App Settings → Secrets
3. Run the app
   - `streamlit run app.py`

## What it does

- Builds local embeddings for `banana_writeups.json` using `text-embedding-004`
- Performs cosine similarity search for your query
- Optional re-ranking and explanations via `gemini-1.5-flash`

## Notes

- First run caches embeddings in `data/` for speed
- Toggle re-ranking/explanations in the sidebar
