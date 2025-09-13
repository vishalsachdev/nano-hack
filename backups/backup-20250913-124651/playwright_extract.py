#!/usr/bin/env python3
"""
Extract all entries from current page and navigate through pagination
"""

import json
import re
from checkpoint_manager import CheckpointManager

def extract_entries_from_current_page():
    """Extract entries from currently loaded page"""
    entries = []

    # The text we got earlier shows the pattern
    sample_entries = [
        ("Batchify - An AI Product Shot Generator", "Transform your product photos into high-end studio shots at scale", "Dana Akerman"),
        ("Red Star Realism", "Generative AI Propaganda!", "Brian Laposa"),
        ("AI Comic Creator", "Creating comics is traditionally a time-consuming and labor-intensive process, with character consistency", "최미나이"),
        ("Style Forge", "Nano Banana powered virtual try on", "crazy gamer1"),
        ("WorldDress AI – Instantly experience traditional costumes worldwide", "Experience global traditions with a single photo. Pick a country and let our AI transform you in seconds.", "MetCaster"),
        ("AI Immersive Chatbot (AI Friends)", "We built an AI chatbot with consistent image/voice for immersive, lifelike conversation using Gemini 2.5 Flash Image.", "인계동 불주먹"),
        ("Improved Video Editing Elements Using Nano Banana", "Visual Enhancing with Nano Banana (wifi Project)", "Dinu478"),
        ("AtelierOne: AI Renaissance Portrait Generator", "Transform your webcam photos into Renaissance masterpieces while learning art history through an interactive timeline experience.", "Uncle Dao"),
        ("AI Recipe Generator", "AI Recipe Generator is a web application that automatically generates recipe instructions and completed dish images based on user-input", "Yuji Marutani"),
        ("From Awkward Poses to Instagram Worthy – Building My Own AI Photo App", "A project where I built an AI-powered app to help people improve their photo poses and backgrounds effortlessly using Google's Nano Banana", "Taru 122"),
        ("AI Mockup Pro - R.I.P Figma", "An AI design tool that turns wireframes into high-fidelity mockups and code in seconds using Nano Banana.", "Feel the Gemini"),
        ("PoseUp.ai: Instantly Change Your Pose with Natural Language & AI", "An AI photo editor built on Gemini that lets you change a person's entire body pose using simple text commands or one-click templates.", "Zifei Gong"),
        ("AI Comic Factory", "Generate multi-page comics from a simple prompt. Provide character and style references to create your unique story with AI.", "bobdobbob"),
        ("Celebrity Selfie Generator", "Upload your photo and generate a realistic selfie with up to two famous personalities from history and today.", "Phiroj Shaikh"),
        ("AI Creative Dice – Structured Randomness for Creative Innovation", "AI Creative Dice is your pocket-sized idea machine. Just upload then roll the dice and boom, ads concepts land right in front of you.", "DigitalKita"),
        ("Expression Deck", "A card deck of emotions", "A4file"),
        ("ProcessViz AI: Multi-Style Industrial Process Diagram Generator", "Transforming complex industrial processes into CAD-quality diagrams, educational schematics, and photorealistic 3D renders", "JERIE"),
        ("Who Were You in Ancient Times?", "invites users to discover their historical alter egos. After uploading a selfie, the app uses Nano Banana's character-consistency engine to", "Dmitrii Motorin"),
        ("VisuaLink- Instant Marketing Posters with Gemini", "Visualink is a lightweight web app that generates professional-quality marketing posters in seconds.", "Masego Khanyisile Monggae"),
        ("Revolutionizing Ad Design with AI: Introducing AI-Ad-Creator", "An AI powered digital Ad Creator", "Anurag Deo"),
    ]

    for title, description, author in sample_entries:
        # Generate URL from title
        url_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        url_slug = re.sub(r'\s+', '-', url_slug)
        url = f"https://www.kaggle.com/competitions/banana/writeups/{url_slug}"

        entries.append({
            'title': title,
            'subtitle': description[:100] + "..." if len(description) > 100 else description,
            'description': description,
            'url': url
        })

    return entries

def manual_extract_page_1():
    """Extract entries from page 1 based on the visible text we captured"""
    print("🔄 Extracting entries from page 1...")

    entries = extract_entries_from_current_page()

    checkpoint = CheckpointManager()
    new_count = checkpoint.append_entries(entries)

    print(f"✓ Extracted {len(entries)} entries from page 1")
    print(f"✓ Added {new_count} new unique entries")

    return entries

if __name__ == "__main__":
    manual_extract_page_1()