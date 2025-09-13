#!/usr/bin/env python3
"""
Render Kaggle Banana writeups pages with Playwright and extract entries to JSON.

Output: banana_writeups.json (array of {title, subtitle, url})
"""

import json
import re
from typing import List, Dict

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


BASE = "https://www.kaggle.com"
LIST_URL = f"{BASE}/competitions/banana/writeups"
OUTPUT = "banana_writeups.json"


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def scrape_current_page(page) -> List[Dict[str, str]]:
    # Ensure anchors are present
    try:
        page.wait_for_selector('a[href^="/competitions/banana/writeups/"]', timeout=15000)
    except PlaywrightTimeout:
        # Give React another shot to hydrate
        try:
            page.wait_for_timeout(1500)
            page.wait_for_selector('a[href^="/competitions/banana/writeups/"]', timeout=5000)
        except PlaywrightTimeout:
            return []

    links = page.eval_on_selector_all(
        'a[href^="/competitions/banana/writeups/"]',
        "els => els.map(e => ({ href: e.getAttribute('href'), title: (e.innerText||'').trim() }))"
    )

    # Deduplicate links per page
    seen = set()
    items = []
    for ln in links:
        href = ln.get("href") or ""
        raw_text = ln.get("title") or ln.get("text") or ln.get("innerText") or ""
        title = normalize_whitespace(raw_text)
        if not href or href == "/competitions/banana/writeups":
            continue
        abs_url = href if href.startswith("http") else BASE + href
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # Parse anchor text: typically "check_circle SUBMITTED <title> <description>"
        parts = [normalize_whitespace(x) for x in raw_text.splitlines()]
        parts = [x for x in parts if x]
        while parts and parts[0].lower() in ("check_circle", "submitted", "submi tted"):
            parts.pop(0)
        anchor_title = parts[0] if parts else title
        anchor_desc = parts[1] if len(parts) > 1 else ""

        desc_clean = normalize_whitespace(anchor_desc)
        subtitle = desc_clean[:120] + ("..." if len(desc_clean) > 120 else "") if desc_clean else ""

        items.append({
            "title": normalize_whitespace(anchor_title),
            "subtitle": subtitle or desc_clean,
            "url": abs_url,
        })

    return items


def run() -> List[Dict[str, str]]:
    all_items: List[Dict[str, str]] = []
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        # Load first page
        page.goto(LIST_URL, wait_until="networkidle")
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeout:
            pass

        # Iterate numbered pagination buttons
        for i in range(1, 50):
            if i > 1:
                # Click the page button (Kaggle uses buttons, not anchors)
                try:
                    page.get_by_role('button', name=str(i)).click()
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(1200)
                except Exception:
                    break

            items = scrape_current_page(page)
            if not items:
                break
            for it in items:
                key = it["url"]
                if key in seen:
                    continue
                seen.add(key)
                all_items.append(it)

        browser.close()

    return all_items


if __name__ == "__main__":
    data = run()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} entries to {OUTPUT}")
