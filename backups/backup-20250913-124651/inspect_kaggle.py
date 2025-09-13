#!/usr/bin/env python3
"""
Detailed inspection of Kaggle writeups page
"""

import requests
from bs4 import BeautifulSoup
from scraper_config import DEFAULT_HEADERS

def inspect_kaggle_page():
    """Detailed inspection of the Kaggle page"""
    url = "https://www.kaggle.com/competitions/banana/writeups"

    print(f"🔍 Inspecting: {url}")

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
        print(f"Status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if page requires JavaScript
        scripts = soup.find_all('script')
        print(f"Scripts found: {len(scripts)}")

        # Look for data attributes that might indicate dynamic content
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        print(f"Elements with data attributes: {len(elements_with_data)}")

        # Check for any mention of writeups in the HTML
        html_text = soup.get_text().lower()
        writeup_mentions = html_text.count('writeup')
        submission_mentions = html_text.count('submission')

        print(f"'writeup' mentions: {writeup_mentions}")
        print(f"'submission' mentions: {submission_mentions}")

        # Look for links to individual writeups
        all_links = soup.find_all('a', href=True)
        writeup_links = [link for link in all_links if '/writeups/' in link.get('href', '')]

        print(f"Total links: {len(all_links)}")
        print(f"Writeup links found: {len(writeup_links)}")

        if writeup_links:
            print("\nSample writeup links:")
            for link in writeup_links[:5]:
                href = link.get('href')
                text = link.get_text(strip=True)
                print(f"  {href} -> {text}")

        # Check if we need to be logged in
        if 'sign in' in html_text or 'login' in html_text:
            print("⚠ Page may require authentication")

        # Save a sample of the HTML for manual inspection
        with open('kaggle_sample.html', 'w') as f:
            f.write(str(soup.prettify()))
        print("✓ Saved HTML sample to kaggle_sample.html")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_kaggle_page()