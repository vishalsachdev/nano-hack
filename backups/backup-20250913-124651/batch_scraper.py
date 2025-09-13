#!/usr/bin/env python3
"""
Batch scraper for Kaggle Nano Banana Hackathon entries

This script scrapes all competition writeups from Kaggle in manageable batches,
with progress tracking, error handling, and resume capabilities.
"""

import argparse
import sys
import time
from typing import List, Dict, Any, Optional

from page_navigator import PageNavigator
from checkpoint_manager import CheckpointManager
from scraper_config import get_config

class BatchScraper:
    """Main batch scraping orchestrator"""

    def __init__(self):
        self.config = get_config()
        self.navigator = PageNavigator()
        self.checkpoint = CheckpointManager(
            progress_file=self.config['progress_file'],
            output_file=self.config['output_file']
        )

    def run_batch_scraping(self, start_page: int = 1, end_page: Optional[int] = None,
                          resume: bool = False) -> None:
        """Run the batch scraping process"""

        print("🚀 Starting Nano Banana Hackathon Entry Scraper")
        print("=" * 60)

        # Handle resume mode
        if resume:
            progress = self.checkpoint.load_progress()
            if progress:
                start_page = progress['current_page'] + 1
                print(f"📍 Resuming from page {start_page}")
            else:
                print("⚠ No progress file found, starting from beginning")
                resume = False

        # Determine total pages if not specified
        if end_page is None:
            end_page = self.navigator.get_total_pages()

        total_pages = end_page
        print(f"📊 Plan: Scrape pages {start_page} to {end_page} ({end_page - start_page + 1} pages)")
        print(f"📦 Batch size: {self.config['pages_per_batch']} pages per batch")
        print()

        # Initialize counters
        total_entries_scraped = 0
        current_batch = 1
        failed_pages = []

        # Process in batches
        for batch_start in range(start_page, end_page + 1, self.config['pages_per_batch']):
            batch_end = min(batch_start + self.config['pages_per_batch'] - 1, end_page)

            print(f"🔄 Batch {current_batch}: Pages {batch_start}-{batch_end}")
            print("-" * 40)

            batch_entries = []

            # Scrape pages in current batch
            for page_num in range(batch_start, batch_end + 1):
                print(f"  Processing page {page_num}/{total_pages}...")

                entries = self.navigator.get_page_entries(page_num)

                if entries:
                    batch_entries.extend(entries)
                    print(f"    ✓ {len(entries)} entries found")
                else:
                    failed_pages.append(page_num)
                    print(f"    ❌ Failed to get entries")

                # Wait between requests
                if page_num < batch_end:  # Don't wait after last page in batch
                    self.navigator.wait_between_requests()

            # Save batch results
            if batch_entries:
                new_entries_count = self.checkpoint.append_entries(batch_entries)
                total_entries_scraped += new_entries_count
                print(f"  ✓ Batch {current_batch} complete: {len(batch_entries)} entries processed")
            else:
                print(f"  ⚠ Batch {current_batch} yielded no entries")

            # Save progress
            self.checkpoint.save_progress(
                current_page=batch_end,
                total_pages=total_pages,
                entries_scraped=total_entries_scraped,
                last_batch_size=len(batch_entries),
                failed_pages=failed_pages
            )

            print()

            # Wait between batches (except for last batch)
            if batch_end < end_page:
                batch_delay = self.config['delay_between_batches']
                print(f"⏳ Waiting {batch_delay}s before next batch...")
                time.sleep(batch_delay)

            current_batch += 1

        # Final summary
        self._print_summary(total_entries_scraped, failed_pages, start_page, end_page)

    def retry_failed_pages(self) -> None:
        """Retry pages that failed during previous runs"""
        progress = self.checkpoint.load_progress()
        if not progress or not progress.get('failed_pages'):
            print("No failed pages to retry")
            return

        failed_pages = progress['failed_pages']
        print(f"🔄 Retrying {len(failed_pages)} failed pages...")

        retry_entries = []
        still_failed = []

        for page_num in failed_pages:
            print(f"  Retrying page {page_num}...")
            entries = self.navigator.get_page_entries(page_num)

            if entries:
                retry_entries.extend(entries)
                print(f"    ✓ {len(entries)} entries recovered")
            else:
                still_failed.append(page_num)
                print(f"    ❌ Still failing")

            self.navigator.wait_between_requests()

        # Save recovered entries
        if retry_entries:
            new_entries_count = self.checkpoint.append_entries(retry_entries)
            print(f"✓ Recovered {new_entries_count} entries from failed pages")

        # Update progress with remaining failed pages
        if progress:
            self.checkpoint.save_progress(
                current_page=progress['current_page'],
                total_pages=progress['total_pages'],
                entries_scraped=progress['entries_scraped'] + len(retry_entries),
                last_batch_size=len(retry_entries),
                failed_pages=still_failed
            )

        print(f"📊 Retry summary: {len(retry_entries)} recovered, {len(still_failed)} still failing")

    def get_status(self) -> None:
        """Display current scraping status"""
        stats = self.checkpoint.get_stats()

        print("📊 Scraping Status")
        print("=" * 30)
        print(f"Total entries collected: {stats['total_entries']}")

        if stats['last_updated']:
            print(f"Last updated: {stats['last_updated']}")

        if stats['progress']:
            progress = stats['progress']
            print(f"Progress: {progress['completion_percentage']}% "
                  f"(Page {progress['current_page']}/{progress['total_pages']})")
            print(f"Entries scraped: {progress['entries_scraped']}")

            if progress['failed_pages']:
                print(f"Failed pages: {len(progress['failed_pages'])}")

        print(f"Backups available: {'Yes' if stats['has_backups'] else 'No'}")

    def _print_summary(self, total_entries: int, failed_pages: List[int],
                      start_page: int, end_page: int) -> None:
        """Print final scraping summary"""
        print("🎉 Scraping Complete!")
        print("=" * 40)
        print(f"Pages processed: {start_page} to {end_page}")
        print(f"Total entries scraped: {total_entries}")

        if failed_pages:
            print(f"Failed pages: {len(failed_pages)} ({', '.join(map(str, failed_pages))})")
            print("💡 Use --retry-failed to attempt recovery")
        else:
            print("✅ All pages processed successfully!")

        # Show file locations
        print(f"\n📁 Output files:")
        print(f"  📄 Data: {self.config['output_file']}")
        print(f"  📊 Progress: {self.config['progress_file']}")
        print(f"  💾 Backups: {self.config.get('backup_dir', 'backups')}/")

def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(
        description="Batch scraper for Kaggle Nano Banana Hackathon entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_scraper.py --start-page 1 --batch-size 5
  python batch_scraper.py --resume
  python batch_scraper.py --retry-failed
  python batch_scraper.py --status
        """
    )

    parser.add_argument('--start-page', type=int, default=1,
                       help='Starting page number (default: 1)')
    parser.add_argument('--end-page', type=int,
                       help='Ending page number (default: auto-detect)')
    parser.add_argument('--batch-size', type=int,
                       help='Pages per batch (overrides config)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last checkpoint')
    parser.add_argument('--retry-failed', action='store_true',
                       help='Retry failed pages from previous run')
    parser.add_argument('--status', action='store_true',
                       help='Show current scraping status')
    parser.add_argument('--clear-progress', action='store_true',
                       help='Clear progress file (start fresh)')

    args = parser.parse_args()

    # Initialize scraper
    scraper = BatchScraper()

    # Override batch size if specified
    if args.batch_size:
        scraper.config['pages_per_batch'] = args.batch_size

    try:
        if args.status:
            scraper.get_status()
        elif args.retry_failed:
            scraper.retry_failed_pages()
        elif args.clear_progress:
            scraper.checkpoint.clear_progress()
            print("✓ Progress cleared. Ready for fresh start.")
        else:
            scraper.run_batch_scraping(
                start_page=args.start_page,
                end_page=args.end_page,
                resume=args.resume
            )

    except KeyboardInterrupt:
        print("\n⚠ Scraping interrupted by user")
        print("💡 Use --resume to continue from last checkpoint")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()