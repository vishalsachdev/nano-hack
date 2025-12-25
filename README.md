# Nano Banana Project Explorer

A semantic search tool to help students discover relevant projects from the [Nano Banana Hackathon](https://www.kaggle.com/competitions/banana/overview) on Kaggle.

**[Try the Live App](https://nanobanana.streamlit.app/)** | **[Read the Build Story](article/intent-by-human-words-by-ai-nano-banana-explorer.html)**

---

## Why This Exists

Built for students in the [Information Systems Practicum](https://practicum.web.illinois.edu/syllabus/), this tool makes it easy to explore 800+ hackathon writeups by *idea* rather than keyword. Whether you're looking for inspiration on virtual try-on, marketing tools, health apps, or creative AI—semantic search surfaces relevant examples fast.

## Features

- **Semantic Search** – Find projects by concept, not just keywords. Search "fitness coaching" and get results about workout apps, health tracking, and personal training tools.
- **Gemini-Powered** – Uses `text-embedding-004` for embeddings and `gemini-2.0-flash` for intelligent re-ranking.
- **800+ Projects Indexed** – Scraped from the Nano Banana Hackathon writeups on Kaggle.
- **Featured Searches** – Quick-access queries for health, wellness, and relationship topics.
- **Fast Startup** – Embeddings are cached locally for instant results after first run.

## Quick Start

1. **Install dependencies**
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set your Gemini API key**
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

Set `GEMINI_API_KEY` in **App Settings → Secrets** and point the entry file to `app.py`. The app auto-deploys on push to GitHub.

## How It Works

1. **Embeddings** – On first run, the app embeds all 800+ project titles/subtitles using Gemini's `text-embedding-004` model. Results are cached in `data/embeddings.npy`.

2. **Cosine Search** – Your query is embedded and compared against all projects using cosine similarity.

3. **Re-ranking** – Top candidates are re-ranked by `gemini-2.0-flash` for improved relevance.

4. **Results** – Projects are displayed in a two-column grid with title, subtitle, and relevance score.

## Project Structure

```
├── app.py                      # Streamlit UI
├── gemini_search.py            # Embeddings, search, re-ranking logic
├── banana_writeups.json        # Dataset (title, subtitle, url)
├── scrape_kaggle_writeups_playwright.py  # Headless scraper
├── data/                       # Cached embeddings and query logs
└── article/                    # Build story documentation
```

## Links

- **Live App**: https://nanobanana.streamlit.app/
- **Course**: [Practicum @ Illinois](https://practicum.web.illinois.edu/syllabus/)
- **Hackathon**: [Nano Banana on Kaggle](https://www.kaggle.com/competitions/banana/overview)
- **Writeups**: [All Submissions](https://www.kaggle.com/competitions/banana/writeups)

## Credits

Built with and for students in the Illinois Practicum. Human intent by Vishal; wiring by AI.
