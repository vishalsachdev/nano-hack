"""Configuration settings for the batch scraper"""

import os

# Scraping configuration
SCRAPER_CONFIG = {
    # Batch processing settings
    'entries_per_page': 20,
    'pages_per_batch': 5,  # Process 100 entries at a time
    'max_pages': 50,  # Upper limit for safety

    # Rate limiting
    'delay_between_requests': 2.0,  # Seconds between requests
    'delay_between_batches': 10.0,  # Seconds between batches

    # Error handling
    'retry_attempts': 3,
    'retry_delay': 5.0,  # Seconds before retry
    'timeout': 30,  # Request timeout in seconds

    # Progress tracking
    'checkpoint_frequency': 1,  # Save after each batch
    'progress_file': 'progress.json',
    'output_file': 'hackathon_entries.json',
    'backup_dir': 'backups',

    # URLs
    'base_url': 'https://www.kaggle.com/competitions/banana/writeups',
    'writeup_base_url': 'https://www.kaggle.com/competitions/banana/writeups/',
}

# User agent for requests
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)

# Headers for requests
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_config():
    """Get configuration with environment variable overrides"""
    config = SCRAPER_CONFIG.copy()

    # Allow environment variable overrides
    if os.getenv('BATCH_SIZE'):
        config['pages_per_batch'] = int(os.getenv('BATCH_SIZE'))

    if os.getenv('DELAY'):
        config['delay_between_requests'] = float(os.getenv('DELAY'))

    if os.getenv('MAX_PAGES'):
        config['max_pages'] = int(os.getenv('MAX_PAGES'))

    return config