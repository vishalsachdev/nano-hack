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
    st.caption("Discover student projects using semantic search powered by Gemini")

    # Sidebar controls
    with st.sidebar:
        st.header("Search Options")
        top_k = st.slider("Results", min_value=5, max_value=50, value=20, step=5)
        enable_rerank = st.checkbox("Gemini re-rank for relevance", value=True)
        enable_explain = st.checkbox("Explain matches (Gemini)", value=False)
        st.markdown("---")
        st.markdown(
            "Set `GEMINI_API_KEY` in your environment. The app will cache embeddings locally for speed."
        )

    # Ensure embeddings
    entries = load_entries()
    try:
        embedding_matrix = ensure_embeddings(entries)
    except Exception as e:
        st.error(f"Failed to prepare embeddings: {e}")
        return

    # Query box
    query = st.text_input("Search projects", placeholder="e.g., virtual try-on, marketing posters, comics")
    if not query:
        st.info("Type a topic or skill to get started.")
        return

    # Search
    try:
        q_emb = embed_query(query)
        idxs, scores = cosine_top_k(q_emb, embedding_matrix, k=max(top_k, 50))
    except Exception as e:
        st.error(f"Search failed: {e}")
        return

    candidates = [entries[i] | {"score": float(scores[n])} for n, i in enumerate(idxs)]

    # Optional re-ranking with Gemini
    results: List[Tuple[Dict, float]]
    if enable_rerank:
        try:
            reranked = rerank_with_gemini(query, candidates, limit=top_k)
            results = reranked
        except Exception as e:
            st.warning(f"Re-ranking unavailable ({e}). Showing semantic matches only.")
            results = [(c, c["score"]) for c in candidates[:top_k]]
    else:
        results = [(c, c["score"]) for c in candidates[:top_k]]

    # Show results
    st.subheader("Results")
    for item, sc in results:
        title = item.get("title", "Untitled")
        url = item.get("url")
        subtitle = item.get("subtitle", "")
        st.markdown(f"- [{title}]({url})  ")
        if subtitle:
            st.markdown(f"  {subtitle}")
        st.caption(f"Similarity: {sc:.3f}")

    # Optional explanations
    if enable_explain:
        with st.expander("Why these results? (Gemini)"):
            try:
                text = explain_results(query, [r[0] for r in results])
                st.write(text)
            except Exception as e:
                st.warning(f"Explanation unavailable: {e}")


if __name__ == "__main__":
    main()

