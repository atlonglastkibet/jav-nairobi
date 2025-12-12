"""
Traffic & ETA page with 3D visualization and speed-based coloring.
"""

import streamlit as st
import sys
import pydeck as pdk
import pandas as pd
import time
import base64
from pathlib import Path

# Add paths for imports
STREAMLIT_APP_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(STREAMLIT_APP_ROOT))

from utils.data_loader import (
    prepare_routes_with_traffic,
    prepare_routes_with_traffic_fast,
    load_gtfs_feed,
    calculate_route_eta,
    get_route_congested_segments,
    get_route_segments_with_speeds,
    CBD_LAT,
    CBD_LON
)
from utils.styling import get_custom_css

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Page config
st.set_page_config(
    page_title="Traffic & ETA",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional custom CSS for traffic page
st.markdown("""
<style>
    /* Traffic page styling */
    .traffic-header {
        background: linear-gradient(135deg, rgba(26, 29, 36, 0.9) 0%, rgba(15, 17, 21, 0.95) 100%);
        border-left: 4px solid #E74C3C;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    .stats-card {
        background: linear-gradient(135deg, rgba(26, 29, 36, 0.6) 0%, rgba(15, 17, 21, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .stats-card:hover {
        border-color: rgba(231, 76, 60, 0.5);
        box-shadow: 0 8px 16px rgba(231, 76, 60, 0.2);
        transform: translateY(-2px);
    }

    .stat-value {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(135deg, #E74C3C 0%, #46CC71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .speed-indicator {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        margin-right: 8px;
    }

    .speed-fast {
        background: rgba(46, 204, 113, 0.2);
        color: #46CC71;
        border: 1px solid #46CC71;
    }

    .speed-moderate {
        background: rgba(241, 196, 15, 0.2);
        color: #F1C40F;
        border: 1px solid #F1C40F;
    }

    .speed-slow {
        background: rgba(230, 126, 34, 0.2);
        color: #E67E22;
        border: 1px solid #E67E22;
    }

    .speed-congested {
        background: rgba(231, 76, 60, 0.2);
        color: #E74C3C;
        border: 1px solid #E74C3C;
    }

    .route-selector {
        background: rgba(26, 29, 36, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }

    /* White button with black text */
    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #f0f0f0 !important;
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
    }

    /* Traffic header with icon */
    .traffic-page-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .traffic-page-logo {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }

    .traffic-page-title {
        font-size: 32px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }

    .traffic-subtitle {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 5px;
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

# Logo and Title
logo_path = STREAMLIT_APP_ROOT / "assets" / "traffic_lights.jpg"
if logo_path.exists():
    st.markdown(f"""
    <div class="traffic-page-header">
        <img src="data:image/jpeg;base64,{get_image_base64(str(logo_path))}" class="traffic-page-logo" alt="Traffic">
        <div>
            <h1 class="traffic-page-title">Traffic & ETA</h1>
            <div class="traffic-subtitle">Real-time snapshot with speed-based route coloring</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("Traffic & ETA")
    st.markdown("**Real-time snapshot with speed-based route coloring**")

# HOW IT WORKS
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        Data from <a href="https://worldmove.ai" target="_blank">WorldMove</a> provides high-fidelity mobility data that has beaten global benchmarks in traffic simulation accuracy.
        The dataset contains millions of synthetic agent-based trajectories representing realistic urban movement patterns learned from global mobility data.
        We analyze a 24-hour snapshot of 104,538 agents moving across Nairobi's road network, aggregating individual movements into grid cells and computing speeds based on congestion-aware models.
        By processing these trajectories through a 1km x 1km spatial grid and mapping them to the OpenStreetMap road network, we estimate traffic speeds and congestion levels with remarkable precision.
        The model applies time-of-day congestion profiles calibrated to Nairobi's known traffic patterns—assigning base speeds of 35 km/h during free-flow nighttime hours,
        dropping to 15 km/h during morning rush (6-9 AM), and bottoming out at 12 km/h during the afternoon rush (3-7 PM).
        These speeds are further adjusted by trip distance and random variation to reflect real-world traffic dynamics.
        This methodology allows us to estimate movement patterns within routes across Nairobi with great accuracy, providing critical input for downstream route optimization.
        Understanding where and when congestion occurs enables the GNN model to recommend stop placements that balance accessibility with realistic travel times.
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_route' not in st.session_state:
    st.session_state.selected_route = None
if 'hour_of_day' not in st.session_state:
    st.session_state.hour_of_day = 9

# Load GTFS feed and prepare route options
feed = load_gtfs_feed()
all_routes = feed.routes.copy()
route_options = {f"{row['route_id']} - {row['route_long_name']}": row['route_id']
                 for _, row in all_routes.iterrows()}

# Route selection (above map)
st.markdown("### Route Selection")

col1, col2 = st.columns([3, 1])

with col1:
    selected_display = st.selectbox(
        "Choose a route to analyze:",
        options=["All Routes"] + list(route_options.keys()),
        index=0,
        label_visibility="collapsed"
    )

with col2:
    if st.button("Clear Selection", use_container_width=True):
        st.session_state.selected_route = None
        st.rerun()

if selected_display != "All Routes":
    selected_route_id = route_options[selected_display]
    if st.session_state.selected_route != selected_route_id:
        st.session_state.selected_route = selected_route_id
        st.rerun()
else:
    st.session_state.selected_route = None

# Load traffic data for selected hour (cached for performance)
routes_df = prepare_routes_with_traffic(hour=st.session_state.hour_of_day)

if routes_df.empty:
    st.error("No traffic data available. Please check data files.")
    st.stop()

# Calculate view state and layers
layers = []
view_state = None

if st.session_state.selected_route:
    # Load DETAILED data only for selected route
    selected_route_data = prepare_routes_with_traffic_fast(hour=st.session_state.hour_of_day, route_id=st.session_state.selected_route)

    if len(selected_route_data) > 0:
        route_info = selected_route_data.iloc[0]

        # Calculate route center and bounds
        path = route_info['path']
        lats = [p[1] for p in path]
        lons = [p[0] for p in path]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        # Enhanced view state for 3D effect
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=13,
            pitch=60,
            bearing=30
        )

        # Get ALL segments with individual speeds and colors
        all_segments = get_route_segments_with_speeds(st.session_state.selected_route, hour=st.session_state.hour_of_day)

        if len(all_segments) > 0:
            # Create PathLayer for each segment with its own color based on speed
            segments_df = pd.DataFrame([{
                'path': seg['segment'],
                'speed': seg['speed'],
                'color': seg['color'],
                'segment_info': f"Speed: {seg['speed']} km/h"
            } for seg in all_segments])

            # Create individual path layer for color-coded segments
            segments_layer = pdk.Layer(
                'PathLayer',
                data=segments_df,
                get_path='path',
                get_color='color',
                get_width=10,
                width_min_pixels=10,
                pickable=True,
                auto_highlight=True
            )
            layers.append(segments_layer)

            # Add markers at congestion points
            congested_segs = [seg for seg in all_segments if seg['is_congested']]
            if len(congested_segs) > 0:
                markers_df = pd.DataFrame([{
                    'lat': seg['mid_lat'],
                    'lon': seg['mid_lon'],
                    'speed': seg['speed']
                } for seg in congested_segs])

                markers_layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=markers_df,
                    get_position=['lon', 'lat'],
                    get_fill_color=[231, 76, 60, 255],
                    get_radius=80,
                    pickable=True,
                    auto_highlight=True
                )
                layers.append(markers_layer)
        else:
            # Fallback
            path_layer = pdk.Layer(
                'PathLayer',
                data=selected_route_data,
                get_path='path',
                get_color='color',
                get_width=8,
                width_min_pixels=8,
                pickable=True,
                auto_highlight=True
            )
            layers.append(path_layer)

else:
    # All routes view
    view_state = pdk.ViewState(
        latitude=CBD_LAT,
        longitude=CBD_LON,
        zoom=11,
        pitch=50,
        bearing=0
    )

    path_layer = pdk.Layer(
        'PathLayer',
        data=routes_df,
        get_path='path',
        get_color='color',
        get_width=3,
        width_min_pixels=3,
        pickable=True,
        auto_highlight=True
    )
    layers.append(path_layer)

# Create deck with tooltip
if st.session_state.selected_route:
    tooltip_config = {
        'html': '<b>Segment Speed:</b> {speed} km/h<br/>'
                '<b>Info:</b> {segment_info}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.95)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '12px',
            'fontSize': '14px'
        }
    }
else:
    tooltip_config = {
        'html': '<b>Route:</b> {route_id}<br/>'
                '<b>Name:</b> {route_name}<br/>'
                '<b>Avg Speed:</b> {avg_speed} km/h<br/>'
                '<b>ETA:</b> {eta_minutes} min<br/>'
                '<b>Distance:</b> {distance_km} km<br/>'
                '<b>Status:</b> {speed_category}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.95)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '12px',
            'fontSize': '14px'
        }
    }

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    tooltip=tooltip_config
)

# Display map
st.pydeck_chart(deck, use_container_width=True, height=650)

# Map caption
st.markdown("""
<div class="map-caption">
Traffic data simulation for Nairobi routes using data from the <a href="https://worldmove.ai" target="_blank">WorldMove</a> mobility dataset.
High-fidelity agent-based mobility patterns enable accurate speed and congestion estimation across the matatu network.
</div>
""", unsafe_allow_html=True)

# Time of day selector (below map)
st.markdown("### Time of Day")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    hour = st.slider(
        "Select hour to analyze traffic conditions:",
        min_value=0,
        max_value=23,
        value=st.session_state.hour_of_day,
        format="%d:00",
        label_visibility="collapsed"
    )
    st.session_state.hour_of_day = hour

with col2:
    if st.button("Morning Rush (9 AM)"):
        st.session_state.hour_of_day = 9
        st.rerun()

with col3:
    if st.button("Evening Rush (5 PM)"):
        st.session_state.hour_of_day = 17
        st.rerun()

# Time period label
time_period = "Morning Rush" if 7 <= hour <= 10 else "Evening Rush" if 17 <= hour <= 20 else "Midnight" if 0 <= hour <= 5 else "Midday"
st.markdown(f"**Current selection:** {hour}:00 - {time_period}")

# Traffic metrics (retained)
if st.session_state.selected_route:
    if len(selected_route_data) > 0:
        route_info = selected_route_data.iloc[0]
    else:
        route_info = routes_df[routes_df['route_id'] == st.session_state.selected_route].iloc[0]

    st.markdown(f"### {route_info['route_name']}")

    speed_class = f"speed-{route_info['speed_category'].lower()}"
    st.markdown(f'<span class="{speed_class} speed-indicator">{route_info["speed_category"].upper()}</span>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">ETA</div>
            <div class="stat-value">{route_info['eta_minutes']:.0f} min</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Avg Speed</div>
            <div class="stat-value">{route_info['avg_speed']:.0f} <span style="font-size: 18px;">km/h</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Distance</div>
            <div class="stat-value">{route_info['distance_km']:.1f} <span style="font-size: 18px;">km</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Route ID</div>
            <div class="stat-value" style="font-size: 24px;">{route_info['route_id']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Congestion hotspots
    all_segments = get_route_segments_with_speeds(st.session_state.selected_route, hour=hour)
    congested_segs = [seg for seg in all_segments if seg['is_congested']]

    if len(congested_segs) > 0:
        st.markdown("### Congestion Hotspots")
        st.markdown(f'<span class="speed-indicator speed-congested">{len(congested_segs)} CONGESTED SEGMENTS</span>',
                    unsafe_allow_html=True)

        with st.expander("View Congested Segments Details"):
            for i, seg in enumerate(congested_segs, 1):
                st.markdown(f"""
                **Segment {i}**
                - Speed: **{seg['speed']} km/h**
                - Location: ({seg['lat1']:.4f}, {seg['lon1']:.4f}) → ({seg['lat2']:.4f}, {seg['lon2']:.4f})
                """)
    else:
        st.success("No congested segments detected on this route at this hour!")

    # Speed distribution
    if len(all_segments) > 0:
        st.markdown("### Speed Distribution")

        fast_count = sum(1 for seg in all_segments if seg['speed'] >= 40)
        moderate_count = sum(1 for seg in all_segments if 25 <= seg['speed'] < 40)
        slow_count = sum(1 for seg in all_segments if 15 <= seg['speed'] < 25)
        congested_count = len(congested_segs)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Fast Segments", fast_count, f"{fast_count/len(all_segments)*100:.0f}%")

        with col2:
            st.metric("Moderate", moderate_count, f"{moderate_count/len(all_segments)*100:.0f}%")

        with col3:
            st.metric("Slow", slow_count, f"{slow_count/len(all_segments)*100:.0f}%")

        with col4:
            st.metric("Congested", congested_count, f"{congested_count/len(all_segments)*100:.0f}%")

else:
    # Network overview
    st.markdown("### Network Overview")

    col1, col2, col3, col4 = st.columns(4)

    avg_speed_all = routes_df['avg_speed'].mean()
    avg_eta_all = routes_df['eta_minutes'].mean()
    total_distance = routes_df['distance_km'].sum()
    num_routes = len(routes_df)

    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Routes Analyzed</div>
            <div class="stat-value">{num_routes}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Network Avg Speed</div>
            <div class="stat-value">{avg_speed_all:.0f} <span style="font-size: 18px;">km/h</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Avg Route ETA</div>
            <div class="stat-value">{avg_eta_all:.0f} <span style="font-size: 18px;">min</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-label">Total Network</div>
            <div class="stat-value">{total_distance:.0f} <span style="font-size: 18px;">km</span></div>
        </div>
        """, unsafe_allow_html=True)

# Speed legend
st.markdown("### Speed Categories")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="stats-card"><span class="speed-indicator speed-fast">FAST</span> ≥ 40 km/h</div>',
                unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stats-card"><span class="speed-indicator speed-moderate">MODERATE</span> 25-40 km/h</div>',
                unsafe_allow_html=True)

with col3:
    st.markdown('<div class="stats-card"><span class="speed-indicator speed-slow">SLOW</span> 15-25 km/h</div>',
                unsafe_allow_html=True)

with col4:
    st.markdown('<div class="stats-card"><span class="speed-indicator speed-congested">CONGESTED</span> < 15 km/h</div>',
                unsafe_allow_html=True)



# HOW TO USE
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW TO USE</div>
    <div class="section-content">
        <ol style="line-height: 1.8;">
            <li><strong>Select time of day</strong> using the slider below the map to see how traffic conditions change throughout the day</li>
            <li><strong>Select a route</strong> from the dropdown to view segment-by-segment speed analysis with real traffic data</li>
            <li><strong>Hover over segments</strong> on the map to see individual segment speeds displayed as rounded-up integers</li>
            <li><strong>Watch the 3D visualization</strong> where each segment is colored by its speed: green for fast, yellow for moderate, orange for slow, and red for congested</li>
            <li><strong>Identify congestion hotspots</strong> marked with red circles where speeds fall below 15 km/h</li>
            <li><strong>Review speed distribution</strong> to see the breakdown of fast, moderate, slow, and congested segments across the route</li>
        </ol>
    </div>
</div>
""", unsafe_allow_html=True)

# FEATURES
st.markdown("""
<div class="content-section">
    <div class="section-title">FEATURES</div>
    <div class="section-content">
        <ul style="line-height: 1.8;">
            <li><strong>Segment-by-Segment Coloring:</strong> Each route segment has its own color based on actual traffic speed</li>
            <li><strong>Rounded Speed Values:</strong> All speeds shown as absolute integers rounded up for accuracy</li>
            <li><strong>Congestion Detection:</strong> Identifies slow segments using actual traffic cell data from WorldMove trajectories</li>
            <li><strong>Speed Distribution:</strong> Percentage breakdown of segment speeds across the route</li>
            <li><strong>Time-Aware Analysis:</strong> Traffic conditions update dynamically based on the hour selected, reflecting Nairobi's congestion patterns</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# PERFORMANCE NOTE
st.markdown("""
<div class="content-section">
    <div class="section-title">PERFORMANCE NOTE</div>
    <div class="section-content">
        The visualization employs a two-tier performance strategy to balance speed and precision. When viewing all routes simultaneously,
        the system uses fast approximation based on time-of-day heuristics—applying known congestion profiles without querying the full traffic dataset—resulting in instant loading.
        This approach sacrifices granular accuracy for responsiveness, making it ideal for getting an overview of network-wide conditions.
        When you select a single route, the system switches to precise segment-level speed calculations, querying actual WorldMove traffic data for each stop-to-stop segment.
        This involves spatial lookups to find the nearest traffic cell, retrieving hourly speed estimates, and computing Haversine distances—typically taking 1-2 seconds.
        The trade-off is intentional: detailed analysis where it matters, speed where it doesn't. For planning purposes, single-route precision is critical for identifying
        specific congestion bottlenecks and optimizing stop placements, while network overviews provide strategic context without computational overhead.
    </div>
</div>
""", unsafe_allow_html=True)

# DOWNSTREAM
st.markdown("""
<div class="content-section">
    <div class="section-title">DOWNSTREAM</div>
    <div class="section-content">
        Traffic data forms the backbone of any mobility optimization system. Understanding movement patterns is essential for planning equitable and efficient transit networks.
        Given the scarcity, inconsistency, and proprietary nature of traffic data in Sub-Saharan African cities, the methodology demonstrated here—leveraging open synthetic mobility data
        from WorldMove—provides a replicable framework for urban planners to estimate traffic speeds with remarkable accuracy without relying on expensive commercial data sources.
        This traffic layer is not merely descriptive; it directly informs the Graph Neural Network training process. Each candidate stop's feature vector includes traffic-based attributes:
        average speeds in the surrounding area, congestion indices during peak and off-peak hours, and temporal variability in accessibility.
        These features allow the GNN to learn that a stop in a high-congestion zone may require additional service frequency to offset delays, or that a stop in a free-flow corridor
        can serve as an express connection point. Downstream, when generating route variants, traffic data serves as a critical weight in the recommendation algorithm.
        A variant that covers more underserved residents but routes through severe congestion may score lower than an alternative that balances equity and performance.
        By integrating traffic into both model training and route evaluation, Jav-Nairobi ensures that recommendations are not just theoretically optimal—they are operationally viable,
        respecting the real-world constraints that make or break public transit systems.
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
