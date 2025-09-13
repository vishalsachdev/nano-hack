"""Page navigation and entry extraction for Kaggle writeups"""

import time
import requests
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from scraper_config import DEFAULT_HEADERS, get_config

class PageNavigator:
    """Handles pagination and entry extraction from Kaggle writeup pages"""

    def __init__(self):
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.failed_requests = []

    def get_page_entries(self, page_num: int) -> List[Dict[str, Any]]:
        """Get all entries from a specific page"""
        print(f"🔄 Scraping page {page_num}...")

        page_url = f"{self.config['base_url']}?page={page_num}"

        try:
            response = self._make_request(page_url)
            if not response:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            entries = self._extract_entries_from_page(soup, page_num)

            print(f"✓ Found {len(entries)} entries on page {page_num}")
            return entries

        except Exception as e:
            print(f"❌ Error scraping page {page_num}: {str(e)}")
            self.failed_requests.append({
                'page': page_num,
                'url': page_url,
                'error': str(e),
                'timestamp': time.time()
            })
            return []

    def _make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        if retries is None:
            retries = self.config['retry_attempts']

        for attempt in range(retries + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config['timeout']
                )

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = self.config['retry_delay'] * (2 ** attempt)
                    print(f"⚠ Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"⚠ HTTP {response.status_code} for {url}")

            except requests.RequestException as e:
                if attempt < retries:
                    wait_time = self.config['retry_delay'] * (2 ** attempt)
                    print(f"⚠ Request failed (attempt {attempt + 1}/{retries + 1}): {str(e)}")
                    print(f"  Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Failed after {retries + 1} attempts: {str(e)}")

        return None

    def _extract_entries_from_page(self, soup: BeautifulSoup, page_num: int) -> List[Dict[str, Any]]:
        """Extract entry data from page HTML"""
        entries = []

        # This is a placeholder - actual CSS selectors need to be determined
        # by inspecting the Kaggle writeups page structure
        entry_selectors = [
            'div[data-testid="writeup-card"]',  # Common pattern for cards
            '.writeup-item',                     # Alternative selector
            'article.writeup',                   # Another possibility
            '.submission-card'                   # Competition submissions
        ]

        entry_elements = []
        for selector in entry_selectors:
            entry_elements = soup.select(selector)
            if entry_elements:
                print(f"✓ Using selector: {selector}")
                break

        if not entry_elements:
            print(f"⚠ No entry elements found on page {page_num}")
            # Fallback: look for any links to writeups
            writeup_links = soup.find_all('a', href=re.compile(r'/writeups/'))
            print(f"Found {len(writeup_links)} writeup links as fallback")

            for link in writeup_links:
                entry = self._extract_entry_from_link(link)
                if entry:
                    entries.append(entry)

            return entries

        # Extract data from found elements
        for element in entry_elements:
            entry = self._extract_entry_from_element(element)
            if entry:
                entries.append(entry)

        return entries

    def _extract_entry_from_element(self, element) -> Optional[Dict[str, Any]]:
        """Extract entry data from a page element"""
        try:
            # Try to find title - common selectors
            title_selectors = ['h3', 'h4', '.title', '[data-testid*="title"]', 'a']
            title = None
            title_link = None

            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title_elem.name == 'a' or title_elem.find('a'):
                        link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                        title_link = link_elem.get('href') if link_elem else None
                    break

            if not title:
                return None

            # Try to find description/subtitle
            desc_selectors = ['.description', '.subtitle', 'p', '.summary']
            description = ""
            subtitle = ""

            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    text = desc_elem.get_text(strip=True)
                    if not subtitle and len(text) < 150:  # Short text is likely subtitle
                        subtitle = text
                    elif not description:
                        description = text
                    break

            # Construct full URL
            if title_link:
                if title_link.startswith('/'):
                    url = f"https://www.kaggle.com{title_link}"
                elif not title_link.startswith('http'):
                    url = urljoin(self.config['base_url'], title_link)
                else:
                    url = title_link
            else:
                # Generate URL from title if no direct link found
                url_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
                url_slug = re.sub(r'\s+', '-', url_slug)
                url = f"{self.config['writeup_base_url']}{url_slug}"

            return {
                'title': title,
                'subtitle': subtitle or title[:100] + "..." if len(title) > 100 else title,
                'description': description or f"Competition entry: {title}",
                'url': url
            }

        except Exception as e:
            print(f"⚠ Error extracting entry: {str(e)}")
            return None

    def _extract_entry_from_link(self, link_element) -> Optional[Dict[str, Any]]:
        """Extract entry data from a simple link element (fallback method)"""
        try:
            title = link_element.get_text(strip=True)
            if not title:
                return None

            href = link_element.get('href')
            if href:
                if href.startswith('/'):
                    url = f"https://www.kaggle.com{href}"
                else:
                    url = href
            else:
                return None

            return {
                'title': title,
                'subtitle': title[:100] + "..." if len(title) > 100 else title,
                'description': f"Competition entry: {title}",
                'url': url
            }

        except Exception as e:
            print(f"⚠ Error extracting from link: {str(e)}")
            return None

    def get_total_pages(self) -> int:
        """Determine total number of pages available"""
        print("🔄 Determining total pages...")

        try:
            response = self._make_request(self.config['base_url'])
            if not response:
                print("⚠ Could not fetch first page to determine total pages")
                return self.config['max_pages']  # Use configured maximum

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for pagination indicators
            pagination_selectors = [
                '.pagination .page-link:last-child',
                '[aria-label="Go to last page"]',
                '.pagination-item:last-child',
                '.page-numbers:last-child'
            ]

            for selector in pagination_selectors:
                last_page_elem = soup.select_one(selector)
                if last_page_elem:
                    # Extract page number from text or href
                    text = last_page_elem.get_text(strip=True)
                    if text.isdigit():
                        total_pages = int(text)
                        print(f"✓ Found {total_pages} total pages")
                        return min(total_pages, self.config['max_pages'])

                    # Try extracting from href
                    href = last_page_elem.get('href')
                    if href:
                        page_match = re.search(r'page=(\d+)', href)
                        if page_match:
                            total_pages = int(page_match.group(1))
                            print(f"✓ Found {total_pages} total pages from href")
                            return min(total_pages, self.config['max_pages'])

            # Fallback: look for any page indicators
            page_numbers = soup.find_all(text=re.compile(r'Page \d+ of (\d+)'))
            if page_numbers:
                match = re.search(r'Page \d+ of (\d+)', page_numbers[0])
                if match:
                    total_pages = int(match.group(1))
                    print(f"✓ Found {total_pages} total pages from text")
                    return min(total_pages, self.config['max_pages'])

        except Exception as e:
            print(f"⚠ Error determining total pages: {str(e)}")

        print(f"⚠ Could not determine total pages, using configured maximum: {self.config['max_pages']}")
        return self.config['max_pages']

    def wait_between_requests(self) -> None:
        """Wait between requests to avoid rate limiting"""
        delay = self.config['delay_between_requests']
        if delay > 0:
            time.sleep(delay)

    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """Get list of failed requests for retry"""
        return self.failed_requests.copy()

    def clear_failed_requests(self) -> None:
        """Clear failed requests list"""
        self.failed_requests.clear()