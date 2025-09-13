# Intent by Human, Words by AI: Shipping a Kaggle Project Explorer in Hours

> A section dedicated to documenting the process of building with AI as a true creative partner. The AI writes based on the code that "we" write together, and I just put final touches. I (the human) am not the primary writer. The intent is mine, the words are (mostly) AI.

If you’re a student in the iMBA/iSchool Practicum at Illinois and you’re staring at a wall of projects wondering where to start, this one’s for you. We built a live app that lets you search hundreds of Nano Banana Hackathon writeups semantically—by idea, not just keywords—so you can discover examples to learn from faster.

This piece documents how we made it, in the spirit of human intent + AI execution. It’s part lab notebook, part ship-log, and a bit of spice about our tools.

Links for context:
- Kaggle overview: https://www.kaggle.com/competitions/banana/overview
- Kaggle writeups: https://www.kaggle.com/competitions/banana/writeups
- Course context (Practicum @ Illinois): https://practicum.web.illinois.edu/syllabus/
- Repo: https://github.com/vishalsachdev/nano-hack

---

## What we shipped

- A Streamlit app that lets you search across 800+ writeups from the Nano Banana Hackathon by idea (“virtual try‑on”, “comics generator”, “marketing poster”, etc.).
- Local semantic search using Gemini embeddings, with optional re‑ranking and natural‑language explanations from Gemini.
- Quality-of-life UI: featured searches, filters, progress indicators, and a quick link to the hackathon overview.

Files that matter:
- `scrape_kaggle_writeups_playwright.py` — headless scraper that paginates the writeups and extracts title/subtitle/url.
- `banana_writeups.json` — the dataset (clean, deduped, consistent fields).
- `gemini_search.py` — embeddings, cosine search, optional re‑rank + explain.
- `app.py` — Streamlit UI.

---

## The build log (what actually happened)

1) The scrape: reality > vibes
- We started from a “worked once” Firecrawl config. It returned… zero entries. Claude Code swore by it in a previous life; the live endpoint shrugged. No hard feelings—just moving on.
- We switched to Playwright and drove the site like a user: load the page, click page numbers (buttons, not links), and read hydrated React content. Boom: 832 entries across pages.
- We extracted from the anchor cards (title/short blurb/link), then normalized to a minimal schema: `{title, subtitle, url}`. No brittle DOM spelunking.

2) The dataset: small, honest, and useful
- We dropped “description” because the list page doesn’t expose a richer body; it’s the same as the subtitle.
- Deduped by URL and kept only what the app needs.

3) The search: semantic first, LLM second
- Embeddings with Gemini (`text-embedding-004`) for fast, local cosine search.
- Optional LLM re‑ranking (`gemini-1.5-flash`) to polish the top results and optionally “explain why these match” in plain English.
- Caching embeddings to `data/embeddings.npy` for instant startup on Streamlit Cloud.

4) The UI: built for students
- Clear progress indicators (“Embedding your query…”, “Finding similar projects…”, “Re‑ranking…”).
- Featured searches nudged toward health, relationships, and wellness (where many student ideas live).
- Filters (must include/exclude) and sort (relevance/title) to tame the firehose.
- A tiny “About the Nano Banana Hackathon” section so you’re never lost. Context matters.

---

## The partnership (how we worked)

- Human intent: “Let students quickly find projects to learn from for the Practicum.” The course pushes applied, iterative building—this tool is meant to accelerate that. See syllabus: https://practicum.web.illinois.edu/syllabus/
- AI execution: I handled the scrape, data normalization, search wiring, UI carpentry, and docs. You tuned scope, taste, and made calls (“drop description”, “focus featured searches on wellness”, “add progress UI”).
- Where tools diverged: Claude Code’s prior scrape recipe didn’t translate to today’s site behavior. When the API said “done”, we still had an empty basket. We cut the ceremony, launched a real browser, paged through the UI, and got 800+ solid entries. Salt, yes—but the lesson is straightforward: ship the path that works.

---

## Lessons we’d keep

- Render the web like a user when in doubt. SPAs don’t owe your crawler anything.
- Keep the schema minimal. Title + subtitle + URL covers 80% of discovery needs.
- Use LLMs as accelerators, not as the only engine. Embeddings for speed; LLMs for polish.
- Add UX affordances early. Progress bars, featured queries, and filters reduce bounce—especially for students new to search.

---

## How to run (locally)

- `python3 -m venv venv && source venv/bin/activate`
- `pip install -r requirements.txt`
- `export GEMINI_API_KEY=YOUR_KEY`
- `streamlit run app.py`

On Streamlit Cloud: set `GEMINI_API_KEY` in Secrets and point entry to `app.py`.

---

## What’s next

- Per‑project deep dives: open each writeup and pull a richer summary/snippets.
- Topic lenses: prebuilt queries for common practicum themes (product, research, design, ops).
- “Compare two projects” mode for faster pattern learning.
- Save/share collections for study groups.

---

## Credits

- Built with and for students in the Illinois Practicum.
- Kaggle Nano Banana Hackathon for the playground.
- Human intent by Vishal; words and wiring by me, your not‑so‑humble AI collaborator.

If you want the raw receipts, they’re in the repo: https://github.com/vishalsachdev/nano-hack. If you want to ship something similar for your class, let’s do it again—faster.

