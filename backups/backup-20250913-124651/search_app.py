import json
import streamlit as st
from typing import List, Dict

def load_entries() -> List[Dict]:
    """Load entries from JSON file"""
    try:
        with open('hackathon_entries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("No data found. Run scraper.py first!")
        return []

def search_entries(entries: List[Dict], query: str) -> List[Dict]:
    """Filter entries based on search query"""
    if not query:
        return entries

    query_lower = query.lower()
    filtered = [
        e for e in entries
        if query_lower in e['title'].lower() or
           query_lower in e['description'].lower() or
           query_lower in e.get('subtitle', '').lower()
    ]

    return filtered

def main():
    st.title("🍌 Nano Banana Hackathon Explorer")
    st.markdown("Search and explore hackathon entries")
    
    # Load data
    entries = load_entries()
    if not entries:
        return
    
    # Sidebar search
    st.sidebar.header("Search")

    # Search input
    search_query = st.sidebar.text_input("Search entries:", placeholder="Enter keywords...")

    # Filter entries
    filtered_entries = search_entries(entries, search_query)
    
    # Display results
    st.subheader(f"Found {len(filtered_entries)} entries")
    
    for entry in filtered_entries:
        with st.expander(f"📌 {entry['title']}"):
            if entry.get('subtitle'):
                st.write(f"**Subtitle:** {entry['subtitle']}")
            st.write(f"**Description:** {entry['description']}")
            if entry.get('url'):
                st.markdown(f"**🔗 [View Entry]({entry['url']})**")

if __name__ == "__main__":
    main()