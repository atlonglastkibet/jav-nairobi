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
    page_title="Jav-Nairobi",
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

# Legend inline below map
st.markdown("""
<div class="legend-inline">
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(231, 76, 60);"></div>
        <span>Severely Underserved</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(230, 126, 34);"></div>
        <span>Underserved</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(241, 196, 15);"></div>
        <span>Adequate</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(70, 204, 113);"></div>
        <span>Well Served</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Map caption
st.markdown("""
<div class="map-caption">
This map shows Nairobi's matatu route network. Routes are color-coded by equity tier, with red indicating severely underserved areas and green indicating well-served areas.
<strong>Routes Source:</strong> <a href="https://digitalmatatus.com/index.html" target="_blank">DIGITAL MATATUS PROJECT</a>
</div>
""", unsafe_allow_html=True)

# Metrics inline
st.markdown(f"""
<div class="metrics-inline">
    <div class="metric-inline-item">
        <div class="metric-inline-number">{metrics['routes']}</div>
        <div class="metric-inline-label">Routes Analyzed</div>
    </div>
    <div class="metric-inline-item">
        <div class="metric-inline-number">{metrics['stops']}</div>
        <div class="metric-inline-label">Existing Stops</div>
    </div>
    <div class="metric-inline-item">
        <div class="metric-inline-number">{metrics['candidates']}</div>
        <div class="metric-inline-label">Candidates Evaluated</div>
    </div>
    <div class="metric-inline-item">
        <div class="metric-inline-number">{metrics['impact']}</div>
        <div class="metric-inline-label">Residents Impacted</div>
    </div>
    <div class="metric-inline-item">
        <div class="metric-inline-number">{metrics['wards']}</div>
        <div class="metric-inline-label">Wards Impacted</div>
    </div>
</div>
""", unsafe_allow_html=True)

# THE PROJECT
st.markdown("""
<div class="content-section">
    <div class="section-title">THE PROJECT</div>
    <div class="section-content">
        Jav-Nairobi demonstrates how to leverage Deep Learning techniques, specifically Graph Neural Networks (GNNs), to revolutionize informal transit systems in Sub-Saharan Africa's sprawling urban landscapes.
        The project identifies underserved regions across Nairobi, generates optimal stop locations, and proposes route recommendations designed to increase equity both spatially and temporally.
        By analyzing over 135 routes, 4,384 existing stops, and 1,645 candidate locations, our model recommends strategic interventions that could serve an additional 1.8+ million Nairobians
        while maintaining—and in many cases improving—route performance metrics like speed and congestion reduction.
    </div>
</div>
""", unsafe_allow_html=True)

# DATA SOURCES
st.markdown("""
<div class="content-section">
    <div class="section-title">DATA SOURCES</div>
    <div class="section-content">
        Prior to our work, linking traffic and commute data for informal transit was incredibly difficult due to the scarceness, inconsistency, and proprietary nature of traffic data from providers like Google and Uber,
        making evidence-based planning nearly impossible for urban planners. Furthermore, there hasn't been a publicly available methodology on how to aggregate open data sources to improve equity in informal transit systems
        across the greater Sub-Saharan region. To address this, we leverage publicly available <a href="https://worldmove.ai" target="_blank">WorldMove</a> mobility data to simulate traffic patterns,
        combine it with GTFS data from <a href="https://digitalmatatus.com/index.html" target="_blank">Digital Matatus</a>, high-resolution population data from <a href="https://www.worldpop.org" target="_blank">WorldPop</a>,
        and geopolitical boundaries from the Kenya National Bureau of Statistics (KNBS) to construct a holistic and dynamic view of Nairobi's matatu ecosystem.
        This enables urban planners to work with robust, accessible data to analyze and build equitable solutions.
    </div>
</div>
""", unsafe_allow_html=True)

# HOW IT WORKS
st.markdown(f"""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        We begin with GTFS data encompassing over {metrics['routes']} routes and {metrics['stops']} stops. By layering 500-meter dissolving buffers around each stop and overlaying high-resolution population data,
        we estimate how many people each stop or route serves by geographic area. Using temporal access patterns from GTFS schedules, we compute trips per hour per capita,
        giving us precise estimates of regions underserved both spatially and temporally. We then generate high-quality stop candidates across all regions by ensuring stops are accessible,
        cover more people, and exist atop existing infrastructure. Using a Graph Neural Network (GNN), we predict optimal stop placements across Nairobi.
        Finally, we connect these stops to existing routes, create route variants, and recommend the variants with the greatest social advantage—balancing fair access in space and time
        while optimizing for performance metrics such as speed and congestion mitigation.
    </div>
</div>
""", unsafe_allow_html=True)

# THE MODEL
st.markdown("""
<div class="content-section">
    <div class="section-title">THE MODEL</div>
    <div class="section-content">
        The matatu network is inherently complex, dynamic, and ever-changing. To optimize it, we need a system capable of understanding this intricate structure.
        Since transit systems naturally form graph structures, with stops as nodes and roads as edges, we employ a Graph Convolutional Network (GCN) to parse and learn from this complexity.
        Each node (stop) aggregates information from its 8 nearest neighbors in the network. Every node holds a rich feature vector of approximately 40 attributes, including traffic patterns at different periods,
        coverage density, demand levels, service quality, accessibility scores, infrastructure proximity, and amenity availability. We process over 6,000 candidate stops with these features to predict
        where optimal stops should be placed to serve the most people. GNNs operate through message passing: each node iteratively exchanges information with its neighbors,
        learning to recognize patterns—such as underserved pockets near well-connected areas or zones with high demand but poor temporal access.
        This iterative refinement allows the model to propose stops that balance equity, accessibility, and operational efficiency in a way traditional optimization methods cannot achieve.
    </div>
</div>
""", unsafe_allow_html=True)

# IMPACT
st.markdown(f"""
<div class="content-section">
    <div class="section-title">IMPACT</div>
    <div class="section-content">
        Deep Learning promises to improve and optimize the complex transit challenges facing Nairobi. Our methodology demonstrates a substantial increase in matatu coverage,
        extending service to over {metrics['impact']} additional Nairobians—all while utilizing existing matatu infrastructure. No new matatus are required.
        The stops we identify, even in underserved and economically disadvantaged regions, require minimal infrastructure investment and benefit from proximity to areas already equipped with infrastructure but lacking proper matatu access.
        We show that it is possible to cover more people and increase fairness without sacrificing performance or speed. By providing alternative route variants,
        we enable planners to improve coverage while responding to demand and maintaining competitive travel times. This approach makes the matatus that Nairobians love and depend upon serve their true purpose: public good for all.
    </div>
</div>
""", unsafe_allow_html=True)

# THE FUTURE
st.markdown("""
<div class="content-section">
    <div class="section-title">THE FUTURE</div>
    <div class="section-content">
        The goal is to formalize matatus and transform Nairobi into a truly intelligent city where matatus operate on predictable schedules centered on social equity.
        This vision does not project into an idealistic world where "flying matatus" might be a possibility, but rather envisions a city that benefits from well-organized, predictable, and reliable matatu services for all.
        With data-driven insights and AI-powered optimization, Nairobi can lead the way in demonstrating how informal transit, often dismissed as chaotic, can evolve into
        a backbone of equitable urban mobility across Africa's rapidly growing cities.
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    <div class="footer-text">
        <strong>JAV-NAIROBI</strong> &copy; 2025<br/>
        Built by <strong>David Kibet</strong><br/>
        <a href="mailto:atlonglastkibet@gmail.com">Email</a> |
        <a href="https://github.com/atlonglastkibet/jav-nairobi" target="_blank">Project Link</a>
    </div>
</div>
""", unsafe_allow_html=True)
