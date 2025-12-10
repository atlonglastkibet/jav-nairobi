"""
Jav-Nairobi: AI-Powered Transit Equity Optimization
Main Streamlit Application Entry Point
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
from pathlib import Path
from utils.styling import get_custom_css
from utils.data_loader import prepare_routes_with_paths, get_app_metrics, CBD_LAT, CBD_LON

# Get the absolute path to the streamlit_app directory
STREAMLIT_APP_ROOT = Path(__file__).parent.absolute()

# Page config
st.set_page_config(
    page_title="",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Jav - AI-Powered Transit Equity Optimization for Nairobi"
    }
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Custom CSS for seamless layout
st.markdown("""
<style>
    .main-title {
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.2;
    }
    /* Force center the logo by targeting Streamlit's container */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    div[data-testid="stImage"] img {
        max-width: 500px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_path_data():
    return prepare_routes_with_paths()

routes_path_df = load_path_data()
metrics = get_app_metrics()

# Logo (centered using columns)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_path = STREAMLIT_APP_ROOT / "assets" / "jav-nairobi.png"
    st.image(str(logo_path))

# Title (spanning full width)
st.markdown('<h1 class="main-title">AI-Powered Transit Equity Optimization for Nairobi</h1>', unsafe_allow_html=True)

# Map - seamless, no breaks
path_layer = pdk.Layer(
    'PathLayer',
    data=routes_path_df,
    get_path='path',
    get_color='color_with_alpha',
    get_width='width',
    width_min_pixels=2,
    pickable=True,
    auto_highlight=True
)

path_view_state = pdk.ViewState(
    latitude=CBD_LAT,
    longitude=CBD_LON,
    zoom=11,
    pitch=45,
    bearing=0
)

path_deck = pdk.Deck(
    layers=[path_layer],
    initial_view_state=path_view_state,
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    tooltip={
        'html': '<b>Route:</b> {route_id}<br/><b>Name:</b> {route_name}<br/><b>Has Variants:</b> {has_variants}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.9)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '10px'
        }
    }
)

st.pydeck_chart(path_deck, use_container_width=True, height=600)

# Metrics panel overlay (using custom HTML)
st.markdown(f"""
<div class="metrics-container">
    <div class="metric-item">
        <div class="metric-number">{metrics['routes']}</div>
        <div class="metric-label">Routes</div>
        <div class="metric-subtext">{metrics['routes_subtext']}</div>
    </div>
    <div class="metric-item">
        <div class="metric-number">{metrics['stops']}</div>
        <div class="metric-label">Stops</div>
        <div class="metric-subtext">{metrics['stops_subtext']}</div>
    </div>
    <div class="metric-item">
        <div class="metric-number">{metrics['underserved']}</div>
        <div class="metric-label">Impact</div>
        <div class="metric-subtext">{metrics['underserved_subtext']}</div>
    </div>
    <div class="metric-item">
        <div class="metric-number">{metrics['wards']}</div>
        <div class="metric-label">Wards</div>
        <div class="metric-subtext">{metrics['wards_subtext']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Legend
st.markdown("""
<div class="legend-container">
    <div class="legend-title">Route Equity Tier</div>
    <div class="legend-item">
        <div class="legend-color" style="background: rgb(231, 76, 60);"></div>
        <span>Severely Underserved</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: rgb(230, 126, 34);"></div>
        <span>Underserved</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: rgb(241, 196, 15);"></div>
        <span>Adequate</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: rgb(70, 204, 113);"></div>
        <span>Well Served</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Info section below map
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### About the Visualization

    This map shows Nairobi's matatu route network radiating from the CBD (blue center point).
    Routes are color-coded by equity tier, with **red** indicating severely underserved areas
    and **green** indicating well-served areas.

    Our GNN model identified **12 new route recommendations** to improve equity and serve
    an additional **1.8M residents** in underserved areas.
    """)

with col2:
    st.markdown("""
    ### Key Insights

    - **135+ routes** currently serve Nairobi's matatu network
    - **88 wards** analyzed for transit equity
    - **3,950 candidate stops** evaluated using Graph Neural Networks
    - **94% accuracy** in identifying optimal stop locations
    - **Gini coefficient improvement**: 0.72 → 0.61 (more equitable)
    """)

st.markdown("---")
st.markdown("*Built for Nairobi*")
