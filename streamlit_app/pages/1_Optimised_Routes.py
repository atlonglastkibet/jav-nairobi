"""
Optimised Routes page - Explore GNN-recommended route variants
Direct Folium HTML embedding for full interactivity.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import base64
from pathlib import Path

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP_ROOT = Path(__file__).parent.parent

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Add streamlit_app to path first for its utils
sys.path.insert(0, str(STREAMLIT_APP_ROOT))
from utils.data_loader import get_routes_with_variants, prepare_folium_route_data
from utils.styling import get_custom_css

# Now add project root and import viz_utils
sys.path.insert(0, str(PROJECT_ROOT))

# Import viz_utils explicitly from project root
import importlib.util
spec = importlib.util.spec_from_file_location("viz_utils", PROJECT_ROOT / "utils" / "viz_utils.py")
viz_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viz_utils)
plot_route_variants_folium = viz_utils.plot_route_variants_folium

# Page config
st.set_page_config(
    page_title="Optimised Routes",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional CSS for full-width embedding
st.markdown("""
<style>
    /* Remove default padding for full-width map */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Style for route selector */
    .stSelectbox {
        margin-bottom: 16px;
    }

    /* Logo and title styling */
    .route-explorer-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .route-explorer-logo {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }

    .route-explorer-title {
        font-size: 32px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title
logo_path = STREAMLIT_APP_ROOT / "assets" / "route_explorer.jpg"
if logo_path.exists():
    st.markdown(f"""
    <div class="route-explorer-header">
        <img src="data:image/jpeg;base64,{get_image_base64(str(logo_path))}" class="route-explorer-logo" alt="Optimised Routes">
        <h1 class="route-explorer-title">Optimised Routes</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("Optimised Routes")

# Load OSMnx graph (cached)
@st.cache_resource
def load_osmnx_graph():
    """Load Nairobi road network graph."""
    import osmnx as ox
    from pathlib import Path

    # Path to cached graph (same as in notebooks)
    graph_path = PROJECT_ROOT / "data" / "processed" / "nairobi_drive.graphml"

    try:
        # Try to load cached graph first
        if graph_path.exists():
            G = ox.load_graphml(str(graph_path))
            return G
        else:
            # Fallback: download from OSM
            st.warning("Downloading road network from OpenStreetMap (this may take a few minutes)...")
            G = ox.graph_from_place("Nairobi, Kenya", network_type='drive')
            # Save for next time
            ox.save_graphml(G, str(graph_path))
            return G
    except Exception as e:
        st.error(f"Could not load road network: {e}")
        return None

# Load routes with variants
routes_list = get_routes_with_variants()

if len(routes_list) == 0:
    st.error("No routes with variants found. Please check data loading.")
    st.stop()

# Route selection
route_options = {r['display_name']: r['route_id'] for r in routes_list}
selected_display = st.selectbox(
    "Select from optimised routes:",
    options=list(route_options.keys()),
    index=0
)

selected_route_id = route_options[selected_display]

# Load data for Folium visualization
with st.spinner("Loading route data..."):
    folium_data = prepare_folium_route_data(selected_route_id)

if folium_data is None:
    st.error(f"Could not load data for route {selected_route_id}")
    st.stop()

# Load road network graph
with st.spinner("Loading road network..."):
    G = load_osmnx_graph()

if G is None:
    st.warning("Road network unavailable. Visualization will use straight lines between stops.")
    st.stop()

# Generate Folium map and get HTML
with st.spinner("Generating interactive map..."):
    try:
        folium_map = plot_route_variants_folium(
            route_id=folium_data['route_id'],
            G=G,
            route_geometries=folium_data['route_geometries'],
            variants_df=folium_data['variants_df'],
            selected_candidates=folium_data['selected_candidates'],
            feed=folium_data['feed'],
            df=folium_data['df'],
            max_variants_to_plot=3,
            output_path=None  # Don't save to file
        )

        # Get the HTML representation of the Folium map
        folium_html = folium_map._repr_html_()

        # Embed the HTML directly using Streamlit's components
        components.html(folium_html, height=800, scrolling=False)

    except Exception as e:
        st.error(f"Error generating map: {e}")
        import traceback
        st.code(traceback.format_exc())

# Map caption
st.markdown("""
<div class="map-caption">
Optimised routes from existing GTFS routes.
<strong>Route Data Source:</strong> <a href="https://digitalmatatus.com/index.html" target="_blank">DIGITAL MATATUS PROJECT</a>
</div>
""", unsafe_allow_html=True)

# HOW IT WORKS
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        We identified 22 routes serving underserved wards across Nairobi—Githurai Ward, Kangemi Ward, Dandora Area III Ward, Gatina Ward, Kahawa West,
        Zimmerman Ward, Matopeni/Spring Valley Ward, Imara Daima Ward, Mountain View Ward, Airbase Ward, Waithaka Ward, Uthiru/Ruthimitu Ward,
        Karen Ward, Njiru Ward, South C Ward, Mihango Ward, Roysambu Ward, Upper Savanna Ward, Nairobi West Ward, Pipeline Ward, Karura Ward, and Mutu-ini Ward.
        For each of these routes, we predicted optimal stop locations using Graph Neural Networks. These new stops aim to increase matatu coverage
        while still factoring for performance metrics like speed and congestion. The added stops are then connected to existing routes, and multiple route variants are generated.
        Each variant is evaluated using a composite score that balances equity (serving underserved populations), coverage (maximizing accessibility),
        temporal equity (ensuring service throughout the day), and performance (minimizing delays and congestion).
        The variant with the highest combined social impact and operational performance is selected as the recommended route extension.
    </div>
</div>
""", unsafe_allow_html=True)

# HOW TO USE
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW TO USE</div>
    <div class="section-content">
        Select a route from the dropdown above, then interact with the map by clicking the colored route lines to view detailed metrics in the floating statistics panel.
        Toggle route layers on and off using the layer control in the top-right corner of the map to compare different variants side by side.
        Hover over stops to see population served and accessibility details. The routes are color-coded: blue represents the existing route and stops,
        green shows the recommended extension (the highest-scoring variant based on our GNN model), yellow displays alternative variant 1, and red shows alternative variant 2.
        The metrics panel on the left updates dynamically when you click any route line, showing real-time statistics including the GNN score, equity multiplier
        (which prioritizes underserved areas), coverage score (population accessibility), and temporal equity score (time-based service fairness).
    </div>
</div>
""", unsafe_allow_html=True)

# RECOMMENDED ROUTE (GREEN)
st.markdown("""
<div class="content-section">
    <div class="section-title">RECOMMENDED ROUTE (GREEN)</div>
    <div class="section-content">
        The green route variant represents the model's top recommendation—the extension path that delivers the greatest combined benefit across all evaluation dimensions.
        This route achieves the highest GNN score by balancing multiple competing objectives: it serves the largest number of previously underserved residents,
        improves temporal equity by ensuring service throughout peak and off-peak hours, and maintains strong operational performance by minimizing route detours and congestion.
        The recommendation prioritizes areas with high equity multipliers—neighborhoods where access to public transit is most needed—while ensuring the new stops are strategically placed
        along existing infrastructure corridors to minimize implementation costs. This variant has been selected because it represents the optimal trade-off:
        it maximizes social impact without compromising the speed and reliability that make matatus an attractive transit option.
        By extending service into underserved pockets while keeping route deviations minimal, the recommended variant demonstrates that equity and efficiency are not mutually exclusive.
    </div>
</div>
""", unsafe_allow_html=True)

# ROUTE VARIANTS
st.markdown("""
<div class="content-section">
    <div class="section-title">ROUTE VARIANTS (YELLOW & RED)</div>
    <div class="section-content">
        The yellow and red route variants represent alternative extension strategies, each with different trade-offs between equity, coverage, and operational feasibility.
        While the green variant strikes the optimal balance, these alternatives may excel in specific dimensions—one might serve a slightly different pocket of underserved residents,
        another might prioritize coverage density over travel time, or emphasize temporal equity in areas with fluctuating demand throughout the day.
        These variants are not inferior solutions; rather, they offer planners flexibility to respond to evolving priorities or constraints.
        For instance, if a particular corridor faces infrastructure limitations, the yellow variant might provide a more immediately feasible path.
        If community input highlights a specific neighborhood's need, the red variant's slightly different route geometry might better address that concern.
        By presenting multiple viable options rather than a single rigid solution, we acknowledge the complexity of real-world urban planning—where political, economic,
        and social factors often require adaptable solutions. The model's ability to generate ranked alternatives ensures that decision-makers have options that still deliver significant impact,
        even if circumstances prevent the top recommendation from being implemented exactly as designed.
    </div>
</div>
""", unsafe_allow_html=True)

# THE METRICS
st.markdown("""
<div class="content-section">
    <div class="section-title">THE METRICS</div>
    <div class="section-content">
        Each route variant is evaluated using a multi-dimensional scoring system that captures the complex trade-offs inherent in transit planning.
        The <strong>GNN Score</strong> is the overall recommendation score generated by the Graph Neural Network, representing the model's confidence that this variant delivers optimal outcomes.
        This score is derived from the weighted combination of several sub-metrics. The <strong>Equity Multiplier</strong> boosts the score for routes serving underserved areas—neighborhoods with limited existing transit access,
        lower income levels, or higher population density relative to service availability. Higher multipliers (up to 2.0) indicate areas where new service will have the greatest equity impact.
        The <strong>Coverage Score</strong> measures the total population within walking distance (typically 500 meters) of the proposed stops, weighted by existing service levels—the goal is to maximize new access,
        not duplicate coverage. The <strong>Temporal Equity Score</strong> assesses whether the route provides balanced service throughout the day, preventing scenarios where neighborhoods have good morning service but are stranded in the evening.
        This metric computes trips per hour per capita across different time periods to ensure fairness. Finally, <strong>Performance Metrics</strong> (speed and congestion scores) ensure that equity gains do not come at the cost of
        unacceptably long travel times or severe route inefficiency. By integrating these diverse dimensions into a single composite score, the model captures what traditional planning methods often miss:
        the nuanced interplay between social equity, operational efficiency, and real-world feasibility.
    </div>
</div>
""", unsafe_allow_html=True)

# IMPACT
st.markdown("""
<div class="content-section">
    <div class="section-title">IMPACT</div>
    <div class="section-content">
        For each existing route, we connect new optimal stop locations to bring matatus closer to the people who need them most, directly impacting the residents living around these stops.
        The beauty of this approach is its pragmatism: we ensure that matatus don't take huge detours from their existing routes, thereby avoiding the addition of more chaos and operational headaches for city planners.
        This methodology is designed to add access without adding complexity—no flying matatus required, just smarter stop placement.
        By leveraging the existing matatu network's organic structure and simply filling in the gaps with data-driven precision, we demonstrate that equitable transit doesn't demand a complete overhaul or futuristic infrastructure.
        It requires understanding where people are, where service is lacking, and how to bridge that gap with minimal disruption.
        The result is a system that serves 1.8+ million more Nairobians, increases coverage in 22 underserved wards, and does so by working with—not against—the matatu culture that already defines Nairobi's streets.
        This is not about imposing rigid schedules or Western-style bus rapid transit; it's about making the informal transit system Nairobi already loves work better for everyone.
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
