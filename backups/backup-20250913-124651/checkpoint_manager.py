"""Checkpoint manager for tracking scraping progress"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

class CheckpointManager:
    """Manages progress checkpoints and data persistence"""

    def __init__(self, progress_file: str = 'progress.json', output_file: str = 'hackathon_entries.json'):
        self.progress_file = progress_file
        self.output_file = output_file
        self.backup_dir = 'backups'

        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_progress(self, current_page: int, total_pages: int,
                     entries_scraped: int, last_batch_size: int,
                     failed_pages: List[int] = None) -> None:
        """Save current scraping progress"""
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'current_page': current_page,
            'total_pages': total_pages,
            'entries_scraped': entries_scraped,
            'last_batch_size': last_batch_size,
            'failed_pages': failed_pages or [],
            'completion_percentage': round((current_page / total_pages) * 100, 2)
        }

        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)

        print(f"✓ Progress saved: Page {current_page}/{total_pages} ({progress_data['completion_percentage']}%)")

    def load_progress(self) -> Optional[Dict[str, Any]]:
        """Load existing progress data"""
        if not os.path.exists(self.progress_file):
            return None

        try:
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)

            print(f"✓ Loaded progress: Page {progress['current_page']}/{progress['total_pages']} "
                  f"({progress['completion_percentage']}%)")
            return progress
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠ Warning: Could not load progress file: {e}")
            return None

    def save_entries(self, entries: List[Dict[str, Any]], create_backup: bool = True) -> None:
        """Save entries to output file with optional backup"""

        # Create backup if output file exists
        if create_backup and os.path.exists(self.output_file):
            self._create_backup()

        # Save entries
        with open(self.output_file, 'w') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(entries)} entries to {self.output_file}")

    def load_entries(self) -> List[Dict[str, Any]]:
        """Load existing entries from output file"""
        if not os.path.exists(self.output_file):
            return []

        try:
            with open(self.output_file, 'r') as f:
                entries = json.load(f)

            print(f"✓ Loaded {len(entries)} existing entries")
            return entries
        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠ Warning: Could not load existing entries file")
            return []

    def append_entries(self, new_entries: List[Dict[str, Any]]) -> int:
        """Append new entries to existing data"""
        existing_entries = self.load_entries()

        # Deduplicate based on URL
        existing_urls = {entry.get('url') for entry in existing_entries}
        unique_new_entries = [
            entry for entry in new_entries
            if entry.get('url') not in existing_urls
        ]

        if unique_new_entries:
            all_entries = existing_entries + unique_new_entries
            self.save_entries(all_entries, create_backup=True)
            print(f"✓ Added {len(unique_new_entries)} new entries (skipped {len(new_entries) - len(unique_new_entries)} duplicates)")
        else:
            print("No new unique entries to add")

        return len(unique_new_entries)

    def _create_backup(self) -> None:
        """Create timestamped backup of current data"""
        if not os.path.exists(self.output_file):
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"hackathon_entries_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        shutil.copy2(self.output_file, backup_path)
        print(f"✓ Created backup: {backup_path}")

    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Keep only the most recent backups"""
        if not os.path.exists(self.backup_dir):
            return

        backup_files = [
            f for f in os.listdir(self.backup_dir)
            if f.startswith('hackathon_entries_backup_') and f.endswith('.json')
        ]

        if len(backup_files) <= keep_count:
            return

        # Sort by modification time, newest first
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)

        # Remove old backups
        for old_backup in backup_files[keep_count:]:
            old_path = os.path.join(self.backup_dir, old_backup)
            os.remove(old_path)
            print(f"✓ Removed old backup: {old_backup}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        entries = self.load_entries()
        progress = self.load_progress()

        return {
            'total_entries': len(entries),
            'last_updated': datetime.fromtimestamp(os.path.getmtime(self.output_file)).isoformat() if os.path.exists(self.output_file) else None,
            'progress': progress,
            'has_backups': len([f for f in os.listdir(self.backup_dir) if f.endswith('.json')]) > 0 if os.path.exists(self.backup_dir) else False
        }

    def clear_progress(self) -> None:
        """Clear progress file - useful for starting fresh"""
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
            print("✓ Progress file cleared")