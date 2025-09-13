# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Nano Banana Hackathon Entry Analyzer** that scrapes competition entries from Kaggle and provides a searchable web interface. The system extracts structured data (title, subtitle, description, URL) from individual Kaggle writeup pages and presents them through a Streamlit-based search interface.

## Core Architecture

The application follows a simple two-component architecture:

### Data Pipeline (`scraper.py`)
- **Current State**: Contains hardcoded data extracted from 10 Kaggle competition entries
- **Data Structure**: Each entry has `title`, `subtitle`, `description`, `url` fields only
- **Output**: Generates `hackathon_entries.json` with structured data
- **Scaling Ready**: Designed to be extended with browser automation for mass extraction

### Web Interface (`search_app.py`)
- **Framework**: Streamlit-based search and browsing interface
- **Functionality**: Full-text search across title, subtitle, and description fields
- **Data Source**: Reads from `hackathon_entries.json`
- **UI**: Expandable cards with direct links to original Kaggle entries

## Development Commands

```bash
# Setup virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate/update data
python scraper.py

# Launch web interface
streamlit run search_app.py
```

## Data Model

```json
{
  "title": "Project Name",
  "subtitle": "One-line description/tagline",
  "description": "Full detailed description of the project and its capabilities",
  "url": "https://www.kaggle.com/competitions/banana/writeups/project-slug"
}
```

## Scaling Approach

The current implementation uses hardcoded data from 10 entries as a proof-of-concept. The architecture supports scaling through:

1. **Browser Automation**: Use Playwright/Selenium to navigate Kaggle pages programmatically
2. **Pagination Handling**: Navigate through multiple pages of competition entries
3. **Content Extraction**: Parse individual writeup pages to extract title, subtitle, and detailed descriptions
4. **Batch Processing**: Process hundreds of entries systematically while maintaining data quality

## Source Data

- **Target Site**: https://www.kaggle.com/competitions/banana/writeups
- **Entry Format**: Individual competition writeup pages with structured content
- **Current Dataset**: 10 manually extracted entries from the Nano Banana Hackathon
- **Potential Scale**: 800+ entries discovered across 40+ pages of the competition

## Key Implementation Notes

- **No Authentication Required**: Scraping uses public Kaggle writeup pages
- **Clean Data Structure**: Removed author, video_url, categories fields for simplicity
- **Real URLs**: All entries link back to actual Kaggle competition pages
- **Search Optimization**: Full-text search across all text fields for comprehensive discovery