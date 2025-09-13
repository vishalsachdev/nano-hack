#!/usr/bin/env python3
"""
Test script to inspect Kaggle writeups page structure
"""

import requests
from bs4 import BeautifulSoup
from scraper_config import DEFAULT_HEADERS, get_config

def test_page_structure():
    """Test what the actual page structure looks like"""
    config = get_config()
    url = config['base_url']

    print(f"🔍 Testing page structure at: {url}")

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        print(f"✓ Page loaded successfully (Status: {response.status_code})")
        print(f"  Page title: {soup.title.string if soup.title else 'No title'}")

        # Look for common selectors
        selectors_to_test = [
            'div[data-testid="writeup-card"]',
            '.writeup-item',
            'article.writeup',
            '.submission-card',
            'a[href*="/writeups/"]',
            '.card',
            '.entry',
            '.competition-entry'
        ]

        print("\n🔍 Testing selectors:")
        found_elements = False

        for selector in selectors_to_test:
            elements = soup.select(selector)
            print(f"  {selector}: {len(elements)} elements")
            if elements:
                found_elements = True
                # Print first element structure
                first_elem = elements[0]
                print(f"    Sample: {first_elem.name} with classes: {first_elem.get('class', [])}")
                text_preview = first_elem.get_text(strip=True)[:100]
                print(f"    Text preview: {text_preview}...")

        if not found_elements:
            print("⚠ No elements found with standard selectors")
            print("\n📝 Page structure sample:")
            # Print first 2000 chars of page to understand structure
            print(soup.get_text()[:2000])

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_page_structure()