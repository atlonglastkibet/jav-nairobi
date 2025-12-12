"""
Community Notes page - Crowdsourced feedback on matatu services and infrastructure.
Users can submit and view community observations about transit quality.
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import base64
from pathlib import Path
from datetime import datetime
import random

# Add paths for imports
STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()

import sys
sys.path.insert(0, str(STREAMLIT_APP_ROOT))
from utils.styling import get_custom_css
from utils.data_loader import CBD_LAT, CBD_LON, load_gtfs_feed

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Page config
st.set_page_config(
    page_title="Community Notes",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional CSS
st.markdown("""
<style>
    .community-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .community-logo {
        width: 48px;
        height: 48px;
        object-fit: contain;
    }

    .community-title {
        font-size: 24px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }

    .note-card {
        background: rgba(30, 33, 40, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
        margin: 12px 0;
        border-radius: 12px;
        transition: transform 0.2s;
    }

    .note-card:hover {
        background: rgba(30, 33, 40, 0.6);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .note-card.Issue {
        background: #ffffff;
        color: #000000;
    }
    
    .note-card.Issue .note-title,
    .note-card.Issue .note-desc,
    .note-card.Issue .note-meta {
        color: #000000;
    }

    .note-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }

    .note-type-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-Issue {
        background: rgba(231, 76, 60, 0.15);
        color: rgb(231, 76, 60);
    }
    
    .note-card.Issue .badge-Issue {
        background: rgba(231, 76, 60, 0.1);
        color: rgb(231, 76, 60);
    }

    .badge-Suggestion {
        background: rgba(241, 196, 15, 0.15);
        color: rgb(241, 196, 15);
    }

    .badge-Comment {
        background: rgba(26, 115, 232, 0.15);
        color: rgb(26, 115, 232);
    }

    .note-title {
        font-size: 16px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0 0 4px 0;
    }

    .note-desc {
        font-size: 14px;
        color: #b0b0b0;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    .note-meta {
        font-size: 12px;
        color: #666;
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
    }

    .stat-box {
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #e0e0e0;
    }

    .stat-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    
    /* Content Section Styling from App.py */
    .content-section {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #E74C3C;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    .section-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Load routes for dropdown
@st.cache_data
def get_route_options():
    feed = load_gtfs_feed()
    routes = feed.routes[['route_id', 'route_long_name']].drop_duplicates()
    return routes.apply(lambda x: f"{x['route_id']} - {x['route_long_name']}", axis=1).tolist()

route_options = get_route_options()

# Header
logo_path = STREAMLIT_APP_ROOT / "assets" / "Community_Notes_logo.png"
if logo_path.exists():
    logo_img = f'<img src="data:image/png;base64,{get_image_base64(logo_path)}" class="community-logo"/>'
else:
    logo_img = '📍'

st.markdown(f"""
<div class="community-header">
    {logo_img}
    <h1 class="community-title">Community Notes</h1>
</div>
""", unsafe_allow_html=True)

# Load or initialize community notes data
NOTES_FILE = STREAMLIT_APP_ROOT / "data" / "community_notes.json"

def load_notes():
    """Load community notes from JSON file."""
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default diverse seed data (English, Swahili, Sheng)
        return [
            {
                "id": 1,
                "lat": -1.2921,
                "lon": 36.8219,
                "type": "Issue",
                "level": "Stop Level",
                "title": "No shelter at CBD stop",
                "description": "Matatu stop lacks shelter. Passengers get soaked during rain. Tunanyeshewa hapa mbaya.",
                "ward": "Nairobi Central",
                "route": "46 - Kawangware",
                "author": "Mama Boi",
                "date": "2025-01-15",
                "upvotes": 12
            },
            {
                "id": 2,
                "lat": -1.2634,
                "lon": 36.8071,
                "type": "Suggestion",
                "level": "Route Level",
                "title": "Extend Route 46 to Githurai",
                "description": "Wasee wa Githurai wanateseka. Extending Route 46 would help many residents who currently walk 20+ minutes.",
                "ward": "Githurai Ward",
                "route": "46 - Kawangware",
                "author": "John Kamau",
                "date": "2025-01-14",
                "upvotes": 28
            },
            {
                "id": 3,
                "lat": -1.3032,
                "lon": 36.7073,
                "type": "Comment",
                "level": "Stop Level",
                "title": "New stop helps a lot",
                "description": "Hii stop mpya imesaidia sana. The new stop on Ngong Road has significantly reduced my commute time.",
                "ward": "Kilimani Ward",
                "route": "111 - Ngong",
                "author": "Daily Commuter",
                "date": "2025-01-13",
                "upvotes": 45
            },
            {
                "id": 4,
                "lat": -1.2529,
                "lon": 36.8912,
                "type": "Issue",
                "level": "Stop Level",
                "title": "Dangerous road crossing",
                "description": "Kuvuka hapa ni noma. Stop requires crossing 4-lane highway with no pedestrian crossing.",
                "ward": "Dandora Area III Ward",
                "route": "32 - Dandora",
                "author": "Safety Advocate",
                "date": "2025-01-12",
                "upvotes": 34
            },
            {
                "id": 5,
                "lat": -1.3154,
                "lon": 36.7426,
                "type": "Suggestion",
                "level": "Route Level",
                "title": "More evening service needed",
                "description": "Matatu za usiku ni shida. After 8 PM, matatus become very infrequent. Need more evening routes.",
                "ward": "Kawangware Ward",
                "route": "2 - Kawangware",
                "author": "Night Shift Worker",
                "date": "2025-01-11",
                "upvotes": 19
            },
            {
                "id": 6,
                "lat": -1.2446,
                "lon": 36.8897,
                "type": "Issue",
                "level": "Route Level",
                "title": "Overcrowding at peak hours",
                "description": "Matatu zinajaa sana asubuhi. Morning rush hour sees severe overcrowding. Need additional matatus.",
                "ward": "Ruaraka Ward",
                "route": "44 - Kahawa West",
                "author": "Morning Commuter",
                "date": "2025-01-10",
                "upvotes": 52
            },
            {
                "id": 7,
                "lat": -1.2841,
                "lon": 36.8155,
                "type": "Comment",
                "level": "Route Level",
                "title": "Clean buses on this route",
                "description": "Nganya za hii route ni safi. The new fleet on this route is very clean and comfortable.",
                "ward": "Nairobi Central",
                "route": "34 - Langata",
                "author": "Happy Traveler",
                "date": "2025-01-09",
                "upvotes": 15
            },
            {
                "id": 8,
                "lat": -1.3000,
                "lon": 36.7800,
                "type": "Suggestion",
                "level": "Route Level",
                "title": "Add digital payment",
                "description": "Tunataka kulipa na M-PESA. It would be great if we could pay via M-PESA directly.",
                "ward": "Kilimani Ward",
                "route": "4W - Kibera",
                "author": "Tech User",
                "date": "2025-01-08",
                "upvotes": 30
            },
            {
                "id": 9,
                "lat": -1.2700,
                "lon": 36.8500,
                "type": "Issue",
                "level": "Stop Level",
                "title": "Potholes at terminal",
                "description": "Barabara imeharibika. The terminal entrance has huge potholes causing delays.",
                "ward": "Eastleigh North",
                "route": "6 - Eastleigh",
                "author": "Driver John",
                "date": "2025-01-07",
                "upvotes": 22
            },
            {
                "id": 10,
                "lat": -1.2900,
                "lon": 36.8000,
                "type": "Suggestion",
                "level": "Stop Level",
                "title": "Add stop closer to hospital",
                "description": "Tafadhali weka stage karibu na hospitali. Patients have to walk too far.",
                "ward": "Upper Hill",
                "route": "7C - Kenyatta",
                "author": "Nurse Mary",
                "date": "2025-01-06",
                "upvotes": 40
            },
            {
                "id": 11,
                "lat": -1.3200,
                "lon": 36.8500,
                "type": "Comment",
                "level": "Route Level",
                "title": "Best music playlist",
                "description": "Ngoma za hii route ni moto! Best music selection in Nairobi.",
                "ward": "South B",
                "route": "11 - South B",
                "author": "Youth Leader",
                "date": "2025-01-05",
                "upvotes": 60
            }
        ]

def save_notes(notes):
    """Save community notes to JSON file."""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

# Load notes
notes = load_notes()

# Initialize session state for detected location
if 'detected_lat' not in st.session_state:
    st.session_state.detected_lat = -1.2921
if 'detected_lon' not in st.session_state:
    st.session_state.detected_lon = 36.8219

# Sidebar for adding new notes
with st.sidebar:
    st.markdown("### Submit a Note")

    # Feedback Level (Outside form for interactivity)
    feedback_level = st.radio(
        "Feedback Level",
        ["Stop Level", "Route Level"],
        help="Choose 'Stop Level' for specific locations or 'Route Level' for general route feedback."
    )

    with st.form("new_note_form"):
        note_type = st.selectbox(
            "Type",
            ["Issue", "Suggestion", "Comment"]
        )

        # Route Selector - Only for Route Level
        route = None
        if feedback_level == "Route Level":
            route = st.selectbox(
                "Route",
                route_options,
                index=0
            )

        title = st.text_input("Title", placeholder="Brief summary (e.g., 'Add stop here')")

        description = st.text_area(
            "Description",
            placeholder="Share your observation (English, Swahili, or Sheng)...",
            height=100
        )

        # Location inputs - Shown for BOTH levels now
        st.markdown("#### Location")
        
        # Detect Location Button (Inside form as requested)
        detect_loc = st.form_submit_button("📍 Detect My Location")
        if detect_loc:
            # Simulation of location detection
            st.session_state.detected_lat = -1.2921 + (random.random() - 0.5) * 0.01
            st.session_state.detected_lon = 36.8219 + (random.random() - 0.5) * 0.01
            st.success(f"Detected: {st.session_state.detected_lat:.4f}, {st.session_state.detected_lon:.4f}")
            # We need to rerun to update the number_inputs below with new session state values
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=st.session_state.detected_lat, format="%.6f")
        with col2:
            lon = st.number_input("Longitude", value=st.session_state.detected_lon, format="%.6f")
        
        st.caption("Coordinates auto-filled from detection or manually editable.")

        author = st.text_input("Your Name (optional)", placeholder="Anonymous")

        submit = st.form_submit_button("Post Note")

        if submit:
            if title and description:
                new_note = {
                    "id": max([n["id"] for n in notes]) + 1 if notes else 1,
                    "lat": lat,
                    "lon": lon,
                    "type": note_type,
                    "level": feedback_level,
                    "title": title,
                    "description": description,
                    "ward": "Auto-detected Ward", # Placeholder
                    "route": route if route else "General / Unknown",
                    "author": author or "Anonymous",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "upvotes": 0
                }
                notes.append(new_note)
                save_notes(notes)
                st.success("Note posted successfully")
                st.rerun()
            else:
                st.error("Please fill in title and description")

# HOW IT WORKS Section
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        Community Notes empowers Nairobi's commuters to directly influence the transit network. By crowdsourcing real-time observations, we create a living map of the city's mobility needs. Users can report <strong>Issues</strong> like safety hazards or infrastructure gaps, offer <strong>Suggestions</strong> for new routes or stops, and leave <strong>Comments</strong> on service quality. Each note is tagged with a specific route and location, allowing our AI models to incorporate this qualitative feedback into equity analysis and route optimization. This ensures that planning decisions are not just data-driven, but people-driven.
    </div>
</div>
""", unsafe_allow_html=True)

# Stats row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(notes)}</div>
        <div class="stat-label">Total Notes</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    issue_count = len([n for n in notes if n["type"] == "Issue"])
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number" style="color: rgb(231, 76, 60);">{issue_count}</div>
        <div class="stat-label">Issues</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    suggestion_count = len([n for n in notes if n["type"] == "Suggestion"])
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number" style="color: rgb(241, 196, 15);">{suggestion_count}</div>
        <div class="stat-label">Suggestions</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    comment_count = len([n for n in notes if n["type"] == "Comment"])
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number" style="color: rgb(26, 115, 232);">{comment_count}</div>
        <div class="stat-label">Comments</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Filter controls
col1, col2 = st.columns([1, 3])

with col1:
    filter_type = st.multiselect(
        "Filter by Type:",
        ["Issue", "Suggestion", "Comment"],
        default=["Issue", "Suggestion", "Comment"]
    )

with col2:
    search_query = st.text_input("Search notes:", placeholder="Search by title, route, or content...")

# Filter notes
filtered_notes = [n for n in notes if n["type"] in filter_type]

if search_query:
    search_lower = search_query.lower()
    filtered_notes = [
        n for n in filtered_notes
        if search_lower in n["title"].lower()
        or search_lower in n["description"].lower()
        or search_lower in n.get("route", "").lower()
        or search_lower in n["ward"].lower()
    ]

# Prepare data for PyDeck - Only include notes with valid coordinates
map_notes = [n for n in filtered_notes if n.get("lat") is not None and n.get("lon") is not None]
notes_df = pd.DataFrame(map_notes)

if len(notes_df) > 0:
    # Add color based on type
    def get_color(note_type):
        colors = {
            "Issue": [231, 76, 60, 200],      # Red
            "Suggestion": [241, 196, 15, 200], # Yellow
            "Comment": [26, 115, 232, 200]      # Blue
        }
        return colors.get(note_type, [100, 100, 100, 200])

    notes_df["color"] = notes_df["type"].apply(get_color)
    notes_df["size"] = notes_df["upvotes"].apply(lambda x: max(50, min(x * 10, 500)))

    # Create PyDeck layer
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=notes_df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius='size',
        radius_scale=1,
        radius_min_pixels=6,
        radius_max_pixels=20,
        pickable=True,
        auto_highlight=True,
        opacity=0.8
    )

    # View state
    view_state = pdk.ViewState(
        latitude=CBD_LAT,
        longitude=CBD_LON,
        zoom=11,
        pitch=0,
        bearing=0,
        min_zoom=9,
        max_zoom=15
    )

    # Create deck
    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        tooltip={
            'html': '<b>{title}</b><br/>{description}<br/><br/><small>📍 {ward}<br/>🚌 {route}<br/>👤 {author}<br/>📅 {date}</small>',
            'style': {
                'backgroundColor': 'rgba(14, 17, 23, 0.95)',
                'color': 'white',
                'borderRadius': '8px',
                'padding': '12px',
                'maxWidth': '300px'
            }
        }
    )

    st.pydeck_chart(deck, use_container_width=True, height=500)

    # List view below map
    st.markdown(f"### {len(filtered_notes)} Notes Found")

    # Sort by upvotes
    sorted_notes = sorted(filtered_notes, key=lambda x: x["upvotes"], reverse=True)

    for note in sorted_notes:
        level_badge = f'<span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-right: 8px;">{note.get("level", "Stop Level")}</span>'
        
        st.markdown(f"""
        <div class="note-card {note['type']}">
            <div class="note-header">
                <div style="display: flex; align-items: center;">
                    {level_badge}
                    <div class="note-type-badge badge-{note['type']}">{note['type']}</div>
                </div>
                <div style="font-size: 12px; color: #888;">{note['date']}</div>
            </div>
            <h3 class="note-title">{note['title']}</h3>
            <div class="note-desc">{note['description']}</div>
            <div class="note-meta">
                <span>📍 {note['ward']}</span>
                <span>•</span>
                <span>🚌 {note.get('route', 'General')}</span>
                <span>•</span>
                <span>👤 {note['author']}</span>
                <span style="margin-left: auto;">👍 {note['upvotes']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("No notes match your filters.")

# Footer
st.markdown("""
<div class="app-footer">
    <div class="footer-text">
        <strong>JAV-NAIROBI</strong> © 2025<br/>
        Built by <strong>David Kibet</strong><br/>
        <a href="mailto:atlonglastkibet@gmail.com">Email</a> |
        <a href="https://github.com/atlonglastkibet/jav-nairobi" target="_blank">Project Link</a>
    </div>
</div>
""", unsafe_allow_html=True)
