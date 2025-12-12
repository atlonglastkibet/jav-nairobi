"""
Jav-Nairobi: AI-Powered Transit Equity Optimization
Main Streamlit Application Entry Point
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
from pathlib import Path
from streamlit_folium import st_folium
from shapely import wkt
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from utils.styling import get_custom_css
from utils.data_loader import (
    prepare_routes_with_paths, get_app_metrics, get_ward_equity_data,
    get_stops_for_map, get_featured_stories, load_stop_features,
    create_ward_coverage_map, CBD_LAT, CBD_LON, COLORS
)

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

    /* Content Section Styling Overrides */
    .content-section {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        max-width: 100% !important;
    }
    .section-title {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        color: #E74C3C !important;
        margin-bottom: 1rem !important;
        text-transform: uppercase !important;
    }
    .section-content {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        color: #e0e0e0 !important;
        text-align: left !important;
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

# ============================================================================
# THE PROJECT
# ============================================================================
st.markdown("""
<div class="content-section">
    <div class="section-title">THE PROJECT</div>
    <div class="section-content">
        Jav-Nairobi demonstrates how to leverage Deep Learning techniques, specifically Graph Neural Networks (GNNs), to revolutionize informal transit systems in Sub-Saharan Africa's sprawling urban landscapes. The project identifies underserved regions across Nairobi, generates optimal stop locations, and proposes route recommendations designed to increase equity both spatially and temporally. By analyzing over 135 routes, 4,384 existing stops, and 6,000+ candidate locations, our model recommends strategic interventions that could serve an additional 1.2+ million Nairobians while maintaining and in many cases improving route performance metrics like speed and congestion reduction.
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# WARD EQUITY DASHBOARD
# ============================================================================

st.markdown("""
<div class="content-section">
    <div class="section-title">THE EQUITY GAP</div>
    <div class="section-content">
        Nairobi's matatus carry 3 million people daily, but coverage is deeply unequal.
        22 wards remain severely underserved—where residents walk 15+ minutes just to catch a matatu,
        missing job opportunities and paying more for motorcycle taxis. This is not just inconvenient. It's inequitable.
    </div>
</div>
""", unsafe_allow_html=True)

# Load ward data
ward_data = get_ward_equity_data()

# Create columns for controls and map (controls increased by 50% from 0.67 to 1.0)
col_controls, col_map = st.columns([1.0, 4.0])

with col_controls:
    st.markdown("### Ward Equity Dashboard")

    # Before/After toggle
    view_mode = st.radio(
        "View:",
        ["Before (Current)", "After (With Extensions)"],
        horizontal=True
    )

    # Ward selector
    ward_options = ['All Wards'] + sorted(ward_data['ward'].dropna().unique().tolist())
    selected_ward = st.selectbox("Select Ward:", ward_options)

    # Display metrics for selected ward
    if selected_ward != 'All Wards':
        ward_row = ward_data[ward_data['ward'] == selected_ward].iloc[0]

        st.markdown("#### Current Situation")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Access", f"{ward_row['pct_access']:.1f}%")
            st.metric("Served", f"{int(ward_row['pop_served']):,}")
        with col2:
            st.metric("Population", f"{int(ward_row['population']):,}")
            st.metric("Unserved", f"{int(ward_row['pop_not_served']):,}")

        if view_mode == "After (With Extensions)":
            st.markdown("#### After Extension")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Access",
                    f"{ward_row['pct_access_after']:.1f}%",
                    delta=f"+{ward_row['access_improvement']:.1f}pp",
                    delta_color="normal"
                )
                st.metric(
                    "Served",
                    f"{int(ward_row['pop_served_after']):,}",
                    delta=f"+{int(ward_row['additional_pop_served']):,}",
                    delta_color="normal"
                )
            with col2:
                improvement_pct = (ward_row['access_improvement'] / ward_row['pct_access'] * 100) if ward_row['pct_access'] > 0 else 0
                st.metric("Improvement", f"{improvement_pct:.0f}%")
                st.metric("Unserved", f"{int(ward_row['pop_not_served'] - ward_row['additional_pop_served']):,}")
    else:
        # Show aggregate stats
        total_pop = ward_data['population'].sum()
        if view_mode == "Before (Current)":
            total_served = ward_data['pop_served'].sum()
            access_pct = (total_served / total_pop * 100)
            st.metric("City-Wide Access", f"{access_pct:.1f}%")
            st.metric("Total Served", f"{int(total_served):,}")
            st.metric("Total Unserved", f"{int(ward_data['pop_not_served'].sum()):,}")
        else:
            total_served_after = ward_data['pop_served_after'].sum()
            access_pct_after = (total_served_after / total_pop * 100)
            additional = ward_data['additional_pop_served'].sum()
            st.metric(
                "City-Wide Access",
                f"{access_pct_after:.1f}%",
                delta=f"+{additional/total_pop*100:.1f}pp"
            )
            st.metric(
                "Total Served",
                f"{int(total_served_after):,}",
                delta=f"+{int(additional):,}"
            )

with col_map:
    # Prepare ward visualization data
    if view_mode == "Before (Current)":
        ward_data['display_access'] = ward_data['pct_access']
    else:
        ward_data['display_access'] = ward_data['pct_access_after']

    # Filter if specific ward selected
    if selected_ward != 'All Wards':
        map_data = ward_data[ward_data['ward'] == selected_ward].copy()
        zoom = 12 - 0.2  # Zoom out by 0.2
    else:
        map_data = ward_data.copy()
        zoom = 10.5 - 0.2  # Zoom out by 0.2

    # Calculate Nairobi bounds for fitting map
    import json
    from shapely import wkt

    # Get bounds of all wards to center map on Nairobi
    all_geoms = []
    for idx, row in map_data.iterrows():
        if pd.notna(row.get('geometry')):
            geom = row['geometry']
            if isinstance(geom, str):
                geom = wkt.loads(geom)
            all_geoms.append(geom)

    # Calculate centroid and bounds
    if all_geoms:
        from shapely.ops import unary_union
        # Use unary_union to handle MultiPolygons correctly
        combined = unary_union(all_geoms)
        bounds = combined.bounds  # (minx, miny, maxx, maxy)
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
    else:
        center_lon = CBD_LON
        center_lat = CBD_LAT

    # Parse geometry if needed
    if 'geometry' in map_data.columns:
        features = []
        for idx, row in map_data.iterrows():
            if pd.notna(row.get('geometry')):
                geom = row['geometry']
                if isinstance(geom, str):
                    geom = wkt.loads(geom)

                # Get color based on access percentage
                access = row['display_access']
                if access >= 80:
                    color = COLORS['well_served'] + [180]
                elif access >= 60:
                    color = COLORS['adequate'] + [180]
                elif access >= 40:
                    color = COLORS['underserved'] + [180]
                else:
                    color = COLORS['severely_underserved'] + [180]

                features.append({
                    'type': 'Feature',
                    'geometry': json.loads(json.dumps(geom.__geo_interface__)),
                    'properties': {
                        'ward': row['ward'],
                        'access': f"{access:.1f}",
                        'population': f"{int(row['population']):,}",
                        'color': color
                    }
                })

        geojson_data = {
            'type': 'FeatureCollection',
            'features': features
        }

        # Create PyDeck layer
        geojson_layer = pdk.Layer(
            'GeoJsonLayer',
            data=geojson_data,
            opacity=0.6,
            stroked=True,
            filled=True,
            extruded=False,
            wireframe=False,
            get_fill_color='properties.color',
            get_line_color=[255, 255, 255, 100],
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True
        )

        # Center map on Nairobi bounds (calculated from ward geometries)
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0,
            bearing=0,
            min_zoom=9,  # Lock minimum zoom to keep Nairobi in view
            max_zoom=15  # Lock maximum zoom
        )

        deck = pdk.Deck(
            layers=[geojson_layer],
            initial_view_state=view_state,
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            map_provider='mapbox',  # Enable map controls
            tooltip={
                'html': '<b>{ward}</b><br/>Access: {access}%<br/>Population: {population}',
                'style': {
                    'backgroundColor': 'rgba(14, 17, 23, 0.9)',
                    'color': 'white',
                    'borderRadius': '8px',
                    'padding': '10px'
                }
            }
        )

        st.pydeck_chart(deck, use_container_width=True, height=500)

        # Legend
        st.markdown("""
        <div class="legend-inline" style="justify-content: center; margin-top: 0.5rem;">
            <div class="legend-inline-item">
                <div class="legend-inline-color" style="background: rgb(231, 76, 60);"></div>
                <span><40% Access</span>
            </div>
            <div class="legend-inline-item">
                <div class="legend-inline-color" style="background: rgb(230, 126, 34);"></div>
                <span>40-60%</span>
            </div>
            <div class="legend-inline-item">
                <div class="legend-inline-color" style="background: rgb(241, 196, 15);"></div>
                <span>60-80%</span>
            </div>
            <div class="legend-inline-item">
                <div class="legend-inline-color" style="background: rgb(70, 204, 113);"></div>
                <span>>80%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# STOP SELECTION INTELLIGENCE
# ============================================================================
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        We begin with GTFS data encompassing over 136 routes and 4,284 stops. By layering 500-meter dissolving buffers around each stop and overlaying high-resolution population data, we estimate how many people each stop or route serves by geographic area. Using temporal access patterns from GTFS schedules, we compute trips per hour per capita, giving us precise estimates of regions underserved both spatially and temporally. We then generate high-quality stop candidates across all regions by ensuring stops are accessible, cover more people, and exist atop existing infrastructure. Using a Graph Neural Network (GNN), we predict optimal stop placements across Nairobi. Finally, we connect these stops to existing routes, create route variants, and recommend the variants with the greatest social advantage balancing fair access in space and time while optimizing for performance metrics such as speed and congestion mitigation.
    </div>
</div>

<div class="content-section">
    <div class="section-title">THE MODEL</div>
    <div class="section-content">
        The matatu network is inherently complex, dynamic, and ever-changing. To optimize it, we need a system capable of understanding this intricate structure. Since transit systems naturally form graph structures, with stops as nodes and roads as edges, we employ a Graph Convolutional Network (GCN) to parse and learn from this complexity. Each node (stop) aggregates information from its 8 nearest neighbors in the network. Every node holds a rich feature vector of approximately 40 attributes, including traffic patterns at different periods, coverage density, demand levels, service quality, accessibility scores, infrastructure proximity, and amenity availability. We process over 6,000 candidate stops with these features to predict where optimal stops should be placed to serve the most people. GNNs operate through message passing: each node iteratively exchanges information with its neighbors, learning to recognize patterns such as underserved pockets near well-connected areas or zones with high demand but poor temporal access. This iterative refinement allows the model to propose stops that balance equity, accessibility, and operational efficiency in a way traditional optimization methods cannot achieve.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Stop Selection Intelligence")
st.markdown("Explore how our GNN identifies optimal locations for new matatu stops.")

# Load stops data
stops_data = get_stops_for_map()

# Filter controls
col1, col2 = st.columns([1, 1])
with col1:
    stop_filter = st.selectbox(
        "Show Stops:",
        ["All Stops", "New Candidate Stops Only", "Existing Stops Only"]
    )
with col2:
    ward_filter = st.selectbox(
        "Filter by Ward:",
        ['All Wards'] + sorted(stops_data['ward'].dropna().unique().tolist())
    )

# Apply filters
filtered_stops = stops_data.copy()
if stop_filter == "New Candidate Stops Only":
    filtered_stops = filtered_stops[filtered_stops['is_new_stop'] == True]
elif stop_filter == "Existing Stops Only":
    filtered_stops = filtered_stops[filtered_stops['is_new_stop'] == False]

if ward_filter != 'All Wards':
    filtered_stops = filtered_stops[filtered_stops['ward'] == ward_filter]

# Limit to reasonable number for performance
if len(filtered_stops) > 2000:
    filtered_stops = filtered_stops.sample(n=2000, random_state=42)

# Create PyDeck scatter layer
scatter_layer = pdk.Layer(
    'ScatterplotLayer',
    data=filtered_stops,
    get_position='[lon, lat]',
    get_color='color',
    get_radius='size',
    radius_min_pixels=2,
    radius_max_pixels=15,
    pickable=True,
    auto_highlight=True,
    opacity=0.8
)

view_state = pdk.ViewState(
    latitude=CBD_LAT,
    longitude=CBD_LON,
    zoom=10.5,
    pitch=0,
    bearing=0
)

deck = pdk.Deck(
    layers=[scatter_layer],
    initial_view_state=view_state,
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    tooltip={
        'html': '<b>{name}</b><br/>Ward: {ward}<br/>GNN Score: {gnn_score_formatted}<br/>Pop (500m): {pop_formatted}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.9)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '10px'
        }
    }
)

st.pydeck_chart(deck, use_container_width=True, height=500)

# Legend
st.markdown("""
<div class="legend-inline" style="justify-content: center; margin-top: 0.5rem;">
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(52, 168, 83);"></div>
        <span>New Candidate Stops</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(26, 115, 232);"></div>
        <span>Existing Stops</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="map-caption">
Click any stop to see details. Green markers indicate GNN-recommended candidate locations, sized by quality score.
Blue markers show existing matatu stops.
</div>
""", unsafe_allow_html=True)

# THE FUTURE
st.markdown("""
<div class="content-section">
    <div class="section-title">THE FUTURE</div>
    <div class="section-content">
        The goal is to formalize matatus and transform Nairobi into a truly intelligent city where matatus operate on predictable schedules centered on social equity.
        This vision does not project into an idealistic world where "<a href='/Wiki#flying-matatus' target='_self'>flying matatus</a>" might be a possibility, but rather envisions a city that benefits from well-organized, predictable, and reliable matatu services for all.
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
