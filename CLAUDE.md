# CLAUDE.md

Kaggle writeup search tool using Gemini embeddings for semantic search.

> See [AGENTS.md](./AGENTS.md) for coding style and commit guidelines.

## Project Overview

- **Purpose**: Search and explore Kaggle competition writeups using semantic embeddings
- **Type**: code
- **Stack**: Streamlit, Gemini embeddings, Playwright scraper

## Course Context
- **Institution**: University of Illinois
- **Role**: Teaching tool / student resource

## AI Assistant Guidelines

### DO:
- Help understand the search architecture and embedding flow
- Explain Gemini API usage and embedding concepts
- Assist with Streamlit UI improvements
- Help debug scraping or embedding issues

### DON'T:
- Provide complete solutions to student assignments using this tool
- Generate writeups that students should create themselves

## Key Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run app
streamlit run app.py

# Update writeups (optional)
pip install playwright && playwright install chromium
python scrape_kaggle_writeups_playwright.py
```

## Architecture

```
scraper → banana_writeups.json → ensure_embeddings() → app.py search UI
```

## Session Log
