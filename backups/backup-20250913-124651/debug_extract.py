#!/usr/bin/env python3
"""
Debug script to understand the text structure
"""

def debug_extraction():
    # Sample from the visible text
    text_sample = """check_circle
Submitted
Batchify - An AI Product Shot Generator
Transform your product photos into high-end studio shots at scale
Dana Akerman
check_circle
Submitted
Red Star Realism
Generative AI Propaganda!
Brian Laposa"""

    print("🔍 Debugging text extraction...")
    lines = text_sample.strip().split('\n')

    print(f"Total lines: {len(lines)}")
    for i, line in enumerate(lines):
        print(f"{i}: '{line.strip()}'")

    print("\n🔍 Looking for 'Submitted' patterns...")
    entries = []

    for i, line in enumerate(lines):
        line = line.strip()
        if line == "Submitted":
            print(f"Found 'Submitted' at line {i}")

            # Title should be next line
            if i + 1 < len(lines):
                title = lines[i + 1].strip()
                print(f"  Title: '{title}'")

                # Description should be line after that
                if i + 2 < len(lines):
                    description = lines[i + 2].strip()
                    print(f"  Description: '{description}'")

                    # Author should be line after that
                    if i + 3 < len(lines):
                        author = lines[i + 3].strip()
                        print(f"  Author: '{author}'")

                        entries.append({
                            'title': title,
                            'description': description,
                            'author': author
                        })

    print(f"\n✓ Extracted {len(entries)} entries:")
    for entry in entries:
        print(f"- {entry['title']}")

if __name__ == "__main__":
    debug_extraction()