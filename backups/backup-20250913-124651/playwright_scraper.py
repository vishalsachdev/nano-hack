#!/usr/bin/env python3
"""
Playwright-based scraper for Kaggle writeups
This handles the dynamic content loading that requires browser execution
"""

import json
import re
import time
from typing import List, Dict, Any
from checkpoint_manager import CheckpointManager

def extract_entries_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract entries from the visible text content"""
    entries = []

    # Split text into lines and process
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for "Submitted" indicators which mark entry starts
        if line == "Submitted" and i > 0:
            # Previous line is usually the title
            title = lines[i-1].strip()

            # Next line is usually the subtitle/description
            subtitle = ""
            if i + 1 < len(lines):
                subtitle = lines[i+1].strip()

            # Look ahead for author (usually comes after subtitle)
            author = ""
            if i + 2 < len(lines):
                potential_author = lines[i+2].strip()
                # Author lines are typically short and don't contain common description words
                if len(potential_author) < 50 and not any(word in potential_author.lower()
                    for word in ['using', 'with', 'the', 'and', 'for', 'in', 'that', 'to']):
                    author = potential_author

            # Generate URL from title
            url_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
            url_slug = re.sub(r'\s+', '-', url_slug)
            url = f"https://www.kaggle.com/competitions/banana/writeups/{url_slug}"

            if title and title != "Submitted":  # Ensure we have a valid title
                entries.append({
                    'title': title,
                    'subtitle': subtitle or title,
                    'description': subtitle or f"Competition entry: {title}",
                    'url': url
                })

        i += 1

    return entries

def scrape_page_with_playwright(page_num: int = 1) -> List[Dict[str, Any]]:
    """Scrape a single page using Playwright"""
    from mcp__playwright import (
        playwright_navigate,
        playwright_get_visible_text,
        playwright_click
    )

    print(f"🔄 Scraping page {page_num} with Playwright...")

    try:
        # Navigate to the writeups page
        base_url = "https://www.kaggle.com/competitions/banana/writeups"

        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page_num}"

        print(f"  Navigating to: {url}")
        playwright_navigate(url=url, headless=True)

        # Wait a moment for content to load
        time.sleep(3)

        # If not page 1, click the page number
        if page_num > 1:
            try:
                playwright_click(selector=f'a[aria-label="Go to page {page_num}"]')
                time.sleep(2)
            except:
                try:
                    # Alternative selector for page numbers
                    playwright_click(selector=f'button:has-text("{page_num}")')
                    time.sleep(2)
                except:
                    print(f"  ⚠ Could not click page {page_num}, trying direct navigation")

        # Get visible text content
        text_content = playwright_get_visible_text()

        # Extract entries from text
        entries = extract_entries_from_text(text_content)

        print(f"  ✓ Found {len(entries)} entries on page {page_num}")
        return entries

    except Exception as e:
        print(f"  ❌ Error scraping page {page_num}: {str(e)}")
        return []

def get_total_pages_playwright() -> int:
    """Get total number of pages using Playwright"""
    from mcp__playwright import playwright_navigate, playwright_get_visible_text

    try:
        playwright_navigate(url="https://www.kaggle.com/competitions/banana/writeups", headless=True)
        time.sleep(3)

        text_content = playwright_get_visible_text()

        # Look for pagination numbers at the end
        lines = text_content.split('\n')
        for line in reversed(lines):
            line = line.strip()
            # Look for sequences of numbers that might be pagination
            if re.match(r'^[\d\s]+$', line):
                numbers = [int(x) for x in line.split() if x.isdigit()]
                if numbers:
                    max_page = max(numbers)
                    if max_page > 1:  # Reasonable page count
                        print(f"✓ Found {max_page} total pages")
                        return max_page

        print("⚠ Could not determine total pages, defaulting to 10")
        return 10

    except Exception as e:
        print(f"❌ Error determining total pages: {e}")
        return 10

def run_playwright_batch_scraping(start_page: int = 1, max_pages: int = None):
    """Run batch scraping using Playwright"""

    print("🚀 Starting Playwright-based Nano Banana Hackathon Entry Scraper")
    print("=" * 60)

    # Initialize checkpoint manager
    checkpoint = CheckpointManager()

    # Determine total pages
    if max_pages is None:
        max_pages = get_total_pages_playwright()

    print(f"📊 Plan: Scrape pages {start_page} to {max_pages}")
    print()

    all_entries = []

    # Process each page
    for page_num in range(start_page, max_pages + 1):
        print(f"📄 Processing page {page_num}/{max_pages}...")

        entries = scrape_page_with_playwright(page_num)

        if entries:
            all_entries.extend(entries)

            # Save progress after each page
            new_entries_count = checkpoint.append_entries(entries)
            print(f"  ✓ Added {new_entries_count} new entries")

            # Save progress
            checkpoint.save_progress(
                current_page=page_num,
                total_pages=max_pages,
                entries_scraped=len(all_entries),
                last_batch_size=len(entries)
            )
        else:
            print(f"  ⚠ No entries found on page {page_num}")

        # Wait between pages
        time.sleep(2)
        print()

    # Final summary
    print("🎉 Scraping Complete!")
    print("=" * 40)
    print(f"Pages processed: {start_page} to {max_pages}")
    print(f"Total entries found: {len(all_entries)}")

    return all_entries

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Playwright-based Kaggle scraper")
    parser.add_argument('--start-page', type=int, default=1, help='Starting page')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to scrape')

    args = parser.parse_args()

    run_playwright_batch_scraping(
        start_page=args.start_page,
        max_pages=args.max_pages
    )