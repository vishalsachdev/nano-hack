#!/usr/bin/env python3
"""
Final extraction of all hackathon entries from the visible text
"""

import json
import re
from checkpoint_manager import CheckpointManager

def extract_all_entries():
    """Extract all entries from the complete visible text"""

    # Complete visible text from the page
    visible_text = """menu
Skip to
content
Create
search
​
explore
Home
emoji_events
Competitions
table_chart
Datasets
tenancy
Models
leaderboard
Benchmarks
code
Code
comment
Discussions
school
Learn
expand_more
More
auto_awesome_motion
View Active Events
menu
Skip to
content
search
​
Sign In
Register
Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.
Learn more
OK, Got it.
Google DeepMind
·
Community Hackathon
·
5 days ago
Accept Rules
more_horiz
Nano Banana Hackathon
Compete for your share of over $400,000 in prizes
Overview
Data
Code
Discussion
Writeups
Rules
Writeups
grid_view
All
keyboard_arrow_up
All Tracks
Overall Track
Special Technology Prize - ElevenLabs
Special Technology Prize - Fal
check_circle
Submitted
Batchify - An AI Product Shot Generator
Transform your product photos into high-end studio shots at scale
Dana Akerman
check_circle
Submitted
Red Star Realism
Generative AI Propaganda!
Brian Laposa
check_circle
Submitted
AI Comic Creator
Creating comics is traditionally a time-consuming and labor-intensive process, with character consistency
최미나이
check_circle
Submitted
Style Forge
Nano Banana powered virtual try on
crazy gamer1
check_circle
Submitted
WorldDress AI – Instantly experience traditional costumes worldwide
Experience global traditions with a single photo. Pick a country and let our AI transform you in seconds.
MetCaster
check_circle
Submitted
AI Immersive Chatbot (AI Friends)
We built an AI chatbot with consistent image/voice for immersive, lifelike conversation using Gemini 2.5 Flash Image.
인계동 불주먹
check_circle
Submitted
Improved Video Editing Elements  Using Nano Banana
Visual Enhancing with Nano Banana (wifi Project)
Dinu478
check_circle
Submitted
AtelierOne: AI Renaissance Portrait Generator
Transform your webcam photos into Renaissance masterpieces while learning art history through an interactive timeline experience.
Uncle Dao
check_circle
Submitted
AI Recipe Generator
AI Recipe Generator" is a web application that automatically generates recipe instructions and completed dish images based on user-input
Yuji Marutani
check_circle
Submitted
From Awkward Poses to Instagram Worthy – Building My Own AI Photo App
A project where I built an AI-powered app to help people improve their photo poses and backgrounds effortlessly using Google's Nano Banana m
Taru 122
check_circle
Submitted
AI Mockup Pro - R.I.P Figma
An AI design tool that turns wireframes into high-fidelity mockups and code in seconds using Nano Banana.
Feel the Gemini
check_circle
Submitted
PoseUp.ai: Instantly Change Your Pose with Natural Language & AI
An AI photo editor built on Gemini that lets you change a person's entire body pose using simple text commands or one-click templates.
Zifei Gong
check_circle
Submitted
AI Comic Factory
Generate multi-page comics from a simple prompt. Provide character and style references to create your unique story with AI.
bobdobbob
check_circle
Submitted
Celebrity Selfie Generator
Upload your photo and generate a realistic selfie with up to two famous personalities from history and today.
Phiroj Shaikh
check_circle
Submitted
AI Creative Dice – Structured Randomness for Creative Innovation
AI Creative Dice is your pocket-sized idea machine. Just upload then roll the dice and boom, ads concepts land right in front of you.
DigitalKita
check_circle
Submitted
Expression Deck
A card deck of emotions
A4file
check_circle
Submitted
ProcessViz AI: Multi-Style Industrial Process Diagram Generator
Transforming complex industrial processes into CAD-quality diagrams, educational schematics, and photorealistic 3D renders
JERIE
check_circle
Submitted
Who Were You in Ancient Times?
invites users to discover their historical alter egos. After uploading a selfie, the app uses Nano Banana's character-consistency engine to
Dmitrii Motorin
check_circle
Submitted
VisuaLink- Instant Marketing Posters with Gemini
Visualink is a lightweight web app that generates professional-quality marketing posters in seconds.
Masego Khanyisile Monggae
check_circle
Submitted
Revolutionizing Ad Design with AI: Introducing AI-Ad-Creator
An AI powered digital Ad Creator
Anurag Deo
1
2
3
4
5
6
7
8
9
10"""

    entries = []
    lines = visible_text.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for "Submitted" indicators
        if line == "Submitted":
            # Get title (next line after Submitted)
            title = ""
            if i + 1 < len(lines):
                title = lines[i + 1].strip()

            # Get description (line after title)
            description = ""
            if i + 2 < len(lines):
                description = lines[i + 2].strip()

            # Get author (line after description)
            author = ""
            if i + 3 < len(lines):
                potential_author = lines[i + 3].strip()
                # Simple heuristic for author detection
                if (len(potential_author) < 50 and
                    potential_author != "check_circle" and
                    potential_author != "Submitted" and
                    not any(word in potential_author.lower() for word in
                           ['using', 'with', 'the', 'and', 'for', 'in', 'that', 'to', 'is', 'a', 'an'])):
                    author = potential_author

            # Generate URL from title
            url_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
            url_slug = re.sub(r'\s+', '-', url_slug)
            url = f"https://www.kaggle.com/competitions/banana/writeups/{url_slug}"

            if title and title != "Submitted":
                entries.append({
                    'title': title,
                    'subtitle': description[:100] + "..." if len(description) > 100 else description,
                    'description': description,
                    'url': url
                })

        i += 1

    return entries

def main():
    """Extract and save all entries"""
    print("🔄 Final extraction of all hackathon entries...")

    entries = extract_all_entries()

    print(f"✓ Extracted {len(entries)} entries from page")

    # Save to checkpoint manager
    checkpoint = CheckpointManager()
    new_count = checkpoint.append_entries(entries)

    print(f"✓ Added {new_count} new unique entries to dataset")

    # Print sample entries
    print(f"\n📋 Sample entries:")
    for i, entry in enumerate(entries[:5]):
        print(f"{i+1}. {entry['title']}")
        print(f"   {entry['subtitle']}")
        print(f"   {entry['url']}")
        print()

if __name__ == "__main__":
    main()