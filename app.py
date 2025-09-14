#!/usr/bin/env python3
"""
Student-friendly project discovery app powered by Gemini.

Features:
- Local semantic search over banana_writeups.json using Gemini embeddings
- Optional Gemini re-ranking and explanations

Usage:
  export GEMINI_API_KEY=YOUR_KEY
  streamlit run app.py
"""

import os
import json
import hashlib
import time
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Tuple

import numpy as np
import streamlit as st

from gemini_search import (
    ensure_embeddings,
    embed_query,
    cosine_top_k,
    rerank_with_gemini,
    explain_results,
)


DATA_FILE = "banana_writeups.json"


@lru_cache(maxsize=1)
def load_entries() -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    st.set_page_config(page_title="Project Explorer", page_icon="🍌", layout="wide")
    st.title("Nano Banana Project Explorer")
    st.caption("Discover projects using semantic search powered by Gemini")

    # Light styling for result cards
    st.markdown(
        """
        <style>
        .nb-card{border:1px solid #e6e6e6;border-radius:10px;padding:12px 14px;margin:10px 0;background:rgba(0,0,0,0.02)}
        .nb-title{font-weight:600;font-size:1.06rem;margin-bottom:4px}
        .nb-sub{color:#555;margin-top:2px;margin-bottom:6px}
        .nb-meta{font-size:0.85rem;color:#888}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.subheader("About the Nano Banana Hackathon")
        st.markdown(
            """
            The Nano Banana Hackathon is a community hackathon hosted on Kaggle, inviting builders to create apps and experiences
            with next‑gen AI capabilities. Participants compete for over $400,000 in prizes across the Overall Track and special
            technology prize tracks (e.g., ElevenLabs, Fal). Projects span creative tools, virtual try‑on, marketing and design,
            education, gaming, and more.

            Explore all entries in the Writeups section and use the search below to quickly find relevant projects to learn from.
            """
        )
        st.link_button("View Hackathon Overview", "https://www.kaggle.com/competitions/banana/overview")
        st.divider()

    # Sidebar controls
    # Results count selector (moved from sidebar)
    top_k = st.slider("Results", min_value=5, max_value=50, value=20, step=5)
    # Re-ranking is enabled by default to improve result quality
    enable_rerank = True

    # Ensure embeddings
    entries = load_entries()
    st.caption(f"Over 800 submissions indexed (currently {len(entries)} writeups).")
    try:
        embedding_matrix = ensure_embeddings(entries)
    except Exception as e:
        st.error(f"Failed to prepare embeddings: {e}")
        return

    # Featured searches
    st.subheader("Featured: Health & Wellness")
    featured = [
        "mental health",
        "fitness coaching",
        "nutrition and meal planning",
        "sleep tracking",
        "meditation and mindfulness",
        "relationship support",
    ]
    cols = st.columns(min(6, len(featured)))
    for i, q in enumerate(featured):
        if cols[i % 6].button(q):
            st.session_state["query_input"] = q
            st.rerun()

    # Query box
    query = st.text_input(
        "Search projects",
        key="query_input",
        placeholder="e.g., virtual try-on, marketing posters, comics",
    )
    if not query:
        st.info("Type a topic or skill to get started.")
        return

    # Search with visual progress indicators
    progress = st.progress(0)
    status = st.empty()
    t0 = time.time()

    try:
        status.info("Embedding your query…")
        q_emb = embed_query(query)
        progress.progress(30)

        status.info("Finding similar projects…")
        idxs, scores = cosine_top_k(q_emb, embedding_matrix, k=max(top_k, 50))
        progress.progress(65)
    except Exception as e:
        status.empty()
        progress.empty()
        st.error(f"Search failed: {e}")
        return

    candidates = [entries[i] | {"score": float(scores[n])} for n, i in enumerate(idxs)]

    # Optional re-ranking with Gemini
    results: List[Tuple[Dict, float]]
    if enable_rerank:
        try:
            status.info("Re-ranking with Gemini for best matches…")
            reranked = rerank_with_gemini(query, candidates, limit=top_k)
            results = reranked
        except Exception as e:
            st.warning(f"Re-ranking unavailable ({e}). Showing semantic matches only.")
            results = [(c, c["score"]) for c in candidates[:top_k]]
        progress.progress(90)
    else:
        results = [(c, c["score"]) for c in candidates[:top_k]]
        progress.progress(85)

    status.success(f"Done in {time.time() - t0:.1f}s")
    progress.progress(100)

    # Default sort is relevance; simply trim to top_k
    filtered = results[:top_k]

    # Show results
    st.subheader(f"Results ({len(filtered)})")
    cols = st.columns(2)

    def render_card(container, item, sc):
        title = item.get("title", "Untitled")
        url = item.get("url")
        subtitle = item.get("subtitle", "")
        html = f"""
        <div class='nb-card'>
          <div class='nb-title'><a href='{url}' target='_blank'>{title}</a></div>
          {f"<div class='nb-sub'>{subtitle}</div>" if subtitle else ""}
          <div class='nb-meta'>Relevance: {sc:.3f}</div>
        </div>
        """
        container.markdown(html, unsafe_allow_html=True)

    for i, (item, sc) in enumerate(filtered):
        render_card(cols[i % 2], item, sc)

    # Optional explanations
    # Explanations removed per request

    # Anonymized query logging
    try:
        os.makedirs("data", exist_ok=True)
        qhash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "query_sha256": qhash,
            "query_len": len(query),
            "rerank": bool(enable_rerank),
            "explain": False,
            "filters": None,
            "results": len(filtered),
            "top_urls": [r[0].get("url") for r in filtered[:5]],
        }
        with open("data/query_logs.jsonl", "a", encoding="utf-8") as lf:
            lf.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
