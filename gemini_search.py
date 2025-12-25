#!/usr/bin/env python3
"""
Utilities for Gemini-powered semantic search over local JSON entries.

- Builds and caches embeddings using text-embedding-004
- Fast cosine similarity search with NumPy
- Optional re-ranking and explanations via gemini-2.0-flash

Env:
  GEMINI_API_KEY
Cache files:
  data/embeddings.npy
  data/embeddings_meta.json
"""

import os
import contextlib
import json
from typing import List, Dict, Tuple

import numpy as np
import google.generativeai as genai


EMBED_MODEL = "models/text-embedding-004"
GEN_MODEL = "gemini-2.0-flash"

EMB_PATH = "data/embeddings.npy"
META_PATH = "data/embeddings_meta.json"


def _ensure_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback to Streamlit secrets if available
        with contextlib.suppress(Exception):
            import streamlit as st  # lazy import to avoid hard dependency elsewhere
            api_key = st.secrets.get("GEMINI_API_KEY") or api_key
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set (env or Streamlit secrets)")
    genai.configure(api_key=api_key)


def _entry_text(e: Dict) -> str:
    # Concatenate key fields for semantic representation
    parts = [e.get("title", ""), e.get("subtitle", "")]
    return "\n\n".join([p for p in parts if p])


def ensure_embeddings(entries: List[Dict]) -> np.ndarray:
    """Create or load cached embeddings for entries.

    Returns: matrix shape (N, D)
    """
    os.makedirs("data", exist_ok=True)

    # If cache exists and matches length, load it
    if os.path.exists(EMB_PATH) and os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("count") == len(entries) and meta.get("model") == EMBED_MODEL:
            m = np.load(EMB_PATH)
            if m.ndim == 3:
                m = m.reshape(-1, m.shape[-1])
            return m

    # Build embeddings
    _ensure_client()
    texts = [_entry_text(e) for e in entries]
    batch_size = 64
    vecs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i+batch_size]
        res = genai.embed_content(model=EMBED_MODEL, content=chunk)

        # Normalize response across SDK variants
        vectors: List[List[float]] = []
        if isinstance(res, dict):
            if 'embeddings' in res:
                for e in res['embeddings']:
                    if isinstance(e, dict):
                        vectors.append(e.get('values') or e.get('embedding'))
            elif 'embedding' in res:
                e = res['embedding']
                vectors.append(e.get('values') if isinstance(e, dict) else e)
        else:
            try:
                vectors = [getattr(e, 'values', None) or getattr(e, 'embedding', None) for e in res.embeddings]
            except Exception:
                try:
                    e = getattr(res, 'embedding')
                    vectors = [getattr(e, 'values', None) or e]
                except Exception:
                    pass

        for v in vectors:
            if v is not None:
                vecs.append(list(v))

    mat = np.array(vecs, dtype=np.float32)
    if mat.ndim == 3:
        mat = mat.reshape(-1, mat.shape[-1])
    np.save(EMB_PATH, mat)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({"count": len(entries), "model": EMBED_MODEL}, f)
    return mat


def embed_query(query: str) -> np.ndarray:
    _ensure_client()
    res = genai.embed_content(model=EMBED_MODEL, content=query)
    if isinstance(res, dict):
        e = res.get('embedding') or {}
        vals = e.get('values') if isinstance(e, dict) else e
    else:
        e = getattr(res, 'embedding', None)
        vals = getattr(e, 'values', None) or e
    return np.array(vals, dtype=np.float32)


def cosine_top_k(q: np.ndarray, mat: np.ndarray, k: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    # Normalize
    qn = q / (np.linalg.norm(q) + 1e-8)
    mn = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-8)
    sims = mn @ qn
    idxs = np.argsort(-sims)[:k]
    return idxs, sims[idxs]


def _get_model():
    _ensure_client()
    return genai.GenerativeModel(GEN_MODEL)


def rerank_with_gemini(query: str, candidates: List[Dict], limit: int = 20) -> List[Tuple[Dict, float]]:
    """Ask Gemini to re-rank top candidates. Returns list of (item, score)."""
    model = _get_model()
    formatted = "\n".join(
        f"- title: {c.get('title','')}\n  subtitle: {c.get('subtitle','')}\n  url: {c.get('url','')}\n  sim: {c.get('score',0):.3f}"
        for c in candidates[: max(limit, 50)]
    )
    prompt = (
        "You are helping students find relevant projects.\n"
        f"Query: {query}\n"
        "Candidates (with initial similarity scores):\n"
        f"{formatted}\n\n"
        f"Return the best {limit} items as JSON array with fields: url, reason, score (0-1)."
    )
    resp = model.generate_content(prompt)
    text = resp.text or "[]"
    try:
        parsed = json.loads(text)
    except Exception:
        # If parsing fails, fall back to initial ranking
        return [(c, float(c.get("score", 0))) for c in candidates[:limit]]

    # Map by URL for lookup
    by_url = {c.get("url"): c for c in candidates}
    out: List[Tuple[Dict, float]] = []
    for item in parsed:
        url = item.get("url")
        sc = float(item.get("score", 0))
        if url in by_url:
            out.append((by_url[url], sc))
    if not out:
        out = [(c, float(c.get("score", 0))) for c in candidates[:limit]]
    return out[:limit]


def explain_results(query: str, items: List[Dict]) -> str:
    model = _get_model()
    bullet = "\n".join(f"- {i.get('title','')} — {i.get('subtitle','')}" for i in items)
    prompt = (
        "Explain to a student why these projects match the query, in 3-4 short bullets.\n"
        f"Query: {query}\nProjects:\n{bullet}"
    )
    resp = model.generate_content(prompt)
    return resp.text or ""
