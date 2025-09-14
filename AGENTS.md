# Repository Guidelines

## Project Structure & Module Organization
- `app.py` — Streamlit UI (search box, progress, two‑column results).
- `gemini_search.py` — embeddings, cosine search, optional re‑rank/explain.
- `scrape_kaggle_writeups_playwright.py` — Playwright scraper for Kaggle writeups.
- `banana_writeups.json` — curated dataset: [{title, subtitle, url}].
- `data/` — cached artifacts (`embeddings.npy`, `embeddings_meta.json`, `query_logs.jsonl`).
- `article/` — long‑form writeups for Substack.

## Build, Test, and Development Commands
- Create venv + install deps:
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
- Run app locally: `streamlit run app.py`
- Compute embeddings (first run will cache): set `GEMINI_API_KEY` and start app, or run a small script using `ensure_embeddings()`.
- Scrape writeups (optional update):
  - `pip install playwright && playwright install chromium`
  - `python scrape_kaggle_writeups_playwright.py`

## Coding Style & Naming Conventions
- Python 3.9+; 4‑space indents; UTF‑8 files.
- Use type hints and short, clear functions. Snake_case names; constants UPPER_CASE.
- Prefer docstrings over inline comments; keep dependencies minimal.
- Follow existing patterns and avoid broad refactors in unrelated changes.

## Testing Guidelines
- No formal test suite yet; prioritize quick manual checks:
  - Load app, run a few featured queries, verify links open.
  - If `banana_writeups.json` changes, ensure embeddings regenerate and counts match.
- If adding tests, use pytest in `tests/` with `test_*.py` names and small fixtures.

## Commit & Pull Request Guidelines
- Use Conventional Commit style: `feat:`, `fix:`, `chore:`, `docs:`, `ui:`.
- Scope examples: `feat(app): …`, `docs(article): …`.
- PRs should include: what/why, before/after screenshots for UI, and any deployment notes.
- Do not commit secrets or large binaries. Keep `data/query_logs.jsonl` out of Git.

## Security & Configuration Tips
- Secrets: `GEMINI_API_KEY` via environment or Streamlit `st.secrets`. Never commit keys.
- Streamlit Cloud redeploys on push to `main`. Verify after changes.

## Architecture Overview
- Flow: scraper → `banana_writeups.json` → `ensure_embeddings()` → `app.py` search UI.
- Updating data? Re‑run scraper, commit JSON, and let embeddings cache refresh on next run.
