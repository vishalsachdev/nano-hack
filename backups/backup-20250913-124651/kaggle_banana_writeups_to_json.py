#!/usr/bin/env python3
"""
Scrape all Kaggle Banana competition writeups via Firecrawl API
and save a JSON array of entries to a local file.

Relies on FIRECRAWL_API_KEY being set in the environment.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any

import requests


FIRECRAWL_API = "https://api.firecrawl.dev/v0/crawl"
OUTPUT_FILE = "banana_writeups.json"


def crawl_firecrawl(api_key: str) -> str:
    """Start the Firecrawl crawl, return jobId."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "url": "https://www.kaggle.com/competitions/banana/writeups",
        "crawlerOptions": {
            "allowExternalLinks": False,
            "deduplicateSimilarURLs": True,
            "limit": 100,
            "maxDiscoveryDepth": 2,
        },
        "pageOptions": {
            "formats": [
                {
                    "type": "json",
                    "prompt": (
                        """
                        Extract all writeup entries with their title, subtitle, description, and URL in the exact format:
                        {"title": "...", "subtitle": "...", "description": "...", "url": "..."}.
                        Return as an array of objects.
                        """
                    ),
                    "schema": {
                        "type": "object",
                        "properties": {
                            "entries": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["title", "subtitle", "description", "url"],
                                    "properties": {
                                        "url": {"type": "string"},
                                        "title": {"type": "string"},
                                        "subtitle": {"type": "string"},
                                        "description": {"type": "string"},
                                    },
                                },
                            }
                        },
                    },
                }
            ]
        },
    }

    # Start async crawl and get jobId
    resp = requests.post(FIRECRAWL_API, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    started = resp.json()
    job_id = started.get("jobId") or started.get("id")
    if not job_id:
        raise RuntimeError(f"Unexpected Firecrawl response: {started}")
    return job_id


def fetch_crawl_result(api_key: str, job_id: str, *, timeout_s: int = 300, poll_s: float = 2.0) -> Dict[str, Any]:
    """Poll Firecrawl for crawl completion and return the final result."""
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    candidate_urls = [
        f"{FIRECRAWL_API}/{job_id}",
        f"{FIRECRAWL_API}/status/{job_id}",
        f"{FIRECRAWL_API}/result/{job_id}",
        f"{FIRECRAWL_API}?jobId={job_id}",
        f"https://api.firecrawl.dev/v0/jobs/{job_id}",
    ]
    deadline = time.time() + timeout_s
    last = {}
    while time.time() < deadline:
        j = None
        for url in candidate_urls:
            r = requests.get(url, headers=headers, timeout=60)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            j = r.json()
            last = j
            break
        if j is None:
            time.sleep(poll_s)
            continue

        # Heuristic: when 'data' exists and is non-empty, assume done
        data = j.get("data")
        status = j.get("status") or j.get("state")
        completed = j.get("completed")
        total = j.get("total")

        if data:
            return j
        # Some APIs indicate completion by status/ratio
        if status in ("completed", "done", "finished"):
            return j
        if isinstance(completed, int) and isinstance(total, int) and total > 0 and completed >= total:
            return j

        time.sleep(poll_s)

    # Timed out; return whatever we last saw
    return last


def extract_entries(crawl_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract entries from the crawl result, de-duplicated by URL."""
    items: List[Dict[str, str]] = []
    data = crawl_result or {}

    # Expected shape: { data: [ { json: { entries: [ ... ] } }, ... ] }
    for page in data.get("data", []) or []:
        page_json = page.get("json") or {}
        for entry in page_json.get("entries", []) or []:
            # Normalize fields and ensure presence
            title = (entry.get("title") or "").strip()
            subtitle = (entry.get("subtitle") or "").strip()
            description = (entry.get("description") or "").strip()
            url = (entry.get("url") or "").strip()

            if not (title and url):
                continue

            items.append({
                "title": title,
                "subtitle": subtitle,
                "description": description,
                "url": url,
            })

    # De-duplicate by URL
    seen = set()
    unique: List[Dict[str, str]] = []
    for it in items:
        u = it["url"]
        if u in seen:
            continue
        seen.add(u)
        unique.append(it)

    return unique


def save_json(entries: List[Dict[str, str]], path: str = OUTPUT_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def main() -> int:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("FIRECRAWL_API_KEY is not set. Please export it and rerun.", file=sys.stderr)
        return 1

    print("Starting Firecrawl crawl for Kaggle writeups…")
    job_id = crawl_firecrawl(api_key)
    print(f"Crawl started. Job: {job_id}")

    result = fetch_crawl_result(api_key, job_id)

    # Save raw for debugging if needed
    try:
        with open("banana_writeups_raw.json", "w", encoding="utf-8") as rf:
            json.dump(result, rf, indent=2, ensure_ascii=False)
    except Exception:
        pass

    entries = extract_entries(result)
    print(f"Extracted {len(entries)} unique entries.")

    save_json(entries, OUTPUT_FILE)
    print(f"Saved JSON to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
