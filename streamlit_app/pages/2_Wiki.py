"""
About page with project information, methodology, and impact.
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
from pathlib import Path
from utils.styling import get_custom_css
from utils.data_loader import prepare_routes_for_animation, CBD_LAT, CBD_LON

# Get the absolute path to the streamlit_app directory
STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()

# Page config
st.set_page_config(
    page_title="Wiki",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

st.title("Wiki")

# Load arc data
@st.cache_data
def load_arc_data():
    return prepare_routes_for_animation()

routes_arc_df = load_arc_data()

# Arc View Section
st.markdown("## Network Visualization: Arc View")
st.markdown("**Routes radiating from CBD** - This conceptual view shows all routes emanating from Nairobi's Central Business District, color-coded by equity tier.")

# Prepare arc layer data
arc_data = routes_arc_df[['source_lat', 'source_lon', 'target_lat', 'target_lon', 'color', 'route_id', 'route_name']].copy()

# Create the pydeck arc layer
arc_layer = pdk.Layer(
    'ArcLayer',
    data=arc_data,
    get_source_position=['source_lon', 'source_lat'],
    get_target_position=['target_lon', 'target_lat'],
    get_source_color=[26, 115, 232],  # Blue for CBD
    get_target_color='color',
    get_width=3,
    get_height=0.3,
    pickable=True,
    auto_highlight=True
)

# Create scatter layer for CBD center
cbd_layer = pdk.Layer(
    'ScatterplotLayer',
    data=pd.DataFrame([{'lat': CBD_LAT, 'lon': CBD_LON}]),
    get_position=['lon', 'lat'],
    get_color=[26, 115, 232, 200],
    get_radius=500,
    pickable=False
)

# Set view state for arc view
arc_view_state = pdk.ViewState(
    latitude=CBD_LAT,
    longitude=CBD_LON,
    zoom=11,
    pitch=50,
    bearing=0
)

# Create arc deck
arc_deck = pdk.Deck(
    layers=[arc_layer, cbd_layer],
    initial_view_state=arc_view_state,
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    tooltip={
        'html': '<b>Route:</b> {route_id}<br/><b>Name:</b> {route_name}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.9)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '10px'
        }
    }
)

# Display arc map
st.pydeck_chart(arc_deck, use_container_width=True, height=600)

# Legend for arc view
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

st.markdown("---")

# Project Overview
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## Project Overview")
st.markdown("""
**Jav-Nairobi** is an AI-powered transit equity optimization system that uses
Graph Neural Networks (GNNs) to recommend optimal matatu bus stop placements
in Nairobi, Kenya.

The system analyzes spatial, temporal, and demographic data to identify underserved
areas and recommend new route extensions that maximize equity and accessibility.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Model Accuracy", "94%", "GNN stop prediction")
with col2:
    st.metric("Population Impact", "1.8M", "New residents served")
with col3:
    st.metric("Equity Improvement", "15%", "Gini coefficient reduction")

st.markdown('</div>', unsafe_allow_html=True)

# The Problem
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## The Problem")
st.markdown("""
Nairobi's matatu network, while extensive, suffers from significant equity challenges:

- **1.8M residents** in underserved areas lack adequate transit access
- **Informal system**: Routes are determined by private operators, not equity
- **Geographic disparity**: Wealthy areas have better service than low-income neighborhoods
- **Limited data**: Traditional planning lacks granular mobility and demographic insights

**Current Gini coefficient: 0.72** (higher = more inequitable)

### Key Challenges:
1. **Spatial inequality**: Poor connectivity in informal settlements
2. **Temporal gaps**: Limited service during off-peak hours
3. **Data scarcity**: Lack of comprehensive transit planning data
4. **Informal operations**: Difficult to coordinate systematic improvements
""")
st.markdown('</div>', unsafe_allow_html=True)

# Our Solution
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## Our Solution: Graph Neural Networks")
st.markdown("""
We developed a GNN-based approach that models the transit network as a graph,
where:
- **Nodes** = Bus stops (existing and candidate locations)
- **Edges** = Road connections and spatial relationships
- **Features** = Demographics, mobility patterns, road characteristics

### Why GNNs?

Traditional ML treats each stop independently. GNNs understand the **network structure**,
considering how stops interact and influence each other.
""")

# Comparison table
st.markdown("""
<table class="comparison-table">
<thead>
<tr>
    <th>Aspect</th>
    <th>Traditional ML</th>
    <th>Graph Neural Networks (Our Approach)</th>
</tr>
</thead>
<tbody>
<tr>
    <td><strong>Network Understanding</strong></td>
    <td>Treats stops independently</td>
    <td>Models entire network structure and relationships</td>
</tr>
<tr>
    <td><strong>Spatial Relationships</strong></td>
    <td>Manual feature engineering</td>
    <td>Automatically learns spatial patterns</td>
</tr>
<tr>
    <td><strong>Data Efficiency</strong></td>
    <td>Needs more labeled examples</td>
    <td>Learns from neighborhood structure (semi-supervised)</td>
</tr>
<tr>
    <td><strong>Scalability</strong></td>
    <td>Performance degrades with network size</td>
    <td>Efficient message passing for large networks</td>
</tr>
<tr>
    <td><strong>Equity Modeling</strong></td>
    <td>Difficult to incorporate system-wide equity</td>
    <td>Natural framework for network-level optimization</td>
</tr>
</tbody>
</table>
""", unsafe_allow_html=True)

st.markdown("### Model Architecture")
st.markdown("""
- **Input**: 42 features per stop (demographics, mobility, infrastructure)
- **GNN Layers**: 3 GraphSAGE layers with neighborhood aggregation
- **Output**: Binary classification (good stop / not good stop) + confidence score
- **Training**: 80/20 train-test split on 4,284 existing stops
""")
st.markdown('</div>', unsafe_allow_html=True)

# Impact
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## Impact & Results")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Model Performance")
    st.markdown("""
    - **Accuracy**: 94%
    - **Precision**: 93%
    - **Recall**: 96% (excellent at finding good stops)
    - **F1 Score**: 94%
    - **AUC-ROC**: 0.97
    """)

with col2:
    st.markdown("### Equity Improvements")
    st.markdown("""
    - **Gini coefficient**: 0.72 → 0.61 (15% improvement)
    - **Coverage increase**: +4.2% average per route
    - **New residents served**: 1.8M across 88 wards
    - **Underserved areas prioritized**: 2x equity multiplier
    """)

st.markdown("### Geographic Distribution")
st.markdown("""
Our 20 route recommendations target the most underserved wards:
- **12 routes** in severely underserved areas (equity multiplier: 2.0x)
- **8 routes** in moderately underserved areas (equity multiplier: 1.5x)
- Focus on informal settlements: Kibera, Mathare, Kawangware
""")
st.markdown('</div>', unsafe_allow_html=True)

# Technology Stack
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## Technology Stack")

st.markdown("""
<div style="display: flex; flex-wrap: wrap; gap: 10px;">
    <span class="tech-badge">PyTorch Geometric</span>
    <span class="tech-badge">GraphSAGE</span>
    <span class="tech-badge">Pydeck</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">GTFS (Digital Matatus)</span>
    <span class="tech-badge">WorldMove (104K trajectories)</span>
    <span class="tech-badge">OSMnx (Road Network)</span>
    <span class="tech-badge">GeoPandas</span>
    <span class="tech-badge">Folium</span>
</div>
""", unsafe_allow_html=True)

st.markdown("### Data Sources")
st.markdown("""
1. **Digital Matatus GTFS Feed** (2019): 135+ routes, 4,284 stops
2. **WorldMove Mobility Data**: 104,000+ trajectories with speed and congestion
3. **OpenStreetMap**: Road network via OSMnx
4. **Kenya Census 2019**: Population density by ward
5. **Poverty & Income Data**: Ward-level socioeconomic indicators
""")
st.markdown('</div>', unsafe_allow_html=True)

# Team & Contact
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("## Team & Contact")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **David Kibet**
    MSc Epidemiology & Data Science
    Data Scientist & Urban Analytics Researcher

    Passionate about using AI and data science to solve urban equity challenges
    in African cities. This project combines graph machine learning, geospatial
    analysis, and transit planning to improve mobility access for underserved communities.
    """)

with col2:
    st.markdown("""
    **Links**

    mail: [Contact](mailto:atlonglastkibet@gmail.com)
    GitHub: [jav-nairobi](https://github.com/altonglastkibet/jav-nairobi)
    LinkedIn: [Your Profile](https://linkedin.com/in/davidkibet)
    """)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); font-size: 12px; padding: 20px;">
    Jav-Nairobi © 2024 | Built with ❤️ for Nairobi's transit equity.
</div>
""", unsafe_allow_html=True)
